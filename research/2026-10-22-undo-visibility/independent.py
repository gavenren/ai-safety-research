#!/usr/bin/env python3
"""Pure schedule oracle, written from the frozen plan without the SQL runner.

This program predicts logical outcomes. It does not run a database, a worker,
or any crash experiment. The comparison input is the canonical schema emitted
here; adapters for other schemas must be separate and disclosed.
"""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

P = (1, 1)
Q = (0, 0)


def truth(predicate, state):
    # Interpret the truth table as a string in increasing input order.
    table = tuple(int(c) for c in f"{predicate:04b}"[::-1])
    return table[(0, 1, 2, 3)[state[0] * 2 + state[1]]]


def schedules(predicates):
    # Enumerate total orders of an atomic undo U and the ordered read jobs.
    jobs = tuple(range(len(predicates)))
    traces = set()
    for split in range(len(jobs) + 1):
        schedule = jobs[:split] + ("U",) + jobs[split:]
        state = P
        decisions = []
        for operation in schedule:
            if operation == "U":
                state = Q
            else:
                decisions.append(truth(predicates[operation], state))
        traces.add(tuple(decisions))
    return sorted(traces)


def case_specs(config):
    number = 0
    for group, rules in (("primary", config["primary_rules"]),
                         ("sensitivity", config["sensitivity_rules"])):
        for rule in rules:
            for order in config["orders"]:
                for f, g in itertools.product(config["predicates"], repeat=2):
                    number += 1
                    yield number, group, rule, order, f, g, None
    for split in config["serial_control_cuts"]:
        for f, g in itertools.product(config["predicates"], repeat=2):
            number += 1
            yield number, "serial_control", "whole_transaction", "xy", f, g, split


def predict(spec):
    number, group, rule, order, f, g, split = spec
    predicates = [f, g]
    if group == "serial_control":
        observations = [list(P if job < split else Q) for job in range(2)]
        accepted = [0, 1]
        post_exit = None
        expected_exit = None
    else:
        state = P if rule == "whole_transaction" else ((0, 1) if order == "xy" else (1, 0))
        gate = int(rule == "durable_gate")
        # The exit audit precedes the deliberate opening intervention.
        post_exit = {"fields": list(state),
                     "receipts": [] if rule == "whole_transaction" else [order[0]],
                     "gate": int(rule in ("durable_gate", "forced_open_gate"))}
        accepted = [] if gate else [0, 1]
        observations = [list(state) for _ in accepted]
        expected_exit = 73
    selected = [predicates[job] for job in accepted]
    decisions = [truth(fn, tuple(obs)) for fn, obs in zip(selected, observations)]
    allowed = schedules(selected)
    local = [bit in {truth(fn, P), truth(fn, Q)} for fn, bit in zip(selected, decisions)]
    violation = tuple(decisions) not in allowed
    probes = [{"job": job + 2, "predicate": fn, "observation": list(Q),
               "decision": truth(fn, Q), "accepted": True}
              for job, fn in enumerate(predicates)]
    return {
        "case_id": number, "group": group, "rule": rule, "order": order,
        "f": f, "g": g, "cut": split, "valid": True,
        "expected_exit_code": expected_exit, "post_exit": post_exit,
        "accepted_jobs": accepted, "refused_jobs": [j for j in range(2) if j not in accepted],
        "observations": observations, "decisions": decisions,
        "action_jobs": [job for job, bit in zip(accepted, decisions) if bit],
        "allowed": [list(t) for t in allowed], "local_pass": local,
        "serial_violation": violation, "local_failure": not all(local),
        "joint_only": violation and all(local),
        "final_source": {"fields": list(Q), "receipts": ["x", "y"], "gate": 0},
        "source_complete": True, "probes": probes, "probe_success": True,
        "known_cut_match": True if split is not None else None,
    }


def summarize(rows):
    counts = {}
    for row in rows:
        key = row["group"] + "/" + row["rule"]
        c = counts.setdefault(key, Counter())
        c["assigned"] += 1
        c["valid"] += 1
        c["unknown"] += 0
        c["accepted_jobs"] += len(row["accepted_jobs"])
        c["refused_jobs"] += len(row["refused_jobs"])
        for name in ("serial_violation", "local_failure", "joint_only", "source_complete", "probe_success"):
            c[name] += int(row[name])
    return {key: dict(value) for key, value in counts.items()}


def control_checks():
    states = list(itertools.product((0, 1), repeat=2))
    checks = []
    def add(name, condition, evidence):
        checks.append({"name": name, "pass": bool(condition), "evidence": evidence})
        assert condition, name
    identities = {"zero": (0, [0, 0, 0, 0]), "one": (15, [1, 1, 1, 1]),
                  "x": (12, [0, 0, 1, 1]), "y": (10, [0, 1, 0, 1]),
                  "xor": (6, [0, 1, 1, 0]), "equal": (9, [1, 0, 0, 1])}
    for name, (fn, expected) in identities.items():
        observed = [truth(fn, s) for s in states]
        add("truth_" + name, observed == expected, observed)
    allowed = schedules([12, 10])
    add("three_serial_cuts", allowed == [(0, 0), (1, 0), (1, 1)], allowed)
    witness = predict((1, "primary", "separate", "xy", 12, 10, None))
    add("joint_only_witness", witness["decisions"] == [0, 1] and witness["joint_only"],
        {k: witness[k] for k in ("decisions", "allowed", "local_pass", "joint_only")})
    outside = predict((2, "primary", "separate", "xy", 6, 0, None))
    add("outside_both_endpoints", outside["decisions"][0] == 1 and outside["local_failure"],
        {k: outside[k] for k in ("decisions", "local_pass", "serial_violation")})
    add("empty_sequence", schedules([]) == [()], schedules([]))
    endpoints = list(itertools.product((0, 1), repeat=2))
    serial_sizes = []
    local_sizes = []
    for a, b in endpoints:
        serial_row = []
        local_row = []
        for c, d in endpoints:
            serial_row.append(len({(b, d), (a, d), (a, c)}))
            local_row.append(len({a, b}) * len({c, d}))
        serial_sizes.append(serial_row)
        local_sizes.append(local_row)
    serial_sum = sum(map(sum, serial_sizes))
    local_sum = sum(map(sum, local_sizes))
    add("analytic_serial_size_sum", serial_sum == 32, serial_sizes)
    add("analytic_local_size_sum", local_sum == 36, local_sizes)
    add("analytic_predicted_counts", (64 - serial_sum) * 4 * 2 == 256 and
        (local_sum - serial_sum) * 4 * 2 == 32 and (64 - local_sum) * 4 * 2 == 224,
        {"serial_violations": (64 - serial_sum) * 8,
         "joint_only": (local_sum - serial_sum) * 8,
         "local_failures": (64 - local_sum) * 8})
    # These pure checks predict the process controls. They are not physical tests.
    checks.append({"name": "physical_controls_not_executed_here", "pass": None,
                   "evidence": "Worker-exit and rollback controls belong to the actual SQLite runner."
                   " This pure oracle predicts fields=[1,1], receipts=[], and no saved reader rows before work."})
    return checks


def canonical(row):
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--compare", type=Path, help="Canonical predictions JSONL to compare after the freeze")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    rows = [predict(spec) for spec in case_specs(config)]
    assert len(rows) == 2816
    assert [row["case_id"] for row in rows] == list(range(1, 2817))
    checks = control_checks()
    summary = summarize(rows)
    for key in ("primary/separate", "sensitivity/forced_open_gate"):
        assert summary[key]["serial_violation"] == 256
        assert summary[key]["joint_only"] == 32
        assert summary[key]["local_failure"] == 224
    assert all(summary[key]["serial_violation"] == 0 for key in
               ("primary/durable_gate", "primary/whole_transaction", "serial_control/whole_transaction"))
    args.out.mkdir(parents=True, exist_ok=True)
    payload = "".join(canonical(row) + "\n" for row in rows)
    (args.out / "predictions.jsonl").write_text(payload)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (args.out / "controls.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    if args.compare:
        actual = [json.loads(line) for line in args.compare.read_text().splitlines()]
        differences = [{"index": i, "expected": expected, "actual": observed}
                       for i, (expected, observed) in enumerate(itertools.zip_longest(rows, actual), 1)
                       if expected != observed]
        receipt = {"match": not differences, "expected_rows": len(rows), "actual_rows": len(actual),
                   "differences": differences,
                   "input_sha256": hashlib.sha256(args.compare.read_bytes()).hexdigest()}
        (args.out / "comparison.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        assert not differences, f"{len(differences)} rows differ"
    print(json.dumps({"rows": len(rows), "pure_predictions_only": True,
                      "summary": summary, "controls_passed": sum(c["pass"] is True for c in checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
