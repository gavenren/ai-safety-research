# Mathematical derivations

Date: 2026-10-09. Prepared and checked by a separate Codex agent. This is not human peer review.

## 1. Matched moments

Use 0 < p < 1 and 0 < rho < 1. Let v = rho p(1-p). Let s2 = E[Q^2].

For the Beta model, set c = (1-rho)/rho, a = pc, and b = (1-p)c. Then

    E[Q] = a/c = p,
    Var(Q) = ab/[c^2(c+1)] = p(1-p)/(c+1) = v.

Thus s2 = p^2 + v.

For the zero-atom model, let h = p + rho(1-p) and w = p/h. Since h >= p > 0, 0 < w <= 1. The distribution has mass w at h and mass 1-w at zero. Then

    E[Q] = wh = p,
    E[Q^2] = wh^2 = ph = p^2 + v.

For the one-atom model, let l = p(1-rho) and w = (p-l)/(1-l). Since 0 <= l <= p < 1, the weights are valid. The distribution has mass w at one and mass 1-w at l. Its mean is p. For a distribution on two points A and B with mean p, the variance is (p-A)(B-p). Here this gives

    Var(Q) = (p-l)(1-p) = rho p(1-p) = v.

All three distributions therefore match the first two moments. They do not generally match higher moments.

## 2. Correlation of the binary tests

Let X_i and X_j be different tests in one group. Each is a failure indicator. Given Q, the tests are independent Bernoulli variables with failure probability Q. Therefore

    E[X_i] = p,
    Var(X_i) = p(1-p),
    E[X_i X_j] = E[Q^2],
    Cov(X_i, X_j) = Var(Q),
    Corr(X_i, X_j) = rho.

Independent groups have zero covariance with each other. The specified model cannot represent negative within-group correlation. It also does not represent every possible dependence structure.

## 3. Chance of no failures

Let A_m = E[(1-Q)^m]. Conditional independence gives A_m as the chance that one group has no failures. Independent groups give P0 = A_m^G, where G = N/m.

The exact expressions are:

    Beta:
        A_m = product over j=0,...,m-1 of [(1-p)c+j]/[c+j].

    Zero-atom:
        A_m = 1-w + w(1-h)^m.

    One-atom:
        A_m = (1-w)(1-l)^m
            = (1-p)[1-p(1-rho)]^(m-1).

The Beta expression is the ratio of two Beta integrals. The other two expressions follow directly from their two probability masses.

For m=1, all models give A_1 = 1-p. For m=2, all give

    A_2 = 1 - 2p + E[Q^2]
        = (1-p)^2 + rho p(1-p).

Equal first and second moments are therefore sufficient for groups of size one or two. They are not generally sufficient for groups of size three or more. For example, the third moment in the one-atom model exceeds the third moment in the zero-atom model by

    rho(1-rho)p(1-p).

Thus their A_3 values differ by that positive amount, with the zero-atom value larger. This is a direct counterexample to identification of the no-failure chance from the first two moments alone. Degenerate cases can still have equality.

## 4. Monotonic decrease with p at fixed rho

The following derivatives hold for interior p and rho. They prove that the no-failure chance decreases with p in each family.

For the Beta model, c stays fixed. Therefore

    d log(A_m)/dp = -c sum over j=0,...,m-1 of 1/[(1-p)c+j] < 0.

For the zero-atom model,

    h' = 1-rho,
    w' = rho/h^2,
    A_m' = -w'[1-(1-h)^m] - wm(1-h)^(m-1)h' < 0.

Both terms are nonpositive, and the first is strictly negative in the interior. A second proof uses a common uniform random variable: both h and w increase with p, so Q can be coupled to increase with p. The function (1-Q)^m decreases with Q.

For the one-atom model,

    d log(A_m)/dp = -1/(1-p)
                    -(m-1)(1-rho)/[1-p(1-rho)] < 0.

Since G is a positive integer, P0 = A_m^G also strictly decreases. The rho=0 and rho=1 limits have the same property. Continuity gives P0(0)=1 and P0(1)=0. There is one root of P0(p)=alpha for 0<alpha<1.

It follows that the maximum chance of the all-zero declaration over p >= p0 occurs at p=p0, provided the chosen model, rho, N, and m remain fixed. This is not a claim about a union of unspecified models or about uncertain rho.

## 5. Limits

At rho=0, Q=p deterministically in all models. Hence A_m=(1-p)^m and P0=(1-p)^N.

As rho approaches one, Q has mass 1-p at zero and mass p at one. The Beta product gives the same limit: its j=0 factor is 1-p, and every later factor approaches one. Thus A_m=1-p and P0=(1-p)^G.

Full dependence applies within each group. It does not remove the assumed independence of different groups. P0=1-p only when G=1.

For p=0 or p=1, the binary variance is zero and correlation is not defined. The endpoint expressions are continuous limits. They are suitable for root bracketing, but should not be described as measured endpoint correlations.

## 6. Meaning of the variance effective sample size

The total count T has variance

    Var(T) = N p(1-p)[1+(m-1)rho].

For the sample mean T/N, the usual variance effective sample size is therefore

    N_eff = N/[1+(m-1)rho].

This identity is exact under the stated design. It matches the variance of a mean of N_eff independent Bernoulli variables. It does not identify the full distribution or a tail probability. Substitution into (1-p)^N_eff does not follow from the variance identity.

An explicit check at p=0.01, rho=0.1, and N=300 gives:

| m | Beta P0 | Zero-atom P0 | One-atom P0 | Variance-size substitution |
|---|---:|---:|---:|---:|
| 2 | 0.05705942126 | 0.05705942126 | 0.05705942126 | 0.06450576448 |
| 30 | 0.2559524079 | 0.3942946190 | 0.06572214764 | 0.4615786773 |
| 300 | 0.7234949221 | 0.9082568807 | 0.06632204145 | 0.9070333352 |

The substitution is not exact even for m=2. At m=300, it is lower than the zero-atom probability. It is therefore not a general conservative upper bound.

As an additional control, Jensen's inequality gives A_m >= (1-p)^m for m>=1. Thus each model has P0 >= (1-p)^N. For any fixed distribution of Q, the power-mean inequality also shows that A_m^(1/m) does not decrease with m. The no-failure chance therefore does not decrease when a fixed total budget uses larger equal groups, for the same latent distribution.

