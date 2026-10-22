# Repeat the undo visibility study

Date: 2026-10-22. Read [the report](report.md) for the question, results, and limits. This is a real local SQLite experiment with synthetic data. It is not a website trial or a language-model benchmark.

## Requirements

The recorded environment is Python 3.13.7 with SQLite 3.50.4 and zlib 1.2.12 on Darwin 25.6.0, arm64. Only the Python standard library is used. The script uses POSIX process resource accounting. Other Python, SQLite, or operating-system versions are not validated by this release.

Use a local filesystem that supports SQLite WAL. Allow about 0.5 GB of free space for one full run and its checks. A full run must stay below 600 measured CPU seconds and 1,200 monotonic seconds. The script stops on an execution error or resource limit. It preserves partial evidence. Do not treat a partial run as a completed experiment. The two recorded full runs are the initial run and its clean repeat. No third full run was used to select the reported results.

## Check the saved evidence

Run these commands from this study folder. Keep the surrounding repository folders for relative report links.

```sh
python3 validate_package.py
check_dir="$(mktemp -d)"
python3 independent.py --out "$check_dir/predictions"
python3 independent_compare.py --actual results --out "$check_dir/comparison"
```

The independent comparison generates the complete oracle, checks all observed logical cases and worker logs, extracts the physical archive into a temporary directory, and reopens every database. It does not execute the undo experiment again. It requires `match: true`, 2,816 logical cases, 2,825 physical databases, 4,872 worker logs, and no differences. The pure evaluator's source hash must match `independent_implementation.json`. The comparison receipt records the adapter hash separately. The pure evaluator has 13 logical controls. The main experiment has 19 hand checks, including nine retained physical databases.

## Run a fresh experiment

Both target directories must not exist. Run:

```sh
run_dir="$(mktemp -d)"
python3 study.py --out "$run_dir/results" --db-dir "$run_dir/databases"
python3 independent_compare.py --actual "$run_dir/results" --out "$run_dir/checks"
python3 compare_runs.py --first results --second "$run_dir/results"
```

Do not run Python with `-O`; required assertions must remain enabled. The worker uses the same Python executable as the driver. No internet connection, external service, account, API key, or random seed is needed for these commands. There are no model calls within the experiment.

The complete run has 2,816 assigned cases and no unknowns. All source-completion and probe checks must pass to match the saved run. Separate and forced-open rules each have 256 serial violations, 224 local endpoint failures, and 32 joint-only violations. The durable gate refuses 1,024 primary jobs. The whole transaction accepts 1,024 primary jobs without a violation. All 768 serial controls must match their exact cut. Adverse results are expected evidence, not execution failures.

The comparison requires identical SHA-256 values for six deterministic logical files. Worker PIDs, timing, clock stamps, and archive bytes are not required to match. Check physical contents through the independent comparison. The saved reproduction receipts record both full runs and their actual resource use.

## File map

- `plan.md`, `config.json`, `freeze.json`: planned experiment and hashes saved before implementation.
- `schema.sql`, `study.py`, `implementation_notes.md`: actual database program and transaction boundaries.
- `independent.py`, `independent_implementation.json`: separately written schedule oracle and its prior hash.
- `independent_compare.py`, `independent_checks/`: complete comparisons with the physical evidence.
- `compare_runs.py`, `reproduction_review.md`: logical file comparison and clean-repeat record.
- `results/cases.jsonl`: one complete logical record per assigned case, in planned order.
- `results/database_dumps.jsonl`: SQL dumps of all trial and physical hand-control databases.
- `results/physical_databases.tar.gz`: the 2,825 actual checkpointed database files. They contain synthetic fields, receipts, gate state, decisions, and actions.
- `results/worker_logs.jsonl`: actual worker status, phase output, stderr, PID, timing, and CPU use.
- `results/summary.json`, `results/summary.csv`, `results/witnesses.json`: reported counts and selected witnesses.
- `results/hand_controls.json`: all 19 main hand checks.
- `results/environment.json`, `results/implementation_receipt.json`, `results/execution_receipt.json`, `results/logical_sha256.json`: versions, prior code hashes, run outcome, resources, and logical hashes.
- `results/reproduction_receipt.json`: clean-repeat comparison and resources; related reproduction files retain the second worker evidence.
- `source_review.md`, `source_supplement.md`, `design_review.md`, `references.bib`: prior work, reading scope, search terms, and pre-execution design.
- `independent_review.md`, `content_review.md`, `checklist.md`, `deviations.md`: review and change records.

## Interpret the records

`audit` is the post-exit source audit. `post_intervention_audit` records the forced gate opening when applicable. `reader_attempts` contains jobs 0 and 1, including refusals. Accepted jobs save both observed inputs and a decision bit. `final` precedes the new probe jobs. `final_with_probes` includes jobs 2 and 3. `serial_violation` scores accepted predicate outputs only. It is not a general serializability test of all stored observation columns.

`source_complete` means Q=(0,0), one receipt per field, and an open final gate. It does not mean that previous decisions were retracted or correct. `probe_success` requires both later probes to observe Q. A gate refusal is not a completed reader job. `unknown` means that required execution evidence was not available; it must never be counted as safe.

## Rights and review

Codex generated the study and report. Separate Codex agents performed implementation and review roles. No human review or external peer review occurred. No new reuse license is assigned. The program and test data were created for this study. Third-party papers and software are not bundled.
