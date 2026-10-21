# Undo after a crash

Read [report.md](report.md) for the question, findings, and limits. This is a finite simulation, with no new website trial. Codex generated the study and report. No human review occurred.

## Repeat the experiment

Use Python 3.13.7 on macOS or Linux and its standard library. The recorded environment is in environment.json. The resource module is not available in standard Windows Python. No package install, account, network request, paid service, or model API is needed. From this folder:

```sh
python3 study.py --out repeat/main
python3 independent.py --out repeat/independent --compare repeat/main/outcomes.csv
python3 validate.py --results repeat/main --reference results
```

The first command checks frozen input hashes, runs 12 hand-checked controls, enumerates every case, and writes the results. The second command uses a separately written evaluator and compares every outcome field. The third command checks raw traces, summaries, report tables, and deterministic files against the saved run. All commands must exit successfully.

`execution.json` records time, memory, runtime, and command. It is not byte-equal across runs. The other eight main result files are deterministic in the recorded environment. A different Python or zlib version can change compressed bytes. In that case, compare decoded traces and use `python3 validate.py --results repeat/main` for value and report checks. The independent run metadata also varies by run. There is no random seed because the input space is fully enumerated.

## Inputs and rules

- [plan.md](plan.md): frozen question, hypotheses, exact rule definitions, case order, decision criteria, resource gate, and limits.
- [config.json](config.json): alphabet, initial values, cuts, settings, and rule order.
- [freeze.json](freeze.json): pre-execution hashes and timestamp.
- [source_search.md](source_search.md): source searches, related work, checked passages, and access limits.
- [study.py](study.py): slot-by-slot simulator and result generation.
- [independent.py](independent.py): separately written field-prefix evaluator.
- [validate.py](validate.py): evidence and report checks.
- [references.bib](references.bib): sources cited in the report.
- [deviations.md](deviations.md): changes, failures, and resolution notes.
- [review.md](review.md): independent review and release checks.

## Results

- `results/cases.jsonl`: all 2,924 ordered synthetic cases. Each line gives initial fields, cuts, external command words, and the reference state.
- `results/outcomes.csv`: 20,468 rule outcomes, one row per case and rule. Boolean fields use 0 or 1. Counts refer to applied undo commands, not service calls.
- `results/traces.jsonl.gz`: one compressed JSON line per outcome. Each line records every slot, crash, external command, and final audit. Gzip has a fixed timestamp for repeatable bytes.
- `results/summary.csv` and `results/summary.json`: exact setting and no-external-edit subset counts.
- `results/pairs.json`: paired classifications against atomic_inverse on the same cases.
- `results/witnesses.json`: the first case in each nonempty rule/outcome category.
- `results/checks.json`: controls, frozen-input checks, case counts, inverse identities, and hypothesis decisions.
- `results/execution.json`: measured execution resources and versions.

The four outcome classes are correct_completion, false_completion, refusal_correct, and refusal_incorrect. A correct state with refusal is not a completed task. A fixed assignment can count as an application without changing a field. All records are synthetic; no private account data are included.

The source papers and websites are not bundled. No third-party code or data was reused. This repository has no selected reuse license. This study does not add one.
