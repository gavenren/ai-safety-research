#!/usr/bin/env python3
"""Score only saved live-site evidence. Python standard library only.

Run: python3 live_analyze.py [--input-dir DIR] [--output-dir DIR]
No browser, network, app storage, or earlier simulated results are read.
The final runner result is a decision record. It is not independent proof of
what the UI showed. Counts below are extracted from saved UI snapshots.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import re
import statistics
import sys
from urllib.parse import urlparse

RULES = ("no_retry", "absence", "timeout24", "closure", "scope")
VIEWS = ("All", "Completed")
DEADLINE = 60.0
WAIT = 24.0
EXPECTED_TRIALS = 60


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(value):
    if not value:
        return None
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result if result.tzinfo else None
    except (ValueError, TypeError):
        return None


def elapsed(start, end):
    return (end - start).total_seconds() if start is not None and end is not None else None


def distribution(values):
    values = [v for v in values if v is not None]
    return {"n": len(values), "minimum": min(values) if values else None,
            "median": statistics.median(values) if values else None,
            "maximum": max(values) if values else None,
            "mean": statistics.mean(values) if values else None}


def field(record, *names):
    return next((record[n] for n in names if n in record and record[n] is not None), None)


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def action_name(record):
    return str(field(record, "action", "kind", "type", "event") or "").lower()


def action_phase(record):
    return str(field(record, "phase", "stage", "label") or action_name(record)).lower()


def action_time(record, end=False):
    names = ("after_utc", "end_utc", "finished_utc", "utc_after", "utc", "timestamp") if end else (
        "before_utc", "start_utc", "started_utc", "utc_before", "utc", "timestamp")
    return utc(field(record, *names))


def snapshot_text(record):
    """Return the stored UI snapshot, never a runner's inferred count."""
    for name in ("snapshot", "dom_snapshot", "domSnapshot", "observation", "accessibility", "dom", "ui"):
        val = record.get(name)
        if isinstance(val, str):
            return val
        if isinstance(val, dict):
            nested = snapshot_text(val)
            if nested is not None:
                return nested
    return None


def snapshot_labels(text, token):
    """Read exact task labels and their adjacent visible checkbox states.

    Supported formats are the saved browser role tree (runner T) and the
    numbered macOS accessibility tree (runner P). A matching input value
    cannot match either task-label expression. A missing checkbox makes the
    count unknown, rather than silently removing a visible task label.
    """
    if text is None:
        return None
    lines = text.splitlines()
    labels = []
    for index, line in enumerate(lines):
        label = re.match(r'^\s*- (?:generic|text): (.*)$', line)
        if label is None:
            label = re.match(r'^\s*\d+ text (.*)$', line)
        if label is None or label.group(1).strip().strip('"') != token:
            continue
        previous = lines[index - 1].strip() if index else ''
        if re.match(r'^- checkbox(?:$| \[)', previous):
            labels.append('[checked]' not in previous)
        elif re.match(r'^\d+ checkbox .*Description: Toggle Todo, Value: [01](?:$|,)', previous):
            labels.append(bool(re.search(r'Value: 0(?:$|,)', previous)))
        else:
            return None
    ready_t = ('heading "todos"' in text and 'textbox "What needs to be done?"' in text
               and all('link "' + view + '"' in text for view in ('All', 'Active', 'Completed')))
    ready_p = ('heading todos' in text and 'text field' in text and all(
        'link Description: ' + view + ', Value:' in text for view in ('All', 'Active', 'Completed')))
    return labels if ready_t or ready_p else None


def snapshot_count(text, token):
    labels = snapshot_labels(text, token)
    return len(labels) if labels is not None else None


def input_token_visible(text, token):
    """Whether a saved input control visibly contains the exact trial token.

    False means the token was not shown in that control. It does not prove
    why a submission did or did not create a task.
    """
    if text is None:
        return None
    inputs = [line.strip() for line in text.splitlines()
              if re.match(r'^\s*- textbox "What needs to be done\?"', line)
              or re.match(r'^\s*\d+ text field(?:\s|$)', line)]
    if not inputs:
        return None
    return any(re.search(r'(?:\]: |"(?: \[active\])?: |Value: )' + re.escape(token) + r'$', line)
               is not None for line in inputs)


def selected_view(record):
    # `view` is the assigned condition in both runner schemas, not the current
    # page state. Read the saved URL so scope and audit view changes are visible.
    url = field(record, "url", "page_url")
    if isinstance(url, str):
        fragment = urlparse(url).fragment.lower().rstrip("/")
        if fragment.endswith("completed"):
            return "Completed"
        if fragment.endswith("active"):
            return "Active"
        if fragment in ("", "/") or fragment.endswith("/all"):
            return "All"
    value = field(record, "selected_view", "current_view", "filter")
    return value if value in (*VIEWS, "Active") else None


def write_csv(path, rows):
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (list, dict)) else v
                             for k, v in row.items()})


class Analyzer:
    def __init__(self, source):
        self.source = source
        self.issues = []
        self.source_files = {}
        self.global_errors = []
        self.diagnostics = []
        self.records = defaultdict(list)
        self.results = defaultdict(list)
        self.raw_line_counts = {}
        self.manifest_saved = None
        self.runner_first_admission = {}

    def issue(self, code, detail, trial=None, severity="error"):
        row = {"severity": severity, "code": code, "detail": detail}
        if trial:
            row["trial_id"] = trial
        self.issues.append(row)

    def read_json(self, name, required=True):
        path = self.source / name
        if not path.is_file():
            if required:
                self.issue("missing_input", name)
            return None
        self.source_files[name] = sha256(path)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as error:
            self.issue("invalid_json", f"{name}: {error}")
            return None

    def load(self):
        manifest = self.read_json("live_plan_manifest.json")
        if isinstance(manifest, dict):
            self.manifest_saved = utc(manifest.get("saved_utc"))
            if self.manifest_saved is None:
                self.issue("invalid_manifest_time", "The plan has no valid UTC save time.")
            for name, expected in manifest.get("files", {}).items():
                path = self.source / name
                if not path.is_file():
                    self.issue("manifest_file_missing", name)
                    continue
                actual = sha256(path)
                self.source_files[name] = actual
                if actual != expected:
                    self.issue("manifest_hash_mismatch", name)
            for required in ("live_plan.md", "live_assignments.csv"):
                if required not in manifest.get("files", {}):
                    self.issue("manifest_entry_missing", required)
        assignments_path = self.source / "live_assignments.csv"
        if not assignments_path.is_file():
            self.issue("missing_assignments", assignments_path.name)
            self.assignments = []
            return
        self.source_files[assignments_path.name] = sha256(assignments_path)
        with assignments_path.open(newline="", encoding="utf-8") as handle:
            self.assignments = list(csv.DictReader(handle))
        if len(self.assignments) != EXPECTED_TRIALS:
            self.issue("assignment_count", f"Expected {EXPECTED_TRIALS}; found {len(self.assignments)}.")
        for key in ("trial_id", "token"):
            for value, n in Counter(a.get(key) for a in self.assignments).items():
                if not value or n != 1:
                    self.issue("assignment_not_unique", f"{key}={value!r}; count={n}")
        self.expected = {a["trial_id"]: a for a in self.assignments}
        design_counts = Counter((a.get("site"), a.get("view"), a.get("rule"), a.get("repeat")) for a in self.assignments)
        if len(design_counts) != 60 or any(n != 1 for n in design_counts.values()):
            self.issue("assignment_cells", "The fixed design does not contain 60 unique cells.")
        expected_cells = {(site, view, rule, str(repeat)) for site in ("todomvc.com", "demo.playwright.dev")
                          for view in VIEWS for rule in RULES for repeat in (1, 2, 3)}
        if set(design_counts) != expected_cells:
            self.issue("assignment_design_mismatch", "Saved cells differ from the fixed two-site design.")
        for runner in sorted({a["runner"] for a in self.assignments}):
            action_file = self.source / f"live_runner_{runner}_actions.jsonl"
            if not action_file.is_file():
                self.issue("missing_raw_file", action_file.name)
            else:
                self.source_files[action_file.name] = sha256(action_file)
                previous = None
                n = 0
                for line_number, line in enumerate(action_file.read_text(encoding="utf-8").splitlines(), 1):
                    if not line.strip():
                        continue
                    n += 1
                    try:
                        record = json.loads(line)
                    except ValueError as error:
                        self.issue("invalid_raw_json", f"{action_file.name}:{line_number}: {error}")
                        continue
                    if not isinstance(record, dict):
                        self.issue("invalid_raw_schema", f"{action_file.name}:{line_number}")
                        continue
                    record["_source"] = f"{action_file.name}:{line_number}"
                    record["_index"] = line_number
                    trial_id = field(record, "trial_id", "trial", "id")
                    if action_name(record) in ("clock_check", "diagnostic_correction", "startup_log_context_correction", "path_metadata_normalization"):
                        self.diagnostics.append({"runner": runner, **record})
                    if action_name(record) == "clock_check":
                        self.issue("diagnostic_clock_record_excluded", record["_source"] + ": clock-only record; a later correction identifies its stale trial label.", severity="warning")
                    start, end = action_time(record), action_time(record, True)
                    if start and end and end < start:
                        self.issue("action_time_reversed", record["_source"], trial_id)
                    if start and previous and start < previous:
                        self.issue("raw_time_order", record["_source"], trial_id)
                    if start:
                        previous = start
                    if trial_id:
                        if action_name(record).startswith("prepare") and start is not None:
                            self.runner_first_admission.setdefault(runner, start)
                        if trial_id not in self.expected:
                            self.issue("unknown_raw_trial", record["_source"], trial_id)
                        elif self.expected[trial_id]["runner"] != runner:
                            self.issue("raw_runner_mismatch", record["_source"], trial_id)
                        self.records[trial_id].append(record)
                    elif record.get("error") or record.get("errors") or "error" in action_name(record):
                        self.global_errors.append({"runner": runner, **record})
                self.raw_line_counts[runner] = n
            result_data = self.read_json(f"live_runner_{runner}_results.json")
            if isinstance(result_data, dict):
                result_data = field(result_data, "results", "trials", "records")
            if result_data is not None and not isinstance(result_data, list):
                self.issue("invalid_result_schema", f"Runner {runner}: expected a list.")
                continue
            for result in result_data or []:
                if not isinstance(result, dict):
                    self.issue("invalid_result_record", f"Runner {runner}")
                    continue
                trial_id = field(result, "trial_id", "trial", "id")
                if not trial_id or trial_id not in self.expected:
                    self.issue("unknown_result_trial", f"Runner {runner}: {trial_id}")
                    continue
                if self.expected[trial_id]["runner"] != runner:
                    self.issue("result_runner_mismatch", f"Runner {runner}", trial_id)
                self.results[trial_id].append(result)
        for runner in sorted({a["runner"] for a in self.assignments}):
            expected_order = [a["trial_id"] for a in self.assignments if a["runner"] == runner]
            observed_order = sorted((r["_index"], trial_id) for trial_id, records in self.records.items()
                                    for r in records if action_name(r) == "initial_submit"
                                    and self.expected.get(trial_id, {}).get("runner") == runner)
            actual_ids = [trial_id for _, trial_id in observed_order]
            if actual_ids != [trial_id for trial_id in expected_order if trial_id in actual_ids]:
                self.issue("trial_submission_order_mismatch", f"Runner {runner}: {actual_ids}")

    def score(self, assigned):
        trial_id = assigned["trial_id"]
        raw_all = self.records[trial_id]
        raw = [r for r in raw_all if action_name(r) not in ("clock_check", "diagnostic_correction")]
        result_list = self.results[trial_id]
        result = result_list[0] if result_list else {}
        evidence_issues = [x["code"] for x in self.issues if x.get("trial_id") == trial_id and x["severity"] == "error"]
        deviations, metadata_warnings = [], []
        def flag(code, detail="", policy=False, warning=False):
            (deviations if policy else metadata_warnings if warning else evidence_issues).append(code)
            self.issue(code, detail or trial_id, trial_id, "policy" if policy else "warning" if warning else "error")
        if not raw and not result:
            flag("no_trial_evidence")
        if len(result_list) > 1:
            flag("duplicate_result_record")
        if result and not raw:
            flag("result_without_raw_records")
        for record in raw + result_list:
            for key in ("trial_id", "runner", "site", "rule", "view", "token", "repeat"):
                if key in record and record[key] is not None and key != "view" and str(record[key]) != str(assigned[key]):
                    flag("assignment_mismatch", f"{key}: {record[key]!r} != {assigned[key]!r}")
        if result.get("view") is not None and result["view"] != assigned["view"]:
            flag("result_view_mismatch")
        submits = [r for r in raw if action_name(r) in ("submit", "initial_submit", "retry", "retry_submit", "submit_initial", "submit_retry")]
        decisions = [r for r in raw if action_name(r) in ("decision", "model_decision", "stop", "record_decision")]
        observations = []
        for record in raw:
            text = snapshot_text(record)
            if text is not None:
                observations.append({"record": record, "count": snapshot_count(text, assigned["token"]),
                                     "time": action_time(record, True), "view": selected_view(record),
                                     "phase": action_phase(record), "index": record["_index"]})
        decision_record = decisions[-1] if decisions else result
        initial = action_time(submits[0]) if submits else None
        decision_time = utc(field(decision_record, "decision_utc", "utc", "after_utc", "end_utc"))
        if initial is None and result.get("initial_submit_utc"):
            flag("submit_time_missing_from_raw")
        if initial and self.manifest_saved and initial < self.manifest_saved:
            flag("scored_action_precedes_plan")
        if submits and decisions and decision_time is None:
            flag("decision_time_missing_from_raw")
        if not decisions and result.get("decision") and result.get("decision") not in ("unstarted", "not_started"):
            flag("decision_missing_from_raw")
        decision = str(field(decision_record, "decision", "outcome", "stop_kind") or "")
        if not decision and result:
            decision = str(result.get("decision") or "")
        if decision and decision not in ("success", "duplicate", "unresolved", "late", "interrupted", "unstarted", "not_started", "error"):
            flag("unknown_decision_value", decision)
        if decisions and result.get("decision") is not None and result["decision"] != decision:
            flag("decision_record_mismatch")
        reported_initial = utc(result.get("initial_submit_utc"))
        initial_time_difference = elapsed(reported_initial, initial)
        if initial_time_difference is not None and initial_time_difference != 0:
            flag("initial_submit_clock_read_difference", f"Raw action start minus result start: {initial_time_difference} seconds.", warning=True)
        if decisions and result.get("initial_submit_utc") != decision_record.get("initial_submit_utc"):
            flag("result_and_decision_initial_time_mismatch")
        if decisions and result.get("decision_utc") and utc(result["decision_utc"]) != decision_time:
            flag("decision_time_mismatch")
        duration = elapsed(initial, decision_time)
        reported_start_duration = elapsed(reported_initial, decision_time)
        deadline_agrees = ((0 <= duration <= DEADLINE) == (0 <= reported_start_duration <= DEADLINE)
                           if duration is not None and reported_start_duration is not None else None)
        if deadline_agrees is False:
            flag("deadline_class_changes_between_clock_reads")
        if duration is not None and duration < 0:
            flag("decision_precedes_submit")
        decision_index = decisions[-1]["_index"] if decisions else None
        # Explicit phase labels are required for the two audit counts.
        post_audit = [o for o in observations if "post_reload" in o["phase"] or "after_reload" in o["phase"] or o["phase"] == "audit_reload"]
        pre_audit = [o for o in observations if "pre_reload" in o["phase"] or "before_reload" in o["phase"] or o["phase"] == "audit_all"]
        decision_obs = [o for o in observations if decision_index is not None and o["index"] < decision_index]
        if decision_index is None:
            decision_obs = [o for o in observations if o["time"] and decision_time and o["time"] <= decision_time
                            and "audit" not in o["phase"] and o not in post_audit and o not in pre_audit]
        decision_obs = [o for o in decision_obs if initial is not None and o["time"] and o["time"] >= initial]
        initial_obs = decision_obs[0] if decision_obs else None
        at_decision = decision_obs[-1] if decision_obs else None
        pre, post = (pre_audit[-1] if pre_audit else None), (post_audit[-1] if post_audit else None)
        def obs_count(observation):
            return observation["count"] if observation else None
        visible, pre_count, post_count = map(obs_count, (at_decision, pre, post))
        input_visibility = {label + "_input_token_visible": input_token_visible(snapshot_text(obs["record"]), assigned["token"]) if obs else None
                            for label, obs in (("initial", initial_obs), ("decision", at_decision), ("pre_reload", pre), ("post_reload", post))}
        post_states = snapshot_labels(snapshot_text(post["record"]), assigned["token"]) if post else None
        post_active_count = sum(post_states) if post_states is not None else None
        if result.get("post_reload_active_count") is not None and result["post_reload_active_count"] != post_active_count:
            flag("active_count_mismatch")
        if decisions and decision_record.get("decision_visible_count") is not None and decision_record["decision_visible_count"] != visible:
            flag("raw_decision_count_mismatch")
        if at_decision and decision_time and at_decision["time"] and at_decision["time"] > decision_time:
            flag("decision_precedes_its_observation")
        if decision_index is not None and any(r["_index"] > decision_index for r in submits):
            flag("submission_after_decision", policy=True)
        if len(decisions) > 1:
            flag("multiple_decisions")
        if len([r for r in submits if action_name(r) == "initial_submit"]) > 1:
            flag("multiple_initial_submissions")
        for observation in observations:
            record = observation["record"]
            reported = field(record, "visible_exact_task_count", "visible_exact_token_count")
            if reported is not None and reported != observation["count"]:
                flag("raw_reported_count_mismatch", record["_source"])
            if record.get("url") and urlparse(record["url"]).hostname != assigned["site"]:
                flag("unexpected_site_url", record["_source"])
            if action_time(record) is None or action_time(record, True) is None:
                flag("missing_observation_time", record["_source"])
        for key, derived in (("decision_visible_count", visible), ("pre_reload_count", pre_count), ("post_reload_count", post_count)):
            if key in result and result[key] is not None and result[key] != derived:
                flag("reported_count_mismatch", f"{key}: result={result[key]!r}; raw={derived!r}")
        started = bool(submits)
        if started:
            if not result:
                flag("missing_result_record")
            if visible is None:
                flag("decision_count_not_derivable")
            if pre_count is None or post_count is None:
                flag("audit_count_not_derivable")
            for audit_name, observation in (("pre_reload", pre), ("post_reload", post)):
                if observation and observation["view"] != "All":
                    flag("audit_all_view_not_verified", audit_name)
                if observation and decision_time and action_time(observation["record"]) and action_time(observation["record"]) < decision_time:
                    flag("audit_precedes_decision", audit_name)
            if pre and post and post["index"] <= pre["index"]:
                flag("reload_audit_order")
        retries = max(0, len(submits) - 1)
        if result.get("retries") is not None and result["retries"] != retries:
            flag("retry_count_mismatch")
        if len(submits) > 2:
            flag("more_than_two_submissions", policy=True)
        errors = [{"source": r["_source"], "action": action_name(r), "error": r.get("error"), "errors": r.get("errors")} for r in raw
                  if r.get("error") or r.get("errors") or "error" in action_name(r)]
        declared_deviations = as_list(result.get("policy_deviations"))
        declared_errors = as_list(field(result, "action_errors", "errors"))
        if started and initial_obs is None:
            flag("missing_initial_observation")
        baseline = [o for o in observations if submits and o["index"] < submits[0]["_index"]]
        if started and (not baseline or baseline[-1]["count"] != 0):
            flag("baseline_zero_not_verified")
        admission_records = [r for r in raw if action_name(r).startswith("prepare")]
        admission = action_time(admission_records[0]) if admission_records else None
        admission_offset = elapsed(self.runner_first_admission.get(assigned["runner"]), admission)
        if admission_offset is not None and admission_offset > 20 * 60:
            flag("admitted_after_runner_budget", policy=True)
        if started and not any("reload" in action_name(r) for r in admission_records):
            flag("pretrial_reload_not_recorded")
        if started and baseline and initial and baseline[-1]["time"] and baseline[-1]["time"] > initial:
            flag("submission_precedes_baseline_end")
        if started and baseline and baseline[-1]["view"] != assigned["view"]:
            flag("baseline_view_not_verified")
        first_count = obs_count(initial_obs)
        retry_eligible = None
        retry_obs_elapsed = None
        retry_obs_reported_start_elapsed = None
        wait_threshold_agrees = None
        if started:
            retry_eligible = False
            if assigned["rule"] == "absence":
                retry_eligible = first_count == 0 if first_count is not None else None
            elif assigned["rule"] == "timeout24":
                eligible_obs = [o for o in decision_obs if o["count"] == 0 and elapsed(initial, action_time(o["record"])) is not None
                                and elapsed(initial, action_time(o["record"])) >= WAIT]
                retry_eligible = bool(first_count == 0 and eligible_obs) if first_count is not None else None
            elif assigned["rule"] in ("closure", "scope"):
                # These task sites have no registered attempt-specific terminal
                # guarantee. A declared signal requires manual evidence review.
                if any(r.get("terminal_guarantee") for r in raw):
                    retry_eligible = None
                    flag("terminal_guarantee_needs_review")
            if retries:
                prior = [o for o in decision_obs if o["index"] < submits[1]["_index"]]
                retry_obs = prior[-1] if prior else None
                retry_obs_elapsed = elapsed(initial, action_time(retry_obs["record"])) if retry_obs else None
                retry_obs_reported_start_elapsed = elapsed(reported_initial, action_time(retry_obs["record"])) if retry_obs else None
                if assigned["rule"] == "timeout24" and retry_obs_elapsed is not None and retry_obs_reported_start_elapsed is not None:
                    wait_threshold_agrees = (retry_obs_elapsed >= WAIT) == (retry_obs_reported_start_elapsed >= WAIT)
                    if not wait_threshold_agrees:
                        flag("wait_class_changes_between_clock_reads")
                if retry_obs is None or retry_obs["count"] != 0:
                    flag("retry_without_zero_observation", policy=True)
                if assigned["rule"] == "absence" and retry_obs is not initial_obs:
                    flag("absence_retry_did_not_follow_first_observation", policy=True)
                if assigned["rule"] == "no_retry":
                    flag("no_retry_rule_retried", policy=True)
                if assigned["rule"] in ("closure", "scope"):
                    flag("retry_without_verified_terminal_guarantee", policy=True)
                if assigned["rule"] == "timeout24" and (retry_obs_elapsed is None or retry_obs_elapsed < WAIT):
                    flag("timeout_retry_before_24_second_observation", policy=True)
                retry_time = action_time(submits[1])
                if elapsed(initial, retry_time) is not None and elapsed(initial, retry_time) > DEADLINE:
                    flag("retry_after_deadline", policy=True)
            elif retry_eligible and decision and duration is not None and duration <= DEADLINE:
                flag("eligible_retry_not_taken", policy=True)
            if assigned["rule"] != "scope" and any(o["view"] is not None and o["view"] != assigned["view"] for o in decision_obs):
                flag("fixed_view_rule_changed_view", policy=True)
            if assigned["rule"] == "scope" and first_count == 0 and not any(o["view"] == "All" for o in decision_obs[1:]):
                flag("scope_rule_did_not_check_all", policy=True)
            if decision == "success" and visible != 1:
                flag("success_without_one_visible_item", policy=True)
            if decision == "duplicate" and (visible is None or visible < 2):
                flag("duplicate_decision_without_visible_duplicate", policy=True)
        screenshot_records = [r for r in raw if action_name(r) == "audit_screenshot"]
        action_wall_times = [elapsed(action_time(r), action_time(r, True)) for r in raw
                             if r.get("before_utc") and r.get("after_utc")]
        action_wall_times = [value for value in action_wall_times if value is not None and value >= 0]
        if started and not screenshot_records:
            flag("audit_screenshot_not_recorded")
        on_time = duration is not None and 0 <= duration <= DEADLINE
        late = duration is not None and duration > DEADLINE
        clean = bool(started and decision == "success" and on_time and post_count == 1)
        duplicate = None if post_count is None else post_count >= 2
        audit_complete = bool(pre_count is not None and post_count is not None and pre and post
                              and pre["view"] == post["view"] == "All")
        state = "unstarted" if not started else "decision_recorded" if decision else "started_without_decision"
        if not started and raw:
            state = "admission_failed"
        # An integrity pass is separate from the planned outcome definition.
        integrity_ok = not evidence_issues
        verified_clean = clean and integrity_ok and visible == 1 and audit_complete and post_active_count == 1
        control_pass = (verified_clean and retries == 0 and first_count == 1 and not deviations
                        and not declared_deviations) if assigned["view"] == "All" else None
        return {**assigned, "state": state, "started": int(started), "raw_actions": len(raw),
                "raw_records_including_diagnostics": len(raw_all), "excluded_diagnostic_records": len(raw_all) - len(raw),
                "raw_observations": len(observations), "submissions": len(submits), "retries": retries,
                "recorded_action_wall_seconds_total": sum(action_wall_times),
                "recorded_action_wall_seconds_maximum": max(action_wall_times) if action_wall_times else None,
                "admission_utc": admission.isoformat() if admission else None, "runner_admission_elapsed_s": admission_offset,
                "retry_eligible": retry_eligible, "initial_visible_count": first_count,
                "decision": decision or ("unstarted" if not started else "missing"),
                "decision_visible_count": visible, "initial_submit_utc": initial.isoformat() if initial else None,
                "decision_utc": decision_time.isoformat() if decision_time else None,
                "reported_initial_submit_utc": result.get("initial_submit_utc"),
                "initial_clock_read_difference_s": initial_time_difference,
                "decision_elapsed_s": duration, "decision_elapsed_from_reported_start_s": reported_start_duration,
                "deadline_class_agrees_between_clock_reads": deadline_agrees,
                "retry_observation_elapsed_s": retry_obs_elapsed,
                "retry_observation_from_reported_start_s": retry_obs_reported_start_elapsed,
                "wait_class_agrees_between_clock_reads": wait_threshold_agrees,
                "pre_reload_count": pre_count, "post_reload_count": post_count, "post_reload_active_count": post_active_count,
                "audit_complete": int(audit_complete), "pre_reload_duplicate": pre_count >= 2 if pre_count is not None else None,
                "pre_reload_zero": pre_count == 0 if pre_count is not None else None,
                "post_reload_zero": post_count == 0 if post_count is not None else None,
                "lost_on_reload": pre_count > 0 and post_count == 0 if pre_count is not None and post_count is not None else None,
                "count_fell_on_reload": post_count < pre_count if pre_count is not None and post_count is not None else None,
                "count_rose_on_reload": post_count > pre_count if pre_count is not None and post_count is not None else None,
                **input_visibility, "screenshot": f"runner_{assigned['runner']}/screenshots/{trial_id}.jpg" if screenshot_records else None,
                "screenshot_record_count": len(screenshot_records),
                "clean_confirmed": int(clean),
                "verified_clean_confirmed": int(verified_clean), "duplicate": duplicate,
                "unresolved_decision": int(decision == "unresolved"), "late_decision": int(late),
                "no_stored_item": int(post_count == 0) if post_count is not None else None,
                "one_item_without_clean_confirmation": int(post_count == 1 and not clean) if post_count is not None else None,
                "all_control_pass": control_pass, "integrity_ok": int(integrity_ok),
                "policy_deviations": sorted(set(deviations)), "declared_policy_deviations": declared_deviations,
                "evidence_issues": sorted(set(evidence_issues)), "metadata_warnings": sorted(set(metadata_warnings)), "action_errors": errors,
                "declared_action_errors": declared_errors}


def summarize(rows):
    counts = {"assigned": len(rows), "started": sum(r["started"] for r in rows),
              "unstarted": sum(not r["started"] for r in rows),
              "decisions_recorded": sum(r["decision"] not in ("missing", "unstarted", "not_started") for r in rows),
              "audits_complete": sum(r["audit_complete"] for r in rows),
              "all_controls_assigned": sum(r["view"] == "All" for r in rows),
              "all_controls_passed": sum(r["all_control_pass"] is True for r in rows),
              "all_controls_failed": sum(r["all_control_pass"] is False for r in rows),
              "duplicate": sum(r["duplicate"] is True for r in rows),
              "duplicate_unknown": sum(r["duplicate"] is None for r in rows),
              "pre_reload_duplicates": sum(r["pre_reload_duplicate"] is True for r in rows),
              "pre_reload_zero": sum(r["pre_reload_zero"] is True for r in rows),
              "post_reload_zero": sum(r["post_reload_zero"] is True for r in rows),
              "lost_on_reload": sum(r["lost_on_reload"] is True for r in rows),
              "count_fell_on_reload": sum(r["count_fell_on_reload"] is True for r in rows),
              "count_rose_on_reload": sum(r["count_rose_on_reload"] is True for r in rows),
              "initial_input_token_visible": sum(r["initial_input_token_visible"] is True for r in rows),
              "decision_input_token_visible": sum(r["decision_input_token_visible"] is True for r in rows),
              "initial_input_visibility_unknown": sum(r["initial_input_token_visible"] is None for r in rows),
              "clean_confirmed": sum(r["clean_confirmed"] for r in rows),
              "verified_clean_confirmed": sum(r["verified_clean_confirmed"] for r in rows),
              "unresolved_decisions": sum(r["unresolved_decision"] for r in rows),
              "late_decisions": sum(r["late_decision"] for r in rows),
              "retries": sum(r["retries"] for r in rows),
              "retry_eligible": sum(r["retry_eligible"] is True for r in rows),
              "retry_eligibility_unknown": sum(r["retry_eligible"] is None for r in rows),
              "trials_with_policy_deviations": sum(bool(r["policy_deviations"] or r["declared_policy_deviations"]) for r in rows),
              "trials_with_action_errors": sum(bool(r["action_errors"] or r["declared_action_errors"]) for r in rows),
              "trials_with_evidence_issues": sum(bool(r["evidence_issues"]) for r in rows),
              "trials_with_metadata_warnings": sum(bool(r["metadata_warnings"]) for r in rows),
              "deadline_checks_agree": sum(r["deadline_class_agrees_between_clock_reads"] is True for r in rows),
              "deadline_checks_disagree": sum(r["deadline_class_agrees_between_clock_reads"] is False for r in rows),
              "wait_checks_agree": sum(r["wait_class_agrees_between_clock_reads"] is True for r in rows),
              "wait_checks_disagree": sum(r["wait_class_agrees_between_clock_reads"] is False for r in rows),
              "raw_actions": sum(r["raw_actions"] for r in rows),
              "raw_observations": sum(r["raw_observations"] for r in rows)}
    counts["decision_seconds_descriptive"] = distribution(r["decision_elapsed_s"] for r in rows)
    counts["recorded_action_wall_seconds_total_descriptive"] = distribution(r["recorded_action_wall_seconds_total"] for r in rows if r["started"])
    counts["action_count_descriptive"] = distribution(r["raw_actions"] for r in rows if r["started"])
    return counts


def pair_rows(rows):
    groups = defaultdict(dict)
    for row in rows:
        groups[(row["site"], row["view"], row["repeat"])][row["rule"]] = row
    pairs = []
    for (site, view, repeat), members in sorted(groups.items()):
        for rule_a, rule_b in combinations(RULES, 2):
            a, b = members.get(rule_a), members.get(rule_b)
            if not a or not b:
                continue
            both_audited = bool(a["audit_complete"] and b["audit_complete"])
            both_clean = bool(a["verified_clean_confirmed"] and b["verified_clean_confirmed"])
            pairs.append({"site": site, "view": view, "repeat": repeat,
                          "rule_a": rule_a, "rule_b": rule_b, "trial_a": a["trial_id"], "trial_b": b["trial_id"],
                          "both_started": bool(a["started"] and b["started"]), "both_audited": both_audited,
                          "a_clean": a["clean_confirmed"], "b_clean": b["clean_confirmed"],
                          "b_minus_a_clean": b["clean_confirmed"] - a["clean_confirmed"],
                          "a_duplicate": a["duplicate"], "b_duplicate": b["duplicate"],
                          "b_minus_a_duplicate": int(b["duplicate"]) - int(a["duplicate"]) if both_audited else None,
                          "a_retries": a["retries"], "b_retries": b["retries"],
                          "a_decision": a["decision"], "b_decision": b["decision"],
                          "a_decision_seconds": a["decision_elapsed_s"], "b_decision_seconds": b["decision_elapsed_s"],
                          "b_minus_a_seconds_both_verified_clean": b["decision_elapsed_s"] - a["decision_elapsed_s"] if both_clean else None})
    return pairs


def hypotheses(rows):
    h1_sites, h2_sites = [], []
    for site in sorted({r["site"] for r in rows}):
        members = [r for r in rows if r["site"] == site and r["view"] == "Completed"]
        by_rule = {rule: [r for r in members if r["rule"] == rule] for rule in RULES}
        counts = {rule: summarize(rs) for rule, rs in by_rule.items()}
        h1_rows = [r for r in members if r["rule"] in ("absence", "timeout24", "closure", "scope")]
        complete = all(r["audit_complete"] and r["integrity_ok"] and not r["policy_deviations"] and not r["declared_policy_deviations"] for r in h1_rows)
        eligible = all(r["retry_eligible"] is True for r in h1_rows if r["rule"] in ("absence", "timeout24"))
        comparisons = [{"retry_rule": a, "reference_rule": b,
                        "retry_duplicates": counts[a]["duplicate"], "reference_duplicates": counts[b]["duplicate"],
                        "more_duplicates": counts[a]["duplicate"] > counts[b]["duplicate"]}
                       for a in ("absence", "timeout24") for b in ("closure", "scope")]
        h1_sites.append({"site": site, "counts": counts, "complete_and_valid": complete,
                         "retry_eligibility_met": eligible, "comparisons": comparisons,
                         "status": "inconclusive" if not complete or not eligible else
                                   "direction_met" if all(c["more_duplicates"] for c in comparisons) else "direction_not_met"})
        ref, intervention = counts["closure"], counts["scope"]
        h2_rows = by_rule["closure"] + by_rule["scope"]
        h2_valid = all(r["audit_complete"] and r["integrity_ok"] and not r["policy_deviations"] and not r["declared_policy_deviations"] for r in h2_rows)
        h2_direction = intervention["clean_confirmed"] > ref["clean_confirmed"] and intervention["duplicate"] <= ref["duplicate"]
        h2_sites.append({"site": site, "closure_clean": ref["clean_confirmed"], "scope_clean": intervention["clean_confirmed"],
                         "closure_duplicates": ref["duplicate"], "scope_duplicates": intervention["duplicate"],
                         "complete_and_valid": h2_valid, "direction_met": h2_direction,
                         "status": "inconclusive" if not h2_valid else "direction_met" if h2_direction else "direction_not_met",
                         "individual_repeats": [{"trial_id": r["trial_id"], "repeat": r["repeat"], "rule": r["rule"],
                                                 "clean_confirmed": r["clean_confirmed"], "duplicate": r["duplicate"],
                                                 "decision": r["decision"], "state": r["state"]} for r in h2_rows]})
    control = [r for r in rows if r["view"] == "All"]
    def combine(items):
        return "inconclusive" if any(x["status"] == "inconclusive" for x in items) else (
            "direction_met" if all(x["status"] == "direction_met" for x in items) else "direction_not_met")
    return {"H1": {"criterion": "Each retry rule has more duplicate trials than each reference rule in Completed view; report each site.",
                    "status": combine(h1_sites), "sites": h1_sites},
            "H2": {"criterion": "Scope has more clean confirmations than closure, with no added duplicates, on both sites.",
                    "status": combine(h2_sites), "sites": h2_sites},
            "H3": {"criterion": "Each All-view trial shows one new item without a retry.",
                    "status": "direction_met" if all(r["all_control_pass"] is True for r in control) else
                              "inconclusive" if any(not r["started"] or not r["audit_complete"] for r in control) else "direction_not_met",
                    "assigned": len(control), "passed": sum(r["all_control_pass"] is True for r in control),
                    "failures_or_missing": [{"trial_id": r["trial_id"], "rule": r["rule"], "site": r["site"],
                                             "decision": r["decision"], "initial_visible_count": r["initial_visible_count"],
                                             "retries": r["retries"], "post_reload_count": r["post_reload_count"],
                                             "evidence_issues": r["evidence_issues"], "policy_deviations": r["policy_deviations"]}
                                            for r in control if r["all_control_pass"] is not True]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    out = args.output_dir or args.input_dir
    out.mkdir(parents=True, exist_ok=True)
    analyzer = Analyzer(args.input_dir)
    analyzer.load()
    rows = [analyzer.score(a) for a in analyzer.assignments]
    pairs = pair_rows(rows)
    groups = []
    for keys in (("rule",), ("view",), ("site",), ("site", "view", "rule")):
        grouped = defaultdict(list)
        for row in rows:
            grouped[tuple(row[key] for key in keys)].append(row)
        for values, members in sorted(grouped.items()):
            groups.append({"group_by": list(keys), **dict(zip(keys, values)), **summarize(members)})
    hypothesis_results = hypotheses(rows)
    global_integrity_failures = [issue for issue in analyzer.issues if "trial_id" not in issue and issue["severity"] == "error"]
    if global_integrity_failures:
        for hypothesis in hypothesis_results.values():
            hypothesis["status_before_global_input_check"] = hypothesis["status"]
            hypothesis["status"] = "inconclusive"
            hypothesis["global_input_check_failed"] = True
    summary = {"study": "Saved live website extension", "analysis_version": 1,
               "source_sha256": analyzer.source_files, "scoring": {
                   "clean_confirmed": "Decision says success at or before 60 seconds, and raw post-reload count is one.",
                   "duplicate": "At least two exact task labels in the raw post-reload All-view snapshot.",
                   "verified_clean_confirmed": "Clean confirmation plus valid raw records, one visible item at decision, and exactly one active item after reload.",
                   "active_state": "A task is active when its adjacent visible checkbox is unchecked. Task text in the input is not a task entry.",
                   "missing": "Missing raw observations remain unknown. They are never changed to zero.",
                   "time": "UTC wall time includes model and tool work. It is not website latency.",
                   "action_counts": "Counts refer to saved action records, not individual browser or tool operations.",
                   "admission_budget": "Measured from the first scored prepare action for each runner.",
                   "inference": "Counts and descriptive measures only. No p-values or field confidence intervals."},
               "overall": summarize(rows), "groups": groups, "hypotheses": hypothesis_results,
               "raw_line_counts": analyzer.raw_line_counts, "global_action_errors": analyzer.global_errors,
               "diagnostic_records": analyzer.diagnostics,
               "validation": {"status": "ISSUES_FOUND" if any(x["severity"] in ("error", "policy") for x in analyzer.issues) else
                                          "PASS_WITH_WARNINGS" if analyzer.issues else "PASS",
                              "issues": analyzer.issues, "issue_counts": dict(Counter(x["code"] for x in analyzer.issues))},
               "limitations": ["Two related public demos; fixed order; three repeats per cell.",
                               "Runners share a browser service and host.", "Stored items use browser storage.",
                               "Reload survival is not server durability or indefinite closure.",
                               "No human review is recorded by this analyzer."]}
    write_csv(out / "live_results.csv", rows)
    write_csv(out / "live_pairs.csv", pairs)
    (out / "live_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    environment = {"python": sys.version, "implementation": platform.python_implementation(),
                   "platform": platform.platform(), "dependencies": "Python standard library only",
                   "analyzer_sha256": sha256(Path(__file__)), "input_hashes": analyzer.source_files,
                   "command": "python3 live_analyze.py", "network_or_browser_access": False}
    (out / "live_analysis_environment.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log = ["Live evidence analysis", f"Assigned rows: {len(rows)}", f"Pair comparisons: {len(pairs)}",
           f"Validation: {summary['validation']['status']}",
           "No browser or network access occurred. All missing trials remain in the results.",
           "All time measures include model and tool work. They are not website latency."]
    log += [json.dumps(issue, sort_keys=True) for issue in analyzer.issues]
    (out / "live_analysis_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(json.dumps({"overall": summary["overall"], "validation": summary["validation"]["status"],
                      "issues": len(analyzer.issues), "hypotheses": {k: v["status"] for k, v in summary["hypotheses"].items()}}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
