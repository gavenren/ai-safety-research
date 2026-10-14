# Derivations for the fixed independent model

These are checks of established run-probability calculations. They are not new theorems.

## Definitions

A failure has probability p. A clean trial has probability q=1-p. All trials are independent and have the same probability. T_k is the time of the first run of k clean trials. H is the fixed maximum number of trials. F_n=P(T_k>n).

## One window and separate blocks

The first k trials are all clean with probability q^k. There are B=floor(H/k) complete, preassigned disjoint blocks. Their clean events are independent. The probability that at least one is clean is 1-(1-q^k)^B. An incomplete final block cannot pass.

One planned window is contained in the set of separate blocks. Each separate block is one possible rolling window. Thus their acceptance events are nested, path by path. For H>=k, their probabilities obey one <= separate <= rolling. Overlapping rolling-window events are not independent.

## First-run recurrence

For n<k, F_n=1. At n=k, the first hit has probability q^k, so F_k=1-q^k.

For n>k, a first hit at n requires three independent parts:

1. No hit in trials 1 through n-k-1.
2. A failure at trial n-k.
3. Exactly k final clean trials.

The failure is necessary. Otherwise a clean run would have finished at n-1. It also separates the prefix from the final run. Therefore P(T_k=n)=F_(n-k-1) p q^k, and

```
F_n = F_(n-1) - p q^k F_(n-k-1), n>k.
P(T_k<=H) = 1-F_H.
```

This also gives the full first-hit distribution and the residual no-hit probability at H. No state after a successful declaration affects this event.

## Independent coefficient check

Multiplying the recurrence by z^n and collecting coefficients gives the formal generating function

```
sum_(n>=0) F_n z^n = (1-q^k z^k)/(1-z+p q^k z^(k+1)).
```

Expand the reciprocal denominator as a geometric series in p q^k z^(k+1)/(1-z). Define A_n=0 for n<0; otherwise

```
A_n = sum_(j=0..floor(n/(k+1))) (-p q^k)^j binom(n-kj,j).
F_n = A_n - q^k A_(n-k).
```

The finite coefficient sum is an independent way to evaluate the probabilities. The validator uses 90-digit arithmetic. Small cases also use exact fractions and direct binary-sequence enumeration.

## Union bound and minimum length

There are H-k+1 possible k-windows when 1<=k<=H. Each has probability q^k. The probability of their union is at most min(1,(H-k+1)q^k). This bound does not assume that window events are independent.

For a fixed binary sequence, increasing k can only remove acceptance, and increasing H can only add acceptance. Thus the rolling probability decreases or stays constant with k and increases or stays constant with H. The uncapped union expression also decreases with k.

For 0<p0<1 and alpha=0.05, let k0 be the least integer with (1-p0)^k0<=alpha. If H>=k0, the choice k=H is feasible. Binary search finds the least feasible k_star. Checking k_star and k_star-1 proves minimality within this integer clean-run family. It does not prove that this is the best sequential test.

A union-bound length is feasible for the exact probability. Hence k_star<=k_union. Both lengths depend on the fixed H.

## Why the boundary p0 is the worst case

Couple trials with independent uniform variables U_i. Set failure X_i(p)=1 if U_i<=p. If p increases, the set of failed trials can only grow. A clean window can disappear but cannot appear. Thus every acceptance probability above is nonincreasing in p. For the declaration p<p0, the supremum false-declaration probability over p>=p0 occurs at p0.

At p=p0 the strict claim is false. Acceptance at p>p0 is also false. These are separate rows in the saved table.

## No unlimited-time guarantee

For fixed finite k and p<1, q^k>0. As B grows, 1-(1-q^k)^B tends to 1. The rolling probability is at least this separate-block probability and at most 1. It also tends to 1. A finite-horizon corrected length cannot be reused for an unlimited horizon.

## Endpoint checks

If H<k, the probability of acceptance is zero. If H=k, it is q^k. For k=1 it is 1-p^H. If p=0, acceptance occurs at k when H>=k. If p=1, it never occurs. These controls check both the event definition and the calculation.
