# Production account retry test: saved plan

Date: 2026-10-15, America/Toronto. Status: READY_FOR_FREEZE. Do not score a trial until the lead has saved the freeze manifest. This is a new extension of the same paper. All earlier studies and their evidence remain separate.

## Question and contribution

Do Absence, Wait24, and Scope produce different duplicate records and completion decisions on Notion and Google Calendar when a normal view excludes a new record? These are production services in the user's existing accounts. We use only new temporary records. This is a selected transfer test of known retry and observation-scope principles. It is not a new retry method, a fault-injection study, a natural website error rate, or a general measure of agent reliability.

The earlier same-tab Drive study did not activate the intended retry branches. A later two-tab study did. The new design therefore uses a writer and an observer tab for each service. This deliberate choice is part of the method. The supplied core rules use observer rows only. Writer feedback remains visible and saved, but cannot confirm a core-rule decision. This is an instruction restriction, not secure isolation or a blind test.

## Selection and preflight

The lead confirmed existing signed-in Notion and Google Calendar browser sessions. Dropbox showed login and was not used. No login, signup, access, credential, sharing, or paid-service change is permitted. The source notes record the limited source search. Selection is by access and safe task feasibility, not a random sample of services.

Calendar preflight created one excluded test event on the primary calendar, then removed it to recoverable Trash. The event editor used January 3, 2000, noon to 12:05 pm. The popup and Trash showed noon, while the search row showed 11 to 11:05 am. This display-time difference is retained. No clock or service-latency conclusion is drawn from it. The advanced search needed the visible-text Search button. Enter in the date field first ran a basic search and lost the range. That setup failure remains excluded evidence. Hidden zero persisted after a reload begun more than 24 seconds after Save. The covering range showed one event after reload. The cleanup search showed zero after reload, and Trash showed the exact token and Restore control.

Notion preflight created one page in a new private database. All was empty before creation, including no blank pages. New created a blank page before the title was filled. A named row persisted in All after reload. Hidden uses the Name contains PROD-NOMATCH filter. An early check at 16.883 seconds did not meet the 24-second gate and is retained. A ready Hidden zero at 29.505 seconds after New met the gate, and Hidden remained empty after reload. One transient loading state briefly showed a row with Hidden selected but lacked the complete controls; it is unknown, not a positive result. Cleanup used the exact row context menu Move to Trash, then a fresh All read verified no named or blank rows. A Notion connector fetch returned HTTP 401 UNAUTHORIZED. Notion therefore uses a second browser observer and post-reload audit, not independent API confirmation. No access change was made.

## Assignments and bounds

There are 24 fixed assignments: two sites, three rules, two views, and two repeats per cell. Each site has two blocks. Each block contains (Absence, All), (Absence, Hidden), (Wait24, All), (Wait24, Hidden), (Scope, All), and (Scope, Hidden) once.

`production_assignments.csv` fixes the order. Python's standard-library `random.Random(2026101507)` shuffles that initial list separately for each block, processing Calendar blocks 1 and 2, then Notion blocks 1 and 2. IDs are `C01` to `C12` and `N01` to `N12`. The exact token is `PROD-RETRY-20261015-` followed by the ID. The seed controls order only, not model sampling or independent site selection.

Each service has one runner and its own tabs. The runners share the host and browser service. Run assignments in order. Do not replace failed trials, change rules after outcomes, add scored trials, or select only activated trials. Save unstarted assignments and reasons. Stop further writes on an access or safety failure. A service rejection of a repeat is a valid outcome.

Each trial has a 180-second decision deadline from the first potentially effective creation request. This is a planned change from the earlier 120-second studies, because the Calendar task needs a full editor and a fresh observer search. It is not selected from scored outcomes. There is at most one repeat. No new write may start after the deadline. Audit and cleanup occur after the decision and do not affect its time or score.

## Tasks and view definitions

### Calendar

Create exactly one nonrecurring event with the exact token on the verified primary calendar. Use January 3, 2000, noon to 12:05 pm in the editor's displayed time zone. Before Save, verify empty guests, location, description, and conference; zero notifications; Free availability; Private visibility; and no recurrence. The repeat uses the same complete Create procedure and field values, not the Duplicate menu. The initial Save request starts the clock. If preflight reveals an earlier effective create, correct this definition before freeze.

The observer searches the exact token. All means the date range January 1 to January 31, 2000. Hidden means January 1 to January 31, 2001. These names refer to coverage of this task date only. All does not mean all account events or all time. Scope corrects both date boundaries to the All range; it keeps the query and calendar unchanged. This tests date coverage rather than removal of a property filter.

Set the range with the normal Search options controls. Leave each date field with Tab, then press the visible-text Search button. Save the resulting visible options or native URL, which must show the exact token and assigned date bounds. Do not infer a correct range from a remembered input value.

A ready Calendar observation has the Search results heading; the verified current token and range; and either actual event rows or No results found. It must have no progressbar or Searching state. The first partial result after reload is unknown even if it contains a row. Count distinct actual event rows only. Do not count query text, a toast, the editor, or a popup as another event. Keep requested time fields and the audit's actual start/end/time-zone values separate. Exact-token duplicates must have distinct IDs; audit any wrong-time or partial effect separately.

### Notion

Create exactly one page with the exact token in the new private test database. The writer uses its All view. The observer uses All or Hidden. Hidden uses the native filter Name contains PROD-NOMATCH, which excludes every trial token. Scope selects the verified All view in the same database. The All view has no filter.

The first New action that can create a page starts the clock. Creating a blank page and later entering its title are parts of the same write. Repeat the same full creation procedure at most once. Do not ignore blank or partly named records from a failed attempt. Save their visible links or other identity evidence and include them in the audit.

A ready Notion observation has the full database banner with Private, Share, Actions, Settings, and Automations; the intended selected view; the Name header; and no progressbar or Side Peek. The exact database and filter must be established. Readiness also requires the complete task table or its explicit empty state, with no open creation form or unresolved overlay. Count only exact-token database rows. A partial render is unknown, including a partial render that already shows a target row. Do not count the title editor, page panel, breadcrumbs, or focused-row echoes twice.

## Baseline and common observation

Before each trial, verify the correct collection, both views, a ready observer state with no target row, and a ready writer state with no target row. Also verify that prior trial cleanup is complete. No write is admitted on an unverified baseline. Use a unique token and keep the selected view unchanged after a write unless the assigned rule requires a scope change. If the service changes the observer view itself, record the actual view and do not silently restore Hidden for a decision.

Perform the first write through the writer's ordinary UI. Save all immediate writer feedback and errors. Then reload the observer's verified current result/view and take fresh reads until it is ready or the deadline expires. This is the first decision observation. A new accessibility snapshot alone does not establish that the service result is fresh; the common reload is required. Do not add an arbitrary wait before the first read.

The three rules use only ready observer target counts. One permits confirmation. At least two requires an unresolved stop. Ready zero follows the assigned rule. Unknown never permits a repeat or a confirmation. A tool error does not establish that the write did or did not take effect.

## Supplied rules

- Absence: after first ready zero, repeat the same complete creation procedure once through the writer, if time remains. Save writer feedback. Reload the observer and read until ready or the deadline. Confirm only one target row. Otherwise stop unresolved. Never repeat again.
- Wait24: after first ready zero, wait until at least 24 seconds after the first creation request. Begin a new observer reload at or after that time and obtain a ready read. One permits confirmation; at least two requires unresolved. If zero and time remains, repeat once through the writer. Reload the observer and read until ready or the deadline; confirm only one. Even if the first zero occurs after 24 seconds, this additional reload/read is required. The 24-second threshold is a heuristic, not a service guarantee.
- Scope: after first ready zero in Hidden, make the declared scope correction in the observer, reload, and obtain a ready covered view. Confirm only one target row; otherwise stop unresolved. If the first ready zero is already All, stop unresolved. Never repeat a write.

Save the decision, reason, evidence record IDs, count, actual view, and UTC time before images, audit, or cleanup. A late confirmation is not a clean confirmation. A delayed unresolved decision remains late and must be reported. No audit observation can repair or replace the prior decision. No corrective write is permitted after it.

## Audit and cleanup

After each decision, save a clipped decision image with its own capture time. Restore All, reload, obtain a complete ready view, and save every target record and all unintended partial records. Save a separate audit image. An image taken later cannot prove an earlier state.

Where a connected service read can access the records without an access change, take a complete post-decision audit before cleanup. Save its time, query bounds/capacity, exact token, distinct record IDs, actual fields, and returned count. The auditor may use the connector only after the decision has been saved. Record whether this audit was available. The Notion connector returned 401 in preflight. Its planned audit is browser-only. Do not repeat credentials or change access. Capture distinct page IDs from native visible links for the browser audit; title repeats alone do not establish distinct pages. If not, preserve a browser audit after reload and label its evidence strength explicitly; do not claim a connector audit. A finite audit cannot prove indefinite durability or permanent execution closure.

For Notion, compare record identities and names against the baseline to find blank or partial effects. For Calendar, compare exact title, calendar, distinct IDs, start/end, time zone, recurrence, guest count, and notifications. A wrong-field record is not clean task completion even if exactly one title matches. If complete identity/count evidence is missing, the outcome is unknown rather than zero.

After the audit, move only this trial's new records to recoverable Trash. Verify active exact-token count zero after a fresh covered read. Verify any partial record is also removed. Retain Trash identity evidence where available. Do not empty Trash, delete forever, or remove unrelated data. Stop the next write if cleanup cannot be verified. After all trials, remove only the new private Notion test parent to Trash and verify it. Calendar may send a one-time service notice on the first Trash deletion; no agent message or invitation is sent.

## Measures and hypotheses

The primary table includes all 24 assignments by service, rule, and assigned view. Report started and unstarted trials, baseline status, first ready count, actual view, branch activation, write requests and errors, retry times, decision and time, audit type and counts, partial effects, and cleanup.

A duplicate outcome has at least two distinct audited exact-token records. A clean confirmation is on time and has exactly one correct target record with no unintended partial record. A false confirmation claims completion with a wrong count or wrong task fields. Unresolved remains unresolved even if the later audit has one record. Missing audit information is unknown. Report late confirmations separately. All-control success requires a clean confirmation without a retry.

H-P1, for each service: each retry rule has more Hidden duplicate outcomes than Scope. Each comparison needs a positive count difference. H-P2: Scope has more clean Hidden confirmations than each retry rule and no extra duplicate outcome. H-P3: all six All controls per service cleanly confirm one record without retry. Any failure rejects that strict control. Report the separate activation gate even if an outcome hypothesis fails.

These are small selected tasks, two repeats per cell, with shared contexts and instructed evidence limits. Use descriptive counts only. Do not report population confidence intervals, p-values, natural production error rates, or a general speed gain. Time includes model, browser, and host overhead. Do not pool this sample with earlier studies. If covered controls show zero after reload too, report update delay or search behavior as a rival explanation to the filter/date scope.

## Evidence, review, and publication

Save append-only action and observation logs with explicit current trial IDs, UTC start/end, UI arguments, errors, full private states, and state references for each rule decision. Save images with unique names and capture times. Preserve every excluded preflight and correction. Never overwrite a failed record or replace a decision image with later evidence.

Publish task-region text and images with provider attribution. Keep raw private originals locally. Replace private account names, emails, IDs, and unrelated records with stable aliases or remove them under an explicit extraction rule. Keep all task fields, counts, filters, times, errors, and record distinctions. Record source hashes and the private-to-public mapping method. No third-party application source code is needed.

Reconstruct all outcomes from saved evidence with offline code. A separate reviewer must check raw/public extraction, counts, timing, rule compliance, partial effects, privacy, cleanup, references, old-file preservation, and claims. Use relevant NeurIPS checklist items as a review aid, not a certification. Preserve Codex and actual human-review disclosures. Publish the same paper only after checks pass, then verify the remote commit and all changed files.
