# Independent method review

Date: 2026-10-14.

Result: **PASS for the stated probability model.**

A separate Codex agent did this review. The agent did not import the main analysis code. No human review occurred. The review gives no evidence about an actual AI system.

## Scope

The review covers the saved plan, configuration, probability method, all 36 design rows, all 12 minimum-length rows, and all 5,982 time rows. It also checks small cases with complete sequence enumeration and a separate state method.

A failure has probability p. A clean result has probability q = 1 - p. Results are independent and p stays fixed. A clean run means k clean results in sequence. The horizon H is the maximum number of tests. A false declaration means a claim that p < p0 when p >= p0.

## Derivation of the main recurrence

Let F_t be the probability of no clean run of length k by test t. For t < k, F_t = 1. At t = k, the only accepting sequence consists of k clean results. Thus F_k = 1 - q^k.

For t > k, a first run that ends at t must have three parts:

1. No accepting run in the first t-k-1 results.
2. A failure at position t-k.
3. Then k clean results.

These events concern disjoint draws. Their joint probability is F_(t-k-1) p q^k. Thus:

    F_t = F_(t-1) - p q^k F_(t-k-1).

This proves the main recurrence under the independence assumption. The rolling acceptance probability is 1 - F_H. It does not treat overlapping windows as independent.

## Independent calculation

The validator uses a coefficient formula. It does not advance F_t from F_(t-1). Define the formal generating function G(z) = sum_(t>=0) F_t z^t. The recurrence gives:

    G(z) = (1 - q^k z^k) / (1 - z + p q^k z^(k+1)).

Let a = p q^k. Expand the reciprocal denominator as a formal series:

    1 / (1 - z + a z^(k+1))
      = sum_(j>=0) (-a)^j z^((k+1)j) / (1-z)^(j+1).

For n >= 0, its coefficient is:

    A_n = sum_(j=0..floor(n/(k+1))) (-a)^j C(n-kj, j).

Set A_n = 0 when n < 0. It follows that:

    F_n = A_n - q^k A_(n-k).

C(u,v) is the number of ways to choose v objects from u objects. The validator calculates these integers exactly and evaluates the coefficient sum at 90 decimal digits. It evaluates each time point separately. It finds first-acceptance mass by taking the difference between two cumulative probabilities. Thus this check does not reuse the main first-hit recurrence.

## Controls

For 198 small parameter cases, the validator enumerates all binary sequences. It sums their exact rational weights with Python Fraction. It compares this result with an exact run-length state calculation and the coefficient formula. These checks cover every H from 0 through 10, every k from 1 through H+1, and p in {0.1, 0.5, 0.9}. A case is one (H,k,p) combination. It is not one sampled sequence.

A further 84 cases compare the coefficient formula with exact state probabilities. These include H up to 24 and p as low as 0.001. The state method checks exact probability conservation. The boundary checks cover p=0, p=1, H<k, H=k, and k=1. All checks passed.

The coefficient and exact rational results have zero difference in the 198 small cases at the stated precision. This is a result for these cases. It is not a proof that all floating arithmetic is exact.

## Rules, bounds, and minimum lengths

For a fixed k and H >= k, acceptance in the first window implies acceptance in one complete separate block. Acceptance in a separate block implies acceptance in a rolling window. Thus the events are nested. Separate blocks use disjoint draws. Their acceptance probability is 1 - (1-q^k)^floor(H/k). The sum of the H-k+1 rolling-window probabilities is a union bound; it is not an independence formula.

For a fixed outcome sequence, a run of length k+1 contains a run of length k. Thus rolling acceptance cannot increase as k increases. The union expression also decreases with k: its adjacent ratio is q(H-k)/(H-k+1), which is below one for this grid.

The validator finds each minimum length by a linear search. The main code uses a binary search. The linear search starts at k0. Every smaller k fails because even its first-window acceptance probability exceeds alpha. The validator checks each chosen k and k-1 directly. It also checks k0 <= k_star <= k_union <= H. Every length check passed.

Increasing H adds possible accepting sequences and cannot lower acceptance at fixed k. Increasing p can only lower acceptance: couple all outcomes with the same independent uniform draws U_i, and define a clean outcome as U_i > p. Each higher p removes clean outcomes from that path. Therefore, over the composite null p >= p0, the largest false-declaration probability occurs at p = p0. This argument covers the full interval, not only the three saved p/p0 values.

The 5% bound applies to one design whose p0, k, and H are fixed before results. This study does not give a joint 5% bound for a user who selects a design after looking at results. It does not give a bound for system changes, dependent draws, delayed labels, or a changing p.

## Full output check

All 36 grid rows match the independent calculations. This includes one-window acceptance, separate-block acceptance, rolling acceptance, the union bound, and rolling acceptance at both corrected lengths.

All 12 calibration rows and their predecessors match. The closest calibration value is about 0.0000019202 from alpha. This distance is much larger than the numeric error.

All 5,982 trajectory rows match. Cumulative probabilities are monotone. The first-acceptance masses plus the final no-acceptance probability sum to one, with an allowance for 30-place output rounding. The two final cumulative values match the relevant grid rows.

The largest difference between a saved probability and the independent value is 4.9991551e-31. This is below the required 1e-28 limit. The main code saves probabilities with Python fixed-point formatting at 30 decimal places. Its output-rounding allowance is 5e-31. Thus the saved-value agreement and this allowance also imply a pre-format difference below 1e-25. No separate access to hidden unrounded outputs was needed.

The plan and configuration hashes match the saved input manifest. The summary row counts and primary hypothesis counts match the CSV files. The primary result is 9 of 9 selected conditions above alpha. This is a finite design-table result, not a statistical significance result.

## Research limits

The run-probability formula and the problem with repeated tests are established ideas. The report can claim a new dated audit table for the fixed grid. It must not claim a new theorem or a new general testing method.

All outputs are model calculations. No AI model, reviewer, or real test process was measured. A probability close to 5% in this model does not certify system safety. The calculation does not show that the independence and fixed-rate assumptions hold in practice.

No material mathematical error was found. No change to the plan or to the main results was needed for this review.

## Repeat the review

Run this command from the study folder:

    python3 validate.py

The script uses only the Python standard library. It writes validation_results.json. It does not import analyze.py or change the saved result files.
