# Duplicate control does not define cumulative usage

Date: 2026-10-26, America/Toronto. Exact finite simulation with two controlled production record extensions. Research note.

## Abstract

A repeated report and a repeated amount are different things. We compare six accounting rules on 3,240 designed delivery histories each. All provider work is complete before report delivery begins. Ignoring repeated event IDs still overcounts final use in 1,440 histories because two distinct cumulative reports contain overlapping use. Taking the last delivered value causes 112 actual budget overruns. Taking the greatest value gives exact final use in every history, but releasing the reservation on any report still causes 72 overruns. Retaining the unused reservation until a final report avoids both errors. It gives the same 1,953 admissions as ignoring progress and waiting for the final report. Two complete runs agree. The contribution is a reproducible comparison corpus for known mechanisms. These are simulation results, not production failure rates. A later production extension used eight shared fixtures and 48 paired decisions on Google Drive and Calendar. It verified 34 saved records. LastValue and HighWaterEarly each caused two excesses against a researcher-defined record limit. The two complete rules had no accounting error or excess in these selected cases. A second extension tested CheckedLedger on 16 new Drive and Calendar cases. It created 26 counted records with no scoped excess or duplicate permit. The Calendar adapter still made seven unsupported full-field completion outputs on four records. A corrected adapter and later named-zone checks resolved current evidence while preserving that negative result.

## Question and safety relevance

Can event-ID deduplication alone make cumulative usage reports safe for reservation accounting? How do six rules differ under delayed, repeated, and reordered reports?

Safety means that actual use stays within the budget. Accounting correctness also requires the final booked amount to equal actual use. A rule can meet the first condition and fail the second. DedupSum does so in this model.

A **cumulative report** gives total use since a fixed start. A **delta** gives an additional amount for a separate interval. **Deduplication** ignores a repeated event ID. A **reservation** holds budget capacity for a job. A **terminal report** proves that a job ended and states its final use. A correct cumulative value does not by itself establish terminal status.

AI agents can share limits on tokens, tool calls, or other resource use. Incorrect accounting can permit excess use or refuse work that fits the limit. This study separates these outcomes. It does not measure a language model's choice of rule or a provider's billing accuracy.

## Related work and contribution

OpenTelemetry distinguishes cumulative totals from interval deltas and requires attention to counter identity and resets [1]. Stripe documents event replay, delivery-order limits, and asynchronous usage aggregation [2,3]. These sources motivate the delivery model. Stripe meter events are not asserted to follow this study's cumulative protocol.

Maximum-based state merge is established practice in conflict-free replicated data types [4]. Zhu and Wang's preprint already requires terminal evidence and stable duplicate settlement. Its Appendix D.5 distinguishes one final partial charge from a conflicting later receipt [5]. AgentScope Go issue 11 is a proposed design, not an implementation result. It already warns against repeated addition of cumulative stream usage [6]. We claim no defect in these systems and no new merge or settlement method.

The repository's [October 25 report](../2026-10-25-reservation-release/report.md) assumes one correct final receipt and tests release after acceptance fencing. The [October 23 report](../2026-10-23-receipt-state/report.md) compares historical receipts with later record state. This study instead tests the controller's accounting after a provider has finished. It varies delivery order, exact replay, cumulative interpretation, and the reservation hold.

The artifact adds every history in a declared small input space, six rules, complete state traces, separate error measures, and an independent prefix-based specification. It shows why a correct final total can coexist with an earlier unsafe admission, and why no overrun can coexist with incorrect accounting. A limited search cannot establish global novelty or priority. [source_search.md](source_search.md) gives exact queries, dates, URLs, reading scope, and excluded leads.

## Method

### Plan and provider contract

The [plan](plan.md) was frozen before main implementation at 17:34:14 UTC. The main source was frozen before its first run. A separate agent wrote and froze a specification before reading the main source or results. It sent expected counts before main execution, after the main implementation had been written. No main source or outcome rule changed in response. The [change record](changes.md) preserves this order.

Job A reserved `R` units. The provider emitted progress report P with cumulative use `x`, then finished with use `z` and emitted terminal report T. Require `0 <= x <= z <= R`. Both reports are true, immutable, and bound to the same job and counter start. P and T have different IDs, even when their values are equal. A repeated copy keeps its original ID and content. No counter reset, correction, conflicting final report, or dishonest source is modeled.

**All A use has already occurred before delivery begins.** The provider cannot cause more use in the study. Audit code knows `z`; the controller receives it only through T. We score actual finished use, not possible future exposure. The experiment therefore studies delayed accounting rather than the timing of live provider work.

The controller starts with booked A use `q=0`, hold `h=R`, terminal flag `f=false`, and booked B use `k=0`. Its available balance is `C-q-h-k`, where `C` is the budget. Once T arrives, `f` stays true in every rule. Thus a later progress report cannot reopen the terminal flag, even in a weak rule.

At event D, a second job B asks for `b` units. Admit and immediately use `b` only if the local available balance is at least `b`. Otherwise refuse. B does not retry. Each delivery update and the D check are atomic: no intermediate local state is visible to another event. All quantities are invented integer resource units. No money or production record is involved.

### Inputs and rules

`R` is 1 or 2. All integer pairs `0 <= x <= z <= R` give nine settings with R. For each, C is R, R+1, or R+2, and b is 1 or 2. There are 54 numeric settings.

Delivery multisets are PT, PPT, PTT, and PPTT. Enumerate distinct delivery orders, then insert D in every gap. These groups have 6, 12, 12, and 30 histories. Thus 60 schedules give **3,240 worlds per rule and 19,440 rule outcomes**. A world is one numeric setting and schedule. Same-ID copies are not artificially labeled as different events. Equal-value and zero-use controls remain in the corpus. Its multiplicities do not describe a real workload distribution.

For a received value v, all rules first update the sticky terminal flag. They then apply the following changes:

| Rule | Booked use q | Hold h |
| --- | --- | --- |
| AddEvery | Add v on every delivery | Zero after T; otherwise max(0,R-q) |
| DedupSum | Add v once per distinct event ID | Zero after T; otherwise max(0,R-q) |
| LastValue | Replace q with v | Zero after T; otherwise max(0,R-q) |
| HighWaterEarly | Set q to max(q,v) | Zero after any report |
| HighWaterHeld | Set q to max(q,v) | Zero after T; otherwise R-q |
| TerminalOnly | Ignore P; assign q=v on T | Keep R before T; zero after T |

The maximum is valid here because each value is a truthful monotone total for one unchanged job. It is not a general rule for gauges, independent increments, counter resets, or downward corrections.

### Measures and checks

After every event and at the initial state, record:

- Actual excess: `max(0,z+k-C)`.
- Uncovered actual A use: `max(0,z-q-h)`.
- Inflated A accounting: `max(0,q+h-R)` before T, and `max(0,q+h-z)` after T.
- Local deficit: `max(0,-available)`.

Each measure has a case count, maximum units, and first bad step. A negative local balance is an accounting observation; it need not prove real excess use. At D, a feasible refusal means `z+b <= C` but B was refused. A **receipt-sufficient refusal** is a feasible refusal after T has already arrived. It cannot be explained by waiting for the final report. We also record final booking error `q-z`, breach before T, and matched admissions against TerminalOnly. Measures overlap and must not be added into one error total.

Eight named controls produce 48 rule rows. They cover distinct cumulative totals, delayed progress, zero progress, equal values with distinct IDs, repeated final and progress reports, a zero final result, and D before all reports. State checks cover continuity, truthful values, sticky status, nonnegative holds, and one B decision. The two complete rules are checked at every step. All inputs, states, observations, decisions, and scores are saved.

## Results

Each row has 3,240 worlds. Every planned world completed.

| Rule | Actual overruns | Final overcounts | Final undercounts | Refusals after sufficient final evidence | B admitted |
| --- | ---: | ---: | ---: | ---: | ---: |
| AddEvery | 0 | 2,196 | 0 | 448 | 1,495 |
| DedupSum | 0 | 1,440 | 0 | 252 | 1,701 |
| LastValue | 112 | 0 | 720 | 0 | 2,065 |
| HighWaterEarly | 72 | 0 | 0 | 0 | 2,106 |
| HighWaterHeld | 0 | 0 | 0 | 0 | 1,953 |
| TerminalOnly | 0 | 0 | 0 | 0 | 1,953 |

Deduplication reduces overcount, but it does not turn cumulative values into separate increments. DedupSum still makes 252 refusals after enough final evidence is present. Its final booking is always `x+z`, which exceeds true use when x is positive. This supports H1 without treating every pre-T refusal as an error.

LastValue has 1,056 histories with uncovered A use and 112 unsafe admissions. A late P can replace the correct final total even though the terminal flag remains true. Only 720 histories end undercounted: some later T copies repair q after an uncovered state. Final-state correctness alone can miss an intermediate accounting error. This supports H2.

HighWaterEarly has correct final q in all 3,240 histories. It still causes 72 overruns, all before the first delivered T. Its 720 uncovered-use histories show that a correct merge and correct final booking do not justify early release. This supports H3.

HighWaterHeld and TerminalOnly have zero actual overruns, zero uncovered use, zero inflated accounting, and zero local deficit. Their B decisions match in every world. Each has 207 feasible refusals, all before T. Under the stated fixed-cap contract, booking progress does not add admission capacity while its residual hold is retained. This supports H4. It does not show that progress is useless for display, forecasting, or a different contract.

AddEvery and DedupSum have 1,661 and 690 local-deficit histories respectively, despite zero actual overruns. Their excess booking can make the local balance negative. The largest additive overcount is six units; the largest real overrun is two. [summary.csv](results/summary.csv) includes all measures and delivery-group results. [paired.json](results/paired.json) preserves matched admission differences.

### Concrete examples

With R=2, C=3, x=z=1, b=2, and order P,T,D, DedupSum books two units for one unit of actual use. It refuses B. TerminalOnly books one and admits B; total real use is three. The two reports are individually true and have different IDs.

With R=C=2, x=1, z=2, b=1, and order T,P,D, LastValue first books two, then lowers q to one. Its terminal flag remains true and its hold remains zero. It admits B, causing real use of three against a budget of two.

With R=C=2, x=0, z=2, b=1, and order P,D,T, HighWaterEarly releases after the zero progress report. It admits B. T later corrects q to two, but cannot undo the extra B use. HighWaterHeld keeps the full hold and refuses B. These are named controls, not selected production cases.

## Conditional arguments

For HighWaterHeld, `q+h=R` before T and `q+h=z` after T. The same identities hold for TerminalOnly. Thus the two rules have the same available balance at D and make the same decision. Before T, R covers z. After T, booked use equals z. The atomic D check therefore implies `z+b <= C` whenever B is admitted. This proof requires the stated cap, correct source values, one job identity, terminal evidence, and atomic local updates.

AddEvery and DedupSum also cover z. Before T, `q+h` is at least R. After T, their sum includes z and only adds nonnegative values. This explains their absence of overruns without making their accounting correct. Safety against excess use and exact accounting are separate properties.

## Reproduction, resources, and uncertainty

Two main runs passed. Seven deterministic files match byte for byte. The corpus has no sampling, random seed, learned model, or training split. Sampling confidence intervals and significance tests do not apply. Enumeration establishes results only for the stated input space.

The main environment was Python 3.13.7 on macOS 26.7.2, arm64, with the standard library only. Main CPU times were 0.91 and 0.89 seconds; wall times were 0.93 and 0.92 seconds. Each result set used 996,223 bytes before its environment record. No network call or model invocation occurs inside the simulator. Each run stayed within the declared limits of 120 CPU seconds, 300 wall seconds, and 200 MB output. Exact records are saved.

The independent specification derives state from the received report prefix, rather than repeating the main transition loop. Both saved runs matched all 19,440 outcomes, 85,536 transitions, 209,952 saved state records, 30 summaries, six paired comparisons, 48 controls, and 12 first adverse examples. State counts include repeated before/after values; they are check coverage, not new observations. [independent_review.md](independent_review.md) records the exact scope and limits. Agreement can reduce coding error but cannot remove a shared mistake in the written model.

Use [README.md](README.md) for commands. The package contains the frozen plan and main source, complete inputs and traces, controls, summaries, paired results, adverse examples, both run logs, and independent checking code. Review checks use saved data and are not additional trials.

## Production record extension

The owner requested this extension after publication of the simulation. It ran on 2026-10-26. It used real Google Drive folders and Google Calendar events in the owner's connected accounts. The [live plan](live/plan.md) and controller were frozen at 17:55:42 UTC, before the first test record was created. A separate agent froze independent expected results at 17:54:49 UTC. These calculations were controls, not website observations.

### What was tested

The question was whether the same six rules would control real record creation as specified when their input totals came from saved production records. This is **controlled policy replay with real record writes**: a local controller receives saved observations in a chosen order, then permits or refuses an actual write. The contribution is execution evidence for selected accounting counterexamples. No new accounting mechanism is claimed.

One successfully saved record was one test unit. Each branch had a declared limit of two records. These were researcher-defined limits, not Google quotas or billing units. Google did not issue the cumulative reports, reorder them, enforce the reservation, or supply the terminal certificate. P was a local envelope built from a fresh saved-record observation. T used a separate observation after the local A producer stopped. Repeated T delivery used the same envelope ID and bytes. Both A use and report capture were complete before each branch's delivery began, as in the simulation.

Each service had four A fixtures. A **fixture** is a known set of test records held unchanged during comparison. Each fixture was shared across six rule branches. Each branch counted its shared A IDs and only its own B ID. It did not count another branch's B records. Thus this extension has **eight shared fixtures and 48 paired policy decisions**, not 48 independent production jobs. No population failure rate, confidence interval, or significance test is justified.

All cases used R=2, C=2, and b=1. The rule definitions did not change.

| Case | P count x | T count z | Delivered order | Purpose |
| --- | ---: | ---: | --- | --- |
| Overlap | 1 | 1 | P,T,D | Distinct reports with overlapping use |
| Late progress | 1 | 2 | T,P,D | An old total arrives after the final total |
| Early release | 0 | 2 | P,D,T | Final evidence remains withheld at D |
| Duplicate final | 0 | 1 | P,T,T,D | Exact replay of one final report |

P=0 was observed before creating that fixture's A records. For P=T=1, T used a separate later read. Every branch started with a fresh local ledger. Its D decision was saved before a permitted B write. In the early case, the controller consumed T only after the B outcome was observed. The controller could store the T envelope without delivering it to the rule before D.

### Production actions and evidence

Drive used six connector-created A folders and 11 browser-created B folders in one new private test parent. Calendar used six A events and 11 B events created through its connected action. These were production API writes; they were not 17 browser creation tasks. Drive evidence includes server creation times and post-save browser observations. Separate browser dispatch-start timestamps were not saved. These creation-order checks assume that server and local clocks can be compared. A browser check separately opened the Calendar early-release B event and showed its expected time, Private visibility, and Free status. The 17 Calendar test titles were also visible in the loaded week view. The two service adapters differ, so this is not a comparison of browser versus connector reliability.

All **34 counted records** were saved and read back by exact ID. One additional Drive parent was setup only. Each permitted B had the expected name, type or event fields, and test scope. A records were read before branch use and again before cleanup. All 26 refused branch names were absent from the final test scopes. No refused B create call was sent. All 22 permitted B writes had saved-record evidence. No write needed a repeat, and no branch ended with an unknown result.

Calendar events had no attendees, recurrence, Meet link, or reminders. They were private and marked Free, from 12:00 to 12:05 on November 2 in America/Toronto. Drive folders had no external sharing. No unrelated record was changed. Official Google field definitions guided identity, time, privacy, and cleanup checks [8–12]. The connector's Calendar `fetch` view did not expose all required fields, so the test used the fuller event read action. Drive metadata did not return the requested `trashed` field. Cleanup therefore used exact-record browser locations, not an invented metadata value. Drive search did not expose a provider completeness flag. Scope checks used the new parent, exact known IDs, and the recorded writes. They do not establish absence outside this test scope.

### Observed results

Each row below has eight paired decisions: four selected cases on each service. The two sites gave the same result for every case and rule. The count of actual saved B records agreed with all 48 local decisions. Agreement means that the controller was enacted as specified; it does not make a weak rule correct.

| Rule | Saved B records | Scoped excess cases | Final overcounts | Final undercounts | Feasible refusals after T |
| --- | ---: | ---: | ---: | ---: | ---: |
| AddEvery | 0 | 0 | 6 | 0 | 4 |
| DedupSum | 2 | 0 | 4 | 0 | 2 |
| LastValue | 6 | 2 | 0 | 2 | 0 |
| HighWaterEarly | 6 | 2 | 0 | 0 | 0 |
| HighWaterHeld | 4 | 0 | 0 | 0 | 0 |
| TerminalOnly | 4 | 0 | 0 | 0 | 0 |

A **scoped excess** means that the branch's saved A records plus its own saved B exceeded the declared limit. There were four such cases. Each had three records against a limit of two. LastValue caused one late-progress excess on each service. HighWaterEarly caused one early-release excess on each service. The latter rule still had the correct final A total. Receiving T later did not reverse the B creation.

AddEvery refused feasible work in both the overlap and duplicate-final cases on each site. DedupSum refused feasible work only in the overlap case. Its duplicate-final control admitted B because the repeated report kept the same ID. This separates repeated-message control from correct treatment of two distinct cumulative reports. HighWaterHeld and TerminalOnly had the same four admissions and four refusals each. Both kept exact final counts and avoided scoped excess in this selected set.

The 10 overcounts, two undercounts, six feasible refusals, and four excess cases are different measures. They can overlap and must not be added into a total failure count. These are observed record counts with local rule calculations. They are not measurements of Google billing errors or naturally occurring delivery faults.

### Cleanup, reproduction, and limits

All 17 Calendar IDs returned cancelled after cleanup. A bounded test-marker search returned no active event and no next-page token. The Drive parent was moved to recoverable Trash. Each of its 17 children was reopened by its recorded URL; every loaded folder path showed Trash, the test parent, and the exact child. An active-marker search returned zero results. No Trash was emptied. Cleanup removed active test data but did not refund the historical creation count.

One initial Drive cleanup observation occurred before the breadcrumb had finished loading. A later read showed the correct path. Subsequent checks waited for the exact folder name. This was a read timing issue; no extra write occurred. A local Calendar evidence export also needed a parser fix for delete replies that omit a structured result. The export was rerun; no service write was retried. Both changes are recorded. Neither changes a rule or a live outcome.

The [live package](live/README.md) contains safe record aliases, captured envelopes, all branch traces, saved-field observations, cleanup evidence, analysis code, and reproduction steps. Private record IDs, account addresses, event links, and unrelated screen content remain local. Hashes bind the public extracts to retained raw evidence, but a hash alone does not prove that an account action occurred. Public files support full recalculation of the analysis. Repeating the live actions requires an authorized account and produces new IDs and times.

The original simulation and its frozen code remain intact. The extension does not test native quota enforcement, monetary billing, natural webhook failures, concurrent writers, counter resets, hostile receipts, model choice of policy, latency, or throughput. A local producer declaration supplies finality. The selected small cases cannot establish general production safety. Repeated checks of the same records are verification evidence, not additional trials.

Two saved-data analysis runs produced identical outputs. A separate prefix-based check matched all 48 decisions, 156 transitions, and 312 saved before/after states. The reviewer also checked the private record evidence and cleanup. See [independent_live_review.md](live/independent_live_review.md). These are repeated checks of the same cases, not extra production trials.

Codex operated the tools, wrote the controller, and prepared this extension. Separate Codex agents checked the design and the evidence. No human review or external peer review occurred. The exact host model and connector build identifiers were not exposed. No new paid service or model API charge was started for the tests.

## Guarded accounting and dispatch extension

The owner requested an improved rule and another account test. This extension used new temporary data on 2026-10-26. **CheckedLedger** combines known accounting and request-control methods. It does not claim a new distributed protocol.

### Repair and conditional argument

The four weak updates are replaced by a maximum for each fixed cumulative counter and a residual reservation. AddEvery and DedupSum must not add overlapping totals. LastValue must not replace a later total with an older value. HighWaterEarly must not release held capacity on progress alone. The two complete rules already avoided these accounting errors in the earlier selected cases. CheckedLedger adds persistent intent records, scope checks, and a transaction around each capacity allocation. SQLite provides single-writer transaction isolation between local connections [13]. Stable request identity is also established practice [14]; this test does not give Google a server-side idempotency guarantee.

A **scope** identifies the site, fixture, and counter start. An **intent** identifies one B write and its fields. A **permit** allows one dispatch. The rule does these checks:

1. Accept a cumulative report only for its fixed scope. Require an integer count, distinct known record aliases, evidence hashes, and consistent flags. The value must fit the reserved maximum.
2. Book the greatest valid count. Ignore an exact repeated report. Reject changed content under an existing event ID, incompatible record sets, and a contradictory final report. A rejected report puts the case in quarantine, which blocks new permits.
3. Keep the unused A reservation until valid final evidence and the local producer-stop assertion arrive. A delayed progress report cannot reduce the settled count.
4. In one SQLite transaction, check the balance and insert the B intent before dispatch. Each pending or saved B intent consumes one unit. A repeated key never receives another permit. A changed payload under the same key is refused.
5. Keep the hold when the outcome is unknown. Settle only from a matching exact-record proof. Reject incorrect fields, a different intended payload, or reuse of a record alias already assigned to another intent.

Let `q` be booked A use, `h` its residual hold, and `a` the number of pending or saved B intents. The local condition is `q+h+a <= C`. Initially, `q=0`, `h=R`, and `a=0`, with `R<=C`. Before terminal evidence, valid progress transfers units from h to q, so their sum remains R. A valid final report changes the sum to its true final use, which cannot exceed R. Replay and rejected reports do not change these amounts. A new permit increases a by one only when at least one unit remains. Settlement changes a pending intent into a saved intent and does not increase a. A transaction makes the check and increase indivisible to other connections.

The bound requires truthful A use and final totals, one shared ledger for all writers, and at most one remote create per permit. The database and Google are not one atomic transaction. A lost permit reply can retain capacity. A later contradiction cannot undo a prior action. Accounting cannot authenticate a false field-verification assertion.

### Saved plan and account procedure

The [plan](guarded/plan.md) was saved before implementation. The plan and controller were frozen at 18:23:45 UTC, before the new test records. A separate agent froze the expected case results before reading the controller. Its pre-live audit included 70 offline checks, with 12 local two-connection races. These checks are not production trials.

Each site had eight cases. Drive A folders used the connector; its four B folders used the browser. Calendar used connector creates for private Free events on 2026-11-03 at 12:00–12:05 America/Toronto. Each saved record was one historical unit. Local markers and private ID maps defined scope. Google did not issue the reports or enforce these test limits.

Cases used `C=R=2`, except unknown with `C=R=1`. Separate P/T observations were delivered in the planned order after A finished. In unknown, a real saved B proof was withheld locally; Google did not fail. In compete, two local Python processes requested the last slot. Only the winner caused a website write.

| Case | A records per site | B records per site | Observed accounting result |
| --- | ---: | ---: | --- |
| overlap | 1 | 1 | Repeated overlapping reports kept one A count. Repeated intent received no new permit; changed payload was refused. |
| late | 2 | 0 | Old progress did not reduce the settled total. |
| early | 2 | 0 | B was refused both before and after T. Progress did not release the hold. |
| release | 1 | 1 | B was refused before T. One new request was permitted after T. |
| unknown | 0 | 1 | The pending hold blocked another write. Incorrect-field proof was refused. Repeated intent and confirmation added no unit. |
| compete | 1 | 1 | Exactly one local process received the last-slot permit. |
| invalid | 1 | 0 | Three invalid reports were rejected. Quarantine blocked B; h remained one. |
| contradiction | 1 | 0 | A conflicting final report was rejected, and quarantine blocked B. |

The retained traces have four permits per site, with one observed saved B for each permit. The known record sets contain **18 A and eight B records across 16 cases**. Each selected case stayed within its limit. Accepted A totals matched the known observed A sets. The 14 cases with final evidence had exact final A booking. The two invalid cases had no accepted final report; they retained a hold and are not counted as final-settlement successes. All repeated requests received no new permit, and no key received two permits. There were 33 requests: 16 on Drive and 17 on Calendar. Calendar repeated a pending request again after reopening the ledger. That extra request is not another case. Twelve requests were refused for capacity, four for quarantine, and two for a changed payload. Seven repeated pending or saved requests received no new permit.

### Negative result: field proof was incomplete

The Calendar execution exposed an important limit in the evidence adapter. Its initial read tools returned start and end offsets, but omitted the saved IANA time-zone label. The intended payload included `America/Toronto`. The adapter nevertheless supplied `fields_verified:true` for four initial B settlements. Those four confirmations and three later repeated completion outputs were not supported for the full intended field set at that time: **seven unsupported completion outputs on four records**. This was not evidence that the events had a wrong saved zone. An offset alone cannot identify the intended IANA zone.

The original traces remain intact. A corrected Calendar adapter rejected all four initial proof sets because zone evidence was missing. Read-only editor checks then verified the named Toronto zone on all 13 exact events. Four later complete B proofs were accepted without new account writes. They establish later evidence and cannot make the earlier claims supported retroactively. Review also required explicit presence checks for fields that may be null. The corrected adapter passed 28 saved-data checks: seven checks on each B record, including missing or wrong zone evidence, wrong start time, absent recurrence or Meet fields, and a complete proof. These are evidence-replay checks, not new production cases. One initial A event had a self-attendee removed on the same saved ID before P/T capture. That correction was an extra metadata action, not another record.

The accounting result is therefore narrower than a full task-success claim. The local holds and once-only permits prevented the selected count errors, while a weak field adapter still allowed unsupported completion claims. A robust integration must check both the ledger condition and every required field before it asserts completion.

### Limits, evidence, and review

The selected cases use one account per service. They do not estimate provider failure rates or general agent reliability. No test forced a lost provider reply, a crash during commit, or simultaneous Google writes. The ID map, source observations, known scope, and stop assertions remain trusted. Quarantine and unresolved holds can reduce useful work; no automatic refund exists.

Two analysis runs produced identical row, request, and summary files. They checked the retained record sets and accounting traces; the separate adapter checks preserve the field-proof failure. The package retains the controller, frozen plan, safe traces, action ledgers, process logs, repeat commands, independent checks, and cleanup evidence. The Drive parent and all 13 child paths showed recoverable Trash. All 13 Calendar IDs returned cancelled, and the bounded active-marker searches were empty. Cleanup did not refund historical use. Raw local-process logs, private IDs, account addresses, and private URLs remain in the private evidence folder. Hashes bind extracts to retained files; they do not prove provider truth on their own.

Codex generated this work. Separate Codex agents operated Calendar and reviewed the design and evidence. Exact model and connector build IDs were not exposed. No human or peer review occurred. No paid compute, new permission, or new license was used. NeurIPS checklist topics were review aids only. Read the [guide](guarded/README.md), [sources](guarded/sources.md), and deviations before reproduction.

## Discussion and limitations

The results support all four planned hypotheses. Event identity, cumulative meaning, finality, and reservation coverage answer different questions. A controller needs the correct combination for its contract. Maximum merge alone is insufficient if the hold is released early. Deduplication alone is insufficient if distinct cumulative totals are added.

The original simulation has one progress value, one final value, one writer, one unchanged counter start, complete eventual delivery, and one second job. The provider has finished before all controller observations. It has no live work, crashes, lost reports, conflicts, tampering, partial local commits, price changes, multiple budgets, counter resets, corrections, or competing writers. The cap and final status are assumed truthful. No real service is shown to provide these guarantees. No natural-language completion claim is measured.

Small designed schedules are not independent random samples. Repeated and equal-value cases remain because they test protocol behavior. The result cannot estimate provider failure rates, model reliability, latency, or throughput. It does not test all possible accounting rules.

## Ethics, rights, and review

The original simulation used invented resource values and report labels. It changed no production record. The later extension used temporary records with the owner's permission, then removed them from active use. Public evidence excludes credentials, private account identifiers, and unrelated data. Sources are linked and paraphrased; no source code, source figure, or full paper is redistributed. No new license is assigned.

Codex generated the study, code, analysis, and report. Separate Codex agents reviewed sources and methods and wrote the independent specification. The exact host model build is not exposed in the run metadata. No human review or external peer review occurred. No affiliation, endorsement, or certification is claimed.

The main misuse risk is to treat a small model as a deployment guarantee. The stated assumptions and excluded cases limit that interpretation. Relevant parts of the NeurIPS Paper Checklist were used as a review aid [7]. This is not NeurIPS approval or a claim of submission compliance. [review.md](review.md) records the separate final audit.

## References

1. OpenTelemetry. [Metrics Data Model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/). Official specification, checked version display 1.62.0. Selected sections.
2. Stripe. [Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks). Official documentation, selected delivery and replay sections.
3. Stripe. [Record usage for billing with the API](https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage-api). Official documentation, selected sections.
4. Shapiro, Preguiça, Baquero, and Zawirski (2011). [Conflict-free Replicated Data Types](https://www.lip6.fr/Marc.Shapiro/papers/RR-7687.pdf). INRIA Research Report 7687, version 2. Selected sections; full proof not checked.
5. Zhu and Wang (2026). [Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation](https://arxiv.org/html/2610.00349v1). Preprint v1. Selected sections; no reproduction of its system.
6. AlanFokCo (2026). [Agent-side harness for higher task goodput on shared inference services](https://github.com/agentscope-ai/agentscope-go/issues/11). AgentScope Go issue 11. Open proposed design, not a paper or implementation result.
7. NeurIPS. [Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). Review aid.

8. Google. [Drive file resource](https://developers.google.com/workspace/drive/api/reference/rest/v3/files). Selected identity and state fields.
9. Google. [Drive file list](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list). Pagination and completeness fields.
10. Google. [Trash or delete files and folders](https://developers.google.com/workspace/drive/api/guides/delete). Recovery and trash-state sections.
11. Google. [Calendar event resource](https://developers.google.com/workspace/calendar/api/v3/reference/events). Selected event fields and cancelled status.
12. Google. [Calendar reminders and notifications](https://developers.google.com/workspace/calendar/api/concepts/reminders). Reminder overrides and attendee updates.

13. SQLite. [Isolation In SQLite](https://www.sqlite.org/isolation.html). Transaction isolation between connections and BEGIN IMMEDIATE.
14. Stripe. [Idempotent requests](https://docs.stripe.com/api/idempotent_requests). Stable request identity and current API v1/v2 distinctions. Stripe was not used for the tests.

All sources were accessed on 2026-10-26. See [references.bib](references.bib) and [source_search.md](source_search.md) for exact reading limits and bibliographic records. [guarded/sources.md](guarded/sources.md) records the second extension search and new source uses.
