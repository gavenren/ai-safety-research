# Repeat the majority-vote audit

This folder contains a secondary audit of fixed Safety-Flag decisions. It has no model weights and makes no model API calls. Read [report.md](report.md) for the result and limits.

## Reproduce the numerical results

The recorded numerical environment is Python 3.12.14 and NumPy 2.3.5. From this folder:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analyze.py > run_log.txt
.venv/bin/python validate.py > validation_log.txt
```

The script uses only the included `data_labels.csv`. The seed is 20261012. It produces 154 point cells, 448 pattern rows, 28,000 bootstrap rows, 14 percentile ranges, and eight controls. A full analysis took about one second on the local CPU. The validator takes a few seconds. No GPU or paid compute was used. Run times depend on the machine. Package installation needs network access; the analysis does not.

## Reproduce the figure

The recorded plotting environment is Python 3.13.7, NumPy 2.5.3, and Matplotlib 3.10.7. This separate environment was already available on the local machine.

```sh
python3.13 -m venv .venv-plot
.venv-plot/bin/python -m pip install -r requirements-plot.txt
.venv-plot/bin/python plot.py > plot_log.txt
```

The figure reads saved result tables. It does not change them. Different fonts or plotting-library builds can change image bytes without changing values.

## Input and rights

The input is unchanged from the [October 10 release](https://github.com/gavenren/ai-safety-research/blob/a713543cfaa4188d6675826fc12ca3f9f2da582a/research/2026-10-10-judge-transfer/data_labels.csv). Its SHA-256 is `a8c004743230361498dc7eaca9ee9900bbc3a4a7f0dfba113b0052668325be7e`. That study's fetch script and source manifest give the original retrieval route. The upstream fixed commit is `82d39d018c5522dfbdf303b49c5d83a8444d03d2`.

Each input row has a test-set name, item ID, model alias, binary reference label, and binary decision. An item key is the pair of test-set name and item ID. Five models vote on each key. The input contains 1,398 keys and 6,990 decisions. A reference label of one means that the source policy calls for a flag. Policies differ across sets.

See [DATA_LICENSE.md](DATA_LICENSE.md) for CC BY 4.0 attribution. No source content, prompt, or response text is included. No new license is assigned to the owner's work.

## Saved output definitions

- `results_cells.csv`: each panel, set, and class; counts, observed rate, product rate, signed gap, and retrospective single-member comparisons.
- `results_patterns.csv`: all 32 error patterns for each set and class. Bits follow the alphabetical model order in `results_summary.json`.
- `results_bootstrap.csv`: all resampled 32-pattern count vectors and paired rates. Draw numbers start at zero. Groups use alphabetical set order, then class zero and class one.
- `results_intervals.csv`: pointwise 2.5th and 97.5th percentiles of full-panel gaps. These are conditional resampling ranges.
- `results_controls.json`: synthetic and single-model calculation checks.
- `validation_results.json`: independent checks of inputs, counts, exact point probabilities, all saved draws, and percentile calculations.

`validate.py` uses exact fractions for point calculations and direct event sums for bootstrap calculations. It does not import `analyze.py`. The main script uses polynomial multiplication. Regenerating files overwrites their local copies. Keep an original copy if a byte comparison is needed. The package manifest excludes itself. Run-time fields in the log can differ between runs.

Codex generated this study and code. Separate agents checked methods, sources, and results. No human or external peer review occurred.
