# Receipt scope and payload binding

Read [report.md](report.md) for the result and limits. This is a synthetic finite study. No website, account, or language-model trial occurred.

## Repeat

Use Python 3.13.7, or a compatible Python 3 standard-library environment. No package installation, service, API key, or dataset download is required. Start in this study folder. Use a new output path:

```sh
python3 study.py --out /tmp/receipt-binding-repeat
python3 compare_results.py /tmp/receipt-binding-repeat
```

The runner refuses to overwrite a prior cases.jsonl. Remove no previous evidence. Choose another unused path when needed. The comparison checks every deterministic result byte against the published files. Execution timestamps, paths, and runtimes are expected to differ.

The original commands and repeat commands are in [execution.json](execution.json) and [repeat_execution.json](repeat_execution.json). Standard output and error logs are included. [reproduction.json](reproduction.json) records the completed comparison. The two planned runs are complete; they repeat the same corpus.

## Evidence

- [plan.md](plan.md), [config.json](config.json), [freeze.json](freeze.json): inputs frozen before implementation.
- [implementation_freeze.json](implementation_freeze.json): code hash before the first run.
- [study.py](study.py), [cases.jsonl](cases.jsonl), [summary.json](summary.json), [controls.json](controls.json), [checks.json](checks.json): complete methods and results.
- [source_search.md](source_search.md), [references.bib](references.bib): primary-source search and checked read scope.
- [deviations.md](deviations.md), [checklist.md](checklist.md): execution limits and review checks.
- Separate agent review and audit files are included before publication.

There is no random seed because enumeration is complete. CPU time was below one second in each observed run. The script checks the 60 CPU-second threshold after computation; it does not interrupt a long computation at that time. See deviations.md. No additional model API charge or paid compute occurred. No new license is assigned to the owner's work. Codex generated the study and report. No human or external peer review occurred.
