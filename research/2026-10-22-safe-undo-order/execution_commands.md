# Execution commands

Both full runs were executed from the workspace root. The following are the exact experiment command strings. These commands were not run a third time during documentation review.

```sh
python3 outputs/2026-10-22-safe-undo-order/study.py --out work/2026-10-22-safe-undo-order/run-1
python3 outputs/2026-10-22-safe-undo-order/study.py --out work/2026-10-22-safe-undo-order/run-2 > work/2026-10-22-safe-undo-order/run-2.stdout.txt 2> work/2026-10-22-safe-undo-order/run-2.stderr.txt
```

Both shell calls returned exit code 0. Each run saved start and final execution receipts before evidence was copied into this package. The first run's stdout was displayed by the terminal tool. The second run's raw stdout and stderr are retained as `reproduction.stdout.txt` and `reproduction.stderr.txt`. The latter is empty. Every case record was flushed to `cases.jsonl` during execution.

After the second run, a standard-library comparison read the five deterministic files from both output directories. It required exact byte equality, then saved their SHA-256 hashes and sizes in `reproduction.json`. The first run's deterministic files were copied into this package. Both final execution receipts were retained. The comparison command in the README performs the same byte check against a repeat directory.

The execution receipts normalize the script component to `study.py`; that field is not an exact capture of the original command path. The commands above preserve that distinction. Timings exclude interpreter startup and initial configuration reads. These values are resource records, not a method speed comparison.
