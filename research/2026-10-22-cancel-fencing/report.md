# Cancellation across restarts: when an old worker can still act

Date: 2026-10-22, America/Toronto. Study type: exact synthetic model with a controlled production extension.

## Abstract

A cancellation flag can return to “active” when a task restarts. This need not restore the authority of an old worker. We enumerate 612 event schedules across one to eight restarts and compare seven fixed rules. This gives 4,284 model cases. A reused active flag admits 364 old effects after cancellation. Modulo-2 and modulo-4 generation checks admit 184 and 90. A unique generation checked before use admits 80. A receiver that rejects tokens below its highest observed token admits 516 old effects before it sees the new worker's token, but none after it. An atomic current-generation check and a fence installed with cancellation admit no old effects after cancellation. Every rule accepts all 612 current-worker actions. These finite model counts are not website or AI-agent failure rates. The contribution is the saved regression corpus and its comparison of three different failure conditions. The underlying methods are established.


Eight selected cases on Google Drive and Calendar added six browser saves and two blocked commands. A new check blocked the old command before dispatch; cancellation after the last check still allowed the old save. Native atomic fencing was not tested, and the missing reopened Calendar read is disclosed.

The sections below describe the original synthetic study. The dated production extension at the end gives the later live evidence, checks, and limits.

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

There is one receiver, one old worker, and one final new worker. Every effect uses the modeled guard. There are no missing receivers, bypass paths, crashes, storage loss, delayed barriers, network requests, payload changes, or physical effects. The original model did not test a real cancellation API or browser agent. Immediate cancellation at `Ai` is an explicit contract, not a claim about provider semantics. A fence cannot undo an earlier effect. This model does not prove that all processes have stopped or that a business task is complete. No model was trained or evaluated. There is no train/test leakage issue; common modeling errors remain possible.

## Ethical and misuse considerations

All inputs and effects in the original model are synthetic. It used no private data, account records, or credentials. No paid service or model API was used. The code is a small defensive consistency test, with no production exploit. The main misuse risk is treating zero failures as a general safety certificate. Required interfaces and limits are stated. Sources are linked and attributed; full text is not redistributed. No reuse license is assigned to the owner's new work.

## Reproduction, AI use, and human review

The [README](README.md) gives commands and file roles. Python 3.13.7 and its standard library ran the model on one arm64 macOS host. The first run used 0.193 process CPU seconds and 0.210 wall seconds, with about 24.7 MB peak resident memory. The repeat used 0.208 process CPU seconds. These measurements are not performance benchmarks. Each run had a 60 CPU-second and 120 wall-second gate. Exactly two full runs were done. Writing and review required additional unmeasured assistant work.

Codex generated the design, code, source review, and report. The exact immutable model build was not exposed. The finite model contains no learned agent. A separate agent independently checked the calculation and reviewed the claims and three primary sources. No human review or external peer review occurred. No affiliation, endorsement, or certification is claimed. The [review checklist](review_checklist.md) uses NeurIPS guidance only as a review aid.

## References

Full details are in [references.bib](references.bib). The source record states which parts were read.

## Production extension: cancellation checks before browser saves

Date: 2026-10-22. This extension used temporary records in Google Drive and Google Calendar. It is separate from the synthetic schedules above.

### Question and method

Can a client check block an old command after local cancellation? Can a command still change a real website if cancellation occurs after the check?

A client is the local program that decides whether to send a browser action. A generation is the number of an authorized run. Cancellation retires generation 0. Restart authorizes generation 1. This cancellation is a local test signal. It is not a request for Google to cancel pending work.

We used four fixed cases per service. Each case had a fresh temporary record. A connector created the fixtures and read their baselines. Browser actions made the scored changes. Read-only connectors then inspected the exact native record IDs. The Drive action renamed an empty test folder. The Calendar action changed a synthetic description on a private, Free, nonrecurring all-day event on October 1, 2026. No external attendees or reminders were used.

The local helper wrote its decision and event order before the browser action. It did not send a browser command or claim that a save occurred. C1 reused an initial check made before cancellation. C2 repeated the generation check after cancellation and restart. C3 placed cancellation after the last client check but before browser dispatch. C4 used a valid generation-1 command. C1 and C3 were deliberate order tests, not spontaneous agent failures or measured network races.

The browser helper sent one logged save for each allowed case. It sent no save for C2. The scorer joined the decision record, browser observations, and saved-record read. It checked intended field values and unchanged exposed connector fields against the baseline. Calendar description comparison removed only trailing CR and LF. It did not remove spaces, parse HTML, or ignore case.

### Results

| Case | Client order | Drive: logged saves / final value | Calendar: logged saves / final value |
| --- | --- | --- | --- |
| C1 | Initial check; cancel; restart; use cached permission | 1 / OLD | 1 / OLD |
| C2 | Initial check; cancel; restart; check generation again | 0 / BASE | 0 / BASE |
| C3 | Last client check; cancel; restart; use admitted command | 1 / OLD | 1 / OLD |
| C4 | Cancel; restart; check the new generation | 1 / NEW | 1 / NEW |

All eight assigned cases were retained. The six logged saves have browser records and matching native-ID readback. The four old-command cases, C1 and C3 on both services, saved OLD after local cancellation. The two C2 cases retained BASE after the local gate refused dispatch. The two current-generation controls saved NEW.

Every checked unchanged connector field matched its baseline. Drive changed its title and modification timestamp in the three save cases. Calendar changed only its description. Both C2 connector responses matched their complete baselines. No extra cancellation dispatch record was present in the saved case log. This is a log count, not proof that the provider performed exactly one internal write.

All local preparations occurred from 16:28:58 to 16:31:59 UTC. Final connector reads were recorded from 16:29:46 to 16:32:15 UTC. Each case's last recorded observation was within eight minutes of preparation. The Calendar C2 connector read preceded its blocked-case UI inspection. Both observations followed the no-dispatch decision. The report does not reverse those times.

Two local scoring runs produced identical result bytes. They used Python 3.13.7 and the standard library. Their CPU times were 0.000595 and 0.000719 seconds. These times exclude browser and provider work. The replay did not create more website trials. See `live_reproduction.json`.

### Interpretation

The result supports the client-side distinction in the synthetic study. A fresh check can block an old command in the selected C2 order. Permission cached before cancellation can still be used to change a real record. Moving the check close to dispatch does not remove a gap between checking and sending: C3 still saved OLD.

The services were not asked to enforce the local generation. Accepting these valid account writes is not evidence of a Google defect. This study does not test an atomic receiver fence. Such a fence would require the service to check the relevant cancellation state as part of the write itself. Google Calendar documents conditional writes with ETags, but these browser trials did not use that interface. [Calendar version guide](https://developers.google.com/workspace/calendar/api/guides/version-resources)

The contribution is a small controlled production extension with saved evidence. The cancellation method and check/use gap are established concepts. This is not a claim of a new algorithm or a general agent safety rate. The original related-work discussion applies to the method. The Google [Drive File reference](https://developers.google.com/workspace/drive/api/reference/rest/v3/files) and [Calendar Event reference](https://developers.google.com/workspace/calendar/api/v3/reference/events) define relevant fields; they do not guarantee these observed outcomes.

### Procedure deviations and limits

The pure rule and case plan were frozen before every preparation. The revised runtime helper freeze was written at 16:29:21 UTC, about 23 seconds after Drive C1's preparation. The preparation records the same helper hash as the later freeze. The freeze preceded that case's browser dispatch. This establishes byte agreement, not a claim that the helper freeze preceded all preparations. The original helper review finding and its correction remain recorded in `runtime_intent_review.md`.

The frozen plan called for a reopened or reloaded UI plus an independent connector read. Drive recorded a reload after each rename. Calendar's three save cases have before-save and filled-editor observations, a postclick observation, and an independent saved-record read. They do not have a reopened post-save editor record. The persisted description and exposed collateral fields are verified by the connector. Calendar's all-day UI check is before Save; a separate post-save all-day UI check was not recorded. This is a readback procedure deviation, not a failed or repeated save. No case was removed because of it.

The four case types use different orders. They are not randomized policy arms. Do not treat four old saves and two blocked commands as a causal percentage improvement. There is one case per type and service. No crash, generation wrap, stale replica, third-party writer, delayed server request, hidden duplicate write, or concurrent controller was tested. The client state is local and sequential. It is not a shared receiver state.

Drive's connector did not expose trashed state or a version counter. The active parent view supplied scoped UI evidence. Calendar's connector returned converted date-time strings, not a raw all-day API flag. Checked exposed fields and before-save UI values do not establish every hidden provider property. The result counts concern this declared observation scope.

### Evidence, reproduction, and review

`live_trace.json` contains synthetic field values, aliases, timestamps, decision events, check results, and private-evidence hashes. Raw IDs, account data, and full UI snapshots remain private. `build_live_trace.py` verifies the private-to-public mapping when the private evidence is available. `live_analysis.py` reproduces the public scores without an account. `live_README.md` gives commands and the limits of reproduction.

Codex generated this extension and its code. Browser tools executed the visible actions. Provider connectors created test records and read saved state. Python ran the local decisions and scoring. No model was called within the scorer, and no paid compute was used. The browser and connector build IDs were not exposed in these records. No human review or peer review occurred. A separate agent reviewed this cancellation extension and repeated the scoring. The review passed for the stated scope. See [live_review.md](live_review.md). The helper review is a separate, narrower check.

Only temporary records were used. Public evidence must exclude personal data from the surrounding UI. Cleanup was verified after scoring. The Drive parent is in Trash, and its 21-folder test scope has no active results. All 23 Calendar fixtures have exact-ID status cancelled, with no active results in the bounded primary-calendar test query. These are counts for the complete five-study run. They do not prove permanent erasure or account-wide absence. See [live_cleanup.md](live_cleanup.md) and [live_cleanup.json](live_cleanup.json). No new license is assigned.
