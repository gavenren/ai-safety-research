# Safe retry timing for computer-use agents

This is a separate user-requested paper dated October 15, 2026. It is not a second daily automation study.

Read [report.md](report.md) or [paper.pdf](paper.pdf). The paper includes a finite synthetic benchmark, an 18-trial local browser pilot, a 60-trial experiment on two live public test sites, a later 30-trial experiment in one authenticated Google Drive account, a 32-trial two-tab extension in that account, a 48-trial extension on two additional public table websites, a 24-trial extension in production Notion and Google Calendar accounts, a 24-trial test of revised rules in those accounts, and a new 20-trial test of saved-field correction. The experiments test instructed retry rules with real browser actions. Storage and audit guarantees differ across the studies. The paper applies known retry and idempotency principles. It does not claim a new protocol or a general improvement in AI agent performance.

Codex generated this work. Separate agents checked the design, sources, calculations, reproduction, and PDF. No human or external peer review occurred. No new reuse license is assigned.

## Analyze the saved-field correction evidence

The latest extension has 20 assigned cases in production Google Calendar and Notion accounts. It defines field equality before the run, then tests wrong saved values and one correction on the same native record. Earlier results remain unchanged.

Use a separate copy of this folder. Python standard library is sufficient. These commands use saved files only. They make no browser, model, connector, or network call.

```sh
python3 -m unittest fieldcheck_tests -v
python3 field_analyzer_tests.py
python3 -m unittest field_independent_tests -v
python3 field_analyze.py --input-dir . --output-dir . > field_analysis_log.txt
python3 field_independent_replay.py --input-dir . --output field_independent_replay.json
```

The [plan](field_plan.md), [assignments](field_assignments.csv), [instructions](field_runner_instructions.md), [field contract](field_contract.md), and [freeze manifest](field_plan_manifest.json) define the test. The checker returns MATCH, MISMATCH, or UNKNOWN. It does not drive the browser. Real agents execute the UI actions and save observations. Calendar calls the frozen checker before the next decision. Notion records the agent’s field judgments; its helper does not enforce the gates. The main and independent analyzers later check the actual Notion values and decision order. The [analysis method](field_analysis_method.md) states how the archived sources become outcomes. Use all 20 assignments for release analysis; the optional subset argument is for development only.

The two runner record bundles contain JSON members keyed by their original filenames, including every trial packet and Calendar connector reply. The task-region action logs retain source references, exact synthetic field values, timestamps, errors, and live decisions. Private identities have stable aliases. [field_evidence_manifest.json](field_evidence_manifest.json) links the public extracts to private source hashes. The [change record](field_changes.md) includes failed injections, source-reference errors, and adapter changes. A record count is a distinct native identity count. A multi-day Calendar event can have more than one visible search row.

The baseline checks title and count offline on the same initial observations. It does not execute another policy or create another record. Its false matches are classification errors, not live false completion claims. The current results do not rescore any earlier strict Calendar UNKNOWN result. [field_adapters.zip](field_adapters.zip) preserves final and retained earlier helper code, with private paths and IDs replaced. [The adapter manifest](field_adapter_manifest.json) states the source hashes and limits. The helpers need the documented browser environment and a new authorized setup; they are not an unattended runner.

For a new live run, use authorized accounts, a new private test database, new unique tokens, and safe past Calendar dates. Recheck the UI and connector representations in a separate preflight. Freeze the new plan and equality contract before scored actions. Reserve one Create before its first possible effect. Never reset that budget after an empty result, timeout, or failed navigation. Permit at most one full-value correction of the assigned field on the first native ID. Missing evidence permits reads or an unresolved stop. It does not permit another Create. Require fresh saved-field and covered-view reads after the last mutation, then a separate audit after the decision. Retain every assigned failure. Move only known test records to recoverable Trash and verify zero active records. Do not send invitations, change access, edit user records, or empty Trash.

Saved evidence can reproduce these counts. A new live run can differ because the services, account state, browser extensions, model inference, and timing can change. No population error rate, general model improvement, or exactly-once service guarantee follows from these selected cases. The [review](field_review.md), [reproduction check](field_reproduction_check.json), and [image review](field_image_review.json) state the completed checks and limits.

## Analyze the revised rule evidence

Use a separate copy of this folder. Python standard library is sufficient. These commands use saved files only. They make no browser, model, connector, or network call.

```sh
python3 v2_policy_tests.py
python3 v2_analyzer_tests.py
python3 v2_analyze.py --input-dir . --output-dir . > v2_analysis_log.txt
python3 v2_independent_replay.py --input-dir . --output v2_independent_replay.json
```

The [saved plan](v2_plan.md), [assignments](v2_assignments.csv), [runner instructions](v2_runner_instructions.md), and [freeze manifest](v2_plan_manifest.json) define the 24 new assignments. The reference function in [v2_policy.py](v2_policy.py) accepts validated facts and returns the next permitted action. It is not an automatic browser driver. Live mutation logs reserve the action before the call; offline replay checks the supplied policy decisions after the run.

The analyzer uses the saved task-region observations, mutation records, native identities, and post-decision audits. It separates exact-title counts from all operation records. It keeps field uncertainty, unsupported evidence references, loading states, and action errors. The raw connector reply files are part of the package. Calendar's literal description string and its visible marker are separate checks. A whitespace-normalized field result is exploratory because that normalization was not specified before the run.

Read [v2_changes.md](v2_changes.md) for preflight failures and the online interpretation of a nonmodal Notion prompt. No saved decision is changed by a later audit. The public logs use stable aliases for native identities and remove unrelated account content. Original private files remain local; [v2_evidence_manifest.json](v2_evidence_manifest.json) records their hashes and the public extraction.

For a new live run, use authorized accounts, a new private Notion database, new unique operation tokens, and safe past Calendar dates. Recheck all procedures before a new plan freeze. The Cancel scenario ends before any effective Notion New or Calendar Save; it is not a failed submitted write. Guard reserves one Create and at most one title repair to the same ID. Never reset the Create budget after a timeout or empty result. Reload the native detail and a covered result after the last mutation. Keep unknown facts unknown. Audit before cleanup, then use recoverable Trash and verify zero active records. Do not use existing user records, send invitations, change access, or empty Trash.

The [independent review](v2_review.md), [reproduction result](v2_reproduction_check.json), and [image review](v2_image_review.json) state the completed checks. The archive has 76 public images; three original images with account details remain private with their hashes recorded. Six tiled captures remain as image limits. Runner summaries describe execution; the analysis derives counts from raw task observations and service replies.

Saved evidence permits offline result reproduction. It cannot reproduce an identical live trajectory. Account state, web interfaces, browser extensions, model inference, and tool timing can change. No general reliability rate or exactly-once service guarantee follows from these selected tests.

## Analyze the saved production account evidence

Use a separate copy of this folder. Python standard library is sufficient. These commands make no browser, model, connector, or network calls.

```sh
python3 production_analyzer_tests.py
python3 production_analyze.py --input-dir . --output-dir .
python3 production_independent_replay.py
```

The main command reads all 24 assignments, the frozen plan, and task-region action logs. It derives ready row counts, actual view scope, request and decision times, distinct audit identities, partial records, field checks, rule paths, and cleanup. Its five outputs are production_trials.csv, production_groups.csv, production_summary.json, production_analysis_checks.json, and production_analysis_log.txt. The separate replay is an independent agent's implementation. See [production_analysis_method.md](production_analysis_method.md), [production_review.md](production_review.md), and [production_reproduction_check.json](production_reproduction_check.json).

Read [production_plan.md](production_plan.md), [production_runner_instructions.md](production_runner_instructions.md), and [production_assignments.csv](production_assignments.csv) before a new run. Use an authorized private Notion test database and nonrecurring events with new unique titles in an authorized Calendar account. Never use existing user records as test data. Record full task state before each action and after each read. Start the clock at Notion New or Calendar Save. A complete empty view is different from a loading view. Preserve failed controls, changed views, partial records, missed timing gates, and procedure departures. Do not replace trials.

The 180-second deadline and one-retry limit apply to this extension only. Calendar All search covers the selected task month; it is not all-time coverage. Both rules that retry use observer rows and exclude writer receipts by instruction. This is a test of supplied procedures on selected production services. It does not measure natural service error rates or unrestricted agent behavior. Strict clean completion requires correct task fields, not just one matching title. Calendar's editor and later reads differ by one hour; this remains unresolved.

The public logs omit private account content and use stable aliases for record identities. The originals remain local. [production_evidence_manifest.json](production_evidence_manifest.json) records extraction rules and hashes. The image archive retains original task-region crop bytes. Notion has browser reload and native page-link audits; its connector was unavailable. Calendar also has a bounded read-only service audit after each decision. Neither finite audit proves indefinite persistence. Move only test records to recoverable Trash after the audit and verify cleanup. Do not empty Trash. Live timing and outcomes can differ on a new run.

## Analyze the saved additional website evidence

Use a separate copy of this folder. Python standard library is sufficient. This procedure makes no browser, model, connector, or network call.

```sh
python3 cross_analyze.py --input-dir . --output-dir .
python3 cross_independent_replay.py
```

The command reads cross_assignments.csv, frozen plan hashes, and both cross_runner action logs. It reconstructs exact task rows, search views, ready states, action times, rule paths, final counts, and cleanup. It writes cross_trials.csv, cross_groups.csv, cross_summary.json, cross_analysis_checks.json, and cross_analysis_log.txt. The saved raw input hashes permit a byte check. Parser checks and a repeated derivation are author checks. The second command uses the separate reviewer's implementation. See cross_review.md and cross_reproduction_check.json for the saved checks.

Read [cross_plan.md](cross_plan.md), [cross_runner_instructions.md](cross_runner_instructions.md), and [cross_assignments.csv](cross_assignments.csv) before a new browser run. Use the actual DemoQA Web Tables and DataTables Add rows pages, one browser tab and separate model context per site. Verify the default baseline. A native search value hides the new rows. Do not reload until the decision and full-table audit are saved: reload erases these examples' temporary rows. Keep failed trials and all decision/audit/cleanup evidence. Repeated DataTables actions create different generated rows, so the shared measure is an extra effect, not an identical-data duplicate.

The sites were selected after feasibility checks. They are public demonstrations, not additional production account services. The fixed rules deliberately exclude other visible evidence, including DataTables footer totals. Receipt is unavailable. New live runs can differ as the sites, model, and tool timing change. The evidence is descriptive and does not establish natural error rates or server durability. See [cross_source_search.md](cross_source_search.md), [cross_preflight.md](cross_preflight.md), and [cross_evidence.md](cross_evidence.md) for selection, failed checks, extraction, attribution, and image limits.

## Analyze the saved two-tab evidence

Use a separate copy of this folder. The analysis uses Python standard library and saved evidence. It makes no browser, model, or connector call.

```sh
python3 trigger_analyze.py --input-dir . --output-dir .
python3 trigger_validate.py --input-dir . --fresh-copy
python3 trigger_independent_replay.py --input-dir .
```

Read [trigger_plan.md](trigger_plan.md), [trigger_runner_instructions.md](trigger_runner_instructions.md), and [trigger_assignments.csv](trigger_assignments.csv) before a new run. Use a new private collection and new test names. Two independent tabs must refer to the same test block. The observer reload is part of the procedure. Do not treat loading as zero or reapply a filter to force an outcome after a write. Keep every assigned trial. The later connector audit must occur after all decisions stop.

The two-tab workflow was selected for stable filtered absence. The core rules ignore writer receipts by instruction; Receipt can use them. This is a controlled comparison of supplied procedures. It is not a natural error rate, new retry protocol, or test of uncertain network execution. Service changes and model/tool timing can change a new run. Offline analysis can reproduce the saved counts without private account access.

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

This command reads report.md and its figures. It writes paper.pdf and checks text coverage. The PDF has fixed metadata. Standalone font files are not included. The PDF embeds font subsets. See [FONT_LICENSE.txt](FONT_LICENSE.txt) for their license notices and [pdf_check.json](pdf_check.json) for the saved build checks. Visual review is a separate step; do not assume that a successful build proves a sound page layout.

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

The account extension preserves all simulation, local-pilot, and public-demo evidence. public_site_final_review.md, public_site_checklist.md, public_site_release_checks.json, public_site_pdf_check.json, and live_review.md describe the preceding 60-trial version. Their old report and PDF hashes are historical. account_review.md and account_validation.json describe that 30-trial evidence. The historical account_version files preserve the release checks for that version.

The two-tab extension preserves the earlier 30-trial evidence. account_version_final_review.md, account_version_checklist.md, account_version_release_checks.json, account_version_pdf_check.json, and account_review.md describe the previous paper. Their report/PDF hashes are historical. The trigger files describe the new 32-trial extension. Current final_review.md, release_checks.json, pdf_check.json, and package_manifest.json apply to the latest release.

The additional website extension preserves all earlier evidence. trigger_version_final_review.md, trigger_version_checklist.md, trigger_version_release_checks.json, and trigger_version_pdf_check.json preserve the preceding two-tab release. Their hashes are historical. The cross files describe the new 48-trial extension. Current final_review.md, release_checks.json, pdf_check.json, and package_manifest.json apply to the latest release.

The production account extension preserves all prior experimental evidence. cross_version_final_review.md, cross_version_checklist.md, cross_version_release_checks.json, and cross_version_pdf_check.json preserve the preceding 48-trial release. Their document hashes are historical. The production files describe the new 24-trial extension. Current final_review.md, release_checks.json, pdf_check.json, and package_manifest.json apply to this release.

The saved-field extension preserves all earlier experimental evidence. The v2_version files preserve the preceding rule-revision release checks and package manifest. Their report and PDF hashes are historical. The field files describe the new 20-trial extension. Current final_review.md, release_checks.json, pdf_check.json, and package_manifest.json apply to this release.
