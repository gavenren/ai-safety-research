# Repeat this study

This folder contains an exact mathematical study of zero observed failures. No AI model, private data, or external API is needed to repeat the calculation.

## Requirements

The calculations and validation use Python 3.13.7 and its standard library. Other Python versions were not tested. The optional figure uses Matplotlib 3.10.7. Exact plot dependency versions are in requirements-plot.txt. No learned-model checkpoint is used. The model inputs are the named probability distributions and the fixed grid in analysis_plan.md and analyze.py.

## Calculate and check

Open a terminal in this study folder. Run:

```sh
python3 analyze.py > run_log.txt
python3 validate.py > validation_log.txt
```

The first command writes results_grid.csv, results_boundaries.csv, and results_summary.json. The second command saves the check output in validation_log.txt. It recomputes every probability and boundary with 60-digit arithmetic. It does not import the main calculation file. The validation tolerance for the saved floating-point results is 5e-13. The log includes source and result hashes.

The validation must end with `PASS: all independent validation checks.` Do not use Python's `-O` flag: it disables assertions in the main calculation. Input settings are constants; no random sampling or seed is used. No files are downloaded for the analysis.

## Optional figure

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-plot.txt
.venv/bin/python plot.py
```

This writes figure_zero_failures.png from the saved grid. Package installation is needed only for the figure. The chart's exact pixels can change with fonts or platform. Numerical outputs are checked separately.

## Evidence and review

- report.md: question, method, results, and limits.
- analysis_plan.md: plan saved before calculation.
- derivations.md: moment and probability calculations, proofs, and limits.
- results_grid.csv: all 252 model probabilities and comparison values.
- results_boundaries.csv: all 84 model-specific boundaries.
- results_summary.json: controls and headline calculations.
- run_log.txt and validation_log.txt: actual completed run outputs.
- source_search.md and references.bib: source search and references.
- review.md: checks, a corrected numerical issue, and review status.
- manifest.json: SHA-256 file hashes, excluding this manifest itself.

## Rights and AI use

The repository has no general reuse license. No new license is assigned. This folder contains original text, code, and synthetic calculations prepared with Codex. It does not redistribute source paper text, datasets, or code. Referenced works retain their own rights. Codex generated the report and code. Separate Codex agents checked the work. No human or external peer review occurred. The exact Codex serving-model version was not exposed to this run and is not invented here.
