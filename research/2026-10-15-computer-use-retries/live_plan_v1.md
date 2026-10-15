# Live website extension plan

Saved on 2026-10-15 before warm-up or scored actions. This is a manual extension to the existing paper.

## Question and scope
Can a fresh view or a 24-second wait prevent duplicate task entries when a live website shows a filtered list? Can a check of the full list prevent these duplicates while confirming the task?

Test two external public demonstration sites: https://todomvc.com/examples/react/dist/ (runner T) and https://demo.playwright.dev/todomvc/ (runner P). These are related TodoMVC apps on two hosts. They are not independent production systems. Tasks use browser storage. Reload survival is not server durability. No network faults or delayed writes will be injected. No private account records will be used.

## Fixed design
60 assigned trials: 2 sites x 2 starting list views (All, Completed) x 5 rules x 3 repeats. The task is to add exactly one active item with the assigned unique token. Each runner uses one tab and one domain sequentially. Both share one Chrome service and host. Add one unique warm-up item to expose filters. Warm-up is excluded. Preserve unrelated items. No deletions are required. Trial tokens stay in the demo browser storage as evidence.

Within each repeat use a cyclic rule order and alternate All/Completed order. assignments.csv fixes the order. No random sampling or random seed. Do not replace failures or skip hard cases. Each initial submission and optional retry has the same token. Maximum two submissions per trial. No scripted policy decision loops: the agent reads each observation and chooses the next allowed action. Deterministic typing and Enter can share one tool call. Use supported computer-use tools only. No app state, local storage, hidden data, network interception, or app source reads by runners.

## Rules
- no_retry: submit once; inspect current view; confirm only if exactly one matching visible item exists. Otherwise stop unresolved.
- absence: submit once; if zero matching visible items, submit once more immediately. Inspect current view, then stop. Confirm only one; more than one is duplicate; zero is unresolved.
- timeout24: submit once; if zero matching visible items, inspect again at or after 24 seconds from the initial submit request. Retry once only if still zero. Inspect and stop. This is a heuristic, not a proved safe bound.
- closure: submit once; retry only if the website gives an attempt-specific guarantee that the first attempt cannot later apply. Empty views, generic errors, and elapsed time do not qualify. Without that signal, stop unresolved if zero items. This rule may be behaviorally equal to no_retry on these tasks.
- scope: submit once; if zero matching visible items, select the visible All filter and inspect again. If one, confirm. If more than one, stop duplicate. If zero and no terminal guarantee, stop unresolved. Do not retry just from absence. This is a scope check added to the closure rule.

The four fixed-view rules cannot change the filter during their decision phase. This is a constrained mechanism test, not a test of an unconstrained agent. The visible filter is not hidden from runners. In particular, an unconstrained agent may already know that Completed omits active tasks.

## Evidence and audit
Before each trial, select its view and verify zero matching tokens. Save full rendered DOM or accessibility observations, UTC times before/after actions, counts, selected view, URLs, decisions and all tool failures. Use a compact view in model output but keep full observations in JSONL. Count exact visible task labels, not the input text or counter. Save one final screenshot per trial after audit. Use .jpg for JPEG bytes.

Stop at 60 seconds after the initial submission request if no rule decision has completed; record a late decision or interruption rather than replacing it. Timing includes model/tool overhead; do not interpret it as website latency. No busy polling. For timeout24, a clock wait may enforce the experimental delay; then take a fresh UI observation before a retry.

After the decision, switch to All and count exact matching task entries. Reload, verify All, and count again. This audit must not change the recorded decision. Record both counts. A duplicate means two or more matching entries after reload. A clean confirmed success needs an on-time decision that says success and one entry after reload. An unresolved decision with one stored item is not a clean confirmed success. This finite audit does not prove indefinite durability or closure of server effects. Set 20 minutes as the per-runner admission budget. Preserve every assigned trial including unstarted trials if the budget expires.

## Hypotheses and decision criteria
H1: In Completed view, absence and timeout24 will have more duplicate trials than closure and scope. Report counts per site, view, and rule. If no duplicates occur or eligibility fails, record the negative or inconclusive result.
H2: Scope will confirm more clean tasks in Completed view than closure without adding duplicates. Require this direction on both sites; report individual repeats, not a population significance claim.
H3: All view will act as a positive control. Every rule is expected to see the new item without a retry. Record failures.
Report retry eligibility, actual retries, policy deviations, visible-at-decision counts, pre/post-reload counts, clean confirmed successes, unresolved and late decisions, and descriptive action/timing measures. No p-values or field error-rate confidence intervals: related demos, repeated contexts and fixed interventions do not give an independent random sample. Pair outcomes by site, view, repeat; timing is exploratory and not causal.

## Prior work and limits
WebVoyager evaluates real-site task completion. WAREX (2025 preprint) tests agents with controlled infrastructure failures. This extension instead tests the narrow scope of a visible-list check on two public demos. List filtering and read reconciliation are established ideas. A limited search does not establish novelty. The new contribution is this saved live-site evidence and a bounded comparison, not a new general retry protocol.

No new API charges or compute purchases. No human review has occurred. A separate agent must check evidence and claims before publication. Use the relevant NeurIPS checklist items. Preserve the earlier synthetic and local browser results separately.
