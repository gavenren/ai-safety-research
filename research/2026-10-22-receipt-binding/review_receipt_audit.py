"""Separate raw-evidence audit. No account calls and no author-code imports.

Requires the parent's private evidence. The reviewer read the author's code
before writing this independent comparison. It is not a blinded evaluation.
"""
import base64
import datetime
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRIVATE = ROOT / "private"


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chash(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def timestamp(value):
    value = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert value.utcoffset() == datetime.timedelta(0)
    return value


def native_event_id(url):
    parsed = urlparse(url)
    assert parsed.hostname in ("calendar.google.com", "www.google.com")
    token = parse_qs(parsed.query).get("eid", [None])[0]
    if token is None:
        token = parsed.path.split("/eventedit/", 1)[1]
    return base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)).decode().split(" ", 1)[0]


def main():
    checks = []

    def check(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    manifest = load(PRIVATE / "manifest.json")
    baselines = {row["value"]["service"] + ":" + row["value"]["alias"]: row["value"]
                 for row in load(PRIVATE / "baselines.json") if row["status"] == "fulfilled"}
    public = load(HERE / "live_evidence.json")
    results = load(HERE / "live_results.json")
    freeze = load(ROOT / "runtime_intent_freeze.json")
    for name, value in freeze["sha256"].items():
        check(sha(ROOT / name) == value, "runtime freeze " + name)
    check(len(public["cases"]) == 12, "12 public cases")
    observed = []
    used_paths = {PRIVATE / "manifest.json", PRIVATE / "baselines.json"}
    expected_dispatches = set()
    for service in ("drive", "calendar"):
        for policy in ("K", "B"):
            for pair in ("EXACT", "PAYLOAD", "TARGET"):
                case = service + "-" + policy + "-" + pair
                alias = "RECEIPT-" + policy + "-" + pair + "-A"
                fixture = manifest[service + ":" + alias]
                data = next(row for row in public["cases"] if row["case_id"] == case)

                def read(name):
                    path = PRIVATE / name
                    used_paths.add(path)
                    return load(path)

                raw = read(f"intent-receipt-{service}-{policy}-{pair}.json")
                first = read(f"intent-first-{service}-{alias}.json")
                final = read(f"receipt-after-{service}-{alias}.json")
                ui = read(f"intent-ui-{service}-{alias}.json")
                source = read(ui["source_file"])
                dispatch_name = f"dispatch-first-{service}-{alias}.json"
                expected_dispatches.add(dispatch_name)
                dispatch = read(dispatch_name)
                sent = read(f"ui-first-{service}-{alias}-sent.json")
                baseline = baselines[service + ":" + alias]
                b = baseline["result"]["structuredContent"]
                x = first["result"]["structuredContent"]
                y = final["result"]["structuredContent"]
                check(not first["result"].get("isError") and not final["result"].get("isError"), case + " no read error")
                check(b == fixture["baseline"] and b["id"] == x["id"] == y["id"] == fixture["id"], case + " native identities")
                check(x == y, case + " all first/final exposed fields equal")
                altered = {name for name in set(b) | set(x) if b.get(name) != x.get(name)}
                if service == "drive":
                    expected_name = fixture["args"]["name"][:-4] + "PAYLOAD-A"
                    check(x["title"] == expected_name, case + " exact first name")
                    check(altered <= {"title", "modified_time"}, case + " unchanged collateral fields")
                    check(x["parent_ids"] == [fixture["args"]["parent_folder"]] and x["shared"] is False, case + " parent and sharing")
                    check(x["mime_type"] == "application/vnd.google-apps.folder" and x["file_or_folder"] == "folder", case + " folder type")
                    check(source["row"]["id"] == ui["observed_id"] == fixture["id"], case + " observed UI identity")
                    check(source["rename_input_value"] == ui["values"]["rename_input_value"] == expected_name, case + " exact UI name")
                    check(dispatch["newName"] == expected_name and dispatch["oldName"] == b["title"] and dispatch["action"] == "rename", case + " dispatch fields")
                else:
                    check(x["description"].rstrip("\r\n") == "PAYLOAD-A", case + " exact first description")
                    check(altered == {"description"}, case + " unchanged collateral fields")
                    check(ui["values"] == {"all_day": True, "availability": "Free", "description": "PAYLOAD-A", "visibility": "Private"} and type(ui["values"]["all_day"]) is bool, case + " observed UI fields")
                    check(ui["observed_id"] == native_event_id(ui["url"]) == native_event_id(source["url"]) == fixture["id"], case + " observed UI identity")
                    check(all(marker in source["state"] for marker in ("Description: All day, Value: 1", "Value: Free", "Value: Private", "Description: Description, Value: PAYLOAD-A,")), case + " raw UI field support")
                    check(dispatch["from"] == "BASE" and dispatch["to"] == "PAYLOAD-A" and dispatch["field"] == "description", case + " dispatch fields")
                stored, new = raw["stored_envelope"], raw["second_envelope"]
                mutable = [key for key in ("service", "account_alias", "operation_id", "target", "action", "payload") if stored[key] != new[key]]
                wanted_mutable = [] if pair == "EXACT" else ["target" if pair == "TARGET" else "payload"]
                check(mutable == wanted_mutable, case + " immutable fields")
                check(stored["target"] == fixture["id"] and stored["payload"] == {"suffix": "PAYLOAD-A"}, case + " stored intent")
                target_alias = alias[:-1] + "B" if pair == "TARGET" else alias
                wanted = "PAYLOAD-B" if pair == "PAYLOAD" else "PAYLOAD-A"
                check(new["target"] == manifest[service + ":" + target_alias]["id"] and new["payload"] == {"suffix": wanted}, case + " requested intent")
                check(chash(stored) == raw["stored_envelope_sha256"] and chash(new) == raw["second_envelope_sha256"], case + " envelope hashes")
                check(raw["helper_sha256"] == sha(ROOT / "runtime_intent.py") and raw["rule_sha256"] == sha(ROOT / "live_intent.py"), case + " actual helper and rule bytes")
                check(raw["evidence_complete"] is True and not raw["evidence_errors"], case + " complete recorded gate")
                ev = stored["evidence"]
                check(ev["read_sha256"] == sha(PRIVATE / f"intent-first-{service}-{alias}.json"), case + " first read hash")
                for reference in ev["browser_action_evidence"]["references"].values():
                    check(sha(PRIVATE / reference["file"]) == reference["sha256"], case + " action reference " + reference["file"])
                check(data["decision"] == raw["decision"], case + " exact recorded decision")
                expected_status = "success" if policy == "K" or pair == "EXACT" else "conflict"
                check(raw["decision"]["status"] == expected_status and raw["decision"]["dispatch"] is False, case + " policy and no dispatch")
                check(raw["second_browser_action_time"] is None and raw["account_mutations_by_helper"] == 0, case + " no helper second action")
                check([e["event"] for e in raw["events"]] == ["first_read_loaded", "second_request_prepared", "receipt_response"], case + " online event order")
                chronology = [ui["time"], dispatch["time"], sent["time"], first["time"], raw["prepared_at_utc"], *[e["time_utc"] for e in raw["events"]], final["time"]]
                check([timestamp(t) for t in chronology] == sorted(timestamp(t) for t in chronology), case + " action/read/response chronology")
                check(timestamp(freeze["frozen_at_utc"]) < timestamp(ui["time"]), case + " helper freeze before first action")
                check((timestamp(final["time"]) - timestamp(ui["time"])).total_seconds() <= 480, case + " case under eight minutes")
                observed_value = "PAYLOAD-A"
                if pair == "TARGET":
                    bf = manifest[service + ":" + target_alias]
                    bb = baselines[service + ":" + target_alias]["result"]["structuredContent"]
                    br = read(f"intent-first-{service}-{target_alias}.json")
                    ba = read(f"receipt-after-{service}-{target_alias}.json")
                    check(bb == br["result"]["structuredContent"] == ba["result"]["structuredContent"] == bf["baseline"], case + " B never changes in exposed fields")
                    check(bb["id"] == bf["id"] and bf["id"] != fixture["id"], case + " distinct B identity")
                    check(timestamp(br["time"]) <= timestamp(raw["prepared_at_utc"]) <= timestamp(ba["time"]), case + " B audit order")
                    observed_value = "BASE"
                false_claim = expected_status == "success" and observed_value != wanted
                row = next(row for row in results["outcomes"] if row["case_id"] == case)
                expected_row = {"case_id": case, "service": service, "policy": policy, "pair": pair,
                                "decision": expected_status, "requested_target": "B" if pair == "TARGET" else "A",
                                "requested_value": wanted, "observed_value": observed_value,
                                "requested_state_matches": observed_value == wanted, "false_success": false_claim,
                                "contract_matches": (pair == "EXACT" or policy == "B"),
                                "timing_check_known": case != "drive-K-EXACT"}
                check(row == expected_row, case + " all score fields")
                observed.append(expected_row)
                for reference in data["evidence"]:
                    check(sha(PRIVATE / reference["file"]) == reference["sha256"], case + " public evidence reference")
                for role, resource in data["resource_checks"].items():
                    for reference in resource["evidence"]:
                        check(sha(PRIVATE / reference["file"]) == reference["sha256"], case + " resource reference " + role)
    check({p.name for p in PRIVATE.glob("dispatch-first-*-RECEIPT-*.json")} == expected_dispatches, "exact 12 logged first dispatches")
    check(not list(PRIVATE.glob("dispatch-second-*-RECEIPT-*.json")), "no logged second receipt dispatch")
    original = PRIVATE / "receipt-interruption-read.json"
    copied = PRIVATE / "intent-first-drive-RECEIPT-K-EXACT-A.json"
    check(original.read_bytes() == copied.read_bytes(), "timeout first read is a byte copy, not a second observation")
    check(sum(row["false_success"] for row in observed) == results["total_false_success"] == 4, "four false claims")
    check(sum(row["false_success"] for row in observed if row["timing_check_known"]) == 4, "four false claims in timing-known subset")
    sensitive = set()
    for value in manifest.values():
        sensitive.update((value["id"], value["url"]))
        sensitive.update(value["baseline"].get("parent_ids", []))
    for path in used_paths:
        sensitive.update(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", path.read_text()))
    public_paths = [p for p in HERE.iterdir() if p.is_file()]
    hits = [p.name for p in public_paths for value in sensitive if value and value in p.read_text()]
    check(not hits, "no exact tested private values in public files")
    result = {"status": "pass", "checks_passed": len(checks), "checks": checks,
              "cases_checked": len(observed), "false_claims": 4, "logged_first_dispatches": 12,
              "logged_second_dispatches": 0, "timeout_copied_read_counted_once": True,
              "public_files_scanned": len(public_paths), "exact_private_values_checked": len(sensitive), "private_matches": 0,
              "account_calls": 0, "human_review": False, "reviewer_read_author_code_before_audit": True,
              "evidence_sha256": sha(HERE / "live_evidence.json"), "result_sha256": sha(HERE / "live_results.json"),
              "review_code_sha256": sha(Path(__file__))}
    (HERE / "review_receipt_audit.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "checks_passed", "cases_checked", "false_claims", "logged_second_dispatches", "private_matches")}, sort_keys=True))


if __name__ == "__main__":
    main()
