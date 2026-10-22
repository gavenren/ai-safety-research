# Independent logical review

Date: 2026-10-22. This review was produced by a separate Codex agent. No human review was done by this reviewer.

## Independence and status

The reviewer read only `plan.md`, `config.json`, and `design_review.md` before it wrote `independent.py`. It did not read the main program, SQL schema, observed results, or physical databases before it saved the implementation hash. `independent_implementation.json` records that boundary at 2026-10-22 13:42:58 UTC. The frozen evaluator hash is `7f804540181d3c739ee71fe5cf62447931f8f6e1413c034cf11183f8a650a171`.

The evaluator uses high-level schedules. It places one atomic undo before, between, or after the ordered accepted reader jobs. It computes the set of possible output sequences from these schedules. It does not copy SQL transitions or query the experiment databases. It retains zero decisions as well as one decisions. An empty accepted sequence passes the logical check but gives no reader service.

The reviewer then ran the pure evaluator. It generated 2,816 predictions in the planned order. All 13 pure control checks passed. No code correction or failed execution occurred in this pure prediction stage. Physical rollback and process-exit controls were not run by this evaluator. They must be checked in the actual database run.

The first-run comparison is complete. All 2,816 observed logical outcomes match the frozen predictions. No difference or failed comparison check occurred. The measured counts agree with the prediction table below.

## Predicted and measured first-run counts

| Group and rule | Cases | Accepted jobs | Refused jobs | Serial violations | Local failures | Joint-only violations |
|---|---:|---:|---:|---:|---:|---:|
| Primary: separate | 512 | 1,024 | 0 | 256 | 224 | 32 |
| Primary: durable gate | 512 | 0 | 1,024 | 0 | 0 | 0 |
| Primary: whole transaction | 512 | 1,024 | 0 | 0 | 0 | 0 |
| Sensitivity: forced open gate | 512 | 1,024 | 0 | 256 | 224 | 32 |
| Serial controls | 768 | 1,536 | 0 | 0 | 0 | 0 |

The model predicts complete source fields, exactly one receipt per field, an open final gate, and successful post-recovery probes in all 2,816 cases. The first run confirms all of these predictions for the declared schedule and storage setup.

## Count derivation

For one undo order, let P be the initial complete state, Q the final complete state, and M the visible intermediate state. These are three different Boolean inputs. Let the first function have outputs a at P and b at Q. Let the second function have outputs c at P and d at Q. The permitted ordered pairs are `(b,d)`, `(a,d)`, and `(a,c)`.

There are 16 endpoint assignments `(a,b,c,d)`. For each assignment, there are four possible observed pairs at M. Thus there are 64 endpoint/output combinations before the unused truth-table bits are counted.

Use endpoint types `(0,0)`, `(0,1)`, `(1,0)`, `(1,1)` for each function. The numbers of distinct permitted pairs are:

| First type / second type | 00 | 01 | 10 | 11 |
|---|---:|---:|---:|---:|
| 00 | 1 | 2 | 2 | 1 |
| 01 | 2 | 3 | 3 | 2 |
| 10 | 2 | 3 | 3 | 2 |
| 11 | 1 | 2 | 2 | 1 |

These entries sum to 32. A separate endpoint check allows the Cartesian product `{a,b} x {c,d}`. The four endpoint types have set sizes 1, 2, 2, and 1. The sum of the local set sizes over all endpoint assignments is therefore `(1+2+2+1)^2 = 36`. Each serially permitted pair is in the local set.

Each function also has one unused truth-table bit. The pair has four such settings. For one order, serial violations therefore number `(64-32)*4 = 128`; local endpoint failures number `(64-36)*4 = 112`; and joint-only violations number `(36-32)*4 = 16`. Two undo orders double these counts to 256, 224, and 32. These are exact finite-corpus counts. They are not estimates of website or agent error rates.

## Audit timing

The independent prediction names the immediate post-exit audit before the forced gate opening. Under this convention, the forced-open rule has gate 1 in that audit and gate 0 when the reader jobs start. After the predictor freeze, the reviewer inspected the runner. It uses this order and also saves a separate post-intervention audit. The timing is aligned.

## SQL inspection after the independent freeze

The reviewer read `study.py` and `schema.sql` only after it saved and ran the pure evaluator. The schema has the planned five tables, primary keys, Boolean value checks, and an action-to-decision foreign key. The connection function uses a private cache, explicit transactions, a five-second busy timeout, `read_uncommitted=0`, and `synchronous=FULL`. Setup selects WAL mode and checks its return value.

For separate undo, the value change and its receipt share one transaction for each field. For whole undo, both field steps share one transaction. The interrupted whole worker calls `os._exit(73)` before that transaction commits. The separate worker commits its first step before the same exit. The phase log is flushed first. Recovery checks receipts in its transaction and skips a completed step.

For gated undo, the gate is saved closed before either field step. Each reader checks the gate, reads both fields, and saves its decision and action in one transaction. The reader writes neither record when the gate is closed. The recovery worker reopens the gate only in a transaction that checks both target fields and both receipts. The extra closed interval is disclosed in the plan. The forced-open intervention has a separate transaction and a separate audit.

These boundaries match the plan. This is a source inspection. The physical outcome checks are separate and remain required.

## First-run evidence checks

The separate `independent_compare.py` adapter was written after the pure evaluator was frozen. It reads the runner's saved result schema but does not import the runner or its scoring functions. It checks all model-defining values against the independent predictions. These include the audit states, reader acceptance and refusal, observations, decisions, possible serial sequences, local and joint checks, saved zero and one decisions, action rows, final source state, probes, and exact serial-control cuts.

The adapter reopened all 2,825 physical databases from `physical_databases.tar.gz` in read-only mode. This number includes 2,816 scored/control databases and nine physical hand controls. It checked each database's integrity, tables, and SQL dump. Every table matched both the independent expected state and the saved logical dump. All 4,872 worker logs had the expected phase, exit status, and empty error output. The summary table, 19 hand-control records, and resource limits also passed. The adapter completed 127,899 checks with no difference. `independent_checks/independent_comparison.json` records the input hashes and each physical database hash.

The frozen pure evaluator remains unchanged. Its post-freeze comparison adapter hash is `9ca72cc401a55c59112784575cc3b3ef89539980d90851c10dae3d856c29f4c2`. The checks do not test arbitrary crash boundaries, other software versions, other writers, or real websites.

The serial score uses only the declared Boolean outputs. It does not claim that the full saved observation columns have a serial explanation. A mixed `(x,y)` observation can yield a Boolean output with an allowed serial explanation. This limit must remain explicit in the report.

## Clean reproduction

The same unchanged adapter also checked the authorized clean reproduction. All 2,816 logical cases again matched the frozen predictions. It reopened all 2,825 databases from the second archive, checked their integrity and saved dumps, and checked all 4,872 worker logs. All 127,899 checks passed with no difference. `independent_checks/clean_comparison.json` is the separate receipt. The six deterministic main result files matched the first run byte for byte, as recorded in the runner's reproduction receipt. The independent physical database hash lists also matched between the two runs.

Both complete runs therefore support the finite-corpus counts above. This is a separate AI review with a separate pure implementation. It is not human review or peer review. A separate content reviewer must still check the final report before publication.
