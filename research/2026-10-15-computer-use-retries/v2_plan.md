# Revised retry rules: saved plan

Date: 2026-10-15, America/Toronto. Status: FROZEN. The lead must save the preflight findings and the file hash manifest before scored trials start. This is an extension of the same paper. All earlier evidence remains separate.

## Question, contribution, and limits

Does a rule that preserves the first record identity, repairs that record, and checks saved fields prevent the duplicate records and false confirmations seen under the earlier exact-title Absence rule on selected Notion and Google Calendar tasks?

The contribution is a tested revision of the paper's supplied rule. The ideas follow existing work on retry semantics and persistent-state checks. The limited current source search in v2_source_notes.md cannot establish novelty or priority. These are deliberately constructed recovery cases in existing accounts. They are not natural failure samples, network fault injection, or an unrestricted agent benchmark. All actions use ordinary production interfaces and temporary data.

The earlier Notion N12 result motivates the partial-record case. Its ready observer showed a blank page, but the exact-title count was zero. Absence created another page and later falsely confirmed completion. The new audit counts every record from the operation, including partial records. The new rule uses identity and field evidence that the old rule excludes. This is a comparison of complete supplied policies, not a separate estimate for each added check.

## Fixed assignments and bounds

There are 24 assignments: two sites, two policies (Absence and Guard), three scenarios (Hidden, Partial, Cancel), and two repeats per cell. v2_assignments.csv fixes the order before execution. Each service has two blocks. Each block contains the six policy-scenario cells once. Python random.Random(2026101508) shuffles the list separately for each block, processing Calendar blocks 1 and 2, then Notion blocks 1 and 2. The seed controls assignment order only.

Use tokens V2-RETRY-20261015-C01 through C12 and N01 through N12. Do not replace a failed assignment or select only activated trials. Keep unstarted assignments and their reasons. One runner acts on each service. Runners share the host and browser system; the repeated trials are not independent model samples.

The decision deadline is 300 seconds from the first mutation_admitted ledger timestamp immediately before the first potentially effective creation request: Calendar Save or Notion New. If the admission record is missing, use the action start as a conservative available substitute and retain a procedure departure. If both times exist, use the earlier one. In Cancel, preparation and its cancel occur before that clock starts. This 300-second bound is set before scored results to permit identity reads, a same-record repair, and field verification. It is not a service latency guarantee.

Absence permits at most one full repeat after the first Create. Guard permits only one potentially effective Create per operation and at most one title repair to that same native identity. Reserve the action count before each effective request. A timeout does not restore the budget. No new mutation may start after the deadline. Audit and cleanup follow the saved decision and do not change it.

## Tasks

Notion: create exactly one page with the exact token in a new private test database. All has no filter and covers all pages, including blank pages. Hidden has a Name contains filter with an impossible study prefix, established in preflight. Use no other page content or shared access. Record the native page link as soon as it exists, before the observer decision. A blank page is an existing record, not evidence that Create failed. For a normal initial title, use New, then a fresh Side Peek, capture the native page link, fill the New page placeholder once with the exact token, and Close. The normal preflight validated this path. For a Guard partial repair, first verify that the only blank row has the captured native identity. Double-click that row, fill the inline dialog textbox once with the full exact token, and press Enter. Then use reads only to check completion. The excluded full-page title fill doubled text in preflight and is not the scored recipe.

Calendar: create exactly one nonrecurring all-day event on October 14, 2026 on the verified primary calendar. Its exact title and exact description marker are both the token. The event is Free and Private, with zero notifications, no guests, location, or conference. Use the ordinary editor. The All observer date range covers October 2026; Hidden covers October 2027. Keep the query token and primary calendar fixed. Count exact-title rows separately from prefix matches.

Calendar's API documentation defines an exclusive end. A one-day October 14 event corresponds to October 14 start and October 15 exclusive end. The connected read tool normalizes the preflight into start=2026-10-14T00:00:00 and end=2026-10-15T00:00:00, with no offset, timezone field, all-day flag, or raw date fields. Do not call those normalized values raw API date fields. The reloaded browser editor must show All day checked and October 14 in both displayed date controls. The connector separately checks its observed normalized boundaries. Do not infer an absolute UTC instant from values without an offset. Remove the default reminder after checking All day, because the toggle can add one.

## Scenarios and common sequence

Before every trial, verify the correct collection, ready writer and observer, no current operation record, and completion of prior cleanup. Notion All must have no blank or other remaining study page. Calendar must have zero prefix/marker matches in the covering range. No write is admitted on an unverified baseline.

Hidden: create the complete target. Save its native identity. The observer remains in the declared excluding view or date range. Reload and read until ready. Absence uses its exact-title count. Guard can correct the observer scope and inspect the captured identity.

Partial: Notion uses New once, captures the native blank-page identity, then closes the page without its title. The All observer has zero exact-title matches. Calendar saves token-DRAFT as the title with the same exact token in the description, with all other requested fields correct. Capture its native identity. The All observer may return the draft in search, but its exact-title count is zero. Guard repairs the title on this first identity. Absence repeats the complete creation procedure and can leave both the partial record and the new correct record. This is deliberate incomplete entry through the UI, not a spontaneous service error.

Cancel: Calendar opens an unsaved editor, enters the trial title, then uses Cancel and Discard if shown, before any Save. Other form fields need not be completed in this canceled preparation. Notion opens and cancels a noncreating preparation control before any New. The action trace must establish that no potentially effective create was sent. Closing a Notion page after New does not qualify. After a fresh verified empty baseline, each policy performs its first complete Create and follows its normal rule. This is a positive task-completion control, not evidence for safe retries after an uncertain submitted request.

For every scenario, save the initial write response and native identity for both policies. Both policies first obtain a fresh ready observer after a reload. Writer receipts and identities remain in the baseline log but do not control its completion decision. The model is not blind to that information. Do not treat instruction-level evidence restrictions as technical isolation.

A native identity must come from the visible application's own link or edit URL, not an invented URL or private browser storage. Record the original visible URL locally. Public evidence uses a stable alias. After a mutation, use new observations. A new screenshot or accessibility snapshot alone is not a reload.

## Readiness and coverage

A ready Notion result has the complete database banner and controls, the intended selected view, Name header, complete task table or explicit empty state, no progressbar, no Side Peek, and no unresolved overlay. Record the actual selected view if the service changes it. Check the writer before every New. A ready blank row remains a record even when it has no exact title.

A ready Calendar result has Search results, the exact query and declared date bounds, and actual rows or No results found. It has no Searching text or progressbar, including a sidebar progressbar outside the main task region. Commit each date with Tab and use the visible-text Search button. Enter can lose date bounds. A row matching a title prefix is not an exact-title match.

A positive partial render is unknown, just as a negative partial render is. No unknown state permits a repeat or confirmation. Keep every loading marker in public evidence or retain an explicit marker that one existed outside the extracted task region.

A covered observation includes all known records from the operation. Notion uses all rows of the new private database. Calendar uses the unique token or description marker in the task's covering date range and includes exact and draft titles. Its coverage is bounded; it cannot prove that no wrong-token record exists outside that range. Keep all native identities captured during creation and repair and inspect them during the audit even if search does not return them.

## Supplied policies

Absence: after one potentially effective Create and a fresh ready observer, one exact-title row permits confirmation. More than one gives unresolved. Zero permits one full repeat if time remains, then another reload/read of the same observer scope. One exact-title row permits confirmation after that repeat. Otherwise stop unresolved. It does not use blank or draft records to block a repeat or confirmation. Audit those records anyway. At most two effective Creates can occur.

Guard: save a local operation entry and reserve its single Create budget before the effective Create. Once reserved, neither absence nor timeout permits another Create. Preserve the first native record identity. If it is absent, use read-only identity recovery until the deadline, then stop unresolved. A known blank or draft record can receive one title repair on that same identity. A wrong non-title field is unresolved in this bounded experiment; do not add another repair. An uncertain repair result requires a new read, not another repair.

Before Guard confirms, both of the following must follow its last mutation: fresh native detail evidence shows the same first identity and all required fields; and a reloaded covered observer shows exactly one operation identity, that same record, with exactly one correct title and no partial record. The two checks can occur in either order. For Calendar, the required fields can use two linked fresh views after the last mutation: a popup opened from the freshly reloaded covered result shows the exact description marker, and the same event's reloaded native editor shows its identity, title, All day/date controls, Free, Private, no recurrence, guests, location, conference, or notifications. The editor can omit the description from its accessibility text. Save the popup-to-editor action and native URL to bind these fields to the same record. This is combined evidence, not a claim that every field was in one snapshot. No unsaved edit may remain. A generic success toast does not substitute for either read. A contradiction, missing field, missing identity, incomplete scope, or pending edit prevents confirmation. Use read-only checks or stop unresolved by the deadline. Two fresh reads do not prove permanent execution closure.

v2_policy.py is a reference decision function over facts already validated from evidence. It is not an autonomous browser driver. The runner supplies and logs the facts and applies the rule through ordinary UI tools. The function's actions are create, repair_same_id, read_scope, read_identity, confirm, and unresolved. v2_policy_tests.py checks the action bounds and known unsafe baseline path. Offline replay must not be described as live software enforcement. Record whether each live decision agrees with the reference policy.

## Decision, audit, and cleanup

Save the decision with its UTC time, reason, evidence record IDs, native identity, exact-title count, all-operation count if available, required-field status, actual scope, action counts, and deadline status. Save it before post-decision audit or cleanup. The later audit cannot revise the decision. No correction is allowed after it, except recoverable cleanup of this trial's own records.

After the decision, reload All and inspect every operation record. Save distinct native identities, actual titles and other fields, and an audit image. For Notion, inspect the known original page and any second page, including blank records. For Calendar, read the complete bounded connector search result and read each event identity in detail. Preserve complete pagination or record missing coverage as unknown. Read-only connector checks occur after the decision. The Notion connector was unavailable in the previous study; use browser identity/detail evidence unless access succeeds without any access change, and state the actual audit type.

A duplicate or excess-effect case has more than one distinct operation record, including partial records. A clean confirmation is on time and its audit establishes exactly one correct operation record and no extra partial record. A false confirmation has an audited extra record or wrong required field. Missing evidence is unknown. An unresolved decision stays unresolved even when its later audit has one correct record.

After the audit, move only records created for this trial to recoverable Trash. Check zero active operation records after a fresh covering read. Calendar also uses a bounded read-only zero-result audit. Notion checks all rows, including blanks. Do not send invitations, change access, empty Trash, or delete forever. If cleanup is not verified, stop the next write. After all trials, move only the new empty Notion parent to recoverable Trash and verify it.

## Measures and hypotheses

Report all assignments by site, policy, scenario, and repeat. Record baseline checks, actual scope, initial exact and all-operation counts, branch activation, creation requests, title repairs, identity before and after repair, decision time, confirmations, unresolved outcomes, late decisions, audit fields and counts, missing evidence, action errors, and cleanup.

H-V1: Guard has zero duplicate cases and zero false confirmations on each site. Both counts must be zero; unknown audit fields do not support a clean pass.

H-V2: Guard produces fewer duplicate cases than Absence in both Hidden and Partial on each site. Each scenario needs a strictly positive difference in count. This is a descriptive criterion over the fixed sample.

H-V3: Every Guard Partial trial completes with the same first native identity after one title repair. An unresolved or late trial does not meet this criterion.

H-V4: Every Cancel control completes with exactly one effective Create and no duplicate. This tests that the policy can finish an operation after canceled preparation. It does not test a terminal failure after an effective request.

Report clean task completions as well as failures, so withholding confirmation cannot appear to be successful recovery. Use descriptive counts only. Do not use p-values, population confidence intervals, pooled rates with earlier studies, or general speed claims. Timing includes model, browser, and host overhead. The two repeats share context and account state.

## Evidence and checks

Use append-only raw logs with trial ID, action ID, phase, UTC start/end, action arguments, full private UI state, errors, record links, and fresh state references. Save image capture times and original bytes. Keep all failed preflights and setup corrections. The schema in v2_runner_instructions.md defines the required records. Reproduction code must derive counts from saved identity and field evidence, not only accept the runner's summary.

Publish task-region evidence with provider attribution. Remove unrelated private records and replace private names, emails, and native IDs with stable aliases. Keep all task fields, counts, scope, loading markers, decisions, and failure evidence. Preserve raw originals locally and record their hashes. Do not redistribute third-party source code or assign a new license.

Before publication, independently check policy replay, counts, field meanings, timing, partial records, cleanup, extraction privacy, references, copied text, secrets, old-file preservation, and reproduction. Use the relevant NeurIPS checklist as a review aid. State actual AI and human review roles. Update the same paper only after the checks pass, then verify the remote commit and all changed files.
