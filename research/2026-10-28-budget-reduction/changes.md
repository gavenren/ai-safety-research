# Changes and review findings

Date: 2026-10-28.

The saved plan preceded main implementation and execution. The independent formulas were frozen before their author read main source or results. Expected counts were shared after the main source freeze and before the main results were inspected. The later comparison adapter used the known schema but did not import the main code. This is partial separation, not a blind final report review.

No input range, rule, hypothesis, measure, or outcome changed after the plan. No exploratory run was added. Both complete main runs and both independent comparisons passed without a source repair. All four frozen source/plan hashes still match. Eleven durable scientific files, including the database and SQL log, matched byte for byte.

The method reviewer found a resource-report detail: a SQLite connection context ends its transaction but does not close its connection. The main script's reopened reader was not explicitly closed before measuring the output directory. We retained the frozen code and evidence. The report and README now distinguish the in-run footprint from durable scientific bytes after process exit. Their 32,768-byte difference is consistent with a temporary shared-memory file; no separate capture proves its contents. This is a reporting qualification, not an experiment outcome change.

The saved reproduction script checks existing outputs after the study processes end. The planned rollback and refused-write controls passed. They are retained as successful controls. No unexpected main-run or independent-comparison failure occurred.

No connected account record was created or changed. No cleanup is required for this local study. Publication attempts and remote verification are recorded separately in task state.
