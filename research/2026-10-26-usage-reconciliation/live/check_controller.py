#!/usr/bin/env python3
"""Pre-execution controller checks. These use invented evidence, not live records."""
import copy
import importlib.util
import json
from pathlib import Path
import controller as c

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("original_simulator", ROOT.parent / "run_study.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
EXPECTED = {
    "overlap": [False, False, True, True, True, True],
    "late": [False, False, True, False, False, False],
    "early": [False, False, False, True, False, False],
    "duplicate": [False, True, True, True, True, True],
}


def synthetic_receipts(site, case):
    setting = c.CASES[case]
    records = [f"{site}-{case}-A{i+1}" for i in range(setting["z"])]
    return {"site": site, "case": case, "fixture": f"{site}-{case}", "counter_start": f"test-{site}-{case}",
            "P": {"id": "P", "captured_at": "2026-10-26T00:00:01Z", "terminal": False, "value": setting["x"], "records": records[:setting["x"]], "evidence_sha256": ["0"*64]},
            "T": {"id": "T", "captured_at": "2026-10-26T00:00:02Z", "terminal": True, "value": setting["z"], "records": records, "evidence_sha256": ["1"*64], "producer_stopped": True}}


def main():
    rows = []
    state_comparisons = 0
    for site in ("drive", "calendar"):
        for case, setting in c.CASES.items():
            receipts = synthetic_receipts(site, case)
            for index, rule in enumerate(c.RULES):
                branch = c.prepare_value(receipts, rule, "CUA-USAGE-20261026-unit-test", "2026-10-26T00:00:03Z")
                assert branch["decision"]["accepted"] is EXPECTED[case][index]
                assert branch["trace"][-1]["event"] == "D"
                if case == "early":
                    assert branch["remaining_events"] == "T"
                    assert not branch["state"]["f"]
                admitted = branch["decision"]["accepted"]
                evidence = {"status": "saved" if admitted else "absent", "observed_at": "2026-10-26T00:00:04Z", "actual_b_count": int(admitted), "evidence_sha256": ["2"*64]}
                if admitted:
                    evidence.update(b_alias=f"{site}-{case}-{rule}-B1", fields_verified=True)
                else:
                    evidence["complete_scope_check"] = True
                done = c.finish_value(branch, evidence, "2026-10-26T00:00:05Z")
                baseline = original.simulate({"id": case, **setting}, rule)
                for live, old in zip(done["trace"], baseline["events"], strict=True):
                    assert live["event"] == old["event"]
                    assert live["before"] == old["before"]
                    assert live["after"] == old["after"]
                    state_comparisons += 2
                assert done["scores"]["final_booking_error"] == baseline["scores"]["final_error"]
                assert done["scores"]["scoped_excess"] == baseline["scores"]["actual_excess_max"]
                assert done["scores"]["feasible_refusal_after_T"] == baseline["scores"]["receipt_sufficient_refusal"]
                rows.append({"site": site, "case": case, "rule": rule, "accepted": admitted, **done["scores"]})
    bad = synthetic_receipts("drive", "overlap")
    bad["T"]["id"] = "P"
    try:
        c.validate_receipts(bad)
        raise AssertionError("Same-ID P/T was accepted")
    except ValueError:
        pass
    early = c.prepare_value(synthetic_receipts("drive", "early"), "HighWaterEarly", "CUA-USAGE-20261026-unit-test", "2026-10-26T00:00:03Z")
    unknown = c.finish_value(early, {"status": "unknown", "observed_at": "2026-10-26T00:00:04Z", "actual_b_count": None, "evidence_sha256": ["3"*64]}, "2026-10-26T00:00:05Z")
    assert unknown["status"] == "unknown" and unknown["remaining_events"] == "T" and unknown["scores"] is None
    output = {"kind": "pre-execution unit checks; no production observations", "passed": True, "branches": len(rows), "state_comparisons": state_comparisons, "expected_B_writes": sum(r["accepted"] for r in rows), "rows": rows, "guards": ["distinct_report_IDs", "unknown_does_not_consume_tail_T"]}
    (ROOT / "controller_checks.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "rows"}, sort_keys=True))


if __name__ == "__main__":
    main()
