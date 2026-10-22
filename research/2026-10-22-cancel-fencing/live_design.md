# Proposed live tests: cancellation and receipt binding

Date: 2026-10-22, America/Toronto.

Status: design only. No account data were changed for this proposal. No live trial was run. This file is not the frozen execution plan. The parent task must freeze the case list, field contract, controller code, scoring code, and stop limits before a trial starts.

## Question and scope

Can a browser controller use a fresh cancellation check and a receipt bound to the intended record and fields to avoid an incorrect save or completion claim in Google Drive and Google Calendar?

A **controller** is the local rule that decides whether to send a browser action. A **generation** is the number of an authorized run. A **receipt** here is a local record of a completed browser action and its saved-state evidence. It is not a provider-issued idempotency receipt. An **atomic check** checks a condition and applies a change as one indivisible step.

The proposal has eight cancellation cases and twelve receipt cases. Each website gets four cancellation cases and six receipt cases. Use the user's connected accounts and fresh temporary records. Browser actions make the changes. Read-only connectors check saved records when they expose the required fields.

These are controlled tests of a local controller on production websites. Cancellation times, reused operation identifiers, and receipt inputs are deliberate test inputs. They are not observations of a spontaneous agent failure or a provider defect. Two services used by one person do not test separate account namespaces.

## Relation to the existing papers

The cancellation paper has seven rules and 612 synthetic schedules per rule. This live extension tests the client check/use boundary and a valid new-generation control. It does not test all seven rules, crash recovery, generation wrap, or a receiver's cancellation fence.

The receipt paper has a sequential contract: the same operation identifier must keep the same target and payload. A payload is the set of fields an operation asks to save. This extension uses that contract for local browser completion claims. It does not test provider idempotency keys, concurrent requests, receipt expiry, or the original cross-account arm.

## Production records and field contract

Use one unique run prefix and a separate case suffix. Keep the same prefix in every value used for a test record. Record native record IDs before any test edit. A title match alone does not establish identity.

| Service | Temporary record | Test field | Fixed fields to check |
|---|---|---|---|
| Drive | A new empty folder in the user's My Drive, outside shared folders | Folder name, with a unique prefix and BASE, OLD, NEW, or PAYLOAD suffix | Native ID, known parent, folder type, active or trashed state |
| Calendar | A new private, Free, one-day all-day event on a fixed past date | Description containing an exact synthetic marker | Native event ID and calendar, title, all-day dates, Free, Private, no guests, no reminders, no recurrence, no location or conference |

Do not change permissions or send invitations. Do not use an existing personal record. Freeze the Calendar date before setup. Check the saved event, not only the filled editor. A connector's date-time conversion must not be treated as a raw API date field. The prior Calendar preflight found that description text can be absent from an accessibility snapshot and present in the visible editor DOM. It also found two trailing line feeds in a connector description. The new preflight must verify the current behavior. If it is the same, permit only trailing CR/LF removal for this field. Do not remove spaces, ignore case, or use substring matching.

Use a fresh case record for each cancellation case. For each receipt case, create record A and a separate target B where required. Do not reuse a record across policies. Exact native identity and saved fields must be available before a case is admitted.

## Eight cancellation cases

The local ledger has run ID, generation, active state, operation ID, native target ID, expected payload, and ordered action records. Write ledger updates atomically with a same-directory temporary file and replacement. This makes the local test state well defined. It does not install a fence at Google.

Generation 0 is the old run. Cancellation permanently retires generation 0. Restart authorizes generation 1. Cancellation is acknowledged in the local ledger; it is not a claim that the website has stopped pending actions. There must be no other pending browser save at the start of each case.

Run each row once on Drive and once on Calendar:

| Case | Ordered test steps | Expected observation, not a promised result |
|---|---|---|
| C1: old precheck | Check generation 0 and cache ALLOW. Cancel 0 and start 1. Use the cached result to send the OLD field update. Reopen and audit. | If the provider saves OLD, an old local decision permitted a post-cancellation change. |
| C2: final dispatch check | Check generation 0. Cancel 0 and start 1. Immediately before the planned send, reread the ledger and compare the command's generation. Block the old command. Reopen and audit. | No save is sent; BASE remains. This checks the local gate under this ordering. |
| C3: cancellation after the final check | Check generation 0 at the final local gate and cache ALLOW. Before browser send, cancel 0 and start 1. Send the already admitted OLD update. Reopen and audit. | If OLD is saved, this is a check/use-gap witness. A last client check alone did not make the write atomic with cancellation. |
| C4: valid new work | Cancel 0 and start 1. Prepare a generation-1 command. Read the ledger at the final gate, send NEW, reopen, and audit. | NEW is saved. The rule can allow current authorized work. |

C1 and C3 use deliberate delays between a check and send. No invisible background worker is required. Record the check, cancel acknowledgement, restart, browser send, save evidence, and readback in order. Do not describe the delay as a natural network race.

Score each case with separate fields: old command sent, old payload saved, current command sent, current payload saved, final field state, and evidence status. A blocked command with a complete audit is different from a save attempt with unknown outcome. If a native conflict prevents OLD, record that result; do not bypass the conflict to obtain the expected witness. Retain a failed setup or uncertain save as an assigned case with a reason.

The four cases have different schedules. Do not pool them into a causal success-rate comparison. Report each case and its evidence. A successful C2 does not prove that the same gate prevents C3.

## Twelve receipt cases

Use two explicit local policies:

1. **Key-only replay:** when the operation ID matches a stored receipt, return that receipt as success without comparing the current target or fields. This is the weak test rule.
2. **Bound receipt:** for the same operation ID, require the same service, account alias, native target, action type, and exact intended payload. Changed target or payload returns CONFLICT and sends no new mutation. An exact repeat can confirm only when its required saved-state evidence is complete.

For each policy and website, run these three pairs. There are 2 policies x 3 pair types x 2 websites = 12 assigned cases.

| Pair type | First operation | Second request under the same operation ID | Correct local contract outcome |
|---|---|---|---|
| Exact repeat | Save PAYLOAD-A to A, then verify it | Same target and same PAYLOAD-A | Replay the completed result; do not send a second save |
| Changed payload | Save PAYLOAD-A to A, then verify it | Target A with PAYLOAD-B | CONFLICT; do not confirm PAYLOAD-B and do not save it |
| Changed target | Save PAYLOAD-A to A, then verify it; verify B still has BASE | Target B with PAYLOAD-A | CONFLICT; do not claim the save on B and do not change B |

The first operation is an actual browser mutation in every admitted case. The second request is sent to the frozen local receipt policy, not a provider idempotency endpoint. Both policies reuse the same operation ID deliberately. Do not invent a provider response. Save the actual policy result verbatim as test output.

The envelope stores the service and account alias, operation ID, action type, native target ID, exact canonical payload, its hash, action-log reference, time, and saved-state evidence. A hash checks integrity; it does not establish that a website saved a value. Keep the original payload immutable. A generic Saved toast does not contain this full binding. Its role is an action observation, with native record identity and a fresh read required for confirmation.

Record two separate judgments:

- **Contract judgment:** exact repeat must replay; altered target or payload must conflict. This is a judgment about the declared local protocol.
- **State judgment:** after the second request, inspect the exact intended target and fields. A success claim for fields that differ is a false completion claim. Missing fields, uncertain identity, or an incomplete audit give UNKNOWN, not MATCH.

For changed-target cases inspect both A and B. All twelve cases must report the number of second browser mutations actually sent. These cases do not establish a duplicate-effect rate: renaming to the same name can hide a duplicate write. No provider-level exactly-once claim is permitted. If the weak rule is only evaluated later on saved evidence, label its verdict as offline or counterfactual. Do not count it as a separately executed live policy.

## Evidence, limits, and stop rules

Freeze a maximum of eight minutes per assigned case, excluding initial website login and final batch review. Permit one browser mutation at a time. Make no blind retry after an uncertain create or save. Inspect the known native record first. A setup correction may have one bounded save after a fresh read. Never repair the experimental outcome before it is recorded and scored.

Keep all assignments in the result table. Use these statuses: COMPLETE, UNKNOWN, SETUP_FAILED, CAPABILITY_UNAVAILABLE, and STOPPED. Report counts by site, policy, and case. Do not calculate a website failure probability from this small selected set. If a connector cannot expose a field, record that limit. Browser and connector reads are separate channels, not proof of independent back-end systems.

Retain private raw action records, original IDs and URLs, read outputs, timestamps, and narrowly cropped screenshots when needed. Public evidence must use synthetic aliases and contain only test content. Check for unrelated personal data before publication. The runner should record the actual browser and tool versions it can observe, and mark unknown versions as unknown.

Stop a case if another writer changes the target, native identity is uncertain, an unexpected invite or permission prompt appears, or an operation could affect non-test content. No new credentials, API charges, messages, account permissions, or shared calendar changes are needed.

After scoring, move only known test records to recoverable Trash. Do not empty Trash or delete records permanently. Verify the exact record state where the interface supports it. Also check the full test-prefix search scope and all result pages. A zero result from a partial search is not proof of cleanup. Record incomplete cleanup as unresolved.

## Capabilities this design does not test

The final local check is not an atomic receiver fence. The experiments cannot establish that all old work is stopped after cancellation. They test one controlled browser command at a time. A new generation marker in a field also does not force the service to reject an old write.

Google Calendar documents conditional updates and deletes with an earlier ETag in If-Match. A changed resource causes a 412 response. This is a different interface from an ordinary browser save. This proposal does not use it. Native conditional-write fencing is NOT TESTED. A future supported API test would need the cancellation marker and effect on the same resource, an atomic condition checked by the service, and a verified current-generation control. It would still be narrower than provider-wide cancellation. [Calendar version guide](https://developers.google.com/workspace/calendar/api/guides/version-resources)

Drive exposes native IDs, names, description, parents, trashed state, and an output-only increasing version. Names can be duplicated. A version observation alone does not provide a conditional-write gate. Its private app properties also do not define a cancellation contract. [Drive File resource](https://developers.google.com/workspace/drive/api/reference/rest/v3/files)

Calendar exposes IDs, descriptions, all-day dates, event status, reminders, and other event fields. Its all-day API end date is exclusive. Calendar event cancellation means a deleted event, not retirement of a browser worker. The writable iCalendar sequence field is not a durable local-run fencing token. [Calendar Event resource](https://developers.google.com/workspace/calendar/api/v3/reference/events)

Drive update changes metadata or content and supports partial field updates. A successful response can identify the saved file. This documentation does not by itself establish a browser receipt contract. [Drive update method](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update)

## Source check and prior evidence

Primary documentation above was read on 2026-10-22. These are service references, not research papers or preprints. Search terms included `site:developers.google.com workspace drive api files update response id version appProperties trashed supportsAllDrives` and `site:developers.google.com workspace calendar api events insert client supplied id etag sequence extendedProperties`. The scope conclusion is an inference from the documented capabilities and the proposed browser interface. It is not a claim that Google offers no other safeguards.

Local material read: `outputs/2026-10-22-cancel-fencing/report.md`, `outputs/2026-10-22-receipt-binding/report.md`, `outputs/2026-10-15-computer-use-field-checks/field_calendar_preflight_README.md`, `outputs/2026-10-15-computer-use-field-checks/field_plan.md`, and `outputs/2026-10-19-safe-undo-live/live_plan.md`. Prior observations guide preflight only; they are not new trial results.

Codex prepared this proposal. No human reviewed it within this subtask. The final report must state the actual execution and review status and must keep the synthetic study results separate from these prospective live cases.
