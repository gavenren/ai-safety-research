# Retry rule design review

Date: 2026-10-15. This is a design proposal before the new plan is frozen. It is not a record of completed trials.

## Evidence that the new rule must address

The earlier production study found 9 duplicate cases in 24 trials. In Notion N12, a ready table showed a blank page and zero exact-title rows. The Absence rule sent a second Create. It then confirmed one exact-title row, but the later audit found two distinct pages. A blank page is an effect of the first request. An exact-title count does not describe all effects. N03 also showed that ready controls and a fresh reload do not ensure that every new page is visible.

The earlier Calendar study could establish distinct record counts, but not strict time-field correctness. The editor used a historical date with a displayed offset that differed from the search and API offset. Use a one-day all-day event to remove that specific interpretation problem. For October 14, 2026, the native API represents a start date of 2026-10-14 and an exclusive end date of 2026-10-15. The connected read tool does not expose these raw keys. Its preflight response uses start=2026-10-14T00:00:00 and end=2026-10-15T00:00:00 with no offset or all-day flag. The reloaded browser editor must separately show All day checked and October 14 in both displayed date controls. This does not prove all other fields by itself.

## Revised rule: Identity guard

An operation is one requested task. A record identity is the native page or event ID, not its title. A pending action is a request that might have created an effect, even when its response failed or its record is not yet visible.

1. Before the first potentially effective action, save the operation token, target collection, desired fields, known record identities, and action status in the local append-only log. Reserve the one-create budget before the action starts. Do not restore that budget after a timeout or an empty search.
2. A known pre-submit cancel can leave the budget unused only if the action trace shows that no effective New or Save was sent. A canceled Calendar editor is such a candidate. Notion New creates a page, so closing the resulting page is not a pre-submit cancel. A Notion control must stop before New, for example by canceling a noncreating template menu. Call this a canceled preparation control, not a simulated network fault.
3. After a potentially effective Create, never send a second Create for that operation. A zero count, a title mismatch, a timeout, or an expired local deadline does not remove this restriction. If no identity can be recovered, use read-only checks and stop unresolved at the bound.
4. Capture a native record identity as soon as it is available. For a blank or partial record, open that same record and set the missing required values. Do not use a new record as a substitute. The repair is one bounded full-value update to an existing ID. If the update response is uncertain, read the same ID again before any further action.
5. Before a confirmation, reload a view that covers the operation, inspect all new task records including blank or draft records, and reload the native record detail. The identity must agree with the captured first identity. All required fields must match the task. A generic toast, a row title, or a typed but unsaved value is not enough. The two checks can occur in either order if both follow the last mutation and no later mutation occurs before the decision.
6. A contradictory identity, extra task record, missing field, incomplete view, open unsaved editor, or unresolved mutation makes the decision unresolved. Save the decision before a separate audit.

This rule prevents the runner from issuing a second Create after an uncertain effective Create. It does not impose server-side deduplication. One UI action could still have an undocumented service effect. A local operation token is not a server idempotency key. A native record link establishes which record to inspect; it does not establish that the fields are correct or that all writes have finished.

## Candidate live design

Use 24 trials: two services, two supplied rules, three scenarios, and two repeats in each cell. Keep one runner per service and block the order by repeat. Shuffle each six-case block using one saved seed. No failed assignment is replaced. Use a new private Notion database and unique Calendar tokens. No new access, invitations, payments, or permanent deletion.

The baseline is the old Absence rule. After a ready exact-title zero, it sends at most one full Create. After another reload, one exact-title row permits confirmation. The baseline intentionally ignores partial records for its decision, but all partial records are preserved for the audit. It is a bounded known-weak comparator, not the expected behavior of an unrestricted agent.

| Scenario | Notion setup | Calendar setup | What it tests |
|---|---|---|---|
| Hidden | Create a complete titled page; the observer uses the existing normal exclusion filter. | Create a complete event; the observer uses a date range that excludes the task day. | Scope correction and refusal to repeat a pending operation. |
| Partial | Use New once, capture the native blank-page link, and close without a title. Observer All has no exact-title row. | Save a draft-title event, token plus -DRAFT, with a shared operation marker in its description. Observer uses the covering range but exact-title count is zero. | Recovery of the first effect; all operation records count, including blank or draft records. |
| Canceled preparation | Open and cancel a control that cannot create a page; never invoke New until the rule permits the first create. | Prepare an event and cancel before Save. | The guard can finish a task when the action trace establishes that no effective create was sent. |

The Calendar draft is preferable to an unmarked untitled event because it permits bounded read-only audits with strong ownership evidence. It is deliberately different from the Notion blank-page setup. Do not combine the sites into a claim about identical fault mechanisms. A title-plus-DRAFT record must not be counted as an exact-title match by the baseline, even if Calendar's text search returns it. The audit must use the shared operation marker or a broad unique token and include both exact and draft titles.

Before freeze, preflight the native identity and detail-edit paths. For Calendar, check the reloaded all-day browser fields and the separate normalized connector boundaries. Do not infer unavailable raw API keys or an absolute UTC instant. For Notion, prove that the blank page has a native link and can receive its title without a new page. Prove the canceled-preparation control leaves zero effective creates. If a path fails, retain that preflight and revise before freeze.

## Measures and decision criteria

Count all native identities attributed to the operation, not only exact-title matches. Keep separate counts for correct target records, incomplete records, and all operation records. An excess-effect case has more than one operation record. A false confirmation is a completion claim followed by an audit that establishes an excess effect or wrong required fields. An unknown field is unknown, not a pass or a false claim.

For each site and scenario, report assignments, effective creates, repairs to an existing ID, IDs before and after repair, strict ready-state gates, confirmations, unresolved decisions, false confirmations, audit counts and fields, and cleanup. Compare all assigned trials. Do not select only cases in which a branch activated.

Proposed strict criteria: the guard has zero excess-effect cases and zero false confirmations in the sample; every guard Partial trial repairs the same captured record ID; every guard canceled-preparation trial completes after exactly one effective create; and guard Hidden trials change scope without another create. A failed criterion remains a result. State the number of clean completions as well as safety failures, so refusal to act cannot be mistaken for recovery success.

Time includes model and host overhead. Use descriptive counts, not population intervals or p-values. The two policy groups differ in their allowed evidence and recovery actions. The design tests the whole policy, not the separate causal value of each gate. The cases are deliberately constructed through ordinary UI actions; they are not natural service failures, injected network faults, or a natural production error-rate sample. Neither finite reads nor a successful audit prove permanent execution closure or indefinite durability.

## Review cautions

- Preserve all loading markers, even those outside the normal task-region extraction. A ready result cannot be inferred from the absence of a marker that the privacy extractor removed.
- Preserve actual selected views after service changes. Check the writer immediately before every effective action.
- Write the decision before audit. Do not fix a failed decision with later evidence.
- Treat the Calendar description marker as a required audit ownership field. Do not expose account IDs or event URLs that encode an email in public logs.
- State that data are temporary and cleanup is recoverable. Do not empty Trash.
- Do not claim a new retry protocol. The contribution is a tested revision of the paper's controller on selected real account workflows.
