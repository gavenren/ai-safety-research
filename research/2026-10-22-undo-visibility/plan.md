# Frozen plan: reader decisions during interrupted undo

Date: 2026-10-22, America/Toronto. Save this plan, config.json, source_review.md, and design_review.md before implementation or experiment execution.

## Question and contribution

Can a completed two-field undo leave saved reader decisions that cannot occur around one atomic undo? Can each decision pass a separate endpoint check while their ordered pair fails the joint check?

The contribution is a reproducible local SQLite regression experiment, its exact serial-decision oracle, and a comparison of final-field, separate-decision, and joint-decision checks. Isolation, compensation, read gates, and atomic transactions are established. Sagas and Atomix already discuss intermediate visibility. No new general mechanism or novelty priority is claimed. The source agent's three-field invariant corpus was not selected. The design agent's two-reader question was selected. The prior October 21 study scores final additive fields and explicitly excludes simultaneous visibility. October 19 fixes later commands and excludes conditional reader actions.

## Experiment scope

Use real temporary local SQLite files, separate connections, and actual child-process exits. The workload is synthetic. This is not a real website test, a language-model evaluation, an operating-system crash, a power-loss test, or a distributed transaction experiment. No connected account data is used. Each case has a fresh database. No email, payment, message, or other external action is sent. A saved decision or action is a local test record that undo does not delete.

The target state Q is (x,y)=(0,0). The fixture starts in P=(1,1), representing a known completed original action. Both rows must become zero. Each undo step subtracts one and saves a unique field receipt in the same SQL transaction. The receipt prevents a second subtraction. There is one undo worker and no unrelated source-field writer. Reader jobs only append to separate decision/action tables. Test both orders xy and yx.

## SQLite and schema contract

Use Python 3.13.7 and its standard library on the available macOS host. Record actual SQLite and zlib versions. Every connection uses no shared cache, read_uncommitted=0, synchronous=FULL, a five-second busy timeout, and explicit transactions. Set journal_mode=WAL during database setup and verify the returned mode. Readers and writers use BEGIN IMMEDIATE. This deliberate schedule is not a contention or throughput test.

Required logical tables: fields(name primary key, value bit); receipts(field primary key); gate(single row, closed bit); decisions(job primary key, phase, predicate, observed_x, observed_y, decision bit); actions(job primary key). The action row exists exactly when the corresponding saved decision is one. An optional table may retain refused job records, but refusals must not enter decisions/actions. All data are synthetic. Additional metadata tables must not change rule behavior. Use primary keys and bit checks. Save the actual SQL schema in schema.sql before trial execution.

The setup transaction inserts x=1, y=1, closed=0, and empty receipts/decisions/actions. No wall-clock time enters a policy. The gate-expiry sensitivity uses a deliberate forced opening, not a clock or a lease implementation.

## Three primary rules and one sensitivity

1. separate: commit each subtraction with its field receipt separately. No reader gate.
2. durable_gate: save closed=1 before the first field step. Commit each subtraction with its receipt separately. Every reader checks the same durable gate in its own read-and-decision transaction. If closed, record a refusal in the run trace and do not read source fields or append a decision/action. The gate remains closed after worker exit. Recovery opens it only in a transaction that verifies both receipts and both target fields. An extra final transaction is allowed; this leaves a conservative closed interval after the last step.
3. whole_transaction: perform both subtractions and both receipts in one SQL transaction. Readers see only committed data. This rule has a stronger transaction boundary than separate.
4. forced_open_gate, sensitivity only: same as durable_gate, but after the controlled exit the driver commits closed=0 despite incomplete undo. Readers then use the ordinary gate check. This is an intentional invalid-release intervention, not a natural timeout or provider defect.

Recovery is a new worker process. It reads receipts through a new connection. Separate rules apply missing steps in their declared order, one transaction each. Whole_transaction applies all missing steps in one transaction. Gate rules open the gate only after verifying completion. A completed step is never applied again. No recovery fault is injected.

## Worker exit and ordered reader jobs

In primary and sensitivity trials, launch a child process for the first attempt. For separate rules, the child exits with code 73 immediately after committing its first field step and receipt. For whole_transaction, it exits with code 73 after executing the first field update and receipt INSERT, but before COMMIT. Use os._exit(73) so ordinary Python cleanup is not run. Save worker stdout, stderr, return code, phase record, and measured time. Flush the phase record before exit. The parent waits for termination before any reader job. A fresh connection then records the actual stored fields, receipts, and gate for audit. This audit is not information supplied to the reader policy.

The child exit points are matched logical first-step boundaries. They are not equal commit boundaries, work, time, or failure probabilities. In particular, SQLite is expected to roll back the uncommitted whole_transaction step. Keep any contradiction as evidence.

Reader jobs 0 and 1 then run in that order. Each uses a fresh connection and one BEGIN IMMEDIATE transaction to check the gate (when applicable), read both fields coherently, compute its fixed Boolean function, and save a decision plus a synthetic action if the bit is one. Both zero and one decisions are retained. The two jobs run after the undo invocation and before recovery finishes, so both overlap the high-level undo interval. Each job completes before the next starts. A refused job is not automatically retried and is not counted as reader service.

Launch the recovery worker and require ordinary exit code zero. Read all final tables through a new connection. Then run two new post-recovery probe jobs, IDs 2 and 3, with the same respective functions. They must be accepted, observe Q, and save the corresponding decisions/actions. These are separately labelled probes, not replacements for refused primary jobs. They verify gate reopening and do not enter the primary serial score. Inspect every final table again and run PRAGMA integrity_check. Retain a logical dump and the checkpointed actual database file.

## Functions and serial oracle

Predicate IDs are integers 0 through 15. For state (x,y), output is (predicate >> (2*x+y)) & 1. Thus the truth-table order is 00,01,10,11. Predicate 12 is x; predicate 10 is y. Constants are 0 and 15.

For accepted jobs in their original order, the high-level undo can occur before all, between any two, or after all. Enumerate every such cut. At a cut k, the first k accepted jobs use P and the rest use Q. The resulting ordered bit sequence is allowed. Remove duplicate sequences. A serial violation occurs when the actual accepted sequence is absent from this set. An empty sequence is valid, but provides no reader service.

Separately, each accepted bit passes a local endpoint check when it equals its function at P or at Q. A joint-only violation is a serial violation for which every accepted bit passes that local check. The local check deliberately ignores order. Evaluate the synthetic action vector from the saved decisions, including zero decisions that produced no action. Do not infer safety from only the number of action rows. This is observational compatibility with the declared high-level operation; it is not proof of a general database history or every possible read function.

Small predeclared witness: after x-first undo, M=(0,1). Jobs with predicates 12 then 10 produce (0,1). Each bit is allowed separately, but the allowed ordered pairs are (1,1),(1,0),(0,0). Recovery can still end at Q.

## Corpus and order

Enumerate primary rules in config order. For each rule, enumerate orders xy,yx; then f=0..15; then g=0..15. This yields 512 cases per primary rule, 1,536 primary trials. Then enumerate the forced_open_gate sensitivity in the same order, 512 trials.

Serial boundary controls use whole_transaction without an injected exit. For k=0,1,2, enumerate f=0..15 and g=0..15 with order xy. Execute the whole undo after the first k reader jobs. Save the same final tables and post-recovery probes. This yields 768 actual database trials. For this control only, the oracle requires the exact known cut's outputs, rather than merely membership in the allowed set. Total scored/control databases: 2,816, with consecutive IDs starting at 1. No sampling or random seed is used.

Before scored trials, run these separate retained hand controls: truth-table identities for x, y, constants, XOR and equality; all three serial cuts for the x/y pair; the joint-only witness; a bit outside both endpoint outputs; empty accepted sequence; a reader transaction deliberately rolled back with zero saved decisions/actions; and worker exit before its first field update for each of the four rules and both orders. The gate may already be closed at that earlier exit, but all source fields and receipts must remain at P and empty. These eight process-exit controls are not scored trials. Do not silently change expected counts after results.

The design review gives pre-execution analytic predictions of 256 separate-rule serial violations and 32 joint-only violations among 512 primary cases. Label them as predictions until measured. An independent program must derive the oracle and expectations without reading main code or results. The fourth truth-table bit is not observed at the selected endpoints/partial state, so some cases are behaviorally identical. This multiplicity is retained and disclosed.

## Measures, hypotheses, and checks

Save case ID, group, rule, order, predicate IDs, exit status, post-exit audit, all reader attempt statuses, accepted primary decisions and observations, allowed serial sequences, local checks, joint score, action vector, final fields/receipts/gate, post-recovery probes, integrity status, and unknown/error reason. Preserve full logical database dumps, worker logs, and physical databases in a compressed archive. Do not publish absolute user paths or credentials. Runtime/PID data are execution evidence and may vary; logical data must reproduce.

Main measures per rule: assigned, valid, unknown; final source completion; accepted and refused primary jobs; serial-violation cases; joint-only cases; cases with a local endpoint failure; post-recovery probe success. Final completion requires Q, exactly one receipt per field, and an open gate. Claims about source completion are explicitly narrower than a clean overall decision history.

H1: all valid primary cases can reach correct final source state, including cases with an invalid earlier decision sequence. H2: separate has at least one serial violation and at least one joint-only violation. H3: whole_transaction has zero serial violations and accepts both primary jobs. H4: durable_gate has zero serial violations but refuses both primary jobs; its later probes succeed. H5: forced_open_gate has the same primary decision outcomes as separate for matched cases. H6: all serial boundary controls match their exact known cut. Retain negative or contradictory findings. No population rates, significance tests, or confidence intervals are justified for this selected complete finite corpus.

Unexpected process status, missing logs, SQL error, busy failure, unreadable database, broken schema, or failed integrity check makes a trial unknown and stops further execution. Preserve its database/logs and all earlier results. Do not replace it or call it safe. An unexpected but fully observed state/decision is a valid adverse result, not grounds for exclusion. A failed programming check must be logged with its source version before correction; reruns must be identified, with no selection of successful observations.

Independent checks: a separately written pure evaluator from this plan must generate cases and expected decisions, serial sets, local/joint scores, and summaries. Compare it to all actual logical outcomes after its implementation hash is saved. Independently inspect schema and transaction boundaries. Reopen physical databases and compare tables with saved logical dumps. Run the documented full procedure in a separate directory, compare all deterministic logical results, and retain variable execution logs separately. Use a separate content reviewer before publication.

## Resources and limits

Hard resource gate: at most 10 cumulative local CPU minutes for each full run (parent plus exited children), at most 20 wall minutes for each full run, and at most two complete full runs (initial and clean reproduction) without a new plan. Checks and source work are recorded separately. Limit trial count to 2,816 plus the declared hand controls. Stop and preserve partial work if the gate is reached. No paid compute or new model API charges.

The test excludes arbitrary crash times, multiple writers, external API effects, hardware faults, independent gate-bypassing readers, and distributed atomicity. Complete gate mediation is assumed. There is no real irreversible action. SQL decisions are conditional test records that survive this undo, not evidence of real downstream harm. SQLite serializes the individual SQL transactions as documented; a violation of our larger application contract is not a SQLite isolation defect. No human or peer review is implied. Record exact AI roles and actual review status.
