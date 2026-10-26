# Guarded usage extension plan

Date: 2026-10-26. Status: saved before implementation and account execution.

## Question and contribution

Can one checked, durable ledger remove the selected double counts and unsafe write decisions from the prior six-rule comparison? Can the same ledger block repeated dispatch, unresolved writes, and two requests for the last unit?

The proposed CheckedLedger combines known maximum merge, residual reservation, terminal settlement, transaction, and intent-key checks. It replaces the four weak updates and adds execution controls to the two complete accounting rules. This is an implementation and selected-case test, not a new accounting mechanism or a claim of global novelty. Prior results remain unchanged.

## Contract and rule

One saved record is one historical unit. Each case has one fixed site, fixture, and counter start. Each report names its scope, immutable event ID, capture time, total, exact known record aliases, terminal flag, local producer-stop flag, and retained evidence hashes. The counter cannot reset. A true final total and a stopped producer are assumptions checked by the operator's known record ledger; Google does not issue these local reports or enforce this limit.

Book the greatest valid cumulative value. Hold the unused part of A's reservation until valid terminal evidence. Ignore exact replay. Reject wrong scope, malformed values, changed bytes under the same event ID, incompatible record sets, and contradictory final reports. A rejected report puts this case in a persistent quarantine: no new write is permitted. This conservative stop can refuse useful work. It cannot undo an earlier permit or repair a dishonest report accepted before the contradiction.

Use one SQLite transaction to check the shared balance and store each new B intent before dispatch. A B intent consumes one unit while pending and after it is saved. Repeated keys return no new permit, including after reopening the database. Bind each key to the exact intended fields. A changed payload under the same key is refused. Unknown outcomes keep their hold. Settle only from fresh exact-record readback, correct fields, matching payload hash, and a distinct saved alias. A mismatch cannot establish success. Cleanup does not refund past use. Every writer must use this ledger, and the operator must dispatch at most once for each permit. SQLite and a remote website are not one atomic transaction.

## Sites and scope

Use temporary empty Google Drive folders in one private parent and private Free Google Calendar events on 2026-11-03 at 12:00-12:05 America/Toronto. No attendees, reminders, recurrence, or Meet links. Marker prefixes are CUA-UG-20261026-DRIVE and CUA-UG-20261026-CAL. Drive A records use the connector; Drive B writes use the browser. Calendar writes use its connector. Record each method separately. Do not change unrelated data, permissions, credentials, or sharing. Do not buy compute or services.

Each site has eight separate fixtures. Each fixture has its own durable ledger and known A/B record set. Limits are researcher-defined case limits, not provider billing or quotas. No B from another fixture counts. The Drive setup parent does not count. Expected writes are nine A and four B records per site, or 26 counted records plus one parent. Actual counts come only from readback. Cases are selected controls, not a population sample.

## Fixed matrix

All cases use C=R=2 except unknown, which uses C=R=1. Each B asks for one unit.

| Case | A records | Report/action order | Planned check |
| --- | ---: | --- | --- |
| overlap | 1 | Capture P1 then separate T1; deliver P,T,P,T; request B; replay key; change payload under key | One B permit, no duplicate count or dispatch; changed payload refused. |
| late | 2 | Capture P1 before second A and T2; deliver T,P; request B | Old progress cannot lower the total or permit excess. |
| early | 2 | Capture P0 before any A; capture T2 after A stops; deliver P; request B; deliver T; new request | Both requests refused; progress cannot release the reservation. |
| release | 1 | Capture P1 then T1; deliver P; request B; deliver T; new request | Before-T refusal; one after-T permit. |
| unknown | 0 | T0; permit and create B; withhold readback; repeat key; request another key; reopen process; invalid field proof; valid readback; repeat saved key | Pending hold survives restart; no second dispatch or false success. The missing reply is local evidence withholding, not a Google outage. |
| compete | 1 | T1; two separate processes request different B keys together | One permit and one limit refusal; only winner is dispatched. Process order is not fixed. |
| invalid | 1 | P1; wrong-scope report; changed same-ID report; malformed boolean value; request B | All invalid reports rejected; persistent quarantine blocks B. |
| contradiction | 1 | T1; new-ID T0; request B | Contradiction rejected; quarantine blocks new writes. |

Every valid P/T pair is captured in order, even when delivery is reversed. Exact duplicate deliveries reuse the same bytes. All A records are complete before the branch actions. The unknown case tests the local pending path with a real saved record. It is not an induced service failure. Compete tests two local processes, not simultaneous Google writes.

## Evidence and decision criteria

Save the plan before implementation, and freeze plan/controller hashes before account writes. A separate agent will freeze an independent specification before reading the controller/results. Use separate raw evidence folders per service. Save every request and reply, times, database export, action ledger, exact-ID field checks, scope checks, and cleanup proof. Public files use safe aliases and hashes; private IDs, addresses, account URLs, and unrelated content remain private.

Pass requires: no case exceeds C; final A booking equals valid final A count where T exists; before T q+h equals R; accepted B is booked once; no repeat intent issues another permit; no saved alias settles two operations; invalid evidence makes no completion claim; every permit has exactly one saved record or an explicit unresolved outcome. A refusal has no corresponding create action. Unknown and quarantine are explicit non-success states. Record every failed check and deviation, without silently replacing cases.

Repeat deterministic analysis of the exported traces twice. Independently check the full decisions and all balances. Compare with the prior four selected-case outcomes as historical context, not a newly rerun randomized baseline. Optional invented local regression tests are separate from production counts. No confidence interval or significance test is justified by the selected matrix.

## Cleanup and publication

Move only the new Drive parent to recoverable Trash and verify its exact children through their paths or available trashed metadata. Cancel all exact Calendar IDs and verify cancelled status and an empty bounded active-marker search. Do not empty Trash. Resolve or disclose unknown cleanup. Check primary sources and relevant NeurIPS checklist topics, private data, claims, reproduction, and review status. State that Codex generated the work; no human or peer review is implied. Update the same paper and index only after required checks pass, then verify the exact remote files. No new license is assigned.
