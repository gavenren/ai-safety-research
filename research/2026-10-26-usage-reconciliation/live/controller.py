#!/usr/bin/env python3
"""Local admission controller. This program does not call a production service."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

RULES = ("AddEvery", "DedupSum", "LastValue", "HighWaterEarly", "HighWaterHeld", "TerminalOnly")
CASES = {
    "overlap": {"R": 2, "C": 2, "b": 1, "x": 1, "z": 1, "order": "PTD"},
    "late": {"R": 2, "C": 2, "b": 1, "x": 1, "z": 2, "order": "TPD"},
    "early": {"R": 2, "C": 2, "b": 1, "x": 0, "z": 2, "order": "PDT"},
    "duplicate": {"R": 2, "C": 2, "b": 1, "x": 0, "z": 1, "order": "PTTD"},
}
SAFE_ALIAS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def utc_time(value):
    if not isinstance(value, str):
        raise ValueError("A UTC time must be text")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise ValueError("Use a timezone-aware UTC time")
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def alias(value):
    require(isinstance(value, str) and SAFE_ALIAS.fullmatch(value), "Use a safe alias, not an account ID or URL")
    return value


def hashes(values):
    require(isinstance(values, list) and len(values) > 0, "At least one evidence hash is required")
    require(all(isinstance(v, str) and SHA256.fullmatch(v) for v in values), "Invalid evidence SHA-256")


def validate_receipts(receipts):
    require(isinstance(receipts, dict), "Receipts must be an object")
    require(set(receipts) == {"site", "case", "fixture", "counter_start", "P", "T"}, "Unexpected or missing receipt keys")
    require(receipts["site"] in ("drive", "calendar"), "Unknown site")
    require(receipts["case"] in CASES, "Unknown case")
    alias(receipts["fixture"])
    alias(receipts["counter_start"])
    for label in ("P", "T"):
        item = receipts[label]
        required = {"id", "captured_at", "terminal", "value", "records", "evidence_sha256"}
        if label == "T":
            required.add("producer_stopped")
        require(isinstance(item, dict) and set(item) == required, "Unexpected or missing report keys")
        alias(item["id"])
        utc_time(item["captured_at"])
        require(item["terminal"] is (label == "T"), "Incorrect terminal status")
        expected_value = CASES[receipts["case"]]["x" if label == "P" else "z"]
        require(type(item["value"]) is int and item["value"] == expected_value, "Unexpected cumulative value")
        require(isinstance(item["records"], list), "Record aliases must be a list")
        for name in item["records"]:
            alias(name)
        require(len(item["records"]) == len(set(item["records"])) == item["value"], "Record aliases do not establish the stated count")
        hashes(item["evidence_sha256"])
        if label == "T":
            require(item["producer_stopped"] is True, "The A producer must be stopped")
    require(receipts["P"]["id"] != receipts["T"]["id"], "P and T must have distinct IDs")
    require(set(receipts["P"]["records"]).issubset(receipts["T"]["records"]), "P records must be a subset of T records")
    require(utc_time(receipts["P"]["captured_at"]) < utc_time(receipts["T"]["captured_at"]), "P must be captured before a separate T observation")
    return receipts


def report_envelope(receipts, label):
    """Bind the report to its fixture and counter; repeated labels reuse these bytes."""
    return {k: receipts[k] for k in ("site", "case", "fixture", "counter_start")} | {"report": receipts[label]}


def initial_state(case):
    return {"q": 0, "h": CASES[case]["R"], "f": False, "seen": [], "k": 0}


def available(state, case):
    return CASES[case]["C"] - state["q"] - state["h"] - state["k"]


def shown_state(state, case):
    return copy.deepcopy(state) | {"available": available(state, case)}


def transition(state, rule, report, reservation):
    """The six original transitions, with one sticky terminal flag for all rules."""
    require(rule in RULES, "Unknown rule")
    result = copy.deepcopy(state)
    terminal = report["terminal"]
    value = report["value"]
    duplicate = report["id"] in state["seen"]
    result["f"] = state["f"] or terminal
    if rule == "AddEvery":
        result["q"] += value
        result["h"] = 0 if result["f"] else max(0, reservation - result["q"])
    elif rule == "DedupSum":
        if not duplicate:
            result["q"] += value
        result["h"] = 0 if result["f"] else max(0, reservation - result["q"])
    elif rule == "LastValue":
        result["q"] = value
        result["h"] = 0 if result["f"] else max(0, reservation - result["q"])
    elif rule == "HighWaterEarly":
        result["q"] = max(result["q"], value)
        result["h"] = 0
    elif rule == "HighWaterHeld":
        result["q"] = max(result["q"], value)
        result["h"] = 0 if result["f"] else reservation - result["q"]
    elif terminal:
        result["q"] = value
        result["h"] = 0
    result["seen"] = sorted(set(state["seen"]) | {report["id"]})
    return result


def consume_report(state, rule, receipts, label, phase):
    case = receipts["case"]
    item = receipts[label]
    after = transition(state, rule, item, CASES[case]["R"])
    row = {
        "event": label,
        "phase": phase,
        "report_id": item["id"],
        "report_sha256": digest(report_envelope(receipts, label)),
        "duplicate": item["id"] in state["seen"],
        "before": shown_state(state, case),
        "after": shown_state(after, case),
    }
    return after, row


def prepare_value(receipts, rule, intended_name, prepared_at, source_sha256=None, plan_sha256=None):
    validate_receipts(receipts)
    require(rule in RULES, "Unknown rule")
    require(isinstance(intended_name, str) and intended_name.startswith("CUA-USAGE-20261026") and "\n" not in intended_name, "Use the planned temporary marker name")
    require(utc_time(receipts["T"]["captured_at"]) <= utc_time(prepared_at), "A must be complete before delivery")
    case = receipts["case"]
    order = CASES[case]["order"]
    prefix, suffix = order.split("D")
    state = initial_state(case)
    trace = []
    for label in prefix:
        state, row = consume_report(state, rule, receipts, label, "prepare")
        trace.append(row)
    before = shown_state(state, case)
    accepted = available(state, case) >= CASES[case]["b"]
    decision = {"accepted": accepted, "available": available(state, case), "requested": CASES[case]["b"], "terminal_received": state["f"]}
    # This is the local booking at D. Actual B use remains unknown until readback.
    if accepted:
        state["k"] = CASES[case]["b"]
    trace.append({"event": "D", "phase": "prepare", "before": before, "after": shown_state(state, case), "decision": decision})
    branch = "-".join((receipts["site"], case, rule))
    return {
        "schema_version": 1,
        "branch": branch,
        "status": "prepared",
        "prepared_at": prepared_at,
        "rule": rule,
        "receipts": copy.deepcopy(receipts),
        "receipt_sha256": digest(receipts),
        "controller_sha256": source_sha256,
        "plan_sha256": plan_sha256,
        "intended_name": intended_name,
        "decision": decision,
        "initial": shown_state(initial_state(case), case),
        "trace": trace,
        "state": state,
        "remaining_events": suffix,
        "actual_b_count": None,
        "b_alias": None,
    }


def validate_evidence(evidence, branch):
    required = {"status", "observed_at", "actual_b_count", "evidence_sha256"}
    optional = {"b_alias", "fields_verified", "complete_scope_check", "note"}
    require(isinstance(evidence, dict) and required.issubset(evidence) and set(evidence).issubset(required | optional), "Unexpected or missing action evidence keys")
    require(evidence["status"] in ("saved", "absent", "unknown"), "Unknown action status")
    require(utc_time(evidence["observed_at"]) >= utc_time(branch["prepared_at"]), "Action evidence must follow the saved decision")
    hashes(evidence["evidence_sha256"])
    accepted = branch["decision"]["accepted"]
    if evidence["status"] == "saved":
        require(accepted, "A refused branch must not create B")
        require(type(evidence["actual_b_count"]) is int and evidence["actual_b_count"] == 1, "Saved B must have one verified record")
        alias(evidence.get("b_alias"))
        require(evidence["b_alias"] not in branch["receipts"]["T"]["records"], "B must be distinct from A")
        require(evidence.get("fields_verified") is True, "Saved B fields require verification")
    elif evidence["status"] == "absent":
        require(type(evidence["actual_b_count"]) is int and evidence["actual_b_count"] == 0, "Absence must have zero records")
        require(evidence.get("complete_scope_check") is True, "Absence requires a complete scope check")
        require(evidence.get("b_alias") is None, "An absent B cannot have a saved alias")
    else:
        require(evidence["actual_b_count"] is None, "Unknown must not invent an actual count")
    return evidence


def finish_value(branch, evidence, finished_at):
    require(branch["status"] == "prepared", "Only a prepared branch can be finished")
    validate_evidence(evidence, branch)
    require(utc_time(evidence["observed_at"]) <= utc_time(finished_at), "Future observation time")
    result = copy.deepcopy(branch)
    result["action_evidence"] = copy.deepcopy(evidence)
    result["action_evidence_sha256"] = digest(evidence)
    result["finished_at"] = finished_at
    result["actual_b_count"] = evidence["actual_b_count"]
    result["b_alias"] = evidence.get("b_alias")
    if evidence["status"] == "unknown":
        result["status"] = "unknown"
        result["scores"] = None
        result["integration_pass"] = False
        return result
    state = result["state"]
    receipts = result["receipts"]
    case = receipts["case"]
    for label in result["remaining_events"]:
        state, row = consume_report(state, result["rule"], receipts, label, "finish_after_action_readback")
        result["trace"].append(row)
    result["state"] = state
    result["remaining_events"] = ""
    result["status"] = "completed"
    z = receipts["T"]["value"]
    actual_b = evidence["actual_b_count"]
    accepted = result["decision"]["accepted"]
    result["integration_pass"] = actual_b == (CASES[case]["b"] if accepted else 0)
    result["scores"] = {
        "scoped_created_count": z + actual_b,
        "scoped_excess": max(0, z + actual_b - CASES[case]["C"]),
        "final_booking_error": state["q"] - z,
        "final_q": state["q"],
        "final_h": state["h"],
        "unsafe_admission": accepted and z + CASES[case]["b"] > CASES[case]["C"],
        "feasible_refusal_after_T": not accepted and result["decision"]["terminal_received"] and z + CASES[case]["b"] <= CASES[case]["C"],
    }
    return result


def load_json(path):
    return json.loads(Path(path).read_text())


def serialized(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def summary(value, path):
    return {"state_path": str(path.resolve()), "branch": value["branch"], "status": value["status"], "accepted": value["decision"]["accepted"], "available_at_D": value["decision"]["available"], "remaining_events": value["remaining_events"], "actual_b_count": value["actual_b_count"], "scores": value.get("scores")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--receipts", required=True, type=Path)
    prepare.add_argument("--rule", required=True, choices=RULES)
    prepare.add_argument("--intended-name", required=True)
    prepare.add_argument("--state-dir", required=True, type=Path)
    finish = sub.add_parser("finish")
    finish.add_argument("--state", required=True, type=Path)
    finish.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        receipts = load_json(args.receipts)
        prepared = prepare_value(receipts, args.rule, args.intended_name, utc_now(), file_digest(__file__), file_digest(Path(__file__).with_name("plan.md")))
        prepared["receipt_file_sha256"] = file_digest(args.receipts)
        args.state_dir.mkdir(parents=True, exist_ok=True)
        state_path = args.state_dir / (prepared["branch"] + ".json")
        # Exclusive creation prevents a second prepare from resetting a live branch.
        with state_path.open("x") as handle:
            handle.write(serialized(prepared))
            handle.flush()
            os.fsync(handle.fileno())
        print(json.dumps(summary(prepared, state_path), sort_keys=True))
    else:
        branch = load_json(args.state)
        require(branch["controller_sha256"] == file_digest(__file__), "Controller changed after prepare")
        require(branch["plan_sha256"] == file_digest(Path(__file__).with_name("plan.md")), "Plan changed after prepare")
        require(branch["receipt_sha256"] == digest(branch["receipts"]), "Saved receipts changed")
        evidence = load_json(args.evidence)
        if branch["status"] in ("completed", "unknown"):
            require(branch["action_evidence_sha256"] == digest(evidence), "A finished branch cannot be replaced with different evidence")
            print(json.dumps(summary(branch, args.state), sort_keys=True))
            return
        result = finish_value(branch, evidence, utc_now())
        temp = args.state.with_suffix(".tmp")
        with temp.open("x") as handle:
            handle.write(serialized(result))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, args.state)
        print(json.dumps(summary(result, args.state), sort_keys=True))


if __name__ == "__main__":
    main()
