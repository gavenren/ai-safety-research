# Runner instructions: two-tab Drive retry trials

Read `trigger_plan.md` and your rows in `trigger_assignments.csv`. The plan is authoritative. Agent A runs blocks 1 and 2; agent B runs blocks 3 and 4. Use the private block URLs supplied by the lead. Use two tabs only: writer and observer. Do not use connectors during trials.

## Prepare each trial

1. Set an explicit trial context containing trial ID, runner, block, rule, view, and token. Pass it to each logger call. Do not close over a stale variable.
2. Open the same assigned block in both tabs. Writer uses All. Observer uses the assigned All or Documents view. Do not mix block URLs.
3. Verify a usable baseline and exact-token absence in both tabs. The observer must show its filter explicitly. Ready means New is enabled, the filter state is explicit, and Item List is readable, No matching results is explicit, or an empty All block shows Drop files here with No filters applied. Loading and blank containers are unknown.
4. Save baseline observations and their UTC times. If a usable baseline cannot be verified, do not create. Record the failed or unstarted assignment. Do not replace it.

## Submit and observe

5. Through the writer, use New, New folder, the exact token, and Create. Record the first Create request time as t0. The deadline is t0 + 120 seconds. Capture before/after state, exact action arguments, and any error. Save writer feedback, including Working or an exact-name success receipt.
6. Reload the observer. Read until ready or the deadline. Use the ready state as the first decision observation. Do not add a discretionary wait. Never call a loading state zero. Do not restore a filter if the site changes it during this phase; record the actual view.
7. Count only exact-token folder rows inside Item List. Ignore input text, toast text, breadcrumbs, and focused-row echoes. Two or more matching rows always require an unresolved stop.

## Apply the assigned rule

- **Absence:** one row confirms. Ready zero permits one repeated creation through the writer. Then reload the observer and get a ready state. One confirms; zero, two or more, or timeout means unresolved.
- **Wait24:** one row confirms. After ready zero, wait until elapsed time is at least 24 seconds, then start a new observer reload and obtain a new ready state. A read started before 24 seconds is not eligible merely because it ends later. One confirms. A new ready zero permits one repeated creation. Then reload and read the observer once it is ready. One confirms; otherwise unresolved. Do not wait another 24 seconds when the first check already occurred after 24 seconds, but still perform the new reload/read.
- **Scope:** one row confirms. Ready zero in Documents requires removing Documents in the observer, reloading, and reading ready All. One confirms; otherwise unresolved. A ready zero already in All is unresolved. **Scope never retries.**
- **Receipt:** perform the common observer check first. One row confirms. Ready zero can still confirm from the current exact-token writer success receipt. If no such receipt was saved, take one fresh writer read. If it has the exact current-token positive receipt, confirm; otherwise unresolved. Generic Working or success is insufficient. Never retry or change the filter.

The three core rules cannot confirm from writer rows or receipts. Preserve that writer evidence in the log. A tool error alone does not permit another write. Unknown observations do not permit a retry. At most two Create requests may occur in a trial. Do not send a new write after the deadline. No later state can make a late decision on time.

## Record decision and audit

8. Save the explicit decision first: trial, UTC time, confirmed/unresolved, evidence source, observer count, actual filter, retry count, and reason. Include every error or plan deviation. Do not revise this decision from later audit evidence.
9. Save a clipped decision image with a unique immutable filename. The planned clip is x=260, y=70, width=1190, height=620. Confirm that it shows required rows/filter and excludes private account chrome. If it cannot do so, retain a full private original and report the issue.
10. After the decision, set observer All, reload, and obtain a usable list. Save all exact-token matching rows, count, and a separate audit image. Do not make a repair write. Keep all originals, including failed reads and images.
11. Continue to the next assigned trial. Do not omit, replace, or repeat a completed trial. Tell the lead when all assignments are done. Only the lead performs the later connector audit and recoverable cleanup.

## Log format and limits

Each action record must have explicit trial ID, block, rule, assigned view, token, tab role, operation, exact arguments, UTC start/end time, before/after visible text, and error if any. Observation records contain the observation method, arguments, time, tab role, and complete returned text. Decision records are separate. Keep counts and annotations separate from raw returned text. If a mistake occurs, add a correction with exact affected record ranges; do not rewrite the raw log.

Use JSONL with these exact common keys: `type`, `trial_id`, `token`, `block`, `runner`, `tab_role` (`writer` or `observer`), `phase`, `before_utc`, `after_utc`, and `state`. Action records add `action`, `args`, and `error` when applicable. Save before/after snapshots in separate linked observations or `before_state` and `after_state`. Use the phase names `baseline_writer`, `baseline_observer`, `initial_create`, `writer_receipt`, `first_observer`, `wait24_observer`, `broaden_scope`, `scope_observer`, `retry_create`, `final_observer`, `decision`, `audit_pre_reload`, and `audit_post_reload`. Extra steps need explicit extra phases. Decision records add `decision_utc`, `decision` (`confirmed` or `unresolved`), and `evidence_phase`. For an unstarted assignment, save `status: unstarted`, an unresolved decision, a null initial-submit time, and a reason. Save the complete returned state, not only a runner summary.

Use model decisions between adaptive steps. Deterministic dialog steps grounded in current UI can share a call, but log each action and its arguments. Do not implement the policy in a loop that decides retries. Keep original files private. Do not publish account names, email addresses, private IDs, live private links, or storage totals. Do not change unrelated files, permissions, account settings, or sharing. Do not delete the test collection yourself.
