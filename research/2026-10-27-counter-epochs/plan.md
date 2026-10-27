# Plan: counter restarts and total use

Date: 2026-10-27. Save this plan before writing the main implementation or running an analysis.

## Question and contribution

Can a rule that infers counter restarts from value decreases calculate exact completed use when old reports arrive late? Does sorting by source order solve every reset error?

This is a finite comparison of known rules, not a new merge protocol. The October 26 study fixed one counter start and excluded resets. This study adds two disjoint counter incarnations. An incarnation means one accumulation period with a stable unique identifier. It is not a budget-authority epoch. The contribution is a complete declared corpus, matched accounting and admission results, full traces, and an independent check. A limited source search does not prove novelty.

## Provider contract and fixed inputs

All external use is complete before delivery starts. Two incarnations E0 and E1 have true nonnegative integer use z0 and z1. Incarnation E1 starts a new counter at zero after E0 ends. They have disjoint use. Each emits one progress point Pi with value pi and one final point Ti with value zi. Require 0 <= pi <= zi <= 2. This gives six (pi,zi) pairs per incarnation, or 36 value configurations. True total Z=z0+z1.

Each report carries a stable report ID, an incarnation ID, a value, a final flag, and a distinct source-order number. The source order is P0=1,T0=2,P1=3,T1=4. Reports are truthful. Copies keep the same ID and fields. Source order is trusted and has no clock skew. Delivery can have any order. No correction, missing primary report, new third incarnation, identity collision, or false source is in the primary corpus.

Use three delivery multisets: P0,T0,P1,T1; P0,T0,T0,P1,T1; P0,T0,P1,T1,T1. Enumerate all distinct permutations: 24,60,60, or 144 orders. Cross these with the 36 value configurations for 5,184 histories. Exact duplicate copies are not artificially given distinct labels.

All five rules ignore an exact repeated report ID before any value update. This common duplicate filter isolates reset interpretation. Initialize empty state and zero accounting.

## Rules

- GlobalMax: take the greatest distinct received value, without separating incarnations.
- ArrivalDrop: maintain last distinct received value l, initially zero, and total q. For value v, add v-l if v>=l; otherwise add v. Then set l=v. This is a deliberately simple arrival-order heuristic.
- SourceOrderDrop: sort all distinct received points by their trusted source-order number. Recompute the same decrease rule over this ordered prefix, starting from zero. This is not Prometheus increase/rate, which also use time ranges and extrapolation.
- EpochLast: retain the last distinct delivered value for each stable incarnation and sum those values.
- EpochMax: retain the greatest received value for each stable incarnation and sum those values. This is the complete identity-aware comparison under this contract, not a new algorithm.

Record every delivered report, duplicate decision, and state after each event, including report IDs seen, arrival order, per-incarnation values where used, last value where used, and booked use q. No request is admitted during report delivery. Intermediate estimates are not scored as completed cost.

## Admission after closure

After the complete primary history, a separate closure barrier confirms that all work ended and both registered final reports arrived. Closure is not inferred from a value drop or a maximum. Each rule sees this same barrier and the same closed report set. A second job asks for b units. Evaluate each combination C in {Z,Z+1,Z+2}, b in {1,2}. Admit if C-q>=b, then use exactly b. These are six matched hypothetical decisions per history, 31,104 decisions per rule and 155,520 across five rules. Decisions are independent branches, not six sequential jobs. No account or provider is called.

## Hypotheses and measures

H1: GlobalMax can undercount disjoint incarnations and permit excess use.

H2: ArrivalDrop can undercount or overcount because a delivery decrease need not be a reset.

H3: SourceOrderDrop removes arrival-order dependence but can miss a reset when the first new-counter value is at least the old final value. It cannot overcount in this two-incarnation contract. Derive the exact condition separately.

H4: EpochLast can lose a final value when an earlier progress point arrives later. EpochMax has exact final use for every primary history. Both source-order and epoch-based conclusions depend on the stated correct identity and completeness contract.

Per history/rule record final error q-Z, undercount, overcount, exact count, first retained adverse example, and final state. Per admission branch record admitted, actual use Z+(b if admitted else 0), excess max(0,actual-C), feasible refusal (not admitted and Z+b<=C), and local balance C-q-(b if admitted else 0). Do not confuse local deficit with actual excess. Report denominators. Also summarize by duplicate group and reset visibility p1<z0 versus p1>=z0. Compare matched decisions against EpochMax.

## Controls and independent checks

Include named examples for visible reset, hidden reset, late old progress, equal counter values, zero use, and exact replay. They must be retained even if a hypothesis fails. Also include one separate missing-final control with p0=p1=1,z0=z1=2 and reports P0,T0,P1. The barrier is false, so all rules refuse admission. Record the partial EpochMax estimate and its difference from Z. This is an assumption-boundary control, not a primary missing-data study.

Freeze an independently implemented expected specification before it reads the main source or outputs. Prefer direct formulas on prefixes and final report positions to a copy of the main state loop. Compare every saved state, duplicate flag, error, admission branch, summary, control, and matched decision. Run the main procedure twice and compare deterministic bytes. Keep any failure or repair record. Do not discard outcomes or change rules after results.

## Resources, rights, and review

Use Python standard library, invented data, no random seed, no model call, and no network inside the study. Bound each main run to 120 CPU seconds, 300 wall seconds, and 200 MB saved output. Record exact environment and time. Use deterministic gzip headers and save full compressed traces. This is an exact finite simulation, not a test of a real agent, live website, Prometheus, OpenTelemetry implementation, quota, or billing system.

No statistical confidence interval or population failure rate follows from selected enumeration. Correct source order, truthful reports, non-reused incarnation IDs, disjoint costs, and the closure barrier are assumptions. No private account data is needed. Cite checked primary sources with original short summaries. Assign no new license. State Codex generation and actual human review status. Complete separate source and method reviews, relevant NeurIPS checklist checks, privacy/link/rights checks, then publish one October 27 report and verify its remote files.
