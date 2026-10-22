# Cancellation across restarts

This is one exact synthetic model study. It contains no browser trials or production cancellation tests. Read [report.md](report.md) for the result and limits.

## Repeat the calculation

Requirements: Python 3.10 or later on a Unix-like system, with the standard library and its `resource` module. Recorded runs used Python 3.13.7 on macOS arm64. No package install, key, model, network request, or random seed is needed.

From this directory, use an empty output directory:

```sh
python3 study.py --out repeat-run
python3 compare.py --baseline . --candidate repeat-run
```

The program refuses to overwrite result files. It enforces a 60-second process CPU limit and checks a 120-second wall limit. The study plan allowed two full author runs. A later reader can repeat it in a new directory. The example creates a directory; the released evidence is flat.

`compare.py` does not run the model. It compares six deterministic files and checks saved hashes. Run-specific time, process ID, command, and environment fields need not match. The author used the same procedure with the repeat output outside the release directory; exact commands are in invocations.txt.

## File roles

- `plan.md`, `config.json`, `source_search.md`, `freeze.json`: frozen model, controls, source record, and input hashes.
- `source_supplement.md`: correction to the last checklist sections' reading time. No model change.
- `study.py`, `implementation_freeze.json`: interpreter, separate schedule enumerator and formula checks, and pre-run code hash.
- `raw_results.jsonl`: all 4,284 policy cases and their complete traces.
- `summary.csv`, `summary.json`: all horizon/rule counts and combined rule totals.
- `controls.json`, `checks.json`: 63 control rows, formula checks, unknown count, and hypotheses.
- `witnesses.json`: first stale witness for each rule with one. Order is restart count, main schedule order, then rule order.
- `execution.json`, `execution.log`: first-run environment, hash, resource use, and progress. `command` is normalized; `invocations.txt` gives exact commands and working directories.
- `repeat_execution.json`, `repeat_execution.log`, `reproduction.json`: repeat environment, progress, and byte comparison.
- `compare.py`: output comparison and saved-hash check.
- `failed_checks.md`, `review_checklist.md`: retained failures and content checks. `separate_review.md` records the completed separate agent review.
- `separate_audit.py`, `separate_audit_freeze.json`, `separate_audit_result.json`, `separate_review.md`: separate evaluator and review evidence.
- `local_checks.json`: report table and local file-link checks.
- `report.md`, `references.bib`: paper and primary-source details.

## Data contract

Each row is a schedule and fixed rule, not a user or real task. `stale_attempt` means O occurs after A1. `stale_accepted` requires this timing and acceptance. `stale_after_new` and `stale_while_inactive` are subsets. `rejected_valid_old` means an old action before A1 was rejected. `trace` records state after each event. `old_state` is the state before O. `effects` holds only accepted O/N labels. A null acceptance means that the event attempts no effect.

All data are synthetic. No third-party full text or private data is included. No new license is assigned. No human review or peer review is claimed.
