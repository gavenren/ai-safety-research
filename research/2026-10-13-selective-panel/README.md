# Reproduce the agreement-routing study

Date: 2026-10-13. Codex generated this work. No human review occurred.

Read [report.md](report.md) for the question, results, and limits. The study uses saved labels. It makes no new model calls and measures no reviewer performance.

## Core calculation

The recorded core environment is CPython 3.13.7 on macOS arm64. The analysis and validator use only the Python standard library. Run these commands from this folder:

```sh
python3 analyze.py > run_log.txt
python3 validate.py > validation_results.json
```

The first command checks the input and plan hashes, then writes all result tables, summary, controls, and environment metadata. The second independently reconstructs the results and prints its check record. It does not import `analyze.py`. A failed assertion gives a nonzero exit code. No package install or random seed is needed for these commands.

## Optional figure

The recorded plot environment uses Python 3.13.7, Matplotlib 3.10.7, and NumPy 2.5.3. To reproduce it in a separate environment:

```sh
python3 -m venv .venv-plot
.venv-plot/bin/python -m pip install -r requirements-plot.txt
.venv-plot/bin/python plot.py > plot_log.txt
```

The figure uses saved result rows. It does not recalculate votes. Exact PNG bytes can vary with fonts, backend, or platform. Numerical outputs should match the recorded versions. The completed final check used a separate copy on the same local machine.

## Files and units

| File | Contents |
| --- | --- |
| analysis_plan.md | Question, rules, measures, baselines, and checks saved before calculation |
| input_manifest.json | Input and plan SHA256 hashes; fixed source versions |
| data_labels.csv | 6,990 source decisions; dataset + item ID + model is the key |
| results_items.csv | 1,398 aligned items, majority label, agreement, error, and three acceptance flags |
| results_groups.csv | 63 set or class rows; rates are fractions from 0 to 1 |
| results_random_distribution.csv | 944 exact probability rows; numerator divided by denominator |
| results_review_scenarios.csv | 378 conditional review scenarios; rates are fractions |
| results_summary.json | Equal-set summaries; do not read them as traffic rates |
| results_controls.json | Synthetic boundary controls, not new AI observations |
| validation_results.json | Independent calculation checks |
| environment.json, plot_environment.json | Actual program versions |
| source_search.md, references.bib | Search record, read scope, and references |
| review.md, method_review.md, final_review.md | Review aid and separate agent checks |
| failed_checks.md | Actual failure and repair record |

The reference value `all` combines both labels inside one test set. Values `0` and `1` are the two reference classes. A blank rate is undefined because its denominator is zero. It is not zero error. Source alias `toxicchat` is displayed as ToxiChat; `gemma-2-9b` is the saved Gemma alias. Decimal rates have twelve places. Exact input counts and probability fractions remain available.

## Source retrieval and rights

The included input is unchanged from this project's [fixed October 12 release](https://github.com/gavenren/ai-safety-research/blob/5da968d9c12edc82e1f0030d7e61f91233c509cd/research/2026-10-12-judge-ensemble/data_labels.csv). Its SHA256 is `a8c004743230361498dc7eaca9ee9900bbc3a4a7f0dfba113b0052668325be7e`.

The original extraction and retrieval procedure is preserved in the [October 10 release](https://github.com/gavenren/ai-safety-research/tree/5da968d9c12edc82e1f0030d7e61f91233c509cd/research/2026-10-10-judge-transfer). The upstream source is [Safety-Flag at a fixed commit](https://github.com/yibo-hu-lab/safety-flag-benchmark/tree/82d39d018c5522dfbdf303b49c5d83a8444d03d2). The reduced labels retain CC BY 4.0 attribution in [DATA_LICENSE.md](DATA_LICENSE.md). No source prompts or responses are included. No new license is assigned to the owner's work.

## Scope of reproduction

These commands reproduce calculations from the supplied labels. They do not regenerate the source model outputs, validate the reference labels, perform human review, or show future safety. The random-routing distribution is conditional on the fixed records. It is not a confidence interval for a deployment population.
