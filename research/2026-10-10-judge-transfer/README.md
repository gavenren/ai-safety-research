# Repeat this study

Read [report.md](report.md) for the question, findings, and limits.

## Environment

The recorded run used Python 3.13.7, NumPy 2.5.3, and Matplotlib 3.10.7 on a local Darwin arm64 CPU. No GPU, model inference, API service, or paid compute is needed. Source model outputs are fixed records, not regenerated models. The model aliases and pinned input files are in `source_manifest.json`.

## Commands

Run these commands in this folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python analyze.py > run_log.txt
.venv/bin/python plot.py
.venv/bin/python validate.py > validation_log.txt
```

The analysis reads the included `data_labels.csv`. It writes the confusion counts, 175 grid cases, summary, and 70,000 bootstrap rate rows. Seed: 20261010. Bootstrap draws: 2,000. The source and target rates are resampled together. The percentile convention is NumPy's default linear interpolation.

To rebuild the minimal source data, use:

```sh
python3 fetch_data.py > retrieval_log.txt
```

This uses `curl` with HTTPS certificate checks enabled. It requests 35 pinned public JSONL files. It retains no prompt or response text. `source_manifest.json` records their hashes and the final reduced-data hash. The retrieval timestamp changes on each run; the reduced-data hash should stay the same. The original reduced-data SHA256 is `a8c004743230361498dc7eaca9ee9900bbc3a4a7f0dfba113b0052668325be7e`.

## Files

- `analysis_plan.md`: saved design and the data-quality amendment.
- `fetch_data.py`, `source_manifest.json`, `retrieval_log.txt`: retrieval and provenance.
- `data_labels.csv`, `DATA_LICENSE.md`: reduced records and attribution.
- `data_quality_audit.json`, `failed_checks.md`: data checks and repaired failures.
- `analyze.py`, `results_confusion.csv`, `results_grid.csv`, `results_summary.json`: calculations and results.
- `results_bootstrap_rates.csv`: all resampled source and target rate pairs.
- `plot.py`, `figure_transfer.png`: figure and its source.
- `validate.py`, `validation_log.txt`, `validation_results.json`, `run_log.txt`: independent arithmetic check and run evidence.
- `source_search.md`, `references.bib`, `review.md`: related work and review record.
- `release_checks.json`, `package_manifest.json`: final checks and local file hashes.

The included validator uses Python's standard library and exact fractions for point calculations. It also checks saved bootstrap percentiles. It does not validate the original model runs or the source labels.

The conditional bootstrap intervals are sensitivity ranges for these records. They are not guarantees for a new population. Do not read the controlled mixture results as deployment harm rates.
