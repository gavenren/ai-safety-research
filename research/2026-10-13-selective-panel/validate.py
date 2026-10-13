#!/usr/bin/env python3
"""Independent checks for the 2026-10-13 saved-vote routing audit.

Use only the Python standard library. Probability checks use a normalized
Fraction recurrence. Small controls enumerate subsets directly. This file
does not import analyze.py or reuse its combinatorial probability formula.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_HASH = "a8c004743230361498dc7eaca9ee9900bbc3a4a7f0dfba113b0052668325be7e"
EXPECTED_MODELS = {
    "Llama-3.1-8B", "Mistral-7B", "OLMo-2-7B", "Qwen2.5-7B", "gemma-2-9b"
}
CHECKS = Counter()


def require(condition, label):
    CHECKS[label] += 1
    if not condition:
        raise AssertionError(label)


def read_csv(name):
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def ratio(numerator, denominator):
    return Fraction(numerator, denominator) if denominator else None


def close(value, expected, label):
    if expected is None:
        require(value in ("", None), label + ": empty denominator")
    else:
        require(value not in ("", None), label + ": value exists")
        actual = float(value)
        require(math.isfinite(actual), label + ": finite")
        require(math.isclose(actual, float(expected), rel_tol=1e-11,
                             abs_tol=1e-12), label + ": numeric equality")


def recurrence_distribution(population, errors, accepted):
    """Normalize exact relative masses; use no factorials or combinations."""
    low = max(0, accepted - (population - errors))
    high = min(accepted, errors)
    masses = {low: Fraction(1)}
    for x in range(low, high):
        masses[x + 1] = masses[x] * Fraction(
            (errors - x) * (accepted - x),
            (x + 1) * (population - errors - accepted + x + 1),
        )
    total = sum(masses.values())
    return {x: weight / total for x, weight in masses.items()}


def quantile(distribution, probability):
    cumulative = Fraction(0)
    for count, mass in sorted(distribution.items()):
        cumulative += mass
        if cumulative >= probability:
            return count
    raise AssertionError("Probability distribution has insufficient mass")


def independent_items():
    path = ROOT / "data_labels.csv"
    require(hashlib.sha256(path.read_bytes()).hexdigest() == INPUT_HASH,
            "fixed input hash")
    rows = read_csv(path.name)
    require(len(rows) == 6990, "input row count")
    seen = set()
    groups = defaultdict(list)
    for row in rows:
        key = row["dataset"], row["item_id"], row["model"]
        require(key not in seen, "input key is unique")
        seen.add(key)
        require(row["reference"] in {"0", "1"}, "binary reference")
        require(row["prediction"] in {"0", "1"}, "binary vote")
        groups[key[:2]].append(row)
    require(len(groups) == 1398, "aligned item count")
    result = {}
    for key, item in groups.items():
        require(len(item) == 5, "five votes per item")
        require({row["model"] for row in item} == EXPECTED_MODELS,
                "complete shared model set")
        labels = {int(row["reference"]) for row in item}
        require(len(labels) == 1, "shared reference per item")
        label = labels.pop()
        votes = sorted(int(row["prediction"]) for row in item)
        majority = votes[2]
        agreement = sum(vote == majority for vote in votes)
        result[key] = dict(reference=label, flag_votes=sum(votes),
                           majority=majority, agreement=agreement,
                           error=int(majority != label))
    require(len({key[0] for key in result}) == 7, "seven test sets")
    return result


def expected_counts(items, dataset, group, threshold):
    sample = [item for key, item in items.items()
              if key[0] == dataset
              and (group == "all" or item["reference"] == int(group))]
    accepted = [item for item in sample if item["agreement"] >= threshold]
    n = len(sample)
    e = sum(item["error"] for item in sample)
    a = len(accepted)
    ea = sum(item["error"] for item in accepted)
    return dict(N=n, E=e, A=a, EA=ea, D=n-a, ED=e-ea)


def small_controls():
    cases = 0
    for n in range(1, 9):
        for e in range(n + 1):
            labels = [1] * e + [0] * (n-e)
            for a in range(n + 1):
                enumerated = Counter(sum(labels[i] for i in subset)
                                     for subset in itertools.combinations(range(n), a))
                total = sum(enumerated.values())
                exact = {x: Fraction(count, total)
                         for x, count in sorted(enumerated.items())}
                require(recurrence_distribution(n, e, a) == exact,
                        "small subset distribution control")
                require(sum(exact.values()) == 1, "control probability sums to one")
                require(sum(x*p for x, p in exact.items()) == Fraction(a*e, n),
                        "control expected errors")
                for q in (Fraction(1, 40), Fraction(39, 40)):
                    answer = quantile(exact, q)
                    require(sum(p for x, p in exact.items() if x < answer) < q,
                            "control quantile left boundary")
                    require(sum(p for x, p in exact.items() if x <= answer) >= q,
                            "control quantile right boundary")
                cases += 1
    # Exhaust all five-vote patterns and both reference labels.
    for votes in itertools.product((0, 1), repeat=5):
        for label in (0, 1):
            majority = sorted(votes)[2]
            agreement = votes.count(majority)
            require(agreement in {3, 4, 5}, "vote agreement range control")
            require((agreement == 5) == (len(set(votes)) == 1),
                    "unanimity endpoint control")
            acceptance = [agreement >= t for t in (3, 4, 5)]
            require(acceptance[0] and acceptance[0] >= acceptance[1] >= acceptance[2],
                    "nested acceptance control")
            require(int(majority != label) in (0, 1), "binary error control")
    require(ratio(0, 0) is None, "zero denominator control")
    require(ratio(0, 4) == 0, "all correct rate control")
    require(ratio(4, 4) == 1, "all wrong rate control")
    return cases


def check_saved_controls():
    saved = json.loads((ROOT / "results_controls.json").read_text())
    count_names = ("n", "errors", "accepted", "accepted_errors", "deferred", "deferred_errors")
    expected = {
        "all_correct": (4, 0, 4, 0, 0, 0),
        "all_wrong": (4, 4, 4, 4, 0, 0),
        "no_accepted": (2, 1, 0, 0, 2, 1),
        "correct_deferred": (2, 1, 1, 1, 1, 0),
        "wrong_deferred": (2, 1, 1, 0, 1, 1),
        "all_accepted": (2, 1, 2, 1, 0, 0),
    }
    require(set(saved) == set(expected) | {"small_random_distribution"}, "saved control keys")
    for name, values in expected.items():
        row = saved[name]
        for field, value in zip(count_names, values):
            require(row[field] == value, "saved control count")
        n, e, a, ea, d, ed = values
        close(row["selective_error"], ratio(ea, a), "saved control selective error")
        close(row["review_break_even_error"], ratio(ed, d), "saved control review error")
    require({x: Fraction(p) for x, p in saved["small_random_distribution"]}
            == recurrence_distribution(4, 2, 2), "saved small probability control")


def main():
    items = independent_items()
    manifest = json.loads((ROOT / "input_manifest.json").read_text())
    require(manifest["data_sha256"] == INPUT_HASH, "manifest data hash")
    require(hashlib.sha256((ROOT / "analysis_plan.md").read_bytes()).hexdigest()
            == manifest["plan_sha256"], "plan hash unchanged")
    datasets = sorted({key[0] for key in items})
    keys = {(dataset, group, threshold)
            for dataset in datasets for group in ("all", "0", "1")
            for threshold in (3, 4, 5)}
    computed = {key: expected_counts(items, *key) for key in keys}

    saved_items = read_csv("results_items.csv")
    require(len(saved_items) == 1398, "saved item row count")
    seen = set()
    for row in saved_items:
        key = row["dataset"], row["item_id"]
        require(key in items and key not in seen, "saved item unique and known")
        seen.add(key)
        expected = items[key]
        for field in ("reference", "flag_votes", "majority", "agreement"):
            require(int(row[field]) == expected[field], "saved item " + field)
        require(int(row["wrong"]) == expected["error"], "saved item error")
        for threshold in (3, 4, 5):
            require(int(row[f"accept_t{threshold}"])
                    == int(expected["agreement"] >= threshold), "saved item routing")
    require(seen == set(items), "saved items complete")

    probability_rows = read_csv("results_random_distribution.csv")
    saved_distributions = defaultdict(dict)
    for row in probability_rows:
        key = row["dataset"], row["reference"], int(row["threshold"])
        x = int(row["accepted_errors"])
        require(x not in saved_distributions[key], "probability key unique")
        numerator, denominator = int(row["probability_numerator"]), int(row["probability_denominator"])
        require(numerator > 0 and denominator > 0, "probability fraction positive")
        saved_distributions[key][x] = Fraction(numerator, denominator)
    require(set(saved_distributions) == keys, "probability groups complete")
    exact_distributions = {}
    for key in keys:
        c = computed[key]
        expected = recurrence_distribution(c["N"], c["E"], c["A"])
        exact_distributions[key] = expected
        actual = saved_distributions[key]
        require(set(actual) == set(expected), "probability support complete")
        for x in expected:
            require(actual[x] == expected[x], "exact recurrence probability equality")
        require(sum(actual.values()) == 1, "probability sum equals one")
        require(sum(x*p for x, p in actual.items()) == Fraction(c["A"]*c["E"], c["N"]),
                "exact distribution mean")

    group_rows = read_csv("results_groups.csv")
    require(len(group_rows) == 63, "saved group row count")
    seen = set()
    count_fields = {"n": "N", "errors": "E", "accepted": "A", "accepted_errors": "EA",
                    "deferred": "D", "deferred_errors": "ED"}
    for row in group_rows:
        key = row["dataset"], row["reference"], int(row["threshold"])
        require(key in keys and key not in seen, "group unique and known")
        seen.add(key)
        c = computed[key]
        n, e, a, ea, d, ed = (c[k] for k in ("N", "E", "A", "EA", "D", "ED"))
        for field, count_name in count_fields.items():
            require(int(row[field]) == c[count_name], "group count " + field)
        require(n == a+d and e == ea+ed, "count conservation")
        base, selective = Fraction(e, n), ratio(ea, a)
        metrics = {
            "coverage": Fraction(a, n), "baseline_error": base,
            "selective_error": selective,
            "selective_minus_baseline": None if selective is None else selective-base,
            "residual_automated_error": Fraction(ea, n),
            "review_break_even_error": ratio(ed, d), "error_capture": ratio(ed, e),
            "random_expected_accepted_errors": Fraction(a*e, n),
        }
        for field, expected in metrics.items():
            close(row[field], expected, "group " + field)
            if field not in ("selective_minus_baseline", "random_expected_accepted_errors"):
                require(expected is None or 0 <= expected <= 1, "rate in range")
        distribution = exact_distributions[key]
        for suffix, q in (("025", Fraction(1, 40)), ("975", Fraction(39, 40))):
            value = quantile(distribution, q)
            require(int(row[f"random_q{suffix}_errors"]) == value, "group random quantile")
            require(sum(p for x, p in distribution.items() if x < value) < q,
                    "saved quantile left boundary")
            require(sum(p for x, p in distribution.items() if x <= value) >= q,
                    "saved quantile right boundary")
            close(row[f"random_q{suffix}_selective_error"], ratio(value, a),
                  "group quantile accepted error")
        if key[2] == 3:
            require(a == n and ea == e and d == ed == 0, "full acceptance identity")
    require(seen == keys, "saved groups complete")
    for dataset in datasets:
        for threshold in (3, 4, 5):
            for field in ("N", "E", "A", "EA", "D", "ED"):
                require(computed[dataset, "all", threshold][field]
                        == sum(computed[dataset, group, threshold][field] for group in ("0", "1")),
                        "reference class count sum")
        for group in ("all", "0", "1"):
            for field in ("A", "EA"):
                require(computed[dataset, group, 3][field]
                        >= computed[dataset, group, 4][field]
                        >= computed[dataset, group, 5][field], "group nested acceptance")

    scenarios = read_csv("results_review_scenarios.csv")
    h_values = {Fraction(0), Fraction(1, 20), Fraction(1, 10), Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)}
    expected_scenario_keys = {(key, h) for key in keys for h in h_values}
    require(len(scenarios) == 378, "saved scenario row count")
    seen = set()
    outcomes = Counter()
    for row in scenarios:
        key = row["dataset"], row["reference"], int(row["threshold"])
        h = Fraction(row["review_error"])
        scenario_key = key, h
        require(scenario_key in expected_scenario_keys and scenario_key not in seen,
                "scenario unique and planned")
        seen.add(scenario_key)
        c = computed[key]
        n, e, a, ea, d, ed = (c[k] for k in ("N", "E", "A", "EA", "D", "ED"))
        # Count replacement errors directly, then check the algebraic identity.
        total_errors = Fraction(ea) + h*d
        system_error = total_errors/n
        base = Fraction(e, n)
        change = system_error-base
        random_error = (Fraction(a*e, n)+h*d)/n
        for field, expected in {
            "system_error": system_error, "baseline_error": base, "change": change,
            "random_system_error": random_error, "routing_minus_random": system_error-random_error,
        }.items():
            close(row[field], expected, "scenario " + field)
        require(change == Fraction(d, n)*h-Fraction(ed, n), "review change identity")
        if d:
            require((change < 0) == (h < Fraction(ed, d)), "strict review break even")
            require((change == 0) == (h == Fraction(ed, d)), "equal review break even")
        else:
            require(change == 0, "no review change identity")
        outcome = "improve" if change < 0 else "worsen" if change > 0 else "tie"
        require(row["outcome"] == outcome, "scenario outcome")
        outcomes[outcome] += 1
    require(seen == expected_scenario_keys, "saved scenarios complete")

    summary = json.loads((ROOT / "results_summary.json").read_text())
    for field, expected in {"group_rows": 63, "items": 1398, "random_probability_rows": len(probability_rows),
                            "scenario_rows": 378, "votes": 6990}.items():
        require(summary[field] == expected, "summary count " + field)
    require(set(summary["thresholds"]) == {"3", "4", "5"}, "summary thresholds complete")
    for threshold in (3, 4, 5):
        rows = [computed[dataset, "all", threshold] for dataset in datasets]
        class_rows = [computed[dataset, group, threshold]
                      for dataset in datasets for group in ("0", "1")]
        stats = Counter()
        for c in rows:
            if c["A"] == 0:
                stats["sets_no_accepted"] += 1
            else:
                delta = Fraction(c["EA"], c["A"])-Fraction(c["E"], c["N"])
                stats["sets_improve" if delta < 0 else "sets_worsen" if delta > 0 else "sets_tie"] += 1
        stats["class_rows_no_accepted"] = sum(c["A"] == 0 for c in class_rows)
        stats["class_rows_selective_worse"] = sum(c["A"] > 0 and Fraction(c["EA"], c["A"])
                                                 > Fraction(c["E"], c["N"]) for c in class_rows)
        actual = summary["thresholds"][str(threshold)]
        for field in ("sets_no_accepted", "sets_improve", "sets_worsen", "sets_tie",
                      "class_rows_no_accepted", "class_rows_selective_worse"):
            require(actual[field] == stats[field], "summary " + field)
        close(actual["mean_set_coverage"], sum(Fraction(c["A"], c["N"]) for c in rows)/7,
              "summary mean set coverage")
        available = [c for c in rows if c["A"]]
        close(actual["mean_set_selective_error"],
              sum(Fraction(c["EA"], c["A"]) for c in available)/len(available),
              "summary mean set selective error")

    controls = small_controls()
    check_saved_controls()
    print(json.dumps({
        "status": "PASS", "checks": sum(CHECKS.values()),
        "input_sha256": INPUT_HASH, "items_checked": len(items),
        "groups_checked": len(group_rows), "exact_probability_rows_checked": len(probability_rows),
        "review_scenarios_checked": len(scenarios), "small_subset_distribution_cases": controls,
        "review_scenario_outcomes": dict(sorted(outcomes.items())),
        "method": "Independent item reconstruction, exact Fraction recurrence, and direct small subset enumeration",
        "check_counts": dict(sorted(CHECKS.items())),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
