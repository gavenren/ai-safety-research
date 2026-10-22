"""Separate audit of retained gate/order evidence. No network or account calls.

This evaluator was written after reading the submitted code and results. It
does not import either submitted analyzer or its rule module. Raw evidence is
read only. Private identifiers are compared but are not written to the result.
"""
import argparse
import base64
import datetime
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(value):
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def event_id(url):
    parsed = urlparse(url)
    assert parsed.hostname in {"calendar.google.com", "www.google.com"}
    encoded = parse_qs(parsed.query).get("eid", [None])[0]
    encoded = encoded or parsed.path.split("/eventedit/", 1)[1].split("/", 1)[0]
    encoded = unquote(encoded)
    return base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode().split(" ", 1)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["gates", "order"])
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    begin = time.perf_counter()
    base = args.base.resolve(); private = base / "private"; package = base / args.kind
    evidence = read(package / "live_evidence.json"); result = read(package / "live_results.json")
    comparisons = 0
    def check(condition, message):
        nonlocal comparisons
        comparisons += 1
        if not condition:
            raise AssertionError(message)
    references = set()
    def check_refs(node):
        if isinstance(node, list):
            for value in node: check_refs(value)
        elif isinstance(node, dict):
            if "file" in node and "sha256" in node:
                name = node["file"]
                choices = [private/name, base/name, package/name]
                matches = [path for path in choices if path.is_file() and digest(path) == node["sha256"]]
                check(bool(matches), "Source hash mismatch: " + name)
                references.add(name)
            for value in node.values(): check_refs(value)
    check_refs(evidence)
    summaries = []
    if args.kind == "gates":
        setup = {x["alias"][-1]: x for x in read(private/"drive-setup.json") if x.get("alias") in {"GATE-A", "GATE-B"}}
        ids = {k: v["result"]["structuredContent"]["id"] for k, v in setup.items()}
        prefixes = {k: v["name"].removesuffix(" DONE") for k, v in setup.items()}
        parents = {v["result"]["structuredContent"]["parent_id"] for v in setup.values()}
        check(len(parents) == 1, "Shared fixture parent")
        parent = next(iter(parents))
        ax_dom_differences = []; late_points = []; total_dispatches = 0
        for case in evidence["cases"]:
            cid = case["case_id"]; raw_case = read(private/f"gate-case-{cid}.json")
            work = dict.fromkeys("AB", "DONE"); counter = 0; history = []
            unsafe = refused = guarded_count = 0
            start = None
            for point, raw_probe in zip(case["points"], raw_case, strict=True):
                n = point["n"]; req = point["request"]; history.append(req)
                action, op = req["action"], req["op"]
                state = {"flag": False, "count": 0, "active": [], "lifecycle": {}}
                if case["rule"] == "boolean":
                    state["flag"] = action == "C"; closed = state["flag"]
                elif case["rule"] == "nonnegative_count":
                    counter = max(0, counter + (1 if action == "C" else -1))
                    state["count"] = counter; closed = counter > 0
                elif case["rule"] == "active_ids":
                    last = {r["op"]: r["action"] for r in history}
                    state["active"] = sorted(k for k, v in last.items() if v == "C")
                    closed = bool(state["active"])
                else:
                    life = {}
                    for actor in sorted({r["op"] for r in history}):
                        actions = [r["action"] for r in history if r["op"] == actor]
                        if "C" in actions:
                            life[actor] = "completed" if "R" in actions[actions.index("C")+1:] else "active"
                    state["lifecycle"] = life; closed = "active" in life.values()
                check(point["local_gate_state"] == raw_probe["state"] == state, "Gate state " + cid)
                check(point["gate_closed"] == raw_probe["closed"] == closed, "Gate closed " + cid)
                decision = read(private/f"decision-{cid}-{n}.json")
                check(decision["state"] == state and decision["closed"] == closed, "Staged decision")
                check(decision["time"] == point["staged_decision_time"], "Staged timestamp")
                start = start or stamp(decision["time"])
                dispatch_path = private/f"dispatch-{cid}-{n}.json"
                if req["duplicate"]:
                    check(not dispatch_path.exists(), "Duplicate request must not write")
                else:
                    total_dispatches += 1
                    dispatch = read(dispatch_path)
                    before = work[op]; work[op] = "PENDING" if action == "C" else "DONE"
                    check(dispatch["alias"] == "GATE-"+op, "Dispatch alias")
                    check(dispatch["oldName"] == prefixes[op]+" "+before and dispatch["newName"] == prefixes[op]+" "+work[op], "Dispatch name")
                    check(stamp(decision["time"]) <= stamp(dispatch["time"]), "Decision before write")
                check(point["observed_work"] == raw_probe["work"] == work, "Observed work")
                read_times = []; guarded = []
                for public_read in point["saved_reads"]:
                    raw_ref = next(r for r in public_read["evidence"] if r["file"].startswith("gate-read-"))
                    raw = read(private/raw_ref["file"])
                    ui_ref = next(r for r in public_read["evidence"] if r["file"].startswith("ui-"))
                    ui = read(private/ui_ref["file"])
                    check(ui["role"] == raw["role"] == public_read["role"], "Read role")
                    check(urlparse(ui["url"]).path.rstrip("/").endswith("/folders/"+parent), "Parent URL")
                    check(stamp(ui["time"]) <= stamp(raw["time"]), "AX precedes DOM")
                    check(stamp(decision["time"]) <= stamp(raw["time"]) <= stamp(raw_probe["time"]), "Read event order")
                    differs = False
                    for actor in "AB":
                        observed = raw["rows"][actor]
                        check(observed["id"] == ids[actor], "Exact gate ID")
                        check(observed["text"].splitlines()[0] == prefixes[actor]+" "+work[actor], "Exact DOM name")
                        check(observed["work"] == work[actor], "DOM work token")
                        differs |= not any(re.search(r"\brow\b.* "+re.escape(prefixes[actor]+" "+work[actor])+r" Folder(?: |$)", line) for line in ui["state"].splitlines())
                    check(differs == public_read["earlier_AX_name_differs_from_later_DOM"], "AX/DOM sequence difference")
                    if differs: ax_dom_differences.append(f"{cid}:{n}")
                    read_times.append(stamp(raw["time"]))
                    if raw["role"] == "guarded_read": guarded.append(raw)
                check(bool(guarded) == (not closed) == point["guarded_read_verified"], "Actual guarded read")
                check(bool(guarded) == raw_probe["guarded_read_completed"], "Probe read claim")
                guarded_count += len(guarded)
                unsafe += bool(guarded) and "PENDING" in work.values()
                refused += closed and all(v == "DONE" for v in work.values())
                if point["reload_records"]:
                    reload_start = min(stamp(read(private/r["evidence"]["file"])["time"]) for r in point["reload_records"])
                    lag = round(min(read_times) - reload_start, 3)
                    check(lag == point["reload_to_first_verified_read_seconds"], "Read lag")
                    if lag > 30: late_points.append({"case": cid, "step": n, "seconds": lag})
                else:
                    check(req["duplicate"], "Only local duplicate has no reload")
            duration = round(stamp(raw_case[-1]["time"])-start, 3)
            check(duration == case["staged_start_to_final_probe_seconds"] and duration < 480, "Case duration")
            timing = not any(x["case"] == cid for x in late_points)
            check(timing == case["strict_stop_rule_eligible"], "Case timing eligibility")
            summaries.append({"case": cid, "guarded": guarded_count, "unsafe": unsafe, "unnecessary": refused, "final_closed": closed, "timing_eligible": timing, "metadata_eligible": timing and case["metadata"]["fresh_start"]})
        for boundary in evidence["metadata_boundaries"]:
            rows = read(private/boundary["evidence"]["file"])
            end = next(c for c in evidence["cases"] if c["case_id"] == boundary["ends_case"])
            next_case = next((c for c in evidence["cases"] if c["case_id"] == boundary["starts_case"]), None)
            for row in rows:
                actor = row["alias"][-1]; actual = row["result"]["structuredContent"]
                check(not row["result"]["isError"], "Metadata read successful")
                check(actual["id"] == ids[actor] and actual["title"] == prefixes[actor]+" DONE", "Metadata identity/name")
                check(actual["parent_ids"] == [parent] and actual["mime_type"] == "application/vnd.google-apps.folder" and actual["shared"] is False, "Metadata fixed fields")
                check(stamp(end["points"][-1]["probe_record_time"]) <= stamp(row["time"]), "Metadata after end")
                if next_case: check(stamp(row["time"]) <= stamp(next_case["points"][0]["staged_decision_time"]), "Metadata before next start")
        for key, total in [("verified_guarded_reads", sum(r["guarded"] for r in summaries)), ("unsafe_permitted_reads", sum(r["unsafe"] for r in summaries)), ("unnecessary_refusals", sum(r["unnecessary"] for r in summaries))]:
            check(result[key] == total, "Gate summary " + key)
        check(total_dispatches == result["scored_browser_renames"] == 32, "Rename count")
        check(sum(r["timing_eligible"] for r in summaries) == result["timing_eligible_cases"] == 7, "Timing subset")
        check(sum(r["metadata_eligible"] for r in summaries) == result["timing_and_fresh_metadata_eligible_cases"] == 6, "Metadata subset")
        strict = [r for r in summaries if r["metadata_eligible"]]
        extras = {"late_points": late_points, "earlier_AX_later_DOM_differences": ax_dom_differences,
                  "strict_subset": {"cases": len(strict), "unsafe": sum(r["unsafe"] for r in strict), "unnecessary": sum(r["unnecessary"] for r in strict), "final_closed": sum(r["final_closed"] for r in strict)}}
    else:
        manifest = read(private/"manifest.json")
        baselines = {r["alias"]: r for r in read(private/"order-fresh-baselines.json")}
        def clear(s, position): return s[:position]+"0"+s[position+1:]
        def complete_path(s, valid):
            if s == "000": return [s]
            for index in [1, 0, 2]:
                if s[index] == "1":
                    after = clear(s, index)
                    if after in valid:
                        tail = complete_path(after, valid)
                        if tail: return [s]+tail
            return None
        all_read_count = all_writes = 0
        for case in evidence["cases"]:
            cid = case["case_id"]; fixture = manifest["calendar:"+cid]; native = fixture["id"]
            valid = set(case["valid_states"])
            actual_path = []; read_times = []
            for point in case["points"]:
                raw = read(private/point["evidence"]["file"]); ui = read(private/point["full_UI_evidence"]["file"])
                title = re.fullmatch(r"FIVE-LIVE-20261022-Q7K "+re.escape(cid)+r" TEST-A([01])", raw["title"])
                location = re.fullmatch(r"TEST-B([01])", raw["location"])
                description = re.fullmatch(r"TEST-C([01])", raw["description"])
                check(bool(title and location and description), "Exact editor tokens")
                state = title[1]+location[1]+description[1]
                check(state == point["observed_state"], "Observed path state")
                check(event_id(raw["editor_url"]) == native == event_id(ui["url"]), "Exact Calendar URL identity")
                check(all(raw[k] is True for k in ["all_day", "free", "private"]), "DOM contract flags")
                check(all(token in ui["state"] for token in ["Description: All day, Value: 1", "Value: Free", "Value: Private"]), "Actual AX contract fields")
                check(stamp(ui["time"]) <= stamp(raw["time"]), "Editor observation order")
                actual_path.append(state); read_times.append(stamp(raw["time"]))
            if case["rule"] == "fixed":
                predicted = ["111"]; [predicted.append(clear(predicted[-1], i)) for i in [1,0,2]]
            elif case["rule"] == "complete": predicted = complete_path("111", valid)
            else:
                predicted = ["111"]
                while predicted[-1] != "000":
                    choices = [clear(predicted[-1], i) for i in [1,0,2] if predicted[-1][i] == "1" and clear(predicted[-1], i) in valid]
                    if not choices: break
                    predicted.append(choices[0])
            check(actual_path == predicted, "Independent path rule")
            for i, write in enumerate(case["writes"], 1):
                decision = read(private/f"order-decision-{cid}-{i}.json")
                sent = read(private/f"ui-{cid}-{i}-sent.json")
                changed = [j for j,(a,b) in enumerate(zip(actual_path[i-1],actual_path[i])) if a != b]
                check(len(changed) == 1 and actual_path[i-1][changed[0]] == "1" and actual_path[i][changed[0]] == "0", "One-way single field action")
                field = "abc"[changed[0]]
                expected = f"FIVE-LIVE-20261022-Q7K {cid} TEST-A0" if field == "a" else "TEST-"+field.upper()+"0"
                check(decision["alias"] == cid and decision["rule"] == case["rule"] and decision["field"] == field and decision["value"] == expected, "Actual field command")
                check(decision["before"] == actual_path[i-1] and decision["after"] == actual_path[i], "Decision path")
                check(read_times[i-1] <= stamp(decision["time"]) <= stamp(sent["time"]) <= read_times[i], "Action and read order")
                check(round(read_times[i]-stamp(sent["time"]),3) == write["post_save_UI_to_read_seconds"], "Saved UI/read interval")
            before = baselines[cid]["result"]["structuredContent"]; final_wrapper = read(private/f"order-final-{cid}.json"); after = final_wrapper["result"]["structuredContent"]
            for obj, state in [(before,"111"),(after,actual_path[-1])]:
                check(obj["id"] == native == event_id(obj["url"]), "Metadata identity")
                check(obj["summary"] == f"FIVE-LIVE-20261022-Q7K {cid} TEST-A{state[0]}" and obj["location"] == "TEST-B"+state[1] and obj["description"].rstrip("\r\n") == "TEST-C"+state[2], "Exact saved metadata tokens")
                check(obj["start"] == "2026-10-01T00:00:00" and obj["end"] == "2026-10-02T00:00:00", "Saved dates")
                check(obj["status"] == "confirmed" and obj["transparency"] == "transparent" and obj["visibility"] == "private", "Saved fixed states")
                check(obj["organizer"]["is_self"] is True and all(a["is_self"] is True for a in obj["attendees"]) and len(obj["attendees"]) == 1, "Self attendee only")
                check(obj["reminders"] == {"use_default":False,"overrides":[]} and obj["recurrence"] is None and obj["recurring_event_id"] is None and obj["hangout_link"] is None and obj["attachments"] is None and obj["event_type"] == "default", "Collateral contract")
            mutable = {"summary","location","description","display_title"}
            check({k:v for k,v in before.items() if k not in mutable} == {k:v for k,v in after.items() if k not in mutable}, "All other exposed fields unchanged")
            check(stamp(final_wrapper["time"]) >= stamp(read(private/f"ui-{cid}-{len(actual_path)-1}-sent.json")["time"]), "Final connector follows write")
            check(round(read_times[-1]-read_times[0],3) == case["baseline_to_last_read_seconds"] and read_times[-1]-read_times[0] < 480, "Case duration")
            summaries.append({"case":cid,"path":actual_path,"target":actual_path[-1]=="000","all_valid":all(s in valid for s in actual_path),"writes":len(case["writes"]),"reads":len(actual_path),"connector_before_last_DOM":stamp(final_wrapper["time"])<read_times[-1]})
            all_writes += len(case["writes"]); all_read_count += len(actual_path)
        check(all_writes == result["browser_field_changes"] == 16, "Write count")
        check(all_read_count == result["saved_editor_observations"] == 22, "Read count")
        check(sum(r["target"] for r in summaries) == result["target_reached_cases"] == 5, "Goal count")
        check(sum(r["target"] and r["all_valid"] for r in summaries) == result["valid_completion_cases"] == 4, "Valid goal count")
        stop = read(private/evidence["partial_stop"]["evidence"]["file"])
        check(evidence["partial_stop"]["rejected_next"] == ["001","100"], "Greedy rejected candidates")
        extras = {"full_metadata_baselines": "one pre-run batch", "no_extra_W_G_read_inferred": True,
                  "known_lost_placeholder": "W-F pre-baseline only, as disclosed by runner; overwritten content cannot be reconstructed from current files"}
    out = {"status":"pass","reviewed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "kind":args.kind,"comparisons":comparisons,"source_references_checked":len(references),
           "independent_method":"separate implementation written after source/results inspection; not blinded", "account_calls":0,
           "cases":summaries,"details":extras,"elapsed_wall_seconds":time.perf_counter()-begin,
           "evidence_sha256":digest(package/"live_evidence.json"),"results_sha256":digest(package/"live_results.json"),"audit_sha256":digest(Path(__file__))}
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ["status","kind","comparisons","source_references_checked"]}))


if __name__ == "__main__": main()
