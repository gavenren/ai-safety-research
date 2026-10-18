#!/usr/bin/env python3
"""Independent tick-loop implementation of the frozen finite-retention plan.

Only Python's standard library is used. The first implementation was made
without access to analyze.py, tests.py, or the main output. Time advances one
integer tick at a time. This implementation does not use a priority queue.
"""
from __future__ import annotations

import argparse
import copy
import csv
import gzip
import hashlib
import itertools
import json
from pathlib import Path

POLICIES = ["no_retry", "new_key", "stable_key", "send_cutoff", "delay_margin", "receiver_cutoff", "permanent"]
LABELS = ["duplicate", "confirmed", "false_exact_claim", "wrong_at_receipt", "late_duplicate", "future_only_false", "missed", "unconfirmed_one", "unconfirmed_duplicate", "clean_confirmed"]
MEASURES = ["effects", "sends", "arrivals", "cache_hits", "rejected_arrivals", "expired_key_encounters"]
ERRORS = ["duplicate", "false_exact_claim", "future_only_false", "late_duplicate"]
CONFIG_KEYS = {"schema_version", "slots", "retention_ticks", "delay_bounds", "spacings", "policies", "stress", "primary", "cost_example", "expiry", "cache_hit_renews", "tie_order", "first_send_always", "drain_after_receipt"}


def _int(value, minimum):
    if type(value) is not int or value < minimum:
        raise ValueError("Invalid integer")


def validate(config):
    if type(config) is not dict or set(config) != CONFIG_KEYS:
        raise ValueError("Invalid config keys")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ValueError("Invalid schema")
    if type(config["slots"]) is not int or config["slots"] != 3:
        raise ValueError("Exactly three slots are required")
    for key, minimum in (("retention_ticks", 1), ("delay_bounds", 0), ("spacings", 1)):
        arr = config[key]
        if type(arr) is not list or not arr or len(arr) != len(set(arr)):
            raise ValueError("Invalid grid")
        for item in arr:
            _int(item, minimum)
    if config["policies"] != POLICIES:
        raise ValueError("Invalid policy order")
    for key in ("stress", "primary", "cost_example"):
        fields = {"retention", "actual_delay_bound", "spacing"}
        if key == "stress":
            fields.add("declared_delay_bound")
        value = config[key]
        if type(value) is not dict or set(value) != fields:
            raise ValueError("Invalid setting")
        for k, v in value.items():
            _int(v, 0 if k.endswith("delay_bound") else 1)
    for key in ("primary", "cost_example"):
        setting = config[key]
        for field, grid in (("retention", "retention_ticks"), ("actual_delay_bound", "delay_bounds"), ("spacing", "spacings")):
            if setting[field] not in config[grid]:
                raise ValueError("Display setting is outside the main grid")
    expected = {
        "expiry": "arrival_minus_creation_greater_than_or_equal_retention",
        "cache_hit_renews": False,
        "tie_order": "prior_arrivals_by_slot_then_send_then_zero_delay_arrival",
        "first_send_always": True,
        "drain_after_receipt": True,
    }
    for key, value in expected.items():
        if type(config[key]) is not type(value) or config[key] != value:
            raise ValueError("Unsupported model option")


def run(T, D, s, B, policy, codes):
    """Return one complete run. Each receipt is part of its arrival event."""
    effects = 0
    table = {}
    pending = []
    events = []
    counts = {key: 0 for key in MEASURES if key != "effects"}
    first_receipt = None
    receipt_index = None
    append_indices = []

    def record(kind, time, slot, **fields):
        event = {"index": len(events), "time": time, "slot": slot, "kind": kind}
        event.update(fields)
        events.append(event)
        return event["index"]

    def arrive(time, slot):
        nonlocal effects, first_receipt, receipt_index
        code = codes[slot]
        key = slot if policy == "new_key" else 0
        counts["arrivals"] += 1
        if policy == "receiver_cutoff" and time >= T:
            counts["rejected_arrivals"] += 1
            record("arrival", time, slot, key=key, outcome="reject", expired=False,
                   effect=None, visible=False, effects=effects)
            return
        entry = table.get(key)
        expired = entry is not None and policy != "permanent" and time - entry[0] >= T
        if expired:
            counts["expired_key_encounters"] += 1
        if entry is None or expired:
            effects += 1
            table[key] = (time, effects)
            effect = effects
            outcome = "append"
        else:
            counts["cache_hits"] += 1
            effect = entry[1]
            outcome = "hit"
        visible = code % 2 == 0
        index = record("arrival", time, slot, key=key, outcome=outcome, expired=expired,
                       effect=effect, visible=visible, effects=effects)
        if outcome == "append":
            append_indices.append((effects, index))
        if visible and first_receipt is None:
            first_receipt = {"time": time, "effect": effect, "effects": effects}
            receipt_index = index

    # This fixed upper time covers all three slots and every possible delay.
    for time in range(2 * s + D + 1):
        prior = sorted(slot for arrival, slot in pending if arrival == time)
        for slot in prior:
            arrive(time, slot)
        pending = [(arrival, slot) for arrival, slot in pending if arrival != time]
        if time % s != 0 or time // s > 2:
            continue
        slot = time // s
        if first_receipt is not None:
            record("skip", time, slot, reason="receipt")
            continue
        permitted = slot == 0
        if slot > 0:
            if policy in ("new_key", "stable_key", "permanent"):
                permitted = True
            elif policy in ("send_cutoff", "receiver_cutoff"):
                permitted = time < T
            elif policy == "delay_margin":
                permitted = time + B < T
        if not permitted:
            record("skip", time, slot, reason="policy")
            continue
        counts["sends"] += 1
        key = slot if policy == "new_key" else 0
        record("send", time, slot, key=key, code=codes[slot])
        if codes[slot] != 0:
            delay = (codes[slot] - 1) // 2
            if delay == 0:
                arrive(time, slot)
            else:
                pending.append((time + delay, slot))
    assert not pending
    confirmed = first_receipt is not None
    at_receipt = first_receipt["effects"] if confirmed else None
    row = {
        "effects": effects,
        **counts,
        "first_receipt_time": first_receipt["time"] if confirmed else None,
        "first_receipt_effect": first_receipt["effect"] if confirmed else None,
        "effects_at_receipt": at_receipt,
        "final_event_time": events[-1]["time"],
        "duplicate": effects > 1,
        "confirmed": confirmed,
        "false_exact_claim": confirmed and effects != 1,
        "wrong_at_receipt": confirmed and at_receipt > 1,
        "late_duplicate": confirmed and any(n > 1 and index > receipt_index for n, index in append_indices),
        "future_only_false": confirmed and effects > 1 and at_receipt == 1,
        "missed": effects == 0,
        "unconfirmed_one": effects == 1 and not confirmed,
        "unconfirmed_duplicate": effects > 1 and not confirmed,
        "clean_confirmed": confirmed and effects == 1,
        "events": events,
    }
    assert sum(row[x] for x in ["missed", "unconfirmed_one", "unconfirmed_duplicate", "clean_confirmed", "false_exact_claim"]) == 1
    assert counts["arrivals"] == effects + counts["cache_hits"] + counts["rejected_arrivals"]
    assert counts["sends"] <= 3 and counts["arrivals"] <= counts["sends"]
    assert row["false_exact_claim"] == (row["wrong_at_receipt"] or row["future_only_false"])
    assert not row["future_only_false"] or row["late_duplicate"]
    if policy == "new_key":
        assert effects == counts["arrivals"] and counts["cache_hits"] == 0
    if policy in ("no_retry", "new_key", "receiver_cutoff", "permanent"):
        assert counts["expired_key_encounters"] == 0
    if policy != "receiver_cutoff":
        assert counts["rejected_arrivals"] == 0
    return row


def settings(config):
    for T, D, s in itertools.product(config["retention_ticks"], config["delay_bounds"], config["spacings"]):
        yield {"grid": "main", "T": T, "D": D, "s": s, "B": D}
    st = config["stress"]
    yield {"grid": "stress", "T": st["retention"], "D": st["actual_delay_bound"], "s": st["spacing"], "B": st["declared_delay_bound"]}


def _arguments(setting, policy, codes):
    return setting["T"], setting["D"], setting["s"], setting["B"], policy, codes


def manual_controls():
    checks = []
    def check(name, condition):
        assert condition, name
        checks.append(name)
    for policy in POLICIES:
        row = run(3, 2, 1, 2, policy, (0, 0, 0))
        check("all_drop_" + policy, row["effects"] == 0 and not row["confirmed"])
        row = run(3, 2, 1, 2, policy, (2, 2, 2))
        check("immediate_visible_" + policy, row["effects"] == 1 and row["sends"] == 1 and row["confirmed"])
    # Lost initial reply. Slot 1 arrives before, at, and after the expiry.
    for spacing, expected in ((1, 1), (2, 2), (3, 2)):
        row = run(2, 0, spacing, 0, "stable_key", (1, 2, 0))
        check("expiry_spacing_" + str(spacing), row["effects"] == expected)
    row = run(2, 0, 1, 0, "stable_key", (1, 1, 2))
    check("hit_does_not_renew", row["effects"] == 2 and row["cache_hits"] == 1 and row["expired_key_encounters"] == 1)
    # Second request succeeds at t=1. The first request creates a second effect at t=3.
    row = run(2, 3, 1, 3, "send_cutoff", (7, 2, 0))
    check("late_first_after_receipt", row["future_only_false"] and row["first_receipt_time"] == 1 and row["final_event_time"] == 3)
    row = run(2, 2, 1, 2, "receiver_cutoff", (6, 0, 0))
    check("receiver_deadline_equality", row["rejected_arrivals"] == 1 and row["effects"] == 0)
    row = run(1, 3, 1, 3, "delay_margin", (8, 2, 2))
    check("initial_send_exception", row["effects"] == 1 and row["sends"] == 1 and row["first_receipt_time"] == 3)
    row = run(3, 2, 1, 2, "stable_key", (4, 2, 2))
    check("arrival_precedes_same_tick_send", row["sends"] == 1 and row["first_receipt_time"] == 1)
    row = run(1, 3, 1, 3, "new_key", (7, 5, 4))
    # All three arrive at t=3, in slot order. A receipt at the final arrival is not late.
    check("same_tick_slot_order", [x["slot"] for x in row["events"] if x["kind"] == "arrival"] == [0, 1, 2] and row["wrong_at_receipt"] and not row["late_duplicate"])
    row = run(1, 3, 1, 3, "new_key", (8, 5, 3))
    check("same_tick_late_after_first_receipt", row["first_receipt_time"] == 3 and row["late_duplicate"] and row["future_only_false"])
    row = run(3, 2, 1, 1, "delay_margin", (1, 6, 0))
    check("broken_bound_duplicate", row["effects"] == 2 and row["false_exact_claim"])
    # A bound greater than the actual delay can only remove allowed retries.
    for B in (2, 3, 4):
        for codes in itertools.product(range(7), repeat=3):
            row = run(4, 2, 1, B, "delay_margin", codes)
            assert not row["duplicate"]
    checks.append("larger_bound_exhaustive_1029_runs")
    return checks


def invalid_controls(config):
    bad = []
    for key in CONFIG_KEYS:
        item = copy.deepcopy(config)
        del item[key]
        bad.append(item)
    for key, value in (("slots", True), ("slots", 2), ("schema_version", True),
                       ("retention_ticks", [0]), ("delay_bounds", [-1]), ("spacings", [0]),
                       ("retention_ticks", [True]), ("spacings", []), ("delay_bounds", [1, 1]),
                       ("policies", list(reversed(POLICIES))), ("cache_hit_renews", 0),
                       ("first_send_always", 1), ("drain_after_receipt", False),
                       ("tie_order", "other"), ("expiry", "other")):
        item = copy.deepcopy(config)
        item[key] = value
        bad.append(item)
    for setting, field, value in (("stress", "declared_delay_bound", -1), ("stress", "actual_delay_bound", True), ("primary", "retention", 99), ("cost_example", "spacing", 99)):
        item = copy.deepcopy(config)
        item[setting][field] = value
        bad.append(item)
    item = copy.deepcopy(config)
    item["unexpected"] = 0
    bad.append(item)
    for index, item in enumerate(bad):
        try:
            validate(item)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("Invalid config accepted: " + str(index))
    return len(bad)


def dump(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def audit(config):
    aggregate = []
    pairs = []
    witnesses = []
    row_count = 0
    event_count = 0
    for setting in settings(config):
        aggregates = {p: {**setting, "policy": p, "assignments": 0, **{m: 0 for m in MEASURES + LABELS}} for p in POLICIES}
        paired = {p: {**setting, "policy": p, "assignments": 0, "permanent_effect_rule_none": 0, "permanent_confirms_rule_not": 0, "rule_duplicate_permanent_not": 0, "rule_clean_permanent_none": 0} for p in POLICIES}
        best = {}
        for codes in itertools.product(range(2 * setting["D"] + 3), repeat=3):
            runs = {p: run(*_arguments(setting, p, codes)) for p in POLICIES}
            permanent = runs["permanent"]
            for policy in ("new_key", "stable_key"):
                for measure in ("sends", "arrivals", "first_receipt_time", "confirmed"):
                    assert runs[policy][measure] == permanent[measure]
            assert runs["new_key"]["effects"] >= runs["stable_key"]["effects"] >= permanent["effects"]
            for policy, row in runs.items():
                row_count += 1
                event_count += len(row["events"])
                agg = aggregates[policy]
                agg["assignments"] += 1
                for m in MEASURES + LABELS:
                    agg[m] += row[m]
                pair = paired[policy]
                pair["assignments"] += 1
                pair["permanent_effect_rule_none"] += permanent["effects"] > 0 and row["effects"] == 0
                pair["permanent_confirms_rule_not"] += permanent["confirmed"] and not row["confirmed"]
                pair["rule_duplicate_permanent_not"] += row["duplicate"] and not permanent["duplicate"]
                pair["rule_clean_permanent_none"] += row["clean_confirmed"] and not permanent["clean_confirmed"]
                order = (row["sends"], row["arrivals"], row["final_event_time"], codes)
                for error in ERRORS:
                    if row[error] and ((policy, error) not in best or order < best[(policy, error)][0]):
                        best[(policy, error)] = (order, {**setting, "policy": policy, "label": error, "codes": list(codes), "outcome": row})
                if setting["grid"] == "main" and policy in ("no_retry", "delay_margin", "receiver_cutoff", "permanent"):
                    assert not row["duplicate"] and not row["false_exact_claim"]
                if setting["grid"] == "stress" and policy in ("no_retry", "receiver_cutoff", "permanent"):
                    assert not row["duplicate"]
        aggregate.extend(aggregates[p] for p in POLICIES)
        pairs.extend(paired[p] for p in POLICIES)
        witnesses.extend(best[k][1] for k in sorted(best))
        q = 2 * setting["D"] + 3
        assert aggregates["no_retry"]["missed"] == q ** 2
        assert aggregates["no_retry"]["clean_confirmed"] == (setting["D"] + 1) * q ** 2
        assert aggregates["permanent"]["missed"] == 1
        assert aggregates["permanent"]["clean_confirmed"] == q ** 3 - (setting["D"] + 2) ** 3
    return aggregate, pairs, witnesses, row_count, event_count


SETTING_NAMES = {"grid": "suite", "T": "retention", "D": "actual_delay_bound", "s": "spacing", "B": "declared_delay_bound"}
MEASURE_NAMES = {"effects": "effect_count", "sends": "send_count", "arrivals": "arrival_count", "cache_hits": "cache_hits", "rejected_arrivals": "receiver_rejections", "expired_key_encounters": "expired_keys"}
PAIR_NAMES = {"permanent_effect_rule_none": "missed_vs_permanent_effect", "permanent_confirms_rule_not": "unconfirmed_vs_permanent_confirmed", "rule_duplicate_permanent_not": "duplicate_vs_permanent_clean", "rule_clean_permanent_none": "clean_confirmed_vs_permanent_unconfirmed"}


def main_setting(setting):
    return {v: setting[k] for k, v in SETTING_NAMES.items()}


def main_format(setting, policy, codes, row):
    """Output-only schema conversion, added after independent results existed."""
    events = []
    effects = []
    first_receipt_index = None
    for event in row["events"]:
        converted = {"kind": event["kind"], "tick": event["time"], "slot": event["slot"]}
        if event["kind"] == "send":
            converted.update(key=event["key"], code=event["code"])
        elif event["kind"] == "skip":
            converted["reason"] = "receipt" if event["reason"] == "receipt" else ("send_cutoff" if policy == "receiver_cutoff" else policy)
        else:
            converted.update(key=event["key"], action={"append": "append", "hit": "cache_hit", "reject": "reject_deadline"}[event["outcome"]],
                             effect_count=event["effects"], effect_id=event["effect"], expired=event["expired"], visible_success=event["visible"])
            if event["outcome"] == "append":
                effects.append({"effect_id": event["effect"], "event_index": event["index"], "slot": event["slot"], "tick": event["time"]})
            if event["visible"] and first_receipt_index is None:
                first_receipt_index = event["index"]
        events.append(converted)
    result = {**main_setting(setting), "policy": policy, "codes": list(codes)}
    result.update({external: row[internal] for internal, external in MEASURE_NAMES.items()})
    result.update({key: row[key] for key in LABELS})
    result.update(events=events, effects=effects,
                  arrived_slots=[e["slot"] for e in events if e["kind"] == "arrival"],
                  sent_slots=[e["slot"] for e in events if e["kind"] == "send"],
                  first_receipt_time=row["first_receipt_time"], first_receipt_effect_id=row["first_receipt_effect"],
                  first_receipt_event_index=first_receipt_index,
                  effect_count_at_receipt=row["effects_at_receipt"], final_event_time=row["final_event_time"])
    return result


def compare_main(config, directory, aggregate, pairs, witnesses):
    rows = 0
    events = 0
    scalar_checks = 0
    with gzip.open(directory / "traces.jsonl.gz", "rt", encoding="utf-8") as handle:
        for setting in settings(config):
            for codes in itertools.product(range(2 * setting["D"] + 3), repeat=3):
                for policy in POLICIES:
                    actual = json.loads(next(handle))
                    expected = main_format(setting, policy, codes, run(*_arguments(setting, policy, codes)))
                    if expected != actual:
                        difference = {key: {"independent": expected.get(key), "main": actual.get(key)} for key in expected.keys() | actual.keys() if expected.get(key) != actual.get(key)}
                        raise AssertionError(json.dumps({"setting": setting, "policy": policy, "codes": codes, "difference": difference}, sort_keys=True))
                    rows += 1
                    events += len(expected["events"])
                    scalar_checks += sum(not isinstance(value, (list, dict)) for value in expected.values())
        assert handle.read() == "", "Extra main trace rows"
    expected_csv = []
    for row in aggregate:
        normalized = {**main_setting(row), "policy": row["policy"], "assignments": row["assignments"]}
        normalized.update({key: row[key] for key in LABELS})
        normalized.update({external: row[internal] for internal, external in MEASURE_NAMES.items()})
        expected_csv.append({key: str(value) for key, value in normalized.items()})
    with (directory / "results.csv").open() as handle:
        assert list(csv.DictReader(handle)) == expected_csv, "Aggregate mismatch"
    expected_pairs = []
    for row in pairs:
        normalized = {**main_setting(row), "policy": row["policy"], "assignments": row["assignments"]}
        normalized.update({external: row[internal] for internal, external in PAIR_NAMES.items()})
        expected_pairs.append(normalized)
    assert json.loads((directory / "paired_results.json").read_text()) == expected_pairs, "Pair mismatch"
    def witness_key(item):
        trace = item["trace"]
        return tuple(trace[key] for key in ["suite", "retention", "actual_delay_bound", "spacing", "declared_delay_bound", "policy"]) + (item["label"],)
    expected_witnesses = {}
    for row in witnesses:
        outcome = row["outcome"]
        item = {"label": row["label"], "rank": [outcome["sends"], outcome["arrivals"], outcome["final_event_time"], row["codes"]],
                "trace": main_format(row, row["policy"], row["codes"], outcome)}
        expected_witnesses[witness_key(item)] = item
    actual_witness_list = json.loads((directory / "witnesses.json").read_text())
    actual_witnesses = {witness_key(row): row for row in actual_witness_list}
    assert len(actual_witnesses) == len(actual_witness_list), "Duplicate witness keys"
    assert expected_witnesses == actual_witnesses, "Minimum witness mismatch"
    main_rows = [row for row in aggregate if row["grid"] == "main"]
    stress_rows = [row for row in aggregate if row["grid"] == "stress"]
    hypotheses = {
        "H1": all(any(r["policy"] == p and r["duplicate"] for r in main_rows) for p in ["stable_key", "send_cutoff"]),
        "H2": all(not r["duplicate"] and not r["false_exact_claim"] for r in main_rows if r["policy"] in ["no_retry", "delay_margin", "receiver_cutoff", "permanent"]),
        "H3": any(r["policy"] == "send_cutoff" and r["future_only_false"] for r in main_rows),
        "H4": all(any(r["grid"] == "main" and r["policy"] == p and r["permanent_effect_rule_none"] for r in pairs) for p in ["delay_margin", "receiver_cutoff"]),
        "H5": any(r["policy"] == "delay_margin" and r["duplicate"] for r in stress_rows) and all(not r["duplicate"] for r in stress_rows if r["policy"] in ["receiver_cutoff", "permanent"]),
    }
    expected_summary = {"aggregate_rows": len(aggregate), "hypotheses": hypotheses,
        "main_policy_rows": sum(r["assignments"] for r in main_rows), "main_scenarios": sum(r["assignments"] for r in main_rows if r["policy"] == "permanent"), "main_settings": len(main_rows) // len(POLICIES),
        "paired_rows": len(pairs), "stress_policy_rows": sum(r["assignments"] for r in stress_rows), "stress_scenarios": sum(r["assignments"] for r in stress_rows if r["policy"] == "permanent"), "stress_settings": len(stress_rows) // len(POLICIES),
        "total_events": events, "total_policy_rows": rows, "witnesses": len(witnesses)}
    assert expected_summary == json.loads((directory / "summary.json").read_text()), "Summary mismatch"
    return {"status": "PASS", "full_trace_rows": rows, "full_trace_events": events, "trace_scalar_values_compared": scalar_checks,
            "aggregate_rows": len(aggregate), "paired_rows": len(pairs), "minimum_witnesses_with_complete_traces": len(witnesses),
            "summary_and_hypotheses_match": True,
            "comparison_scope": "Every main trace key and value, including all event fields, effects, sent/arrived slots, scalar outcomes, and assignment identifiers; exact aggregate rows, paired rows, and minimum witnesses after field-name conversion",
            "independence_note": "Only main output data was read after the independent implementation and outputs were complete; no main program or tests were read or imported",
            "main_output_sha256": {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in ["traces.jsonl.gz", "results.csv", "paired_results.json", "witnesses.json", "summary.json"]}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument("--compare-main", type=Path)
    args = parser.parse_args()
    inp, out = args.input_dir, args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads((inp / "config.json").read_text())
    validate(config)
    manifest = json.loads((inp / "input_manifest.json").read_text())
    for filename, expected in manifest["sha256"].items():
        assert hashlib.sha256((inp / filename).read_bytes()).hexdigest() == expected
    controls = manual_controls()
    invalid_count = invalid_controls(config)
    aggregate, pairs, witnesses, rows, events = audit(config)
    with (out / "independent_results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]))
        writer.writeheader()
        writer.writerows(aggregate)
    dump(out / "independent_pairs.json", pairs)
    dump(out / "independent_witnesses.json", witnesses)
    receipt = {"status": "PASS", "implementation": "integer tick loop; no event heap", "independence": "First implementation used only frozen plan/config/manifest; no main code or result access", "event_convention": "Each scheduled slot has a send or skip event, even after a first receipt. A receipt is part of its arrival event. Final event time includes skip decisions. This convention was confirmed before enumeration.", "rows": rows, "events": events, "aggregate_rows": len(aggregate), "pair_rows": len(pairs), "witnesses": len(witnesses), "manual_controls": controls, "invalid_config_controls": invalid_count, "frozen_sha256": manifest["sha256"]}
    dump(out / "independent_receipt.json", receipt)
    if args.compare_main:
        comparison = compare_main(config, args.compare_main, aggregate, pairs, witnesses)
        dump(out / "independent_comparison.json", comparison)
        print(json.dumps({"comparison": comparison["status"], "trace_rows": comparison["full_trace_rows"], "events": comparison["full_trace_events"], "scalar_values": comparison["trace_scalar_values_compared"]}, sort_keys=True))
    print(json.dumps({k: receipt[k] for k in ["status", "rows", "events", "aggregate_rows", "pair_rows", "witnesses", "invalid_config_controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
