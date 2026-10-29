# Production website extension plan

Date: 2026-10-29, America/Toronto. Save before account writes and test analysis.

## Question and scope

Can the six published accounting rules control real browser saves when their inputs come from saved, corrected website records? This is a selected integration test. It extends the same paper. It does not claim a new accounting method or a production failure rate.

Use the user's connected Google Drive and primary Google Calendar accounts. Use temporary empty folders and private Free events. No guests, reminders, recurrence, or Meet links. Use one new private Drive parent. Do not change unrelated records or sharing. Do not use paid services. Calendar events use 2026-11-04 12:00-12:05 America/Toronto. The marker is CUA-CORR-20261029.

One test credit is an invented accounting unit. Store source item, revision, and credits in each record name. These fields are study data, not provider charges. A correction does not undo physical resource use. Revisions are assigned by the study after sequential observed saves. They are not provider version guarantees. The study operator closes each test period after both corrections. This is not a provider finality certificate.

## Fixed cases

Repeat the same three cases on each service. Each case has two separate source records A and B. Values below are (uA,vA,uB,vB). Create and read revision 1 through the connector. Then change the same record to revision 2 in the browser. Reopen or reload and observe the saved name. Read the exact object again through the connector. Do not analyze a case if these observations conflict. Retain failures and report unknown outcomes.

| Case | Values | Local delivery order | Cap | New demand |
| --- | --- | --- | ---: | ---: |
| credit | (2,0,0,0) | A2,A1,B1,B2 | 1 | 1 |
| upward | (0,2,0,0) | A2,A1,B1,B2 | 2 | 1 |
| replay | (1,1,1,1) | A2,A2,B2,A1,B1 | 3 | 1 |

The delivery harness copies saved observations. Reordering and repeat delivery are local controlled conditions, not observed Google delivery faults. A1/A2/B1/B2 have distinct study event IDs. The repeated A2 uses identical fields. Delta for revision 1 is u; delta for revision 2 is v-u. No rule sees a future record before delivery. The scorer has all final values.

## Rules and actual output actions

Use the published evaluate function unchanged. All rules ignore a seen event ID before updating. Net adds signed deltas. GlobalClamp clips the shared sum at zero after each delta. ItemClamp clips each item's sum. ArrivalReplace takes the last distinct delivered value. MaxReplace takes each item's maximum. RevisionReplace takes each item's greatest source revision. Complete receipt and the study's closure declaration are required before an admission decision. Admit iff q+1<=cap.

Pre-create six output markers per service, one for each rule. Reuse each marker for the three cases in fixed order: credit, upward, replay. The exact pre-case name is the baseline. Each case has a fresh local accounting state; earlier output saves do not count in that case. If admitted, change that rule's output marker name through the browser to a unique case-and-rule result name. If refused, make no Save call. Read all six exact objects after each case and compare with the required name. Save intermediate evidence before later overwrites. A refusal is a local dispatch refusal, not a website rejection.

At most 25 records are created: 12 source records, 12 output records, and one Drive parent. Expected browser writes are 12 source corrections and 18 admitted output renames. There are 36 rule decisions on six matched service cases. This is not 36 independent samples. Each admitted output rename costs one artificial credit. The study cap excludes setup, source corrections, cleanup, and real provider use. Record these operations separately.

## Hypotheses and checks

Net and RevisionReplace should match all selected final charges. In credit, the other four rules should overcount and refuse a feasible output save. In upward, ArrivalReplace should admit a save with final test charge 3 above cap 2. Other rules should refuse. In replay, all rules should admit, and exact repeat should not change accounting. These are preselected tests, not estimates of frequency.

Save plan and code hashes before account writes. Freeze a separate formula evaluator before results. Store exact IDs, requests, responses, timestamps, and browser observations privately. Publish safe aliases, test-only fields, evidence hashes, commands, all decision traces, and sanitized operation records. Check one same-ID output save per admission and zero dispatches per refusal. Compare final q, state q, duplicate flags, decisions, excess test credits, and feasible refusals independently. Run saved-data analysis twice and require identical output. Check rules against the original implementation. Do not silently revise a rule after an error.

## Cleanup and publication

Cancel all 12 exact Calendar IDs; check cancelled status and a bounded active marker search. Move only the new Drive parent to recoverable Trash; check each child's exact folder path and active marker scope. Do not empty Trash. State any cleanup uncertainty. The public evidence must exclude private IDs, account addresses, unrelated records, and secrets.

Use checked primary sources and relevant NeurIPS checklist topics as a review aid. Keep source licences and no new repository licence. State Codex's roles and no human review. Update the existing report and index only after review and evidence checks. Verify remote commit, exact file hashes, and unchanged unrelated files. A local save or upload screen is not publication proof.
