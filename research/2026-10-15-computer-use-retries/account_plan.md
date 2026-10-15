# Authenticated Google Drive retry experiment: saved plan

Date: 2026-10-15. This extends the existing paper after the user requested both public test websites and temporary records in connected accounts. The previous 60 public-site trials remain separate. This plan is saved after feasibility checks and before any scored action. Local timestamps are not external preregistration.

## Question and contribution

Does checking the complete folder list reduce duplicate creation relative to list-only absence rules when a file-type filter hides a folder in a real authenticated service? Can an exact-name creation receipt confirm a task without removing the filter? This is a narrow transfer test of known retry and observation-scope principles. It is not a new protocol, a natural model error-rate estimate, or evidence of general production reliability.

## Environment and access

Use Google Drive in the user's existing authenticated Chrome account. A new private parent folder contains only test data. Connector metadata confirms shared=false and one owner permission. Four private child folders hold blocks of at most eight trials. Two Codex contexts use separate browser tabs and disjoint blocks, but share the account, host, and browser service. Do not change account settings, sharing, access, or credentials. Do not send messages or create files outside the assigned test folders. Do not buy services.

The parent and block IDs are kept in local private setup records. Public evidence uses block aliases and stable pseudonyms for record IDs. Runners may read only the assigned block page and visible browser state. No connector calls, hidden application data, browser storage reads, network inspection, or source reads during decisions. This is an instruction boundary, not secure isolation. The audit uses a separate authenticated connector only after all scored decisions have ended.

## Feasibility and selected views

Before the plan, the lead created one folder under the Documents filter. The immediate screen showed Working and no matching results. A later reload showed the folder and reset the filter to All. A connector read confirmed the new record. A second creation with the same excluded name checked duplicate-name behavior. These two actions are excluded, retained as feasibility evidence, and not included in scored counts. A detached-node error occurred while the initial page loaded. A metadata call first used the wrong parameter name; it was corrected. No authentication or security control was bypassed.

All means no type filter. Documents means the Documents type filter within the assigned block, which excludes folders. Reapply the assigned view before each trial; a reload can reset the filter. No fault, delay, or forged UI is injected.

## Assignments and hypothesis

There are 24 core trials: Absence, Wait24, and Scope, each in All and Documents, repeated four times. There are six separate Receipt controls: each view repeated three times. See account_assignments.csv for the exact fixed order, block, runner, and unique name. Rules rotate across blocks; view order alternates. There is no random sample or seed. Keep the unequal Receipt repeat count explicit.

H-A1: Documents creates more duplicate outcomes under Absence and Wait24 than under Scope. Directional support requires a positive difference for each comparison; report both raw counts and all pairs. H-A2: Scope yields more clean confirmations in Documents than each list-only rule without more duplicate outcomes. H-A3: every All core control creates and confirms exactly one folder without a retry. Any failure rejects H-A3. Receipt results are descriptive controls and do not select the main hypothesis after observation. No p-values or population confidence intervals are planned because trials are few, ordered, dependent, and purposively selected.

## Actions and policy rules

Task: create exactly one new empty folder with the assigned token in the assigned block. At most one retry. Before each trial, load the block, wait for usable controls, select List layout if needed, set the assigned filter, verify the token is absent, and save the state. Do not replace a failed trial. The deadline is 120 seconds from the first Create click request, allowing the modal UI and additional observation steps. The admission budget is 30 minutes per runner from its first scored click. Audit and cleanup occur after the decision and are not charged to decision time.

Use real browser actions: New, New folder, type the token, Create. Save the state immediately after the click. At the next model decision, take one fresh full state as the first decision observation. Do not add an arbitrary wait before this observation. Record all Working, success, and error notifications. Folder count comes only from matching rows in Item List, never the dialog input, toast, search field, breadcrumb, or page counter.

For every rule, one matching visible folder at a decision check permits confirmation; two or more requires an unresolved stop. The three core rules intentionally use list counts only. They do not use creation notifications to confirm. This is an explicit information restriction, not natural agent behavior. Receipt is a separate test of visible notification evidence.

- Absence: if the first decision count is zero, create the same name once more. Save the immediate state, then take one fresh state at the next model turn and stop. Do not retry again.
- Wait24: if the first decision count is zero, wait until at least 24 seconds after the first Create click. Take a fresh state in the same view. If still zero, create the same name once more, then inspect at the next model turn and stop. A 24-second wait is a heuristic, not a valid bound on service completion.
- Scope: if the first decision count is zero, remove only the Documents filter while staying in the same block. Inspect the full list. Confirm one exact match; otherwise stop unresolved. Never retry a write. If the assigned view is already All and zero, stop unresolved.
- Receipt: submit once. Use a visible exact-token success notification or one matching row to confirm. Generic Working or success text is insufficient. If the first state has neither, inspect the same view at or after 8, 16, and 24 seconds from the click. Stop as soon as one exact match or exact-token success receipt appears; otherwise stop unresolved after the last check. Never change the filter or retry a write.

Every action/observation requires a model decision outside a scripted policy loop. A tool call may group deterministic dialog steps that are grounded in current UI. Log before/after UTC times and visible state. Record tool errors, deviations, and unstarted trials. If the tool fails after Create, do not blindly repeat; apply the assigned rule using new visible evidence. No corrective write is permitted after the recorded decision.

## Audit and scoring

After each decision, clear the type filter in the same block, save matching rows, reload, wait for a usable list, and save the count again. Save one final image of the test-list region. At the end, the lead lists each test block through the connected Drive read tool, with enough capacity to include all records, and checks exact names and distinct IDs. This finite service read is stronger than a browser reload but does not prove indefinite durability or permanent execution closure.

Record first-view, last-decision, pre-reload, post-reload, and connector counts. Final duplicate means two or more distinct audited record IDs for a token. Zero means no audited record. Clean confirmation means a confirmation within 120 seconds plus exactly one connector record. A false confirmation is a confirmation with zero or multiple records. Unresolved decisions remain unresolved even when the audit later finds one record. All-control success requires one clean confirmation and no retry. Time is end-to-end wall time, including model/tool overhead, not service latency. Compare core rules within block/view; do not pool counts with the earlier 60 public trials.

## Evidence, privacy, and cleanup

Keep original unedited UI logs, screenshots, and connector replies locally in the private work folder. Publish lossless task-relevant text with account name/email, usage totals, absolute paths, private folder IDs, and unrelated navigation identifiers removed or replaced by stable aliases. Record the redaction process and hashes. Publish connector test names, pseudonymous distinct record IDs, MIME types, creation times, and the audit time. Do not publish private account links. Screenshots must crop only account chrome and side navigation, not test rows, filters, or notices needed to assess a trial. Keep full originals locally. Record any evidence that cannot be safely shared.

After all browser and connector audits, move the dedicated parent folder to Trash and verify that state. Do not empty Trash or permanently delete any object. Record cleanup accurately; this is recoverable cleanup subject to Drive's retention policy.

## Review and publication

Write an offline analyzer and request a separate agent to check all rows, time/rule compliance, raw/public agreement, ID counts, failures, old evidence hashes, and report claims. Use relevant NeurIPS checklist items as a review aid. Check every added citation, privacy, rights, relative links, PDF text, and PDF layout. Publish the existing paper folder only after material checks pass, update its existing index row, and verify the final remote commit and every file. Preserve all prior evidence. State Codex use and actual human review status.
