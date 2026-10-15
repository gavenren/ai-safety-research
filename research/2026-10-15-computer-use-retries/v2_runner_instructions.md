# Runner instructions and evidence schema

Status: FROZEN. Do not run scored trials before the lead confirms the saved file hash manifest. Read v2_plan.md and your fixed rows in v2_assignments.csv. Do not change assignments after results. The saved plan governs the experiment.

Use one JSON object per line. Preserve full private UI states locally. Every action or observation needs trial_id, record_id, phase, started_at_utc, ended_at_utc, kind, label, arguments, result or state, and error (null if absent). Record a pending mutation before the potentially effective call. A tool timeout must remain in the log. Do not replace it with a later successful read.

Phases: baseline, preparation, initial_create, initial_observation, recovery, verification, decision, audit, cleanup. Preflights use separate IDs and cannot enter the scored sample.

The trial start record contains service, policy, scenario, repeat, token, target collection alias, expected fields, deadline_seconds=300, create_admitted=0, repair_admitted=false, and current time. The baseline cites ready writer/observer record IDs, exact scope, zero task records, and prior cleanup evidence.

For every effective Create, write a mutation_admitted record before the call with mutation_kind=create, sequential admitted count, operation token, and target. Calendar Save and Notion New are effective. An uncertain response still consumes that count. The first such admission establishes the decision clock. Use the earlier of its timestamp and the effective action start. If the admission is missing, use the action start and retain the missing-admission departure. For Cancel, save the preparation and cancel evidence separately. No Save or New can occur in that canceled preparation.

A native_identity record contains the full private native link or edit URL, its source state ID, captured_at_utc, and record role (first or repeated). Keep it before the observer decision for both policies. The Absence runner retains it but does not use it to change its title-count rule.

For an observer read, save observation_ready, observation_fresh, actual scope and query, exact_title_count, all_operation_count when established, actual record titles and links, any blank/draft rows, and every readiness marker. A fresh read requires a reload after the latest mutation. Save both the reload and complete result. Unknown counts are null. A partial rendering with a positive row is still unknown.

For a Guard repair, reserve repair_admitted=true before the title mutation. Its mutation_kind is repair_title. Include the first native ID and current edit URL. Set the full exact title once. Do not make another record. One repair is permitted. If the response is uncertain, inspect the same ID again; do not repeat the repair. Do not repair a wrong non-title field in scored trials.

Before each policy decision, save a policy_facts object with these fields:

```
policy: Absence | Guard
deadline_expired: boolean
baseline_verified_empty: boolean
create_admitted: integer
observation_ready: boolean
observation_fresh: boolean
exact_title_count: integer | null
native_id: string | null
detail_fresh: boolean
fields_match: true | false | null
title_only_repair: boolean
repair_admitted: boolean
edit_pending: boolean
scope_covered: boolean
coverage_fresh: boolean
operation_ids: array of distinct native IDs | null
```

Missing evidence must remain false or null. fields_match=true requires all required fields. detail_fresh=true requires a native-detail reload after the latest mutation. For Calendar, cite the linked fresh popup for the description marker and the same event's reloaded editor for other fields, as allowed by the plan. Save all source state IDs and the binding edit action/URL. coverage_fresh=true requires a covered observer reload after that mutation. operation_ids is the complete known set in the covered task scope, including partial records. A native link without a field read cannot establish fields_match. Do not let later audit facts enter an earlier decision.

The reference function accepts these facts as a JSON object on stdin. Example command: python3 v2_policy.py < facts.json. It emits action and reason. This is a reference check, not automatic browser control. Log its output if used live; otherwise label later comparison as offline replay. read_scope means read the current assigned scope for Absence, and obtain sufficient covering scope for Guard when the facts require it. The runner must ground each UI action in the current page.

For a terminal decision, record decision=confirm or unresolved, decided_at_utc, elapsed_seconds, reference action/reason if evaluated, evidence IDs for the final observer and native detail, exact count, known all-operation count, fields status, create and repair counts, and current native ID. Save it before images, audit, or cleanup. A late decision remains late.

The audit record includes audit_started_at_utc and audit_ended_at_utc, method, scope, full query and capacity/pagination, all operation IDs, title and fields for each, original identity still present, correct target count, partial count, total count, and missing data. Keep raw service replies before cleanup. For Calendar, the audit end is after the last detailed event read, not only the list call. Browser All-day evidence and normalized connector boundaries are separate fields.

The cleanup record includes each exact removed identity, Trash action evidence, the later ready covering zero state, and connector zero when available. A phase label alone does not establish readiness. Preserve any earlier still-loading or nonzero cleanup state. Stop the next write until a later valid zero is saved. Do not empty Trash.

Save three task-region images per trial if the tool produces valid crops: decision, audit, and final cleanup. Keep image bytes, own capture times, state IDs, and hashes. Do not claim an audit image proves an earlier decision. Retain defective images and identify their limits. Root handles privacy extraction and publication; do not remove private raw evidence.
