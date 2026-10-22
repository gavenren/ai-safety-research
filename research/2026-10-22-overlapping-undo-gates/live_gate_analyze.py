"""Repeat gate scoring from public extracts. This does not access a website."""
import argparse
import json
from pathlib import Path

from live_rules import initial_gate_state, update_gate, gate_closed


def analyze(evidence):
    cases = []
    comparisons = 0
    for case in evidence["cases"]:
        local, actual_work = initial_gate_state(), {"A": "DONE", "B": "DONE"}
        for point in case["points"]:
            request = point["request"]
            local = update_gate(case["rule"], local, request["action"], request["op"])
            assert local == point["local_gate_state"]
            assert gate_closed(case["rule"], local) == point["gate_closed"]
            if not request["duplicate"]:
                actual_work[request["op"]] = "PENDING" if request["action"] == "C" else "DONE"
            assert actual_work == point["observed_work"]
            assert point["status"] == "verified"
            assert point["guarded_read_verified"] == (not point["gate_closed"])
            comparisons += 5
        last = case["points"][-1]
        cases.append({
            "case_id": case["case_id"], "rule": case["rule"], "schedule": case["schedule"],
            "observed_boundaries": len(case["points"]),
            "guarded_reads": sum(p["guarded_read_verified"] for p in case["points"]),
            "unsafe_permitted_reads": sum(not p["gate_closed"] and p["guarded_read_verified"] and "PENDING" in p["observed_work"].values() for p in case["points"]),
            "unnecessary_refusals": sum(p["gate_closed"] and all(v == "DONE" for v in p["observed_work"].values()) for p in case["points"]),
            "final_work_done": all(v == "DONE" for v in last["observed_work"].values()),
            "final_gate_closed": last["gate_closed"],
            "timing_eligible": case["strict_stop_rule_eligible"],
            "timing_and_fresh_metadata_eligible": case["strict_stop_rule_eligible"] and case["metadata"]["fresh_start"] and case["metadata"]["end_verified"],
            "case_seconds": case["staged_start_to_final_probe_seconds"],
        })
    assert len(cases) == 8 and sum(c["observed_boundaries"] for c in cases) == 40
    by_rule = {}
    for rule in sorted({c["rule"] for c in cases}):
        group = [c for c in cases if c["rule"] == rule]
        by_rule[rule] = {"cases": len(group), "boundaries": sum(c["observed_boundaries"] for c in group),
                         "guarded_reads": sum(c["guarded_reads"] for c in group),
                         "unsafe_permitted_reads": sum(c["unsafe_permitted_reads"] for c in group),
                         "unnecessary_refusals": sum(c["unnecessary_refusals"] for c in group),
                         "final_closed_cases": sum(c["final_gate_closed"] for c in group)}
    return {"status": "descriptive_results_with_protocol_deviations",
            "publication_ready": False, "cleanup_review": "separate_required_check",
            "cases": cases, "by_rule": by_rule,
            "assigned_cases": 8, "observed_boundaries": 40, "scored_browser_renames": 32,
            "verified_guarded_reads": sum(c["guarded_reads"] for c in cases),
            "unsafe_permitted_reads": sum(c["unsafe_permitted_reads"] for c in cases),
            "unnecessary_refusals": sum(c["unnecessary_refusals"] for c in cases),
            "timing_eligible_cases": sum(c["timing_eligible"] for c in cases),
            "timing_and_fresh_metadata_eligible_cases": sum(c["timing_and_fresh_metadata_eligible"] for c in cases),
            "controller_replay_comparisons": comparisons,
            "limits": ["These are selected paired cases on two reused folders, not independent tasks or failure rates.",
                       "Repeat deliveries affect a local controller, not a provider API.",
                       "There is no separately measured gate activation clock.",
                       "One observation exceeded the frozen 30-second bound; one case lacked a fresh full start metadata read.",
                       "No native provider lock or atomic read guarantee was tested."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = analyze(json.loads(args.evidence.read_text()))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "observed_boundaries", "verified_guarded_reads", "unsafe_permitted_reads", "unnecessary_refusals")}))


if __name__ == "__main__":
    main()
