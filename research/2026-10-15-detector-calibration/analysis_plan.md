# Saved analysis plan

Date: 2026-10-15 (America/Toronto). Save this plan and its hash before calculation. This is a mathematical audit of synthetic inputs. No AI system is tested. Earlier repository results and a primary-source search are known. This is not external preregistration.

## Question and contribution

How does uncertainty from a small positive-control set affect a zero-flag test whose sample size uses measured detector sensitivity? Does a one-sided exact lower bound control false declarations? What happens to acceptance and planned workload under a fixed cap?

The method is established binomial inference with a split error budget. The contribution is the complete joint probability and workload table for the specified rules. This is distinct from October 10 error-rate transfer and October 14 repeated target windows. It claims no new theorem or first treatment of imperfect judges. Source search includes Feng et al. 2026, Lee et al. 2026, Cai et al. 2021/2023, and NIST binomial limits. Exact versions and read sections will be recorded.

## Model

A fixed detector flags each true failure with probability s (sensitivity). The m positive controls are known failures, independently sampled from the same conditional failure population as the target. K, the count flagged, has Binomial(m,s) distribution. Control labels are correct. The target sample is independent of the controls and contains independent items with fixed true failure probability p. The detector and system stay unchanged. A target item is flagged with probability q=p*s+(1-p)*f, where f is the false-positive rate. The grid sets f=0. This maximizes zero-flag probability at fixed p and s. The correction proof allows any f>=0.

A declaration claims p<p0. It is false for p>=p0, including equality. One calibration and one target batch are allowed. The batch length may depend on K but is fixed before target outcomes. All n target tests are performed even if a flag appears early. There is no repeat, model selection, adaptive prompt, repair, or stopping search. Only zero target flags permit a declaration.

## Rules

Let N(a,b) be the least positive integer n with (1-p0*a)^n<=b. If a=0, no finite n is available.

- perfect_assumed: n=N(1,.05). Ignores detector errors. It is an intentionally wrong baseline when s<1.
- known_sensitivity: n=N(s,.05). Uses the true s as an unavailable oracle comparison.
- point_estimate: n=N(K/m,.05). If K=0, skip the target batch and make no declaration.
- lower_bound: use the one-sided Clopper-Pearson lower limit L(K) with error delta=.025. L(0)=0. For k>0 it solves Pr[Binomial(m,L)>=k]=delta. Use n=N(L(K),.025). If K=0, skip the target batch and make no declaration.

The main implementation uses the lower side of a bracket for L, to avoid rounding it upwards. It checks every chosen n and predecessor. Calibration error plus target error is .05. The proof can use the sharper bound delta+(1-delta)*.025=.049375. This is unconditional over calibration and target observations; it is not a promise for each observed K.

Use both no target cap and H=20*N(1,.05). If a rule requires n>H, skip the entire target batch and make no declaration. Never replace n with H. The oracle and assumed-perfect rules do not require K>0. A skipped test is not a safe result.

## Grid, measures, and decision criteria

Use every combination in config.json: p0 in {.001,.01,.05}, m in {5,20,100}, s in {.1,.25,.5,.75,.9,1}, p/p0 in {.5,1,2}, four rules, and two cap settings. There are 1,296 result rows. These are chosen inputs, not fitted observations. The planned worked example is p0=.01,m=5,s=.1, both caps and all p multipliers. Any other highlighted example is exploratory.

For each rule, enumerate all k=0,...,m. Let A(k) indicate that a batch is launched. Its declaration probability is

sum_k Pr(K=k;s)*A(k)*(1-p*s)^n(k).

For the two K-independent baselines the formula reduces to one power or zero. Save the full policy for each possible K, all grid probabilities, and workload. Record launch probability, probability of no declaration, unconditional expected planned target count E[A*n], conditional target count E[A*n]/Pr(A) when defined, and maximum launched count. Control cost m is separate; no money or human time is inferred. These target counts are expectations of full batch sizes, not measured compute or sequential stopping costs.

Primary descriptive hypothesis: at least one boundary condition p=p0 for point_estimate exceeds .05 without a cap. Count all such conditions, the maximum, and ties. Also report cap effects without discarding adverse or negative results. The corrected rule must meet its proved bound under the model. Check the oracle's .05 bound. For p=.5*p0 report true-declaration probability; for p=2*p0 report false declarations. Do not describe a low false-declaration rate alone as practical success.

## Controls, uncertainty, and reproduction

Use exact finite sums with 70-digit Decimal arithmetic and 220 bisections; save probabilities to 30 decimals. No random sampling or seed is needed. An independent validator must use a different numerical route for the lower bounds and integer lengths, then check all tables. Include exact small enumeration controls, binomial normalization, s=0 and s=1, p=0 and p=1 where defined, cap event inclusion, monotonicity in p, and nonzero f controls. Check input and plan hashes.

Save code, inputs, bounds, policy branches, raw tables, summary, dependency versions, logs, derivations, figure, source reading limits, and failed checks. Core calculations should use the Python standard library. Existing plot packages may be used. No paid service, package install, or model inference experiment is authorized by this plan.

No sampling confidence interval is appropriate for these deterministic model probabilities. Numerical uncertainty must be checked separately from model uncertainty. Correct labels, sensitivity transfer, stable rates, and independence are not established for a real detector. The finite grid cannot establish a global worst case for the point-estimate rule.

## Release

Write the complete report with limits, rights, ethics, AI-use disclosure, and no-human-review status. Use the relevant NeurIPS checklist items as a review aid. Get independent method and final reproduction checks. Publish only after required checks pass; verify all remote files and preserve prior files. Record amendments before new analysis. No study result is yet available when this plan is saved.
