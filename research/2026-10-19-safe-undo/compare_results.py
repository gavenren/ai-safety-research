"""Compare saved outputs through a schema adapter; do not run either model."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


COUNTS = {"scalar_values": 0, "objects": 0, "arrays": 0}


def equal(expected, actual, path):
    if type(expected) is not type(actual):
        raise AssertionError(f"Type mismatch at {path}: {type(expected)} vs {type(actual)}")
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            raise AssertionError(f"Key mismatch at {path}: {set(expected) ^ set(actual)}")
        COUNTS["objects"] += 1
        for key in expected:
            equal(expected[key], actual[key], path + "." + str(key))
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise AssertionError(f"Length mismatch at {path}")
        COUNTS["arrays"] += 1
        for index, (left, right) in enumerate(zip(expected, actual)):
            equal(left, right, path + f"[{index}]")
    else:
        COUNTS["scalar_values"] += 1
        if expected != actual:
            raise AssertionError(f"Value mismatch at {path}: {expected!r} vs {actual!r}")


def xy(record):
    return [record["x"], record["y"]]


def outcome(row):
    return {"after": xy(row["final"]), "complete": row["status"] == "complete",
            **{key: value for key, value in row.items()
               if key not in {"final", "status", "abstain"}}}


def trace(case, number):
    return {
        "case_id": number, "length": case["length"],
        "initial": xy(case["initial"]), "word": case["word"],
        "actual_states": [xy(state) for state in case["actual_trajectory"]],
        "reference_states": [xy(state) for state in case["reference_trajectory"]],
        "revision_counts": [state["x_revision"] for state in case["actual_trajectory"]],
        "survives": [state["agent_contribution_survives"]
                     for state in case["actual_trajectory"]],
        "before": xy(case["pre_undo"]), "target": xy(case["target"]),
        "has_set": case["has_set"],
        "outcomes": {rule: outcome(result) for rule, result in case["outcomes"].items()},
    }


def aggregate_numbers(row):
    keys = ["cases", "correct_final", "changed", "false_confirmation", "wrong_change",
            "collateral_change", "new_damage", "unresolved", "abstain_correct",
            "clean_completion"]
    return {**{key: row[key] for key in keys}, "complete": row["cases"] - row["abstain"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.input_dir
    load = lambda name: json.loads((root / name).read_text())
    independent = load("independent_results.json")
    with gzip.open(root / "independent_cases.jsonl.gz", "rt") as stream:
        cases = [json.loads(line) for line in stream]
    numbered = {case["case_id"]: number for number, case in enumerate(cases)}
    by_id = {case["case_id"]: case for case in cases}
    with gzip.open(root / "traces.jsonl.gz", "rt") as stream:
        main_cases = [json.loads(line) for line in stream]
    equal([trace(case, number) for number, case in enumerate(cases)], main_cases, "traces")

    # Main omits exactly the six empty with-set rows at length zero. The
    # independent file retains them. Main also calls with_set "has_set".
    subset = {"all": "all", "no_set": "no_set", "with_set": "has_set"}
    expected_aggregates = [
        {"length": row["length"], "subset": subset[row["subgroup"]],
         "rule": row["rule"], **aggregate_numbers(row)}
        for row in independent["aggregates"] if row["cases"]
    ]
    with (root / "results.csv").open(newline="") as stream:
        main_aggregates = [{key: value if key in {"subset", "rule"} else int(value)
                            for key, value in row.items()}
                           for row in csv.DictReader(stream)]
    aggregate_order = lambda row: (row["length"], row["subset"], row["rule"])
    equal(sorted(expected_aggregates, key=aggregate_order),
          sorted(main_aggregates, key=aggregate_order), "aggregates")
    lookup = {(row["length"], row["rule"]): row for row in independent["aggregates"]
              if row["subgroup"] == "all"}

    # Independent subgroup paired rows are additional evidence. All 30 rows
    # present in the main file are compared. The false-confirmation paired
    # column follows directly because the control is clean in every case.
    expected_pairs = [
        {"length": row["length"], "rule": row["rule"],
         "abstains_before_correct": row["abstain_pre_correct"],
         "abstains_before_wrong": row["abstain_pre_wrong"],
         "provenance_clean_rule_abstains": row["abstain_total"],
         "provenance_clean_rule_false": lookup[(row["length"], row["rule"])]["false_confirmation"]}
        for row in independent["paired_counts"] if row["subgroup"] == "all"
    ]
    pair_order = lambda row: (row["length"], row["rule"])
    equal(sorted(expected_pairs, key=pair_order),
          sorted(load("paired_results.json"), key=pair_order), "paired_counts")

    def member(case_id):
        case = by_id[case_id]
        return {"case_id": numbered[case_id], "word": case["word"],
                "target": xy(case["target"])}

    expected_groups = [
        {"key": row["observation"], "cases": row["cases"], "ambiguous": row["ambiguous"],
         "targets": {json.dumps(xy(item["target"]), separators=(",", ":")): item["count"]
                     for item in row["target_counts"]},
         "minimum_pair": [member(case_id) for case_id in (row["minimum_pair"] or [])]}
        for row in independent["observation_groups"]
    ]
    group_order = lambda row: row["key"]
    equal(sorted(expected_groups, key=group_order),
          sorted(load("observation_groups.json"), key=group_order), "observation_groups")
    expected_witnesses = {}
    for rule, labels in independent["minimum_failure_cases"].items():
        for label, case in labels.items():
            expected_witnesses[rule + ":" + label] = {
                "case_id": numbered[case["case_id"]], "initial": xy(case["initial"]),
                "word": case["word"], "before": xy(case["pre_undo"]),
                "target": xy(case["target"]), "outcome": outcome(case["outcomes"][rule]),
            }
    equal(expected_witnesses, load("witnesses.json"), "minimum_failure_examples")
    group_counts = []
    for length in range(6):
        selected = [row for row in expected_groups if row["key"][0] == length]
        group_counts.append({"length": length, "groups": len(selected),
                             "ambiguous_groups": sum(row["ambiguous"] for row in selected),
                             "histories_in_ambiguous_groups": sum(row["cases"] for row in selected
                                                                  if row["ambiguous"])})
    first_pair = independent["global_minimum_ambiguity_pair"]
    first_ids = [numbered[case["case_id"]] for case in first_pair]
    first_group = next(row for row in expected_groups
                       if [member["case_id"] for member in row["minimum_pair"]] == first_ids)
    expected_summary = {
        "histories": independent["case_count"], "policy_outcomes": independent["policy_count"],
        "aggregate_rows": len(expected_aggregates), "paired_rows": len(expected_pairs),
        "witnesses": len(expected_witnesses), "hypotheses": independent["hypotheses"],
        "totals": {rule: aggregate_numbers(row) for rule, row in independent["totals"].items()},
        "observation_counts": group_counts, "first_ambiguity": first_group,
    }
    equal(expected_summary, load("summary.json"), "summary")
    inputs = ["traces.jsonl.gz", "results.csv", "paired_results.json", "observation_groups.json",
              "witnesses.json", "summary.json", "independent_cases.jsonl.gz",
              "independent_results.json", "independent_checks.json", "independent_audit.py"]
    result = {
        "status": "PASS", "scope": "All main saved results, with schema conversion only.",
        "model_logic_changed_after_comparison": False,
        "case_count": len(cases), "policy_outcomes": len(cases) * 6,
        "trajectory_state_pairs": sum(len(case["actual_trajectory"]) for case in cases),
        "aggregate_rows_compared": len(expected_aggregates),
        "independent_zero_count_rows_not_in_main": 6,
        "paired_rows_compared": len(expected_pairs),
        "independent_extra_subgroup_paired_rows": 60,
        "observation_groups_compared": len(expected_groups),
        "minimum_ambiguity_pairs_compared": independent["ambiguous_group_count"],
        "minimum_failure_examples_compared": len(expected_witnesses),
        "all_main_summary_fields_compared": True,
        "recursive_comparison_counts": COUNTS,
        "input_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                         for name in inputs},
        "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "comparison.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "case_count", "policy_outcomes",
                                                 "recursive_comparison_counts")}, sort_keys=True))


if __name__ == "__main__":
    main()
