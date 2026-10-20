#!/usr/bin/env python3
"""Independent audit. This file does not read or import analyze.py.

Candidate method: enumerate full words, group by final state and length,
then scan each word for the visible ordered subsequence.
"""
import argparse
import collections
import csv
import itertools
import json
from pathlib import Path
import sys
import time

OPS = ("add1", "sub1", "set0", "set1", "flip_y")
RULES = ("visible", "replay", "no_loss", "agreement")
OUTCOMES = (
    "correct_completion",
    "false_completion",
    "refusal_correct",
    "refusal_incorrect",
)


def sequential(initial, word, agent=False):
    x, y = initial
    x += int(agent)
    for op in word:
        if op == "add1":
            x += 1
        elif op == "sub1":
            x -= 1
        elif op == "set0":
            x = 0
        elif op == "set1":
            x = 1
        elif op == "flip_y":
            y = 1 - y
        else:
            raise ValueError("Unknown command")
    return (x, y)


def target_formula(initial, word):
    """Independent expression: start after the last x assignment."""
    last = max((i for i, op in enumerate(word) if op.startswith("set")),
               default=-1)
    base = initial[0] if last < 0 else int(word[last][-1])
    tail = word[last + 1:]
    return (base + tail.count("add1") - tail.count("sub1"),
            initial[1] ^ (word.count("flip_y") % 2))


def subsequence(short, long):
    cursor = iter(long)
    return all(any(item == wanted for item in cursor) for wanted in short)


def obs_key(initial, current, visible, bound):
    return (tuple(initial), tuple(current), tuple(visible), bound)


def read_jsonl(path):
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def classify(claim, final, target):
    if claim:
        return "correct_completion" if final == target else "false_completion"
    return "refusal_correct" if final == target else "refusal_incorrect"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    root = args.directory
    started = time.process_time()
    config = json.loads((root / "config.json").read_text())
    require(tuple(config["commands"]) == OPS, "Unexpected commands")
    require(config["max_actual_length"] == 4, "Unexpected actual length")
    require(config["candidate_max_length"] == 5, "Unexpected candidate limit")
    results = root / "results"
    cases = read_jsonl(results / "cases.jsonl")
    rows = read_jsonl(results / "decisions.jsonl")
    require(len(cases) == 44444, "Wrong number of cases")

    initials = tuple(itertools.product((0, 1), repeat=2))
    expected_cases = {
        (initial, word, mask)
        for initial in initials
        for length in range(5)
        for word in itertools.product(OPS, repeat=length)
        for mask in range(1 << length)
    }
    seen_cases = set()
    seen_case_ids = set()
    formula_checks = 0
    for case in cases:
        initial = tuple(case["initial"])
        word = tuple(case["word"])
        mask = case["mask"]
        key = (initial, word, mask)
        require(key in expected_cases, "Unexpected case")
        require(key not in seen_cases, "Duplicate case")
        seen_cases.add(key)
        require(case["case_id"] not in seen_case_ids, "Duplicate case ID")
        seen_case_ids.add(case["case_id"])
        visible = tuple(op for i, op in enumerate(word) if mask & (1 << i))
        require(visible == tuple(case["visible"]), "Wrong visible log")
        require(len(word) - len(visible) == case["missing"], "Wrong loss count")
        require(sequential(initial, word, True) == tuple(case["current"]),
                "Wrong current state")
        expected_target = target_formula(initial, word)
        require(expected_target == tuple(case["target"]), "Wrong true target")
        require(sequential(initial, word) == expected_target,
                "Target formula and step replay differ")
        formula_checks += 1
    require(seen_cases == expected_cases, "Missing cases")
    print(f"PASS exact case set: {len(cases)}")

    # The main implementation uses a subsequence index. This implementation
    # stores full words by final state and length, then filters at read time.
    buckets = collections.defaultdict(list)
    candidate_word_checks = 0
    for initial in initials:
        for length in range(6):
            for word in itertools.product(OPS, repeat=length):
                current = sequential(initial, word, True)
                target = target_formula(initial, word)
                require(target == sequential(initial, word),
                        "Candidate target expressions differ")
                buckets[(initial, current, length)].append((word, target))
                candidate_word_checks += 1

    def query(initial, current, visible, bound):
        if type(bound) is not int or bound < 0:
            raise ValueError("Bound must be a nonnegative integer")
        if any(op not in OPS for op in visible):
            raise ValueError("Unknown command")
        if len(visible) + bound > 5:
            raise ValueError("Candidate length exceeds this audit")
        candidates = []
        for length in range(len(visible), len(visible) + bound + 1):
            candidates.extend(
                (word, target)
                for word, target in buckets[(initial, current, length)]
                if subsequence(visible, word)
            )
        return candidates

    negative_controls = 0
    for bad in (-1, True, 1.5, "1"):
        try:
            query((0, 0), (1, 0), (), bad)
        except ValueError:
            negative_controls += 1
        else:
            raise AssertionError("Malformed bound was accepted")
    try:
        query((0, 0), (1, 0), ("unknown",), 0)
    except ValueError:
        negative_controls += 1
    else:
        raise AssertionError("Unknown command was accepted")
    require(not query((0, 0), (999, 0), (), 1),
            "Inconsistent current state has candidates")
    negative_controls += 1
    small = query((0, 0), (1, 0), (), 0)
    enlarged = query((0, 0), (1, 0), (), 1)
    require({t for _, t in small} == {(0, 0)},
            "Complete empty-log control failed")
    require({t for _, t in enlarged} == {(0, 0), (1, 0)},
            "Hidden assignment ambiguity control failed")
    negative_controls += 2
    require(target_formula((0, 0), ("set1",)) != small[0][1],
            "False-bound witness did not fail as expected")
    negative_controls += 1
    assigned = query((0, 0), (0, 0), ("set0",), 1)
    require(len(assigned) > 1 and {t for _, t in assigned} == {(0, 0)},
            "Many histories with one target control failed")
    negative_controls += 1

    observations = {}
    observation_ids = set()
    expected_decisions = {}
    for row in rows:
        key = obs_key(row["initial"], row["current"], row["visible"],
                      row["bound"])
        require(key not in observations, "Duplicate observation")
        require(row["observation_id"] not in observation_ids,
                "Duplicate observation ID")
        observation_ids.add(row["observation_id"])
        observations[key] = row
        initial, current, visible, bound = key
        require(type(bound) is int and bound >= 0, "Malformed bound")
        require(len(visible) + bound <= 5, "Unexpected candidate length")
        candidates = query(initial, current, visible, bound)
        targets = frozenset(target for _, target in candidates)
        require(len(candidates) == row["candidate_count"],
                f"Candidate count differs: {row['observation_id']}")
        require(targets == frozenset(map(tuple, row["targets"])),
                f"Target set differs: {row['observation_id']}")
        require(len(row["targets"]) == len(targets), "Duplicate target rows")
        require(all(target[1] == current[1] for target in targets),
                "Candidate changed the saved y value")
        visible_final = (
            current[0] if any(op.startswith("set") for op in visible)
            else current[0] - 1, current[1]
        )
        replay_ok = sequential(initial, visible, True) == current
        decisions = {
            "visible": (True, visible_final),
            "replay": (True, visible_final) if replay_ok else (False, current),
            "no_loss": (True, target_formula(initial, visible))
            if bound == 0 and replay_ok else (False, current),
            "agreement": (True, next(iter(targets)))
            if len(targets) == 1 else (False, current),
        }
        require(set(row["decisions"]) == set(RULES), "Wrong rule keys")
        for rule, (claim, final) in decisions.items():
            actual = row["decisions"][rule]
            require(type(actual["claim"]) is bool, "Claim must be boolean")
            require(actual["claim"] == claim and tuple(actual["final"]) == final,
                    f"Decision differs: {row['observation_id']} {rule}")
        expected_decisions[key] = (decisions, targets,
                                   frozenset(word for word, _ in candidates))
    print(f"PASS candidate sets and decisions: {len(observations)} observations")

    counts = collections.Counter()
    required_observations = set()
    bound_observations = collections.defaultdict(set)
    honest_membership_checks = 0
    monotonicity_checks = 0
    for case in cases:
        k = case["missing"]
        length = len(case["word"])
        settings = [("tight", k), ("loose", k + 1)]
        if k:
            settings.append(("false", k - 1))
        selected = {}
        for setting, bound in settings:
            key = obs_key(case["initial"], case["current"], case["visible"],
                          bound)
            required_observations.add(key)
            bound_observations[setting].add(key)
            require(key in observations, "Required observation absent")
            decisions, targets, candidate_words = expected_decisions[key]
            selected[setting] = (decisions, targets)
            if setting != "false":
                require(tuple(case["word"]) in candidate_words,
                        "True history omitted under honest bound")
                require(tuple(case["target"]) in targets,
                        "True target omitted under honest bound")
                honest_membership_checks += 1
            for rule, (claim, final) in decisions.items():
                outcome = classify(claim, final, tuple(case["target"]))
                counts[(setting, length, k, rule, outcome)] += 1
            counts[(setting, length, k, "oracle", "correct_completion")] += 1
        tight_decisions, tight_targets = selected["tight"]
        loose_decisions, loose_targets = selected["loose"]
        require(tight_targets <= loose_targets, "Target-set monotonicity failed")
        if loose_decisions["agreement"][0]:
            require(tight_decisions["agreement"] == loose_decisions["agreement"],
                    "Completion monotonicity failed")
        monotonicity_checks += 1
    require(required_observations == set(observations),
            "Unused or missing observation rows")

    case_order = lambda case: (
        *case["initial"], len(case["word"]),
        tuple(OPS.index(op) for op in case["word"]), case["mask"])
    require(cases == sorted(cases, key=case_order), "Case order differs from plan")
    first_witness = {}
    for case in cases:
        tight_key = obs_key(case["initial"], case["current"], case["visible"],
                            case["missing"])
        decisions, targets, words = expected_decisions[tight_key]
        predicates = {
            "safe_missing": case["missing"] > 0
            and decisions["agreement"] == (True, tuple(case["target"])),
            "replay_false": decisions["replay"][0]
            and decisions["replay"][1] != tuple(case["target"]),
            "ambiguous": len(targets) > 1,
            "multiple_histories_one_target": len(words) > 1 and len(targets) == 1,
        }
        if case["missing"]:
            false_key = obs_key(case["initial"], case["current"], case["visible"],
                                case["missing"] - 1)
            false_decisions = expected_decisions[false_key][0]
            predicates["false_bound"] = (
                false_decisions["agreement"][0]
                and false_decisions["agreement"][1] != tuple(case["target"]))
        for name, predicate in predicates.items():
            if predicate:
                first_witness.setdefault(name, case["case_id"])
    witnesses = json.loads((results / "witnesses.json").read_text())
    require(set(witnesses) == set(first_witness), "Witness keys differ")
    cases_by_id = {case["case_id"]: case for case in cases}
    rows_by_id = {row["observation_id"]: row for row in rows}
    witness_candidates_checked = 0
    for name, item in witnesses.items():
        require(item["case"]["case_id"] == first_witness[name],
                f"First witness differs: {name}")
        require(item["case"] == cases_by_id[item["case"]["case_id"]],
                "Witness case differs from case data")
        observation = item["observation"]
        require(observation == rows_by_id[observation["observation_id"]],
                "Witness observation differs from decision data")
        for candidate in item.get("candidates", []):
            word = tuple(candidate["word"])
            initial = tuple(observation["initial"])
            current = tuple(observation["current"])
            visible = tuple(observation["visible"])
            require(subsequence(visible, word), "Witness has wrong visible log")
            require(len(visible) <= len(word) <= len(visible) + observation["bound"],
                    "Witness exceeds bound")
            require(sequential(initial, word, True) == current,
                    "Witness does not replay to current state")
            require(target_formula(initial, word) == tuple(candidate["target"]),
                    "Witness has wrong target")
            witness_candidates_checked += 1
    require(len({tuple(x["target"]) for x in witnesses["ambiguous"]["candidates"]}) == 2,
            "Ambiguity witness must have different targets")

    summaries = []
    for setting, length, k, rule in sorted({key[:4] for key in counts}):
        row = {"setting": setting, "length": length, "missing": k, "rule": rule}
        row.update({outcome: counts[(setting, length, k, rule, outcome)]
                    for outcome in OUTCOMES})
        row["total"] = sum(row[outcome] for outcome in OUTCOMES)
        summaries.append(row)
    (results / "independent_summary.json").write_text(
        json.dumps(summaries, indent=2, sort_keys=True) + "\n")
    independent_rows_written = len(json.loads(
        (results / "independent_summary.json").read_text()))
    require(independent_rows_written == len(summaries),
            "Independent summary receipt row count differs")
    require(all(row["total"] > 0 for row in summaries),
            "Independent summary contains an empty joint group")

    def in_scope(scope, length, missing):
        if scope == "all":
            return True
        if scope == "L4_missing":
            return length == 4 and missing > 0
        if scope.startswith("missing"):
            return missing == int(scope[len("missing"):])
        if scope.startswith("L"):
            return length == int(scope[1:])
        raise AssertionError(f"Unknown summary scope: {scope}")

    outcome_map = {
        "correct_completion": "correct_completion",
        "false_completion": "false_completion",
        "refusal_correct_state": "refusal_correct",
        "refusal_incorrect_state": "refusal_incorrect",
    }
    summary_comparisons = 0
    summary_keys = set()
    with (results / "summary.csv").open() as handle:
        main_summary = list(csv.DictReader(handle))
    for row in main_summary:
        setting, scope, rule = (row[name] for name in ("setting", "scope", "rule"))
        require((setting, scope, rule) not in summary_keys,
                "Duplicate main summary key")
        summary_keys.add((setting, scope, rule))
        expected = {
            public: sum(value for (s, length, missing, r, o), value in counts.items()
                        if s == setting and r == rule and o == independent
                        and in_scope(scope, length, missing))
            for public, independent in outcome_map.items()
        }
        for name, value in expected.items():
            require(int(row[name]) == value,
                    f"Summary differs: {setting} {scope} {rule} {name}")
            summary_comparisons += 1
        require(int(row["cases"]) == sum(expected.values()),
                f"Summary denominator differs: {setting} {scope} {rule}")
        summary_comparisons += 1
    scopes = ["all"] + [f"L{i}" for i in range(5)] + [
        f"missing{i}" for i in range(5)] + ["L4_missing"]
    expected_summary_keys = {
        (setting, scope, rule)
        for setting in ("tight", "loose", "false")
        for scope in scopes
        for rule in (*RULES, "oracle")
    }
    # Empty scope rows may be omitted. Every nonempty row must be present.
    required_summary_keys = {
        key for key in expected_summary_keys
        if any(s == key[0] and r == key[2] and in_scope(key[1], length, missing)
               for s, length, missing, r, _ in counts)
    }
    require(required_summary_keys <= summary_keys <= expected_summary_keys,
            "Main summary has missing or unexpected keys")

    def total(setting, rule, outcome, missing_only=False):
        return sum(value for (s, _, k, r, o), value in counts.items()
                   if (s, r, o) == (setting, rule, outcome)
                   and (not missing_only or k > 0))

    hypotheses = {
        "H1": all(total(s, "agreement", "false_completion") == 0
                  for s in ("tight", "loose")),
        "H2": total("tight", "agreement", "correct_completion", True)
        > total("tight", "no_loss", "correct_completion", True),
        "H3": total("tight", "replay", "false_completion") > 0,
        "H4": monotonicity_checks == len(cases),
        "H5": total("false", "agreement", "false_completion") > 0,
        "H6": any(len(expected_decisions[key][2]) > 1
                  and len(expected_decisions[key][1]) == 1
                  for setting in ("tight", "loose")
                  for key in bound_observations[setting]),
    }
    observation_stats = {
        setting: {
            "unique_observations": len(keys),
            "zero_targets": sum(not expected_decisions[key][1] for key in keys),
            "one_target": sum(len(expected_decisions[key][1]) == 1 for key in keys),
            "multiple_targets": sum(len(expected_decisions[key][1]) > 1 for key in keys),
            "multiple_histories_one_target": sum(
                len(expected_decisions[key][2]) > 1
                and len(expected_decisions[key][1]) == 1 for key in keys),
        }
        for setting, keys in sorted(bound_observations.items())
    }
    main_json = json.loads((results / "summary.json").read_text())
    require(main_json["case_count"] == len(cases), "JSON case total differs")
    require(main_json["unique_observations_all_settings"] == len(observations),
            "JSON unique observation total differs")
    require(main_json["hypotheses"] == hypotheses, "JSON hypotheses differ")
    json_summary_values = 2 + len(hypotheses)
    for setting, values in observation_stats.items():
        for name, value in values.items():
            main_name = "no_targets" if name == "zero_targets" else name
            require(main_json["observation_counts"][setting][main_name] == value,
                    f"JSON observation count differs: {setting} {name}")
            json_summary_values += 1
    result = {
        "status": "PASS",
        "cases": len(cases),
        "unique_observations": len(observations),
        "main_decisions_checked": len(observations) * len(RULES),
        "case_target_formula_checks": formula_checks,
        "candidate_word_formula_checks": candidate_word_checks,
        "honest_history_membership_checks": honest_membership_checks,
        "monotonicity_checks": monotonicity_checks,
        "hypotheses": hypotheses,
        "observation_stats": observation_stats,
        "independent_joint_summary_rows": independent_rows_written,
        "main_summary_rows_compared": len(main_summary),
        "main_summary_values_compared": summary_comparisons,
        "main_json_summary_values_compared": json_summary_values,
        "independent_negative_and_boundary_controls": negative_controls,
        "first_witnesses_compared": len(witnesses),
        "witness_candidate_words_checked": witness_candidates_checked,
    }
    (results / "independent_check.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    print(f"CPU seconds: {time.process_time() - started:.3f}")


if __name__ == "__main__":
    main()
