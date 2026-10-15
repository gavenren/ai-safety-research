# Additional website retry test: saved plan

Date: 2026-10-15. This extends the existing computer-use paper. Earlier studies remain separate. Freeze this plan, assignments, and runner instructions before any scored write. Local timestamps and hashes are not external preregistration.

## Question and contribution

Do the supplied Absence, Wait24, and Scope rules produce different extra effects when a native search field hides new rows on two additional public websites? The sites are DemoQA Web Tables (https://demoqa.com/webtables) and the official DataTables Add rows example (https://datatables.net/examples/core/api/add_row.html). They are actual hosted demonstrations from different providers. They are not authenticated production services. This is a selected replication of a known scope mechanism, not a new retry protocol or a general model improvement.

The websites were selected after excluded feasibility checks. The source record states search terms, related work, versions, and read limits. The first DataTables later read was at 19.606 seconds, so it did not meet the 24-second feasibility gate. A separate second preflight verified the gate at 36.318 seconds before freeze. All feasibility evidence and failed checks remain available.

## Design and admission

Run 48 fixed assignments: two sites, three rules, All/Hidden views, and four repeats per cell. Each site has four blocks of six assignments. A fixed Python random.Random(20261016) shuffles the initial ordered list of (Absence, All), (Absence, Hidden), (Wait24, All), (Wait24, Hidden), (Scope, All), (Scope, Hidden) separately for each block, processing DemoQA then DataTables. The saved CSV controls execution order. The seed controls order only, not model sampling or independent site selection.

One separate Codex runner owns each site and its own browser tab. Both share the host and browser service. Each trial starts from a verified reload baseline. Use only normal browser controls, visible page text, and screenshots. No connector, internal app data, network inspection, browser-storage read, page-script execution, or mutation through code is permitted for scored actions. Public documentation visible on the page may be present in saved observations; it is not used to infer the current row count.

Run all assignments in order. Never replace a failed or missing trial, add a trial to obtain a branch, or remove a control failure. Stop writes if there is an access or safety problem. Save unstarted assignments with their reason. No login, signup, payment, message, permission change, or existing account record is needed.

## Task, rows, and baseline

DemoQA: create exactly one row with First Name equal to its unique token (CROSS-Q01-20261015 through CROSS-Q24-20261015), Last Name TEMP, Email retry-qNN@example.com, Age 30, Salary 1, and Department Test. The address is synthetic and uses the reserved example.com domain. Repeat all six values unchanged if a rule permits a retry. The exact first name identifies target rows; count only actual table rows, never an input or label. A duplicate is at least two target rows.

DataTables: add exactly one new row to the fresh example. The UI generates labels, so there is no user-entered token. Save all baseline row vectors. A new row is one whose complete five-cell vector was absent from baseline. A repeated Add creates another generated row. This is an extra effect, not an identical-data duplicate. Trial IDs CROSS-D01 through CROSS-D24 identify local evidence, not a site field. A fresh baseline must be the initial one-row example. Do not infer success from a counter name alone; compare actual visible rows.

Start with an enabled Add action, empty search, visible complete table, and all default rows: DemoQA has the three documented example rows, and DataTables has its initial 1.1 through 1.5 row. Save the All baseline and verify no target/new row. Set All to empty search or Hidden to CROSS-NOMATCH. Save the assigned baseline. Do not reapply a filter after the initial write if the site changes it.

A ready DemoQA view has the Web Tables heading, enabled Add, the current search field, a table with all seven headers, no open form, and pagination with disabled Next. Zero is allowed only when this complete table has no target row. The empty filtered preflight uses Page 1 of 0. A ready DataTables view has Add new row, current table Search, all five headers, and either complete visible rows or No matching records found, with disabled Next. Missing controls, loading, read errors, open forms, or ambiguous pages are unknown, not zero.

Use one tab per site. A fresh observation is a new browser read, not a reload. Reload erases these examples' temporary state and is forbidden between the first write and final audit. This differs from the Drive study. It does not establish server persistence or execution closure.

## Supplied rules and deadline

The first Submit (DemoQA) or Add new row (DataTables) request starts a 120-second deadline. Routine opening and filling of a form precede Submit. Save the request start and end, exact arguments, errors, and subsequent ready observation. A tool error does not mean a committed write. Do not blindly resend an error.

The three rules use newly visible target rows only. DataTables also exposes total-entry counts in its footer. The model can see these counts but the supplied rules do not use them to confirm or cancel a retry. This deliberate information restriction must be stated in the report. It is not an unconstrained agent test or a claim that the whole screen lacks evidence.

On the first ready view, one new target row permits confirmation; two or more require unresolved stop. Ready zero follows the assigned rule. Unknown does not authorize a repeat. Obtain a fresh read if needed, within the deadline.

- Absence: after ready zero, repeat the same complete write once. Read the same actual view. Confirm one target row; otherwise stop unresolved. No second retry.
- Wait24: after ready zero, wait until at least 24 seconds after the first request. Start a new observation at or after that time. If it shows one target row, confirm; if two or more, stop unresolved; if zero and time remains, repeat once. Read the same view and confirm only one. The 24 seconds are a heuristic, not a service guarantee. Do not reload. If the first zero arrives after 24 seconds, still take a new read before deciding.
- Scope: after ready zero with Hidden active, clear only search. Read the complete All view. Confirm one target row; otherwise stop unresolved. If the first ready zero is already All, stop unresolved. Never repeat the write.

No new write may start after 120 seconds. Stop unresolved at the deadline. Save the decision time, evidence record, count, and reason before taking images or audit actions. A late claim is not clean. No correction after decision can change its score.

Receipt is not included: neither selected task has an established positive receipt tied to an exact current request or record. Form closure and a generic page response do not substitute for the earlier Receipt rule. Report this capability limit rather than inventing receipt trials.

## Audit, cleanup, and evidence

After saving the decision, save its screenshot with capture times. Clear search and read the full table without reloading. Save the final audit count, every relevant row vector, and a separate screenshot. This is the primary outcome. A DataTables audit compares row vectors with baseline. A DemoQA audit counts exact tokens. Verify disabled Next so the complete relevant list is in view.

Then reload and verify the initial default rows and empty search. Save a cleanup record and screenshot. Post-reload zero is expected cleanup, not an experimental write failure. Do not pool pre-reload effects with post-reload state. If reset fails, preserve the state and stop further trials until the reason is known. Do not use Delete or clear browser storage as a substitute. No permanent deletion or account data change is needed.

Log each UI action with explicit current trial ID, operation, arguments, phase, UTC start/end, error, and before/after visible states. Observation calls have their own times and state. Each decision and audit points to its evidence record. Every trial has three images: decision, audit, and cleanup. Use a fresh filename and never overwrite. A later image cannot replace an earlier decision text. All actions that depend on new state require a model decision; no scripted policy loop is permitted. A helper can log and execute a chosen action, or fill a known form in one fixed batch.

Save full originals locally. Publish the task region of each observation, with an explicit extraction rule and source hashes. Remove unrelated navigation, page source examples, local absolute paths, and private account data if any appears. Preserve every task field, search value, row, status, error, time, and correction. Synthetic example.com addresses and public default sample records may remain. Images must show the site/task context, search, rows, and pagination without private account controls. Document actual byte format. Attribute provider UI; do not assign a new license.

## Measures, hypotheses, and interpretation

Primary counts use all 48 assignments, grouped by site, rule, and assigned view. Record started/failed/unstarted assignments, baseline status, first ready count, actual view, repeat requests and tool outcomes, rule activation, decision time, audit effects, cleanup, and deviations.

An extra-effect outcome has at least two new task rows before cleanup. A correct confirmation is on time with exactly one new row in the audit. A false confirmation has a count other than one. Unresolved remains unresolved even when audit later shows one. A missing audit is unknown, not zero. Never use cleanup zero to score a decision.

H-X1, separately for each site: each retry rule has more Hidden extra-effect cases than Scope. H-X2: Scope has more correct Hidden confirmations than each retry rule, with no extra-effect cases. H-X3: all 12 All controls per site cleanly confirm one new row with no retry. A single failure rejects that strict control. Report all failures.

An activation gate is separate: each site must show an actual Hidden Absence retry, an eligible Hidden Wait24 retry, and a Scope clear-search branch after Hidden zero. Missing activation is untested; it cannot cause extra trials or replacements. Receipt remains unavailable.

These are small selected deterministic tasks, repeated in shared contexts. Counts are descriptive. Do not present confidence intervals, significance, natural website rates, a general speed gain, server durability, a hidden network fault, or secure information isolation. Site differences in record identity and storage remain explicit. Earlier experiments are not pooled.

## Review and publication

Reconstruct results offline from saved states and action times. Keep code, versions, commands, outputs, all failures, and image hashes. Ask a separate agent to check the plan, logs, policies, counts, claims, rights, privacy, and images. Use relevant NeurIPS checklist items as a review aid. Preserve prior evidence. Update the same paper only when checks pass. Fetch the remote commit and verify every file. Disclose Codex use and the actual absence of human or external peer review.
