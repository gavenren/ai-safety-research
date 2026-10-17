# Plan: repair rules and stale decisions

Date: October 17, 2026 (America/Toronto). Status: freeze this plan before execution.

## Question and contribution

Which of six repair rules can violate a current-value task contract, overwrite fields outside the task, or reject a valid write after concurrent changes?

The contribution is a small exhaustive regression corpus, exact comparisons, and minimal examples. Snapshot checks were studied on October 16. The present study includes a write and retry policy. It does not repeat that read-only model. Token replacement without new derivation and dependency validation are established ideas, including PlanFence v2. No new concurrency method or priority claim is intended. This is a synthetic model, not an agent, browser, or provider benchmark.

## State and task contract

One fixed record has four bits (A,X,Y,U) and one revision V. A=1 permits the operation now. X is a source field. Y is the field to set. U is an unrelated field. The authorized operation is: set Y to the current X, only when current A=1; preserve A, X, and U. Current means immediately before the atomic commit. This is an explicit task contract, not an inference about a real user's intent. A change that returns to an earlier value is allowed under this contract. Historical revocation is outside scope.

Initial states are all four choices A=1, X in {0,1}, Y=1-X, U in {0,1}. Initial V=0. Thus a repair is initially needed. A background write flips one of A, X, or U and increments V atomically. There are no background Y writes. Even a return to an old vector advances V. Every read returns the complete current state and V atomically and authoritatively. No caches, failed writes, deletion, identity reuse, partial writes, or hidden dependency exists.

Each assigned scenario gives K gap words. Each word is an ordered sequence of zero through b background flips on A, X, U. Each policy runs on its own copy of the same initial record and scenario. A round consists of an atomic read, optional denial at that read, that round's background word, then an atomic guarded or unguarded commit. A rejected guard advances to the next round if one remains. Success or read denial ends the policy. Unused suffix words do not run. Stop occurs at that policy's own event; there is no common final wall-clock horizon. No write occurs between guard evaluation and effect.

This is a fixed input-program comparison. Different policies can consume different prefixes. Prefixes can repeat under different unused suffixes; retain these assignments with their declared multiplicity. Report counts as corpus counts, not natural probabilities or causal speed gains.

## Six rules

Every successful rule sets Y and then stops. A successful write increments V. All rules retain record identity. None creates another record.

1. `replace`: one unguarded commit of the original full record with Y replaced by original X. A, X, U are copied from the initial read. It stops on success in round 1.
2. `patch`: one unguarded write of Y=original X only. Other fields are untouched. It stops in round 1.
3. `refresh_cas`: retain original X as the candidate Y and original permission. Each round reads the current V. It commits Y only if V still equals that round's read V. It does not recompute the candidate or recheck A at later reads. A conflict can therefore attach a fresh revision to an old decision. At most K commit attempts.
4. `replan_cas`: each round reads all fields, stops without writing if A=0, and otherwise computes candidate Y from that read X. It commits Y only when V still matches that round's read V. At most K rounds.
5. `dependency_guard`: each round reads all fields, stops if A=0, and otherwise computes candidate Y from that read X. At commit it atomically requires current A and X to equal the read A and X. It ignores U and V. Only Y is written. At most K rounds.
6. `source_only_guard`: same as dependency_guard but at commit it checks only X. It omits the permission dependency A. It still checks A at each round's initial read.

CAS means compare-and-set: comparison and write form one indivisible event. These are abstract capabilities. A client-side check followed by a separate save is not this atomic guard. Permission denials count as unresolved stops, not success. Rules do not skip a write merely because Y already equals the candidate after intervening changes.

## Grid and units

K in {1,2,3}; b in {0,1,2}. All four initial records and all K-word programs. Per gap, q=1+3+...+3^b choices. Each setting contains 4*q^K assignments. Nine settings; six policies. All are predeclared. No random seed, statistical interval, or significance test is needed for exact enumeration. No model is trained or evaluated.

## Measures

For every assigned scenario and policy, save initial state, complete input words, each consumed read/background/commit event, decision state, and result fields. A successful commit is semantically invalid if A=0 immediately before commit OR candidate Y differs from pre-commit X. A collateral overwrite occurs if the agent changes A, X, or U at commit. It is counted even if the final vector appears to satisfy Y=X. Keep these outcomes separate and give their union.

Also record success, read denial, exhausted guard retries, attempted commits, rejected guards, consumed background writes, and harmless guard rejection. A rejected guard is harmless under this contract when A=1 and candidate Y equals current X at that rejected commit point. It is a rejection of a valid Y-only effect, not necessarily a provider error.

Aggregate counts by K,b,policy. Report permission violation, source-value violation, their semantic union, collateral overwrite, and the total bad union as five distinct outcomes. For each nonempty bad outcome, keep one witness with minimum consumed background writes, then earliest round count, then lexical initial tuple and full word program. For lexical ties, encode A=0, X=1, U=2; compare tuples of these integer indices, not alphabetic text. Count each scenario once per policy. Do not pool unequal settings into a production rate.

## Hypotheses and decisions

H1: `refresh_cas` has no invalid effect when K=1, but at least one invalid effect when K>1. A strict version check alone is insufficient if a retry retains an old plan.
H2: `replan_cas` and complete `dependency_guard` have zero semantic violations and zero collateral overwrites in this finite model. Prove the conditional claim as well as testing it.
H3: `source_only_guard` has at least one permission violation despite checking X and checking permission at the earlier read.
H4: `replace` has at least one collateral overwrite that `patch` avoids for the same input. Patch can still have a semantic violation.
H5: Complete dependency guards accept some same-input assignments where replan CAS exhausts its budget due only to U writes or changes that return A/X to the read values. Count all such paired outcomes, then count two disjoint subsets. Unrelated-only: every assigned gap word is nonempty and contains only U. Returned-dependency: the first word contains A or X and has even A and X parity; every later word is nonempty and also has even A and X parity. This places an actual dependency return before the complete guard's first accepted effect. Both subsets require dependency_guard success and replan_cas exhaustion. Other paired outcomes stay outside these subsets. Do not infer population benefit.

Retain a failed hypothesis as a valid result. The tests do not prove a general real-world guarantee. Expected zero-write controls: every rule succeeds with no invalid or collateral effect. The counter may change on every write even when current task meaning returns to its old state.

## Checks and publication conditions

Save input hashes and time before execution. Use exact integer counts. A separate agent must implement the model from this plan without importing the main program, compare every result row, and review the proof and report. Include direct handcrafted examples for stale target, withdrawn permission, unrelated U conflict, X changes and returns, and full-record collateral overwrite. Validate missing/malformed configuration. Run the documented commands in a fresh directory and compare deterministic outputs. Check source metadata, attribution, secrets, relative links, and rights. Apply relevant NeurIPS checklist items. Publish only after all material issues are resolved and verify every remote Git blob. No paid compute or account mutation is needed for the analysis.
