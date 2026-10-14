# Analysis plan: repeated clean windows

Run date: 2026-10-14, America/Toronto.

## Question and scope

For an unchanged system with independent binary test outcomes, how does a fixed test budget change the probability of a false declaration when any clean window can trigger acceptance? How much longer must the clean window be to keep that probability at or below 5%?

This is an exact probability-model audit evaluated with high-precision arithmetic. It is not an AI experiment or evidence about actual system failure rates. The repeated-testing problem and run-probability methods are established. The proposed contribution is the full dated comparison table and the minimum integer window lengths for the stated grid. No first-discovery claim is planned.

## Assumptions

- One unchanged system; one fixed failure definition; correct and immediate labels.
- Independent outcomes with constant failure probability p. Every test uses a fresh draw from the same population.
- A failure does not change the system. A later clean window can replace the earlier failed window only under the explicit repeated-window rules.
- The horizon H, rule, and window length are fixed before outcomes are seen.
- A declaration claims p<p0. It is false at every p>=p0, including equality.

## Design fixed before calculations

Set alpha=0.05. Use p0 in {0.001, 0.01, 0.05}. Set k0 to the smallest positive integer for which (1-p0)^k0<=alpha. Use H/k0 in {1, 2, 5, 10}. For each design use p/p0 in {1, 2, 5}. All 36 conditions will be saved.

Compare:

1. One planned window: accept only if the first k0 tests have no failure.
2. Separate blocks: accept if any complete disjoint k0 block within H has no failure.
3. Rolling windows: accept if any k0 consecutive tests within H have no failure.
4. Union bound: min(1, (H-k0+1)(1-p)^k0), an upper bound for rule 3, not a probability model for independent windows.

For each of the 12 (p0,H) designs, find the minimum positive integer k_star with rolling acceptance probability at p0 no greater than alpha. Find the minimum k_union satisfying (H-k+1)(1-p0)^k<=alpha. Search within 1 through H; feasibility follows from the single H-window probability. Check the candidate and its predecessor. Save rolling probabilities at both corrected lengths for all 36 conditions.

For the p0=0.01, H=10*k0 design, save cumulative acceptance and first-acceptance probabilities at every test for k0 and k_star. Save the probability of no acceptance by H separately. This illustration is selected before results.

## Hypotheses and decision criteria

The primary descriptive hypothesis is that the uncorrected rolling rule exceeds alpha at p=p0 for every H>k0 in the grid. Report every counterexample or tie. Check the pathwise nesting: one-window acceptance is a subset of separate-block acceptance, which is a subset of rolling acceptance. Verify that k_star<=k_union. The size of a gap is a result, not a significance test.

The minimum-length calculation is a deterministic design result under the model. It does not choose a rule from observed AI data. We will not label the correction optimal outside the fixed clean-window family.

## Computation, controls, and uncertainty

Use the first-hit recurrence for runs, with Python standard-library Decimal arithmetic at 60 digits. Retain at least 30 decimal places in probability files. Compare against a separate implementation at 90 digits. The reviewer must not import the main analysis code. Use direct enumeration and a run-length state calculation on small cases to check the recurrence. Check p=0, p=1, H<k, H=k, k=1, probability conservation, and monotonicity in H, k, and p where appropriate. Check each calibrated predecessor. Required numeric agreement is absolute error below 1e-25 for unrounded values and below 1e-28 for saved 30-place probabilities, with rounding allowance.

No Monte Carlo simulation is planned. No random seed or sampling confidence interval applies. Numerical precision checks do not remove model uncertainty. Any calculation failure or design change must be recorded. No empirical AI data, training data, private data, paid service, or new model call is used.

## Reporting and review

Include the complete derivation, plan hash, input configuration, code, raw results, versions, commands, logs, source-search record, source and method review, and separate final review. Explain the difference from the October 9 fixed-budget dependence study. State that Codex generated the work and that no human review occurred. Use the NeurIPS checklist only as a review aid. Publish only after required checks pass, then verify the remote files and index.
