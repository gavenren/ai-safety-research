# Independent method review

Date: 2026-10-15.

Status: PASS. A separate Codex agent did this review. This is an AI review. No human review occurred. No AI system was tested.

## Scope

The review covers the saved plan, probability model, code, all numerical tables, and the result summary. The reviewer read the main code to find its numerical method and file fields. The validator does not import or run that code. It uses separate calculations. The plan and input hashes still match the saved manifest.

The model requires correct control labels and transfer of detector sensitivity from controls to target failures. It also requires independent observations and a fixed system and detector. The calculations do not establish these conditions for a real system.

## Proof check

Let K be the number of flagged positive controls. Let L(K) be its exact one-sided binomial lower limit. The error probability of this limit is delta. The limit increases with K. For fixed true sensitivity s, the event L(K)>s is an upper tail of K. Inversion of the binomial tail gives

Pr[L(K)>s] <= delta.

The main program uses a lower numerical bracket for L(K). The independent calculation places the exact root within each saved bracket. Thus the numerical choice does not increase the limit.

Let B be the event L(K)>s. Suppose p>=p0, so the proposed declaration p<p0 is false. On the complement of B, the target flag rate q obeys

q = p*s + (1-p)*f >= p0*L(K).

For each launched batch in this event, the selected length n gives a probability of zero flags of at most beta. The target is independent of the controls. A skipped batch gives no declaration. On B the declaration probability is at most one. Thus the unconditional false-declaration probability is at most

beta*(1-Pr[B]) + Pr[B] <= beta + (1-beta)*delta = 0.049375.

This proof allows any false-positive rate f in [0,1]. It does not require f=0. The numerical grid uses f=0. At fixed p and s this choice gives the largest zero-flag probability. The bound covers one control set and one target batch. It is not a bound conditional on each observed K. It does not cover repeated calibration or a search over target batches.

A finite cap removes whole target batches that are too large. It cannot increase the declaration event or unconditional planned workload. Replacing a required length with the cap would be a different rule. The code does not do that.

## Numerical checks

Run `python3 validate.py` from this folder. The recorded run used Python 3.14.7. The validator uses the Python standard library and 90-digit Decimal arithmetic. It computes binomial mass by recurrence from zero successes. It then uses the complement of the lower tail for CP inversion. CP means Clopper-Pearson. This differs from the main direct upper-tail sum of binomial coefficients. It uses 290 bisections. It finds test lengths by integer doubling and binary search. The main calculation uses a logarithm and integer corrections.

The actual checks passed:

- All 128 bound rows, including 125 positive roots and their full numerical brackets.
- Six closed-form checks for the first and last positive roots.
- All 1,536 policy rows, including each selected length, its predecessor, cap choice, launch choice, and reason.
- All fields in 1,296 result rows, including the probability mixture, launch probability, expected planned count, conditional planned count, and maximum launched count.
- Exact enumeration of 45 small binomial cases and 216 small joint control-and-target cases.
- Binomial normalization and CP coverage at 21 size-and-sensitivity conditions, including zero and unit sensitivity.
- Cap event inclusion in 648 comparisons and failure-rate monotonicity in 432 groups.
- 576 endpoint and nonzero false-positive checks. These include p=0, p=1, s=0, and s=1.
- All 216 corrected-rule null rows below 0.049375 and all 216 oracle null rows below 0.05.
- Summary counts, maximum values, all maximum ties at saved precision, and all 24 planned-example rows.

The largest difference from a saved number is 4.992e-31. The saved-number comparison tolerance is 6e-29. The largest difference between the main lower bracket and the independent root is less than 5.804e-67. The smallest probability margin at an integer decision is 1.5125e-9. Numerical error is much smaller than this margin. These are checks on arithmetic. They do not measure uncertainty in the model assumptions.

## Issue found and resolved

The first summary retained one condition at a maximum. The saved plan asked for all ties. The reviewer requested this repair. The main summary now saves all ties at its stated 30-place precision. The two rules that do not depend on K now use the single target probability directly. This also removes irrelevant last-digit differences across control sizes. The reviewer checked the revised files. The plan and grid did not change. No material mathematical error remains.

## Interpretation limits

The point-estimate rule exceeds 5% in 41 of 54 boundary conditions, with and without the cap. Its grid maximum is about 11.31%. This is a maximum over the chosen grid. It is not a global maximum.

The corrected rule passes the bound under the model. Its low false-declaration rate alone does not establish practical success. In the planned example, the capped corrected rule launches with probability 0.856%. The full result table must also show the chance of a true declaration and the planned workload.

The grid results are deterministic probabilities for synthetic inputs. They are not observed incident rates or measurements from an AI model. A sample confidence interval for these computed values would be inappropriate. No random seed, new inference call, or paid service was used in this review.
