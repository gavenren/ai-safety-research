# Safe retry timing for computer-use agents

This is a separate user-requested paper dated October 15, 2026. It is not a second daily automation study.

Read [report.md](report.md) or [paper.pdf](paper.pdf). The paper includes a finite synthetic benchmark, an 18-trial local browser pilot, a 60-trial experiment on two live public test sites, and a later 30-trial experiment in one authenticated Google Drive account. The experiments test instructed retry rules with real browser actions. Storage and audit guarantees differ across the studies. The paper applies known retry and idempotency principles. It does not claim a new protocol or a general improvement in AI agent performance.

Codex generated this work. Separate agents checked the design, sources, calculations, reproduction, and PDF. No human or external peer review occurred. No new reuse license is assigned.

## Analyze the saved account evidence

Use a separate copy of this folder. The commands use Python standard library and saved, redacted evidence. They make no browser or connector call.

```sh
python3 account_analyze.py
python3 account_validate.py --fresh-copy
```

Read account_plan.md before any new browser run. Use a new private test collection and new token names. Never use existing user records as tests. Use account_assignments.csv for the design. The later connector audit must list every test record only after all decisions stop. A new trajectory can differ. The saved data permit an offline check without private account access.

Read account_redaction.md for removed private fields and public ID pseudonyms. The original private logs are not in this public repository. The four published block images show later audits, not the original trial decisions. Three original trial images are missing. Screenshots show only the test region. The audit is a finite service read; it is not a durability guarantee. Cleanup means moving only the test parent to Trash, not emptying Trash or permanent deletion.

## Analyze the saved live-site evidence

Use a separate copy of this folder. The analyzer uses Python's standard library and does not make model or browser calls.

```sh
python3 live_analyze.py --input-dir . --output-dir live-output
python3 live_validate.py --fresh-copy
```

It reads all 60 assignments and the two runner logs. It writes a full trial table, grouped counts, matched comparisons, and analysis checks. See live_summary.json and live_review.md for the saved result and independent review. A final count means a task was retained in this browser at the reload audit. It does not mean server durability.

To repeat the browser test, read live_plan.md and live_runner_instructions.md. Use the same two hosted implementations and a new unique token prefix. Use one browser tab and model context per origin. Keep each model decision outside any scripted loop. Save the full observations, action times, decisions, errors, and screenshots. Do not replace failures. The live apps, service timing, and exact model version can change, so a new run need not reproduce the same trajectories. The saved action evidence permits analysis without a new run.

The fixed procedures use All and Completed views. Only Scope changes to All before its decision. Thus this is a comparison of supplied procedures, not a free-choice agent benchmark. Two related public test apps do not establish production safety. The live plan was amended after failed feasibility checks and before scored actions. Both plan versions and the failures remain in the package. No external preregistration is claimed.

## Analyze the saved browser evidence

Use a separate copy of this folder. Python standard library is sufficient.

```sh
python3 browser_analyze.py --input-dir . --output-dir .
python3 browser_validate.py --input-dir . --output-dir validation-output
```

This command reads the frozen audit and SQLite database. It checks their agreement, scores all 18 assigned trials, and writes browser_results.csv, browser_summary.json, browser_pairs.csv, and browser_analysis_log.txt. It does not make model calls. The second command independently rebuilds all trial fields and timing pairs from the stored events. It checks the action logs and runs the analyzer in a temporary folder. It writes browser_validation_results.json in validation-output. The saved package includes the reviewer's result for comparison. See browser_review.md for the separate text and image review. The saved trajectories cannot be repeated byte for byte because model and tool timing can change.

## Repeat the browser task

Read browser_plan.md and browser_runner_prompt.md first. Check the app in a separate temporary test database:

```sh
python3 browser_app_checks.py
python3 browser_app.py --config browser_config.json --data-dir new-browser-data --port 8769
```

Use a new data directory. The app rejects an existing event database. Start two separate agent contexts. Give each the saved prompt and its assigned URL: http://127.0.0.1:8769/runner/A or http://127.0.0.1:8769/runner/B. Each runner must use the supported browser interface, one model decision per action, and its own action log. Do not give the runner the source, configuration, or audit. The app uses real timers and durable append rows. It does not enforce the policy-specific retry guard.

After all trials stop, wait for every admitted timer to resolve. A separate observer can retrieve http://127.0.0.1:8769/audit and check unresolved_attempts is zero. Save that response as browser_audit.json. Back up the database with SQLite's backup API as browser_state.sqlite. Save events.jsonl, both runner logs, and completion screenshots. Preserve unstarted or interrupted trials if the 12-minute admission budget expires. Never replace a failed trial. Run browser_analyze.py on this new evidence. Its output can differ from the saved pilot. No API spending is required by the analysis or app. A fresh agent experiment uses the chosen agent service.

The server used Python 3.14.7. App checks used Python 3.13.7. Browser and available agent identity are recorded in browser_environment.json. The plan, app, evidence, and validation hashes are saved in the browser manifest files. browser_screenshots.zip contains the stopped-trial and runner-completion screenshots. The 20 saved files have .png names, but the browser tool returned JPEG bytes. The archive preserves the original evidence names and bytes. Use a viewer that detects the image format from its bytes. browser_runner_A_actions.jsonl and browser_runner_B_actions.jsonl contain the real browser action records. The warm-up W01 remains in raw evidence but is excluded from every scored count.

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

## Version history and limits

The first published version was a synthetic study. Its numerical evidence remains unchanged. simulation_final_review.md, simulation_release_checks.json, simulation_pdf_check.json, and reproduction_check.json refer to that version. Their old report or PDF hashes are historical records. The current final_review.md describes the latest extension; each historical review states its own scope. package_manifest.json lists current package hashes.

The pilot tests a real agent in a constructed local browser application. It is not a public-web or pixel-only benchmark. Two contexts share one host and browser service. The rules are supplied by prompt, so these are not natural error rates. Truthful terminal status is a constructed app capability. The finite case counts are not field error rates. Synthetic and browser results must remain separate.

The live-site extension keeps all original simulation and local browser data unchanged. local_browser_final_review.md, local_browser_release_checks.json, local_browser_pdf_check.json, browser_review.md, and browser_reproduction_check.json refer to the earlier 18-trial paper. Their report/PDF/index hashes are historical. live_review.md and live_validation.json apply to the 60-trial evidence. The current release_checks.json, pdf_check.json, and package_manifest.json apply to the latest account extension.

The account extension preserves all simulation, local-pilot, and public-demo evidence. public_site_final_review.md, public_site_checklist.md, public_site_release_checks.json, public_site_pdf_check.json, and live_review.md describe the preceding 60-trial version. Their old report and PDF hashes are historical. account_review.md, account_validation.json, final_review.md, release_checks.json, pdf_check.json, and package_manifest.json describe the current version.
