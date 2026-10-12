#!/usr/bin/env python3
"""Independent checks for the saved vote audit. Do not import analyze.py."""

import csv
import hashlib
import itertools
import json
import math
import platform
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
MODELS = (
    "Llama-3.1-8B", "Mistral-7B", "OLMo-2-7B", "Qwen2.5-7B", "gemma-2-9b"
)
BITS = tuple(itertools.product((0, 1), repeat=5))
WRONG = tuple(bits for bits in BITS if sum(bits) >= 3)
CHECKS = Counter()


def require(condition, message, group="other"):
    CHECKS[group] += 1
    if not condition:
        raise AssertionError(message)


def close(got, expected, message, group="other"):
    got = float(got)
    expected = float(expected)
    require(math.isfinite(got), message + ": non-finite value", group)
    require(math.isclose(got, expected, rel_tol=1e-11, abs_tol=1e-12),
            f"{message}: {got} != {expected}", group)


def integer(value, message):
    require(isinstance(value, (int, str)) and not isinstance(value, bool),
            message + ": not an integer", "types")
    parsed = int(value)
    require(str(parsed) == str(value), message + ": noncanonical integer", "types")
    return parsed


def rows(name):
    with (BASE / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def exact_product(rates):
    """Sum disjoint majority-error events, with exact rational arithmetic."""
    total = Fraction(0)
    for bits in itertools.product((0, 1), repeat=len(rates)):
        if sum(bits) <= len(rates) // 2:
            continue
        probability = Fraction(1)
        for bit, rate in zip(bits, rates):
            probability *= rate if bit else 1 - rate
        total += probability
    return total


def product_float(rates):
    # A direct event sum, separate from the primary polynomial method.
    return math.fsum(math.prod(rate if bit else 1 - rate
                               for bit, rate in zip(bits, rates))
                     for bits in WRONG)


def percentile_linear(values, quantile):
    # Independent implementation of the documented NumPy linear rule.
    ordered = sorted(values)
    index = (len(ordered) - 1) * quantile
    left = math.floor(index)
    right = math.ceil(index)
    return ordered[left] + (ordered[right] - ordered[left]) * (index - left)


def control_checks():
    values = {}
    for size in (1, 3, 5):
        for endpoint in (0, 1):
            result = exact_product([Fraction(endpoint)] * size)
            require(result == endpoint, "endpoint control failed", "controls")
    for numerator in range(11):
        rate = Fraction(numerator, 10)
        require(exact_product([rate]) == rate, "one-model control failed", "controls")
    dependent_actual = Fraction(1, 5)
    independent = exact_product([Fraction(1, 5)] * 5)
    require(independent == Fraction(181, 3125), "identical voter expectation", "controls")
    require(dependent_actual != independent, "identical voter contrast", "controls")
    values["identical_voters_02"] = {
        "observed_error": float(dependent_actual), "independent_error": float(independent)
    }
    rates = [Fraction(1, 10), Fraction(1, 5), Fraction(3, 10),
             Fraction(2, 5), Fraction(1, 2)]
    probabilities = [math.prod(rate if bit else 1 - rate
                               for bit, rate in zip(bits, rates)) for bits in BITS]
    require(sum(probabilities) == 1, "synthetic product mass", "controls")
    reconstructed = [sum(p for bits, p in zip(BITS, probabilities) if bits[j])
                     for j in range(5)]
    require(reconstructed == rates, "synthetic product marginals", "controls")
    observed = sum(p for bits, p in zip(BITS, probabilities) if sum(bits) >= 3)
    require(observed == exact_product(reconstructed), "synthetic product majority", "controls")
    close(product_float([float(r) for r in rates]), observed,
          "float product control", "controls")
    close(percentile_linear([0, 1, 2, 3], 0.025), 0.075,
          "linear percentile lower control", "controls")
    close(percentile_linear([0, 1, 2, 3], 0.975), 2.925,
          "linear percentile upper control", "controls")
    values["synthetic_product"] = {
        "member_rates": [float(rate) for rate in rates],
        "observed_error": float(observed), "independent_error": float(observed)
    }
    return values


def saved_control_checks():
    controls = json.loads((BASE / "results_controls.json").read_text())["controls"]
    expected_rates = {
        "all_correct": [0] * 5, "all_wrong": [1] * 5,
        "identical_voters_02": [0.2] * 5,
        "synthetic_product": [0.1, 0.2, 0.3, 0.4, 0.6],
        "single_0": [0], "single_02": [0.2], "single_05": [0.5], "single_1": [1]
    }
    require(len(controls) == len(expected_rates), "saved control count", "controls")
    seen = set()
    for row in controls:
        name = row["name"]
        require(name in expected_rates and name not in seen, "saved control name", "controls")
        seen.add(name)
        require(row["rates"] == expected_rates[name], "saved control rates", "controls")
        rates = [Fraction(str(rate)) for rate in row["rates"]]
        independent = exact_product(rates)
        actual = Fraction(1, 5) if name == "identical_voters_02" else independent
        close(row["observed_error"], actual, name + " actual control", "controls")
        close(row["independent_error"], independent, name + " product control", "controls")
    require(seen == set(expected_rates), "missing saved controls", "controls")


def read_inputs():
    manifest = json.loads((BASE / "input_manifest.json").read_text())
    digest = hashlib.sha256((BASE / "data_labels.csv").read_bytes()).hexdigest()
    require(digest == manifest["data_sha256"], "input hash differs", "input")
    decisions = rows("data_labels.csv")
    require(len(decisions) == 6990, "decision count differs", "input")
    aligned = defaultdict(dict)
    labels = {}
    for row in decisions:
        key = (row["dataset"], row["item_id"])
        require(all(row.values()), "empty input value", "input")
        require(row["model"] in MODELS, "unknown model", "input")
        reference = integer(row["reference"], "reference")
        prediction = integer(row["prediction"], "prediction")
        require(reference in (0, 1) and prediction in (0, 1), "nonbinary label", "input")
        require(row["model"] not in aligned[key], "duplicate input decision", "input")
        require(key not in labels or labels[key] == reference,
                "inconsistent reference", "input")
        labels[key] = reference
        aligned[key][row["model"]] = int(prediction != reference)
    require(len(aligned) == 1398, "item count differs", "input")
    grouped = defaultdict(list)
    for key, voters in aligned.items():
        require(set(voters) == set(MODELS), "missing model vote", "input")
        grouped[(key[0], labels[key])].append(tuple(voters[m] for m in MODELS))
    require(len(grouped) == 14, "class cell count differs", "input")
    require(len({key[0] for key in grouped}) == 7, "dataset count differs", "input")
    for dataset, _ in grouped:
        require((dataset, 0) in grouped and (dataset, 1) in grouped,
                "missing class", "input")
    return grouped, digest


def check_points(grouped):
    point_rows = rows("results_cells.csv")
    require(len(point_rows) == 154, "point row count differs", "points")
    panel_indices = list(itertools.combinations(range(5), 3)) + [tuple(range(5))]
    expected = {}
    full = {}
    for (dataset, reference), votes in grouped.items():
        n = len(votes)
        for panel in panel_indices:
            members = tuple(MODELS[j] for j in panel)
            counts = [sum(vote[j] for vote in votes) for j in panel]
            marginals = [Fraction(count, n) for count in counts]
            errors = sum(sum(vote[j] for j in panel) > len(panel) // 2 for vote in votes)
            observed = Fraction(errors, n)
            product = exact_product(marginals)
            values = {
                "n": n, "panel_size": len(panel), "errors": errors,
                "member_error_counts": counts, "observed_error": observed,
                "independent_error": product, "gap": observed - product,
                "mean_member_error": sum(marginals) / len(marginals),
                "best_member_error": min(marginals),
            }
            expected[(dataset, reference, "|".join(members))] = values
            if len(panel) == 5:
                full[(dataset, reference)] = values
    seen = set()
    for row in point_rows:
        key = (row["dataset"], integer(row["reference"], "point reference"), row["panel"])
        require(key in expected and key not in seen, f"unexpected point key {key}", "points")
        seen.add(key)
        for name, value in expected[key].items():
            if name == "member_error_counts":
                got = json.loads(row[name])
                require(got == value and all(type(v) is int for v in got),
                        f"{key} {name}", "points")
            elif name in ("n", "panel_size", "errors"):
                require(integer(row[name], name) == value, f"{key} {name}", "points")
            else:
                close(row[name], value, f"{key} {name}", "points")
    require(seen == set(expected), "missing point keys", "points")
    return full


def check_patterns(grouped):
    pattern_rows = rows("results_patterns.csv")
    expected = {(dataset, reference, "".join(map(str, bits))): count
                for (dataset, reference), votes in grouped.items()
                for bits, count in ((bits, Counter(votes)[bits]) for bits in BITS)}
    require(len(pattern_rows) == 14 * 32, "pattern row count differs", "patterns")
    seen = set()
    for row in pattern_rows:
        key = (row["dataset"], integer(row["reference"], "pattern reference"), row["pattern"])
        require(key in expected and key not in seen, f"unexpected pattern key {key}", "patterns")
        seen.add(key)
        require(integer(row["count"], "pattern count") == expected[key],
                f"pattern count differs {key}", "patterns")
    require(seen == set(expected), "missing pattern keys", "patterns")


def check_bootstrap(grouped, full):
    bootstrap_rows = rows("results_bootstrap.csv")
    require(len(bootstrap_rows) == 28000, "bootstrap row count differs", "bootstrap")
    by_cell = defaultdict(dict)
    for row in bootstrap_rows:
        key = (row["dataset"], integer(row["reference"], "bootstrap reference"))
        draw = integer(row["draw"], "draw")
        require(key in grouped and draw not in by_cell[key],
                f"unexpected bootstrap key {key}, {draw}", "bootstrap")
        by_cell[key][draw] = row
    require(set(by_cell) == set(grouped), "missing bootstrap cells", "bootstrap")
    rng = np.random.default_rng(20261012)
    ranges = {}
    for key in sorted(grouped):
        votes = grouped[key]
        n = len(votes)
        histogram = Counter(votes)
        probabilities = np.array([histogram[bits] / n for bits in BITS])
        generated = rng.multinomial(n, probabilities, size=2000)
        require(set(by_cell[key]) == set(range(2000)), "bootstrap draw index differs", "bootstrap")
        gaps = []
        for draw in range(2000):
            row = by_cell[key][draw]
            counts = json.loads(row["pattern_counts"])
            require(len(counts) == 32 and all(type(c) is int and c >= 0 for c in counts),
                    "invalid draw counts", "bootstrap")
            require(integer(row["n"], "bootstrap n") == n and sum(counts) == n,
                    "draw sample size differs", "bootstrap")
            require(counts == generated[draw].tolist(), "seeded draw differs", "bootstrap")
            require(all(c == 0 for c, p in zip(counts, probabilities) if p == 0),
                    "draw contains an unseen pattern", "bootstrap")
            observed = sum(count for bits, count in zip(BITS, counts) if sum(bits) >= 3) / n
            marginal = [sum(count for bits, count in zip(BITS, counts) if bits[j]) / n
                        for j in range(5)]
            product = product_float(marginal)
            gap = observed - product
            for field, expected in (("observed_error", observed),
                                    ("independent_error", product), ("gap", gap)):
                close(row[field], expected, f"{key} draw {draw} {field}", "bootstrap")
            gaps.append(gap)
        ranges[key] = (percentile_linear(gaps, 0.025), percentile_linear(gaps, 0.975))
    interval_rows = rows("results_intervals.csv")
    require(len(interval_rows) == 14, "interval row count differs", "intervals")
    seen = set()
    for row in interval_rows:
        key = (row["dataset"], integer(row["reference"], "interval reference"))
        require(key in ranges and key not in seen, "unexpected interval key", "intervals")
        seen.add(key)
        close(row["gap"], full[key]["gap"], f"{key} interval point", "intervals")
        close(row["lower"], ranges[key][0], f"{key} interval lower", "intervals")
        close(row["upper"], ranges[key][1], f"{key} interval upper", "intervals")
    require(seen == set(ranges), "missing interval keys", "intervals")


def main():
    controls = control_checks()
    saved_control_checks()
    grouped, digest = read_inputs()
    full = check_points(grouped)
    check_patterns(grouped)
    check_bootstrap(grouped, full)
    return {
        "status": "PASS", "input_sha256": digest,
        "input_rows": 6990, "aligned_items": 1398,
        "point_cells_checked": 154, "pattern_histograms_checked": 14,
        "pattern_rows_checked": 448, "bootstrap_rows_checked": 28000,
        "percentile_ranges_checked": 14,
        "primary_algorithm_controls_checked": 8,
        "independent_method": "Fraction event enumeration for point cells; direct event sums for every bootstrap row",
        "bootstrap_seed_and_order_checked": True,
        "percentile_rule_checked": "linear, independently implemented with sorted values",
        "validator_control_results": controls,
        "check_counts": dict(CHECKS), "total_checks": sum(CHECKS.values()),
        "python_version": platform.python_version(), "numpy_version": np.__version__,
    }


if __name__ == "__main__":
    try:
        result = main()
    except Exception as error:
        result = {"status": "FAIL", "error": f"{type(error).__name__}: {error}",
                  "check_counts": dict(CHECKS), "total_checks": sum(CHECKS.values())}
    (BASE / "validation_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "PASS" else 1)
