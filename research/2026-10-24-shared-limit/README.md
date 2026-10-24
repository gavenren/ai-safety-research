# Shared-limit caller comparison

Read [report.md](report.md) for the question, method, results, and limits. This package tests synthetic schedules on local SQLite. It contains no live website or model-performance trial.

## Files

- `plan.md`, `freeze.json`, and the initial versions: the plan, saved before implementation, and its correction history.
- `run_study.py`: the complete SQL experiment and controls.
- `independent_check.py`: the separately written pure specification.
- `compare_independent.py`: comparison of saved SQL traces, logical rows, and physical database rows with that specification.
- `independent_freeze.json`, `independent_adapter_freeze.json`, `independent_review.md`: review order and evidence.
- `summarize_pairs.py`: paired metadata comparisons and adverse examples.
- `make_figure.py`: standard-library SVG figure generator.
- `results/`: inputs, complete traces, SQL statement logs, summaries, controls, environment, and compressed database evidence.
- `run.log`, `reproduction_run.log`, `reproduction_environment.json`: records of the two actual full runs.
- `reproduction.json`: seven deterministic outputs and their matching hashes.
- `independent_comparison.json`, `independent_reproduction_comparison.json`: checks of both actual runs.
- `source_search.md`, `source_review.md`, `references.bib`, `review.md`, `changes.md`: sources, review, and deviations.
- `manifest.json`: SHA-256 hashes of the selected publication files, except the manifest itself.

## Requirements

Tested with Python 3.13.7 and SQLite 3.50.4 on macOS 26.7.2, arm64. Only the Python standard library is needed. The runner uses Unix `resource` limits and SQLite error-code attributes. This is not a tested Windows recipe. SQLite must support WAL and BEGIN IMMEDIATE. Other environment versions have not been validated.

There are no downloads, account credentials, network calls, model API calls, or random seeds in the experiment. The scripts use invented inputs. Each full run permits at most 5,184 cases, 120 CPU seconds, 450 wall seconds, and 500 MB output. A limit or unexpected error stops execution. Preserve partial output if that occurs.

## Check the saved evidence

Run from this folder. Extract the saved database to a new local name:

```sh
python3 -c 'import gzip,pathlib; pathlib.Path("saved_evidence.sqlite").write_bytes(gzip.decompress(pathlib.Path("results/evidence.sqlite.gz").read_bytes()))'
python3 compare_independent.py --traces results/traces.jsonl.gz --database saved_evidence.sqlite --logical results/logical_database.json.gz --output saved_comparison.json
```

Expected result: `status` is `pass`, with 5,184 cases and 10,368 worker decisions. The adapter opens the database read-only. SQLite can create WAL sidecar files in the local directory; these are not publication data. The recorded physical hash is for the extracted database. The output report's file name differs when using `saved_evidence.sqlite`; its semantic checks must still pass.

## Repeat the experiment

Use a new output folder. The program refuses an existing folder so it cannot silently replace a partial run.

```sh
python3 run_study.py --out repeat_results > repeat_run.log
python3 summarize_pairs.py repeat_results > repeat_pairs.log
python3 compare_independent.py --traces repeat_results/traces.jsonl.gz --database repeat_results/evidence.sqlite --logical repeat_results/logical_database.json.gz --output repeat_comparison.json
python3 check_reproduction.py results repeat_results
```

`check_reproduction.py` checks the seven deterministic outputs named in `reproduction.json`. It does not compare environment timings or physical database layout. The complete expected 3-by-3 breach matrix is `[120,45,60;45,0,0;60,0,0]`, with rules ordered OwnCAS, SharedEpoch, AtomicSum. All row and epoch error counts must be zero. The expected code-517 snapshot control must pass.

To run the pure specification alone:

```sh
python3 independent_check.py --output repeat_independent
```

To regenerate the published figure from the saved summary:

```sh
python3 make_figure.py
```

The study performed two complete SQL runs. Both matched the independent specification. The documented saved-evidence check also passed using the compressed database. No third full run was needed.

## Interpretation and rights

The exact counts apply to this fixed corpus. They do not estimate a real workload's error probability. A complete guard must cover every relevant writer and commit with its effect. The study does not test an external provider's support for that condition.

Codex generated this package. Separate AI review is recorded. No human review or external peer review occurred. No new license is assigned. Sources retain their own rights. No source paper, figure, or implementation is redistributed.
