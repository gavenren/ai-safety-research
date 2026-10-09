# Analysis plan

Date: 2026-10-09. Saved before calculation.

## Question

For a fixed budget of 300 binary safety tests, how much can the chance of zero observed failures change between three distributions with the same mean failure probability and within-group correlation?

## Contribution and scope

This is an exact mathematical sensitivity study. It does not run or fit an AI model. Earlier research already studies Beta mixtures, repeat attempts, and test budget allocation. The proposed contribution is a repeatable comparison of three matched distributions for a zero-failure decision rule. It does not claim a new probability model, theorem, or first study of dependence.

## Hypothesis

Mean failure probability and pairwise correlation do not determine the chance of zero failures when each group has at least three tests. Equal first and second moments must give equal zero-failure probabilities for one or two tests per group. Differences can increase when a fixed budget uses fewer groups and more repeated tests.

## Model

Each group has an unobserved failure probability Q. Groups are independent draws from one fixed population. Given Q, repeated binary outcomes in the group are independent with failure probability Q. Equal group sizes m divide total budget N=300. There is no model drift, adaptive stopping, or measurement error.

Let p=E[Q], rho=Var(Q)/(p(1-p)). Compare:

1. Beta: Q has shape parameters a=p(1/rho-1), b=(1-p)(1/rho-1).
2. Zero-atom: Q is zero or h=p+rho(1-p); the probability of h is p/h.
3. One-atom: Q is l=p(1-rho) or one; the probability of one is (p-l)/(1-l).

At rho=0, use Q=p for all three models. An atom means a nonzero probability at one exact value. These models are selected examples, not claimed extrema over all distributions.

## Grid and baseline

N=300. Repeats m in {1,2,5,10,30,100,300}. Independent groups G=N/m.
Mean p in {0.001,0.01,0.05}. Correlation rho in {0,0.01,0.1,0.5}.
Use the independent-outcome probability (1-p)^N as the baseline.
The target rate is p0=0.01. The nominal false-clearance limit is alpha=0.05.

## Measures

For each grid point compute P0=[E[(1-Q)^m]]^G. This is the probability that all 300 tests show no failures. Also compute the conventional variance effective sample size N/[1+(m-1)rho], and the corresponding plug-in zero-failure probability. This plug-in is a comparison only, not an exact probability or valid certificate.
For each model, rho, and m, solve P0(p)=0.05 by bisection. Report the boundary as conditional on the selected model and known rho. It is not a population-independent safety guarantee or a fitted confidence interval.

## Decision rule

A hypothetical rule declares evidence for p<p0 only if no failure is seen in the 300 pre-planned tests. At p=p0, the probability P0 is the rule's probability of making that declaration at the boundary. Flag a value greater than 0.05. Under each model P0 decreases in p, so this boundary is the maximum over p>=p0. Include a proof or remove this composite-null interpretation if it cannot be justified.

## Validation and uncertainty

Check all model moments algebraically and numerically. Check m=1 and m=2 equality, rho=0 equality, probabilities in [0,1], monotonic decrease with p, bisection residuals, and the full-dependence limit. Use a second high-precision calculation for the full grid. Request separate agent review of derivations, code, and claims.
No Monte Carlo sampling is planned. There are no random seeds or sampling confidence intervals. Numerical agreement and sensitivity to model assumptions will be reported separately. No p value from real-world observations will be reported.

## Publication criteria

Publish only if all checks pass and the report states that results are conditional mathematical calculations. Include all grid rows and negative controls. Record any plan change below. Do not assign a new license. No private data, harmful prompts, or paid services are used.

## Changes

None at plan creation.
