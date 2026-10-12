# Analysis plan

Date: 2026-10-12 (America/Toronto). Saved before computation of ensemble results. This is a local plan, not an external registration.

## Question and contribution

Does independence conditional on the test set and reference class predict the error of majority votes in the pinned Safety-Flag records? The new work is a class-specific secondary audit of ten three-model panels and the full five-model panel. The product model and the concern about dependent errors are established. This study does not claim a new method or a first finding of dependent judges.

The October 10 report tested transfer of a single judge's rate correction. This study keeps each test set separate and compares joint votes with a product of the individual error rates. The question and calculations differ.

## Inputs

Use the unchanged reduced data from the October 10 study, pinned at this repository's commit a713543cfaa4188d6675826fc12ca3f9f2da582a. Those data derive from Safety-Flag commit 82d39d018c5522dfbdf303b49c5d83a8444d03d2. Five primary model aliases and seven test sets give 1,398 common items and 6,990 saved decisions. Use dataset plus item ID as the key. Require exactly one decision per model and a shared binary reference label. Reject missing values, duplicate keys, or inconsistent labels. Use only saved option-token decisions, not generated JSON verdicts. Do not run model inference.

## Hypothesis and decision criteria

The hypothesis is that the conditional product model differs materially from measured majority error in at least one full-panel class cell. Define material as an absolute gap of at least five percentage points. This is an audit threshold, not a safety standard or a significance threshold. Publish all 14 primary cells, regardless of direction. If none reaches the threshold, report this negative result. The ten triples are a planned sensitivity analysis, not separate independent replications.

## Method

For each test set and reference class, form five error indicators: one means that a model disagrees with the supplied reference label. Reference-negative error is a false positive (false alarm). Reference-positive error is a false negative (missed flag). Enumerate all ten triples and the five-model panel. A majority is wrong when more than half of its members are wrong. Odd panel sizes remove ties.

For each panel, calculate observed error from aligned item rows. Calculate the independent expectation by summing the product probabilities of every error pattern with a wrong majority. Each model keeps its own measured class error rate. Condition only on set and class. Item difficulty is not available and is not controlled. A gap can therefore include shared item difficulty and other dependence; it is not a causal estimate of shared training effects.

The signed gap is observed error minus independent expectation. Positive means that the product model understates error. Save both rates, the gap, integer counts, panel members, class sizes, and individual error rates for all 154 cells. Also save each five-model error-pattern frequency, including zero-count patterns.

## Comparisons and controls

Compare with the mean single-member error and the lowest single-member error in the same class cell. The lowest value is a retrospective comparator, not a deployable model selection rule. Do not select a preferred panel using these test labels. Summaries give cells equal weight and must be labelled as such. They are not deployment averages.

Check the independent calculation against exact rational enumeration in a separate validator. For a one-model control, expected and observed error must match. For an all-correct or all-wrong control, majority error must be zero or one. For identical voters with error 0.2, actual majority error is 0.2, while the product model need not equal it. A complete synthetic product distribution must reproduce the expected majority rate exactly. These are algorithm controls, not observations of AI behaviour.

## Uncertainty

For the 14 full-panel cells, use 2,000 paired item-bootstrap draws with seed 20261012. A bootstrap draw samples items with replacement within the set and class. Equivalent multinomial draws over the 32 observed five-model error patterns preserve all joint votes. Recompute all five marginal rates and the observed and independent majority rates in each draw. Save draw-level counts and rates. Report the 2.5th and 97.5th percentiles of the paired gap using NumPy's linear rule.

These are conditional resampling ranges, not validated population confidence intervals. They omit reference-label errors, unknown item clusters, new prompts, and model changes. At sample endpoints the bootstrap cannot invent unseen patterns. Do not use a significance claim or population prevalence estimate. Do not bootstrap triples or rank panels by the intervals.

## Checks and rights

Preserve source attribution and CC BY 4.0 terms for derived labels. Do not include source prompt or response text. Save input hashes, versions, commands, logs, raw results, and source search notes. Run the documented procedure and obtain independent agent review. Use relevant NeurIPS checklist parts as a review aid. Inspect source links, claim support, text originality, rights, secrets, and relative links. No human or external peer review is assumed. No paid compute or new API inference is permitted.

## Changes

No analysis amendments at plan creation. Record any later change here before dependent computations where possible.
