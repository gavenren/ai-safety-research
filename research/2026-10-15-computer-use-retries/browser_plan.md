# Saved real-browser extension plan

Date: 2026-10-15. This extends the existing paper. It is a direct user request, not another daily study.

## Question and scope

Can a real Codex agent apply the retry rules through a browser? Does an empty observation permit duplicate stored records while a truthful terminal failure signal avoids them? Does the terminal rule confirm recovery earlier than a chosen 24-second timeout in the tested runs?

This is a controlled local browser pilot. The application and delays are constructed. The clicks, browser observations, model decisions, elapsed seconds, HTTP requests, and SQLite writes are real. It is not a public-web benchmark or a test of natural model error frequency. Each agent is instructed to apply a rule. No paid API or new paid compute service will be used. Existing Codex agent turns perform the task.

## Fixed design before implementation and execution

Use 18 scored trials: 3 policies x 3 conditions x 2 repeats. Two separate Codex contexts each perform all nine policy-condition pairs, in a fixed counterbalanced order. Each context uses only its own Chrome tab. The policy is visible. The condition label, configured outcome, delay, and trial order are withheld from each runner. Runners must not read server code, configuration, audit data, or other runner logs. They can see truthful historical count and first-attempt status through explicit Check state requests. This is limited blinding, not a secure separation of machines or a blind model benchmark.

Conditions:

| Code | First attempt | Retry if sent | Read lag |
| --- | --- | --- | --- |
| pending | Commit after a nominal 16 seconds | Commit after 2 seconds | 0 seconds |
| failure | Permanent drop after 4 seconds | Commit after 2 seconds | 0 seconds |
| stale | Commit after 4 seconds | Commit after 2 seconds | 8 seconds |

Nominal delay is a requested scheduler delay, not a hard real-time guarantee. Record actual resolution times and timing-bound breaches. The 24-second threshold is chosen before execution from the largest nominal action delay plus the largest lag. It is conservative for these three selected condition combinations. It is not an optimal or fastest safe timeout.

Policies:

- Absence: send one retry after the first requested observation with count zero.
- Bound24: send one retry only after a newly requested observation with count zero and observed elapsed time at least 24 seconds. Do not combine an old observation with a later clock.
- Terminal: send one retry only after a requested observation with count zero and first-attempt status permanently dropped.

All policies first submit once. At most one retry is allowed. After a requested observation, count one permits Claim complete; count two requires Stop: duplicate. If observed elapsed time is at least 60 seconds without a clean claim, use Stop: unresolved. A claim received by the server after 60 seconds is a late claim and cannot count as on-time clean confirmation. Any violation stays in the results. Never restart or replace a scored trial because its result is inconvenient.

The runner must read a fresh browser state after each browser action. Each next action is selected in a separate model decision. A deterministic loop must not decide or execute a complete trial. Read-only accessibility or DOM text and screenshots are permitted. Direct HTTP calls, page-script mutations, storage reads, and hidden state inspection are not permitted for the runner. The server has no client policy gate: retry and claim buttons remain available after submission. It only enforces the shared maximum of two attempts and records all other actions and rejected requests.

Poll through the visible Check state button. Allow short waits of at most 2 seconds when no action condition is met. Poll timing remains model/tool dependent; do not claim a fixed observation frequency. Preserve actual query timestamps. Actions that occur after a stop continue. The final audit waits for all admitted attempts to resolve, then reads the stored records independently.

The total trial budget is 12 minutes after the first scored submission. If it is reached, stop starting new trials and retain pending, interrupted, and unstarted trials. Do not extend the budget to obtain a desired result. Setup, code checks, audit, and publication are outside this trial budget.

## Measures and decision criteria

Save server events, durable record rows, per-trial configuration, browser versions, runner instructions, runner action/observation records, and completion screenshots. Save timestamps for submission, resolution, requested snapshots, stop, and audit. Distinguish configured delays from measured delays. The server's monotonic clock measures elapsed time. The browser User-Agent provides its reported version. Exact underlying model build and service reasoning latency may not be exposed; record this limit.

Primary: final duplicate count (>1 stored record), clean on-time claim (claim by 60 seconds and exactly one final record), unsafe claim (a completion claim with final count other than one), and prompt-rule adherence. Secondary: claim elapsed seconds, snapshot calls, submit calls, first pending exposure, stale-negative exposure, late effects after stop, and actual timing-bound breaches. Save a complete table for all 18 trials, including failures and unstarted cases.

H-B1: At least one absence trial that observes an empty state before a later original commit produces two final records. If no such exposure or duplicate occurs, report this negative or unexposed result. Do not increase delays or rerun scored trials.

H-B2: Terminal trials have no duplicate when the status contract holds. Compare their clean-completion count with Bound24. For each repeat-condition pair clean under both, report actual claim-time difference. Separately show the two failure-condition pairs. Treat any lower observed delay as a pilot observation. Tool/model latency and shared machine load prevent a causal performance estimate.

H-B3: The final audit can detect duplicate effects after an agent claim. Report all observed instances, including zero. A screenshot alone does not establish durable success.

Use raw paired values, counts, ranges, and medians. With two repetitions per cell, do not use statistical significance or a population error-rate confidence interval. Do not pool these results with the synthetic grid. No zero-failure safety certification is permitted.

## Controls and checks

Before scored trials, perform code-level checks on a separate test database. The tests must exercise permanent drop, two append effects, delayed visibility, observation identity, duplicate/late claims, post-stop resolution, and trial isolation. A single warm-up UI trial is allowed, with its own ID and exclusion label, only to check controls. The scored configuration and implementation must be hashed before the first scored submission. Record any later change; if an issue invalidates a scored trial, preserve it and report the limitation.

An independent agent will audit event order, SQLite records, adherence, counts, and report calculations. Re-run the analysis on frozen evidence. The stochastic model/browser trajectory itself is not expected to repeat byte for byte. Retain the original simulation evidence. Update the same report, PDF, bibliography/search record, README, and repository index after all checks pass. Keep truthful AI-use and human-review statements. Verify each published file against its remote Git blob.
