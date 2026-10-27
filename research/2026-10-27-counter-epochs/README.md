# Counter restarts and total use

Date: 2026-10-27. Read [the report](report.md).

Sorting reports by source order does not expose every counter restart. In this declared finite model, SourceOrderDrop undercounts 1,296 of 5,184 histories. A maximum for each stable counter incarnation gives an exact final total in all primary histories. An incarnation is one accumulation period. These results require truthful identities, disjoint use, and separate evidence that all final reports arrived. They are simulation results, not production rates.

## Repeat the study

Use Python 3.13.7 and its standard library for the closest match to the saved run. The script uses the Unix `resource` module. Use macOS or another Unix-like system; native Windows is not supported. No install, network request, account, model call, or random seed is needed. Run these commands from this folder. They write to new result folders and leave the published evidence unchanged.

```sh
python3 run_study.py --out rerun_a > rerun_a.log
python3 run_study.py --out rerun_b > rerun_b.log
python3 check_reproduction.py rerun_a rerun_b > rerun_comparison.json
python3 compare_independent.py --results rerun_a --out rerun_independent_a.json
python3 compare_independent.py --results rerun_b --out rerun_independent_b.json
python3 check_reproduction.py results rerun_a > saved_result_comparison.json
```

Each comparison must exit with code zero and set `passed` to `true`. The byte check compares seven scientific files. It excludes the environment record because elapsed times differ. Compression bytes can differ on another Python or compression-library version. In that case, compare decompressed records and report the byte difference; do not claim byte identity. The independent comparison still checks values and every state.

The two original runs used `--out results` and `--out reproduced`. Their logs and environment records are included. The second full result folder is omitted from publication because its seven scientific files are byte-identical. `reproduction.json` preserves that check. One complete raw result set remains in `results/`.

Expected totals per main run are 5,184 histories, five rules, 25,920 rule-history outcomes, 151,200 states, and 155,520 independent admission branches. The independent comparison also checks 35 control rows, 30 summary rows, five matched-decision tables, and ten first adverse examples. Do not add counts from overlapping summary groups.

## Files

- `plan.md`, `plan_freeze.json`: fixed contract, rules, measures, and resource bounds before implementation.
- `run_study.py`, `implementation_freeze.json`: main simulation and frozen source hash.
- `independent_spec.py`, `independent_freeze.json`: separate formula specification frozen before access to main code or results.
- `compare_independent.py`, `independent_adapter_freeze.json`: full comparison code and its freeze.
- `results/inputs.json`: all declared inputs and report orders.
- `results/traces.jsonl.gz`: all rule states and independent admission branches. Read with Python's `gzip.open` and `json.loads`.
- `results/summary.csv`, `paired.json`, `controls.json`, `witnesses.json`, `checks.json`: summaries and retained evidence. These five files are all in `results/`.
- `results/environment.json`, `reproduction_environment.json`, `run.log`, `reproduction_run.log`: actual run records.
- `check_reproduction.py`, `reproduction.json`: exact-byte comparison and saved result.
- `independent_comparison.json`, `independent_reproduction_comparison.json`, `independent_review.md`: separate comparison results and limits.
- `source_search.md`, `source_review.md`, `references.bib`: search terms, checked sources, source limits, and references.
- `design_review.md`, `final_review.md`, `changes.md`: method review, publication checks, and changes after the plan.
- `manifest.json`: sizes and SHA-256 hashes for the other published study files.

## Limits and review status

All inputs are invented. Both source order and counter identity are trusted. The simulation has no live concurrency, missing primary report, or admission before closure. A separate negative control with a missing final report refuses admission. Known-rule comparisons do not prove research priority or a new protocol.

Codex generated the study and report. Separate Codex agents checked formulas, methods, and sources. The exact model build was not exposed. No human or external peer review occurred. No new license is assigned.
