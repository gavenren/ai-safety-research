#!/usr/bin/env python3
"""Independent prefix calculation. It does not read the live controller.

The values in this file are planned controls, not website observations.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

RULES = ("AddEvery", "DedupSum", "LastValue", "HighWaterEarly",
         "HighWaterHeld", "TerminalOnly")
CASES = {
    "overlap": {"x": 1, "z": 1, "order": "PTD"},
    "late": {"x": 1, "z": 2, "order": "TPD"},
    "early": {"x": 0, "z": 2, "order": "PDT"},
    "duplicate": {"x": 0, "z": 1, "order": "PTTD"},
}
SITES = ("drive", "calendar")
R, C, B = 2, 2, 1


def ledger(prefix, rule, case):
    """Derive A state from the whole report prefix, without state mutation."""
    reports = [event for event in prefix if event in ("P", "T")]
    unique = set(reports)
    values = {"P": case["x"], "T": case["z"]}
    terminal = "T" in unique
    if not reports:
        booked, hold = 0, R
    elif rule == "AddEvery":
        booked = sum(values[event] for event in reports)
        hold = 0 if terminal else max(0, R - booked)
    elif rule == "DedupSum":
        booked = sum(values[event] for event in unique)
        hold = 0 if terminal else max(0, R - booked)
    elif rule == "LastValue":
        booked = values[reports[-1]]
        hold = 0 if terminal else max(0, R - booked)
    elif rule == "HighWaterEarly":
        booked = max(values[event] for event in unique)
        hold = 0
    elif rule == "HighWaterHeld":
        booked = max(values[event] for event in unique)
        hold = 0 if terminal else R - booked
    elif rule == "TerminalOnly":
        booked = values["T"] if terminal else 0
        hold = 0 if terminal else R
    else:
        raise ValueError(rule)
    return {"q": booked, "h": hold, "f": terminal,
            "seen": sorted(unique)}


def expected(site, case_name, rule):
    case = CASES[case_name]
    order = case["order"]
    d = order.index("D")
    before_d = ledger(order[:d], rule, case)
    balance = C - before_d["q"] - before_d["h"]
    accepted = balance >= B
    states = []
    for length in range(len(order) + 1):
        prefix = order[:length]
        state = ledger(prefix, rule, case)
        k = B if "D" in prefix and accepted else 0
        state.update(k=k, available=C-state["q"]-state["h"]-k)
        states.append(state)
    final_error = states[-1]["q"] - case["z"]
    return {
        "site": site, "case": case_name, "rule": rule,
        "input": {"R": R, "C": C, "b": B, **case},
        "initial": states[0],
        "events": [{"event": event, "before": states[i],
                    "after": states[i+1]} for i, event in enumerate(order)],
        "decision": {"accepted": accepted, "available": balance,
                     "terminal_seen": before_d["f"]},
        "final": states[-1],
        "expected_b_writes": int(accepted),
        "expected_scoped_use": case["z"] + int(accepted),
        "expected_scoped_excess": max(0, case["z"]+int(accepted)-C),
        "final_error": final_error,
        "final_overcount": final_error > 0,
        "final_undercount": final_error < 0,
        "receipt_sufficient_refusal": (not accepted and before_d["f"]
                                       and case["z"] + B <= C),
    }


def build():
    rows = [expected(site, case, rule) for site in SITES
            for case in CASES for rule in RULES]
    summary = []
    for site in (*SITES, "ALL"):
        for rule in RULES:
            group = [r for r in rows if r["rule"] == rule
                     and (site == "ALL" or r["site"] == site)]
            summary.append({
                "site": site, "rule": rule, "decisions": len(group),
                "permitted_b_writes": sum(r["expected_b_writes"] for r in group),
                "refused_b_writes": sum(not r["decision"]["accepted"] for r in group),
                "scoped_excess_cases": sum(r["expected_scoped_excess"] > 0 for r in group),
                "final_overcounts": sum(r["final_overcount"] for r in group),
                "final_undercounts": sum(r["final_undercount"] for r in group),
                "receipt_sufficient_refusals": sum(r["receipt_sufficient_refusal"] for r in group),
            })
    expected_per_site = {
        "AddEvery": (0, 0, 3, 0, 2),
        "DedupSum": (1, 0, 2, 0, 1),
        "LastValue": (3, 1, 0, 1, 0),
        "HighWaterEarly": (3, 1, 0, 0, 0),
        "HighWaterHeld": (2, 0, 0, 0, 0),
        "TerminalOnly": (2, 0, 0, 0, 0),
    }
    for row in summary:
        multiplier = 2 if row["site"] == "ALL" else 1
        values = tuple(row[key] for key in ("permitted_b_writes", "scoped_excess_cases",
                       "final_overcounts", "final_undercounts", "receipt_sufficient_refusals"))
        assert values == tuple(multiplier * n for n in expected_per_site[row["rule"]])
    assert len(rows) == 48
    assert sum(r["expected_b_writes"] for r in rows) == 22
    assert sum(r["expected_scoped_excess"] > 0 for r in rows) == 4
    for site in SITES:
        for case in CASES:
            held = expected(site, case, "HighWaterHeld")
            final = expected(site, case, "TerminalOnly")
            assert held["decision"] == final["decision"]
            assert held["final"] == final["final"]
    return {
        "status": "Independent planned calculations; no live outcomes read",
        "method": "A state is derived from each complete report prefix.",
        "planned_sites": list(SITES),
        "planned_fixtures": len(SITES) * len(CASES),
        "planned_actual_a_records": len(SITES) * sum(c["z"] for c in CASES.values()),
        "planned_rule_decisions": len(rows),
        "planned_permitted_b_writes": 22,
        "planned_total_records_excluding_containers": 34,
        "rows": rows, "summary": summary,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
