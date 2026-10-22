"""Synthetic helper checks only. Temporary files; no account calls or trials."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import datetime
import base64

import runtime_intent as runtime


def fixture(service, alias):
    native = "synthetic-" + service + "-" + alias
    if service == "drive":
        args = {"name": "LOCAL-SELF-CHECK " + alias + " BASE", "parent_folder": "synthetic-parent"}
        baseline = {"id": native, "title": args["name"], "mime_type": "application/vnd.google-apps.folder", "file_or_folder": "folder", "parent_ids": ["synthetic-parent"], "shared": False}
    else:
        args = {"title": "LOCAL-SELF-CHECK " + alias}
        baseline = {"id": native, "summary": args["title"], "status": "confirmed", "start": "2026-10-01T00:00:00", "end": "2026-10-02T00:00:00", "location": None, "transparency": "transparent", "visibility": "private", "hangout_link": None, "reminders": {"use_default": False, "overrides": []}, "recurrence": None, "recurring_event_id": None, "attendees": [], "organizer": {"is_self": True}, "description": "BASE\n\n"}
    return {"id": native, "url": "synthetic://" + native, "args": args, "baseline": baseline}


def main():
    checks = 0
    def require(value):
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(f"Synthetic check {checks} failed")
    with tempfile.TemporaryDirectory(prefix="intent-helper-check-") as temp:
        base = Path(temp)
        (base / "private").mkdir()
        shutil.copy(runtime.HERE / "live_intent.py", base / "live_intent.py")
        runtime.atomic_json(base / "execution_freeze.json", {"sha256": {"live_intent.py": runtime.sha(base / "live_intent.py")}})
        aliases = ["CANCEL-C" + str(i) for i in range(1, 5)] + [f"RECEIPT-{p}-{t}-{target}" for p in ["K", "B"] for t in ["EXACT", "PAYLOAD", "TARGET"] for target in (["A", "B"] if t == "TARGET" else ["A"])]
        manifest = {service + ":" + alias: fixture(service, alias) for service in ["drive", "calendar"] for alias in aliases}
        runtime.atomic_json(base / "private/manifest.json", manifest)
        for service in ["drive", "calendar"]:
            for case, expected in [("C1", "OLD"), ("C2", "none"), ("C3", "OLD"), ("C4", "NEW")]:
                output = runtime.cancel_prepare(base, service, case)
                require(output["expected_dispatch"] == expected)
                record = json.loads(Path(output["record"]).read_text())
                require(record["browser_action_time"] is None and record["browser_action_sent"] is None)
                require(record["state"] == {"generation": 1, "active": True})
                require([e["sequence"] for e in record["events"]] == list(range(1, len(record["events"]) + 1)))
                require([e["time_utc"] for e in record["events"]] == sorted(e["time_utc"] for e in record["events"]))
                before = Path(output["record"]).read_bytes()
                try:
                    runtime.cancel_prepare(base, service, case)
                    require(False)
                except FileExistsError:
                    require(Path(output["record"]).read_bytes() == before)
            for policy in ["K", "B"]:
                for pair in ["EXACT", "PAYLOAD", "TARGET"]:
                    alias = f"RECEIPT-{policy}-{pair}-A"
                    first = manifest[service + ":" + alias]
                    saved = copy.deepcopy(first["baseline"])
                    if service == "drive":
                        saved["title"] = runtime.field_value(service, first, alias, "PAYLOAD-A")["name"]
                    else:
                        saved["description"] = "PAYLOAD-A\n\n"
                    wrapper = {"time": runtime.utc(), "result": {"isError": False, "structuredContent": saved}}
                    start = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=4)
                    times = [(start + datetime.timedelta(seconds=i)).isoformat() for i in range(4)]
                    wrapper["time"] = times[3]
                    if service == "drive":
                        url = "https://drive.google.com/drive/folders/synthetic-parent"
                        values = {"rename_input_value": saved["title"], "active_parent_id": "synthetic-parent"}
                    else:
                        eid = base64.urlsafe_b64encode((first["id"] + " synthetic@example.invalid").encode()).decode().rstrip("=")
                        url = "https://calendar.google.com/calendar/u/0/r/eventedit/" + eid
                        values = {"description": "PAYLOAD-A", "all_day": True, "availability": "Free", "visibility": "Private"}
                    ui = {"time": times[0], "service": service, "alias": alias, "url": url, "observed_id": first["id"], "values": values, "source_file": "synthetic-raw-UI.json"}
                    runtime.atomic_json(base / "private/synthetic-raw-UI.json", {"synthetic_only": True, "url": url, "values": values})
                    ui_path = base / "private" / f"intent-ui-{service}-{alias}.json"
                    runtime.atomic_json(ui_path, ui)
                    label = f"first-{service}-{alias}"
                    runtime.atomic_json(base / "private" / f"dispatch-{label}.json", {"time": times[1], "label": label})
                    runtime.atomic_json(base / "private" / f"ui-{label}-sent.json", {"time": times[2], "role": "synthetic_postclick", "url": url, "state": "synthetic observation only"})
                    runtime.atomic_json(base / "private" / f"intent-first-{service}-{alias}.json", wrapper)
                    result = runtime.receipt_prepare(base, service, policy, pair)
                    expected = "success" if policy == "K" or pair == "EXACT" else "conflict"
                    require(result["decision"]["status"] == expected)
                    require(result["evidence_complete"])
                    require(result["second_browser_mutation_permitted"] is False)
                    record = json.loads(Path(result["record"]).read_text())
                    require(record["decision"]["dispatch"] is False)
                    require(record["second_envelope"]["payload"] == {"suffix": "PAYLOAD-B" if pair == "PAYLOAD" else "PAYLOAD-A"})
                    require(record["stored_envelope"]["payload"] == {"suffix": "PAYLOAD-A"})
                    if pair == "TARGET":
                        require(record["stored_envelope"]["target"] != record["second_envelope"]["target"])
                        require(record["decision"]["mismatched_fields"] == ([] if policy == "K" else ["target"]))
                        if service == "drive":
                            require(f"RECEIPT-{policy}-TARGET-B PAYLOAD-A" in record["expected_second_browser_fields"]["name"])
                    broken = copy.deepcopy(wrapper)
                    broken["result"]["structuredContent"]["id"] = "wrong-target"
                    require(runtime.check_first_read(service, alias, first, broken)[0] is False)
                    stale = copy.deepcopy(wrapper)
                    stale["time"] = "2000-01-01T00:00:00+00:00"
                    require(runtime.check_action_evidence(base, service, alias, first, stale)[0] is False)
                    bad_ui = copy.deepcopy(ui)
                    bad_ui["observed_id"] = "wrong-target"
                    runtime.atomic_json(ui_path, bad_ui)
                    require(runtime.check_action_evidence(base, service, alias, first, wrapper)[0] is False)
                    runtime.atomic_json(ui_path, ui)
                    source_path = base / "private/synthetic-raw-UI.json"
                    source_bytes = source_path.read_bytes()
                    source_path.unlink()
                    require(runtime.check_action_evidence(base, service, alias, first, wrapper)[0] is False)
                    source_path.write_bytes(source_bytes)
                    if service == "calendar":
                        broken = copy.deepcopy(wrapper)
                        broken["result"]["structuredContent"]["description"] = " PAYLOAD-A\n\n"
                        require(runtime.check_first_read(service, alias, first, broken)[0] is False)
                        bad_ui = copy.deepcopy(ui)
                        bad_ui["values"]["all_day"] = 1
                        runtime.atomic_json(ui_path, bad_ui)
                        require(runtime.check_action_evidence(base, service, alias, first, wrapper)[0] is False)
                        runtime.atomic_json(ui_path, ui)
        require(not list((base / "private").glob("*.lock")))
        require(not list((base / "private").glob(".*.json.*")))
    print(json.dumps({"status": "pass", "scope": "synthetic local helper checks only; no account calls or live trials", "checks": checks, "runtime_sha256": hashlib.sha256(Path(runtime.__file__).read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
