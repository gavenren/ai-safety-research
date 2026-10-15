#!/usr/bin/env python3
"""Independent checks for the saved computer-use retry model.

This file does not import the main analyzer. It obtains event times by direct
threshold calculations. It then checks every saved run against those times.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import platform
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from decimal import Decimal, localcontext
from pathlib import Path


KEY_FIELDS = ("suite", "d1", "outcome1", "d2", "outcome2", "lag",
              "schedule", "policy", "server_mode")
MEASURES = ("duplicate", "clean_confirmed", "unsafe_completion",
            "detected_duplicate", "deadline_stop", "no_claim", "zero_effect",
            "one_effect_unconfirmed", "submit_calls", "query_calls", "capped_clean_time")


def count_at(t, times, mode):
    count = sum(v <= t for v in times)
    return min(count, 1) if mode == "deduplicate" else count


def direct_result(row, config):
    """Use closed-form visibility times, not a per-tick event loop."""
    d1, d2, lag = (int(row[n]) for n in ("d1", "d2", "lag"))
    o1, o2 = row["outcome1"], row["outcome2"]
    mode, policy = row["server_mode"], row["policy"]
    deadline = config["deadline"]
    schedule = config["schedules"][row["schedule"]]
    visible_first = d1 + lag if o1 == "commit" else float("inf")
    retry = None
    if policy == "absence_retry":
        candidate = schedule[0]
        if candidate < visible_first:
            retry = candidate
    elif policy in ("timeout8", "bound12"):
        threshold = config["execution_bound"]
        if policy == "bound12":
            threshold += config["lag_bound"]
        candidates = [t for t in schedule if t >= threshold]
        if candidates and candidates[0] < visible_first:
            retry = candidates[0]
    elif policy == "terminal_retry" and o1 == "drop":
        candidates = [t for t in schedule if t >= d1 + lag]
        if candidates:
            retry = candidates[0]
    elif policy not in ("terminal_retry", "no_retry"):
        raise AssertionError(f"Unknown policy: {policy}")

    effect_times = []
    resolution_times = [d1]
    if o1 == "commit":
        effect_times.append(d1)
    if retry is not None:
        resolution_times.append(retry + d2)
        if o2 == "commit":
            effect_times.append(retry + d2)
    visible_times = [v + lag for v in effect_times]
    positive_queries = [t for t in schedule if any(v <= t for v in visible_times)]
    stop = positive_queries[0] if positive_queries else deadline
    observed = count_at(max(0, stop - lag), effect_times, mode)
    if positive_queries:
        reason = "confirmed" if observed == 1 else "detected_duplicate"
    else:
        reason = "deadline"
    declared = int(reason == "confirmed")
    final = len(effect_times) if mode == "append" else min(1, len(effect_times))
    clean = int(declared and final == 1)
    return {
        "retry_tick": "" if retry is None else str(retry),
        "stop_tick": str(stop),
        "stop_reason": reason,
        "declared": str(declared),
        "observed_count_at_stop": str(observed),
        "effects_at_stop": str(count_at(stop, effect_times, mode)),
        "final_effects": str(final),
        "audit_tick": str(max(stop, *resolution_times)),
        "duplicate": str(int(final > 1)),
        "clean_confirmed": str(clean),
        "unsafe_completion": str(int(declared and final != 1)),
        "detected_duplicate": str(int(reason == "detected_duplicate")),
        "deadline_stop": str(int(reason == "deadline")),
        "no_claim": str(1 - declared),
        "zero_effect": str(int(final == 0)),
        "one_effect_unconfirmed": str(int(final == 1 and not declared)),
        "submit_calls": str(1 + int(retry is not None)),
        "query_calls": str(sum(t <= stop for t in schedule)),
        "capped_clean_time": str(stop if clean else deadline),
    }


def key(row):
    return tuple(str(row[n]) for n in KEY_FIELDS)


def expected_keys(config):
    suites = {"main": {"attempt_delays": config["attempt_delays"],
                       "read_lags": config["read_lags"]},
              **config["stress_suites"]}
    for suite, values in suites.items():
        for d1, o1, d2, o2, lag, schedule, policy, mode in itertools.product(
                values["attempt_delays"], config["outcomes"],
                values["attempt_delays"], config["outcomes"], values["read_lags"],
                config["schedules"], config["policies"], config["server_modes"]):
            yield tuple(map(str, (suite, d1, o1, d2, o2, lag, schedule, policy, mode)))


def expected_trace(row, config):
    """Construct a sorted event list from the independently checked times."""
    d1, d2, lag = (int(row[n]) for n in ("d1", "d2", "lag"))
    mode = row["server_mode"]
    stop = int(row["stop_tick"])
    attempts = [(1, 0, d1, row["outcome1"])]
    if row["retry_tick"]:
        launch = int(row["retry_tick"])
        attempts.append((2, launch, launch + d2, row["outcome2"]))
    commits = [due for _, _, due, outcome in attempts if outcome == "commit"]
    events = []
    for attempt, launch, due, outcome in attempts:
        events.append((launch, 2 if attempt == 2 else -1, attempt,
                       {"tick": launch, "event": "submit", "attempt": attempt}))
        count_after_this_resolution = sum(
            o == "commit" and (d < due or d == due and a <= attempt)
            for a, _, d, o in attempts)
        if mode == "deduplicate":
            count_after_this_resolution = min(count_after_this_resolution, 1)
        events.append((due, 0, attempt,
                       {"tick": due, "event": "resolve", "attempt": attempt,
                        "outcome": outcome, "effects": count_after_this_resolution}))
    for tick in config["schedules"][row["schedule"]]:
        if tick > stop:
            continue
        asof = max(0, tick - lag)
        events.append((tick, 1, 0,
                       {"tick": tick, "event": "query", "as_of": asof,
                        "observed_count": count_at(asof, commits, mode),
                        "first_attempt_state": row["outcome1"] if d1 <= asof else "pending"}))
    events.append((stop, 3, 0,
                   {"tick": stop, "event": "stop", "reason": row["stop_reason"],
                    "declared": int(row["declared"]), "effects": int(row["effects_at_stop"])}))
    audit = int(row["audit_tick"])
    events.append((audit, 4, 0,
                   {"tick": audit, "event": "final_audit", "final_effects": int(row["final_effects"])}))
    return [record for _, _, _, record in sorted(events)]


def ratio9(numerator, denominator):
    if denominator == 0:
        return ""
    with localcontext() as context:
        context.prec = 60
        return f"{Decimal(numerator) / Decimal(denominator):.9f}"


def check_summary(base, name, fields, rows):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[f] for f in fields)].append(row)
    with (base / name).open(newline="") as handle:
        summaries = list(csv.DictReader(handle))
    summary_keys = [tuple(r[f] for f in fields) for r in summaries]
    assert len(summary_keys) == len(set(summary_keys))
    assert set(summary_keys) == set(groups)
    comparisons = 0
    for summary in summaries:
        members = groups[tuple(summary[f] for f in fields)]
        expected = {"runs": str(len(members))}
        for measure in MEASURES:
            total = sum(int(r[measure]) for r in members)
            expected[measure + "_sum"] = str(total)
            expected[measure + "_mean"] = ratio9(total, len(members))
        clean = [r for r in members if r["clean_confirmed"] == "1"]
        clean_sum = sum(int(r["stop_tick"]) for r in clean)
        expected["clean_time_sum"] = str(clean_sum)
        expected["clean_time_mean"] = ratio9(clean_sum, len(clean))
        for field, value in expected.items():
            assert summary[field] == value, (name, summary_keys, field, summary[field], value)
            comparisons += 1
    return {"rows": len(summaries), "field_comparisons": comparisons}


def check_paired(base, rows, config):
    with (base / "results_paired.csv").open(newline="") as handle:
        paired = list(csv.DictReader(handle))
    seen = set()
    for saved in paired:
        suite, schedule = saved["suite"], saved["schedule"]
        baseline = saved["comparison"].removeprefix("terminal_retry minus ")
        assert baseline in ("bound12", "no_retry", "absence_retry", "timeout8")
        pair_key = (suite, schedule, baseline)
        assert pair_key not in seen
        seen.add(pair_key)
        left = {r["case_id"]: r for r in rows if r["suite"] == suite and
                r["schedule"] == schedule and r["server_mode"] == "append" and
                r["policy"] == "terminal_retry"}
        right = {r["case_id"]: r for r in rows if r["suite"] == suite and
                 r["schedule"] == schedule and r["server_mode"] == "append" and
                 r["policy"] == baseline}
        assert left.keys() == right.keys()
        jointly = [c for c in left if left[c]["clean_confirmed"] == right[c]["clean_confirmed"] == "1"]
        time_delta = sum(int(left[c]["stop_tick"]) - int(right[c]["stop_tick"]) for c in jointly)
        expected = {
            "cases": str(len(left)), "jointly_clean": str(len(jointly)),
            "clean_gain": str(sum(int(left[c]["clean_confirmed"]) - int(right[c]["clean_confirmed"]) for c in left)),
            "duplicate_delta": str(sum(int(left[c]["duplicate"]) - int(right[c]["duplicate"]) for c in left)),
            "paired_time_delta_sum": str(time_delta),
            "paired_time_delta_mean": ratio9(time_delta, len(jointly)),
        }
        for field, value in expected.items():
            assert saved[field] == value, ("paired", pair_key, field, saved[field], value)
    assert len(seen) == (1 + len(config["stress_suites"])) * len(config["schedules"]) * 4
    return len(paired)


def check_hypotheses(base, rows, config):
    saved = json.loads((base / "hypothesis_checks.json").read_text())
    main_append = [r for r in rows if r["suite"] == "main" and r["server_mode"] == "append"]
    expected = {
        "main_cases": 256, "all_cases": 336, "all_runs": len(rows),
        "main_runs": sum(r["suite"] == "main" for r in rows), "summary_rows": 120,
        "H1_fresh_absence_duplicates_by_schedule": {
            s: sum(int(r["duplicate"]) for r in main_append if r["policy"] == "absence_retry" and
                   r["lag"] == "0" and r["schedule"] == s) for s in config["schedules"]},
        "H2_terminal_and_bound_duplicates": {
            p: sum(int(r["duplicate"]) for r in main_append if r["policy"] == p)
            for p in ("terminal_retry", "bound12")},
        "H3_absence_duplicates": {
            s: sum(int(r["duplicate"]) for r in main_append if r["policy"] == "absence_retry" and
                   r["schedule"] == s) for s in config["schedules"]},
        "H4_stress_duplicates": {
            suite: {p: sum(int(r["duplicate"]) for r in rows if r["suite"] == suite and
                          r["server_mode"] == "append" and r["policy"] == p)
                    for p in config["policies"]} for suite in config["stress_suites"]},
        "deduplication_duplicates_all_suites": sum(int(r["duplicate"]) for r in rows if r["server_mode"] == "deduplicate"),
    }
    for field, value in expected.items():
        assert saved[field] == value, ("Hypothesis field", field)
    with (base / "results_paired.csv").open(newline="") as handle:
        pairs = [r for r in csv.DictReader(handle) if r["suite"] == "main" and
                 r["comparison"] == "terminal_retry minus bound12"]
    assert len(saved["H2_paired_main"]) == len(pairs)
    for left, right in zip(saved["H2_paired_main"], pairs):
        assert {k: str(v) for k, v in left.items()} == right
    fast = {r["case_id"]: r for r in main_append if r["policy"] == "absence_retry" and r["schedule"] == "every1"}
    slow = {r["case_id"]: r for r in main_append if r["policy"] == "absence_retry" and r["schedule"] == "every4"}
    assert fast.keys() == slow.keys()
    matrix = Counter((fast[c]["duplicate"], slow[c]["duplicate"]) for c in fast)
    return {
        "hypothesis_fields_checked": len(expected) + 1,
        "H3_every1_vs_every4": {
            "neither_duplicate": matrix[("0", "0")],
            "both_duplicate": matrix[("1", "1")],
            "every1_only_duplicate": matrix[("1", "0")],
            "every4_only_duplicate": matrix[("0", "1")],
            "total_paired_cases": len(fast),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    base = args.input_dir
    config = json.loads((base / "config.json").read_text())
    with (base / "results_runs.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows, "No saved run rows"
    actual_keys = [key(r) for r in rows]
    required_keys = set(expected_keys(config))
    assert len(actual_keys) == len(set(actual_keys)), "Duplicate run keys"
    assert set(actual_keys) == required_keys, "Missing or additional grid rows"
    assert len(rows) == 13440, f"Wrong total row count: {len(rows)}"
    cases = defaultdict(set)
    scenario_to_id = {}
    for row in rows:
        scenario = key(row)[:6]
        cases[row["case_id"]].add(scenario)
        assert scenario_to_id.setdefault(scenario, row["case_id"]) == row["case_id"]
    assert all(len(value) == 1 for value in cases.values()), "Case ID reused"
    assert len(cases) == 336, "Wrong number of scenarios"
    with (base / "cases.csv").open(newline="") as handle:
        case_rows = list(csv.DictReader(handle))
    assert len(case_rows) == len(cases)
    for case in case_rows:
        assert (case["suite"], case["d1"], case["outcome1"], case["d2"], case["outcome2"], case["lag"]) in cases[case["case_id"]]

    checked_fields = 0
    for row in rows:
        predicted = direct_result(row, config)
        for field, value in predicted.items():
            assert row[field] == value, (key(row), field, row[field], value)
            checked_fields += 1
        assert sum(int(row[n]) for n in ("clean_confirmed", "unsafe_completion", "no_claim")) == 1
        assert int(row["no_claim"]) == int(row["detected_duplicate"]) + int(row["deadline_stop"])
        assert int(row["submit_calls"]) in (1, 2)
        if row["declared"] == "1":
            assert row["observed_count_at_stop"] == "1"
            assert int(row["final_effects"]) >= 1

    indexed = {key(r): r for r in rows}
    trace_events = 0
    post_stop_resolution_events = 0
    traces_seen = set()
    with gzip.open(base / "traces.jsonl.gz", "rt") as handle:
        for line in handle:
            record = json.loads(line)
            trace_key = key(record["run"])
            assert trace_key in indexed and trace_key not in traces_seen
            traces_seen.add(trace_key)
            row = indexed[trace_key]
            assert {k: str(v) for k, v in record["run"].items()} == row
            expected = expected_trace(row, config)
            assert record["events"] == expected, ("Trace mismatch", trace_key)
            trace_events += len(expected)
            post_stop_resolution_events += sum(e["event"] == "resolve" and e["tick"] > int(row["stop_tick"]) for e in expected)
    assert traces_seen == set(indexed)
    examples = json.loads((base / "trace_examples.json").read_text())
    assert len(examples) == 5
    for record in examples:
        row = indexed[key(record["run"])]
        assert record["events"] == expected_trace(row, config)
        assert row["suite"] == "main" and row["d1"] == "8" and row["d2"] == "1"
        assert row["lag"] == "0" and row["outcome1"] == row["outcome2"] == "commit"
        assert row["schedule"] == "every1" and row["server_mode"] == "append"

    summaries = {
        "results_summary.csv": check_summary(base, "results_summary.csv",
            ("suite", "server_mode", "schedule", "policy"), rows),
        "results_by_outcome.csv": check_summary(base, "results_by_outcome.csv",
            ("suite", "server_mode", "schedule", "policy", "outcome1"), rows),
        "results_by_lag.csv": check_summary(base, "results_by_lag.csv",
            ("suite", "server_mode", "schedule", "policy", "lag"), rows),
    }
    paired_rows = check_paired(base, rows, config)
    hypothesis_checks = check_hypotheses(base, rows, config)
    dedup_pairs = 0
    for row in rows:
        if row["server_mode"] != "append":
            continue
        other_key = key(row)[:-1] + ("deduplicate",)
        other = indexed[other_key]
        for field in ("retry_tick", "stop_tick", "audit_tick", "submit_calls", "query_calls"):
            assert row[field] == other[field], ("Matched server control", field, key(row))
        assert int(other["final_effects"]) == min(1, int(row["final_effects"]))
        assert other["duplicate"] == "0"
        assert other["unsafe_completion"] == "0"
        dedup_pairs += 1

    policy_checks = Counter()
    for row in rows:
        if row["policy"] in ("no_retry", "terminal_retry"):
            assert row["duplicate"] == "0"
            policy_checks["no_retry_or_terminal_safe_all_suites"] += 1
        if row["suite"] == "main" and row["policy"] == "bound12":
            assert row["duplicate"] == "0"
            policy_checks["bounded_rule_safe_inside_contract"] += 1
        if row["policy"] == "terminal_retry" and row["retry_tick"]:
            assert row["outcome1"] == "drop"
            assert int(row["retry_tick"]) - int(row["lag"]) >= int(row["d1"])
            policy_checks["terminal_retry_requires_visible_drop"] += 1
        if row["policy"] == "timeout8" and row["outcome1"] == "commit" and row["lag"] == "0" and int(row["d1"]) <= 8:
            assert row["retry_tick"] == ""
            policy_checks["resolution_at_timeout_is_seen_before_retry"] += 1

    # Tight local two-world relation. This is not a claim that waiting fails.
    # At one shared negative history, r is the chance of an immediate retry.
    # A guaranteed successful retry duplicates in the pending world and
    # recovers in the dropped world. Both event probabilities are r.
    ambiguity_cases = 0
    for numerator in range(21):
        r = Fraction(numerator, 20)
        duplicate_pending = r
        recovery_dropped = r
        nonrecovery_dropped = 1 - r
        assert duplicate_pending == recovery_dropped
        assert duplicate_pending + nonrecovery_dropped == 1
        ambiguity_cases += 1

    summary = {
        "status": "PASS",
        "validator_method": "Direct event-time thresholds; no import of analyze.py",
        "python_version": platform.python_version(),
        "rows_checked": len(rows),
        "scenario_count": len(cases),
        "field_comparisons": checked_fields,
        "rows_by_suite": dict(sorted(Counter(r["suite"] for r in rows).items())),
        "matched_server_pairs": dedup_pairs,
        "traces_checked": len(traces_seen),
        "trace_events_checked": trace_events,
        "post_stop_resolution_events_checked": post_stop_resolution_events,
        "trace_examples_checked": len(examples),
        "summary_tables_checked": summaries,
        "paired_rows_checked": paired_rows,
        "hypothesis_checks": hypothesis_checks,
        "policy_checks": dict(sorted(policy_checks.items())),
        "exact_local_ambiguity_cases": ambiguity_cases,
        "input_sha256": {
            name: hashlib.sha256((base / name).read_bytes()).hexdigest()
            for name in ("config.json", "results_runs.csv", "traces.jsonl.gz",
                         "results_summary.csv", "results_by_outcome.csv",
                         "results_by_lag.csv", "results_paired.csv", "trace_examples.json",
                         "cases.csv", "hypothesis_checks.json")
        },
        "numeric_tolerance": "None. All checked row fields are exact integers or labels.",
        "limits": "This check validates the synthetic model. It does not validate a real service contract or a population error rate.",
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "validation_results.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
