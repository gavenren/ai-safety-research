# Independent method review

Date: 2026-10-13.

Status: PASS for the method and saved numeric results reviewed here. This is a separate Codex agent review. It is not human review or external peer review. It does not prove that the source labels are correct.

## Scope and method

The reviewer read the saved analysis plan before the routing outputs were available. The reviewer checked the fixed input directly. The input has 6,990 distinct model-item rows and 1,398 aligned items. Each item has the same five models, one shared reference label, and five binary votes. The SHA256 agrees with the fixed input in the plan.

The reviewer wrote `validate.py` separately. It does not import `analyze.py`. It reads the original votes again. It finds the majority from the middle sorted vote and counts the votes that match that majority. It then makes every count and rate again.

The probability check uses exact rational numbers through Python's `Fraction` class. For adjacent accepted-error counts, its relative mass recurrence is:

`w(x+1) / w(x) = ((E-x)*(A-x)) / ((x+1)*(N-E-A+x+1))`.

Here `N` is the number of items, `E` is the number of majority errors, and `A` is the number of accepted items. The check starts at the smallest possible count, then divides all masses by their sum. It does not use the combination formula in the analysis. Direct enumeration of all subsets checks this recurrence for every error count and accepted count with `N` from 1 through 8.

The quantile convention is the first integer whose cumulative probability reaches the required probability. The check verifies both sides of each 2.5% and 97.5% boundary.

## Executed checks

Command from the study folder:

```sh
python3 validate.py
```

The command finished with exit code 0. It reported 53,852 successful assertions. The count is a record of software checks, not a measure of research quality.

The checks cover:

- All 1,398 item summaries and all three routing decisions for each item.
- All 63 group rows, six item counts per row, rates, and zero-denominator fields.
- All 944 saved exact probability fractions, their full support, total probability, mean, and quantiles.
- All 378 review scenarios and their outcome labels.
- All summary counts and equal-set descriptive means.
- Count conservation, nested acceptance, class sums, and full acceptance at threshold 3.
- All saved controls, including no acceptance, no deferral, all-correct decisions, and all-wrong decisions.
- All 32 five-vote patterns for both reference labels.
- 284 small finite distributions checked by direct subset enumeration.
- The fixed data hash and the plan hash in the input manifest.

No numeric mismatch was found. No analysis correction was needed after this validation run.

## Review identity

Let `EA` be accepted errors, `ED` be deferred errors, `D` be deferred items, and `h` be the reviewer's error rate on those exact deferred items. The saved data give `E = EA + ED`. Review replaces the panel decision. The change from the original total error rate is therefore:

`(EA + h*D)/N - E/N = (h*D - ED)/N`.

For `D > 0`, this change is negative exactly when `h < ED/D`. Equality gives no change. For `D = 0`, review has no effect. The validator checks these statements with exact fractions for all saved scenarios.

The equal-workload random-routing calculation is correct under its stated extra assumption: the reviewer has the same error rate `h` on the random deferred subset. The records do not test that assumption.

## Interpretation checks and limits

The method supports fixed-data descriptions. It does not support a population safety claim, a significance claim, a claim about future model versions, or measured reviewer performance. The random-routing ranges describe a selection procedure on these fixed records. They are not population confidence intervals.

The directional set-level hypothesis is supported on these seven saved sets. Both restricted thresholds have lower accepted-item error than the full-acceptance baseline in every set. The class-level results are mixed. At threshold 5, five of 14 reference-class rows have higher accepted-item error. These are Aegis class 0, BeaverTails class 1, ETHICS class 0, ToxicChat class 0, and XSTest class 0. The report must keep this result visible. A lower whole-set error rate does not show improvement for each reference class.

No threshold was fitted to these results. However, previous studies of these labels were already known. The plan correctly states this fact. The study must keep the scope of its contribution narrow. Review routing and risk-coverage analysis are established methods.

This review covers the method and numeric files. It does not replace the final report review, source review, license check, or publication verification.
