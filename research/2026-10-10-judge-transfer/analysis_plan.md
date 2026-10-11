# Analysis plan

Saved: 2026-10-10, before data-wide calculations or results.
Status: planned secondary analysis with controlled class reweighting.

## Question and contribution

Does a standard error correction, fitted on six source test sets, reduce rate error on the seventh test set?
The correction estimates the share of items with a positive reference label from the share that an AI judge flags.
This study tests cross-test-set transfer using the saved Safety-Flag decisions. It does not introduce a new correction method.
The source already studies classification errors, confidence calibration, pooled ranking stability, and cost under changed class proportions. This study changes the calibration source and checks corrected prevalence error on the held-out test set.
A limited source search cannot establish first discovery.

## Hypothesis

A correction that uses other test sets will not always reduce absolute rate error. Differences in conditional error rates can make it worse.
This is a descriptive hypothesis about the selected public records and the planned mixture grid.

## Inputs and scope

Use Safety-Flag repository commit 82d39d018c5522dfbdf303b49c5d83a8444d03d2.
Use the five primary, general-purpose model rows: Llama-3.1-8B, Mistral-7B, OLMo-2-7B, Qwen2.5-7B, and gemma-2-9b.
Exclude the source's Qwen2.5-32B reference because its precision differs across test sets. Exclude dedicated guards and other reference rows to keep one clear protocol.
Use all seven test sets and the intersection of item IDs across these five models, separately for each test set. Verify that reference labels match across models and that all option-label predictions are binary.
Read the source's solo.answer_lp decision, as its primary analysis does. This is the higher-probability option, not necessarily the generated JSON verdict.
Store only test set, item ID, model, binary reference label, and binary option decision. Do not publish source prompts, harmful responses, or extra metadata.
Data are derived records under CC BY 4.0. Keep attribution and retrieval hashes.
The first candidate, C-SafeQA, is gated. No access request was made and no gated data will be used.
Before this plan, one record and the source analysis code were inspected for schema and methods only.

## Method and baseline

For each model and held-out test set, pool counts from the other six sets to obtain sensitivity s_c and false-positive rate f_c.
Sensitivity is P(judge flags | reference positive). False-positive rate is P(judge flags | reference negative).
Set J_c = s_c - f_c. J_c describes how well the two reference classes can be separated.
For the held-out set, measure s_t and f_t from its released labels and decisions.
For each assumed positive-class share p in {0.01, 0.05, 0.10, 0.25, 0.50}, calculate q = p*s_t + (1-p)*f_t.
This q is an expected judge flag rate in a controlled mixture. It is not a newly observed deployment rate.
The raw baseline estimates p by q. The corrected estimate is (q-f_c)/J_c.
Show both the unbounded corrected estimate and its projection to [0,1]. Use the unbounded result for the primary comparison. Clipping is a secondary operational comparison.
If J_c <= 0, mark the cell as not eligible for positive-orientation correction, report it, and do not silently delete it.
The known-p control is exact by construction. A fixed 0.5 baseline will also be reported: this is useful at the source's balanced design but has no access to the chosen mixture share.
The no-transfer oracle uses the held-out error rates and should recover p when its J_t is nonzero. This is a calculation control, not a usable estimator without target labels.

## Measures and decision rules

Plan 5 models x 7 held-out sets x 5 mixture shares = 175 cells.
Save all confusion counts, source/target error rates, J_c, q, corrected/clipped estimates, signed and absolute errors, and the error change.
A positive error change means correction is worse than the raw baseline. Use 1e-12 tolerance for ties.
Report improved/worse/tied counts and mean absolute error, overall and by model and p. These cells overlap and are not independent statistical trials.
Report out-of-range estimates and small J_c values. Do not choose a post hoc minimum-J cutoff.
Verify the bias identity: corrected-p = [p*(s_t-s_c)+(1-p)*(f_t-f_c)]/J_c.

## Uncertainty and controls

Use 2,000 stratified item bootstrap draws with numpy default_rng seed 20261010.
Resample items within each test-set/reference-class stratum. Use the same selected item indices for all five models, preserving paired decisions. Keep class sizes fixed.
Recompute source and target error rates for each draw. Report 2.5th and 97.5th percentiles for the signed error and the absolute-error change for each planned cell.
These are conditional sampling intervals. They do not cover source label error, dependence between related items, policy differences, model updates, or real deployment shift.
If any draw has J_c <= 0, report its fraction and suppress that cell's correction interval. Do not hide invalid draws or publish a bounded interval across a singular correction.
Save bootstrap error-rate draws so interval calculations can be repeated.
Check no held-out IDs enter calibration under the compound (test set, item ID) key. The source does not provide enough text or lineage to rule out semantic duplicates across test sets. State this limit.
Use an independent calculation check from the saved minimal data. Check arithmetic controls, full row counts, file hashes, and selected bootstrap summaries. No model inference or training is run.

## Interpretation limits

This is a secondary analysis of fixed model outputs plus exact mixture calculations. The labels preserve different source policies. They are not universal ground truth.
The study measures transfer across these specific test sets. It does not show a live deployment failure rate or general performance on future content.
No causal claim, significance test across the overlapping cells, safety certification, or novelty guarantee will be made.

## Changes

None at plan save.

### Amendment 1: data quality, before rate analysis

The first fetch stopped because Aegis has two duplicate IDs per model. A separate schema audit found that all repeated records are identical, including fields outside the analysis. Retain one copy per ID, matching the source analysis. Reject conflicting copies. No error-rate results had been calculated when this rule was set. The original plan SHA256 was 8b368bf1a8de9691c3f212f651df196d009df490247c834db54623b01c946d15.

The source pool uses class-count weights across its six sets. Bootstrap ranges are conditional item-bootstrap sensitivity intervals, not validated population confidence intervals. Related items, including contrast pairs across classes, can make these ranges too narrow. At empirical class rates of zero or one, the bootstrap does not express unseen outcomes. A separate methods agent checked the formula and these limits before analysis.
