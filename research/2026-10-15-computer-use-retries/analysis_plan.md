# Saved study plan

Date: 2026-10-15. This is a separate user-requested paper. It is not a second daily automation run.

## Question and contribution

How do action completion delay and read delay interact with computer-use retry rules? Does a truthful terminal failure signal improve safe completion and confirmation time over absence-based retries and a conservative fixed timeout?

The contribution is an original, bounded finite-state comparison with all event traces. It combines a pending append action with a delayed negative observation, and scores effects after outstanding actions settle. It does not introduce idempotency, exactly-once execution, terminal status, or retry safety as new ideas. Source search began before this plan. Closest sources include cua-speedrun (2026), Beyond Single-Use Tokens (2026), RStackBench (2026), and RIFL (2015). The search cannot establish global novelty.

## Fixed model

Time uses integer ticks, not seconds. An initial attempt starts at time zero. A submitted attempt resolves once after its assigned positive delay. A commit appends one durable item. A drop has no effect and can never commit later. There are no other writers, rollbacks, identity errors, or false positive observations. At most one retry is allowed. Both attempts refer to one desired logical item.

A query at time t gives the exact historical item count and attempt states as of max(0,t-L). L is a fixed read lag for that case. Pending, committed, and dropped states are specific to an attempt. An attempt does not become terminal until its actual resolution time. Queries are processed after all resolutions at the same tick, and a retry is sent after that query. Positive delays prevent a same-tick retry commit.

Policies receive this common observation. Some deliberately ignore terminal state. No policy sees the actual delay or outcome before a query reveals it. Static execution and lag bounds are known to the timeout policies. A query has no extra duration; time and call count are separate measures. A count of one causes the controller to stop and claim completion. A count of two causes it to stop with a detected duplicate and no completion claim. Pending effects still occur after that stop. Otherwise the controller stops at deadline 24 and makes no completion claim. A retry at tick 24 remains an admitted action and must be scored after it settles.

## Rules and controls

All rules send the initial attempt and follow the same chosen query schedule until stop. They send at most one retry after a negative observation:

- no_retry: never retry. This is a conservative availability control.
- absence_retry: retry after the first negative observation.
- timeout8: retry at the first negative query at or after tick 8. This ignores read lag.
- bound12: retry at the first negative query at or after tick 12 (execution bound 8 plus lag bound 4).
- terminal_retry: retry only when the first attempt is observed as permanently dropped.

Run all five rules under append semantics and, as a matched positive control, ideal server deduplication. Under deduplication, all committed attempts for this logical item yield at most one stored item. A dropped attempt does not prevent a later successful attempt. This is an assumed server feature, not a new client mechanism or implementation.

## Inputs and suites

The main grid uses each attempt delay in {1,2,4,8}, each outcome in {commit,drop}, and read lag in {0,1,2,4}: 256 cases. The four query schedules are every tick, every 2 ticks, every 4 ticks, and ticks {1,2,4,8,12,16,20,24}. With five rules and two server modes, there are 10,240 main runs.

Two separate stress suites break one declared timing bound. Late execution sets both possible attempt delays to 12 and retains the four main lags (16 cases). Stale reads use main delays but lag 8 (64 cases). Each uses all rules, modes, and schedules. Never pool these with the main grid. No scenario is sampled from real applications. No random seed or population inference is appropriate.

## Measures

Save every query, observed historical state, submit time, terminal resolution, stop, declaration, and final effect count. Resolve every admitted action even after controller stop or deadline. The final audit time is the last admitted resolution time, or the stop time, whichever is later.

Primary measures are duplicate effects (final count greater than one), clean confirmed completion (an observation of exactly one by tick 24 and exactly one final effect), unsafe completion (claim followed by final count other than one), detected duplicate stops, and deadline stops. No claim includes both detected duplicate stops and deadline stops. Also report final zero effects, exactly one eventual effect without confirmation, total submit calls, query calls, and confirmation tick.

Report capped clean-completion time: the confirmation tick for a clean confirmed result and 24 for every other result. This defined score is not wall time. Report both query and write costs; do not hide them in one arbitrary weighted score. For time comparisons, also use paired cases where both compared rules have clean confirmed completion. Report counts and means by suite, schedule, rule, server mode, and initial outcome. Report fresh-read (L=0) results separately.

## Hypotheses and decision criteria

H1: In append mode, absence_retry has at least one duplicate with L=0. A fresh negative result does not prove that the first action is finished.

H2: In the main append grid, terminal_retry and bound12 have zero duplicates. terminal_retry has at least as many clean confirmed cases as bound12 and a lower mean confirmation tick on their jointly clean cases for at least one schedule. Retain a negative result if this fails.

H3: Faster observation does not necessarily improve retry safety. Compare every1 with every4 for absence_retry in append mode. Report the full paired duplicate difference, even if it is zero or has the opposite sign.

H4: The two timing violations can break timeout safety, while a truthful terminal-drop rule and ideal deduplication retain at-most-one effects. This is a contract test, not an estimate of field robustness.

Formal analysis will give an indistinguishable-history example, a sufficient terminal-drop condition, a bounded-time condition, and a tight one-retry safety/recovery relation for a two-world example. These are explicit special cases of established distributed-systems reasoning, not claimed as new general theorems.

## Checks, disclosures, and publication

Use an independent implementation to check all rows and selected traces. Check events at equality boundaries, post-stop duplicate effects, both dropped attempts, zero lag, bound violations, and matched deduplication. Check deterministic reproduction and all report numbers. Preserve any failure and repair. Use separate source and final agent reviews and the relevant NeurIPS checklist items. No model or browser-agent benchmark will be claimed. No real website, private task, account, payment, or message will be used as experimental data. Only local code and synthetic states are required. No paid compute or model calls.

Publish the paper, optional PDF, plan, code, inputs, raw traces, results, reviews, source record, and reproduction steps to gavenren/ai-safety-research after checks pass. State that Codex generated the work and that no human or external peer review occurred. Do not assign a new license.
