# Repeat this study

This folder contains the October 14, 2026 mathematical audit of repeated clean-window tests. No AI model was tested. All inputs are synthetic design values in [config.json](config.json). No external data download is needed.

## Commands

Use CPython 3.13.7. The analysis and validator use only the standard library. From this folder run:

```sh
python3 analyze.py > run_log.txt
python3 validate.py > validation_log.txt
```

The first command writes three result CSV files, the summary, and the environment record. The second checks the results with separate calculations. The fixed plan and configuration must match [input_manifest.json](input_manifest.json).

For the optional figure, use Python 3.13.7 with Matplotlib 3.10.7 and NumPy 2.5.3:

```sh
python3 plot.py > plot_log.txt
```

The original run used separate installed environments for core calculations and plotting. It used local CPU computation. It made no paid call and ran no model inference. No random sampling or random seed is used.

## Files and scope

Read [report.md](report.md) for the interpretation and limits. [derivations.md](derivations.md) gives the probability arguments. [analysis_plan.md](analysis_plan.md) records the question and criteria before calculation. [source_search.md](source_search.md) records sources and read scope.

[results_grid.csv](results_grid.csv) has 36 conditions. [results_calibration.csv](results_calibration.csv) has 12 minimum-length designs. [results_trajectory.csv](results_trajectory.csv) has 5,982 time rows for the planned 1% example. Probabilities use 30 decimal places; displayed report percentages are rounded. These are model probabilities, not empirical rates or confidence intervals.

Separate checks are in [method_review.md](method_review.md), [validation_results.json](validation_results.json), and [final_review.md](final_review.md). [review.md](review.md) records the publication checklist.

Codex generated the work. No human or external peer review occurred. No third-party dataset, paper text, or code is redistributed. No new license is assigned to the owner's work.
