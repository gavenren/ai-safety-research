# Plan: lowering a total budget with work still reserved

Date: 2026-10-28, America/Toronto. Save and freeze this plan before main implementation or experiment execution.

## Question and contribution

Does an atomic guard on every new job protect a strict total budget when a separate caller lowers the budget? Compare five cap-change rules. Distinguish already spent use, reserved possible use, the requested cap, and the cap that was actually applied. A failed cap request must not be called a completed reduction.

The October 24 report excluded changing capacity. The October 25 to 27 reports used fixed budgets. The contribution is an exact small comparison corpus run on a real local SQLite database, with state and SQL records and an independent specification. Guards, reservations, and version checks are established methods. A limited source search does not prove global novelty or a new protocol. This is not a test of Kubernetes, Go's rate limiter, a production site, or an AI model.

## Strict contract

Spent use s cannot be refunded. One outstanding job A has a reserved upper bound a. It later completes for x units, with 0<=x<=a. Until completion, the controller must protect the full possible a, even if a future test branch later resolves for less. Define covered use L=s+r, where r is A's remaining hold. Initial s=s0, r=a, cap C0=s0+a+slack, and revision e=0. Revision is a counter changed by each committed ledger effect.

A requested lower cap n is conditional. A successful cap change claims that L<=n at its commit, and that subsequent modeled operations preserve this bound. A refused change leaves the prior cap active and reports refusal. It does not satisfy the lower-cap request. This contract does not treat a configured prospective threshold as a guarantee about old rights or past costs. No cancellation or refund is available. Each case has exactly one cap request.

## Fixed input corpus

Enumerate s0 in {0,1,2}; a in {1,2}; x in {0,...,a}; slack in {0,1,2}; requested n in {0,...,C0-1}; and B demand b in {1,2}. C0 is derived, not separately enumerated. Each setting receives every distinct order of R,U,S,B with R before U: 12 schedules. All five rules receive the same input and order. A rule does not see x before S. Retain all cases, including negative outcomes and refusals. Record the generated input count rather than guess it.

Events are:

- R: the cap caller reads s,r,C,e in one SELECT, fetches the result, and ends the read. Keep the snapshot in application memory. No write transaction remains open.
- U: the cap caller tries the selected cap-change rule inside BEGIN IMMEDIATE. If accepted, set C=n and e=e+1 in the same commit. If refused, change no ledger field.
- S: A settles once. In one BEGIN IMMEDIATE transaction set s=s+x, r=0, and e=e+1. This models truthful final settlement; no charge occurs elsewhere and no retry occurs. Settlement must proceed even if an earlier bad cap decrease made the bound impossible. It must not hide incurred use.
- B: a different caller requests b units. In one BEGIN IMMEDIATE transaction admit only if s+r+b<=C, then set s=s+b and e=e+1. B uses exactly b immediately in this model. If refused, change no ledger field. There is no retry.

Dispatch the events sequentially in their prescribed order on separate connections for the cap caller, A, B, and audit. This imposes interleavings between cap read and cap write. It is not a parallel stress test or a remote effect. All guards, updates, and commits at U, S, and B are atomic local transactions. The stale application snapshot at R is deliberate.

## Five cap rules

1. BlindSet: apply n without a load check.
2. SpentOnly: apply n only if the current s<=n. Ignore the outstanding hold.
3. CachedCover: apply n only if the R snapshot's s+r<=n. Do not recheck current load or revision.
4. VersionedCover: require the snapshot's s+r<=n and current e equal the R revision. Otherwise refuse.
5. AtomicCover: require current s+r<=n in the write transaction. Recompute even if the earlier R snapshot would have refused.

All read the same R snapshot; unused fields are deliberate baseline omissions. All B callers use the same complete current guard. A higher accepted count does not mean a better rule if it includes unsafe changes.

## Hypotheses, measures, and criteria

H1: BlindSet and SpentOnly can accept a cap below current covered use even though B always has a complete guard. SpentOnly may defer an actual-use breach until A settles.

H2: CachedCover can accept an unsafe reduction after intervening B use. It can also refuse a now-feasible reduction after A returns unused capacity.

H3: VersionedCover and AtomicCover preserve L<=C at every step in every primary case. VersionedCover can refuse feasible reductions after a revision change. AtomicCover accepts exactly the numerically feasible reductions at U.

H4: Some histories have L>C after the cap change but never have actual s>C. End-of-history actual use alone misses those unsafe successful changes.

Measure U accepted/refused, unsafe accepted changes (accepted and L at U exceeds n), feasible refused changes (refused while current L<=n), successful changes already below spent use at U, accepted changes with positive hold exposure but not actual excess at U, B admitted/refused, any covered-use breach L>C, any actual-use breach s>C, final actual excess, maximum excess in each measure, and first occurrence event. Use the applied C, not an unaccepted requested n, for breach scores. Record requested-cap feasibility separately. Distinguish actual breaches introduced by U from later breaches introduced by S. Never label B as an unsafe accepted action merely because an earlier cap write was invalid.

Retain all states before and after each event, the R snapshot, every condition and outcome at U/B, SQL statements with caller/case/event labels, final rows, and deterministic summaries. Summaries have all cases and strata by order (S before/after U, B before/between/after R,U), prior-spent group, and settlement x=a versus x<a. These groups overlap. Save first examples in declared lexicographic input/schedule order for unsafe changes, feasible refusals, actual breaches, and exposure without actual breach. These are first retained examples, not globally minimal ones.

Match each rule to AtomicCover on each input to describe decision differences. No population inference, confidence interval, significance test, or random seed is appropriate for this selected exact corpus.

## Controls and review

Save named controls for an already impossible target, a pending-liability reduction, intervening B use, returned unused hold, settlement with unchanged covered total, and a serial feasible reduction. Include a separate database rollback control: change spent, cap, and revision inside a transaction, roll back, and prove all fields are unchanged from another connection. Include a conditional refused-write control to prove no field changes. Record SQLite integrity checks and all final rows from a reopened database. Check that B never commits with resulting L>C. A settlement may expose an earlier invalid cap; report that origin.

Before the main implementation or results are shared, a separate agent must read only this plan and freeze an independent expected evaluator. It should use direct schedule/prefix formulas rather than SQL or a copy of main updates. Compare every input, every state, every decision and score, summaries, paired decisions, controls, and retained examples. Compare reopened database rows too. Run the main procedure twice and compare deterministic scientific files; keep environment records separately. Preserve any failed run and repair history.

## Resources, rights, and disclosure

Use Python's standard library and local SQLite. Use WAL mode, synchronous FULL, read_uncommitted OFF, and no shared cache. Every case has a fresh distinct database row. Bound each run to 120 CPU seconds, 450 wall seconds, and 200 MB saved output; periodic wall/file checks are not hard real-time guarantees. Record Python, SQLite, operating system, source hashes, CPU/wall times, output size, commands, and logs. No paid compute, external model call, account action, or private input is required.

State all assumptions and result limits. Data are invented. No random workload, crash, network partition, malicious report, cancellation, refund, or enforcement at an external provider is tested. Do not claim a new resource protocol or criticize a source system under a contract it does not promise. Assign no new license. State that Codex generated the study and report and that no human review occurred. Complete source, method, reproducibility, privacy, reference, and relevant NeurIPS checklist checks before publication. Publish one report for this run and verify the remote commit and every package file.
