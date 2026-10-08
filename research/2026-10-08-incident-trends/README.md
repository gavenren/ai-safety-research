# Repeat this study

Read [the report](report.md). The study date is October 8, 2026.

## Quick reproduction

Use Python 3.13. From this folder, run:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py
```

This uses the four included data extracts. It regenerates all result tables, the summary, and three figures. No API key is required. No random sampling is used.

## Reproduce from the original archives

```sh
python fetch_sources.py
python analyze.py --source-dir .cache
```

The source download is about 198 MB. Extraction needs additional disk space. The script checks archive and extracted-file SHA-256 hashes. It saves no article text in this study folder.

## Files

- `analysis_plan.md`: plan and documented change after schema inspection.
- `source_manifest.json`: source URLs, snapshot dates, file sizes, and hashes.
- `data_*.csv`: minimal source extracts with IDs, dates, publication flags, and selected classification fields.
- `analyze.py`: calculations, integrity checks, and figure generation.
- `results_*.csv` and `results_summary.json`: numerical results.
- `figure_*.png`: figures for the report.
- `references.bib` and `source_search.md`: references and search record.
- `review.md`: checks and review limits.
- `run_log.txt`: output from the completed analysis.
- `DATA_LICENSE.md`: attribution and the source data license.

The source dates are calendar dates without a time zone. No date conversion is applied. The study date uses America/Toronto.

The counts describe database records. They do not measure all AI incidents or risk per AI use. A missing severity score is not a score of zero.
