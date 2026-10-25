# Reservation release after an acceptance fence

Read [report.md](report.md) for the question, results, and limits. This package is a finite simulation. No website, account, payment, or language model executes a trial.

## Requirements

Tested with Python 3.13.7 on macOS 26.7.2, arm64. Only the Python standard library is needed. The runner uses Unix resource limits. This is not a tested Windows recipe. There are no network calls, credentials, paid services, or random seeds.

Each main run has 1,680 input worlds and 8,400 rule outcomes. The limits are 120 CPU seconds, 300 wall seconds, and 200 MB of output. Unexpected errors stop the run and preserve partial files. Keep any partial output and `failure.json`; do not replace them silently.

## Check the published evidence

Run from this study folder:

```sh
python3 compare_independent.py --results results --output checked_saved_results.json
```

Expected result: `status` is `pass`, with 8,400 cases, 1,680 worlds, 15 summary rows, and 10 paired comparisons. This reads the existing experiment evidence and does not run the main experiment. It imports the independently written specification, not `run_study.py`.

## Repeat the experiment

Use a new output folder. The runner refuses an existing folder to preserve partial work.

```sh
python3 run_study.py --out repeat_results > repeat_run.log
python3 compare_independent.py --results repeat_results --output checked_repeat_results.json
python3 check_reproduction.py results repeat_results
```

The last command compares seven deterministic output files. Environment timing and figure files are excluded. Expected actual-breach counts in rule order are `130,105,55,0,0`. Expected exposure-breach counts are `200,175,70,0,0`. Rule order is Timeout, ZeroObservation, FenceOnly, ClosureCertificate, TerminalOnly. Every rule has 1,680 worlds.

To regenerate the figure from the saved summary:

```sh
python3 make_figure.py
```

The completed study used two full main runs. Both matched the separately frozen specification. Seven deterministic outputs matched byte for byte. No third full main run was needed. Read the saved logs and comparison reports for exact evidence.

## File guide

| Files | Contents |
| --- | --- |
| `plan.md`, `freeze.json`, `implementation_freeze.json` | Plan and main-code hashes saved before execution. |
| `run_study.py` | Complete main interpreter, schedule generator, audit, and controls. |
| `independent_check.py`, `independent_freeze.json` | Position-based specification written before main-code/result access. |
| `compare_independent.py`, `independent_adapter_freeze.json` | Later comparison adapter and its saved hash. |
| `independent_controls.json`, `independent_result.json`, `independent_review.md` | Independent control expectations, run result, and review order. |
| `independent_comparison.json`, `independent_reproduction_comparison.json` | Full checks of both actual main runs. |
| `results/inputs.json` | All 1,680 input worlds. |
| `results/traces.jsonl.gz` | All 8,400 rule outcomes, with complete initial, before/after, and final states. |
| `results/controls.json` | All 35 named control rows, expectations, and traces. |
| `results/summary.csv`, `results/paired.json` | Per-rule/branch counts and matched-rule differences. |
| `results/witnesses.json` | First adverse examples in enumeration order; no global minimality claim. |
| `results/checks.json`, `results/environment.json` | Property checks and main-run environment. |
| `run.log`, `reproduction_run.log`, `reproduction_environment.json`, `reproduction.json` | Two run records and the seven matching hashes. |
| `make_figure.py`, `results/breach_comparison.svg` | Standalone comparison figure and generator. |
| `source_search.md`, `source_review.md`, `references.bib` | Primary-source search, reading limits, and attribution. |
| `design_review.md`, `review.md`, `changes.md` | Design, final review, and work record. |
| `manifest.json` | SHA-256 file manifest, excluding itself. |

The adapter's source-access flags describe what the comparison program reads. The reviewer inspected the main source only after the first independent comparison passed. The review records that chronology. The second comparison used unchanged frozen code after source inspection.

## Scope and rights

The corpus counts are not independent samples of production risk. All policies receive the same observation, fence, and receipt schedule. The model assumes correct charge bounds and sound job-specific evidence. B charges immediately, and all final A outcomes arrive. These assumptions must hold for the stated safety argument.

Codex generated the package. Separate AI review is recorded. No human review or external peer review occurred. No source asset is redistributed and no new license is assigned.
