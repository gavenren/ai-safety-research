#!/usr/bin/env python3
"""Independent pure specification for the 2026-10-24 shared-limit plan.

Written from plan.md without reading run_study.py. No SQL experiment is run.
The optional evidence adapter is separate from the specification below.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import itertools
import json
from pathlib import Path


RULES = ("OwnCAS", "SharedEpoch", "AtomicSum")
WORKERS = ("A", "B")
EVENTS = ("RA", "CA", "RB", "CB")


def key_of(spec):
    """Use semantic inputs, not the runner's case numbering."""
    return (
        spec["capacity"], spec["demands"]["A"], spec["demands"]["B"],
        spec["policies"]["A"], spec["policies"]["B"], tuple(spec["schedule"]),
    )


def inputs():
    orders = [p for p in itertools.permutations(EVENTS)
              if p.index("RA") < p.index("CA") and p.index("RB") < p.index("CB")]
    assert len(orders) == 6
    schedules = []
    for p in orders:
        schedules.append(p)
        schedules.extend(p[:i] + ("U",) + p[i:] for i in range(5))
    assert len(schedules) == len(set(schedules)) == 36
    for policies in itertools.product(RULES, repeat=2):
        for capacity in range(1, 5):
            for demands in itertools.product((1, 2), repeat=2):
                for schedule in schedules:
                    yield {
                        "capacity": capacity,
                        "demands": dict(zip(WORKERS, demands)),
                        "policies": dict(zip(WORKERS, policies)),
                        "schedule": list(schedule),
                    }


def evaluate(spec):
    """State machine. No sqlite3, subprocess, network, random, or main imports."""
    units = {w: 0 for w in WORKERS}
    versions = {w: 0 for w in WORKERS}
    epoch = note = completed_u = 0
    reads = {}
    outcomes = {}
    accepted = {w: 0 for w in WORKERS}
    steps = []
    counts = dict.fromkeys((
        "accepted_jobs", "refused_jobs", "bad_admissions", "feasible_refusals",
        "row_version_errors", "epoch_accounting_errors", "reads", "write_attempts",
        "sql_refusals", "read_denials", "maximum_excess_units",
    ), 0)
    bound_breach = False

    def state():
        return {"capacity": spec["capacity"], "epoch": epoch, "note": note,
                "allocations": units.copy(), "versions": versions.copy()}

    for event in spec["schedule"]:
        before = state()
        result = None
        observation = None
        if event == "U":
            note = 1 - note
            epoch += 1
            completed_u += 1
            result = "metadata_applied"
        else:
            kind, worker = event
            demand = spec["demands"][worker]
            if kind == "R":
                counts["reads"] += 1
                observation = {
                    **state(),
                    "own_version": versions[worker],
                    "sum": sum(units.values()),
                    "eligible": sum(units.values()) + demand <= spec["capacity"],
                }
                reads[worker] = observation.copy()
                result = "read"
            else:
                assert kind == "C" and worker in reads and worker not in outcomes
                feasible = sum(units.values()) + demand <= spec["capacity"]
                if not reads[worker]["eligible"]:
                    result = "read_denied"
                    counts["read_denials"] += 1
                else:
                    counts["write_attempts"] += 1
                    valid = (versions[worker] == reads[worker]["own_version"]
                             and units[worker] == 0)
                    rule = spec["policies"][worker]
                    if rule == "SharedEpoch":
                        valid = valid and epoch == reads[worker]["epoch"]
                    elif rule == "AtomicSum":
                        valid = valid and feasible
                    else:
                        assert rule == "OwnCAS"
                    if valid:
                        units[worker] = demand
                        versions[worker] += 1
                        epoch += 1
                        accepted[worker] += 1
                        result = "accepted"
                        counts["accepted_jobs"] += 1
                        counts["bad_admissions"] += int(sum(units.values()) > spec["capacity"])
                    else:
                        result = "sql_refused"
                        counts["sql_refusals"] += 1
                if result != "accepted":
                    counts["refused_jobs"] += 1
                    counts["feasible_refusals"] += int(feasible)
                outcomes[worker] = result

        after = state()
        excess = max(0, sum(units.values()) - spec["capacity"])
        bound_breach = bound_breach or bool(excess)
        counts["maximum_excess_units"] = max(counts["maximum_excess_units"], excess)
        counts["epoch_accounting_errors"] += int(epoch != sum(accepted.values()) + completed_u)
        counts["row_version_errors"] += sum(
            int(versions[w] != accepted[w] or units[w] != spec["demands"][w] * accepted[w])
            for w in WORKERS
        )
        steps.append({"event": event, "before": before, "result": result,
                      "read": observation, "after": after})

    assert set(outcomes) == set(WORKERS)
    assert counts["accepted_jobs"] + counts["refused_jobs"] == 2
    counts["bound_breach"] = int(bound_breach)
    return {"input": spec, "steps": steps, "reads": reads, "outcomes": outcomes,
            "final": state(), "scores": counts}


def swapped(spec):
    exchange = {"A": "B", "B": "A"}
    return {
        "capacity": spec["capacity"],
        "demands": {w: spec["demands"][exchange[w]] for w in WORKERS},
        "policies": {w: spec["policies"][exchange[w]] for w in WORKERS},
        "schedule": [e if e == "U" else e[0] + exchange[e[1]] for e in spec["schedule"]],
    }


def run_pure_checks(records):
    by_key = {key_of(r["input"]): r for r in records}
    assert len(records) == len(by_key) == 5184
    symmetry = noise = complete_pairs = serial_own = 0
    for r in records:
        spec = r["input"]
        other = by_key[key_of(swapped(spec))]
        assert r["scores"] == other["scores"]
        for w, other_w in (("A", "B"), ("B", "A")):
            assert r["outcomes"][w] == other["outcomes"][other_w]
            assert r["final"]["allocations"][w] == other["final"]["allocations"][other_w]
            assert r["final"]["versions"][w] == other["final"]["versions"][other_w]
        symmetry += 1
        if "OwnCAS" not in spec["policies"].values():
            assert r["scores"]["bound_breach"] == 0
            complete_pairs += 1
        if (set(spec["policies"].values()) == {"OwnCAS"}
                and tuple(spec["schedule"]) in (("RA", "CA", "RB", "CB"),
                                               ("RB", "CB", "RA", "CA"))):
            assert r["scores"]["bound_breach"] == 0
            serial_own += 1
        # A SharedEpoch worker can change the other worker's outcome indirectly.
        # The noise-invariance check therefore excludes every such mixed pair.
        if "U" in spec["schedule"] and "SharedEpoch" not in spec["policies"].values():
            clean_spec = {**spec, "schedule": [e for e in spec["schedule"] if e != "U"]}
            clean = by_key[key_of(clean_spec)]
            assert r["outcomes"] == clean["outcomes"]
            assert r["final"]["allocations"] == clean["final"]["allocations"]
            noise += 1
    return {"cases": len(records), "symmetry_cases": symmetry,
            "complete_pair_cases": complete_pairs, "serial_own_controls": serial_own,
            "noise_invariance_pairs_without_shared_epoch": noise}


def aggregate(records):
    groups = collections.defaultdict(collections.Counter)
    maximum = collections.defaultdict(int)
    for r in records:
        spec = r["input"]
        group = (spec["policies"]["A"], spec["policies"]["B"],
                 "U" if "U" in spec["schedule"] else "no_U")
        groups[group]["cases"] += 1
        for label, value in r["scores"].items():
            if label == "maximum_excess_units":
                maximum[group] = max(maximum[group], value)
            else:
                groups[group][label] += value
    return [{"policy_a": a, "policy_b": b, "stratum": s,
             **groups[a, b, s], "maximum_excess_units": maximum[a, b, s]}
            for a, b, s in sorted(groups)]


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    records = [evaluate(spec) for spec in inputs()]
    checks = run_pure_checks(records)
    packed = b"".join(json_bytes(r) for r in records)
    (args.output / "independent_expected.jsonl.gz").write_bytes(gzip.compress(packed, mtime=0))
    summary = {"scope": "Independent pure evaluator only; no SQL experiment",
               "checks": checks, "groups": aggregate(records),
               "expected_jsonl_sha256": hashlib.sha256(packed).hexdigest()}
    (args.output / "independent_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(checks, sort_keys=True))


if __name__ == "__main__":
    main()
