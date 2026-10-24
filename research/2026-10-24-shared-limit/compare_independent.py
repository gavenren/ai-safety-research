#!/usr/bin/env python3
"""Compare SQL evidence with the separately frozen pure specification.

This adapter knows the evidence schema. It imports only independent_check.py,
not the main runner. The database is opened read-only.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import sqlite3
import time
from pathlib import Path

import independent_check as oracle


SELECT = """SELECT q.capacity,q.epoch,q.note,a.units,a.version,b.units,b.version
FROM quotas q JOIN allocations a ON a.case_id=q.id AND a.worker=0
JOIN allocations b ON b.case_id=q.id AND b.worker=1 WHERE q.id=?"""
BASE_UPDATE = "UPDATE allocations SET units=?,version=version+1 WHERE case_id=? AND worker=? AND units=0 AND version=?"
EXTRA_SQL = {
    "OwnCAS": "",
    "SharedEpoch": " AND EXISTS(SELECT 1 FROM quotas WHERE id=? AND epoch=?)",
    "AtomicSum": " AND (SELECT SUM(units) FROM allocations WHERE case_id=?)+? <= (SELECT capacity FROM quotas WHERE id=?)",
}
SCORES = {
    "breach": "bound_breach", "accepted_jobs": "accepted_jobs",
    "refused_jobs": "refused_jobs", "bad_admissions": "bad_admissions",
    "feasible_refusals": "feasible_refusals", "excess_units": "maximum_excess_units",
    "row_errors": "row_version_errors", "epoch_errors": "epoch_accounting_errors",
    "reads": "reads", "write_attempts": "write_attempts",
    "guard_refusals": "sql_refusals", "read_denials": "read_denials",
}


def normalize_sql(sql):
    return " ".join(sql.split())


def state_from_spec(s):
    return {"capacity": s["capacity"], "epoch": s["epoch"], "note": s["note"],
            "units": [s["allocations"][w] for w in oracle.WORKERS],
            "versions": [s["versions"][w] for w in oracle.WORKERS]}


def dbrow(s):
    return [s["capacity"], s["epoch"], s["note"],
            s["units"][0], s["versions"][0], s["units"][1], s["versions"][1]]


def stmt(sql, params=(), rowcount=-1, rows=()):
    return {"sql": normalize_sql(sql), "params": list(params),
            "rowcount": rowcount, "rows": list(rows)}


def select(case_id, s):
    return stmt(SELECT, [case_id], rows=[dbrow(s)])


def expected_decision(expected, step):
    event = step["event"]
    if not event.startswith("C"):
        return None
    w = event[1]
    result = step["result"]
    return {
        "accepted": result == "accepted",
        "reason": {"accepted": "accepted", "sql_refused": "guard_refusal",
                   "read_denied": "read_denial"}[result],
        "write_attempt": int(result != "read_denied"),
        "feasible_before": sum(step["before"]["allocations"].values())
            + expected["input"]["demands"][w] <= expected["input"]["capacity"],
    }


def expected_sql(case_id, expected, step):
    before, after = (state_from_spec(step[k]) for k in ("before", "after"))
    out = [select(case_id, before)]
    event = step["event"]
    if event.startswith("R"):
        out.append(select(case_id, before))
    elif event == "U":
        out.extend([stmt("BEGIN IMMEDIATE"),
                    stmt("UPDATE quotas SET note=1-note,epoch=epoch+1 WHERE id=?", [case_id], 1),
                    stmt("COMMIT")])
    elif step["result"] != "read_denied":
        w = event[1]
        wi = oracle.WORKERS.index(w)
        spec = expected["input"]
        rule = spec["policies"][w]
        read = expected["reads"][w]
        params = [spec["demands"][w], case_id, wi, read["own_version"]]
        if rule == "SharedEpoch":
            params.extend([case_id, read["epoch"]])
        elif rule == "AtomicSum":
            params.extend([case_id, spec["demands"][w], case_id])
        out.extend([stmt("BEGIN IMMEDIATE"),
                    stmt(BASE_UPDATE + EXTRA_SQL[rule], params, int(step["result"] == "accepted"))])
        if step["result"] == "accepted":
            out.append(stmt("UPDATE quotas SET epoch=epoch+1 WHERE id=?", [case_id], 1))
        out.append(stmt("COMMIT"))
    out.append(select(case_id, after))
    return out


def validate(traces_path, database_path, logical_path):
    expected_map = {oracle.key_of(s): oracle.evaluate(s) for s in oracle.inputs()}
    checks = oracle.run_pure_checks(list(expected_map.values()))
    seen = set()
    ids = set()
    sql_counts = collections.Counter()
    read_fields = state_fields = decisions = scores = 0
    expected_quotas, expected_allocations = [], []

    def eq(actual, expected, where):
        if actual != expected:
            raise AssertionError(f"{where}: actual={actual!r}; expected={expected!r}")

    def check_sql(actual, expected, where):
        normalized = [{**x, "sql": normalize_sql(x["sql"])} for x in actual]
        eq(normalized, expected, where)
        for row in normalized:
            sql_counts[row["sql"].split()[0]] += 1

    with gzip.open(traces_path, "rt") as f:
        for line_no, line in enumerate(f, start=1):
            actual = json.loads(line)
            cid = actual["case_id"]
            if cid in ids:
                raise AssertionError(f"duplicate case ID {cid}")
            ids.add(cid)
            inp = actual["input"]
            spec = {"capacity": inp["capacity"],
                    "demands": dict(zip(oracle.WORKERS, inp["demands"])),
                    "policies": dict(zip(oracle.WORKERS, actual["policies"])),
                    "schedule": inp["schedule"]}
            key = oracle.key_of(spec)
            if key in seen or key not in expected_map:
                raise AssertionError(f"duplicate or unexpected semantic input at {cid}")
            seen.add(key)
            expected = expected_map[key]
            initial = state_from_spec(expected["steps"][0]["before"])
            eq(actual["initial"], initial, f"{cid} initial")
            expected_setup = [stmt("BEGIN IMMEDIATE"),
                stmt("INSERT INTO quotas VALUES(?,?,0,0)", [cid, spec["capacity"]], 1),
                stmt("INSERT INTO allocations VALUES(?,?,0,0)", [cid, 0], 1),
                stmt("INSERT INTO allocations VALUES(?,?,0,0)", [cid, 1], 1),
                stmt("COMMIT"), select(cid, initial)]
            check_sql(actual["setup_sql"], expected_setup, f"{cid} setup SQL")
            eq(len(actual["trace"]), len(expected["steps"]), f"{cid} step length")
            job_decisions = {}
            for i, (step, target) in enumerate(zip(actual["trace"], expected["steps"])):
                where = f"{cid} step {i}"
                eq(step["event"], target["event"], where + " event")
                for side in ("before", "after"):
                    eq(step[side], state_from_spec(target[side]), where + " " + side)
                    state_fields += 7
                target_read = state_from_spec(target["read"]) if target["read"] is not None else None
                eq(step["read"], target_read, where + " read")
                if target_read is not None:
                    read_fields += 7
                decision = expected_decision(expected, target)
                eq(step["decision"], decision, where + " decision")
                if decision is not None:
                    decisions += 1
                    job_decisions[target["event"][1]] = decision
                check_sql(step["sql_log"], expected_sql(cid, expected, target), where + " SQL")
            eq(actual["jobs"], [job_decisions[w] for w in oracle.WORKERS], f"{cid} jobs")
            eq(actual["final"], state_from_spec(expected["final"]), f"{cid} final")
            target_scores = {actual_key: expected["scores"][expected_key]
                             for actual_key, expected_key in SCORES.items()}
            eq(actual["scores"], target_scores, f"{cid} scores")
            scores += len(SCORES)
            s = actual["final"]
            expected_quotas.append([cid, s["capacity"], s["epoch"], s["note"]])
            expected_allocations.extend([cid, wi, s["units"][wi], s["versions"][wi]] for wi in (0, 1))
    eq(seen, set(expected_map), "complete semantic input coverage")
    expected_dump = {"quotas": sorted(expected_quotas), "allocations": sorted(expected_allocations)}
    with gzip.open(logical_path, "rt") as f:
        eq(json.load(f), expected_dump, "logical database dump")
    connection = sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        eq(connection.execute("PRAGMA integrity_check").fetchall(), [("ok",)], "database integrity")
        actual_quotas = [list(r) for r in connection.execute("SELECT id,capacity,epoch,note FROM quotas ORDER BY id")]
        actual_allocations = [list(r) for r in connection.execute("SELECT case_id,worker,units,version FROM allocations ORDER BY case_id,worker")]
        eq(actual_quotas, expected_dump["quotas"], "reopened physical quota rows")
        eq(actual_allocations, expected_dump["allocations"], "reopened physical allocation rows")
    finally:
        connection.close()
    return {
        "status": "pass", "main_runner_imported": False, "main_runner_source_read": False,
        "cases": len(seen), "worker_decisions_compared": decisions,
        "read_values_compared": read_fields, "event_state_values_compared": state_fields,
        "score_values_compared": scores, "physical_quota_rows": len(expected_quotas),
        "physical_allocation_rows": len(expected_allocations),
        "sql_statements_compared": sum(sql_counts.values()), "sql_by_command": dict(sql_counts),
        "pure_checks": checks,
        "meaning": "All saved trace semantics, SQL dispatch data, logical dump, and reopened physical final rows match the frozen independent specification. This does not validate provider behavior or unconstrained concurrency.",
    }


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--logical", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = validate(args.traces, args.database, args.logical)
    result["wall_seconds"] = time.monotonic() - started
    result["files"] = {name: {"name": path.name, "sha256": sha256(path)}
                       for name, path in (("traces", args.traces), ("database", args.database),
                                          ("logical", args.logical))}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
