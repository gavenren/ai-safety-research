#!/usr/bin/env python3
"""Reproduce the public saved-data analysis. No service or browser is accessed."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import controller as c

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def check(condition, text):
    if not condition:
        raise AssertionError(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    source_names = ["branches.json", "controller.py", "plan.md", "controller_freeze.json", "expected_controls.json"]
    for site in ("drive", "calendar"):
        source_names.extend(f"{site}_{name}.json" for name in ("observations", "record_ledger", "receipts", "cleanup", "evidence_index"))
    source_hashes = {name: c.file_digest(ROOT / name) for name in source_names}
    frozen = read("controller_freeze.json")
    for name in ("controller.py", "plan.md"):
        check(source_hashes[name] == frozen["files"][name], f"Frozen file changed: {name}")
    branches = read("branches.json")["branches"]
    check(len(branches) == 48, "Expected 48 paired decisions")
    check(len({b["branch"] for b in branches}) == 48, "Duplicate branch")
    ledgers = {site: read(f"{site}_record_ledger.json") for site in ("drive", "calendar")}
    ledger = {r["alias"]: r for rows in ledgers.values() for r in rows}
    check(len(ledger) == 34, "Record alias count differs")
    receipts = {r["fixture"]: r for site in ("drive", "calendar") for r in read(f"{site}_receipts.json")}
    check(len(receipts) == 8, "Expected eight shared fixtures")
    obs = {site: read(f"{site}_observations.json")["observations"] for site in ("drive", "calendar")}
    indexes = {site: {r["file"]: r for r in read(f"{site}_evidence_index.json")["private_evidence"]} for site in ("drive", "calendar")}
    hash_sets = {site: {r["sha256"] for r in index.values()} for site, index in indexes.items()}
    cal_by_file = {r["evidence_file"]: r for r in obs["calendar"]}
    drive_by_file = {}
    for row in obs["drive"]:
        drive_by_file.setdefault(row["evidence_file"], []).append(row)
    for site in obs:
        for row in obs[site]:
            check(row["evidence_sha256"] == indexes[site][row["evidence_file"]]["sha256"], "Observation hash mismatch")
            check(not row["tool_error"], "Unresolved tool error in public observations")

    record_creation_times = {}
    record_read_times = {}
    precleanup_checks = 0
    for alias, record in ledger.items():
        site = alias.split("-", 1)[0]
        check(record["create_evidence_file"] in indexes[site], "Missing create evidence index")
        check(record["readback_evidence_file"] in indexes[site], "Missing saved readback index")
        if site == "calendar":
            create = cal_by_file[record["create_evidence_file"]]
            saved = cal_by_file[record["readback_evidence_file"]]
            check(create["returned_alias"] == alias and saved["returned_alias"] == alias, "Calendar stable identity mismatch")
            check(saved["title_matches_alias"], "Calendar title mismatch")
            fields = saved["saved_fields"]
            check(fields["start"] == "2026-11-02T12:00:00-05:00" and fields["end"] == "2026-11-02T12:05:00-05:00", "Calendar time mismatch")
            check(fields["visibility"] == "private" and fields["transparency"] == "transparent", "Calendar private/free mismatch")
            check(fields["attendees"] == [] and fields["reminders"] == {"use_default": False, "overrides": []}, "Calendar attendee or reminder mismatch")
            check(not fields["recurrence"] and not fields["hangout_link"] and fields["status"] == "confirmed", "Calendar saved-state mismatch")
            record_creation_times[alias] = create["started_utc"]
            record_read_times[alias] = saved["ended_utc"]
            final_reads = [r for r in obs[site] if "-precleanup-" in r["evidence_file"] and r.get("returned_alias") == alias]
            check(len(final_reads) == 1 and final_reads[0]["saved_fields"] == saved["saved_fields"] and final_reads[0]["title_matches_alias"], "Calendar fields changed before cleanup")
        else:
            saved = drive_by_file[record["readback_evidence_file"]][0]
            matches = [r for r in saved["records"] if r["record_alias"] == alias]
            check(len(matches) == 1, "Drive stable identity missing")
            fields = matches[0]
            check(fields["exact_known_id"] and fields["title_matches_expected"] and fields["in_test_parent"], "Drive identity, title, or parent mismatch")
            check(fields["mime_type"] == "application/vnd.google-apps.folder" and fields["shared"] is False, "Drive folder or sharing mismatch")
            record_creation_times[alias] = fields["created_time"]
            record_read_times[alias] = saved["observed_at"]
            final_reads = [r for packet in drive_by_file["precleanup_exact_reads.json"] for r in packet["records"] if r["record_alias"] == alias]
            check(len(final_reads) == 1 and final_reads[0] == fields, "Drive fields changed before cleanup")
        check(c.utc_time(record_creation_times[alias]) > c.utc_time(frozen["frozen_at_utc"]), "Record predates frozen live plan")
        precleanup_checks += 1
    drive_scope = drive_by_file["precleanup_scope.json"][0]
    check({r["record_alias"] for r in drive_scope["records"]} == {r["alias"] for r in ledgers["drive"]}, "Drive final scope differs from known IDs")
    cal_scope = cal_by_file["106-scope-precleanup.json"]
    check(set(cal_scope["returned_aliases"]) == {r["alias"] for r in ledgers["calendar"]} and not cal_scope["next_page_token"], "Calendar final scope differs from known IDs")

    for fixture, pair in receipts.items():
        c.validate_receipts(pair)
        for label in ("P", "T"):
            check(all(h in hash_sets[pair["site"]] for h in pair[label]["evidence_sha256"]), "Receipt evidence hash missing")
        for alias in pair["P"]["records"]:
            check(c.utc_time(record_creation_times[alias]) <= c.utc_time(pair["P"]["captured_at"]), "P record was created after P")
        for alias in set(pair["T"]["records"]) - set(pair["P"]["records"]):
            check(c.utc_time(record_creation_times[alias]) > c.utc_time(pair["P"]["captured_at"]), "Extra A predates P")
        check(all(ledger[a]["role"] == "A" for a in pair["T"]["records"]), "Receipt contains a non-A record")

    rows = []
    comparisons = 0
    before_A_checks = 0
    refused_absence_checks = 0
    for branch in branches:
        pair = branch["receipts"]
        site, case, rule = pair["site"], pair["case"], branch["rule"]
        check(pair == receipts[pair["fixture"]], "Branch does not use the saved shared receipt pair")
        check(branch["status"] == "completed" and branch["integration_pass"], "Incomplete or failed branch")
        check(branch["receipt_file_sha256"] in hash_sets[site], "Private receipt file hash missing")
        prepared = c.prepare_value(pair, rule, branch["intended_name"], branch["prepared_at"], source_hashes["controller.py"], source_hashes["plan.md"])
        prepared["receipt_file_sha256"] = branch["receipt_file_sha256"]
        replay = c.finish_value(prepared, branch["action_evidence"], branch["finished_at"])
        check(replay == branch, "Full saved branch replay differs")
        comparisons += 2 * len(branch["trace"])
        check(all(h in hash_sets[site] for h in branch["action_evidence"]["evidence_sha256"]), "Action evidence hash missing")
        if site == "drive":
            before = drive_by_file[f"{case}-{rule}-before.json"][0]
            before_aliases = {r["record_alias"] for r in before["records"]}
            check(before_aliases == set(pair["T"]["records"]), "Drive A guard set differs")
            check(c.utc_time(before["observed_at"]) <= c.utc_time(branch["prepared_at"]), "Drive A check did not precede decision")
            check(all(r["title_matches_expected"] and r["in_test_parent"] for r in before["records"]), "Drive A guard fields differ")
        else:
            before = [r for r in obs[site] if f"-A-before-{branch['branch']}-" in r["evidence_file"]]
            check({r["returned_alias"] for r in before} == set(pair["T"]["records"]), "Calendar A guard set differs")
            check(all(c.utc_time(r["ended_utc"]) <= c.utc_time(branch["prepared_at"]) and r["title_matches_alias"] and r["saved_fields"]["status"] == "confirmed" for r in before), "Calendar A guard time or fields differ")
        before_A_checks += 1
        if branch["decision"]["accepted"]:
            alias = branch["b_alias"]
            check(alias in ledger and ledger[alias]["role"] == "B" and ledger[alias]["case"] == case and ledger[alias]["rule"] == rule, "B record attribution mismatch")
            check(c.utc_time(branch["prepared_at"]) < c.utc_time(record_creation_times[alias]), "B creation did not follow decision")
            check(c.utc_time(record_read_times[alias]) <= c.utc_time(branch["action_evidence"]["observed_at"]) <= c.utc_time(branch["finished_at"]), "B saved-state timing differs")
        else:
            check(not any(r["case"] == case and r["rule"] == rule and r["role"] == "B" for r in ledgers[site]), "Refused branch has a B record")
            action_hashes = set(branch["action_evidence"]["evidence_sha256"])
            absence = [r for r in obs[site] if r["evidence_sha256"] in action_hashes]
            check(absence, "Refusal absence evidence missing")
            if site == "drive":
                check(all(r.get("query_returned_count") == 0 for r in absence), "Drive refusal query is not empty")
            else:
                check(all(r.get("returned_aliases") == [] and not r.get("next_page_token") for r in absence), "Calendar refusal query is not empty")
            refused_absence_checks += 1
        row = {"site": site, "case": case, "rule": rule, "accepted": int(branch["decision"]["accepted"]), "actual_B": branch["actual_b_count"], "A_count": pair["T"]["value"], **branch["scores"], "integration_pass": int(branch["integration_pass"])}
        rows.append(row)

    cleanup_counts = {}
    for site in ("drive", "calendar"):
        cleanup = read(f"{site}_cleanup.json")
        check({r["alias"] for r in cleanup["records"]} == {r["alias"] for r in ledgers[site]}, "Cleanup aliases differ")
        check(cleanup["active_marker_count"] == 0 and cleanup["permanent_deletion"] is False, "Cleanup scope failed")
        if site == "drive":
            check(cleanup["parent"]["trash_breadcrumb_verified"] and cleanup["exact_child_breadcrumbs_verified"] == 17, "Drive cleanup evidence incomplete")
            check(all(r["exact_id_location_opened"] and r["breadcrumb_has_trash_parent_and_child"] for r in cleanup["records"]), "Drive child cleanup evidence incomplete")
            check(cleanup["connector_trashed_boolean_observed"] is False, "Drive evidence method overstated")
            check(all(r["evidence_sha256"] == indexes[site][r["evidence_file"]]["sha256"] for r in cleanup["records"]), "Drive cleanup evidence hash mismatch")
        else:
            check(cleanup["exact_records_cancelled"] == 17 and all(r["status"] == "cancelled" and r["exact_id_match"] for r in cleanup["records"]), "Calendar exact cleanup failed")
            check(all(r["readback_evidence_sha256"] == indexes[site][r["readback_evidence_file"]]["sha256"] for r in cleanup["records"]), "Calendar cleanup evidence hash mismatch")
        cleanup_counts[site] = len(cleanup["records"])

    summary = []
    for site in ("drive", "calendar", "both"):
        for rule in c.RULES:
            subset = [r for r in rows if r["rule"] == rule and (site == "both" or r["site"] == site)]
            summary.append({"site": site, "rule": rule, "decisions": len(subset), "B_saved": sum(r["actual_B"] for r in subset), "scoped_excess_cases": sum(r["scoped_excess"] > 0 for r in subset), "scoped_excess_units": sum(r["scoped_excess"] for r in subset), "final_overcounts": sum(r["final_booking_error"] > 0 for r in subset), "final_undercounts": sum(r["final_booking_error"] < 0 for r in subset), "feasible_refusals_after_T": sum(r["feasible_refusal_after_T"] for r in subset)})
    expected = read("expected_controls.json")
    for row in summary:
        scale = 2 if row["site"] == "both" else 1
        control = expected["per_site"][row["rule"]]
        for actual, planned in (("B_saved", "B"), ("scoped_excess_cases", "excess_cases"), ("final_overcounts", "overcounts"), ("final_undercounts", "undercounts"), ("feasible_refusals_after_T", "feasible_refusals_after_T")):
            check(row[actual] == scale * control[planned], "Observed control differs from the prior calculation")
    for site in ("drive", "calendar"):
        for case in c.CASES:
            selected = [r for r in rows if r["site"] == site and r["case"] == case and r["rule"] in ("HighWaterHeld", "TerminalOnly")]
            check(len(selected) == 2 and selected[0]["accepted"] == selected[1]["accepted"], "Complete rule decisions differ")
            check(all(r["final_booking_error"] == 0 and r["scoped_excess"] == 0 for r in selected), "Complete rule control failed")
    totals = {"paired_decisions": len(rows), "shared_fixtures": len(receipts), "A_records": sum(r["role"] == "A" for r in ledger.values()), "B_records": sum(r["role"] == "B" for r in ledger.values()), "total_records": len(ledger), "scoped_excess_cases": sum(r["scoped_excess"] > 0 for r in rows), "final_overcounts": sum(r["final_booking_error"] > 0 for r in rows), "final_undercounts": sum(r["final_booking_error"] < 0 for r in rows), "feasible_refusals_after_T": sum(r["feasible_refusal_after_T"] for r in rows)}
    output = {"status": "passed", "scope": "Reanalysis of sanitized saved evidence, not new production trials. Private evidence hashes identify retained files but do not independently prove service state.", "totals": totals, "state_comparisons": comparisons, "A_before_branch_checks": before_A_checks, "precleanup_unchanged_record_checks": precleanup_checks, "refused_absence_checks": refused_absence_checks, "exact_record_cleanup": cleanup_counts, "expected_controls_match": True, "input_sha256": source_hashes, "limitations": ["Eight A fixtures are shared across 48 paired decisions.", "The budget and receipt delivery are local test controls, not Google billing or quotas.", "Drive search packets contain no pagination field; counts are bounded query results and exact known-ID checks.", "Drive cleanup uses browser location evidence; the connector did not expose the trashed field.", "Calendar coverage is the primary calendar and declared marker/date scope."]}
    write_csv(args.out / "live_rows.csv", rows)
    write_csv(args.out / "live_summary.csv", summary)
    write_json(args.out / "live_checks.json", output)
    print(json.dumps({"status": "passed", **totals}, sort_keys=True))


if __name__ == "__main__":
    main()
