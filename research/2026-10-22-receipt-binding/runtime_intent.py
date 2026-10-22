"""Record local cancellation and receipt decisions before browser actions.

No network or browser calls. No account mutations. A preparation record is not
evidence that a browser action was sent or that a provider saved a value.
"""
import argparse
import contextlib
import datetime
import hashlib
import json
import os
from pathlib import Path
import tempfile
import base64
from urllib.parse import parse_qs, urlparse

from live_intent import canonical_json, check_generation, envelope_hash, receipt_decision

HERE = Path(__file__).resolve().parent
ACCOUNT_ALIAS = "connected-account-1"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path, value):
    """Write and fsync a same-directory temporary file, then replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def new_record(path):
    """One writer per case. Preserve any existing or partial record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        if path.exists():
            raise FileExistsError(f"Record already exists; inspect it before any action: {path}")
        yield
    finally:
        lock.unlink()


def event(record, name, **fields):
    row = {"sequence": len(record["events"]) + 1, "time_utc": utc(), "event": name}
    row.update(fields)
    record["events"].append(row)


def verify_frozen_rules(base):
    freeze = json.loads((base / "execution_freeze.json").read_text())
    actual = sha(base / "live_intent.py")
    if actual != freeze["sha256"]["live_intent.py"]:
        raise ValueError("Frozen live_intent.py hash does not match")
    return actual


def field_value(service, fixture, alias, suffix):
    if service == "calendar":
        return {"description": suffix}
    baseline_name = fixture["args"]["name"]
    if not baseline_name.endswith(" BASE"):
        raise ValueError("Drive fixture has no exact BASE suffix")
    if f" {alias} " not in baseline_name:
        raise ValueError("Drive fixture alias is not in its baseline name")
    return {"name": baseline_name[:-len("BASE")] + suffix}


def cancel_prepare(base, service, case):
    rule_hash = verify_frozen_rules(base)
    manifest = json.loads((base / "private/manifest.json").read_text())
    alias = "CANCEL-" + case
    fixture = manifest[service + ":" + alias]
    path = base / "private" / f"intent-cancel-{service}-{case}.json"
    with new_record(path):
        record = {
            "kind": "cancellation_prepare", "service": service, "case": case,
            "target_alias": alias, "native_target": fixture["id"], "target_url": fixture["url"],
            "prepared_at_utc": utc(), "rule_sha256": rule_hash, "helper_sha256": sha(Path(__file__)),
            "state": {"generation": 0, "active": True}, "events": [],
            "browser_action_sent": None, "browser_action_time": None,
            "saved_state": None, "status": "preparing", "account_mutations_by_helper": 0,
        }
        event(record, "initial_state", **record["state"])
        atomic_json(path, record)
        if case in ("C1", "C2", "C3"):
            command_generation = 0
            cached = check_generation(command_generation, record["state"]["generation"], record["state"]["active"])
            event(record, "final_check" if case == "C3" else "initial_check", command_generation=0,
                  observed_state=dict(record["state"]), allow=cached)
            atomic_json(path, record)
        record["state"]["active"] = False
        event(record, "cancel_acknowledged_locally", retired_generation=0, state=dict(record["state"]))
        atomic_json(path, record)
        record["state"] = {"generation": 1, "active": True}
        event(record, "restart", state=dict(record["state"]))
        atomic_json(path, record)
        if case in ("C2", "C4"):
            command_generation = 0 if case == "C2" else 1
            allowed = check_generation(command_generation, record["state"]["generation"], record["state"]["active"])
            event(record, "final_check", command_generation=command_generation,
                  observed_state=dict(record["state"]), allow=allowed)
            basis = "fresh_generation_check"
        else:
            allowed = cached
            basis = "cached_check_before_cancellation"
        suffix = ("NEW" if command_generation == 1 else "OLD") if allowed else None
        record["expected_dispatch"] = suffix if suffix else "none"
        record["expected_browser_fields"] = field_value(service, fixture, alias, suffix) if suffix else None
        record["command_generation"] = command_generation
        record["decision"] = {"allow": allowed, "basis": basis, "dispatch_payload": suffix}
        event(record, "dispatch_decision", **record["decision"], browser_action_performed=False)
        record["status"] = "prepared_before_browser_action"
        atomic_json(path, record)
    return {"record": str(path), "expected_dispatch": record["expected_dispatch"],
            "browser_fields": record["expected_browser_fields"], "browser_action_performed": False}


def check_first_read(service, alias, fixture, wrapper):
    """Check exact saved fields. The wrapper time is a READ time, not a UI time."""
    errors = []
    timestamp = wrapper.get("time")
    try:
        parsed = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() != datetime.timedelta(0):
            errors.append("read_time_not_UTC")
        if parsed > datetime.datetime.now(datetime.timezone.utc):
            errors.append("read_time_in_future")
    except (AttributeError, TypeError, ValueError):
        errors.append("missing_or_invalid_read_time")
    response = wrapper.get("result")
    if not isinstance(response, dict) or response.get("isError"):
        return False, errors + ["read_tool_failed_or_missing"], None
    actual = response.get("structuredContent")
    if not isinstance(actual, dict):
        return False, errors + ["missing_structured_content"], None
    baseline = fixture["baseline"]
    expected = {}
    if service == "drive":
        expected = {
            "id": fixture["id"], "title": field_value(service, fixture, alias, "PAYLOAD-A")["name"],
            "mime_type": "application/vnd.google-apps.folder", "file_or_folder": "folder",
            "parent_ids": [fixture["args"]["parent_folder"]], "shared": False,
        }
    else:
        fields = ["id", "summary", "status", "start", "end", "location", "transparency", "visibility",
                  "hangout_link", "reminders", "recurrence", "recurring_event_id", "attendees", "organizer"]
        expected = {k: baseline[k] for k in fields}
        expected["id"] = fixture["id"]
        if type(actual.get("description")) is not str or actual["description"].rstrip("\r\n") != "PAYLOAD-A":
            errors.append("description_not_exact_PAYLOAD_A")
    for field, value in expected.items():
        if field not in actual or canonical_json(actual[field]) != canonical_json(value):
            errors.append("saved_field_mismatch_or_missing:" + field)
    return not errors, errors, actual


def timestamp_utc(value):
    parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != datetime.timedelta(0):
        raise ValueError("Timestamp must be UTC")
    return parsed


def calendar_url_id(url):
    parsed = urlparse(url)
    if parsed.hostname not in {"calendar.google.com", "www.google.com"}:
        raise ValueError("Unexpected Calendar hostname")
    eid = parse_qs(parsed.query).get("eid", [None])[0]
    if eid is None and "/eventedit/" in parsed.path:
        eid = parsed.path.split("/eventedit/", 1)[1].split("/", 1)[0]
    if not eid:
        raise ValueError("Calendar URL has no event identity")
    decoded = base64.urlsafe_b64decode(eid + "=" * (-len(eid) % 4)).decode("utf-8")
    return decoded.split(" ", 1)[0]


def check_action_evidence(base, service, alias, fixture, read_wrapper, now=None):
    """Require recorded UI fields and a fresh UI/action/read order.

    The helper validates recorded observations. It cannot authenticate the
    observer or infer a browser action from a timestamp alone.
    """
    errors = []
    now = now or datetime.datetime.now(datetime.timezone.utc)
    label = f"first-{service}-{alias}"
    paths = {
        "before_ui": base / "private" / f"intent-ui-{service}-{alias}.json",
        "dispatch": base / "private" / f"dispatch-{label}.json",
        "sent_ui": base / "private" / f"ui-{label}-sent.json",
    }
    records = {}
    references = {}
    for name, path in paths.items():
        try:
            data = path.read_bytes()
            records[name] = json.loads(data)
            references[name] = {"file": path.name, "sha256": hashlib.sha256(data).hexdigest()}
        except (OSError, ValueError):
            errors.append("missing_or_invalid_evidence:" + name)
    if len(records) != 3:
        return False, errors, {"references": references}
    ui, dispatch, sent = (records[n] for n in ["before_ui", "dispatch", "sent_ui"])
    if ui.get("service") != service or ui.get("alias") != alias or ui.get("observed_id") != fixture["id"]:
        errors.append("UI_identity_mismatch")
    if dispatch.get("label") != label:
        errors.append("dispatch_label_mismatch")
    if not isinstance(sent.get("state"), str) or not sent["state"] or not isinstance(sent.get("role"), str) or not sent["role"]:
        errors.append("missing_postclick_UI_observation")
    values = ui.get("values")
    if not isinstance(values, dict):
        values = {}
        errors.append("missing_UI_values")
    try:
        if service == "drive":
            parent = fixture["args"]["parent_folder"]
            parsed = urlparse(ui["url"])
            if parsed.hostname != "drive.google.com" or not parsed.path.rstrip("/").endswith("/folders/" + parent):
                errors.append("Drive_UI_parent_URL_mismatch")
            if values.get("active_parent_id") != parent:
                errors.append("Drive_UI_parent_identity_mismatch")
            if values.get("rename_input_value") != field_value(service, fixture, alias, "PAYLOAD-A")["name"]:
                errors.append("Drive_UI_intended_name_mismatch")
        else:
            if calendar_url_id(ui["url"]) != fixture["id"]:
                errors.append("Calendar_UI_URL_identity_mismatch")
            for key, expected in {"description": "PAYLOAD-A", "all_day": True, "availability": "Free", "visibility": "Private"}.items():
                if key not in values or canonical_json(values[key]) != canonical_json(expected):
                    errors.append("Calendar_UI_field_mismatch_or_missing:" + key)
    except (KeyError, TypeError, ValueError, UnicodeError):
        errors.append("invalid_UI_identity_URL")
    source = ui.get("source_file")
    if not isinstance(source, str) or not source:
        errors.append("missing_raw_UI_source")
    else:
        source_path = base / "private" / source
        if source_path.resolve().parent != (base / "private").resolve() or source_path.resolve() == paths["before_ui"].resolve():
            errors.append("invalid_raw_UI_source_reference")
        elif not source_path.is_file() or not source_path.stat().st_size:
            errors.append("raw_UI_source_not_present")
        else:
            references["raw_ui_source"] = {"file": source, "sha256": sha(source_path)}
    try:
        times = [timestamp_utc(x["time"]) for x in [ui, dispatch, sent, read_wrapper]]
        if not times[0] <= times[1] <= times[2] <= times[3] <= now:
            errors.append("UI_action_read_order_invalid")
        if now - times[0] > datetime.timedelta(minutes=8):
            errors.append("first_operation_evidence_exceeds_case_time_limit")
    except (KeyError, AttributeError, TypeError, ValueError):
        errors.append("invalid_UI_action_read_time")
    details = {"references": references, "ui_observation_time_utc": ui.get("time"),
               "browser_dispatch_time_utc": dispatch.get("time"), "postclick_UI_time_utc": sent.get("time"),
               "first_read_time_utc": read_wrapper.get("time"), "check_errors": errors}
    return not errors, errors, details


def receipt_prepare(base, service, policy, pair):
    rule_hash = verify_frozen_rules(base)
    manifest = json.loads((base / "private/manifest.json").read_text())
    case_alias = f"RECEIPT-{policy}-{pair}"
    alias_a = case_alias + "-A"
    source = base / "private" / f"intent-first-{service}-{alias_a}.json"
    if not source.exists():
        raise FileNotFoundError(f"Save the first independent read before this command: {source}")
    source_bytes = source.read_bytes()
    wrapper = json.loads(source_bytes)
    fixture_a = manifest[service + ":" + alias_a]
    alias_second = case_alias + ("-B" if pair == "TARGET" else "-A")
    fixture_second = manifest[service + ":" + alias_second]
    read_complete, errors, actual = check_first_read(service, alias_a, fixture_a, wrapper)
    action_complete, action_errors, action_details = check_action_evidence(base, service, alias_a, fixture_a, wrapper)
    errors = errors + action_errors
    evidence_complete = read_complete and action_complete
    # The payload is the exact suffix token. Drive's alias prefix is decoration
    # for the target already bound by native ID; it is not another intent field.
    action = "set_folder_name_suffix" if service == "drive" else "set_event_description"
    stored = {
        "service": service, "account_alias": ACCOUNT_ALIAS,
        "operation_id": "FIVE-LIVE-20261022-Q7K:" + service + ":" + case_alias,
        "target": fixture_a["id"], "action": action, "payload": {"suffix": "PAYLOAD-A"},
        "evidence": {"read_file": source.name, "read_sha256": hashlib.sha256(source_bytes).hexdigest(), "read_time_utc": wrapper.get("time"),
                     "browser_action_evidence": action_details,
                     "saved_field_checks_complete": read_complete, "action_evidence_complete": action_complete,
                     "evidence_complete": evidence_complete, "check_errors": errors},
    }
    second = dict(stored, target=fixture_second["id"], payload={"suffix": "PAYLOAD-B" if pair == "PAYLOAD" else "PAYLOAD-A"})
    path = base / "private" / f"intent-receipt-{service}-{policy}-{pair}.json"
    with new_record(path):
        record = {
            "kind": "receipt_prepare", "service": service, "policy": policy, "pair": pair,
            "prepared_at_utc": utc(), "rule_sha256": rule_hash, "helper_sha256": sha(Path(__file__)),
            "first_target_alias": alias_a, "second_target_alias": alias_second,
            "stored_envelope": stored, "stored_envelope_sha256": envelope_hash(stored),
            "second_envelope": second, "second_envelope_sha256": envelope_hash(second),
            "expected_second_browser_fields": field_value(service, fixture_second, alias_second, second["payload"]["suffix"]),
            "evidence_complete": evidence_complete, "evidence_errors": errors,
            "events": [], "status": "preparing", "second_browser_action_time": None,
            "account_mutations_by_helper": 0, "after_read": None,
        }
        event(record, "first_read_loaded", read_reference=source.name, read_time_utc=wrapper.get("time"), evidence_complete=evidence_complete)
        event(record, "second_request_prepared", envelope_sha256=record["second_envelope_sha256"])
        atomic_json(path, record)
        rule = "key_only" if policy == "K" else "bound"
        decision = receipt_decision(rule, stored, second, evidence_complete=evidence_complete)
        record["decision"] = decision
        event(record, "receipt_response", **decision)
        record["status"] = "decision_recorded_before_any_second_action"
        atomic_json(path, record)
    return {"record": str(path), "decision": decision, "evidence_complete": evidence_complete,
            "evidence_errors": errors, "second_browser_mutation_permitted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    cancel = commands.add_parser("cancel-prepare")
    cancel.add_argument("service", choices=["drive", "calendar"])
    cancel.add_argument("case", choices=["C1", "C2", "C3", "C4"])
    receipt = commands.add_parser("receipt-prepare")
    receipt.add_argument("service", choices=["drive", "calendar"])
    receipt.add_argument("policy", choices=["K", "B"])
    receipt.add_argument("pair", choices=["EXACT", "PAYLOAD", "TARGET"])
    args = parser.parse_args()
    if args.command == "cancel-prepare":
        result = cancel_prepare(HERE, args.service, args.case)
    else:
        result = receipt_prepare(HERE, args.service, args.policy, args.pair)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
