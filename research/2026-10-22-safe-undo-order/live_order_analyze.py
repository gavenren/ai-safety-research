"""Repeat order scoring from public extracts. No live account access."""
import argparse
import json
from pathlib import Path
from live_rules import order_path


def analyze(evidence):
    rows, comparisons = [], 0
    for case in evidence["cases"]:
        actual = [p["observed_state"] for p in case["points"]]
        expected = order_path(case["rule"], case["valid_states"])
        assert actual == expected
        assert all(p["status"] == "verified" for p in case["points"])
        assert all(case["metadata"]["baseline_checks"].values())
        assert all(case["metadata"]["final_checks"].values())
        assert case["metadata"]["all_other_exposed_fields_unchanged"]
        assert all(s["verified"] for s in case["writes"])
        comparisons += 6
        rows.append({"case_id": case["case_id"], "condition": case["condition"], "rule": case["rule"],
                     "observed_path": actual, "browser_field_changes": len(case["writes"]),
                     "target_reached": actual[-1] == "000",
                     "all_saved_states_valid": all(s in case["valid_states"] for s in actual),
                     "partial_stop": actual[-1] != "000",
                     "invalid_saved_states": [s for s in actual if s not in case["valid_states"]],
                     "baseline_to_last_read_seconds": case["baseline_to_last_read_seconds"],
                     "max_post_save_UI_to_read_seconds": max((w["post_save_UI_to_read_seconds"] for w in case["writes"]), default=0)})
    assert len(rows) == 6 and sum(r["browser_field_changes"] for r in rows) == 16
    return {"status": "observed_controller_paths_with_stated_limits", "publication_ready": False,
            "assigned_cases": 6, "saved_editor_observations": sum(len(r["observed_path"]) for r in rows),
            "browser_field_changes": 16, "target_reached_cases": sum(r["target_reached"] for r in rows),
            "valid_completion_cases": sum(r["target_reached"] and r["all_saved_states_valid"] for r in rows),
            "partial_stops": sum(r["partial_stop"] for r in rows),
            "cases_with_invalid_saved_state": sum(bool(r["invalid_saved_states"]) for r in rows),
            "replay_comparisons": comparisons, "cases": rows,
            "limits": ["The validity condition is supplied by the researcher, not enforced by Calendar.",
                       "Baseline connector reads were a batch before the cases, not a separate immediate read before each case.",
                       "Fields were read sequentially after Save, not as an atomic server snapshot.",
                       "The selected cases do not estimate task failure rates or autonomous agent performance.",
                       "The partial stop is relative to one-way actions; later correction remains possible.",
                       "Cleanup and separate review require final confirmation."]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("evidence", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    result = analyze(json.loads(args.evidence.read_text()))
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "assigned_cases", "browser_field_changes", "valid_completion_cases", "partial_stops")}))


if __name__ == "__main__":
    main()
