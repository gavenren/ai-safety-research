#!/usr/bin/env python3
"""Check the analysis against saved live records and exact reruns.

This check does not create trial inputs or run a browser experiment.
"""
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
OUTPUTS = ("live_results.csv", "live_pairs.csv", "live_summary.json", "live_analysis_log.txt", "live_analysis_environment.json")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def exact_text_count(snapshot, token):
    """Second count method: match exact task text nodes, never input nodes."""
    patterns = (r"^\s*- generic: " + re.escape(token) + r"$",
                r"^\s*\d+ text " + re.escape(token) + r"$")
    return sum(any(re.fullmatch(pattern, line) for pattern in patterns) for line in snapshot.splitlines())


def main():
    with (ROOT / "live_results.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    with (ROOT / "live_assignments.csv").open(newline="") as handle:
        assignments = list(csv.DictReader(handle))
    with (ROOT / "live_pairs.csv").open(newline="") as handle:
        pairs = list(csv.DictReader(handle))
    summary = json.loads((ROOT / "live_summary.json").read_text())
    manifest = json.loads((ROOT / "live_plan_manifest.json").read_text())
    require(len(rows) == len(assignments) == 60, "All 60 assigned rows must be present.")
    require([r["trial_id"] for r in rows] == [a["trial_id"] for a in assignments], "Result order must match the assignments.")
    require(len({r["token"] for r in rows}) == 60, "Tokens must be unique.")
    require(len(pairs) == 120, "Expected all ten rule pairs in each of twelve blocks.")
    for name, expected in manifest["files"].items():
        require(digest(ROOT / name) == expected, f"Plan hash differs: {name}")
    logs = {}
    snapshot_checks = 0
    for runner in ("T", "P"):
        logs[runner] = [json.loads(line) for line in (ROOT / f"live_runner_{runner}_actions.jsonl").read_text().splitlines() if line.strip()]
        for record in logs[runner]:
            if record.get("trial_id") and record.get("snapshot"):
                actual = exact_text_count(record["snapshot"], record["token"])
                recorded = record.get("visible_exact_task_count", record.get("visible_exact_token_count"))
                require(actual == recorded, f"Independent count differs: {record['trial_id']} {record['action']}")
                snapshot_checks += 1
    clean = duplicate = unresolved = no_item = lost = retries = late = control_pass = 0
    for row, assigned in zip(rows, assignments):
        for key in assigned:
            require(row[key] == assigned[key], f"Assignment differs: {row['trial_id']} {key}")
        raw = [r for r in logs[row["runner"]] if r.get("trial_id") == row["trial_id"] and r["action"] != "clock_check"]
        first = next(r for r in raw if r["action"] == "initial_submit")
        decision_index = next(i for i, r in enumerate(raw) if r["action"] in ("decision", "model_decision"))
        decision = raw[decision_index]
        observed = [r for r in raw[:decision_index] if r.get("snapshot")][-1]
        before_reload = next(r for r in raw if r["action"] == "audit_all")
        after_reload = next(r for r in raw if r["action"] == "audit_reload")
        pre = exact_text_count(before_reload["snapshot"], row["token"])
        post = exact_text_count(after_reload["snapshot"], row["token"])
        visible = exact_text_count(observed["snapshot"], row["token"])
        seconds = (parse_time(decision["decision_utc"]) - parse_time(first["before_utc"])).total_seconds()
        retry_count = sum(r["action"] == "retry_submit" for r in raw)
        require(int(row["pre_reload_count"]) == pre, f"Pre-reload count differs: {row['trial_id']}")
        require(int(row["post_reload_count"]) == post, f"Post-reload count differs: {row['trial_id']}")
        require(int(row["decision_visible_count"]) == visible, f"Decision count differs: {row['trial_id']}")
        require(float(row["decision_elapsed_s"]) == seconds, f"Decision time differs: {row['trial_id']}")
        require(int(row["retries"]) == retry_count, f"Retry count differs: {row['trial_id']}")
        expected_clean = decision["decision"] == "success" and 0 <= seconds <= 60 and post == 1
        require(int(row["clean_confirmed"]) == expected_clean, f"Clean result differs: {row['trial_id']}")
        clean += expected_clean
        duplicate += post >= 2
        unresolved += decision["decision"] == "unresolved"
        no_item += post == 0
        lost += pre > 0 and post == 0
        retries += retry_count
        late += seconds > 60
        control_pass += (row["view"] == "All" and expected_clean and retry_count == 0
                         and exact_text_count(first["snapshot"], row["token"]) == 1)
    totals = dict(clean_confirmed=clean, duplicate=duplicate, unresolved_decisions=unresolved,
                  post_reload_zero=no_item, lost_on_reload=lost, retries=retries, late_decisions=late)
    for key, value in totals.items():
        require(summary["overall"][key] == value, f"Summary total differs: {key}")
    require(summary["hypotheses"]["H3"]["passed"] == control_pass, "Control total differs.")
    before = {name: digest(ROOT / name) for name in OUTPUTS}
    with tempfile.TemporaryDirectory(prefix="live-analysis-check-") as temporary:
        output = Path(temporary)
        subprocess.run([sys.executable, str(ROOT / "live_analyze.py"), "--input-dir", str(ROOT), "--output-dir", str(output)],
                       check=True, capture_output=True, text=True)
        rerun = {name: digest(output / name) for name in OUTPUTS}
    require(before == rerun, "Rerun output is not byte-identical.")
    report = {"status": "PASS", "assigned_rows_checked": len(rows), "rule_pairs_checked": len(pairs),
              "independent_snapshot_counts_checked": snapshot_checks, "raw_trial_reconstructions_checked": len(rows),
              "reproduction": "All five output files are byte-identical on a fresh rerun.",
              "output_sha256": before, "independent_totals": totals,
              "independent_all_view_controls_passed": control_pass,
              "scope": "Saved live inputs only. No new browser experiment or synthetic trial result was made.",
              "validator_sha256": digest(Path(__file__)), "python": sys.version}
    (ROOT / "live_analysis_verification.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
