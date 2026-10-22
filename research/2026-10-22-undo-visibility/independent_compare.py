#!/usr/bin/env python3
"""Compare frozen pure predictions with observed SQLite evidence.

Written after the independent predictor was frozen. This adapter inspects the
main result schema but does not import the main runner or its scoring code.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sqlite3
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("frozen_oracle", ROOT / "independent.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def source_tables(source):
    return {"fields": dict(zip(("x", "y"), source["fields"])),
            "receipts": source["receipts"], "gate": source["gate"],
            "decisions": [], "actions": []}


def attempt(job, phase, predicate, accepted, observation=None, decision=None):
    return {"job": job, "phase": phase, "predicate": predicate,
            "status": "accepted" if accepted else "refused",
            "observed_x": observation[0] if accepted else None,
            "observed_y": observation[1] if accepted else None,
            "decision": decision if accepted else None}


def save_attempts(tables, attempts):
    result = json.loads(json.dumps(tables))
    for item in attempts:
        if item["status"] == "accepted":
            result["decisions"].append({k: v for k, v in item.items() if k != "status"})
            if item["decision"]:
                result["actions"].append(item["job"])
    return result


def inspect_database(path):
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        result = {
            "fields": dict(connection.execute("SELECT name, value FROM fields ORDER BY name")),
            "receipts": [r[0] for r in connection.execute("SELECT field FROM receipts ORDER BY field")],
            "gate": connection.execute("SELECT closed FROM gate WHERE singleton=1").fetchone()[0],
            "decisions": [dict(zip(("job", "phase", "predicate", "observed_x", "observed_y", "decision"), row))
                          for row in connection.execute("SELECT job, phase, predicate, observed_x, observed_y, decision FROM decisions ORDER BY job")],
            "actions": [r[0] for r in connection.execute("SELECT job FROM actions ORDER BY job")],
        }
        return result, [r[0] for r in connection.execute("PRAGMA integrity_check")], "\n".join(connection.iterdump()) + "\n"
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--actual", type=Path, required=True, help="Complete result directory")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--db-dir", type=Path, help="Read retained databases directly; otherwise use the published archive")
    args = parser.parse_args()
    freeze = json.loads((ROOT / "independent_implementation.json").read_text())
    for name, expected_hash in freeze["source_sha256"].items():
        if sha(ROOT / name) != expected_hash:
            raise RuntimeError("A frozen independent input changed: " + name)
    receipt = json.loads((args.actual / "execution_receipt.json").read_text())
    if receipt["status"] != "completed":
        raise RuntimeError("The actual run is not complete. Do not compare a partial run as complete.")
    predicted = [oracle.predict(s) for s in oracle.case_specs(json.loads((ROOT / "config.json").read_text()))]
    observed = read_jsonl(args.actual / "cases.jsonl")
    differences = []
    count = 0

    def check(label, actual, expected):
        nonlocal count
        count += 1
        if actual != expected:
            differences.append({"check": label, "actual": actual, "expected": expected})

    check("case_count", len(observed), len(predicted))
    expected_dumps = {}
    expected_workers = {}
    for expected, actual in zip(predicted, observed):
        case = expected["case_id"]
        prefix = f"case_{case}"
        for key in ("case_id", "group", "rule", "order", "f", "g", "cut", "valid"):
            check(prefix + "/" + key, actual.get(key), expected[key])
        for key in ("exit_status", "expected_exit_status"):
            check(prefix + "/" + key, actual.get(key), expected["expected_exit_code"])
        check(prefix + "/recovery_status", actual.get("recovery_status"), 0)
        check(prefix + "/unknown", actual.get("unknown_reason"), None)
        check(prefix + "/integrity", actual.get("integrity"), "ok")
        base = {"fields": [1, 1], "receipts": [], "gate": 0} if expected["group"] == "serial_control" else expected["post_exit"]
        audit = source_tables(base)
        check(prefix + "/audit", actual.get("audit"), audit)
        intervention = None
        if expected["rule"] == "forced_open_gate":
            intervention = dict(audit, gate=0)
        check(prefix + "/intervention", actual.get("post_intervention_audit"), intervention)
        primary = []
        for job, predicate in enumerate((expected["f"], expected["g"])):
            accepted = job in expected["accepted_jobs"]
            index = expected["accepted_jobs"].index(job) if accepted else None
            primary.append(attempt(job, "primary", predicate, accepted,
                                   expected["observations"][index] if accepted else None,
                                   expected["decisions"][index] if accepted else None))
        probes = [attempt(p["job"], "probe", p["predicate"], True, p["observation"], p["decision"]) for p in expected["probes"]]
        check(prefix + "/reader_attempts", actual.get("reader_attempts"), primary)
        check(prefix + "/probes", actual.get("probes"), probes)
        for actual_key, expected_key in (("accepted_sequence", "decisions"), ("action_vector", "decisions"),
                                         ("local_endpoint_checks", "local_pass"), ("serial_violation", "serial_violation"),
                                         ("joint_only_violation", "joint_only"), ("local_endpoint_failure", "local_failure"),
                                         ("source_complete", "source_complete"), ("probe_success", "probe_success")):
            check(prefix + "/" + actual_key, actual.get(actual_key), expected[expected_key])
        check(prefix + "/allowed_sequences", sorted(actual.get("allowed_sequences", [])), expected["allowed"])
        final = save_attempts(source_tables(expected["final_source"]), primary)
        with_probes = save_attempts(final, probes)
        check(prefix + "/final", actual.get("final"), final)
        check(prefix + "/final_with_probes", actual.get("final_with_probes"), with_probes)
        expected_dumps[f"trial-{case:04d}.sqlite3"] = with_probes
        cut_control = expected["group"] == "serial_control"
        check(prefix + "/exact_cut_expected", actual.get("exact_cut_expected"), expected["decisions"] if cut_control else None)
        check(prefix + "/exact_cut_match", actual.get("exact_cut_match"), True if cut_control else None)
        label = f"trial-{case:04d}"
        if cut_control:
            phase = {"phase": "completed", "rule": expected["rule"], "order": expected["order"], "mode": "complete", "committed": True}
            expected_workers[(label, "complete")] = (0, phase)
            check(prefix + "/worker_phase", actual.get("worker_phase"), phase)
        else:
            phase = {"phase": "after_first_step", "rule": expected["rule"], "order": expected["order"], "mode": "interrupted", "committed": expected["rule"] != "whole_transaction"}
            recovery = dict(phase, phase="completed", mode="recovery", committed=True)
            expected_workers[(label, "interrupted")] = (73, phase)
            expected_workers[(label, "recovery")] = (0, recovery)
            check(prefix + "/worker_phase", actual.get("worker_phase"), phase)
            check(prefix + "/recovery_phase", actual.get("recovery_phase"), recovery)
    config = json.loads((ROOT / "config.json").read_text())
    for rule in config["primary_rules"] + config["sensitivity_rules"]:
        for order in config["orders"]:
            label = "hand-before-" + rule + "-" + order
            expected_dumps[label + ".sqlite3"] = source_tables({"fields": [1, 1], "receipts": [], "gate": int(rule in ("durable_gate", "forced_open_gate"))})
            expected_workers[(label, "exit_before")] = (73, {"phase": "before_first_update", "rule": rule, "order": order, "mode": "exit_before", "committed": False})
    expected_dumps["hand-reader-rollback.sqlite3"] = source_tables({"fields": [1, 1], "receipts": [], "gate": 0})
    dumps = read_jsonl(args.actual / "database_dumps.jsonl")
    by_name = {item["database"]: item for item in dumps}
    check("dump_names", sorted(by_name), sorted(expected_dumps))
    check("dump_no_duplicate_names", len(by_name), len(dumps))
    for name, tables in expected_dumps.items():
        check("logical_dump/" + name, by_name.get(name, {}).get("tables"), tables)
    logs = read_jsonl(args.actual / "worker_logs.jsonl")
    worker_keys = [(item["label"], item["mode"]) for item in logs]
    check("worker_keys", sorted(worker_keys), sorted(expected_workers))
    for log in logs:
        key = log["label"], log["mode"]
        if key not in expected_workers:
            continue
        status, phase = expected_workers[key]
        label = "/".join(key)
        check("worker/" + label + "/status", log["returncode"], status)
        check("worker/" + label + "/stderr", log["stderr"], "")
        check("worker/" + label + "/error", log["error"], None)
        check("worker/" + label + "/stdout", [json.loads(line) for line in log["stdout"].splitlines()], [phase])
        check("worker/" + label + "/time", log["elapsed_seconds"] >= 0 and log["cumulative_cpu_increment_seconds"] >= 0, True)
    physical = []
    def check_physical(name, path):
        tables, integrity, sql = inspect_database(path)
        check("physical/" + name + "/tables", tables, expected_dumps[name])
        check("physical/" + name + "/saved_dump", tables, by_name[name]["tables"])
        check("physical/" + name + "/sql_dump", sql, by_name[name]["sql_dump"])
        check("physical/" + name + "/integrity", integrity, ["ok"])
        physical.append({"database": name, "sha256": sha(path)})
    if args.db_dir:
        check("physical_file_names", sorted(p.name for p in args.db_dir.glob("*.sqlite3")), sorted(expected_dumps))
        for name in sorted(expected_dumps):
            check_physical(name, args.db_dir / name)
    else:
        with tempfile.TemporaryDirectory(prefix="undo-independent-") as scratch:
            with tarfile.open(args.actual / "physical_databases.tar.gz", "r:gz") as archive:
                members = archive.getmembers()
                check("archive_names", sorted(m.name for m in members), sorted(expected_dumps))
                for member in members:
                    if not member.isfile() or member.name not in expected_dumps or not re.fullmatch(r"[a-zA-Z0-9_-]+\.sqlite3", member.name):
                        raise RuntimeError("Unexpected archive member")
                    path = Path(scratch) / member.name
                    path.write_bytes(archive.extractfile(member).read())
                    check_physical(member.name, path)
                    path.unlink()
    controls = json.loads((args.actual / "hand_controls.json").read_text())
    check("physical_hand_control_count", len(controls), 19)
    check("physical_hand_controls_pass", all(c["passed"] and c["observed"] == c["expected"] for c in controls), True)
    predicted_summary = oracle.summarize(predicted)
    actual_summary = json.loads((args.actual / "summary.json").read_text())
    check("summary_row_count", len(actual_summary), len(predicted_summary))
    summary_map = {row["group"] + "/" + row["rule"]: row for row in actual_summary}
    check("summary_keys", sorted(summary_map), sorted(predicted_summary))
    names = {"accepted_jobs": "accepted_primary_jobs", "refused_jobs": "refused_primary_jobs",
             "joint_only": "joint_only_violation", "local_failure": "local_endpoint_failure"}
    for key, counts in predicted_summary.items():
        for field, value in counts.items():
            check("summary/" + key + "/" + field, summary_map.get(key, {}).get(names.get(field, field)), value)
        check("summary/" + key + "/exact_cut_matches", summary_map.get(key, {}).get("exact_cut_matches"), 768 if key.startswith("serial_control/") else 0)
    check("run_status", receipt["status"], "completed")
    check("run_error", receipt["error"], None)
    check("run_case_count", receipt["usage"]["scored_rows_saved"], 2816)
    check("run_worker_count", receipt["usage"]["worker_calls"], 4872)
    check("run_database_count", receipt["databases_retained"], 2825)
    check("run_resource_limits", receipt["usage"]["cpu_seconds"] < 600 and receipt["usage"]["wall_seconds"] < 1200, True)
    args.out.mkdir(parents=True, exist_ok=True)
    report = {"match": not differences, "logical_cases": len(observed), "expected_cases": len(predicted),
              "physical_databases_reopened": len(physical), "worker_logs_checked": len(logs),
              "checks": count, "differences": differences,
              "predictor_sha256": sha(ROOT / "independent.py"), "adapter_sha256": sha(Path(__file__)),
              "actual_sha256": {name: sha(args.actual / name) for name in ("cases.jsonl", "database_dumps.jsonl", "worker_logs.jsonl", "hand_controls.json", "execution_receipt.json")},
              "physical_source": "retained_files" if args.db_dir else "published_archive",
              "physical_manifest": physical}
    (args.out / "independent_comparison.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("physical_manifest", "actual_sha256", "differences")}, sort_keys=True))
    if differences:
        print(json.dumps(differences[:10], indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
