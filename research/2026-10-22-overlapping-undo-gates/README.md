# Repeat the gate study

This package is a finite synthetic model. It uses only the Python standard library. No service, account, database, or AI API is needed.

## Read the evidence

- `report.md`: question, results, assumptions, and limits.
- `plan.md`, `config.json`, `source_search.md`, `freeze.json`: inputs saved before implementation.
- `plan_initial.md`, `freeze_initial.json`, `deviations.md`: retained pre-execution count-check correction.
- `implementation.json`: code hash saved before the first run.
- `study.py`: generator, four state machines, oracle, alternate formulas, controls, and runner.
- `raw_results.jsonl`: every history and every post-request state for all four rules.
- `summary.json`, `witnesses.json`, `hand_controls.json`, `checks.json`: measured summaries and checks.
- `execution.json`, `run.log`: first run.
- `reproduction_execution.json`, `reproduction_run.log`, `reproduction.json`: repeated run and exact file comparisons.
- `references.bib`, `source_checks.md`, `checklist.md`: sources and review aid.

## Run

The original commands, from the workspace root, were:

```sh
python3 outputs/2026-10-22-overlapping-undo-gates/study.py --out work/2026-10-22-overlapping-undo-gates/run-1
python3 outputs/2026-10-22-overlapping-undo-gates/study.py --out work/2026-10-22-overlapping-undo-gates/run-2
```

The execution receipts store the short script name `study.py` in their command field. The lines above give the actual script paths used. Output directories must be new. The script refuses an existing directory to preserve evidence.

After you download the folder, use Python 3.13 or later. Run this command from the package folder. Choose an output path that does not exist:

```sh
python3 study.py --out /tmp/overlapping-gates-reproduction
```

The input paths are resolved against the script's folder. The output path is resolved against your working folder. The program checks frozen hashes before it runs. It does not write into the study inputs. It uses `SIGALRM` for the wall limit; use a Unix-like system. There is no random seed.

A successful run reports 1,603 histories and status `complete`. The two-operation group has 1,596 histories; the one-operation control group has seven. Five separate hand histories are checks, not new primary histories.

Compare these six files against the saved package: `raw_results.jsonl`, `summary.json`, `witnesses.json`, `hand_controls.json`, `checks.json`, and `run.log`. Each must match byte for byte. `execution.json` contains variable commands, clocks, and memory records, so it must not match byte for byte. Its source and deterministic-output hashes must match.

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib
old = Path('.')
new = Path('/tmp/overlapping-gates-reproduction')
names = ['raw_results.jsonl', 'summary.json', 'witnesses.json',
         'hand_controls.json', 'checks.json', 'run.log']
for name in names:
    a = (old / name).read_bytes()
    b = (new / name).read_bytes()
    assert a == b, name
    print(name, hashlib.sha256(a).hexdigest())
PY
```

The released `reproduction.json` records this comparison for the two runs already completed. A repeated corpus is not another independent sample.

## Row schema

Each JSONL row has one `history_id`, group, duplicate pattern, ordered event list, overlap indicator, all post-event states, and all rule scores. A label such as `A_C1` means operation A, close, duplicate delivery. The rule update function receives only A and C, not the duplicate marker. The oracle uses the first-event labels.

`unsafe_open` means a reader was permitted while work was active. `unnecessary_closed` means a reader was refused while no work was active. Counts of points and histories are different measures. No actual reader process or external action is executed.

## Rights and status

No new license was selected. The note is AI-generated. Separate agent review passed; see [separate_review.md](separate_review.md). No human review or external peer review occurred. The main agent must verify the remote files before it reports publication.

## Production extension, 2026-10-22

Eight selected Google Drive cases added 40 observed boundaries. The flag and count rules admitted three reads while another operation remained pending. The registry matched the selected checkpoints. One late read and one missing fresh metadata baseline limit the full-set claim.

See [live_README.md](live_README.md) for the separate evidence replay and its limits. See [live_cleanup.md](live_cleanup.md) for cleanup. The original synthetic procedure and data above are retained.
