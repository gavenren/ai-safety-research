# Cumulative usage reconciliation study

Date: 2026-10-26. Read [report.md](report.md) for the question, method, results, and limits.

The original study is a finite simulation. Its simulator does not call a model, provider, website, or connected account. A separate production extension is described at the end of this README and in [live/README.md](live/README.md). All provider work is complete before the modeled report deliveries. Inputs are invented integers and report labels.

## Environment and limits

The saved runs used Python 3.13.7 on macOS 26.7.2, arm64. Only the Python standard library is needed. There is no random seed. The main script uses the Unix `resource` module for a 120 CPU-second limit. It checks a 300-second wall limit and 200 MB output limit during enumeration and at the end. The latter checks are periodic, not hard real-time guarantees. Windows was not tested.

First run: 0.90607 CPU seconds and 0.92614 wall seconds. Second run: 0.88596 CPU seconds and 0.91869 wall seconds. Each primary output set used 996,223 bytes before its environment record. See [results/environment.json](results/environment.json), [reproduction_environment.json](reproduction_environment.json), [run.log](run.log), and [reproduction_run.log](reproduction_run.log).

## Check the saved evidence

Run from this study folder after obtaining the whole repository or this complete study folder:

```sh
python3 compare_independent.py --results results --output checked_saved_results.json
```

This recomputes expected states from the independent specification and compares the saved data. It does not run or import `run_study.py`. A pass covers every input, state, event, decision, score, summary, paired comparison, control, and saved first witness. It is a check of the finite model, not another production trial.

## Repeat the main procedure

The output directory must be empty or absent. `reproduced/` is not included in the published package because its deterministic data duplicate `results/`. Use this command once in a fresh download:

```sh
python3 run_study.py --out reproduced > reproduction_run.log
python3 check_reproduction.py results reproduced > reproduction.json
python3 compare_independent.py --results reproduced --output independent_reproduction_comparison.json
```

The comparison must return `pass`. Seven deterministic files must match exactly: inputs, controls, compressed traces, summary, paired results, witnesses, and checks. Environment times can differ. Gzip headers use a zero timestamp and no path, so identical traces have identical compressed bytes.

To repeat the independent enumeration alone:

```sh
python3 independent_spec.py --output independent_rerun.json
```

This produces the independent representation and its summaries. It does not produce the main trace schema. `compare_independent.py` maps between them. Do not confuse this output with another main run.

The original first command was `python3 run_study.py --out results > run.log`. It was followed by the reproduction commands above. Two full main runs were completed. Later checks read saved evidence. No third main run was needed.

## Files and data contract

| File | Purpose |
| --- | --- |
| plan.md and plan_freeze.json | Question, hypotheses, exact rules, input order, measures, controls, and pre-implementation hash |
| implementation_freeze.json | Main-source hash before execution |
| run_study.py | Event-by-event main interpreter |
| results/inputs.json | All 3,240 input worlds in the fixed order |
| results/traces.jsonl.gz | 19,440 complete world/rule records; 85,536 transitions |
| results/summary.csv | Six rules, each with ALL and four delivery groups; 30 rows |
| results/paired.json | Six matched admission comparisons against TerminalOnly |
| results/controls.json | Eight named controls times six rules |
| results/witnesses.json | First adverse example for each applicable rule/measure; no global minimality claim |
| results/checks.json | Main input, control, and invariant checks |
| reproduction.json | Byte equality and SHA-256 for seven deterministic files |
| independent_spec.py and independent_freeze.json | Prefix-formula specification and its freeze before main access |
| compare_independent.py and independent_adapter_freeze.json | Schema adapter and its freeze before complete comparison |
| independent_comparison.json and independent_reproduction_comparison.json | Full comparison results for both saved main runs |
| independent_result.json and independent_controls.json | Independent enumeration and hand-specified controls |
| design_review.md and independent_review.md | Design and independent verification scope |
| source_search.md and source_review.md | Source queries, checked sections, prior work, and claim review |
| references.bib | Source records |
| changes.md and review.md | Order of work, deviations, and final method review |
| manifest.json | SHA-256 and size of each selected study file except the manifest itself |

Each trace has initial state, all before/after states, report metadata, D decision, final state, and scores. `q` is booked A use; `h` is its hold; `f` records whether T arrived; `seen` lists received IDs; `k` is booked B use. `available=C-q-h-k`. The event `D` has no report value. The initial first-bad index is -1 and its label is INITIAL.

The actual-excess and uncovered-use scores use fixed audit truth z. They do not estimate live-provider exposure. A final error is q-z. Local deficit, actual excess, inflated accounting, and refusal are different measures and can overlap. They must not be summed as independent failures.

## Review and rights

Codex generated the study. Separate Codex agents reviewed its sources and methods and wrote the independent specification. The host model build is not exposed. No human or external peer review occurred. The independent implementation shares the written model and can share a model error. No production reliability or global novelty is claimed. No new license is assigned. Third-party works are linked and paraphrased, not copied into this package.

## Production record extension

The owner requested a live extension on October 26 after the original publication. See [live/README.md](live/README.md) for the separate production evidence and analysis commands. Eight shared fixtures support 48 paired decisions on Google Drive and Google Calendar. All 34 counted records were saved and checked. The test budget and report delivery were local controls, not Google quota or billing behavior. The original frozen simulation files remain unchanged.

## Guarded ledger extension

The owner requested a second production test after the six-rule comparison. The [guarded plan](guarded/plan.md) defines eight cases on each of Drive and Calendar. [CheckedLedger](guarded/controller.py) uses a fixed cumulative counter, residual reservation, and a stored intent before dispatch. The controller has no network code. The account adapters execute only a saved permit.

The new tests created 26 counted temporary records. They had no scoped count excess or repeated permit. Calendar's initial field adapter produced seven unsupported full-field completion outputs on four records because the read tools omitted the saved time-zone label. Later exact-event browser checks and a corrected adapter resolve the current field evidence. The original failed proof timing remains in the report and traces.

Use [the saved-data analysis guide](guarded/analysis_README.md) to repeat the public calculations. Use [the frozen operator guide](guarded/README.md) with [Calendar execution notes](guarded/calendar_execution_notes.json) for the procedure and deviations. Read [the source record](guarded/sources.md) for the new references. These are selected controlled cases, not provider error rates or a general deployment guarantee.

## Prospective Calendar zone extension

The owner then requested new events to test the corrected field check. The [new guide](calendar_zone_live/README.md) gives the 12-event, 36-evaluation procedure and repeat command. The check refused missing and incorrect assigned zone evidence and both actual wrong saved zones. Complete evidence changed eight refusals to acceptance. All 12 temporary events returned cancelled. The earlier seven unsupported outputs remain in the paper.
