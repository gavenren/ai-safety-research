# Production retry runner instructions

Status: READY_FOR_FREEZE. Do not start scored writes until the lead confirms the frozen plan. Follow `production_plan.md` and your site's rows of `production_assignments.csv`. The CSV order is authoritative.

## Ownership and access

Open your own writer and observer tabs in the existing authenticated browser. Do not take over another agent's tabs. Use only the assigned new Notion test database or exact Calendar trial events. No signup, login change, purchase, message, invitation, sharing change, account setting change, or unrelated record edit is permitted. Do not inspect hidden page state, browser storage, network traffic, or page source. Use supported browser UI controls only for scored actions.

Do not read connector data before the trial decision. A post-decision connector audit is allowed only for your exact test records. If the lead performs that audit, wait for its complete result before cleanup. Record an unavailable audit honestly. Do not change permissions to obtain it.

## Trial sequence

1. Set the explicit current trial ID and exact token from the CSV. Verify previous cleanup. Verify the writer collection and ready All state, observer collection and assigned state, and no existing exact token. Save both baselines. Do not write if a baseline is unknown.
2. Prepare and execute the initial creation procedure. Save the first action that can create a record: Calendar Save or Notion New. This start time defines the 180-second deadline. Record title edits and partial creation errors too.
3. Save writer feedback. Reload the observer's verified current view and take fresh observations until fully ready or the deadline. Do not treat a partial positive or negative result as ready. Record actual view changes made by the service.
4. Apply only the assigned Absence, Wait24, or Scope branch in the plan. Maximum one repeat. Unknown never permits a repeat. Check the deadline immediately before a repeat request. Do not use writer receipts for a core decision. Keep them in the log.
5. Save the final decision before any audit action. Include its UTC time, confirmed/unresolved, observer evidence record IDs, ready count, actual view, and reason. An observation after the deadline cannot support clean confirmation.
6. Capture a task-region decision image. Change to All, reload, obtain a complete audit, save record identities/fields and any blank or partial effects, and capture the audit image. Obtain the post-decision service audit when available. Do not change the decision from this later evidence.
7. Trash only the current trial's records. Reload the covered view and verify active target count zero and no partial residue. Save cleanup evidence and image. Do not delete forever or empty Trash. Stop new writes if cleanup is uncertain.

## Rules

One ready observer target row permits confirmation. Two or more require unresolved. Unknown requires another read, within the deadline.

Absence: ready zero permits one full repeat, then reload/read; confirm only one.

Wait24: after ready zero, begin a new reload at least 24 seconds after initial creation. Even a late first zero requires this new check. If the new ready state is zero and time remains, repeat once. Reload/read; confirm only one. Save the exact reload start time used for the threshold.

Scope: after ready zero in Hidden, apply the frozen scope correction and reload/read. Confirm only one. If zero was already All, stop unresolved. Never repeat.

## Site rules

Calendar: create a nonrecurring event on the verified primary calendar for Jan 3, 2000, 12:00–12:05 pm in the editor zone. Use the exact token, no guests, no location/description/conference, no notifications, Free, Private. Save all fields before Save. Repeat Create, not Duplicate. All search dates are Jan 1–31, 2000; Hidden dates are Jan 1–31, 2001. Search exact token. Use Tab after each date and the Search button with visible text. Save the actual options/native URL. Ready requires Search results, correct query/range, rows or No results found, and no Searching/progressbar. Preserve the preflight time-display discrepancy; do not reinterpret search-row time as service timing.

Notion: use the specified private database. All has no filter. Hidden uses Name contains PROD-NOMATCH. Scope selects All in the same database. Clock starts at New if it can create a page. Title entry completes that same attempt. Save any blank or partial page after an error. Ready needs the full Private/Share/Actions/Settings/Automations banner, intended selected view, Name header, no progressbar or Side Peek, and complete task table or explicit empty state. Do not score the transient row that can appear during reload. No creation form or unresolved overlay may remain.

## Log schema

Use JSONL. Give every record a unique `record_id`. Include `trial_id`, `token`, `site`, `runner`, `tab_role`, `phase`, `start_utc`, and `end_utc` on each record. UTC times must use ISO 8601 with an offset or Z. Do not capture a stale trial ID in a helper closure; pass the ID explicitly.

Actions use `type: action`, `action`, `args`, `before_state`, `after_state`, and `error` (null on success). Observations use `type: observation`, `state`, and `url`. Action states must be full originals or references to separately logged observations. Each observation has its own timing. A snapshot helper must not recursively take more snapshots around its own observation.

Use clear phases: `baseline_writer`, `baseline_observer`, `initial_create`, `writer_feedback`, `first_observer_reload`, `first_observer`, `wait24_reload`, `wait24_observer`, `broaden_scope`, `scope_reload`, `scope_observer`, `retry_create`, `final_observer_reload`, `final_observer`, `decision`, `audit_reload`, `audit_observer`, `service_audit`, `cleanup`, and `cleanup_observer`. Add a distinct phase for an extra or failed action. Never reuse a phase to conceal it.

Decision records use `type: decision`, `decision_utc`, `decision`, `reason`, `evidence_record_ids`, `observed_count`, `actual_view`, `initial_request_record_id`, and `retry_request_record_id` (null if absent). Unstarted records use `type: unstarted`, a reason, and null initial request. Preserve every assignment.

Audit records use `type: audit`, `audit_kind` (browser_after_reload or connector), `evidence_record_ids`, `complete`, `target_count`, `records`, `partial_records`, and `audit_utc`. Records retain private actual IDs/links, names, and relevant fields. Save connector request bounds, pagination, response limits, and raw response where available. Images use `type: image`, phase, capture start/end, local path, byte format, crop, and related observation IDs. Images are not decision observations unless separately read before the decision.

Keep full private originals locally. Do not redact the raw file during the run. Append corrections as new records. Use unique image names and do not overwrite. The Notion connector returned 401 during preflight; use the declared browser-only audit and do not claim API confirmation. Do not repeat credentials or change access. Capture distinct page IDs from native visible links. Scope selects All; it does not edit the Hidden filter. The lead will make the public extraction and hashes after the run. Retain setup errors, late decisions, failed writes, and missing audits. Do not rerun a trial to improve its result.
