# Duplicate control does not define cumulative usage

Date: 2026-10-26, America/Toronto. Exact finite simulation. Research note.

## Abstract

A repeated report and a repeated amount are different things. We compare six accounting rules on 3,240 designed delivery histories each. All provider work is complete before report delivery begins. Ignoring repeated event IDs still overcounts final use in 1,440 histories because two distinct cumulative reports contain overlapping use. Taking the last delivered value causes 112 actual budget overruns. Taking the greatest value gives exact final use in every history, but releasing the reservation on any report still causes 72 overruns. Retaining the unused reservation until a final report avoids both errors. It gives the same 1,953 admissions as ignoring progress and waiting for the final report. Two complete runs agree. The contribution is a reproducible comparison corpus for known mechanisms. These are simulation results, not production failure rates.

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

## Discussion and limitations

The results support all four planned hypotheses. Event identity, cumulative meaning, finality, and reservation coverage answer different questions. A controller needs the correct combination for its contract. Maximum merge alone is insufficient if the hold is released early. Deduplication alone is insufficient if distinct cumulative totals are added.

The model has one progress value, one final value, one writer, one unchanged counter start, complete eventual delivery, and one second job. The provider has finished before all controller observations. It has no live work, crashes, lost reports, conflicts, tampering, partial local commits, price changes, multiple budgets, counter resets, corrections, or competing writers. The cap and final status are assumed truthful. No real service is shown to provide these guarantees. No natural-language completion claim is measured.

Small designed schedules are not independent random samples. Repeated and equal-value cases remain because they test protocol behavior. The result cannot estimate provider failure rates, model reliability, latency, or throughput. It does not test all possible accounting rules.

## Ethics, rights, and review

All data are invented resource values and report labels. No connected account or production record was changed. The study contains no credentials or private account data. Sources are linked and paraphrased; no source code, source figure, or full paper is redistributed. No new license is assigned.

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

All sources were accessed on 2026-10-26. See [references.bib](references.bib) and [source_search.md](source_search.md) for exact reading limits and bibliographic records.
