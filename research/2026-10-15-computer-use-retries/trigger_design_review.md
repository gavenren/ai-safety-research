# Review of the proposed two-tab Drive experiment

Date: 2026-10-15. This is design advice before scored trials. The reviewer read the earlier account plan, independent review, and Sections 7 and 8 of the paper. No browser action or external write was made for this review.

## Decision

The proposed 32-trial comparison is suitable as a small, selected stress test if live feasibility checks establish the intended view. Use four rules, two observer views, and four repeats per cell. Keep all earlier results unchanged. The earlier same-tab experiment remains a valid negative transfer result.

The new task must be named precisely: create one folder in a writer tab and check its result in a separate observer tab. It is a real account workflow with a supplied observation rule. It is not a natural error-rate test, a new retry protocol, an uncertain network-commit test, or a direct replication of the same-tab workflow.

## Feasibility and admission

Before scored trials, save the exact feasibility actions, names, observations, and any rejected workflow. Check both an All observer and a Documents observer after creation in the writer tab. For Documents, require a usable empty list with an explicit Documents filter at the first fresh observation and at or after 24 seconds. Then remove the filter and verify the created folder. For All, require a usable list that shows the folder without a retry. Read the observer through the same browser operations that the final plan will use. A loading state is unknown, not zero.

Select the workflow because it exposes the stated condition. Say that this is purposeful case selection. Do not imply that the fraction of failures estimates how often users meet this condition. Save the final plan and assignments only after feasibility, but before any scored action. Mark all feasibility records as excluded. Record any failure to find a suitable workflow.

After scoring starts, retain all 32 assigned trials, including trials with no trigger, late decisions, loading failures, or automatic view changes. Do not replace, rerun, or extend cells to obtain the desired result. Do not restore a filter during a decision merely because the site changed it. A fixed set with no activation remains a result, although it does not answer the requested retry comparison.

## What counts as an activated rule

Record these separate events for each trial: first usable observer count; selected observer filter; elapsed time of each observation; rule branch selected; retry request time, if any; and the final service-record count. An empty observation alone is not a completed retry trial.

Predeclare a minimum evidence criterion for the requested mechanism: at least one Documents trial under Absence and at least one under Wait24 must execute their permitted second creation after an eligible zero count. Wait24 needs a fresh zero observation at elapsed time of at least 24 seconds. Scope must have at least one zero-to-broader-view path. Receipt must have at least one confirmation supported by its exact-name writer receipt while its observer has zero matching rows. If any of these events is absent, state which branch remains untested. This criterion is an evidence gate, not a reason to discard outcomes or add trials.

Report every assigned cell as the primary result. Report activation counts and descriptive results for exposed trials separately. Do not use an exposed-only subset to claim a causal population effect. With four repeats per cell, shared service state, fixed order, and one account, use counts and full paths rather than population confidence intervals or significance tests.

## Controls and causal interpretation

Use the same writer and observer arrangement for every rule and both view conditions. The writer starts in All for every trial. The observer starts in its assigned view. Verify the unique token is absent in usable baseline lists before the first write. The observer must refer to the same block as the writer; save both block aliases. Avoid a selected row that hides the filter toolbar before the baseline and each planned first decision capture.

All is an essential control for stale cross-tab state. If All also remains empty, filtered scope and cross-tab update delay are mixed causes. Report this directly. Do not claim that the Documents filter alone caused a duplicate in that case. If only Documents is empty while matched All controls work, the data support a narrower scope mechanism. The final record audit still determines whether an eligible retry created a duplicate.

Specify whether the observer is reloaded, refreshed, or merely re-read. Use one common first-observation operation for all rules. A fresh accessibility read of an old page is not proof that the page has fresh service data. If a reload resets the type filter, it cannot serve as an undeclared refresh that preserves Documents. Any new operation found during feasibility must be fixed in the saved plan.

The model will see writer evidence while it operates the writer. Core rules therefore impose a deliberate information restriction when they ignore its row or positive receipt. State this restriction clearly. Receipt differs in permission to use visible evidence, not in model capability. Use an exact-token receipt generated after the current trial's first write; a generic success message or a previous token is not evidence for this trial.

## Time and observation cost

Start the 120-second deadline at the first Create click request. Include tab switches, model decisions, tool calls, and waits. If the first zero observation occurs after 24 seconds, Wait24 can make its required fresh check immediately; it need not add another 24-second delay. Do not describe the chosen 24 seconds as a service completion bound.

Count writer reads, observer reads, tab switches, filter changes, write submissions, and elapsed time separately. Audit actions occur after the decision and must not enter the controller's confirmation cost. State whether a full-state call also returns an image. Do not compare raw screenshot counts between rules unless they represent the same operation. The two-tab path adds real overhead, so timings cannot be directly pooled with the earlier same-tab study.

## Evidence and cleanup

Use a logger with explicit trial ID, tab role, operation, UTC start/end time, full tool-call arguments, observed text, and error outcome. Do not rely on a closure that captures an old trial variable. Save each image under an immutable unique trial and phase name. Save the exact decision record before the audit. No later audit can retroactively convert an unresolved decision into a successful confirmation.

After all decisions, use the separate connector to count distinct record IDs by exact token. Keep the read capacity and returned count. Compare this finite audit with browser lists and preserve disagreements. Keep private IDs and account details local; publish stable aliases and complete task-relevant observations. Move only the dedicated test parent to Trash after all checks. Do not empty Trash.

## Claim limit

The strongest likely contribution is a documented case where a real service keeps a result outside the observer's view, so two supplied retry rules can create duplicate service records, while a scope check or a visible receipt can avoid a repeated write. This claim requires the actual branch and audit evidence. It would extend the existing paper with a specific authenticated case; it would not establish broad novelty, general safety, natural agent behavior, or a guarantee of exactly-once execution.
