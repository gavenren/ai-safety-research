# Design review

Date: 2026-10-27.

Reviewer: a separate Codex agent. Human review: none.

Review input: the frozen `plan.md`. The reviewer did not read the main implementation or its results before this review. This is a design review, not a result check.

Decision: no blocking design error found. The study can proceed under the stated contract. Retain the limits below in the report.

## Count and rule checks

There are six allowed progress/final pairs for one incarnation. Their cross product gives 36 value configurations. The base multiset has 4! = 24 permutations. Each repeated-final multiset has 5!/2! = 60. Thus the declared primary corpus has 36*(24+60+60) = 5,184 histories. Six independent admission branches give 31,104 decisions for each rule. These are design counts, not executed results.

All rules use the same exact-ID duplicate filter. This removes copy handling as a source of different results. The rules remain intentionally different in how they use identity, source order, and delivery order.

For SourceOrderDrop, the first two ordered points give q=z0. If p1<z0, the remaining points give q=z0+z1=Z. If p1>=z0, they give q=z1. Thus this rule never overcounts under the contract. It undercounts exactly when z0>0 and p1>=z0. The case z0=0 is exact even though it falls in the declared hidden-reset group. State this zero-total exception in the proof and results.

For EpochMax, each final report is present and each incarnation's progress value is no greater than its final value. Its two maxima must therefore equal z0 and z1. This proves exact final accounting under this contract. It does not prove exact accounting with an omitted final report or an unknown incarnation.

## Admission and comparison checks

The same closure barrier is used for all rules. Admission occurs after all primary reports arrive. Each branch begins from the same closed history. This avoids accidental treatment of the six branches as sequential jobs.

The capacities are selected from the known true total to test boundary decisions. This is a valid controlled test. It is not a model of how a deployed agent learns the capacity or true use. The report must distinguish the test's reference truth from a rule's booked use.

Some rules deliberately ignore final flags or incarnation IDs that the input supplies. State this choice. The comparison does not show that EpochMax is better than every reasonable accounting method. For example, complete final receipts could also support exact accounting under a suitable contract. No additional baseline is required for the declared five-rule question.

The aggregate counts weight every declared delivery history once. Repeated-final groups can change the distribution of the first appearances of distinct reports. Their aggregate weights are design choices, not estimates of real delivery frequencies. Keep the planned group summaries and denominators.

## Boundary and independent-check requirements

The missing-final control checks refusal while the barrier is false. It does not establish how a real service proves closure. Report its partial estimate separately from primary completed-cost results. Its known true total is available to the test evaluator, not established by the received evidence.

The plan requires an independent specification frozen before it reads the main source or outputs. Compare states as well as totals. Include the effect of exact replays. Confirm every reported adverse example with its saved trace. A successful final-total check alone cannot validate the intermediate state logs.

No measured failure rate, statistical significance, live-site result, billing result, or end-to-end agent safety claim follows from this finite corpus. The identity, source-order, truthful-report, disjoint-cost, and closure assumptions are essential. No material design gap requires a plan change before execution.
