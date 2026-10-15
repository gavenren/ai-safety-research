# Probability arguments

These arguments concern the synthetic model in analysis_plan.md. They do not establish its assumptions for an AI detector. The binomial limits and error allocation are established methods. No new theorem is claimed.

## 1. Calibration and target probability

Let K be the number of flags among m known failures. Independence and common sensitivity s give

P(K=k) = choose(m,k) s^k (1-s)^(m-k).

A fresh target item is a true failure with probability p. The detector has sensitivity s and false-positive probability f. Therefore its flag probability is q=p*s+(1-p)*f. Target trials are independent of each other and of K.

The policy maps K to a required target length n(K). This mapping is fixed before observations. A(K) is one if the test can launch and zero otherwise. Conditional on K=k with A(k)=1, the probability of zero flags is (1-q)^n(k). Summing over K gives

R(p,s,f) = sum_k P(K=k;s) A(k) (1-q)^n(k).

A skipped batch contributes zero. This is not a declaration that the system meets the target. The equation remains valid when n depends on calibration, because target outcomes do not set n. Reusing target data to select the size would need another argument.

## 2. Minimum integer length

For 0<a<=1 and 0<p0<1, let z=1-p0*a. For 0<b<1, z^n decreases strictly in n. The smallest positive integer with z^n<=b is ceil(log(b)/log(z)). The program checks the candidate and its predecessor to avoid a numerical rounding error. With a=0, no finite length works. The code marks this case as no test. It never divides by zero or uses n=0 as a successful empty test.

## 3. Exact one-sided lower limit

Define T_m(k,x)=P[Binomial(m,x)>=k]. For k>0 this is continuous and strictly increasing in x between zero and one. Set L(0)=0. For k>0, define L(k) by T_m(k,L(k))=delta. This is the one-sided Clopper-Pearson lower confidence limit. It is a standard binomial tail inversion [NIST](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

For a fixed true s, L(k)>s exactly when T_m(k,s)<delta. These k values form an upper tail. If j is the smallest such value, then P[L(K)>s]=P(K>=j)=T_m(j,s)<delta. If no such value exists, the probability is zero. Thus P[L(K)>s]<=delta for all s in [0,1]. This is a repeated-sampling statement about the planned controls, not a posterior probability for s after one K is seen.

The main program brackets each root for 220 bisections and uses the lower bracket endpoint. Rounding the bound down cannot increase its overcoverage error. The saved bounds include both full-precision endpoints. A separate high-precision calculation checks them and the resulting integer decisions.

## 4. Split-error guarantee

Let E be the event L(K)<=s. For the null p>=p0 and any f>=0,

q=p*s+(1-p)*f >= p0*s >= p0*L(K) on E.

When the corrected policy launches, n is chosen so that (1-p0*L(K))^n<=b. Hence the conditional declaration probability on each good calibration outcome is at most b. If it does not launch, this probability is zero. On E's complement it is at most one. Therefore

R <= b*P(E)+P(not E) <= b+(1-b)*delta.

With b=.025 and delta=.025 this gives .049375, below .05. The usual looser sum b+delta also gives .05. The argument is unconditional over the controls and the target. It does not bound the declaration probability for every observed K. For example, an unusually high control count can overstate true sensitivity.

A cap only removes possible declaration events. If a required length exceeds H, the policy runs no target batch. It does not shorten the batch. Thus the cap preserves the bound. The guarantee needs a fixed split and policy. Selecting a split or detector after results is outside this argument.

## 5. Oracle and worst-case direction

The known-sensitivity rule chooses n using true s and b=.05. If s>0 it has R<=.05 for every p>=p0 and f>=0. It is a comparison that assumes unavailable knowledge. At s=0 no finite length works.

For all fixed policies in this study, increasing p at f=0 decreases (1-p*s)^n. Thus p=p0 is the worst case over p>=p0. At a fixed p and s, any f>0 raises q and decreases zero-flag probability. The joint worst case over p>=p0 and f>=0 is therefore (p0,0). Positive false flags do not prove detector quality; they only make this particular zero-flag declaration less likely. They can also reduce true declarations when p<p0.

The point-estimate rule has no such general guarantee. Its full error is the mixture R, not the value calculated after substituting K/m for s.

## 6. Workload and acceptance

The unconditional expected planned target count is W=sum_k P(K=k) A(k)n(k). The launch probability is B=sum_k P(K=k)A(k). If B>0, the conditional count is W/B. If B=0 it is undefined. The maximum count uses only branches with positive probability at the stated s. All n tests are planned as one batch; these values do not describe stopping at the first flag.

The calibrated rules also need m known-positive controls. These costs stay separate from target counts. The oracle and assumed-perfect baselines use no control data. No human time, money, or real model compute is measured. A cap can reduce W mainly by preventing most tests. That reduction alone is not evidence of efficiency.

For p<p0, R is a true-declaration probability under the same model. We report p=.5*p0. This one alternative does not establish performance for all systems that meet the target or the optimality of the rule.
