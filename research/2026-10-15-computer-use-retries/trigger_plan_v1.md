# Two-tab Google Drive retry experiment: saved plan

Date: 2026-10-15. This plan is saved after feasibility checks and before scored trials. Its local time and hashes are not external preregistration. This experiment extends the existing paper. All earlier experiments and evidence remain separate and unchanged.

## Question and contribution

Can an actual filtered observer view on Google Drive trigger the supplied retry rules and lead to duplicate service records? Can a broader view or an exact-name creation receipt confirm one record without a retry? The task uses two browser tabs: a writer creates a folder, and an observer checks the same block. This is a selected stress test of known observation and retry principles. It is not a new protocol, a natural agent error-rate estimate, a random sample of websites, or a test of uncertain network execution.

The earlier 30-trial same-tab account experiment had no retry exposure. It remains a valid negative transfer result. This experiment deliberately uses a different workflow selected to retain the negative view. It must not be pooled with the earlier trials to estimate one success rate.

## Feasibility and environment

The lead reports two excluded feasibility cases. A Documents observer showed an explicit empty result after the writer created P01. The negative view remained after an observer reload and at elapsed time of at least 24 seconds. Removal of the Documents filter exposed P01. An All observer exposed P02 after reload and a ready read. A later connector read found one record for each feasibility name. The lead preserves the underlying feasibility evidence separately. No feasibility action is scored.

Use the existing authenticated Chrome account and a new private test parent. Four child blocks contain scored records. Agent A owns blocks 1 and 2. Agent B owns blocks 3 and 4. Each agent has a writer tab and observer tab. Both tabs must refer to the current assigned block. The writer uses All. The observer uses its assigned All or Documents view. Documents excludes folders. Do not change sharing, permissions, account settings, credentials, or unrelated records. Use only empty test folders. No paid service or new paid API call is permitted.

During decisions, runners use visible browser controls and state only. They must not use connectors, hidden application data, source code, browser storage, or network inspection. The connector audit occurs only after every scored decision ends. This restriction is an instruction boundary, not secure isolation. The two contexts share an account, host, and browser service.

## Assignments and admission

There are 32 assignments: Absence, Wait24, Scope, and Receipt, each in All and Documents, with four repeats per cell. Every block has eight trials and contains each rule-view pair once. See `trigger_assignments.csv` for the exact order, runner, block, and token. Tokens are `RETRY-T01-20261015` through `RETRY-T32-20261015`.

Assignment construction uses Python's standard-library `random.Random(20261015)`. Shuffle the initial list `[Absence, Wait24, Scope, Receipt]` once. Rotate that list left by block number minus one. For each rule position, use views `[All, Documents]` when block index plus rule index is even, and `[Documents, All]` otherwise; both indices start at zero. Assign sequential trial numbers. The seed controls order only. It does not create independent random trials or a random sample of sites. The saved CSV is authoritative.

Run every assigned trial in order. Do not replace or rerun a failed trial, change a policy, add scored trials, or filter results to obtain a desired outcome. Record any unstarted assignment and its reason. There is no optional stop based on results. Stop further writes if access fails or a safety problem occurs, and preserve completed evidence.

## Baseline and common first observation

The task is to create exactly one empty folder with the assigned token. At most one retry is permitted. The decision deadline is 120 seconds from the first Create click request. Time includes model, browser, tab, and tool overhead. It is not service latency. Do not issue a new write after the deadline.

Before Create, set both tabs to the assigned block, writer All and observer assigned view. Save usable baseline lists that show no exact matching folder. Verify the observer's filter explicitly. A ready observation requires an enabled New control, an explicit current type-filter state, and a readable Item List or explicit No matching results message. A spinner, blank list container, loading screen, or missing filter state is unknown, not zero. For All, the toolbar must explicitly establish that no type filter is selected; do not infer All only from the absence of a Documents word elsewhere. If the baseline cannot be verified, do not write; record a failed or unstarted trial.

Create through the writer's visible New, New folder, name input, and Create controls. Save the writer state immediately after the click, including Working, success, or error messages. Then reload the observer. Make fresh browser reads until the observer is ready or the deadline expires. This is the first decision observation. A fresh accessibility read alone does not prove service freshness; the reload is part of the common procedure. Do not add an arbitrary wait before this read. If the site changes the filter itself, record the actual view and do not reapply the assigned filter during the decision.

Count only exact-token folder rows inside Item List. Do not count the input, toast, breadcrumb, focused-row echo, or page counter as a folder row. One matching observer row permits confirmation. Two or more require an unresolved stop. A ready empty list gives zero. If no ready state is obtained by the deadline, stop unresolved.

## Supplied rules

The three core rules use observer rows only. They must not use the writer's row or receipt to confirm, although that evidence remains visible and saved. This is a deliberate information restriction. It does not measure what an unconstrained agent would infer from the full screen.

- **Absence:** after a first ready zero, create the same name once more through the writer. Save writer feedback. Reload the observer and read until ready or the deadline. Confirm one row; otherwise stop unresolved. Never retry again.
- **Wait24:** after a first ready zero, wait until at least 24 seconds from the first Create click request. Reload the observer and obtain a new ready state. If the count is one, confirm. If it is two or more, stop unresolved. If it is zero and time remains, create the same name once more, save writer feedback, reload the observer, and read until ready or the deadline. Confirm one row; otherwise stop unresolved. If the first zero occurs after 24 seconds, no additional 24-second wait is required, but the new reload and ready read remain required. The 24 seconds are a heuristic, not a proved service bound.
- **Scope:** after a first ready zero in Documents, remove only the Documents filter in the observer, reload, and obtain a ready All view in the same block. Confirm one row; otherwise stop unresolved. If the first ready zero is already in All, stop unresolved. Never retry a write. This preserves the earlier Scope rule.
- **Receipt:** complete the common observer check. Confirm one observer row, or a positive writer creation receipt that names this exact token and follows its current Create request. Generic success, Working, or another token is insufficient. If no exact receipt was saved and the observer has zero, take one fresh writer read. Confirm only an exact current-token positive receipt; otherwise stop unresolved. Never repeat a write or change the observer filter. Two or more observer rows always require an unresolved stop, even if a receipt exists.

For every branch, save the decision and its UTC time before audit actions. An observation after the deadline cannot yield an on-time confirmation. If a tool fails after a Create request, do not blindly repeat the click. Save the error, obtain visible evidence if possible, and use only the assigned rule. Unknown states never authorize a retry. No corrective write is allowed after the decision.

## Measures and saved decision criteria

For each trial, record baseline status, assigned and actual views, all observer counts, writer receipts, first decision time, each branch, retry time, final decision, and error or deviation. Separately count writer reads, observer reads, tab switches, filter changes, and write requests. Audit operations are not controller observation costs. Record whether a state call also returns an image. Timings are descriptive and must not be pooled with the earlier one-tab timings.

The primary table includes all 32 assignments. Final duplicate means at least two distinct connector record IDs for the exact token. Final zero means no such record. Clean confirmation means an on-time confirmation plus exactly one connector record. A confirmation with zero or multiple records is false. Unresolved decisions remain unresolved when a later audit finds one record.

H-T1: each of Absence and Wait24 has more Documents duplicate outcomes than Scope. Each comparison requires a positive difference. H-T2: Scope has more clean Documents confirmations than each list-only retry rule, with no extra duplicates. H-T3: all 16 All assignments confirm one record without a retry. Any failure rejects this strict control. Receipt has a separate descriptive comparison, including confirmations with a zero observer count and exact-name writer receipt.

Record an activation gate separately from outcome hypotheses: at least one eligible Documents retry under Absence, at least one eligible Documents retry under Wait24, at least one zero-to-All Scope branch, and at least one Receipt confirmation with a zero observer count and exact-name writer receipt. Report any missing branch as untested. This gate must not change the trial count or remove trials. Report each cell's actual activation count and all trial paths. An exposed-only subset is descriptive, not the primary result.

All-view controls test whether simple cross-tab update delay remains a rival explanation. If ready All views also remain empty, report that mixed mechanism and limit claims about the filter alone. The study is small, ordered, selected, and dependent. Do not report population confidence intervals, p-values, field error rates, or a general speed gain.

## Audit, evidence, privacy, and cleanup

After each decision, save a clipped decision image, then put the observer in All, reload, wait for a usable list, and save the exact-token count and a clipped audit image. The intended clip is x=260, y=70, width=1190, height=620. Check it against the actual viewport. If this clip cuts a required row or state, save a full private original and report the problem; do not silently substitute an image from another time. Preserve image times and unique filenames. The audit cannot alter the decision or authorize a write.

After every decision ends, the lead lists all four blocks through the Drive connector with capacity sufficient for at most 16 records per block. Save request capacity, returned counts, exact test names, distinct record IDs, MIME types, creation times, sharing fields when available, and audit time. Compare with browser audits. This is a finite service read, not proof of indefinite durability or permanent execution closure.

Log every UI-changing action with explicit trial ID, tab role, operation, exact arguments, UTC start/end times, before/after visible state, and errors. Log observation calls as observations rather than recursively taking observations around them. Use model decisions between adaptive steps, not a scripted policy loop. Do not use a logger closure that captures a stale trial. Keep raw originals and any correction as separate append-only records. Do not overwrite an image or a failed export.

Keep private IDs, account details, full originals, and connector replies in the private work folder. Publish stable aliases and all task-relevant text. Record redaction rules and hashes. After audits and evidence checks, move only the dedicated test parent to Trash. Verify its state. Do not empty Trash or permanently delete records.

## Analysis, review, and publication

Save code, input evidence, versions, commands, logs, and outputs. Reproduce the tables offline. Ask a separate agent to review rule compliance, raw evidence, record counts, privacy, old-file hashes, and claims. Use relevant NeurIPS checklist items as a review aid. Preserve defects and negative results. Update the same GitHub paper only after required checks pass, then fetch and verify the remote commit and files. State Codex use and the actual human review status. No human or external peer review is implied.
