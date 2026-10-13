# Analysis plan

Date: 2026-10-13 (America/Toronto).
Status: saved before this run's routing calculations. This is not an external preregistration. The previous joint-vote study and its results were already known.

## Question and contribution

Does low agreement route more safety-panel errors to review than uniform random routing at the same workload? What error rate on routed items would let a reviewer reduce total error?

This is a secondary audit of a fixed saved-data release. Abstention, risk-coverage measures, and review routing are established methods. The contribution is the complete three-threshold, seven-set audit, its class-specific denominators, exact random-routing reference distributions, and conditional review break-even calculations. No new method or global novelty is claimed.

## Fixed input

Use the unchanged data_labels.csv from the October 12 study at repository commit 5da968d9c12edc82e1f0030d7e61f91233c509cd. Its SHA256 is a8c004743230361498dc7eaca9ee9900bbc3a4a7f0dfba113b0052668325be7e. It has five saved model votes for each of 1,398 items from seven sets. Keep all common items and all five models. Check key uniqueness, shared reference labels, and binary votes. Source policies and reference-label quality differ. There is no new model inference or human-review data.

## Hypothesis and decision criteria

The directional hypothesis is that accepting only unanimous votes lowers accepted-item error in all seven sets, relative to accepting every majority vote. Report how many sets improve, tie, or worsen. Check the two intermediate routing choices in full. No significance test or deployment decision is planned. A negative or mixed result is valid.

## Method and measures

For each item, let s be the number of flag votes. The majority label is 1 if s>=3. Agreement is max(s,5-s). Accept the majority label when agreement is at least t, with t in {3,4,5}. Route all other items to review. The same rule applies to both reference classes. No within-score random tie breaking or threshold fitting is used.

Primary output: 7 sets x 3 thresholds = 21 rows. Supplement: each of two reference classes separately gives 42 rows. No pooled primary rate is used. Keep all 1,398 aligned item summaries with routing decisions to support reproduction.

For each row save total items N, baseline majority errors E, accepted items A, accepted errors EA, deferred items D=N-A, and deferred errors ED=E-EA. Report coverage A/N, selective error EA/A, residual automated error EA/N, deferred-item error ED/D, and error capture ED/E. Use an empty field when a denominator is zero. Define all denominators in the report.

Baselines: no deferral (t=3); uniform random selection of exactly A items from the same finite group. Under random selection, accepted errors X have a hypergeometric distribution with population N, error count E, and draw count A. Save all possible X and exact probability numerator/denominator. Calculate the mean and 2.5%/97.5% quantiles by integer arithmetic. Divide quantiles by A for accepted-error ranges where A>0. These ranges describe random routing on the fixed records. They are not population confidence intervals or a test of model safety. Class-stratified random references are descriptive, and do not assume that a live router can see the reference class.

Reviewer scenarios: for h in {0,0.05,0.10,0.20,0.30,0.50}, calculate (EA+h*D)/N and compare it with E/N. Here h is the reviewer's mean error on this exact routed subset under the source labels. Review replaces the panel decision. It can correct a wrong decision or make a correct decision wrong. No human or model review performance is measured. For D>0, total error falls exactly when h<ED/D. Derive and check this identity. Include the equal-workload random-routing expectation (A*E/N+h*D)/N under the explicit assumption of the same h in that different routed subset. Do not infer this assumption in real use.

## Controls, uncertainty, and limitations

Verify count conservation, nested acceptance, rates in range, class sums, full-acceptance identity, unanimity endpoints, all-correct/all-wrong examples, and zero-denominator behaviour. Independently check the hypergeometric probabilities by a recurrence or direct small-subset enumeration, and check mean A*E/N, total probability one, and quantile boundaries. Validate reviewer identities with exact rational arithmetic.

All results are finite-data descriptions or conditional calculations. Do not attach population error bars to these selected records. The exact routing distribution is the only randomized baseline; no random seed is needed. Unknown label error, item relationships, dataset selection, training overlap, prompt changes, and future shift remain unmeasured. There is no training/test split because no rule is learned or selected. The analysis cannot validate deployment performance.

## Reporting and review

Save code, data, complete tables, probability distributions, versions, commands, logs, actual failures, and a figure if useful. Record later changes and exploratory examples. Explain how this question differs from the October 10 transfer correction and October 12 independent-vote studies. Use current primary sources and a bounded novelty claim. Obtain separate source/method and final reproduction review before publication. Preserve data attribution and do not assign a new license to the owner's work.
