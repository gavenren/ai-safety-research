# Production record extension plan

Date: 2026-10-26. Owner-requested extension to the existing usage accounting paper.
Status: Plan saved before any test record is created.

## Question and contribution

Do the six specified accounting rules make different admission decisions when their cumulative inputs come from saved production records? Do permitted writes produce the predicted scoped record counts?

This is a controlled policy replay with real production writes. Google does not supply or enforce the test budget. The test does not inspect Google billing or simulate a provider webhook. Local envelopes carry snapshots of real saved records. The operator deliberately changes delivery order or repeats an envelope. This extension adds execution evidence to selected known counterexamples. It does not establish a new accounting method.

## Sites, unit, and scope

Use the owner's Google Drive and primary Google Calendar. Drive records are empty folders in one new test parent. Calendar records are private events on 2026-11-02, 12:00-12:05 America/Toronto, with no attendees, no reminder, no Meet link, and free time status. Use marker CUA-USAGE-20261026 and distinct case/role/rule names. Do not change unrelated records, sharing, permissions, or credentials. No paid compute or service is allowed.

One successfully saved A or B record is one test unit. The budget is a researcher-defined count limit, not a native service quota. Each branch consists of the immutable A IDs for that case and its own B ID, if any. B records from other branches are excluded. Container folders do not count. Counts concern created records, not time, storage bytes, tokens, or money. Cleanup does not reverse historical use.

Four A fixtures are shared across the six rules at each site. These are eight production fixtures and 48 paired policy decisions, not 48 independent production trials. Anticipated totals are 12 A records and 22 B records, plus one Drive parent. The exact total must come from readback evidence.

## Matrix, hypotheses, and baseline

All cases have reservation R=2, budget C=2, and B request b=1. TerminalOnly is the baseline. Run rules in the order AddEvery, DedupSum, LastValue, HighWaterEarly, HighWaterHeld, TerminalOnly.

| Case | Progress x | Final z | Delivery order | Intended check |
| --- | ---: | ---: | --- | --- |
| overlap | 1 | 1 | P,T,D | Two distinct cumulative reports overlap; AddEvery and DedupSum should refuse feasible B. |
| late | 1 | 2 | T,P,D | Old progress should make LastValue admit B beyond the declared limit. |
| early | 0 | 2 | P,D,T | HighWaterEarly should admit B before final evidence and exceed the declared limit. |
| duplicate | 0 | 1 | P,T,T,D | Repeating the same final envelope should cause AddEvery to refuse feasible B. |

The four cases include equal-value distinct-ID and same-ID replay controls. The two complete rules should have exact final booking, no scoped excess, and equal B decisions. No estimate of a natural failure rate or confidence interval is planned; cases are selected and share fixtures.

## Capture and execution

1. Check the marker is absent in the bounded test scope. Save the query and result.
2. For each A fixture, create x records and read their exact IDs and saved fields. Capture P from this complete known set. If x=0, use the empty marker-specific known set before any A create. The envelope includes site, fixture, counter start, unique P ID, value, and evidence references.
3. Create any remaining z-x A records. Read back all z exact IDs and fields. Stop A permanently for this test and capture T with a distinct ID and terminal=true. Terminal status is the local producer's recorded stop, not a claim supplied by Google. P and T are captured in this order even if delivered in another order. If x=z, use a fresh separate read for T.
4. Only after A is complete, apply each rule to the declared envelope schedule. Save before/after states, received envelope hashes, the D decision, and a write-ahead intended B name. The early case must pause at D for the real write before delivering T to that branch. A repeated T uses the exact same bytes and ID.
5. If D admits, create one B record with the branch marker. Fetch the exact ID and verify saved fields. If D refuses, do not call create; check its marker is absent in the final complete test-scope enumeration. Save refusal decisions even when the case has no write.
6. Re-read A and all created B IDs before cleanup. Require all A IDs to remain active and unchanged. Compute each scoped count from its known A IDs and own B ID. Do not infer completion from a toast or attempted write. If any write has an uncertain result, search its exact marker before a retry. If unresolved, label the branch unknown and stop new dependent writes.

Drive setup may use the connector. Drive B writes use the browser where available. Calendar writes use the connected Calendar action, followed by fresh exact-ID reads; the browser may provide a separate visible-state audit. These methods must be counted separately. Tool versions that are not exposed must be reported as unavailable.

## Scores and evidence

Use the original six transitions without modification. Save final q, h, terminal flag, seen IDs, decision-time balance, accepted/refused/unknown status, B write count and observed saved ID, and final scoped use. Scores are final booking error q-z, unsafe admission/scoped excess max(0,z+observed_B-C), and feasible refusal after T. Record failures and deviations, including incomplete enumeration or missing readback. Do not replace a failed case with a silent extra trial.

Save raw connector responses, browser snapshots, timestamps, and record mapping privately. Public files contain opaque aliases, marker suffixes, relevant safe fields, local receipt envelopes, policy traces, raw result rows, analysis code, reproduction commands, and hashes of private evidence. Do not publish account emails, calendar IDs, record IDs, private URLs, or unrelated screen content. Public data permit full analysis replay; repeating live writes requires an authorized account and will produce different IDs and times.

## Cleanup and publication gate

Remove only exact IDs created by this run. Move Drive parent to Trash, then verify each created child and parent has trashed=true, or report any incomplete verification. Delete the test Calendar events, then require exact-ID cancelled status and a bounded marker search with no active result. Do not empty Trash or permanently delete data. Record retrieval failures honestly. An unverified cleanup is a material issue to resolve or clearly report before claiming completion.

Before publication: independently recompute all decisions, reconcile allowed writes with actual saved IDs, verify all refusals have no B record, check cleanup, sources, private data, and report claims. Use the relevant NeurIPS checklist items. Keep synthetic results intact and label this extension separately. State actual AI roles and human-review status. Update the same report and index, then verify exact remote file hashes.
