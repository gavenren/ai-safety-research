# Lowering a total budget

Date: 2026-10-28. Read [the report](report.md).

The study compares five ways to lower a budget while old work holds reserved capacity. All new jobs have the same complete atomic guard. Checking only spent use still permits 576 unsafe reductions in 3,888 selected cases. Checking current spent plus reserved use in the cap transaction permits no unsafe reduction in this corpus. These are local synthetic SQL results.

## Repeat the work

Use Python 3.13.7, SQLite 3.50.4, and a Unix-like system for the closest match. The script uses Python's Unix `resource` module; native Windows is unsupported. No package installation, network, account, paid service, model call, or seed is needed. Run from this folder. New output folders must not already exist.

```sh
python3 run_study.py --out rerun_a > rerun_a.log
python3 run_study.py --out rerun_b > rerun_b.log
python3 check_reproduction.py rerun_a rerun_b > rerun_bytes.json
python3 compare_independent.py --results rerun_a --out rerun_independent_a.json
python3 compare_independent.py --results rerun_b --out rerun_independent_b.json
python3 check_reproduction.py results rerun_a > saved_bytes.json
```

Each program must exit with code zero. Main and comparison outputs set `passed` to `true`. The original commands used `results` and `reproduced` as output folders. Both ran fully. The second full folder is omitted from publication because its 11 scientific files have identical bytes. The second environment record and all logs remain.

The byte comparison excludes environment records because time differs. On a different SQLite or compression-library version, database pages, SQL text, or compressed bytes can differ. Do not claim byte identity if that check fails. Keep the difference and use the independent row, trace, and decision checks to assess the changed environment separately. A different engine may need a separate reproduction study.

Expected primary scope: 3,888 input histories, five rules, 19,440 rule cases, 77,760 steps, 174,960 saved state records, and 38,880 U/B decisions. Before/after state records include repeated boundary values. Six named controls create 30 additional cases. The engine controls use one further row. The reopened database therefore has 19,471 rows. Summary groups overlap.

## Files

- `plan.md`, `plan_freeze.json`: pre-experiment contract, rules, measures, and source hash.
- `run_study.py`, `implementation_freeze.json`: frozen main SQL procedure.
- `independent_spec.py`, `independent_freeze.json`: separate formulas, frozen before main-source access.
- `compare_independent.py`, `independent_adapter_freeze.json`: output and SQL comparison, frozen before main-result access.
- `results/inputs.json`: complete generated settings and orders.
- `results/traces.jsonl.gz`: full per-case states, conditions, decisions, and scores.
- `results/sql.jsonl.gz`: every SQL statement after connection setup, with caller/case/event labels. Setup PRAGMAs precede tracing and are recorded as settings instead.
- `results/ledger.sqlite`, `results/final_rows.json`: actual database and reopened row export.
- `results/summary.csv`, `results/paired.json`, `results/witnesses.json`: overlapping groups, matched outcomes, first adverse examples.
- `results/controls.json`, `results/engine_controls.json`, `results/checks.json`: named cases and verification records.
- `results/environment.json`, `reproduction_environment.json`: actual versions, run times, and in-run resource records.
- `run.log`, `reproduction_run.log`, `independent_run.log`, `independent_reproduction_run.log`: saved successful command output.
- `check_reproduction.py`, `reproduction.json`: byte-comparison procedure and results.
- `independent_comparison.json`, `independent_reproduction_comparison.json`, `independent_review.md`: complete independent checks and limits.
- `source_search.md`, `references.bib`, `source_review.md`, `design_review.md`, `final_review.md`, `changes.md`: search, references, reviews, and later record changes.
- `package_checks.json`, `manifest.json`: local publication checks and file sizes/hashes. The manifest excludes itself.

Read compressed JSON lines with Python `gzip.open` and `json.loads`. Inspect the SQLite database with a read-only URI to avoid changing saved fields. SQLite can create temporary reader files in the folder even when the ledger is opened read-only.

## Resource measurement note

The saved `output_bytes_before_environment` is an in-run directory footprint. Each value is 6,536,149 bytes. After process exit, the 11 durable scientific files total 6,503,381 bytes. The 32,768-byte difference is consistent with a temporary SQLite shared-memory file. The main procedure does not explicitly close its reopened read connection before measurement. No separate temporary file capture establishes its contents. Keep these two measures distinct. The environment record is excluded from both totals.

## Scope and review status

This is a complete selected finite corpus, not a production rate estimate. Spent use cannot be refunded. The reserved amount is a truthful maximum. There is no crash, external call, cancellation, or concurrent stress test. A refused reduction leaves the old cap active and does not meet the lower-cap request.

Codex generated the work. Separate Codex agents performed source, method, and independent formula checks. The exact model build was not exposed. No human or external peer review occurred. No new license is assigned.
