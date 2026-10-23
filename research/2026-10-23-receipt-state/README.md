# Receipt history and later state

Read [report.md](report.md) for the study. This is a complete finite model, not a production website test. Six rules run on 338 histories each. All input identifiers are invented.

## Repeat the analysis

Use Python 3.13.7 for the recorded environment. No package installation, model download, network call, API key, or random seed is needed. From this folder, run:

```sh
python3 analyze.py --out reproduced > reproduction_run.log
python3 independent_check.py --main-results reproduced/results.jsonl --out independent_reproduced > reproduction_check.log
python3 compare_outputs.py
```

The first command reconstructs the fixed grid and full traces. The second independently computes expected states and compares every record, score, and event. The last command checks the saved deterministic files against the reproduced files. Timestamps, CPU time, wall time, and command paths can differ and are excluded from byte comparison.

Expected result: 338 histories, 2,028 outcomes, seven main controls, 4,428 independent checks, and complete agreement on 14,716 trace events and 192,566 scalar values. The independent program does not import the main program. Both use the same frozen plan. The reviewer saw the author's predicted aggregate counts before its first run; this was not a blind review.

The recorded main run took 0.103 CPU seconds and 0.106 wall seconds. The recorded independent comparison took 0.232 CPU seconds. These are single local observations, not a benchmark. Model runs stay below the plan's 60 CPU second and 10,000 outcome limits. Source review and report work are not included in those timings.

## Files and interpretation

- `plan.md`, `plan_freeze.json`: question, hypotheses, rules, inputs, measures, stop gate, and pre-execution hash.
- `analyze.py`: event-based main implementation.
- `independent_check.py`: separate final-word and parity evaluator with a full-record adapter.
- `results/`: all inputs, raw outcome traces, aggregate counts, paired count differences, examples, controls, and measured environment.
- `independent_verified/`: independent rows, totals, paired examples, and comparison record.
- `run.log`, `initial_run.log`, `independent_check.log`: actual run outputs.
- `main_reproduction.json`, `independent_reproduction.json`: saved byte-comparison results.
- `review.md`, `final_review.md`, `independent_review.md`, `final_source_review.md`: review scope and results.
- `source_search.md`, `references.bib`: checked source record and read limits.
- `changes.md`: instrumentation and wording changes after the plan freeze.

All rows are synthetic. An extra effect is unauthorized under the declared single-operation contract. An unknown state is not a false claim. A correct read-time claim does not guarantee state at reply time. Exact counts do not estimate production risk.

Codex generated this study and report. Separate AI agents reviewed it. No human or peer review occurred. No new license is assigned.
