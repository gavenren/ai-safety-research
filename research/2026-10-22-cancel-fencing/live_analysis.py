"""Score the sanitized cancellation trace. No account or model calls."""
import argparse
import datetime
import hashlib
import json
import platform
import resource
import sys
import time
from pathlib import Path


def score(trace):
    results = []
    assert len(trace["cases"]) == 8
    assert {(r["service"], r["case"]) for r in trace["cases"]} == {(s, c) for s in ("drive", "calendar") for c in ("C1", "C2", "C3", "C4")}
    for row in trace["cases"]:
        assert row["native_target_matches"] and row["collateral_fields_equal"]
        assert row["evidence_status"] == "complete_for_declared_scope"
        assert all(row["ui_gates"].values())
        assert row["prepare_to_last_observation_seconds"] <= 480
        old = row["command_generation"] == 0
        mutation = row["logged_browser_mutations"] == 1
        results.append({
            "service": row["service"], "case": row["case"],
            "decision_allow": row["decision"]["allow"],
            "logged_browser_mutations": row["logged_browser_mutations"],
            "final_field": row["observed_final_field"],
            "old_command_sent_after_local_cancellation": old and mutation,
            "old_payload_saved_after_local_cancellation": old and mutation and row["observed_final_field"] == "OLD",
            "old_command_blocked_and_baseline_preserved": old and not mutation and row["observed_final_field"] == "BASE",
            "new_command_saved": not old and mutation and row["observed_final_field"] == "NEW",
            "checked_collateral_fields_equal": True,
            "rule_freeze_precedes_preparation": row["rule_freeze_precedes_preparation"],
            "helper_freeze_precedes_preparation": row["helper_freeze_precedes_preparation"],
        })
    return {
        "cases": results, "assigned_cases": len(results),
        "services": 2, "logged_browser_mutations": sum(r["logged_browser_mutations"] for r in results),
        "old_payload_saved_cases": sum(r["old_payload_saved_after_local_cancellation"] for r in results),
        "old_command_blocked_cases": sum(r["old_command_blocked_and_baseline_preserved"] for r in results),
        "valid_new_command_saved_cases": sum(r["new_command_saved"] for r in results),
        "checked_collateral_mismatch_cases": sum(not r["checked_collateral_fields_equal"] for r in results),
        "late_helper_freeze_cases": sum(not r["helper_freeze_precedes_preparation"] for r in results),
        "unknown_cases": 0,
        "scope": "controlled local controller order with real browser saves; no atomic receiver test",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, default=Path(__file__).with_name("live_trace.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("live_results.json"))
    parser.add_argument("--execution", type=Path, default=Path(__file__).with_name("live_execution.json"))
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cpu = time.process_time()
    wall = time.perf_counter()
    data = args.trace.read_bytes()
    result = score(json.loads(data))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    execution = {"started_at_utc": started, "finished_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 "cpu_seconds": time.process_time() - cpu, "wall_seconds": time.perf_counter() - wall,
                 "python": sys.version, "platform": platform.platform(), "cpu_limit_seconds": 30,
                 "trace_sha256": hashlib.sha256(data).hexdigest(), "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 "result_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "account_calls": 0, "model_calls": 0}
    args.execution.write_text(json.dumps(execution, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, sort_keys=True))


if __name__ == "__main__":
    main()
