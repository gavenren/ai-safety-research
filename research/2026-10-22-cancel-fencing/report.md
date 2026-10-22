# Cancellation across restarts: when an old worker can still act

Date: 2026-10-22, America/Toronto. Study type: exact synthetic model.

## Abstract

A cancellation flag can return to “active” when a task restarts. This need not restore the authority of an old worker. We enumerate 612 event schedules across one to eight restarts and compare seven fixed rules. This gives 4,284 model cases. A reused active flag admits 364 old effects after cancellation. Modulo-2 and modulo-4 generation checks admit 184 and 90. A unique generation checked before use admits 80. A receiver that rejects tokens below its highest observed token admits 516 old effects before it sees the new worker's token, but none after it. An atomic current-generation check and a fence installed with cancellation admit no old effects after cancellation. Every rule accepts all 612 current-worker actions. These finite model counts are not website or AI-agent failure rates. The contribution is the saved regression corpus and its comparison of three different failure conditions. The underlying methods are established.

## Research question and safety relevance

Can an old worker act after its run is cancelled, even when a token is unique? What changes when tokens repeat or the receiver has not learned that the run ended?

A **generation** identifies a run of a task. A **guard** is a condition that must pass before an effect. A **fence** makes the receiver reject effects from a retired generation. A **high-water mark** is the greatest token the receiver has seen. A **schedule** is one allowed order of model events. An **atomic** check and effect form one indivisible step. A **stale effect** is an accepted action from the old worker after the first cancellation. Here, every effect is only an inert item in a local list.

A user can cancel an agent task and then start new work. The new work can be valid while a delayed action from the old run is invalid. A task-level active flag cannot express this distinction by itself. A completion claim about cancellation must state the receiver boundary at which old effects are excluded.

## Related work and contribution

Chubby describes delayed requests and recipient checks of lock generations. These are established mechanisms. We do not implement or test Chubby. [Burrows, 2006, Sections 2.3–2.4](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf)

Kleppmann explains that a pause can occur between a client check and its write. His fencing example requires the receiver to check increasing tokens. Our high-water rule models only that token-order condition; it is not a test of Redlock. [Kleppmann, 2016](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html)

Zhu and Wang distinguish a root cut from a protected receiver fence. Their preprint includes delayed-effect and stale-process tests. Our corpus adds repeated restarts and bounded token reuse to a much smaller single-receiver model. It omits their delegation, multiple authority roots, certificates, and worker-process tests. We did not verify their implementation or proofs. [Zhu and Wang, preprint v1, 2026, Sections 4.4 and 6.2](https://arxiv.org/html/2609.21284v1)

The [October 16 study](../2026-10-16-field-snapshot/report.md) tests reused versions during field reads. The [October 17 study](../2026-10-17-repair-dependencies/report.md) tests stale decisions during repair. The present contract permanently retires one worker, permits a new worker, and tests what the receiver knows. It does not claim a new concurrency method. The [search record](source_search.md) and [timing correction](source_supplement.md) give reading limits and access failures. The limited search does not prove novelty.

## Method

The [plan](plan.md), [configuration](config.json), and source record were hashed before implementation. [freeze.json](freeze.json) records the time and hashes. [implementation_freeze.json](implementation_freeze.json) records the code hash before the first run. No model or hypothesis changed after execution.

The old worker holds generation 0. Initially the controller is active at generation 0, and the receiver mark is 0. For each restart count n from 1 to 8, control events have the fixed order `A1,R1,...,An,Rn`. Cancellation `Ai` sets the controller inactive and advances its generation to i. Restart `Ri` makes that generation active. `A1` permanently retires the old worker. A later restart never authorizes that worker again.

Three events are added. `C` checks whether generation 0 is current and active. `O` attempts the old effect. `N` attempts the new effect with token n. All schedules with `C` before `O` and `Rn` before `N` are included. `C` remains in schedules for rules that do not use it, so all rules receive the same schedules. `N` uses a current check at its effect boundary, with no delayed precheck. This is a current-work control, not a test of many new workers.

| Rule | Old effect condition | Required capability |
| --- | --- | --- |
| Active flag | Controller is active at O | Read the current active flag at commit |
| Modulo 2 | Active, and generation remainder is 0 after division by 2 | Atomic check of a reused generation |
| Modulo 4 | Active, and generation remainder is 0 after division by 4 | Atomic check of a reused generation |
| Unique precheck | Use the Boolean saved by C | Read a unique generation before use |
| Unique at commit | Active, and current generation equals 0 at O | Authoritative generation check atomic with effect |
| Receiver high-water | Token 0 is at least the receiver mark | Receiver checks and advances its mark on accepted writes |
| Cancellation fence | Same token condition, but each Ai also advances the receiver mark | Cancellation acknowledgement includes the receiver barrier |

The last rule has a stronger interface. Its acknowledgement and receiver barrier are one model event. The high-water rule receives no cancellation update and promises only token order after a newer token is observed. Failure under our immediate-cancellation contract is not failure of that weaker promise. The model assumes atomicity and retained state. It does not test storage durability or barrier propagation.

There are `choose(2n+3, 2)` schedules at each n. Keep the control chain ending in `N` fixed. Choose two positions for `C` and `O`, in that order. Counts are 10, 21, 36, 55, 78, 105, 136, and 171; the sum is 612. The main recursive generator is checked against this separate insertion method.

A stale action is accepted `O` after `A1`, regardless of later restarts. Each rule has 604 such attempt schedules and eight valid pre-cancellation attempt schedules. Measures count stale acceptances, stale acceptances after `N`, stale acceptances while inactive, rejection of valid old actions, and acceptance of `N`. Every trace is saved, including rejections. Unexpected execution or file errors stop a run and remain recorded. No case was dropped.

## Results

All six planned hypotheses hold in this corpus. Each row uses the same 612 schedules. The two middle columns are subsets of stale acceptances.

| Rule | Stale accepted out of 604 | After new action | While inactive | New actions accepted out of 612 |
| --- | ---: | ---: | ---: | ---: |
| Active flag | 364 | 88 | 0 | 612 |
| Modulo 2 | 184 | 48 | 0 | 612 |
| Modulo 4 | 90 | 28 | 0 | 612 |
| Unique precheck | 80 | 8 | 36 | 612 |
| Unique at commit | 0 | 0 | 0 | 612 |
| Receiver high-water | 516 | 0 | 240 | 612 |
| Cancellation fence | 0 | 0 | 0 | 612 |

Source: [summary.json](summary.json). [summary.csv](summary.csv) gives all 56 horizon/rule rows. No rule rejects any of the eight valid old actions. There are zero unknown cases.

The first modulo-2 stale witness occurs at two restarts. The first modulo-4 witness occurs at four. A short test can therefore miss token reuse. For example, `A1,R1,A2,R2,C,O,N` makes generation 2 look like token 0 under the modulo-2 guard.

A unique token alone does not close a check-use gap. In `C,A1,O,R1,N`, the old check passes before cancellation. Its stored Boolean then admits an effect while the controller is inactive. A check at the effect boundary rejects it.

The high-water rule has a different gap. In `A1,R1,C,O,N`, the controller has cancelled the old run, but the receiver mark is still 0 at `O`. It admits the old effect. After `N`, the mark is n, greater than 0. Every later old action is rejected. The cancellation fence instead raises the mark at `A1`.

## Validation and derivation

The interpreter retains every state transition. A separate index-based formula in the same program checks all 4,284 old acceptance results. It does not call the interpreter. Nine named hand controls give 63 rule rows, including fixed expected witnesses. Two schedule generators agree on every schedule. These are internal cross-checks, not an independent agent implementation.

The formulas follow from the event contract. Let a and r be the numbers of cancellations and restarts before `O`. The controller is active exactly when a=r. Its generation is a. The active rule checks a=r. A modulo-m rule also checks `a mod m=0`. The unique precheck passes exactly when `C` precedes `A1`. The unique commit check passes exactly when `O` precedes `A1`. For the write-only high-water rule, the mark is 0 before `N` and n after it; old acceptance is exactly `O` before `N`. For the cancellation fence, the mark is positive after `A1`; old acceptance is exactly `O` before `A1`. `N` occurs after `Rn`, its token is n, and no later cancellation exists. Every current-worker check passes. These statements exhaust this model's transitions, not those of a larger system.

A clean repeat reproduced all six deterministic files byte for byte. [reproduction.json](reproduction.json) gives their hashes. Two model runs completed. One document-write command used the wrong working directory, and the first comparison command could not find its not-yet-created script. The documents and comparison script were then saved at the correct paths. The comparison passed without a third model run. [failed_checks.md](failed_checks.md) records this issue and the source-reading timing correction. A separate agent wrote and froze an evaluator before reading the main code or results. All 4,284 records and 51,408 field comparisons matched, including full traces. It also checked all 56 summary rows, witness selection, frozen hashes, and the repeat comparison. See [separate_review.md](separate_review.md).

## Discussion

An active flag answers whether some work is active. It does not identify which worker may act. A generation that repeats can restore an old token's apparent validity. A unique generation avoids reuse, but a pre-use check still needs a valid link to the effect boundary. A receiver mark needs a newer value before it can reject an old one.

The two zero-count rules rely on stronger atomic checks or a cancellation barrier at the receiver. The results do not show that client-only code can supply those capabilities. A real provider can lack the required interface.

## Limitations and uncertainty

This is complete enumeration of a designed finite model, not a random sample. There are no confidence intervals, significance claims, or production failure rates. Repeated prefixes and unused C events create multiplicities. The counts depend on this corpus and its one-to-eight restart bound.

There is one receiver, one old worker, and one final new worker. Every effect uses the modeled guard. There are no missing receivers, bypass paths, crashes, storage loss, delayed barriers, network requests, payload changes, or physical effects. No real cancellation API or browser agent was tested. Immediate cancellation at `Ai` is an explicit contract, not a claim about provider semantics. A fence cannot undo an earlier effect. This model does not prove that all processes have stopped or that a business task is complete. No model was trained or evaluated. There is no train/test leakage issue; common modeling errors remain possible.

## Ethical and misuse considerations

All inputs and effects are synthetic. No private data, account records, or credentials were used. No paid service or model API was used. The code is a small defensive consistency test, with no production exploit. The main misuse risk is treating zero failures as a general safety certificate. Required interfaces and limits are stated. Sources are linked and attributed; full text is not redistributed. No reuse license is assigned to the owner's new work.

## Reproduction, AI use, and human review

The [README](README.md) gives commands and file roles. Python 3.13.7 and its standard library ran the model on one arm64 macOS host. The first run used 0.193 process CPU seconds and 0.210 wall seconds, with about 24.7 MB peak resident memory. The repeat used 0.208 process CPU seconds. These measurements are not performance benchmarks. Each run had a 60 CPU-second and 120 wall-second gate. Exactly two full runs were done. Writing and review required additional unmeasured assistant work.

Codex generated the design, code, source review, and report. The exact immutable model build was not exposed. The finite model contains no learned agent. A separate agent independently checked the calculation and reviewed the claims and three primary sources. No human review or external peer review occurred. No affiliation, endorsement, or certification is claimed. The [review checklist](review_checklist.md) uses NeurIPS guidance only as a review aid.

## References

Full details are in [references.bib](references.bib). The source record states which parts were read.
