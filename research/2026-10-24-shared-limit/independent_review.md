# Independent specification and SQL evidence review

Date: 2026-10-24. Reviewer: a separate Codex agent. This is an AI review, not human review or peer review.

## Review order and scope

The reviewer read the plan and earlier repository studies. Before implementation, the reviewer found one overbroad check in the first plan: an unrelated update can change OwnCAS or AtomicSum behavior indirectly when it first causes a SharedEpoch peer to refuse. The plan was corrected to limit the unchanged-behavior check to pairs with no SharedEpoch worker. The initial and corrected plans remain in the package. No trial had run at that point.

The reviewer then wrote `independent_check.py` from the corrected plan without reading or importing the main runner. Its hash and the plan hash were saved in `independent_freeze.json` before its first execution. The pure evaluator covers all 5,184 semantic inputs and retains every read, decision, and state transition.

After the main SQL run, the reviewer received the evidence schema and read selected raw examples. A separate adapter, `compare_independent.py`, maps the saved evidence to the frozen specification. Its code hash was saved in `independent_adapter_freeze.json` before the complete comparison. The adapter imports the independent specification only. It does not import the main runner.

The complete comparison passed before the reviewer read the main runner source. The reviewer then inspected that source for transaction boundaries, case isolation, connection settings, guard scope, control behavior, and evidence retention. The independent specification did not change after that inspection.

## Comparison results

All 5,184 cases matched. The comparison checked:

- 10,368 worker decisions, including acceptance, reason, attempt status, and current feasibility.
- 350,784 scalar values in complete states before and after scheduled events.
- 72,576 scalar values in saved worker reads.
- 62,208 case score values.
- 137,132 SQL log statements, including SQL text, parameters, returned rows, and affected-row counts.
- All 5,184 quota rows and 10,368 allocation rows in the logical dump and reopened physical database.

The physical database was opened read-only. Its integrity check returned `ok`. Exact file hashes and comparison counts are in `independent_comparison.json`.

The pure evaluator also passed worker-exchange checks for all 5,184 cases; checked the bound for 2,304 cases with two complete rules; checked 32 fully serial OwnCAS cases; and matched 1,920 metadata/no-metadata pairs without a SharedEpoch worker. These checks are deterministic properties of this corpus. They are not independent statistical samples.

## Independent count derivation

There are five demand/capacity settings where either request fits alone but both together exceed the limit: `(1,1,1)`, `(1,2,2)`, `(2,1,2)`, `(2,2,2)`, and `(2,2,3)`, written as `(dA,dB,C)`.

OwnCAS/OwnCAS has four base schedules in which both reads precede the first commit. Each has six metadata variants, including no metadata update. The bound-breach count is therefore `5*4*6 = 120`.

AtomicSum/OwnCAS can fail only when the complete-check worker commits first and the weak worker retains its earlier eligible read. There are two such base schedules. Metadata does not affect either rule, so the count is `5*2*6 = 60`. Worker exchange gives the same count.

For SharedEpoch/OwnCAS with SharedEpoch at A, consider those same two base schedules. For `RA RB CA CB`, three U positions preserve A's saved epoch, and the no-U case also preserves it: four variants. For `RB RA CA CB`, four U positions plus no U preserve it: five variants. The count is `5*(4+5) = 45`. Worker exchange again preserves the result.

Every accepted AtomicSum effect directly checks the current bound. Every accepted SharedEpoch effect has an eligible earlier read and no subsequent epoch change. Because every accepted allocation and U update changes the epoch, its observed allocation sum remains valid at commit. Induction over accepted effects therefore gives zero breaches for all pairs formed only from these two complete rules. This argument depends on the full writer participation stated in the plan.

The derivations matched both the pure evaluator and the SQL traces. The largest excess is two units. A breach can first occur only on the second accepted allocation. Thus bad admissions and case-level breaches have equal counts in this corpus, although they are distinct measures.

## Source inspection after comparison

The main code uses completed autocommit SELECT statements for R events. It closes cursors and checks that no transaction remains open. C and U events use `BEGIN IMMEDIATE` and `COMMIT`. Allocation and epoch changes share that transaction. Every read and write is restricted by the case ID. The AtomicSum aggregate is also restricted by the case ID. Separate worker, metadata, and audit connections are used. These choices match the declared application-level experiment.

The same-row control checks a real stale conditional update. The held-snapshot control records SQLite error 517 and then rolls back. The rollback control tests allocation and epoch fields in one control row; the primary traces separately show the two-table allocation/epoch transactions. The experiment does not test crashes between those statements or distributed effects.

No material mismatch was found in the observed run. The metadata-scope correction is a pre-experiment plan correction, not a post-result removal of cases.

## Reproduction

Run these commands from the study folder. Use a new output folder for the main run:

```sh
python3 run_study.py --out repeat_results
python3 independent_check.py --output repeat_independent
python3 compare_independent.py --traces repeat_results/traces.jsonl.gz --database repeat_results/evidence.sqlite --logical repeat_results/logical_database.json.gz --output repeat_independent/comparison.json
```

To check the published data instead, first extract `results/evidence.sqlite.gz` to `results/evidence.sqlite` if the uncompressed file is absent. Then supply the three paths under `results/` to the comparison command. The adapter writes only its output report and opens the physical database read-only. SQLite can create temporary sidecar files when it opens a WAL database; these are not study data and do not need publication.

The comparison establishes agreement between this declared specification and these saved local SQL operations. It does not establish that a production interface exposes an atomic shared guard, that all external writers obey it, or that an AI agent will select the correct rule. No general database portability, human review, or operational safety guarantee follows from this result.
