# Independent method and result check

Date: 2026-10-12 (America/Toronto).

Review status: PASS for the method and numeric files checked here. This is an AI agent check. No human review or external peer review occurred. This check does not review the final report, source search, or publication package.

## Method review

The plan defines the question, comparisons, threshold, input checks, and resampling rule before the analysis. The planned calculations answer a descriptive question about the saved records. No method error that prevents this study was found.

Keep these limits in the report:

- The product model uses error rates fitted on the same class cell. Its comparison with measured error is not a test of forecasts on new items.
- A gap can include shared item difficulty. It does not identify a cause such as shared training data.
- The 154 comparisons overlap. The triples are sensitivity checks, not independent replications.
- The supplied reference labels can contain errors. They are not direct measures of harm during use.
- The bootstrap holds the observed patterns fixed. It cannot add patterns that the sample did not contain. Its ranges can be zero at an endpoint.
- The lowest individual error uses the test labels. It is a comparison made after the data were collected, not a model selection rule for use on new data.

## Independent implementation

The reviewer wrote `validate.py` without importing `analyze.py`. It aligns the raw rows by dataset and item ID and checks all five model votes and their common reference label. It uses exact fractions to enumerate the product probabilities for all 154 point cells. The primary analysis uses polynomial convolution instead.

For each of the 28,000 bootstrap rows, the validator checks the 32 integer pattern counts, sample size, random seed, draw order, observed error, all recomputed marginal rates used in the product sum, and gap. It implements the linear percentile rule with sorted values. It checks all 14 saved ranges. It also checks eight saved primary algorithm controls and separate controls in the validator.

The checks passed for 6,990 decisions, 1,398 aligned items, 154 point cells, 448 pattern rows, 28,000 bootstrap rows, 14 ranges, and eight primary controls. The run completed 546,783 individual checks. `validation_results.json` contains the result and version record.

## Execution record

The first attempt used the system `python3`. It stopped at the import step with `ModuleNotFoundError: No module named 'numpy'`. It did not test or change the numeric files. This was a local environment failure.

The second attempt used the bundled Python runtime. It passed with Python 3.12.14 and NumPy 2.3.5. The command was equivalent to the following command from this study folder:

```text
python validate.py
```

The process exit status was 0. The numeric files were not changed by the validator. The validator wrote `validation_results.json`.
