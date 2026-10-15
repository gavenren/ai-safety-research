# Safe retry timing for computer-use agents

This is a separate user-requested paper dated October 15, 2026. It is not a second daily automation study.

Read [report.md](report.md) or [paper.pdf](paper.pdf). The new contribution is a finite synthetic benchmark and full policy comparison. The paper applies known retry and idempotency principles. It does not claim a new protocol or a measured improvement in a real AI agent.

Codex generated this work. Separate agents checked the design, sources, calculations, reproduction, and PDF. No human or external peer review occurred. No new reuse license is assigned.

## Repeat the numerical study

Use a separate copy of this folder. The commands replace generated results in that copy. The saved numerical run used CPython 3.13.7 on Darwin. The analyzer and independent validator need only the Python standard library.

```sh
python3 analyze.py > run_log.txt
python3 validate.py --input-dir . --output-dir . > validation_log.txt
```

The first command checks the saved plan and configuration hashes before it runs. It writes 336 cases, 13,440 result rows, all event traces, grouped tables, and hypothesis checks. There is no random seed because there is no random sampling. A tick is a synthetic time unit, not a second.

The second command checks each run with an independent event-time implementation. It does not import the analyzer. It also checks the full traces, later effects, grouped tables, paired comparisons, and a local two-world proof. Read [validation_results.json](validation_results.json), [method_review.md](method_review.md), and [derivations.md](derivations.md).

Use [reproduction_check.json](reproduction_check.json) to compare the saved numerical output hashes. Environment files can differ on another operating system or Python version. These differences do not change the input cases. The saved checks use the recorded environment.

## Repeat the figure

The saved figure used Python 3.13.7, Matplotlib 3.10.7, and NumPy 2.5.3. Use the versions in [requirements-plot.txt](requirements-plot.txt).

```sh
python3 -m pip install -r requirements-plot.txt
python3 plot.py > plot_log.txt
```

The figure reads the saved summary table. It uses no model calls or external data. Font and library differences can change image bytes.

## Repeat the PDF

Use the packages in [requirements-pdf.txt](requirements-pdf.txt) and the DejaVu Serif, DejaVu Sans, and DejaVu Sans Mono font files. The saved build used Python 3.12.14. See [pdf_environment.json](pdf_environment.json) for exact versions. The build script can find a common Linux DejaVu font directory. You can also give the font directory explicitly.

```sh
python3 -m pip install -r requirements-pdf.txt
python3 build_pdf.py --font-dir /path/to/dejavu-fonts > pdf_log.txt
```

This command reads report.md and the PNG figure. It writes paper.pdf and checks text coverage. The PDF has fixed metadata. Standalone font files are not included. The PDF embeds font subsets. See [FONT_LICENSE.txt](FONT_LICENSE.txt) for their license notices and [pdf_check.json](pdf_check.json) for the saved build checks. Visual review is a separate step; do not assume that a successful build proves a sound page layout.

## Files and evidence

- [analysis_plan.md](analysis_plan.md), [config.json](config.json), and [input_manifest.json](input_manifest.json): saved plan, cases, hypotheses, and the pre-analysis change record.
- [analyze.py](analyze.py) and [validate.py](validate.py): two separate numerical implementations.
- [cases.csv](cases.csv) and [results_runs.csv](results_runs.csv): input cases and every run result.
- [traces.jsonl.gz](traces.jsonl.gz): one compressed JSON record per run, with every event and the final audit. Decompress with a gzip reader.
- [trace_examples.json](trace_examples.json): five readable traces for one zero-lag case.
- [results_summary.csv](results_summary.csv), [results_by_lag.csv](results_by_lag.csv), [results_by_outcome.csv](results_by_outcome.csv), and [results_paired.csv](results_paired.csv): all summary tables and paired comparisons.
- [source_search.md](source_search.md) and [references.bib](references.bib): exact searches, source versions, read limits, and citations.
- [failed_checks.md](failed_checks.md), [review.md](review.md), and [final_review.md](final_review.md): changes, checklist review, and independent final review.
- [release_checks.json](release_checks.json) and [package_manifest.json](package_manifest.json): release checks and package hashes. A local release check does not prove GitHub publication.

## Limits

All cases are synthetic. No browser, visual model, or AI policy was tested. Truthful terminal status and ideal server deduplication are explicit assumptions. The finite case counts are not field error rates. Main and stress suites must remain separate.
