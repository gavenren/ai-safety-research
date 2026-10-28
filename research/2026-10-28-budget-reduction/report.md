# A correct job guard does not make every budget reduction safe

Date: 2026-10-28, America/Toronto. Research note. Invented workloads on a real local SQLite database.

## Abstract

An AI task can have spent use and work that still holds reserved capacity. Lowering its budget does not remove either amount. We compare five cap-change rules on 3,888 selected schedules each. Every new job uses the same complete atomic admission check. A rule that checks only spent use still accepts 576 reductions below covered use. Of these, 288 later exceed the applied cap in actual use. A saved earlier coverage check accepts 219 unsafe reductions. A complete revision check has no unsafe reduction but refuses 507 reductions that currently fit. A current coverage check inside the write transaction accepts 1,077 feasible reductions and has no unsafe change or feasible refusal. The contribution is a repeatable finite comparison corpus with full SQL evidence and a separate formula check. These are results for local application rules, not production failure rates or a new resource protocol.

## Question and safety relevance

Does an atomic check on every new job protect a strict total budget when another caller lowers that budget?

A **cap** is the active upper bound on total use. A **reservation** holds capacity for work whose final use is not yet known. **Spent use** is use that cannot be refunded. **Covered use** is spent use plus the full remaining reservation. An **atomic transaction** commits its check and changes as one unit. A **revision** is an integer that changes after each committed ledger effect. The **ledger** is the stored account of spent and reserved use.

An AI system can use these records to control tool or compute use. A change to a limit is a separate state-changing operation. A complete job guard does not validate that operation. A success response for a lower cap also needs a precise meaning. In this study it claims that existing covered use fits the lower cap at that commit. A refused request leaves the old cap active and does not complete the requested reduction.

## Related work and contribution

Kubernetes states that quota changes do not alter resources that already exist [1]. Go's rate-limiter documentation states that earlier reservations can leave use above or below a changed rate [2]. These are documented semantics. Their quota and token-bucket contracts differ from our strict cumulative budget. We do not test those systems or claim defects in them.

Zhu and Wang's preprint distinguishes unresolved obligations from settled use and limits what fencing can reclaim [3]. We checked selected sections only. We do not reproduce its protocol or proofs. SQLite documents writer serialization and transaction boundaries [4,5]. Our saved earlier read ends before the later write. A stale application value used in that write is not a SQLite isolation defect.

The repository's [October 24 study](../2026-10-24-shared-limit/report.md) tested different job guards with fixed capacity. The [October 25 study](../2026-10-25-reservation-release/report.md) tested release of a hold. The [October 26 study](../2026-10-26-usage-reconciliation/report.md) tested usage reports and holds. The [October 27 study](../2026-10-27-counter-epochs/report.md) tested counter restarts after completed work. These studies kept the total budget fixed.

This study changes that boundary. Its contribution is a declared five-rule cap-change corpus, separate actual and possible-use outcomes, every SQL statement after connection setup, and an independently implemented expectation. Reservations, revision checks, and current-state guards are established methods. The limited [source search](source_search.md) does not prove research priority. No new protocol is claimed.

## Method

### Plan and input contract

The [plan](plan.md) was frozen at 13:40:06 UTC before main implementation. A separate agent froze its formula specification at 13:41:34 UTC, before reading the main source. The main source was frozen at 13:42:37 UTC before execution. Independent counts were shared only after the main freeze. A schema comparison adapter was frozen before its reviewer read main results. The source hashes and access order are saved. This reduces implementation copying but does not remove shared assumptions.

Initially the ledger has spent use s0, one hold a for job A, cap `C0=s0+a+slack`, and revision zero. Job A settles once for x units, where `0<=x<=a`. Until then, the full a remains covered. The future x value is not available to a rule before settlement. New job B requests b units and uses exactly b if accepted. No cancellation or refund is available.

Enumerate `s0 ∈ {0,1,2}`, `a ∈ {1,2}`, `x ∈ {0,...,a}`, `slack ∈ {0,1,2}`, `n ∈ {0,...,C0-1}`, and `b ∈ {1,2}`. The requested new cap n is strictly lower than C0. There are 324 numeric settings. Each receives all 12 orders of four events R,U,S,B with R before U. Thus each rule has `324 × 12 = 3,888` cases. Five rules give 19,440 cases. These ranges and orders are selected inputs, not a random sample.

The four events are:

- R: the cap caller reads all four ledger fields in one SELECT. It fetches the result and ends the read. The saved values remain in application memory.
- U: the cap caller applies its rule. If accepted, it sets the cap to n and increments the revision. Otherwise it changes no ledger field.
- S: A settles. It adds x to spent use, clears its hold, and increments the revision. It must record this use even if a prior cap change was invalid.
- B: the job caller accepts only if `spent+hold+b<=cap`. If accepted, it adds b to spent use and increments the revision. Otherwise it changes no field.

U, S, and B each use `BEGIN IMMEDIATE`, the check and update, then COMMIT. Separate connections serve the cap caller, A, B, and audit. The runner executes the prescribed order. This produces controlled interleavings between R and U, not parallel stress. There is no external provider action.

### Five cap-change rules

All rules receive the same R read. Some baselines deliberately ignore relevant fields. Define `L=spent+hold`.

| Rule | Condition to apply n at U |
| --- | --- |
| BlindSet | No load condition |
| SpentOnly | Current spent use is at most n |
| CachedCover | L saved at R is at most n |
| VersionedCover | L saved at R is at most n, and the current revision equals the saved revision |
| AtomicCover | Current L is at most n, checked inside the write transaction |

AtomicCover rechecks the current state even if the earlier state would have refused. Revision changes include settlement with unchanged L. No rule retries. There is one conditional cap request per case. Refusal preserves C0; it is not a promise to apply n later.

### Measures and controls

An **unsafe reduction** accepts n when current L is greater than n. A **feasible refusal** refuses n when current L is at most n. A covered-use breach is `L>C`; an actual-use breach is `spent>C`. Both use the applied cap C. An unaccepted target n is not used as the active cap. Scores retain the first breach event and maximum excess, as well as final actual excess.

We distinguish a cap already below spent use at U from one that covers spent use but not its hold. A later actual breach at S can result from the earlier unsafe cap change. B is scored against its own current guard; it is not blamed for an earlier invalid cap write.

Six named controls cover an already impossible target, pending liability, B use between R and U, returned unused hold, settlement with unchanged L, and a serial feasible decrease. They repeat selected primary settings and are not extra independent samples. Two database controls check rollback of all changed fields and a refused conditional write that leaves every field unchanged. A separate connection sees only committed values. Integrity checks and reopened final rows are retained.

Every case saves its initial state and before/after state at four events. This gives 174,960 primary state records, including repeated boundary states. It is not that many independent trials. The package also retains 77,760 event steps, 38,880 cap/job decisions, 50 overlapping summary rows, five matched-rule tables, and the first adverse examples in declared order.

## Results

All planned cases completed. Every row below has 3,888 cases. Unsafe changes and feasible refusals are subsets of the corresponding accepted and refused requests.

| Rule | Cap accepted | Unsafe reductions | Actual-use breach cases | Exposure without actual breach | Feasible refusals | B accepted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BlindSet | 3,888 | 2,811 | 2,523 | 288 | 0 | 1,920 |
| SpentOnly | 1,653 | 576 | 288 | 288 | 0 | 2,247 |
| CachedCover | 1,095 | 219 | 189 | 30 | 201 | 2,475 |
| VersionedCover | 570 | 0 | 0 | 0 | 507 | 2,511 |
| AtomicCover | 1,077 | 0 | 0 | 0 | 0 | 2,418 |

The number of refused cap requests is 3,888 minus accepted requests. AtomicCover refuses 2,811 requests that do not fit at U. Its zero-breach result does not mean it meets every requested lower cap.

All 11,571 accepted B actions across the five rules passed their current guard and left L within the cap at that action. Yet the first three cap rules still broke the bound. This supports H1 and H2: a complete admission guard does not cover a separate cap setter.

BlindSet accepts 2,235 caps already below spent use and 576 that omit possible held use. SpentOnly removes the first group but retains all 576 hold failures. Of these, 288 later exceed the cap at S; the other 288 never exceed it in actual use. CachedCover has 165 cases already above n in spent use at U and 54 with hold exposure only at U. Of the latter, 24 later exceed the cap and 30 do not. These are designed branch counts, not estimated probabilities.

Every first covered-use breach occurs at U. The maximum actual excess is six units for BlindSet and two for SpentOnly or CachedCover. Both complete rules have zero excess. Actual use never decreases, and no later cap change occurs, so any actual breach remains at the end. Covered-use breaches can disappear when unused hold is released. Thus final actual totals miss unsafe reductions in the exposure-only column, as predicted by H4.

VersionedCover accepts 507 fewer reductions than AtomicCover and refuses 507 changes that currently fit. This supports H3. Its conservative revision condition is not an implementation error. It accepts only when the saved state is still current. AtomicCover uses current numeric feasibility directly.

The higher B count under VersionedCover is not a general utility advantage. Refused reductions leave a higher old cap active. It admits 93 more B jobs than AtomicCover in matched inputs while completing fewer requested reductions. CachedCover differs from AtomicCover on 420 cap decisions: 219 unsafe extra acceptances and 201 feasible refusals. Complete matched counts are in [paired.json](results/paired.json). Groups in [summary.csv](results/summary.csv) overlap and must not be added.

### Retained examples

In the pending-liability control, spent use is zero, A holds two, and the cap is two. The requested cap is one. SpentOnly accepts because zero fits. B refuses because the hold already exceeds one. A then settles for two, so actual use exceeds the new cap. B's refusal cannot undo the earlier unsupported success at U.

In the intervening-B control, R sees L=1 under cap three and target one. B spends one, so current L becomes two. CachedCover then uses the old value and applies one. AtomicCover and VersionedCover refuse. This is a stale application read despite atomic SQL writes.

In the returned-hold control, R sees L=2. A then settles for zero, reducing L to zero. The target is one. CachedCover still refuses from its old read; VersionedCover refuses from that read and changed revision. AtomicCover applies one. In the unchanged-total control, A settles for its full hold of two. L stays two, but the revision changes. VersionedCover refuses target two while AtomicCover accepts it. The latter change is still a reduction from the initial cap three.

The first adverse examples are saved in [witnesses.json](results/witnesses.json). They are the first in the declared enumeration order, not claimed global minima.

## Conditional arguments

At the initial state, `L=s0+a<=C0`. R changes nothing. S changes covered use by `x-a<=0`. An accepted B checks `L+b<=C` and increases L by b. Thus neither S nor a properly guarded B can be the first covered-use violation. Only an accepted U with `n<L` can cause it in this model.

AtomicCover directly excludes that U condition. VersionedCover also excludes it: an unchanged revision means no ledger effect occurred after R, and its saved feasibility test then uses the current L. Induction over the four events proves both preserve `L<=C`. This requires every relevant effect to update the revision and every caller to use the declared transaction boundary. No bypassing writer is present.

The stale-check failure has a compact expression. Let d be b if an accepted B lies strictly between R and U, and zero otherwise. Let h be `a-x` if S lies between R and U, and zero otherwise. Then

`L_U = L_R + d - h`.

CachedCover is unsafe exactly when `L_R<=n<L_R+d-h`. It refuses a feasible reduction exactly when `L_R+d-h<=n<L_R`. An intervening charge can invalidate earlier success evidence. Returned unused capacity can invalidate an earlier refusal. A revision check blocks both kinds of changed state, including harmless or offsetting changes. The current guard uses the numeric condition at U.

These are conditional arguments for known mechanisms. They do not show that a real provider reports every charge, honors a hold, or can revoke prior work. If irreversible spent use alone exceeds n, no non-refunding cap update can truthfully claim this strict bound has been achieved.

## Reproduction and uncertainty

Two full SQL runs produced identical bytes for all 11 durable scientific files, including the database, SQL log, and state traces. Both integrity checks returned `ok`. The separate formula evaluator matched both runs: all 174,960 primary state records, 38,880 U/B decisions, 428,776 logged SQL statements, 30 control-rule cases, 19,471 reopened rows, summaries, paired results, and 11 first adverse examples. Its schema adapter was written after source access; its underlying formulas were frozen earlier. See [independent_review.md](independent_review.md).

The environment was Python 3.13.7, SQLite 3.50.4, and macOS 26.7.2 on arm64. CPU times were 4.413954 and 4.510571 seconds. Wall times were 6.025109 and 6.134285 seconds. These are resource records, not performance comparisons. Each run used no external call or model API. There is no random seed or training/test split.

Each in-run output measurement was 6,536,149 bytes before the environment record. The 11 durable scientific files total 6,503,381 bytes after process exit. The 32,768-byte difference is consistent with a temporary SQLite shared-memory file. The reopened read connection was not explicitly closed before the in-run measurement. Its context manager ends a transaction but does not close the connection. We retain the frozen code and distinguish these measures. No individual temporary file capture was made. This reporting issue does not change the saved ledger or results.

Runs stayed within 120 CPU seconds, 450 wall seconds, and 200 MB saved output. Wall and file checks are periodic, not hard real-time guarantees. Peak memory was not measured. No unexpected main-run or independent-comparison failure occurred. The rollback and refused-update controls were planned successful tests, not failures to discard.

Exact enumeration gives exact counts for this input set. It does not provide a population failure rate, confidence interval, or significance claim. Shared assumptions can make independent implementations agree incorrectly. [README.md](README.md) gives commands, platform requirements, and byte-comparison limits.

## Discussion and limitations

A lower stored number and an achieved strict bound are different results. The cap-change operation must account for past use and remaining obligations. Guarding only new work does not establish that result. A failed reduction should be reported as refused while the old cap remains active.

The study has one hold, one cap request, one new job, small integers, and truthful final settlement. It excludes cancellation, refunds, price changes, late billing, multiple cap requests, crashes, untracked writers, distributed transactions, and hostile input. There is no live website test or computer-use agent action. The evidence is real local SQL execution of an invented workload. No result tests Kubernetes or Go behavior. Different prospective-limit contracts can legitimately permit settings below existing use.

We do not measure eventual completion, fairness, throughput, or portability across database engines. We do not claim that rejecting an impossible reduction meets the owner's desired lower budget. A queued reduction, task cancellation, or explicit grandfathering policy requires a different contract and further tests.

## Ethical issues, rights, and review status

Codex generated the study, code, analysis, and report. Separate Codex agents prepared independent formulas and checked sources, method, and results. The exact model build was not exposed. No human or external peer review occurred. No university affiliation, endorsement, or certification is claimed.

Inputs are invented. No private account record, credential, paid compute, or new permission was used. No external implementation, dataset, figure, or long quotation was copied. Source text is paraphrased and attributed. No new license is assigned. The main misuse risk is to present these finite counts as a real-system safety guarantee. Relevant NeurIPS checklist topics are used as a review aid only [6].

## References

1. Kubernetes. [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/). Selected sections checked on 2026-10-28.
2. The Go Authors. [rate package, v0.16.0](https://pkg.go.dev/golang.org/x/time@v0.16.0/rate). Selected reservation and limit-change documentation checked. This version is not claimed as latest.
3. Genliang Zhu and Chu Wang. [Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation](https://arxiv.org/html/2610.00349v1). Preprint v1. Selected sections checked; not a full-paper review or reproduction.
4. SQLite. [Isolation In SQLite](https://www.sqlite.org/isolation.html). Connection and writer-isolation sections checked.
5. SQLite. [Transaction](https://www.sqlite.org/lang_transaction.html). Transaction lifetime, modes, and rollback sections checked.
6. NeurIPS. [Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist). Review aid, not approval or submission compliance.

All source access dates are 2026-10-28. Full entries and read scopes are in [references.bib](references.bib) and [source_search.md](source_search.md).
