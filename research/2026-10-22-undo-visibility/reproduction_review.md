# Clean reproduction review

Status: **Passed**. Two complete runs were executed. No third full run was executed.

The second run used the unchanged study code, SQL schema, frozen plan, and configuration. It used new output and database directories. Each run retained 2,816 scored or serial-control trials and nine hand-control databases. No trial was replaced or excluded.

## Exact logical comparison

The six deterministic files match byte for byte. The SHA-256 values below identify the initial files. The second files have the same values. Full comparison data and commands are in [reproduction_receipt.json](results/reproduction_receipt.json).

| File | Exact match | SHA-256 |
| --- | --- | --- |
| cases.jsonl | Yes | `ad0ee492532fd0f2c6d97dd9e9639c31da82e257f80bc90759c52f1431d88919` |
| database_dumps.jsonl | Yes | `390a468fdd89dbf205d1b7b4f49df76a5600b0891604536aac75bc7659ac27b9` |
| summary.json | Yes | `048b250cf36b83d8206de3e400ceefb7624a03694161cae881b6d549a2391ae7` |
| summary.csv | Yes | `1ed6300e8bb7ed1eb6b4672b351e16dd20dd7635884299fd6c3e448a5e8b1e74` |
| witnesses.json | Yes | `d16abd2019e2c85731bee74d492022cce827fc701be8812ed4fb64f0e54db38f` |
| hand_controls.json | Yes | `cd3d62ccc5e72b8faf80d6e58bff7b25936c8713d6189ea41883c8f17aebaca7` |

## Recorded resources

| Measure | Initial run | Clean reproduction |
| --- | ---: | ---: |
| Parent plus exited-child CPU seconds | 375.585259 | 374.620997 |
| Monotonic elapsed seconds | 400.691098 | 397.727004 |
| Span between saved UTC stamps, seconds | 533.742865 | 397.729081 |
| Worker process calls | 4872 | 4872 |
| Physical databases retained | 2825 | 2825 |

The run receipt calls its monotonic value wall_seconds. The UTC spans are listed separately. The cause of their difference is not established from the saved records. Both time measures and CPU use are below their respective resource limits in each run.

## Evidence and limits

The second run's worker stdout, stderr, process exit statuses, process identifiers, and timings are retained in [reproduction_worker_logs.jsonl.gz](results/reproduction_worker_logs.jsonl.gz). Its environment, pre-run source hashes, and execution receipt are retained in the results folder. The second run's physical databases, compressed archive, and full logical results remain in the private work directory. The initial physical archive is part of the published evidence package. Physical archive byte identity is not a pass criterion.

This review checks reproducibility of the two finite runs. The separate independent evaluator checks the model predictions and stored tables. Its second archive check is recorded separately. No human or peer review is claimed.
