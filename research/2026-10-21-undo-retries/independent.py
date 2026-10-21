#!/usr/bin/env python3
"""Independent whole-field prefix evaluator of the frozen undo plan.

This code was built from plan.md and config.json before the evaluator author
read the main implementation or results. It uses one rule equation per field
per attempt. It has no step-level pending flag or slot-event simulation.
"""

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path


FIELDS = [
    "case_id", "setting", "rule", "initial_x", "initial_y", "target_x",
    "target_y", "final_x", "final_y", "done_x", "done_y", "stopped", "claim",
    "correct", "outcome", "applications_x", "applications_y", "changes_x",
    "changes_y", "repeated", "omitted",
]
INVERSE_RULES = {
    "restart_inverse", "before_inverse", "after_inverse",
    "stop_on_uncertainty", "atomic_inverse",
}


def words(alphabet, maximum):
    return [word for n in range(maximum + 1)
            for word in itertools.product(alphabet, repeat=n)]


def cases(config):
    case_id = 0
    for setting in config["settings"]:
        available = words(config["alphabet"], setting["max_word_length"])
        crashes = setting["crashes"]
        for initial in itertools.product(config["initial_values"], repeat=2):
            for cuts in itertools.product(config["cuts"], repeat=crashes):
                for word_ids in itertools.product(range(len(available)), repeat=crashes):
                    case_id += 1
                    yield {
                        "case_id": case_id,
                        "setting": setting["name"],
                        "initial": initial,
                        "cuts": cuts,
                        "external": tuple(available[i] for i in word_ids),
                    }


def word_delta(word):
    dx = dy = 0
    for command in word:
        if command == "x_add1":
            dx += 1
        elif command == "x_sub1":
            dx -= 1
        elif command == "y_add1":
            dy += 1
        elif command == "y_sub1":
            dy -= 1
        else:
            raise ValueError(command)
    return dx, dy


def prefix_result(rule, value, initial, done, prefix):
    """Return value, flag, application count, change count for one field.

    prefix is 0, 1, or 2: the count of this field's logical slots executed.
    The equations collapse the frozen two-slot protocol into a single update.
    """
    if rule == "restart_inverse":
        applied = prefix >= 1
        next_done = False
    elif done:
        return value, done, 0, 0
    elif rule == "before_inverse":
        applied = prefix == 2
        next_done = prefix >= 1
    elif rule in {"after_inverse", "after_set", "stop_on_uncertainty"}:
        applied = prefix >= 1
        next_done = prefix == 2
    elif rule in {"atomic_inverse", "atomic_set"}:
        applied = prefix >= 1
        next_done = prefix >= 1
    else:
        raise ValueError(rule)
    next_value = value
    if applied:
        next_value = initial if rule.endswith("_set") else value - 1
    return next_value, next_done, int(applied), int(next_value != value)


def evaluate(case, rule):
    initial = case["initial"]
    value = [n + 1 for n in initial]
    done = [False, False]
    applications = [0, 0]
    changes = [0, 0]
    stopped = False
    total_delta = [0, 0]
    attempts = list(zip(case["cuts"], case["external"], itertools.repeat(True)))
    attempts.append((4, (), False))
    for cut, external_word, interrupted in attempts:
        if not stopped:
            for field, slot_offset in enumerate((0, 2)):
                prefix = min(2, max(0, cut - slot_offset))
                new, flag, count, changed = prefix_result(
                    rule, value[field], initial[field], done[field], prefix)
                value[field] = new
                done[field] = flag
                applications[field] += count
                changes[field] += changed
        if interrupted and rule == "stop_on_uncertainty":
            stopped = True
        delta = word_delta(external_word)
        for field in (0, 1):
            value[field] += delta[field]
            total_delta[field] += delta[field]
    target = [initial[i] + total_delta[i] for i in (0, 1)]
    claim = rule == "restart_inverse" or all(done)
    correct = value == target
    outcome = ("correct_completion" if correct else "false_completion") if claim else (
        "refusal_correct" if correct else "refusal_incorrect")
    return dict(zip(FIELDS, (
        case["case_id"], case["setting"], rule,
        *initial, *target, *value, *map(int, done), int(stopped), int(claim),
        int(correct), outcome, *applications, *changes,
        int(max(applications) > 1), int(min(applications) < 1),
    )))


def hand_controls():
    records = []

    def check(label, rule, cut, external, expected):
        case = {"case_id": 0, "setting": "hand", "initial": (0, 0),
                "cuts": (cut,), "external": (external,)}
        row = evaluate(case, rule)
        for key, expected_value in expected.items():
            assert row[key] == expected_value, (label, key, row[key], expected_value)
        records.append(label)

    check("saved_intent_omits_effect", "before_inverse", 1, (), {
        "final_x": 1, "final_y": 0, "applications_x": 0,
        "applications_y": 1, "done_x": 1, "done_y": 1,
        "outcome": "false_completion", "omitted": 1})
    check("effect_before_marker_repeats", "after_inverse", 1, (), {
        "final_x": -1, "final_y": 0, "applications_x": 2,
        "applications_y": 1, "outcome": "false_completion", "repeated": 1})
    check("unmarked_restart_repeats_both", "restart_inverse", 4, (), {
        "final_x": -1, "final_y": -1, "applications_x": 2,
        "applications_y": 2, "outcome": "false_completion"})
    check("repeated_assignment_removes_later_edit", "after_set", 1, ("x_add1",), {
        "final_x": 0, "target_x": 1, "applications_x": 2,
        "changes_x": 2, "outcome": "false_completion"})
    check("single_atomic_assignment_removes_later_edit", "atomic_set", 0, ("x_add1",), {
        "final_x": 0, "target_x": 1, "applications_x": 1,
        "applications_y": 1, "outcome": "false_completion", "repeated": 0})
    check("atomic_inverse_preserves_later_edit", "atomic_inverse", 0, ("x_add1",), {
        "final_x": 1, "final_y": 0, "target_x": 1,
        "applications_x": 1, "applications_y": 1,
        "outcome": "correct_completion"})
    check("stop_refuses_after_unmarked_completed_effect", "stop_on_uncertainty", 3, (), {
        "final_x": 0, "final_y": 0, "done_x": 1, "done_y": 0,
        "applications_x": 1, "applications_y": 1, "stopped": 1,
        "outcome": "refusal_correct"})
    check("stop_claims_after_complete_durable_pair", "stop_on_uncertainty", 4, ("x_add1",), {
        "final_x": 1, "final_y": 0, "stopped": 1,
        "outcome": "correct_completion"})
    check("unchanged_assignment_is_still_an_application", "after_set", 1, (), {
        "final_x": 0, "applications_x": 2, "changes_x": 1,
        "outcome": "correct_completion"})
    return records


def compare(main_path, independent_path):
    with Path(main_path).open(newline="") as main_file:
        main = list(csv.DictReader(main_file))
    with Path(independent_path).open(newline="") as own_file:
        own = list(csv.DictReader(own_file))
    assert len(main) == len(own), ("row_count", len(main), len(own))
    checked = 0
    for main_row, independent_row in zip(main, own):
        for field in FIELDS:
            assert main_row[field] == independent_row[field], (
                "mismatch", independent_row["case_id"], independent_row["rule"],
                field, main_row[field], independent_row[field])
            checked += 1
    return {"matched_rows": len(own), "matched_fields": checked, "status": "pass"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--compare", type=Path, help="Optional main outcomes CSV")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    config = json.loads((package / "config.json").read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    controls = hand_controls()
    corpus = list(cases(config))
    assert len(corpus) == 2924
    assert [case["case_id"] for case in corpus] == list(range(1, 2925))
    counts = {setting["name"]: sum(case["setting"] == setting["name"] for case in corpus)
              for setting in config["settings"]}
    assert counts == config["expected_cases"]
    rows = [evaluate(case, rule) for case in corpus for rule in config["rules"]]
    assert len(rows) == 20468
    assert len({(row["case_id"], row["rule"]) for row in rows}) == len(rows)
    inverse_checks = atomic_checks = 0
    for row in rows:
        if row["rule"] in INVERSE_RULES:
            for field in ("x", "y"):
                assert row[f"final_{field}"] - row[f"target_{field}"] == (
                    1 - row[f"applications_{field}"])
                inverse_checks += 1
        if row["rule"] == "atomic_inverse":
            assert row["outcome"] == "correct_completion"
            assert row["applications_x"] == row["applications_y"] == 1
            atomic_checks += 1
    output = args.out / "independent_outcomes.csv"
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    checks = {
        "method": "whole-field prefix equations; no volatile slot-state machine",
        "cases": len(corpus), "outcomes": len(rows), "case_counts": counts,
        "hand_controls": controls, "inverse_field_identities": inverse_checks,
        "atomic_inverse_case_checks": atomic_checks,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outcomes_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    if args.compare:
        checks["comparison"] = compare(args.compare, output)
    (args.out / "independent_checks.json").write_text(
        json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(json.dumps(checks, sort_keys=True))


if __name__ == "__main__":
    main()
