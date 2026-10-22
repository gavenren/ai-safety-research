"""Check private cancellation evidence and write an alias-only public trace.

This script uses saved local files only. It makes no account or browser call.
The private UI files can contain unrelated account data and are not published.
"""
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRIVATE = ROOT / "private"


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.utcoffset() == dt.timedelta(0)
    return parsed


def calendar_id(url):
    parsed = urlparse(url)
    assert parsed.hostname in ("calendar.google.com", "www.google.com")
    value = parse_qs(parsed.query).get("eid", [None])[0]
    if value is None:
        value = parsed.path.split("/eventedit/", 1)[1].split("/", 1)[0]
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode().split(" ", 1)[0]


def main():
    manifest = load(PRIVATE / "manifest.json")
    initial_rows = load(PRIVATE / "baselines.json")
    baselines = {row["value"]["service"] + ":" + row["value"]["alias"]: row["value"]
                 for row in initial_rows if row["status"] == "fulfilled"}
    rule_freeze = load(ROOT / "execution_freeze.json")
    helper_freeze = load(ROOT / "runtime_intent_freeze.json")
    for name in ("plan.md", "amendment-01.md", "design-cancel-receipt.md", "live_intent.py"):
        assert sha(ROOT / name) == rule_freeze["sha256"][name]
    assert sha(ROOT / "runtime_intent.py") == helper_freeze["sha256"]["runtime_intent.py"]
    rows = []
    all_evidence = {"baselines.json": sha(PRIVATE / "baselines.json"), "manifest.json": sha(PRIVATE / "manifest.json")}
    expected_names = {
        "C1": ["initial_state", "initial_check", "cancel_acknowledged_locally", "restart", "dispatch_decision"],
        "C2": ["initial_state", "initial_check", "cancel_acknowledged_locally", "restart", "final_check", "dispatch_decision"],
        "C3": ["initial_state", "final_check", "cancel_acknowledged_locally", "restart", "dispatch_decision"],
        "C4": ["initial_state", "cancel_acknowledged_locally", "restart", "final_check", "dispatch_decision"],
    }
    expected_end = {"C1": "OLD", "C2": "BASE", "C3": "OLD", "C4": "NEW"}
    expected_dispatches = set()
    for service in ("drive", "calendar"):
        for case in ("C1", "C2", "C3", "C4"):
            alias = "CANCEL-" + case
            key = service + ":" + alias
            fixture = manifest[key]
            base_wrapper = baselines[key]
            baseline = base_wrapper["result"]["structuredContent"]
            assert baseline == fixture["baseline"]
            files = {}

            def private(name):
                path = PRIVATE / name
                files[name] = sha(path)
                return load(path)

            intent = private(f"intent-cancel-{service}-{case}.json")
            after = private(f"cancel-after-{service}-{case}.json")
            assert not after["result"].get("isError")
            actual = after["result"]["structuredContent"]
            assert actual["id"] == baseline["id"] == fixture["id"] == intent["native_target"]
            assert intent["target_alias"] == alias and intent["case"] == case and intent["service"] == service
            assert intent["rule_sha256"] == rule_freeze["sha256"]["live_intent.py"]
            assert intent["helper_sha256"] == helper_freeze["sha256"]["runtime_intent.py"]
            assert intent["browser_action_sent"] is None and intent["saved_state"] is None
            events = intent["events"]
            assert [e["event"] for e in events] == expected_names[case]
            assert [e["sequence"] for e in events] == list(range(1, len(events) + 1))
            assert [stamp(e["time_utc"]) for e in events] == sorted(stamp(e["time_utc"]) for e in events)
            assert stamp(base_wrapper["ended"]) < stamp(intent["prepared_at_utc"])
            assert stamp(rule_freeze["timestamp_utc"]) < stamp(intent["prepared_at_utc"])
            assert intent["state"] == {"active": True, "generation": 1}
            for event in events:
                if event["event"] in ("initial_check", "final_check"):
                    state = event["observed_state"]
                    assert event["allow"] == (state["active"] is True and event["command_generation"] == state["generation"])
            retired = next(e for e in events if e["event"] == "cancel_acknowledged_locally")
            assert retired["retired_generation"] == 0 and retired["state"] == {"active": False, "generation": 0}
            assert next(e for e in events if e["event"] == "restart")["state"] == {"active": True, "generation": 1}
            assert intent["decision"]["allow"] is (case != "C2")
            assert intent["command_generation"] == (1 if case == "C4" else 0)
            assert intent["expected_dispatch"] == ("none" if case == "C2" else expected_end[case])
            assert stamp(after["time"]) > stamp(events[-1]["time_utc"])
            dispatch_at = None
            before_at = None
            if case == "C2":
                assert not (PRIVATE / f"dispatch-cancel-{service}-{case}.json").exists()
                ui = private(f"ui-cancel-{service}-{case}-blocked-read.json")
                assert stamp(ui["time"]) > stamp(events[-1]["time_utc"])
            else:
                dispatch_name = f"dispatch-cancel-{service}-{case}.json"
                expected_dispatches.add(dispatch_name)
                dispatch = private(dispatch_name)
                before = private(f"ui-cancel-{service}-{case}-before.json")
                sent = private(f"ui-cancel-{service}-{case}-sent.json")
                ui = private(f"ui-cancel-{service}-{case}-filled.json") if service == "calendar" else sent
                dispatch_at = dispatch["time"]
                before_at = before["time"]
                assert stamp(events[-1]["time_utc"]) < stamp(before_at) <= stamp(dispatch_at) <= stamp(sent["time"]) <= stamp(after["time"])
                assert dispatch["alias"] == alias
                if service == "drive":
                    assert dispatch["action"] == "rename"
                    assert dispatch["oldName"] == baseline["title"]
                    assert dispatch["newName"] == actual["title"]
                    assert '"' + baseline["title"] + '" renamed to "' + actual["title"] + '"' in sent["state"]
                    private(f"ui-cancel-{service}-{case}-menu.json")
                    private(f"ui-cancel-{service}-{case}-edit.json")
                    private(f"ui-cancel-{service}-{case}-reload-initial.json")
                else:
                    assert dispatch["from"] == "BASE" and dispatch["to"] == expected_end[case]
                    assert dispatch["field"] == "description"
                    assert calendar_id(dispatch["url"]) == fixture["id"]
                    assert "Description: Description, Value: BASE," in before["state"]
            if service == "drive":
                checked = [key for key in baseline if key not in ("title", "modified_time")]
                expected_full = fixture["args"]["name"][:-len("BASE")] + expected_end[case]
                assert baseline["title"] == fixture["args"]["name"]
                assert actual["title"] == expected_full
                parent = fixture["args"]["parent_folder"]
                assert urlparse(ui["url"]).hostname == "drive.google.com"
                assert urlparse(ui["url"]).path.rstrip("/").endswith("/folders/" + parent)
                assert expected_full + " Folder" in ui["state"]
                ui_gates = {"active_parent_and_named_row": True, "native_identity_confirmed_by_connector": True}
            else:
                checked = [key for key in baseline if key != "description"]
                assert baseline["description"].rstrip("\r\n") == "BASE"
                assert type(actual["description"]) is str and actual["description"].rstrip("\r\n") == expected_end[case]
                assert calendar_id(ui["url"]) == fixture["id"]
                markers = ["Description: All day, Value: 1", "Value: Free", "Value: Private", "Value: Does not repeat", "Description: Description, Value: " + expected_end[case] + ","]
                assert all(marker in ui["state"] for marker in markers)
                ui_gates = {"event_url_identity": True, "all_day": True, "free": True, "private": True, "no_recurrence": True, "expected_description_in_editor": True}
            assert all(key in actual and actual[key] == baseline[key] for key in checked)
            assert set(actual) == set(baseline)
            final_at = max(stamp(after["time"]), stamp(ui["time"]))
            duration = (final_at - stamp(intent["prepared_at_utc"])).total_seconds()
            assert 0 < duration <= 480
            row = {
                "service": service, "case": case, "target_alias": alias,
                "initial_field": "BASE", "expected_final_field": expected_end[case],
                "observed_final_field": expected_end[case], "command_generation": intent["command_generation"],
                "prepared_at_utc": intent["prepared_at_utc"], "events": events,
                "decision": intent["decision"], "dispatch_at_utc": dispatch_at,
                "before_ui_at_utc": before_at, "scored_ui_at_utc": ui["time"],
                "connector_read_recorded_at_utc": after["time"],
                "logged_browser_mutations": int(case != "C2"),
                "native_target_matches": True, "collateral_fields_checked": checked,
                "collateral_fields_equal": True, "ui_gates": ui_gates,
                "different_connector_fields": sorted(key for key in baseline if baseline[key] != actual[key]),
                "prepare_to_last_observation_seconds": duration,
                "helper_freeze_precedes_preparation": stamp(helper_freeze["frozen_at_utc"]) < stamp(intent["prepared_at_utc"]),
                "rule_freeze_precedes_preparation": True,
                "raw_evidence_sha256": files,
                "evidence_status": "complete_for_declared_scope",
            }
            rows.append(row)
            all_evidence.update(files)
    assert {path.name for path in PRIVATE.glob("dispatch-cancel-*.json")} == expected_dispatches
    public = {"schema": 1, "kind": "eight controlled production browser cases", "date": "2026-10-22", "cases": rows,
              "plan_freeze_utc": rule_freeze["timestamp_utc"], "runtime_helper_freeze_utc": helper_freeze["frozen_at_utc"],
              "private_evidence_sha256": all_evidence,
              "limitations": ["local cancellation only", "no atomic receiver fence", "no provider-wide cancellation proof", "no hidden-write or duplicate-effect count", "connector fields and scoped UI only"]}
    text = json.dumps(public, indent=2, sort_keys=True) + "\n"
    for entry in manifest.values():
        assert entry["id"] not in text and entry["url"] not in text
    assert "@" not in text and "https://" not in text
    (HERE / "live_trace.json").write_text(text)
    print(json.dumps({"status": "pass", "cases": len(rows), "recorded_mutations": sum(r["logged_browser_mutations"] for r in rows), "late_helper_freeze_cases": [r["service"] + ":" + r["case"] for r in rows if not r["helper_freeze_precedes_preparation"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
