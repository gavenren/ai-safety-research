# When a fresh screen is not enough: retry timing and view scope for computer-use agents

Date: 2026-10-15 (America/Toronto).  
Research type: formal analysis, exhaustive synthetic event study, controlled local browser pilot, and live test-site experiment.  
Codex generated this paper, code, and analysis. No human or external peer review occurred. The browser studies test real agent actions under supplied rules. The latest extension uses two external public test sites.

## Abstract

Computer-use agents can repeat an action when its result is not visible. We compare supplied retry rules in three separate studies. An exhaustive event model covers 336 cases and 13,440 runs. In its main append grid, first-empty retry creates 60 duplicates with checks every tick. Truthful terminal status and an adequate timing bound each create none. An 18-trial local browser pilot then produces four duplicates under absence retry and none under terminal status or a 24-second bound. It does not show a general browser speed gain. The new extension runs 60 trials on two live public TodoMVC test sites. A Completed view hides active tasks by design. In that view, immediate absence retry and a 24-second wait each produce duplicates in five of six trials. A rule that checks the All view produces no duplicates and four clean confirmations in six trials; Closure confirms none in that view. The All-view control fails in nine of 30 trials, and ten trials finish with no task after reload. These failures prevent a general task-success claim. The contribution is reproducible evidence that read freshness, view scope, execution closure, and confirmed completion are separate properties. The live sites use browser storage and supplied procedures. These results are not production error rates or a new general retry protocol.
## 1. Research question and contribution

An agent clicks a button. The next observation shows no new item. Should the agent click again? This question applies to any action that creates an additional record when repeated. A **non-idempotent action** can change the intended result when it is repeated. An **idempotent action** has the same intended effect when repeated [5].

We ask how the completion delay of an earlier action and the delay of an observation affect retry safety, confirmed completion, and observation cost. **Execution closure** means that an earlier attempt can no longer create a future effect. A current read and execution closure are different properties.

The contribution of this paper is its specific test design and full comparison. We combine pending writes, delayed negative reads, observation schedules, and post-stop effect checks. We include a conservative no-retry control, an adequate fixed-bound baseline, and a matched server-deduplication control. We publish every event trace, including writes that finish after the controller stops. This contribution is a small synthetic benchmark, interface audit, local browser pilot, and live test-site comparison. It is not a new exactly-once protocol, learned agent, or general theorem. The limited source search cannot prove that this is the first such comparison.

Reliable completion matters because an extra record can be harmful even when the original task eventually succeeds. Faster tools are useful only if the controller interprets their observations correctly. We therefore keep duplicate prevention, useful completion, delay, and call count separate.

## 2. Related work

CUA-Speedrun studies speed and cost across computer-use configurations. Its fast input-output analysis shows that a screenshot can arrive before an application updates its interface. The tested agent can then take extra steps. Our study isolates retry effects with controlled policies. It does not reproduce that model experiment [1].

RStackBench separates visible success from persisted task state. Its controlled browser tests distinguish delayed persistence from a missing required action. It tests individual fault layers and identifies combined faults as future work. Our model combines a pending non-idempotent write with a negative read and scores all later effects. We do not reuse its code, tasks, or data [2].

CapLease studies repeated agent proposals after uncertain execution. It uses durable authorization state and states the need for a suitable external idempotency contract. We do not propose a replacement for that system. Our comparison concerns the evidence that permits one retry, under explicitly different server contracts [3].

RIFL already treats lost results and duplicate execution as systems problems. Its browser example discusses uncertain outcomes and recognition of prior effects. HTTP Semantics also limits automatic retries of non-idempotent requests. These sources establish that absence of a visible result is not a general retry guarantee [4,5].

The original source record contains 15 exact queries, read sections, versions, access limits, and additional related work. The browser extension adds two queries and a new check of the closest sources. RStackBench already reports a small model planning pilot; real-agent execution alone is not a new research idea [7]. See [source_search.md](source_search.md), [browser_source_search.md](browser_source_search.md), and [references.bib](references.bib). The study does not claim that waiting, verification, durable status, or duplicate suppression is new.

WebVoyager already evaluates agents on live websites [8]. WAREX tests infrastructure faults on browser benchmarks [9]. The new experiment uses normal list filters on two hosted versions of TodoMVC. It tests the scope of the evidence used by a supplied retry rule. It does not reproduce either benchmark. The TodoMVC specification defines task creation, filters, and browser storage [10]. Microsoft uses its hosted TodoMVC demo in its test generator guide [11]. See [live_source_search.md](live_source_search.md) for the added search and source limits.

## 3. Method

### 3.1 Saved plan and finite environment

The plan and input configuration were saved before implementation or numerical analysis. A design review then changed the completion guard, still before analysis: an observed count of two stops with a detected duplicate and no completion claim. An observed count of one is the only completion claim. The original hash, amendment time, and final hashes are in [input_manifest.json](input_manifest.json). No cases or hypotheses changed.

Time is an integer **tick**, a synthetic time unit. It is not a measured second. The initial attempt starts at tick zero. Each attempt resolves after its assigned delay, either by committing one durable append or by dropping permanently with no effect. At most one retry is allowed. Both attempts refer to one desired item. A dropped attempt cannot later commit.

At time t, a query returns the exact count and attempt status at historical time max(0, t-L), where L is the case's fixed read lag. Status is pending, committed, or permanently dropped. Due resolutions occur before a query at the same tick. The retry is sent after the query. Each attempt has a positive delay. No controller sees the future delay or outcome before the observation reveals it.

The controller stops on a positive count: one gives a completion claim; two gives a detected duplicate. With no positive result it stops at tick 24. A deadline stop does not cancel an admitted action. Every admitted action continues until resolution, including actions sent at the deadline. The final audit occurs after the last admitted resolution or controller stop, whichever is later.

The model has no other writers, rollback, incorrect status, identity error, read error, or crash. Query calls have no added duration. Delay and call count are therefore separate measures, not a full service-latency model.

### 3.2 Five rules and two server contracts

Each rule makes the same initial submission and follows the same chosen query schedule. A retry is possible only after an empty observation and only if none has been sent before.

| Rule | Condition that permits the one retry |
| --- | --- |
| No retry | Never retry |
| Absence retry | The first empty observation |
| Timeout 8 | An empty observation at tick 8 or later |
| Bound 12 | An empty observation at tick 12 or later |
| Terminal status | The first attempt is observed as permanently dropped |

Timeout 8 uses the main maximum execution delay but ignores read lag. Bound 12 adds the maximum execution delay of 8 to the maximum lag of 4. It is an adequate timing baseline under the main contract. The terminal rule uses information from the same response that the other rules ignore. This extra information is an application capability, not an ability inferred from a screenshot.

Under **append semantics**, each successful attempt creates another item. Under **ideal deduplication**, all successful attempts for the same logical item produce at most one item. A dropped attempt does not prevent a later attempt from succeeding. This matched positive control assumes correct stable identity and server enforcement. The client cannot create this guarantee by assigning a local identifier alone.

### 3.3 Cases, schedules, and measures

The main grid uses both attempt delays in {1,2,4,8}, both outcomes in {commit,drop}, and lag in {0,1,2,4}. This gives 256 cases. The four query schedules are every tick, every 2 ticks, every 4 ticks, and backoff at {1,2,4,8,12,16,20,24}. Five rules and two server modes give 10,240 main runs.

The late-execution stress suite sets both delays to 12 and retains the four main lags: 16 cases. The stale-read suite uses the main delays but lag 8: 64 cases. Both use all rules, schedules, and modes. There are 3,200 stress runs. These suites break one timing bound and remain separate from the main grid.

A **duplicate** is a final effect count greater than one. A **clean confirmation** is a completion claim by tick 24 with exactly one final effect. An **unsafe claim** observes one item, claims completion, and later ends with a duplicate. A detected duplicate and a deadline stop make no completion claim. We also save zero effects and one effect without confirmation.

Mean clean time is the mean confirmation tick among clean cases. Comparisons between terminal status and Bound 12 use their jointly clean cases. The **capped clean-time score** uses the confirmation tick for a clean result and 24 otherwise. This defined score is not wall time. Query and submission counts are reported separately. Full rows and grouped summaries preserve all measures.

All cases are constructed. Equal weighting is a description of this grid, not an estimate of application frequencies. Some delay values repeat when a branch is not taken. These are designed factor combinations, not independent experimental observations. There is no training set, random sampling, fitted parameter, seed, significance test, or population confidence interval.

## 4. Formal boundary

A simple trace shows why freshness is insufficient. At tick 1, a current read sees zero items while the original attempt is pending. A retry commits at tick 2. The controller sees one item and stops. The original attempt then commits at tick 8. The final count is two. Scoring only the controller's stop state would miss the failure.

Consider two worlds with the same observation history before a retry decision. In one, the original attempt will commit later. In the other, it will drop. Suppose the retry succeeds and there is no later distinguishing observation before the decision. If a policy retries with probability r, its duplicate probability in the commit world is r. Its recovery probability in the drop world is also r. Thus a duplicate limit epsilon on this local decision also limits recovery to epsilon. This is a tight, conditional two-world result. It does not apply after new distinguishing evidence arrives and is not a claimed new distributed-systems theorem.

For terminal status, a retry is sent only after a truthful permanent drop. The original attempt therefore cannot add an effect later. At most one remaining attempt exists, so the final count is at most one. Delayed visibility can delay this decision but cannot reverse a permanent drop.

For Bound 12 in the main model, a query at t >= 12 has an as-of time at least 8. The first attempt has resolved by tick 8. If the returned count is zero, that attempt did not commit and cannot do so later. One retry is then safe. This argument fails when the declared execution or lag bound is false. Full assumptions, proofs, and the local ambiguity check are in [derivations.md](derivations.md).

## 5. Results

### 5.1 Current negative reads still permit unsafe retries

The following results use append semantics and queries every tick. Each rule has 256 cases. Time is in ticks. Mean clean time must not be compared across rows with different successful case sets as if those sets were matched.

| Rule | Duplicates | Clean confirmations | Unsafe claims | Mean queries | Mean clean time |
| --- | ---: | ---: | ---: | ---: | ---: |
| No retry | 0 | 128 | 0 | 14.750 | 5.500 |
| Absence retry | 60 | 132 | 56 | 10.109 | 5.848 |
| Timeout 8 | 12 | 180 | 12 | 12.125 | 8.022 |
| Bound 12 | 0 | 192 | 0 | 13.125 | 9.500 |
| Terminal status | 0 | 192 | 0 | 11.500 | 7.333 |


Absence retry creates 60 duplicates (23.44% of this grid). Of these, 56 occur after a one-item completion claim; four are already visible when the controller stops. These are different failure records. Both count as duplicate effects.

In the 64 zero-lag cases, absence retry still produces 12 duplicates (18.75%). This supports H1: current state can be correct while the earlier operation is unfinished. The trace above is one such case. All five policies for that case are in [trace_examples.json](trace_examples.json).

No retry avoids duplicates but confirms only 128 cases. Terminal status and Bound 12 both confirm 192, with zero duplicates. The remaining 64 cases drop both possible attempts. Thus the safe rules recover every case in this main grid where at least one of the two possible attempts can commit. This is a property of the designed cases and deadline, not a real-world success rate.

### 5.2 Terminal status improves the safe timing baseline

Terminal status and Bound 12 have the same 192 clean cases for every schedule. With queries every tick, mean time falls from 9.500 to 7.333 ticks, a reduction of 2.167 ticks or 22.81%. Mean queries across all 256 cases fall from 13.125 to 11.500, a 12.38% reduction. Both use 1.500 submissions per case. Their capped clean-time scores are 13.125 and 11.500 ticks. H2 holds in all four tested schedules.

The improvement comes from earlier evidence that the first attempt permanently dropped. It does not come from hidden knowledge of the outcome. A service without this status signal cannot assume the same benefit.

| Query schedule | Absence duplicates | Timeout 8 duplicates | Bound 12 clean time | Terminal clean time |
| --- | ---: | ---: | ---: | ---: |
| Every tick | 60 | 12 | 9.500 | 7.333 |
| Every 2 ticks | 52 | 12 | 9.875 | 7.833 |
| Every 4 ticks | 36 | 12 | 11.000 | 9.333 |
| Backoff | 60 | 12 | 10.708 | 8.885 |


### 5.3 Faster checks can increase duplicate effects

For absence retry, changing from every four ticks to every tick adds 24 duplicate cases: 36 to 60, or 9.375 percentage points in this grid. Faster reads also change which duplicates are detected before stopping. The paired counts are 24 cases worse with every-tick queries, zero worse with every-four-tick queries, 36 with duplicates in both, and 196 with duplicates in neither. This supports the planned directional comparison H3. It does not mean that slow tools are generally safer or better.

The safe rules show a different cost tradeoff. Terminal status uses 11.500 queries per case with every-tick observation and 3.250 with every-four-tick observation. Its mean clean time rises from 7.333 to 9.333 ticks. Backoff uses 5.094 queries and 8.885 clean ticks. The study does not select an optimal schedule or attach a monetary value to a query.

![Retry safety, confirmation time, and observation cost](figure_retry_cost.png)

Figure 1. Main synthetic append grid. Panel A uses all 256 cases. Panels B and C compare terminal status with Bound 12. Their clean case sets match. Panel B uses those 192 cases; Panel C uses all 256. Neither safe rule has a duplicate in this grid. Backoff is the fixed schedule in Section 3.3.

### 5.4 Bound violations and server deduplication

These stress results use every-tick queries. They must not be pooled with the main cases.

| Bound violation | Rule | Cases | Duplicates | Clean confirmations | Deadline stops |
| --- | --- | ---: | ---: | ---: | ---: |
| Delay 12 | No retry | 16 | 0 | 8 | 8 |
| Delay 12 | Bound 12 | 16 | 3 | 6 | 7 |
| Delay 12 | Terminal status | 16 | 0 | 9 | 7 |
| Read lag 8 | No retry | 64 | 0 | 32 | 32 |
| Read lag 8 | Bound 12 | 64 | 4 | 40 | 20 |
| Read lag 8 | Terminal status | 64 | 0 | 41 | 23 |


The 12-tick rule creates three duplicates in the late-execution suite and four in the stale-read suite. The terminal rule creates none. However, it confirms only 9 of 16 and 41 of 64 cases before the deadline. Safety does not imply timely completion. The full schedule results are retained even when they are worse.

Under ideal server deduplication, no policy produces a duplicate in any of the 6,720 matched runs. This confirms the intended positive control. It does not demonstrate an implemented or universal exactly-once service. H4 holds under the stated truthful-status and deduplication contracts.

## 6. Real agent and browser pilot

### 6.1 Saved design and executed task

We added a controlled browser pilot after the synthetic study. The new plan and configuration were saved before implementation and scored execution. The implementation was hashed before the warm-up and scored trials. The original synthetic results remain unchanged. See [browser_plan.md](browser_plan.md), [browser_plan_manifest.json](browser_plan_manifest.json), and [browser_execution_manifest.json](browser_execution_manifest.json).

Two separate Codex agent contexts used Chrome through the supported computer-use interface. Each context received nine trials in a fixed order. Runner B used the reverse policy-condition order of runner A. The agents read the rendered accessibility or DOM state and used visible buttons. The runners were instructed to select each next action in a separate model decision and not use a scripted policy loop. The saved logs record actions and states, but do not contain model-turn boundaries or tool code. Thus, those logs cannot alone prove every access or decision constraint. This is a real agent interaction test with an artificial local task. It is not a pixel-only benchmark or a public-web evaluation.

The task was to create exactly one stored item. A local Python HTTP server accepted submissions. Independent timers then committed or permanently dropped each attempt. Each commit inserted a row into SQLite. A requested state check showed the item count and first-attempt status at a configured historical time. That snapshot did not update by itself. The agent could submit, request state, claim completion, or stop. The app enforced a maximum of two submissions. It did not enforce the policy-specific retry or claim rules. The state fields were structured and truthful by construction.

| Condition | Initial attempt | Retry if sent | Read lag |
| --- | --- | --- | ---: |
| Pending | Commit after 16 seconds | Commit after 2 seconds | 0 seconds |
| Failure | Permanently drop after 4 seconds | Commit after 2 seconds | 0 seconds |
| Stale | Commit after 4 seconds | Commit after 2 seconds | 8 seconds |

These are nominal timer delays. The evidence records actual resolution times. Three rules each had two runs per condition, for 18 assigned trials. Absence retried after the first requested empty state. Bound24 required a newly requested empty state at elapsed time 24 seconds or later. Terminal required a requested empty state with permanent failure status. All rules allowed one retry at most. The 24-second threshold adds the largest nominal action delay and largest read lag. It is conservative for these selected combinations. It is not the fastest possible safe timeout.

A requested count of one permitted a completion claim before the 60-second deadline. A count of two required a duplicate stop. A state check at or after 60 seconds required an unresolved stop. A late claim was retained but could not count as a clean on-time confirmation. Pending actions continued after every stop. Final stored rows, not the stop screen, determined duplicate outcomes.

The runner prompts hid condition labels, delay values, outcomes, source code, and audit data. The runners were told not to inspect those data or the other runner. They shared one machine and browser service, so this was instruction-based separation, not a secure isolation boundary. The lead did one excluded warm-up trial. The fixed budget allowed new scored trials for 12 minutes after the first scored submission. There was no replacement of an inconvenient trial.

### 6.2 Measurements and limits of comparison

The primary measures were final duplicates, clean on-time claims, unsafe claims, and adherence to the supplied rule. An unsafe claim is any completion claim whose final item count is not one. The server used a monotonic clock for all measured elapsed seconds. Browser and model overhead contributed to these times. The study did not measure their parts separately.

We retained each browser action log, requested snapshot, server event, durable record, and stopped-trial screenshot. The final audit waited for all accepted attempts to resolve. A negative observation was called stale when a committed record already existed at the observation request time but was absent from its historical snapshot. An unresolved-negative exposure was an empty observation made before the initial attempt resolved. A pending-status exposure could also come from a delayed historical snapshot. These are test exposures, not model mistakes by themselves.

The saved hypotheses asked whether absence could create duplicates, whether terminal could avoid them and recover earlier than Bound24, and whether the final audit could find a duplicate after a completion claim. All assigned trials remain in the results. Timing comparisons pair the same runner and condition where both policies have clean on-time claims. Two repetitions per cell do not support a population error rate, a safety certificate, or a statistical significance claim. We do not combine these seconds or counts with the synthetic grid.

### 6.3 Observed results

All 18 assigned trials started and stopped. The frozen evidence contains 380 server events, 23 stored rows including the excluded warm-up, and 62 requested snapshots including the warm-up. The scored trials used 28 accepted submissions and 61 snapshots. The browser reported Chrome 155.0.0.0 on macOS. The server used CPython 3.14.7. The exact immutable agent model build was not available. See [browser_environment.json](browser_environment.json).

| Rule | Trials | Duplicates | Clean on-time claims | Unsafe claims | Deadline misses | Snapshots |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Absence | 6 | 4 | 1 | 4 | 1 | 13 |
| Bound24 | 6 | 0 | 5 | 0 | 1 | 30 |
| Terminal | 6 | 0 | 5 | 0 | 1 | 18 |

Deadline misses include unresolved stops and late completion claims. Absence had one unresolved stop. Bound24 had one unresolved stop. Terminal had one late claim. The four duplicates came from both pending and both stale-condition absence trials. Three had an empty observation before a later original commit. All three created duplicates, which meets the narrow H-B1 criterion. The fourth, A09, saw an empty historical state after the original record already existed. It also created a duplicate. Thus both unresolved execution and delayed visibility were active in the observed failures. All four false completion claims were allowed by the deliberately weak absence rule. They are not evidence that an unconstrained agent would naturally choose that rule.

A01 gives a measured example with no configured read lag. The first empty check occurred at 4.091 seconds. The agent submitted a retry at 7.087 seconds. That retry committed at 9.097 seconds. A check at 12.560 seconds showed one item while the original attempt remained pending. The original attempt committed at 16.008 seconds. The completion claim arrived at 16.244 seconds and referred to the earlier one-item snapshot. The final database held two items. The other three duplicate trials also had two stored items before the claim reached the server. There were no post-stop effects and no duplicate created after a claim. H-B3 therefore had zero observed instances. The pilot does not reproduce the synthetic study's later-after-stop duplicate trace.

Bound24 and Terminal each had five clean on-time claims and no duplicates. Terminal used 18 snapshots, versus 30 for Bound24, across six assigned trials each. These are observed call totals. Different delays, interrupted contexts, and outcome sets prevent a causal efficiency claim. The server-visible rule checks passed in 17 trials. A04 made a late terminal-policy claim at 69.230 seconds after reading a one-item snapshot requested at 20.076 seconds. Its final count was one, but it failed the on-time criterion. This is a deadline failure, not a duplicate failure.

The agent logs report context recovery or compaction delays in A02, A04, B05, and B07. A02 stopped unresolved at 93.147 seconds. B05 stopped unresolved at 68.737 seconds. Both had one final item. B07's first check arrived at 49.340 seconds; its clean claim arrived at 52.488 seconds. Repeated Statsig telemetry HTTP 403 notices appeared in both runner logs. The saved task requests reached the local server. The study cannot isolate how much time came from telemetry, model inference, tool work, context recovery, or shared host load. No trial was removed or repeated.

### 6.4 Paired timing results

The table preserves all six planned pairs. The difference is Terminal minus Bound24, so a negative value means the terminal trial was faster. A difference is given only when both trials were clean and on time. All values are measured seconds.

| Runner and condition | Bound24 claim | Terminal claim | Paired difference | Pair status |
| --- | ---: | ---: | ---: | --- |
| A, failure | None | 17.789 | Not compared | Bound24 unresolved |
| A, pending | 25.488 | 69.230 | Not compared | Terminal late |
| A, stale | 21.268 | 16.529 | -4.739 | Both clean |
| B, failure | 37.583 | 22.092 | -15.491 | Both clean |
| B, pending | 21.599 | 23.272 | +1.673 | Both clean |
| B, stale | 15.364 | 52.488 | +37.124 | Both clean |

The four matched differences range from -15.491 to +37.124 seconds. Their median is -1.533 seconds and mean is +4.642 seconds. Terminal is faster in two pairs and slower in two. Only the B failure pair is clean under both rules. In that pair, Terminal confirms 15.491 seconds earlier than Bound24. The A failure pair is not a valid speed comparison because Bound24 has no completion claim. H-B2 supports zero duplicates under the tested truthful-status contract, but these browser data do not establish a general speed gain. In particular, the synthetic 22.81% reduction must not be presented as a browser measurement.

No trial breached the selected 24-second first-resolution-plus-lag threshold. The largest timer overrun above its nominal scheduled delay was 0.012 seconds. Nominal timer values were not exact real-time guarantees. The saved raw times retain full precision. The 60-second claim deadline and tool delay had larger effects on clean completion than these small scheduling overruns.

The full trial table, all six pairs, and evidence checks are in [browser_results.csv](browser_results.csv), [browser_pairs.csv](browser_pairs.csv), and [browser_summary.json](browser_summary.json). The pilot supports the specific duplicate-risk mechanism and shows a separate deadline problem. It does not establish field error rates, natural agent behavior, or universal safe retry timing.




## 7. Live test-site experiment: check the scope of a view

### 7.1 Question, plan, and site selection

A **view scope** is the set of records that a page can show under its current filters. A Completed task view excludes active tasks by design. Its empty result can be current and correct even after an active task was created. This cause differs from the delayed writes and old snapshots in Sections 3 and 6.

The question is whether a fresh check or a 24-second wait prevents duplicate entries under an incomplete view. A second question asks whether changing to the All view can confirm one task without a retry. The contribution is a saved small comparison of supplied procedures. Checking filters and reconciling records are established ideas; the experiment is not a new general retry protocol.

The fixed design assigns 60 trials: two hosted implementations, two starting views, five rules, and three repeat blocks. The sites are [official KnockoutJS TodoMVC](https://todomvc.com/examples/knockoutjs/) and [Microsoft's TodoMVC demo](https://demo.playwright.dev/todomvc/). They are external live websites built for tests. They implement one related workflow. They are not two independent production application domains.

The initial plan was saved before warm-up. The final plan was amended before all scored trials. UI Testing Playground failed a certificate check and was excluded. The official React and Vue apps each showed a warm-up item that disappeared after reload. KnockoutJS had an initial input action with no created row, then passed a separate warm-up. The Microsoft demo also passed its reload check. These failed setup checks remain in [live_preflight.md](live_preflight.md). Site selection therefore favors apps that passed a small feasibility check. The amended plan and hash record are [live_plan.md](live_plan.md) and [live_plan_manifest.json](live_plan_manifest.json). These are local records, not external preregistration.

### 7.2 Procedures and measures

Each task requests exactly one active item with a unique token. One agent context uses each origin in one active write tab. The browser is reloaded before each trial, and the view is set to All or Completed. The token must have no visible match before submission. The fixed assignment file uses a cyclic rule order and alternating view order across three blocks. There is no random sampling. The two contexts share the host and browser service.

| Rule | Procedure after a fresh zero-match view |
| --- | --- |
| No retry | Stop unresolved without another submission. |
| Absence | Submit the same token once more, inspect, and stop. |
| Wait24 | Inspect at or after 24 seconds; retry once only if still zero. |
| Closure | Retry only after an attempt-specific guarantee of no future effect; otherwise stop unresolved. |
| Scope | Select All and inspect again. Confirm one match. Without a match or a closure signal, stop unresolved. |

The 24 seconds are a chosen heuristic. They are not a proved bound for either website. Neither app provides the required terminal-failure signal. Closure and No retry therefore have the same permitted retry behavior here. This is not a test of successful terminal-failure recovery.

Only Scope can change the filter during its decision phase. All controls are visible to every rule. This tests prescribed procedures with different evidence use. An unconstrained agent could already inspect the filter, and need not make the mistakes that Absence is instructed to make. The 60-second decision deadline starts with the initial submit request. At most one retry is allowed. Each runner has a 20-minute trial admission budget. No failed or late trial is replaced.

The runner stops with success only when it observes exactly one matching visible task. The later audit selects All, counts exact token matches, reloads, and counts again. It checks that the task remains active. An audit cannot repair the earlier decision. A **clean confirmed success** requires an on-time success decision and exactly one active task after reload. A **duplicate** means two or more matching task entries after reload. Pre-reload duplicates, reload loss, unresolved decisions, errors, and rule deviations are separate measures.

The observations come from rendered page content and accessibility information through the supported browser tool. The test is not pixel-only. The audit uses the same UI and browser service; it is not an independent server audit. Reload survival means retention in this browser at that check. It does not prove server storage or indefinite durability. The runners were instructed not to read app source, storage APIs, or hidden browser state. This was an instruction boundary, not a secure access boundary. Source inspection by a separate design reviewer did not supply task outcomes.

The saved plan defines three directional checks: more duplicates for Absence and Wait24 in Completed view; more clean confirmations for Scope than Closure on both sites; and All-view success without retries as a positive control. Report all cells rather than a population significance claim. Repeated tasks in two related apps do not justify field error rates or independent-trial confidence intervals. Measured time includes model, tool, and host delay. Timing comparisons are descriptive and exploratory.

### 7.3 Results

All 60 assigned trials started, stopped, and received both audits. There were 29 clean confirmed successes and 31 unresolved decisions. The final audits found 40 single-task outcomes, 10 duplicate outcomes, and 10 zero-task outcomes. All matching tasks were active. The counts before and after reload agreed in every scored trial. Thus the ten zero outcomes were not observed losses across reload: each was already zero in the full-list audit before reload.

| Rule | View | Trials | Clean confirmed | Duplicates | No task | Retries |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No retry | All | 6 | 4 | 0 | 2 | 0 |
| No retry | Completed | 6 | 0 | 0 | 1 | 0 |
| Absence | All | 6 | 6 | 0 | 0 | 2 |
| Absence | Completed | 6 | 0 | 5 | 0 | 6 |
| Wait24 | All | 6 | 6 | 0 | 0 | 2 |
| Wait24 | Completed | 6 | 0 | 5 | 0 | 6 |
| Closure | All | 6 | 5 | 0 | 1 | 0 |
| Closure | Completed | 6 | 0 | 0 | 2 | 0 |
| Scope | All | 6 | 4 | 0 | 2 | 0 |
| Scope | Completed | 6 | 4 | 0 | 2 | 0 |

No task means zero matching task entries after reload. A single item found only by the audit does not count as a clean confirmation. Of the 31 unresolved decisions, 11 had one task, 10 had two tasks, and 10 had no task. All ten duplicate trials stopped unresolved while the Completed view still hid both active items. No success decision had a duplicate or zero final audit count.

The Microsoft demo had 18 clean confirmations, six duplicate outcomes, and no zero-task outcomes in 30 trials. KnockoutJS had 11 clean confirmations, four duplicate outcomes, and ten zero-task outcomes in 30 trials. Its input still contained the token after 16 initial submission actions. Six of these trials later had one task after their permitted retry; ten had none. The logs show input text retention and missing task rows. They do not isolate a cause in the application, input event path, or tool. No claim of a lost server write follows from this observation.

H1 met its saved direction on both sites. In Completed view, Absence and Wait24 each created three duplicates in three Microsoft trials and two in three KnockoutJS trials. Closure and Scope created none. A 24-second wait did not remove the effect of the filter.

H2 also met its direction on both sites. In Completed view, Scope made three clean confirmations in three Microsoft trials and one in three KnockoutJS trials. Closure made none on either site. The two remaining Scope trials had no task before or after reload and stopped unresolved. The scope check confirmed an existing task; it did not recover those missing submissions.

H3 did not meet its criterion. Only 21 of 30 All-view trials confirmed a new task without a retry. All nine failures of this control occurred on KnockoutJS. Four later recovered with their permitted retry, so the All-view group had 25 clean confirmations in total. The other five ended with no task. This failed control limits a causal comparison of overall success counts across rules and sites.

There were 16 retries: eight under Absence and eight under Wait24. Every retry had an eligible empty observation. The analyzer found no scored tool error, policy deviation, or late decision. The largest decision interval was 44.431 seconds. These are wall times through the model and browser service, not website latency. The study does not claim that Scope is faster or that Wait24 is an efficient timeout.

Both runners had setup errors when they tried to use tabs owned by the parent session. They then opened their own tabs before scoring. Three T result records have a start time one millisecond before the action log's start time, from two clock reads. A diagnostic clock record during T06 had a stale T01 label; its later correction remains in the raw log. The analyzer excludes that clock-only record from trial actions. It keeps both start times and obtains the same result for all 60 deadline checks and all eight Wait24 checks under either time. No raw record was removed or rewritten to hide a failed test.

The package retains 302 scored UI observations, 428 scored action records, and 60 audit screenshots. An action record can contain several deterministic tool operations; it is not a token count or model-call count. The installed Chrome app version was 155.0.8059.40 on macOS. The exact immutable model build and provider inference hardware were unavailable. See [live_results.csv](live_results.csv), [live_summary.json](live_summary.json), [live_pairs.csv](live_pairs.csv), and [live_environment.json](live_environment.json).


### 7.4 Interpretation

The live test adds a distinct boundary to the earlier timing result. A current empty list does not prove absence if its filter excludes the requested record. Waiting longer does not change that scope. In the tested Completed view, a full-list check confirmed four existing tasks without a repeat submission. This is the supported improvement.

The scope rule was not uniformly successful: it had four zero-task outcomes across both views. The failed All controls show why a reliable create action must also be checked. The experiment does not identify the cause of the input failures. A future study can separate input delivery, page readiness, and task creation, with the checks fixed before data collection.

These results concern two related hosted test apps and instructed procedures. They do not show that a free-choice agent would ignore an obvious Completed filter. They do not test a server transaction, an uncertain network commit, or a production terminal-status service. Closure and No retry have the same available retry actions here, so their small difference in clean counts cannot establish a benefit of terminal status. Keep these results separate from the local delayed-write pilot and the synthetic event model.


## 8. Computer-use interface implications

The results support a concrete interface requirement: distinguish an unresolved attempt from a terminal failure with no future effect. A timeout, unchanged screen, or current empty record list is not that failure signal. Where the application supports it, bind status to the specific attempt and keep that identity across recovery.

A controller should retain pending actions after its own wait ends. It should use a documented terminal signal, a valid execution-and-visibility bound, or a server-enforced idempotency contract before a repeat action. If none is available, the outcome remains unresolved. Waiting or asking for review has an availability cost; it does not prove failure.

An evaluator should also let admitted actions finish after the agent stops. In this grid, that step exposes 56 unsafe early claims for every-tick absence retry. A test that checks only the visible count at stop can award success before a duplicate appears. The browser late claim also shows why a deadline should be checked at claim receipt. A snapshot timestamp can be valid while the later claim is too late. These recommendations apply known systems reasoning to computer-use interfaces. The controlled browser pilot tests the same distinction with real requests and writes. The live test-site extension adds view scope as a separate requirement. Before an absence check can support a decision, the controller must check record identity, filters, and search coverage. A full-list match can confirm an existing effect; it still cannot prove closure of an absent pending write. Production workflows and broader model comparisons remain future work.

## 9. Limitations

The main grid runs a finite event model. Its tick values are chosen; its call costs and delays are not measured on a service. The browser extension uses real model decisions, requests, timers, and stored writes, but its task and fault conditions are constructed. The grid weights are artificial. Real applications can have unbounded delays, rollback, partial writes, status loss, incorrect status, changing caches, and multiple writers.

The terminal rule assumes a truthful, durable, attempt-specific drop record. Some sites expose no such record. The model gives all rules the same response but only this rule uses that extra field. Its advantage is therefore conditional on an interface capability. A richer failure model can invalidate the guarantee.

Only one retry and one logical item are modeled. There is no crash recovery, concurrent controller, permission change, authentication failure, or imperfect action identity. Ideal deduplication is a control, not a tested implementation. The deadline is fixed, query duration is zero, and the schedules are not learned or optimized. Neither the finite cases nor the proof justify a safety certification or field error estimate.

The same cases are disclosed to the policy designers. The browser runners did not receive the condition configuration, but each received a prescribed policy. This does not measure natural retry behavior. There are only two contexts, one machine, one browser service, and one simple local task. Repeated trials share context within each runner. Tool and model delay can remove an intended negative-state exposure before a check occurs. The exact model build and service timing are not available. The live extension adds two public test sites, with one shared task design and prescribed filters. The apps were selected after feasibility checks. It does not supply a held-out production benchmark. Further work should test more agents, richer applications, and permitted production workflows.

## 10. Ethics, rights, and AI use

The study can help prevent duplicate records and premature completion claims. It contains no harmful prompts, exploit steps, private records, account data, or real transactions. No experiment sends messages or changes a private external account. The live tests create small synthetic task entries in browser storage on public test apps. They do not make purchases or create server account records. GitHub publication is a separate authorized action, not experimental evidence.

Codex generated the plan, implementations, calculations, figure, and paper. Two separate Codex contexts performed the local browser pilot, and two later contexts performed the live test-site trials. Other Codex agents checked sources, design, calculations, and reproduction. AI review is not human or external peer review. No human review, university affiliation, endorsement, or certification is claimed. The browser pilot used real model inference through the existing Codex service. No model training, separate paid API, or new paid compute service was used.

All synthetic input cases and local browser tasks are newly constructed. The live extension uses existing TodoMVC test apps and new synthetic task tokens. Its screenshots and rendered UI logs retain source attribution. No third-party application code, paper, dataset, or figure is redistributed. Sources retain their rights. No new license is assigned to this work. The paper uses original prose and cites the related methods.

## 11. Checks and reproduction

The main implementation advances the environment one tick at a time. The independent validator uses direct event-time thresholds and does not import the analyzer. It checked all 13,440 run rows, 167,520 trace events, 676 post-stop resolutions, 6,720 matched server pairs, all grouped result tables, and 48 paired comparisons. All checked integer and label fields match exactly. See [method_review.md](method_review.md) and [validation_results.json](validation_results.json).

The browser analyzer reads the frozen SQLite database and audit independently of the application code. It checks event, snapshot, stop, and stored-row identities before it computes outcomes. Its author also reviewed the design, so a fresh reviewer separately checks the final evidence. See [browser_review.md](browser_review.md) and [browser_reproduction_check.json](browser_reproduction_check.json). The action logs and screenshots support the observed interaction sequence; they do not reveal internal model reasoning.

Run the documented commands in [README.md](README.md). The package includes the saved plan, cases, complete compressed traces, readable examples, summaries, code, dependency versions, logs, proofs, source record, and agent reviews. Relevant parts of the NeurIPS checklist were used to review claims, assumptions, reproduction, limits, rights, and AI use [6]. This is not a conference submission or approval claim. See [final_review.md](final_review.md) for the final reproduction outcome.

The live analysis reads the saved action logs and assignment file. A separate reviewer checks its output against the recorded UI states. See [live_review.md](live_review.md) and [live_validation.json](live_validation.json). Exact trajectories cannot be repeated because the hosted apps and model/tool timing can change. Saved evidence permits a local result check without a new browser run.

## References

1. Aggarwal, P., Jang, L. K., Welleck, S., Fried, D., Salakhutdinov, R., and Koh, J. Y. (2026). *cua-speedrun: Standardized Benchmarking of the Speed of Computer-Use Agents*. arXiv:2609.40284v1, September 30. Preprint. [Source](https://arxiv.org/html/2609.40284v1).
2. Calanza, E. (2026). *RStackBench: A Five-Layer Fault-Injection Method for Measuring Browser-Agent Execution Reliability in Controlled Applications*. Independent author preprint, August. [Source](https://exzilcalanza.info/wp-content/uploads/2026/08/rstackbench-browser-agent-reliability-preprint.pdf).
3. Xu, J., Fan, L., Wang, Z., Li, X., and Liu, H. (2026). *Beyond Single-Use Tokens: Durable Authorization State for Replay-Resistant LLM Agent Actions*. arXiv:2608.01710v1, August 3. Preprint. [Source](https://arxiv.org/html/2608.01710v1).
4. Lee, C., Park, S. J., Kejriwal, A., Matsushita, S., and Ousterhout, J. (2015). *Implementing Linearizability at Large Scale and Low Latency*. SOSP 2015. DOI: 10.1145/2815400.2815416. [Author-hosted paper](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf).
5. Fielding, R. T., Nottingham, M., and Reschke, J., editors (2022). *HTTP Semantics*. RFC 9110, Section 9.2.2. Internet Standard. [Source](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2).
6. NeurIPS. *Paper Checklist Guidelines*. Accessed October 15, 2026. [Review aid](https://neurips.cc/public/guides/PaperChecklist).

7. Calanza, E. (2026). *Measuring the Gap Between Visible UI Success and Persisted State in Browser Agents*. Author report, August 14. [Source](https://exzilcalanza.info/rstackbench-browser-agent-reliability/).

8. He, H., Yao, W., Ma, K., Yu, W., Dai, Y., Zhang, H., Lan, Z., and Yu, D. (2024). *WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models*. ACL 2024, pages 6864-6890. [Paper](https://aclanthology.org/2024.acl-long.371/).
9. Kara, S., Faisal, F., and Nath, S. (2025). *WAREX: Web Agent Reliability Evaluation on Existing Benchmarks*. arXiv:2510.03285v1, September 28. Preprint. [Paper](https://arxiv.org/html/2510.03285v1).
10. TodoMVC contributors. *Application Specification*. Accessed October 15, 2026. [Specification](https://github.com/tastejs/todomvc/blob/master/app-spec.md).
11. Microsoft. *Test generator*. Playwright documentation. Accessed October 15, 2026. [Guide](https://playwright.dev/docs/codegen).
