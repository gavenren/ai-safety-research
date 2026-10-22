# Safe undo order

Read [report.md](report.md) for the study and its limits. The test is a synthetic finite model. It uses no database, website, connected account, or language model during execution.

## Repeat the experiment

Use Python 3.13 on macOS or another Unix system that supports Python's `resource` and `signal.alarm` functions. The recorded system used Python 3.13.7 on macOS 26.7.2, arm64. No package installation, GPU, network access, or random seed is required.

From this folder, use a new output path:

```sh
python3 study.py --out /tmp/safe-undo-order-repeat
```

The output path must not exist. The script checks the frozen file hashes. It stops on an assertion error, uses a 60 CPU-second limit and a 120-second wall limit, and saves an execution receipt. The reported CPU and wall times begin after startup and configuration reads. A hard operating-system termination may prevent a final receipt; the start receipt and any partial case file remain available.

Compare the deterministic output to this package:

```sh
python3 - /tmp/safe-undo-order-repeat <<'PY'
from pathlib import Path
import sys
out = Path(sys.argv[1])
for name in ['cases.jsonl', 'summary.json', 'conditions.json', 'witness.json', 'checks.json']:
    assert Path(name).read_bytes() == (out / name).read_bytes(), name
print('All five deterministic files match.')
PY
```

Execution timestamps and timing are expected to differ. A repeat uses the same 1,179 cases. It does not add new cases or a new independent dataset.

## Files

- `plan.md`, `config.json`, `source_search.md`, and `freeze.json`: plan saved before implementation.
- `study.py` and `implementation_freeze.json`: implementation and its hash before execution.
- `cases.jsonl`: all 1,152 primary and 27 smaller-state rule cases, including every state trace.
- `summary.json` and `conditions.json`: counts by rule, priority, and state condition.
- `witness.json`: the first avoidable dead end and the two paired rules.
- `checks.json` and `analytic_checks.md`: executed controls and a post-run count derivation.
- `execution_run_1.json`, `execution_run_2.json`, `reproduction.json`, and `reproduction.*.txt`: run receipts and clean-repeat evidence.
- `validation.md`, `deviations.md`, and `references.bib`: review record, changes, and references.

The graph oracle in study.py is a different algorithm in the same program, written by the same Codex agent. It is not an independently authored implementation. A separate agent's evaluator and completed review are recorded in `separate_review.md` and `validation.md`. No human review occurred. No new reuse license is assigned.

## Production extension, 2026-10-22

Six selected Google Calendar cases added 16 browser field changes. Fixed order crossed a declared invalid state, greedy order stopped before the target, and complete search followed a valid path. The state condition was supplied by the researcher; Calendar did not enforce it.

See [live_README.md](live_README.md) for the separate evidence replay and its limits. See [live_cleanup.md](live_cleanup.md) for cleanup. The original synthetic procedure and data above are retained.
