# Design review: visible intermediate undo and durable reader actions

Date: 2026-10-22. This is a design proposal. No experiment was run for this review.

## Prior-work boundary in this repository

I read the October 17 repair report, the October 19 improved undo report, and the October 21 crash report.

- October 17 tests whether the inputs to a later write are still valid. Its main oracle uses the state immediately before that write.
- October 19 removes one increment and preserves a fixed sequence of later commands. The synthetic method excludes conditional branches, copied values, external effects, and multi-record constraints.
- October 21 tests per-field effects and progress records. All fields are scored at a common final horizon. Its derivation explicitly does not establish simultaneous visibility of the two undo steps.

The useful next boundary is a reader that observes part of an undo and records a decision that survives recovery. Correct final source fields cannot remove that decision. This is a change in the safety contract, not a new name for the October 21 final-state check.

## Suggested question

Can a correctly completed two-step undo leave durable reader decisions that cannot occur around one atomic undo? Which storage and reader rules prevent this result, and how many reader requests must they refuse?

The most useful extra measure is a decision sequence that passes every separate endpoint check but fails a joint serial-order check. An endpoint is the complete state before or after undo. This measure detects more than an invalid intermediate invariant.

## Recommended experiment type

Use a small actual local SQLite experiment. Use temporary database files and separate connections. Do not call it a website test or a language-model trial. Do not claim a new compensation or isolation algorithm. The contribution can be the checked regression package, the serial trace oracle, the failure examples, and the comparison of final-state and action-trace checks.

Use a controlled worker exit at a declared SQL boundary. It is a process-exit test, not a machine crash, power-loss test, or test of arbitrary kill times. The SQLite version, journal mode, synchronization mode, operating system, commands, child exit status, and fresh-connection checks must be recorded.

## Small state and task

Use two bit fields x and y. The primary initial target is (0,0). A completed original action changed them to (1,1). Undo must toggle each field once to restore (0,0). The two field receipts start false. The initial action is a fixture, not an uncertain action under test.

Test both undo orders: x then y, and y then x. Every field change and its receipt belong to the same SQL transaction. There is one undo worker, no unrelated writer, no receipt expiry, no identity reuse, and no lost command replies. These exclusions isolate visibility from the failure modes already tested on October 21.

The database also contains a reader decision table. For each reader job, save the reader ID, predicate ID, observed x and y, decision bit, and refusal status. A separate action table can receive one synthetic action record when the decision is 1. No email, payment, message, or external action is sent. A false decision is still an observed outcome, so it must remain in the decision table even when it creates no action row.

## Reader jobs and exact serial oracle

Two reader jobs run in a fixed order after the controlled worker exit and before recovery. Each uses a new connection and one transaction for its coherent source read and durable decision/action write. Use an explicit transaction mode and document it. With the writer already exited, this need not depend on a timeout race.

Each job uses one Boolean predicate of x and y. There are exactly 16 predicates on two bits. Encode a predicate by a four-bit truth table with a frozen input order, for example (0,0), (0,1), (1,0), (1,1). Enumerate all 16 choices for each job. The functions are fixed programs. A language model does not select or execute them.

Let P be the complete pre-undo state and Q the complete post-undo state. Let the two predicates be f and g. Both reader jobs overlap the high-level undo interval. Their response order is fixed. An atomic undo permits only these decision pairs:

1. (f(P), g(P)): both readers occur before the atomic undo.
2. (f(P), g(Q)): the undo occurs between the readers.
3. (f(Q), g(Q)): both readers occur after the undo.

Remove duplicate pairs before a membership check. A decision trace is serially valid if it is in this set. This oracle is about the declared high-level operation and fixed reader order. It is not a claim that all possible database transactions or real-world effects have this contract.

A refused reader contributes no source decision and no action. Apply the same oracle to the ordered subsequence of accepted readers. Record refusals separately. A rule that refuses both readers is safe for this trace contract but provides no reader service during the interval.

Also check each accepted decision separately against its two endpoint values. This weaker check can pass while the serial trace check fails.

### Small joint failure example

P=(1,1), Q=(0,0). The x-first step commits, so the intermediate state is (0,1). Reader 1 returns x, so its result is 0. Reader 2 returns y, so its result is 1. Each result is possible at an endpoint. But the pair (0,1) is not among (1,1), (1,0), and (0,0). There is no single atomic undo point that explains both responses in order. Recovery can later restore (0,0) without removing the reader decisions.

## Three primary storage rules

### Separate commits

Commit the first field change and its receipt. Exit before the second field step. Readers see the saved intermediate state and can record decisions. Recovery skips the completed receipt and applies the remaining field change. Both receipts and final fields must pass the final check.

### Separate commits with a durable reader gate

Persist a closed gate before the first field step. Commit each field change with its receipt. Keep the gate closed across worker exit. Readers check the gate in the same transaction as their source read and action write. A closed gate produces a recorded refusal and no action. Recovery applies remaining steps and opens the gate only with verified completion. Prefer to open it in the same transaction as the last step, or state the separate final transition precisely.

This rule needs every tested reader to obey the gate. A client-local flag does not isolate other clients. The method should not imply that the gate is a native feature of a website or that a database automatically enforces an application flag.

### One transaction for the whole undo

Start one transaction for both field changes and both receipts. Execute the first field change and its receipt statement, then exit before commit. SQLite must roll back that uncommitted transaction. The reader jobs should observe the complete pre-undo state. Recovery runs the complete undo transaction. This is an ideal storage control with a stronger transaction boundary.

The exit points are matched logical first-step boundaries. They are not equal instruction counts, equal transaction costs, or equal failure hazards. State this difference in the paper.

## Optional gate-expiry sensitivity

Add an explicitly separate rule that treats an expired gate as open even though one receipt is missing. A test-controlled logical clock can reach the fixed expiry before the reader jobs. This should expose the same partial state as the separate-commit rule.

This is a counterexample to expiry without recovery proof. Do not describe it as a natural clock failure, an implementation of a lease service, or an estimate of timeout frequency. Keep it out of the primary comparison if its extra mechanism distracts from the core question.

## Corpus and controls

Recommended primary corpus: one target (0,0), two undo orders, 16 choices of f, and 16 choices of g. This gives 512 assigned cases per rule, or 1,536 cases for the three primary rules. Each assigned case has a fresh database file. Use deterministic case IDs and execution order. A separate gate-expiry sensitivity would add 512 cases.

All three other bit targets can be covered with a smaller declared check set, such as the predicates x, y, x XOR y, and x equals y. This gives 3 targets * 2 orders * 4 * 4 = 96 cases per rule. The full truth-table primary set has a coordinate-relabel symmetry, but the physical extra-target controls still help catch encoding errors. They are selected controls, not additional natural tasks.

Other mandatory controls should be fixed before the run:

- Reader jobs before undo starts: every accepted result uses P.
- Reader jobs after a complete undo: every accepted result uses Q; the gate must be open.
- Constant predicates: no source-state disagreement can change their outputs.
- A worker exit before any undo mutation: no partial field state may be visible.
- A reader transaction that is rolled back: no durable decision or action row may remain.
- A failed or unexpected worker exit, missing receipt, busy error, or invalid saved bit: mark the trial invalid or unknown. Do not replace it silently.

Do not count a database read, successful SQL call, or child exit code alone as proof of the final stored result. Use a new connection to inspect fields, receipts, gate, decisions, and action rows.

## Planned measures and decisions

Keep the following measures separate:

- Final source-state and receipt correctness.
- Number of accepted reader jobs and refused reader jobs.
- Cases with a serially invalid accepted decision trace.
- Cases with a serially invalid trace although all separate endpoint checks pass.
- Cases with a decision bit outside both endpoint outputs.
- Durable synthetic action rows that cannot be explained by any permitted serial trace.
- Unknown or invalid trials, with their exact cause.

The primary decision criteria can be:

1. Every valid trial reaches the declared final undo state after recovery.
2. Separate commits have at least one serially invalid durable decision trace despite correct final fields.
3. At least one such trace passes both separate endpoint checks.
4. The whole-undo transaction has no serial violation in valid trials and accepts both jobs.
5. The durable-gate rule has no serial violation, but refuses both jobs at the primary interruption point.
6. All pre-undo, post-undo, and constant-predicate controls meet their declared reference.

If a criterion fails, retain that result and inspect whether the model, implementation, or storage assumption failed. Do not redefine the corpus to force the expected answer.

## Optional analytic count checks, not measured results

With all truth tables, a fixed partial state M differs from both endpoints. For one undo order, there are 256 predicate pairs. The serially valid decision sets have total size 32 over the 16 endpoint-output assignments, out of 64 possible endpoint/output combinations. Thus the ideal exposed-partial-state model predicts 128 invalid pairs per order, or 256 of 512 primary cases. Of those, 16 per order pass both separate endpoint checks, giving 32 of 512 cases.

These are predictions for the stated truth-table corpus. They are not actual SQLite measurements. A separate implementation should derive and check them without importing the main evaluator. The fourth unused truth-table bit produces multiplicity; it is not an extra independent observation.

## Limits and release advice

The basic isolation result is established prior work. The source review must position the package against compensation, database isolation, transactional outbox, and current agent recovery studies. Do not claim a new theorem or a general safety method from these cases.

This test adds actual transaction and process-exit evidence, but the workload remains synthetic. It excludes operating-system failure, hardware failure, multiple recovery workers, arbitrary external clients, adaptive users, stale replicas, native remote API behavior, and real irreversible effects. All counts describe selected deterministic cases. There is no justified population error rate, confidence interval, or performance claim.

Set a small resource limit before execution, for example ten local CPU minutes and a fixed maximum of 3,000 primary/sensitivity database trials. If full synchronization or process startup makes the plan exceed the limit, preserve partial results and report them. Do not silently reduce synchronization strength or change the trial set after seeing results.

This design is ready for source critique and final specification. The parent should freeze the exact schema, transaction boundaries, gate policy, truth-table order, control cases, trial order, and unknown-result rules before implementation.
