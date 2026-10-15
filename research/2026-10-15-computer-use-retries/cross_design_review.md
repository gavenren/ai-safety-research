# Review of the plan before scored trials

Date: 2026-10-15. Reviewer: a separate Codex agent. This is an AI review, not human review or external peer review. No website action was made by this reviewer. Scored trials were pending when these files were reviewed.

## Decision

No material design blocker was found. The plan is suitable for the stated narrow question after the lead fixes one stale preflight sentence and freezes the files. This decision is not a check of results which do not yet exist.

The plan correctly treats the work as a selected replication on hosted public demonstrations. It does not claim a new retry protocol, natural agent behavior, server persistence, or a general website failure rate.

## Files and checks

Reviewed cross_plan.md, cross_runner_instructions.md, cross_assignments.csv, and cross_preflight.md. Also read the saved raw DemoQA and DataTables preflight action records and visible task states in the private work directory. No private account data was needed for this review.

A separate Python check recreated the stated random.Random(20261016) procedure. It used a fresh copy of the stated six rule-view pairs for each block, with one random generator across DemoQA then DataTables. All 48 CSV assignments matched. There are 48 distinct trial IDs, four trials in each site-rule-view cell, 24 trials per site, and 12 All controls per site. All 24 DemoQA tokens are distinct. DataTables has no typed token, as stated.

## Feasibility

The DemoQA raw record shows the fixed search before and after Submit. Its late hidden read has no target row. Clearing search after the second Submit shows two identical target rows. Reload restores the three initial sample rows and empty search.

The first DataTables late read did not meet the 24-second gate. This failed check is retained. The second preflight shows the hidden search after the first Add and a late hidden read. Its second Add is followed by a three-entry footer and, after search is cleared, three full row vectors. One vector is the initial baseline. Reload restores that baseline and empty search. The reported elapsed times agree with subtraction of the recorded request and later-read timestamps: 30.611 seconds for DemoQA; 19.606 and 36.318 seconds for DataTables. These are recorded observation intervals, not service latency measurements.

The preflight is enough to admit the proposed workflow. It does not prove every later trial will have the same result. The plan keeps failed and unstarted assignments and does not permit replacements.

## Rules, timing, and outcome definitions

The ready-state conditions require the active search and complete table. Open forms, missing controls, read errors, and loading are unknown. This prevents a missing page from being scored as zero. Disabled Next prevents an incomplete page from being used as a full audit.

The clock starts at the first final Submit or Add request. The Wait24 read must start at or after 24 seconds from that request, even if the first zero was already later. The runner must check the 120-second deadline again after a retry form is filled. This avoids using an earlier time check to permit a late Submit. No scored reload is allowed because reload resets these examples.

Absence permits one repeat after ready zero. Wait24 permits one repeat only after the eligible new ready-zero observation. Scope removes the search only when Hidden is still active and never repeats a write. These branch definitions are consistent between the plan and runner instructions. All assigned controls stay in the denominator.

The task-specific effect definitions are clear. DemoQA counts exact-token rows. DataTables compares observed complete row vectors with the initial baseline and counts new rows. A repeated DataTables click creates an extra row with a different label; it is not an identical-data duplicate. The report must retain this difference.

The final audit occurs after the saved decision and before reset. Cleanup zero cannot be used as an audit outcome. A later image or audit cannot repair a wrong or unresolved earlier decision. The audit is a visible browser-state check, not an independent service record read.

## Important limits retained

- DataTables shows footer totals in the same screen. The supplied rules ignore those totals. Thus, the trial is not evidence that the full screen concealed success.
- One runner per site shares the host and browser service. Repeated deterministic trials are not independent samples of sites or agent behavior.
- Both sites use table tasks. They add two providers but limited task diversity.
- Receipt is unavailable. No generic message or form closure is promoted to an exact-request receipt.
- The fixed count and activation gate are separate. A missing branch is untested and cannot justify replacement trials.
- No signup, payment, message, or account record is needed. Cleanup is verified reset of temporary example state.

## Small edit before freeze

The question section still says that a second DataTables preflight must verify the gate before freeze. That check is already complete in cross_preflight.md and its raw P02 record. Change the sentence to state that the second check passed at 36.318 seconds. This is a factual update before the plan is frozen, not a result-dependent change to the scored design.

## Points to check in final analysis

Keep these cases separate: on-time correct confirmations, wrong-count confirmations, late confirmations, unresolved decisions, and missing audits. A late one-row confirmation fails the clean-confirmation criterion but is not a wrong-count claim. A confirmation with no audit has unknown truth. Record tool requests, successful tool returns, errors, and observed row effects separately. Do not infer one from another.

Ensure each eligible Wait24 observation has its own actual start time and raw state. Retain the footer totals in published task extracts even though the policy ignores them. Verify all image crops include the relevant search, row, and pagination evidence. This plan review did not inspect scored images or validate the later parser, measurements, report, cleanup, or publication.
