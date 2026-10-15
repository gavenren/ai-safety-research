# Independent method review

Date: 2026-10-15
Status: PASS
Reviewer: a separate Codex agent. No human review occurred.

## Scope

I read the saved plan, amended count-two guard, input configuration, and main implementation. I wrote a separate validator from direct event-time thresholds. It does not import `analyze.py`. I then compared the saved results with the independent calculations.

The checked main model has 256 cases. The late-execution suite has 16 cases. The stale-read suite has 64 cases. There are 13,440 total runs across policies, query schedules, and server modes. These are synthetic coverage counts. They are not samples from real computer use.

## Results

- All 13,440 run rows passed 255,360 exact field comparisons.
- All 13,440 event traces passed. They contain 167,520 events.
- The event checks include 676 attempt resolutions after the controller stopped.
- All five selected example traces passed.
- All 720 rows in the three summary tables passed 18,000 field comparisons.
- All 48 paired comparison rows passed.
- All 6,720 matched append and deduplication pairs passed.
- The terminal-drop rule and no-retry rule have no duplicates in every saved suite.
- The bound12 rule has no duplicates inside the declared timing contract.
- Equal-time completion occurs before the query. A zero-lag read at the execution boundary sees the original commit.

The validator uses exact integers and labels for run results. It checks rounded summary means from exact integer sums. No numerical tolerance is used for the run comparisons. The validation runtime was Python 3.13.7 with the standard library.

## Information available to the controller

I found no use of a hidden future outcome in a policy decision. The main controller uses the query schedule, declared static bounds, and the historical snapshot. The hidden resolution delay and outcome are used by the simulated environment and final audit. They do not enter a retry decision before the snapshot exposes them.

The terminal-drop rule receives stronger evidence than a count alone. All policies have access to the same response, but some ignore this status. This is an explicit model contract. It is not a claim that every ordinary web page exposes reliable action status.

## Formal arguments

The arguments in `derivations.md` are valid under the stated assumptions. A fresh absence read cannot distinguish an unresolved future commit from an unresolved future drop. The two-world safety/recovery equality applies only to the immediate one-retry decision specified there. It does not rule out a later safe retry after terminal status.

A truthful permanent drop state is sufficient for at-most-one effects with one retry. Read delay does not weaken that permanence. The fixed-time proof also requires valid execution and lag bounds, no rollback, and the recorded same-tick event order. The stress suites correctly remove timing assumptions while retaining truthful terminal status.

## Limits

This review checks the supplied model and calculations. It does not test a browser agent, measure a real service, verify a deployment contract, or establish a population error rate. The case grid weights all listed cases equally for summaries. It does not estimate the frequency of those cases in practice. The study provides evidence for a bounded evaluation design and a tooling contract.

No material method issue remains in the checked files. Final claim, reference, presentation, and package checks are separate publication steps.
