# Method review: temporary account records

Date: 2026-10-15. This is design advice. It is not an outcome review. No new browser test or external change was made for this review.

The review read the published report, `live_plan.md`, `live_review.md`, and the saved publication state. The prior study has 60 public test-site trials. It remains a separate evidence set. Do not repeat or replace it.

## Proposed bounded test

Use one authenticated account app and one private test collection. A collection can be a task list, table, or folder. Prefer an app that permits the same title on two records, has a clear list filter, and permits removal of the new records. Do not use purchases, sent messages, calendar invitations, public issues, shared project changes, or workflow triggers. Do not change account access settings.

Use 24 assigned trials: three rules, two starting views, and four repeat blocks. The rules are Absence, Wait24, and Scope. One view includes the new active record. The other view excludes it by an ordinary status filter. Use synthetic titles such as `RETRY-ACCOUNT-20261015-A01`. Each trial has a new token. An optional retry uses exactly the same token and fields. At most two submissions are allowed.

Use a cyclic rule order across blocks and alternate which view comes first. Save the full assignment list, exact app, exact filter, test record fields, permitted actions, and outcome measures before the first scored submission. The sample is fixed and not random. Do not replace a failed trial with a new one.

The 24-trial design omits the earlier No retry and Closure arms to limit account changes. It directly compares the three requested rules. Do not claim a new account result for omitted arms. The maximum is 48 trial records, plus a small number of labelled warm-up records. A second app would require a separately saved plan and should not be added after seeing results.

## Feasibility and admission checks

Use one or two separately named warm-up records before scoring. Record each setup attempt and its outcome. Confirm that the app permits duplicate test titles and that one ordinary new record is visible after a new read. Confirm that the creation form can create an active record while the exclusion view stays selected.

Some apps use the selected filter to set default field values. A Completed filter can then create a completed record instead of hiding an active one. Some apps change the view or open the new record after creation. These behaviors can remove the intended empty-list exposure. Do not silently force the view back or ignore the new record. Report the feasibility failure or amend the design before scoring.

Save any success toast, created-record link, or attempt-specific receipt. A receipt can be evidence of success even when the list is empty. If the procedure scores only the selected list and does not use such a receipt, state this restriction in the plan and paper. Do not describe a deliberately ignored success receipt as an unknown commit.

Before each scored trial, verify the assigned view, the create form, and zero exact-token matches in the test collection. Preserve all unrelated records. Use one writer and one app tab for the trial sequence. No fault injection, network interception, source inspection, or hidden storage read is needed.

## Rules and limits

- Absence: submit once and inspect the assigned list. If the exact visible count is zero, submit once more. Inspect the list and stop.
- Wait24: submit once and inspect. If the exact visible count is zero, wait until at least 24 seconds after the initial commit action request. Read the UI again. Retry once only if that fresh count is still zero. Inspect and stop. The delay is a heuristic, not a server guarantee.
- Scope: submit once and inspect. If zero, select the full test-collection view and read it again. Confirm one exact match. Stop with a duplicate result for more than one. Stop unresolved for zero; absence alone does not permit a retry.

The two fixed-view rules must not change the list filter in their decision phase. Scope may change only this evidence scope. All rules must obey app-level validation or confirmation steps. Use real browser actions and a model decision after each relevant observation. Do not substitute a scripted policy loop.

Save a 90-second decision deadline before the first scored trial. This allows the account app's dialogs and navigation. The prior live study used 60 seconds, so do not pool the timing results or imply that deadlines are matched. The clock starts at the initial commit action request, not at typing. Stop trial admission after 25 minutes. Keep late, failed, and unstarted assignments in the result table. Do not make another experimental write after the deadline.

## Audit and server evidence

Freeze the decision before the audit. The audit opens the full test collection, counts exact titles and active state, reloads, and counts again. Count rows or stable record IDs, not search highlights, input fields, or page counters. A duplicate is at least two distinct records for the trial token. A clean confirmation requires an on-time success decision and exactly one active record in the audit. Save zero-record, single-record-unconfirmed, duplicate, late, and interrupted results separately.

When a read-only connector is available, use it after the browser decision to list the exact test collection and match tokens to distinct service record IDs. Keep this audit separate from the browser runner. Follow pagination to exhaustion within the test collection. Record the read time and any limits. The connector must not create or repair a test record.

This can establish agreement with a service-backed read at that time. It does not prove indefinite durability, linearizability, or execution closure. If the connector audit is unavailable, label the result as UI retention only. A reload or second tab in the same browser is not independent proof of server storage. An ordinary documented cloud app alone is not a measurement of its storage contract.

After all trial decisions, use a final finite read of every exact test token before cleanup. This can find a late extra record. Save the interval from each initial write to this read. It is a finite observation window, not a guarantee that no future effect is possible.

## Cleanup

Before testing, create a local manifest for the dedicated test collection, warm-up tokens, and trial tokens. Add the stable record IDs found by each audit. After evidence is saved, remove only records that match this manifest. An uncertain test identity is a stop condition for deletion. Do not use account-wide bulk deletion or empty the whole trash.

Record each cleanup action and its result. Reopen the collection and run the same scoped read to confirm that all live test records are absent. If removal moves records to Trash, state that fact. Do not claim permanent removal. Remove the empty temporary collection only after checking that it contains no unrelated record. Report any remaining test records promptly; do not hide cleanup failure.

## Privacy and reproducibility

Keep full account UI logs and unredacted screenshots outside the publication package. Prefer observations scoped to the temporary collection. The publication can contain trial tokens, rules, selected filters, exact counts, statuses, action times, decisions, tool errors, and public app URLs. It must not contain names, email addresses, unrelated titles, account navigation history, credentials, or private record links.

Save the raw file hashes locally. Publish a clear redaction record and a hash manifest for the public evidence. Retain the public count-bearing UI excerpts and all test failures. Do not turn a hand-written count summary into a claimed raw export. A separate reviewer should compare the public evidence against the private originals before publication. State that public readers can repeat the analysis but cannot inspect any withheld account context. Do not publish screenshots if safe framing or redaction cannot preserve the evidence.

Keep the account study in new `account_*` files. Do not edit the prior raw results. Use a separate section in the same paper. Update the abstract, limitations, ethics text, and reproduction steps: the old statement that no private account was changed will no longer apply.

## Questions and decision criteria

H1: In the exclusion view, Absence and Wait24 have more duplicate outcomes than Scope. Report each rule's four outcomes and their exact evidence. No duplicates is a valid negative result.

H2: Scope makes more clean confirmations in the exclusion view than the fixed-view rules without adding duplicates. A failed create action remains a failure. Do not count an item found only by the later audit as a decision success.

H3: Every inclusion-view trial sees its new item without a retry. Report any failed control. A failed control limits the interpretation of differences in overall completion counts.

Report all 24 assigned trials, retry eligibility, actual retries, decision count, audit count, service-read count if available, late records, errors, policy deviations, and cleanup. Use descriptive counts. Four repeated trials per cell in one account are not an independent random sample of production use. Do not report population error rates, a general speed gain, or a new retry guarantee.

## Main risks

1. Filter behavior can change record fields or reset the view. Verify it before scoring.
2. The UI can give a useful receipt outside the chosen list. Preserve it and state how the rule treats it.
3. Reload survival can be mistaken for server evidence. Separate the connector audit from the UI audit.
4. Account screenshots and logs can expose unrelated private data. Keep originals local and check the public extracts.
5. Cleanup can remove an unrelated record or miss a late write. Use exact tokens, recorded IDs, and a finite final audit.
6. Prescribed rules can cause mistakes that a free-choice agent would avoid. Keep the causal claim limited to these procedures.

The final saved plan must resolve the exact app and its UI behavior. This advice does not certify eligibility or predict any observed outcome.

## Drive-specific advice after the parent's feasibility report

The parent reports a new private, unshared Drive test folder. A preflight child folder is excluded by the Documents filter. The create action leaves this filter selected. The parent reports a Working toast and will check whether a later toast confirms creation. This reviewer has not inspected that UI or the account.

Folder creation is suitable if both duplicate titles and exact child counts can be checked. All is the inclusion view; Documents is the exclusion view. Verify folder type as well as exact title. Keep all experimental folders inside the dedicated parent. Do not use files from the user's other folders.

Capture the toast text in every decision observation. Working means that work is in progress; it is not a permanent failure or a completed create. An explicit receipt that names the exact test folder can provide positive evidence outside the list. A generic receipt must not be described as an exact-token receipt. Preserve any receipt link without publishing its private account URL.

To measure this extra evidence, one possible final plan has 30 trials. Keep the 24 core trials above and add six Receipt controls: two views and three repeats. Save their fixed placement in the assignment order before scoring. Receipt submits only once. It confirms one visible matching folder, or an explicit creation receipt for the exact trial token. If neither exists, it stops unresolved. It never retries. Count and report any wrong confirmation against the later audit. The different repeat counts must remain visible in the table. An alternative is a balanced 24-trial design with four rules, two views, and three repeats. Choose one before scoring; do not choose it from outcomes.

The account connector can audit only the dedicated parent after all browser decisions. This avoids giving the browser runner extra evidence. Follow pagination and count distinct child IDs. Record the audit time and the interval from each initial create. If a per-trial full-list UI audit is also used, retain it separately. A later connector read is a service-backed finite check, not an exact measurement at decision time.

Moving the dedicated parent to Trash is a suitable bounded cleanup if its contents are all test folders. Check this before the move. Confirm the parent is absent from active Drive and is in Trash. Report that the test data is in Trash; do not claim permanent deletion. Do not empty Trash. No message, invitation, or public notification is required.
