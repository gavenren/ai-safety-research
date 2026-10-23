#!/usr/bin/env python3
"""Independent word-form evaluator for the frozen October 23 receipt study.

This file does not import, execute, or inspect the main policy program.
It calculates a word's final state from its last assignment and flip parity.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import time

ALPHABET = ("set0", "set1", "flip_y")
RULES = ("R0", "R1", "R2", "R3", "R4", "R5")
NAMES = ("ReceiptNow", "ReadNow", "ReadDated", "ReplayNow", "NewKeyNow", "FreshCASNow")
WORDS = tuple(word for n in range(3) for word in itertools.product(ALPHABET, repeat=n))
EXPECTED_PLAN_SHA256 = "c84529e57362e4166643ed400783be8c42c6a79b2993fffa4cbeca104df1d0f4"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state_after(start, word):
    """Closed form: last x assignment wins; parity sets y; length sets v."""
    if len(start) != 3 or start[0] not in (0, 1) or start[1] not in (0, 1):
        raise ValueError("invalid state")
    if type(start[2]) is not int or start[2] < 0:
        raise ValueError("invalid revision")
    if any(command not in ALPHABET for command in word):
        raise ValueError("unknown command")
    assignments = [int(command[-1]) for command in word if command.startswith("set")]
    return (assignments[-1] if assignments else start[0],
            start[1] ^ (word.count("flip_y") % 2), start[2] + len(word))


def evaluate(target, gap_a, gap_b, rule):
    if type(target) is not int or target not in (0, 1) or rule not in RULES:
        raise ValueError("invalid target or rule")
    if tuple(gap_a) not in WORDS or tuple(gap_b) not in WORDS:
        raise ValueError("word outside frozen model")
    initial = (1 - target, 0, 0)
    first = (target, 0, 1)
    at_read = state_after(first, gap_a)
    pre_action = state_after(first, tuple(gap_a) + tuple(gap_b))
    match_read = at_read[0] == target
    mismatched = not match_read
    dispatched = rule in ("R3", "R4", "R5") and mismatched
    accepted = mismatched and (rule == "R4" or (rule == "R5" and not gap_b))
    refused = rule == "R5" and mismatched and bool(gap_b)
    final = (target, pre_action[1], pre_action[2] + 1) if accepted else pre_action
    if rule == "R2" or refused:
        current_claim = None
    elif rule == "R1":
        current_claim = match_read
    else:
        current_claim = True
    action = ("replay" if rule == "R3" and dispatched else
              "write" if accepted else "refuse" if refused else "none")
    read_claim = match_read if rule == "R2" else None
    scores = {
        "false_historical_claim": 0,
        "false_read_point_claim": 0,
        "reply_claim": int(current_claim is not None),
        "false_positive_reply_claim": int(current_claim is True and final[0] != target),
        "false_negative_reply_claim": int(current_claim is False and final[0] == target),
        "unknown_reply_state": int(current_claim is None),
        "extra_effect": int(accepted),
        "target_value_overwrite": int(accepted and pre_action[0] != target),
        "unrelated_field_damage": int(final[1] != pre_action[1]),
        "reads": int(rule != "R0"),
        "dispatches": int(dispatched),
        "receipt_hits": int(rule == "R3" and dispatched),
        "accepted_new_writes": int(accepted),
        "condition_refusals": int(refused),
    }
    return {
        "target": target, "gap_a": list(gap_a), "gap_b": list(gap_b), "rule": rule,
        "initial": list(initial), "first": list(first),
        "observed": list(at_read) if rule != "R0" else None,
        "pre_action": list(pre_action), "final": list(final),
        "action": action, "original_applied_claim": True,
        "read_claim": read_claim, "current_claim": current_claim,
        "condition_evaluated": int(rule == "R5" and dispatched),
        "scores": scores,
    }


def complement(word):
    return tuple({"set0": "set1", "set1": "set0", "flip_y": "flip_y"}[x] for x in word)


def self_check():
    """Fixed manual cases and proofs independent of main outputs."""
    checks = []
    def require(name, value):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    require("word_count", len(WORDS) == 13 and len(set(WORDS)) == 13)
    require("unchanged_value_write_advances_revision", state_after((1, 0, 1), ("set1",)) == (1, 0, 2))
    require("unrelated_write_preserves_target", state_after((1, 0, 1), ("flip_y",)) == (1, 1, 2))
    require("return_changes_revision", state_after((1, 0, 1), ("set0", "set1")) == (1, 0, 3))
    require("last_assignment", state_after((1, 0, 1), ("flip_y", "set0")) == (0, 1, 3))
    for target in (0, 1):
        same = f"set{target}"
        other = f"set{1 - target}"
        for rule in RULES:
            r = evaluate(target, (), (), rule)
            require(f"clean_empty_{target}_{rule}", not r["scores"]["false_positive_reply_claim"] and not r["scores"]["extra_effect"])
        r = evaluate(target, (other,), (), "R3")
        require(f"replay_still_mismatch_{target}", r["action"] == "replay" and r["final"][0] != target and r["scores"]["false_positive_reply_claim"] == 1)
        r = evaluate(target, (other,), (same,), "R1")
        require(f"false_negative_after_return_{target}", r["current_claim"] is False and r["scores"]["false_negative_reply_claim"] == 1)
        r = evaluate(target, (), (other,), "R1")
        require(f"false_positive_after_read_{target}", r["current_claim"] is True and r["scores"]["false_positive_reply_claim"] == 1)
        r = evaluate(target, (other,), (same,), "R4")
        require(f"same_value_extra_effect_{target}", r["scores"]["extra_effect"] == 1 and r["scores"]["target_value_overwrite"] == 0)
        r = evaluate(target, (other,), (), "R5")
        require(f"conditional_unauthorized_effect_{target}", r["action"] == "write" and r["scores"]["extra_effect"] == 1)
        r = evaluate(target, (other,), ("flip_y",), "R5")
        require(f"unrelated_revision_refusal_{target}", r["action"] == "refuse" and r["current_claim"] is None)
        r = evaluate(target, (), (other,), "R5")
        require(f"matching_read_skips_guard_{target}", r["condition_evaluated"] == 0 and r["scores"]["false_positive_reply_claim"] == 1)
        for gap_a, gap_b in itertools.product(WORDS, repeat=2):
            for rule in RULES:
                row = evaluate(target, gap_a, gap_b, rule)
                opposite = evaluate(1-target, complement(gap_a), complement(gap_b), rule)
                require(f"symmetry_{target}_{gap_a}_{gap_b}_{rule}", row["scores"] == opposite["scores"] and row["action"] == opposite["action"] and row["current_claim"] == opposite["current_claim"])
                require(f"cost_{target}_{gap_a}_{gap_b}_{rule}", row["scores"]["dispatches"] == row["scores"]["receipt_hits"] + row["scores"]["accepted_new_writes"] + row["scores"]["condition_refusals"])
                if rule == "R5":
                    require(f"guard_cost_{target}_{gap_a}_{gap_b}", row["condition_evaluated"] == row["scores"]["accepted_new_writes"] + row["scores"]["condition_refusals"])
    for invalid in ((2, (), (), "R0"), (1, ("bad",), (), "R0"), (1, (), (), "R6")):
        try:
            evaluate(*invalid)
        except ValueError:
            checks.append("invalid_input_rejected")
        else:
            raise AssertionError("invalid input accepted")
    return checks


def predicted_totals():
    # A has eight matching and five mismatching words for each target.
    # Starting from a mismatch, B has five matching and eight mismatching words.
    targets, match, mismatch, words = 2, 8, 5, 13
    return {
        "R0": {"false_positive_reply_claim": targets * (match*mismatch + mismatch*match)},
        "R1": {"false_positive_reply_claim": targets*match*mismatch,
               "false_negative_reply_claim": targets*mismatch*mismatch},
        "R2": {"reply_claim": 0, "unknown_reply_state": targets*words*words},
        "R3": {"false_positive_reply_claim": targets*(match*mismatch + mismatch*match),
               "receipt_hits": targets*mismatch*words, "extra_effect": 0},
        "R4": {"false_positive_reply_claim": targets*match*mismatch,
               "extra_effect": targets*mismatch*words,
               "target_value_overwrite": targets*mismatch*match},
        "R5": {"false_positive_reply_claim": targets*match*mismatch,
               "extra_effect": targets*mismatch,
               "target_value_overwrite": targets*mismatch,
               "condition_refusals": targets*mismatch*(words-1)},
    }


def make_rows():
    return [evaluate(target, gap_a, gap_b, rule)
            for target, gap_a, gap_b, rule in itertools.product((0, 1), WORDS, WORDS, RULES)]


def paired_examples():
    pairs = [
        ("same_receipt_different_reply_truth", evaluate(1, (), (), "R0"), evaluate(1, (), ("set0",), "R0")),
        ("same_read_different_reply_truth", evaluate(1, (), (), "R1"), evaluate(1, (), ("set0",), "R1")),
        ("same_read_conditional_write_or_refusal", evaluate(1, ("set0",), (), "R5"), evaluate(1, ("set0",), ("flip_y",), "R5")),
    ]
    assert pairs[0][1]["current_claim"] == pairs[0][2]["current_claim"]
    assert pairs[0][1]["final"][0] != pairs[0][2]["final"][0]
    assert pairs[1][1]["observed"] == pairs[1][2]["observed"]
    assert pairs[1][1]["scores"]["false_positive_reply_claim"] != pairs[1][2]["scores"]["false_positive_reply_claim"]
    assert pairs[2][1]["observed"] == pairs[2][2]["observed"]
    assert pairs[2][1]["action"] == "write" and pairs[2][2]["action"] == "refuse"
    return [{"name": name, "left": left, "right": right} for name, left, right in pairs]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-results", type=Path)
    parser.add_argument("--out", type=Path, default=Path("independent_results"))
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    cpu_start = time.process_time()
    root = Path(__file__).resolve().parent
    if digest(root / "plan.md") != EXPECTED_PLAN_SHA256:
        raise ValueError("plan hash differs from the frozen plan")
    names = self_check()
    rows = make_rows()
    if len(rows) != 2028:
        raise AssertionError("wrong corpus size")
    aggregate = {rule: {key: sum(r["scores"][key] for r in rows if r["rule"] == rule)
                        for key in rows[0]["scores"]} for rule in RULES}
    for rule, fields in predicted_totals().items():
        for field, expected in fields.items():
            if aggregate[rule][field] != expected:
                raise AssertionError((rule, field, aggregate[rule][field], expected))
    for target in (0, 1):
        for initial_x, expected_match in ((target, 8), (1-target, 5)):
            assert sum(state_after((initial_x, 0, 0), word)[0] == target for word in WORDS) == expected_match
    comparison = {"status": "not_requested"}
    if args.main_results:
        comparison = compare_main(args.main_results, rows)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "rows.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    (args.out / "summary.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    (args.out / "paired_examples.json").write_text(json.dumps(paired_examples(), indent=2, sort_keys=True) + "\n")
    receipt = {"status": "pass", "started_utc": started,
               "finished_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "platform": platform.platform(),
               "command": sys.argv, "cpu_seconds": time.process_time() - cpu_start,
               "code_sha256": digest(__file__), "plan_sha256": EXPECTED_PLAN_SHA256,
               "histories": 338, "rule_outcomes": len(rows),
               "manual_symmetry_cost_checks": len(names), "comparison": comparison,
               "main_code_read_or_imported": False}
    (args.out / "execution.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


def compare_main(path, independent_rows):
    """Only the author's data schema is shared; policy evaluation remains separate."""
    score_map = {
        "false_history": "false_historical_claim", "false_dated": "false_read_point_claim",
        "reply_claims": "reply_claim", "false_positive": "false_positive_reply_claim",
        "false_negative": "false_negative_reply_claim", "unknown": "unknown_reply_state",
        "extra_effects": "extra_effect", "overwrites": "target_value_overwrite",
        "unrelated_damage": "unrelated_field_damage", "reads": "reads",
        "dispatches": "dispatches", "receipt_hits": "receipt_hits",
        "accepted_new_writes": "accepted_new_writes", "condition_refusals": "condition_refusals",
    }
    action_names = {"none": "none", "replay": "original_receipt_replay",
                    "write": "new_key_effect", "refuse": "condition_refused"}
    expected_by_key = {(r["target"], tuple(r["gap_a"]), tuple(r["gap_b"]), r["rule"]): r for r in independent_rows}
    seen = set()
    scalar_checks = 0
    trace_events = 0

    def state(values):
        return dict(zip(("x", "y", "v"), values)) if values is not None else None

    def same(actual, expected, name):
        nonlocal scalar_checks
        if type(actual) is not type(expected):
            raise AssertionError((name, "type", type(actual).__name__, type(expected).__name__))
        if isinstance(expected, dict):
            if set(actual) != set(expected):
                raise AssertionError((name, "keys", set(actual), set(expected)))
            for key in expected:
                same(actual[key], expected[key], name + "." + key)
        elif isinstance(expected, list):
            if len(actual) != len(expected):
                raise AssertionError((name, "length", len(actual), len(expected)))
            for index, (a, e) in enumerate(zip(actual, expected)):
                same(a, e, f"{name}[{index}]")
        else:
            scalar_checks += 1
            if actual != expected:
                raise AssertionError((name, actual, expected))

    for line_number, line in enumerate(Path(path).read_text().splitlines(), start=1):
        actual = json.loads(line)
        key = (actual["target"], tuple(actual["A"]), tuple(actual["B"]), actual["rule"])
        if key in seen or key not in expected_by_key:
            raise AssertionError((line_number, "duplicate or unexpected case", key))
        seen.add(key)
        row = expected_by_key[key]
        a, b, target, rule = row["gap_a"], row["gap_b"], row["target"], row["rule"]
        receipt = {"account": "synthetic-account", "effect_number": 1, "key": "original",
                   "payload": {"set_x": target}, "post_revision": 1, "target": "synthetic-record"}
        claims = {"original_applied": True, "current_match": row["current_claim"],
                  "read_match": row["read_claim"], "read_point": len(a) + 2 if rule == "R2" else None}
        scores = {main: row["scores"][own] for main, own in score_map.items()}
        scores.update({"dated_claims": int(rule == "R2"),
                       "reply_positive_claims": int(row["current_claim"] is True),
                       "reply_negative_claims": int(row["current_claim"] is False)})
        trace = []

        def event(kind, values, detail=None):
            trace.append({"point": len(trace), "kind": kind, "detail": detail, "state": state(values)})

        event("initial", row["initial"])
        event("first_effect_and_receipt", row["first"], receipt)
        for index, command in enumerate(a):
            event("external_A", state_after(tuple(row["first"]), tuple(a[:index+1])), command)
        if rule != "R0":
            event("atomic_read", row["observed"])
        for index, command in enumerate(b):
            event("external_B", state_after(tuple(row["first"]), tuple(a + b[:index+1])), command)
        if row["action"] == "replay":
            event("original_receipt_replay", row["final"], receipt)
        elif row["action"] == "write":
            event("new_key_effect", row["final"], {"expected_revision": row["observed"][2] if rule == "R5" else None,
                  "key": "repair", "set_x": target})
        elif row["action"] == "refuse":
            event("condition_refused", row["final"], {"expected_revision": row["observed"][2], "new_key": "repair"})
        event("reply", row["final"], claims)
        expected = {"history_id": f"t{target}-a{WORDS.index(tuple(a)):02d}-b{WORDS.index(tuple(b)):02d}",
                    "target": target, "A": a, "B": b, "rule": rule, "receipt": receipt,
                    "read": state(row["observed"]), "baseline": state(row["pre_action"]),
                    "final": state(row["final"]), "action": action_names[row["action"]],
                    "claims": claims, "scores": scores, "trace": trace}
        same(actual, expected, f"row{line_number}")
        trace_events += len(trace)
    if seen != set(expected_by_key):
        raise AssertionError("missing independent cases")
    return {"status": "pass", "main_results_sha256": digest(path),
            "rule_outcomes": len(seen), "scalar_values_compared": scalar_checks,
            "trace_events_compared": trace_events,
            "fields": "every case field, every score, every trace event, and every receipt"}


if __name__ == "__main__":
    main()
