# Plan: acceptance fences and reservation release

Date: 2026-10-25, America/Toronto. This plan is saved before implementation and execution.

## Question and contribution

When does evidence that future acceptance is blocked justify release of a reservation for external work? Compare a timeout, a zero-charge observation, an acceptance-fence receipt, a closure certificate, and a terminal outcome. Separate actual overspend from temporary exposure and uncovered liability. The contribution is a fixed regression corpus with independent implementation and full traces. The mechanisms are established, including in Zhu and Wang (arXiv 2610.00349v1). This is not a new protocol, priority claim, or test of a named implementation.

## Hypotheses

H1: Timeout, ZeroObservation, and FenceOnly each permit some premature releases and actual budget breaches.
H2: ClosureCertificate and TerminalOnly preserve charge coverage and the budget at every prefix.
H3: Some exposure breaches occur in cases whose final actual charge is within budget. Final outcomes alone miss these failures.
H4: ClosureCertificate can admit more safe work than TerminalOnly, but a saved certificate can be unavailable after the true state has already become safe.

## Model and inputs

This is an exact finite simulation. No provider or browser will execute a trial. Initially job A has a reservation of a units and a request in transit. It is not yet accepted. B has no reservation. Total cumulative budget C is fixed. Demands a,b are each 1 or 2. Capacity C is 1,2,3,4. Retain only a<=C: 14 settings. Include two resolution branches, charge and zero. Future branch choice is not visible to a rule or used to reduce unresolved liability.

Six events occur once each:

- A: accept job A if F has not occurred; otherwise reject it.
- E: resolve A. If accepted and the branch is charge, irreversibly charge a. Otherwise resolve with zero charge. No later A charge can occur after E.
- T: deliver the correct terminal result and settle A exactly once. Set its hold to zero and book its actual charge, even if an earlier rule released the hold. A late charge can make available balance negative; do not drop it.
- O: read current actual A charge, zero or a. This is a point observation only.
- F: atomically fence all future A acceptance and record accepted/resolved/charged status. It does not cancel accepted work. Its closure certificate is true exactly when A was not accepted, or A resolved with zero charge. A completed zero-charge result is a model terminal outcome; it is not a claim about the no-effect certificate format of a cited protocol.
- D: if A still has a hold, apply the selected release rule. Then atomically check available>=b and, if true, book and immediately charge B. B is synchronous in this model. A rejected B does not retry.

Require A<E<T and O<D. There are 6!/(3!*2!)=60 schedules. All five rules receive the same O,F,T actions at the same points. Compare use of evidence, not deployment costs. There are 14*2*60=1,680 input worlds and 8,400 rule outcomes. Branch copies when A is rejected are deliberate controls, not independent observations.

## Rules

All rules honor T. If T occurred before D, no hold remains and no early release is needed. Otherwise:

1. Timeout: release the entire A hold.
2. ZeroObservation: release only when O observed zero charge.
3. FenceOnly: release only when F occurred.
4. ClosureCertificate: release only when the saved F receipt contains a true closure certificate.
5. TerminalOnly: retain the hold until T.

The last two rules have different evidence interfaces from the weak baselines. The closure certificate is assumed sound and bound to this exact one-off job. Authentication, lost identities, retries, crashes, compromised sources, partial charges, and changing budgets are outside scope.

## State and truth

Save actual charge, hold, booked A/B charges, acceptance and resolution flags, fence state, O result, F receipt, settlement flag, and D decision. Available balance is C-hold-booked_A-booked_B. All local admissions use that balance. No rule uses the provider truth audit to make a decision, except the declared O,F,T data.

Provider liability L is the largest total A charge still compatible with the provider's current state and declared maximum charge. If A charged, L=a. If A resolved with no charge, L=0. If accepted and unresolved, L=a. If not accepted and not fenced, L=a. If not accepted and fenced, L=0. Do not use the future resolution branch to set L early.

At each event, record actual excess max(0,actual_A+booked_B-C), exposure excess max(0,L+booked_B-C), uncovered A liability max(0,L-hold-booked_A), and local deficit max(0,-available). Also record current liability and available balance.

## Measures and decision criteria

For each case record any actual breach, any exposure breach, exposure without final actual breach, any uncovered liability, their maximum units and first event, premature refund at D (a positive hold removed while L>0), negative available balance, B accepted/refused, and safe-feasible B refusal (refused although pre-D L+b<=C). Preserve A acceptance/fence outcome, final charge, release decision, and exact settlement count. Measures overlap; do not add them as independent failures.

Summarize every policy and branch, plus full input rows. Compare matched policies per world. H1-H4 use exact existence or zero checks, not statistical significance. Preserve all outcomes and failed controls. Save first adverse examples in canonical case order without claiming global minimality. No confidence interval or random seed is appropriate for this designed finite corpus.

## Controls

Check every case for one settlement, correct final booked A, immutable charges, fixed bounds on each job, and correct bookkeeping. A local accounting identity alone is not a safety claim.

Check all T-before-D cases for equal decisions across rules. Check F-before-A rejection. Check complete-rule prefix coverage and budget. Check that C>=a+b prevents actual and exposure breaches but does not necessarily prevent uncovered liability. Check paired charge/zero branches have identical decisions before E. Check final actual breach equals final negative balance because all final outcomes arrive.

Include named expected examples for: acceptance before fence with a late charge; fence before acceptance; early terminal receipt; zero observation followed by charge; zero resolution before fence; and zero resolution after fence with no refreshed certificate before D. Each named control must state expected outcomes before running.

## Independent check and reproduction

The main interpreter will use permutation enumeration. A separate agent will write a specification using event positions or another generator, without reading the main code or results. Freeze that implementation before comparison. Compare all input worlds, evidence, decisions, states, measures, and summaries. Run the main procedure twice into different new directories and compare deterministic outputs. Never silently replace partial runs.

Use Python standard library only. Record Python/OS versions, source and data hashes, commands, CPU/wall time, output bytes, and actual review status. Experiment limits per run: 8,400 outcomes, 120 CPU seconds, 300 wall seconds, 200 MB. Set a Unix CPU resource limit and check time/output size. Stop on unexpected errors and retain partial evidence. At most two complete main runs unless a documented correction requires another.

## Publication gate

Publish only after independent comparison, reproduction, source/claim review, privacy/rights checks, relative links, and a separate final review pass. Use the NeurIPS checklist as an aid. State that Codex generated the work, no human review occurred, and no live website, agent action selection, or production risk rate was tested. Do not criticize a real protocol as defective from these selected model rules. Do not assign a new license or incur paid compute.
