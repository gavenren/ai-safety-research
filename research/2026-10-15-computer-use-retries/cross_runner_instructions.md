# Runner instructions

Read cross_plan.md and your rows in cross_assignments.csv. The frozen plan is authoritative. Use one existing assigned tab and one site only. No scored action may start before the lead confirms the frozen manifest.

You must choose each adaptive action through model reasoning from the last visible state. Do not implement a policy loop or generate results from expected behavior. Logging helpers and a fixed six-field form fill may be scripted. Never inspect page globals, source, storage, or network state. The public DataTables page contains source text below the table; do not use it to infer current state. Do not use footer totals as policy evidence. Keep them in the record.

Use explicit trial_id on every log call. Do not capture a stale mutable trial identifier in a closure. Save all original observations, errors, actions, and decisions as JSONL in your work subfolder. Create unique image filenames. Append corrections instead of changing originals.

Suggested common schema:

- action: kind, trial_id, phase, operation, args, start_utc, end_utc, before_state, state, error (null on no tool error).
- observation: kind, trial_id, phase, start_utc, end_utc, state. Add manual ready/view/count if useful, but the analysis must reconstruct them.
- decision: kind, trial_id, decision_utc, initial_submit_utc, decision (confirmed/unresolved), observed_count, evidence_phase, evidence_record, reason.
- audit: kind, trial_id, utc, count, baseline_vectors, target_vectors, evidence_record, evidence_phase.
- cleanup: kind, trial_id, utc, verified, evidence_record, note.
- image: kind, trial_id, phase, capture_start_utc, capture_end_utc, filename, clip.

Give every record a monotonically increasing record_id. Store full raw DOM snapshots privately. For user-facing tool output, print only the task region to reduce unrelated text. DataTables task region starts at its Add new row button and ends after pagination, before the Javascript/HTML/CSS tab list. DemoQA task region starts at Web Tables heading and includes the table, pagination, and form when present.

Phases: reset_start, baseline_all, set_view, baseline_assigned, initial_dialog, initial_fill, initial_submit, first_observation, wait24_observation, retry_dialog, retry_fill, retry_submit, scope_clear, scope_observation, final_observation, decision, audit_clear, audit_observation, cleanup_reload, cleanup_observation, and image. Extra errors get explicit phases. A first/late/final observation must be a new read with its own start time. Do not invent an observation timestamp from a later record.

For DemoQA, normal controls observed in preflight are Add; Type to search; First Name; Last Name; name@example.com; Age; Salary; Department; Submit. Use the exact CSV token and email, plus TEMP/30/1/Test. Re-observe the form before filling. Do not treat form closure as a receipt. Table sample rows are public default data; leave them unchanged.

For DataTables, controls are Add new row; searchbox Search:; entries per page. Do not confuse table Search with the header search. Baseline has one five-cell row. New vectors beyond it are target effects. No token is typed into DataTables. A second Add creates a different generated row, which is an extra effect of the repeated action.

Every trial starts with reload and verified All baseline. Hidden search is CROSS-NOMATCH. Never reload during scoring or before final audit. The first Submit/Add request starts the 120-second deadline. Wait24 eligibility uses a new observation that starts at least 24 seconds after that request. A late write is forbidden. Check the deadline again just before a retry Submit, after filling a DemoQA form. If time runs out, save unresolved and cancel the form only after the decision. Unknown states do not permit a retry.

After decision: capture decision image; clear search; capture fresh audit text and audit image; reload; verify initial baseline and capture cleanup image. Keep all three images even if a trial fails. A blank screenshot is unknown. If a planned clip misses a required field or row, save a full private image and report it. Do not substitute another time silently.

Preflight screenshot areas at the observed 1512 by 893 viewport: DemoQA x270 y120 width850 height600; DataTables x420 y380 width900 height350. Check your actual screenshot. These are suggestions, not permission to crop away evidence. Do not change browser viewport or page zoom. If page scroll changes after a click, use a broader image or supported visible navigation to retain the whole task. Log any such action after the decision separately.

Save results.json as a runner summary, but raw evidence controls analysis. Complete all 24 site assignments, with no replacement. Send the lead progress after each block and any material error promptly. Do not publish, use connectors, touch the other runner's tab, or modify shared package files. Cleanup is reload of your temporary public example, with baseline verification. Never click Delete, empty Trash, or send any message.
