# Plan: mixed caller rules at one shared limit

Date: 2026-10-24, America/Toronto. Saved before implementation or experiment. The source search and design review preceded this plan. Earlier candidate designs were not run.

## Question and proposed contribution

Does one caller with a complete shared-limit check protect the whole task when another caller checks only its own row? Compare all ordered pairs of three rules using real local SQLite operations on invented data. The contribution is an exact mixed-rule corpus, per-effect audit, and paired unrelated-edit control. Shared-limit races, compare and set, and atomic checks are established mechanisms. This is not a new protocol, a SQLite defect, or a reproduction of a named prior system.

## Hypotheses and contract

H1: Own-row version checks can accept two distinct writes that exceed the shared limit while every local row and version is correct.
H2: A mixed pair with one complete check can still exceed the limit when the weak writer acts last using an earlier read.
H3: Every pair drawn only from SharedEpoch and AtomicSum preserves the limit in this corpus.
H4: An unrelated metadata write can cause SharedEpoch to refuse a currently feasible request. AtomicSum is unaffected by the metadata value.

Two workers A and B each request one allocation, demand 1 or 2 units. The capacity is 1, 2, 3, or 4. Initial allocations are both zero. Each allocation row has a version starting at zero. A separate case row holds capacity, epoch zero, and irrelevant metadata bit zero. Epoch increases with every accepted allocation and every metadata write. Each accepted allocation and its epoch increment commit in one transaction.

Only writes that keep the sum of allocations at or below capacity are authorized. This is the reference contract. A successful own-row update is not itself a claim that the shared condition is true. The experiment scores accepted effects and bound breaches, not invented natural-language completion claims. Allocations never decrease, requests never repeat, and there are no external effects, crashes, expiry, or refunds.

## Rules and events

Each worker has R (read) before C (commit attempt). R reads both allocations, capacity, epoch, and own version in one SELECT, fetches all rows, and closes the cursor. Its transaction ends before C. All three rules use the initial own version and skip C writes if the R sum plus demand already exceeds capacity.

- OwnCAS: at C, check the own-row version and zero allocation, then assign the demand. Do not check the current shared sum or epoch.
- SharedEpoch: at C, require the own-row version and zero allocation, plus the epoch observed at R. This whole check and the allocation and epoch changes are inside BEGIN IMMEDIATE / COMMIT.
- AtomicSum: at C, require the own-row version and zero allocation, plus current sum + demand <= capacity. Check and changes are inside BEGIN IMMEDIATE / COMMIT.

OwnCAS uses the same explicit write transaction boundary. All writes therefore use SQLite's serialized writer mechanism. The weakness is the application read/check outside that transaction. No policy holds a read transaction across events. A no-op C after a read denial remains in the assigned trace.

U is an optional unrelated command. It toggles the metadata bit and increments the epoch in one transaction. It does not change capacity, allocations, or row versions. Include all six orders of RA,CA,RB,CB subject to each R preceding its C. For each order, include no U and one U in each of the five positions. There are 6*(1+5)=36 schedules. Four demand pairs and four capacities give 576 scenarios. Apply all nine ordered worker-policy pairs to separate case namespaces: 5,184 case outcomes, each with two worker jobs. The no-U stratum has 96 cases per policy pair; the U stratum has 480. Do not treat their multiplicity as a probability distribution.

The implementation uses one file-backed SQLite database per full run. Case IDs partition all tables and queries. A case cannot read or change another case's state. Use separate A, B, metadata, and audit connections. Use WAL, synchronous FULL, read_uncommitted OFF, and no shared cache. Schedule operations sequentially on these connections. This exercises prescribed interleavings; it is not a random concurrent stress test or throughput benchmark.

## Evidence and measures

Retain every input schedule, demand, capacity, policy pair, read, SQL statement with parameters and returned row count/data, observed state after each event, and final state. Save the complete physical database in compressed form after checkpoint and close. Reopen it and check integrity and all final case/worker rows. Also save a deterministic logical database dump and trace data.

Report case-level bound breach (any prefix sum > capacity), accepted jobs, refused jobs, bad admissions (accepted effect whose post-sum > capacity), feasible refusals (refused effect although current pre-sum + demand <= capacity), maximum excess units, row-version errors, epoch accounting errors, reads, write attempts, and SQL refusals. A feasible refusal is a cost under this current-capacity contract, not a violation of the epoch rule itself. State which labels overlap. Preserve results by policy pair and no-U/U stratum. Do not count an expected refusal or a read denial as successful allocation.

Compare every trace outcome with a separate pure evaluator written from this plan without reading the main code. Check label symmetry under exchange of workers/demands/policies. In matched no-U/U inputs, OwnCAS and AtomicSum acceptance decisions should be unchanged; SharedEpoch may differ. Match controls by removing U from the schedule. Retain minimum adverse examples and all negative results.

## Controls before main cases

1. Same-row CAS: both callers observe version zero. The first update accepts; the stale second update is refused and does not alter the row.
2. Held-snapshot control: connection A keeps a WAL read transaction open; B commits a change. A's upgrade is rejected with SQLITE_BUSY_SNAPSHOT (517), then rolled back. This expected error is a passed engine control, not a runner failure.
3. Rollback control: a tentative allocation and epoch increment are rolled back; both remain zero.
4. Epoch/accounting check: epoch always equals accepted allocations plus completed U events in each case. Successful local allocations equal the request and have version one; refused allocations remain zero with version zero.
5. No-U fully serial schedules with OwnCAS preserve the bound. All complete-rule pairs preserve the bound in every schedule.

## Execution and decisions

Use Python's standard sqlite3 library and standard library only. No random seed is needed. No LLM invocation, network call, paid service, or connected-account mutation occurs in the experiment. Record Python, SQLite, OS, SQLite compile options, journal settings, CPU/wall time, commands, and code/data hashes.

Stop on unexpected SQL, schema, resource, or evidence failures. Save the error and partial evidence; mark unrun/unknown cases and do not replace them. A fully observed unsafe outcome is a result. Main-run limits: 5,184 cases, 120 CPU seconds, 450 wall seconds, 500 MB output. Set a CPU resource limit and check elapsed time and output size during execution. Run at most two complete main runs before final review unless a documented correction requires another run.

Publish only after hypotheses and failures are reported, the independent evaluator matches, deterministic output reproduces, the report matches raw evidence, sources and rights/privacy are checked, and a separate final reviewer passes the bounded claims. Exact corpus counts receive no sampling intervals or significance tests. There is no natural sample or learned model. The new work must not claim a production agent failure rate, general database portability, fairness, availability under retries, or safety of an external effect after a local admission.
