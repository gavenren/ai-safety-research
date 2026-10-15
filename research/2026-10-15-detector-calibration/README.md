# Repeat the detector calibration study

This is an exact probability audit with synthetic inputs. No AI system or diagnostic device was tested. No external dataset is required.

Use CPython 3.14.7. From this folder run:

```sh
python3 analyze.py > run_log.txt
python3 validate.py > validation_log.txt
```

The first command uses only the standard library. It checks the saved plan and configuration hashes. It writes the bounds, policy branches, probability grid, summary, and environment record. The separate validator checks these outputs with different calculations.

For the optional figure, use CPython 3.13.7, Matplotlib 3.10.7, and NumPy 2.5.3:

```sh
python3 plot.py > plot_log.txt
```

Core and plot commands used existing local environments. No package installation, paid service, model inference experiment, or random sampling occurred. There is no random seed.

## Files

- [report.md](report.md): question, results, assumptions, and limits.
- [analysis_plan.md](analysis_plan.md), [config.json](config.json), and [input_manifest.json](input_manifest.json): design saved before calculation and its hashes.
- [derivations.md](derivations.md): binomial mixture, sample size, and error-bound arguments.
- [results_bounds.csv](results_bounds.csv): all 128 calibration outcomes, with full-precision root brackets.
- [results_policy.csv](results_policy.csv): all 1,536 calibrated policy branches and cap decisions.
- [results_grid.csv](results_grid.csv): all 1,296 conditions and workload measures.
- [results_summary.json](results_summary.json): counts and the planned example. Maximum ties use the saved 30-decimal probability precision.
- [source_search.md](source_search.md) and [references.bib](references.bib): source dates, versions, read scope, and attribution.
- [method_review.md](method_review.md), [final_review.md](final_review.md), and [review.md](review.md): checks and review status.
- [failed_checks.md](failed_checks.md): failures, repairs, and scope notes.

CSV probabilities and workload means use 30 decimal places. Empty count fields mean no finite length or no launched batch, as specified by the column. A skipped batch makes no declaration. The table does not record actual AI tests or compute use.

Codex generated the study and report. Separate agents checked the work. No human or external peer review occurred. No new license is assigned to the owner's work. Sources retain their rights; no source data, paper text, figures, or code are included.
