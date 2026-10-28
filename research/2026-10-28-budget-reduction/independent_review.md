# Independent formula and evidence check

Date: 2026-10-28. Reviewer: a separate Codex agent. This is an AI review. No human review occurred.

## Access order and independence

The reviewer first read only `plan.md` and `plan_freeze.json`. The separate specification was frozen at 13:41:34 UTC. Its SHA-256 is `4d8f3df20b8c0b760a35846a7058905033ed3137ebba393646d1c9f43dee02fe`. The main source and main results had not been read. Expected counts were computed and saved privately.

The main agent reported its source freeze at 13:42:37 UTC. Only after that notice did this reviewer read the main source and send the expected counts. The main source was read to map its output fields, named control inputs, and SQL statements. The comparison adapter was frozen at 13:44:29 UTC, before main-output access. Its SHA-256 is `738485915480f2067ab2c6bae7212d7a33e2b4ddaf468e387876e2a5ea8950ee`.

The specification did not change after its freeze. The comparison adapter imports no main implementation. The independent counts were released before main result comparison; this was not a blind review of the final report. Both agents share the written plan and can share an incorrect assumption.

## Independent calculation

The independent evaluator calculates each record directly from the positions of completed events. It does not update a stored row or execute SQL. For a prefix ending after k events, let S_k mean that settlement S has occurred. Let B_k and U_k mean that the respective event occurred and was accepted. Each indicator is zero or one.

The expected fields are:

```text
spent(k) = s0 + x*S_k + b*B_k
hold(k) = a*(1-S_k)
cap(k) = n if U_k=1, else C0
revision(k) = S_k + B_k + U_k
```

The decision at an event uses only the prefix before that event. The saved read uses the prefix before R. This gives a finite recursion through earlier events, with no circular dependence. Future settlement cost x does not enter a decision before S.

The formulas test the five planned conditions separately. They also check that an accepted B never leaves covered use above the applied cap. Covered-use breaches can first appear only at U. Actual-use breaches can first appear only at U or S. Thus a later settlement breach is not incorrectly assigned to the complete B admission guard.

## Results

Both saved main runs passed the complete comparison without a repair. Each run had 3,888 common input histories and 19,440 rule-history cases.

| Rule | Accepted cap changes | Unsafe accepted changes | Actual-use breach cases | Feasible refused changes | Exposure with no actual breach |
| --- | ---: | ---: | ---: | ---: | ---: |
| BlindSet | 3,888 | 2,811 | 2,523 | 0 | 288 |
| SpentOnly | 1,653 | 576 | 288 | 0 | 288 |
| CachedCover | 1,095 | 219 | 189 | 201 | 30 |
| VersionedCover | 570 | 0 | 0 | 507 | 0 |
| AtomicCover | 1,077 | 0 | 0 | 0 | 0 |

Each row uses 3,888 selected histories. These are exact corpus counts, not independent samples or production failure rates. An unsafe change means that a successful reduction sets the cap below current spent use plus the outstanding hold. A feasible refusal means that the current covered use would permit the reduction. It is a cost under the numeric contract, not a failure of the revision rule's more restrictive policy.

For each main run, the comparison checked:

- All 3,888 generated inputs and their order.
- All 19,440 full primary traces, including 174,960 initial, before, and after state records and 77,760 steps.
- All 38,880 primary cap and B decisions, including every saved condition. Read snapshots, settlement outcomes, and every score field were also checked.
- All 428,776 SQL log statements in order, including caller, case, and event labels. The SQL sequence is derived from the independent decisions and the documented main schema. It is not an independent SQL engine implementation.
- All 50 summary rows and all five matched-rule comparison tables.
- All 11 first adverse examples. The check requires the first matching input in the stated order, not any example with the property.
- All 30 named control cases, with 270 state records. Both separate engine controls matched: rollback restores all changed fields, and a refused conditional write changes no row.
- All 19,471 saved final rows and the same rows read directly from each completed SQLite database. This includes primary cases, named controls, and one engine-control row. Both reopened integrity checks returned `ok`.

The two comparison outputs and logs retain these checks. Their result counts agree. The separate byte-comparison record reports that all 11 scientific files match across the two main runs. This reviewer checked that record and the run evidence; the main simulation was not rerun by this reviewer.

## Arguments and limits

Initially, covered use is at most C0. S replaces hold a with charge x<=a, so it cannot increase covered use. An accepted B tests its complete resulting covered use under the current cap. AtomicCover tests current covered use before it changes the cap. Thus all transitions preserve the bound for AtomicCover.

For VersionedCover, a matching revision means that no committed S, B, or U effect occurred after the saved read. Every such effect changes the revision. Its accepted saved check therefore also checks the current covered use. This argument requires the stated complete revision protocol and no wraparound or bypass.

SpentOnly does not test the outstanding hold. CachedCover can retain a check from before B adds use, or refuse after S returns unused capacity. Neither a safe refusal nor preservation of the old cap means that the requested lower cap became active.

This check validates the saved finite model and local database evidence. It does not establish truthful external settlement, a real provider reservation, a deployment-wide boundary, crash safety, or a production failure rate. Events are dispatched in a fixed order; this is not a parallel stress test. The cases use invented small integer inputs. No human, external peer, or production-account review was performed. The check does not establish global novelty, source rights, final report quality, or remote publication; those require separate checks.

## Repeat the comparison

From this study folder, run:

```sh
python3 compare_independent.py --results results --out independent_comparison.json
python3 compare_independent.py --results reproduced --out independent_reproduction_comparison.json
```

Both commands completed with exit code zero in this review. The second result folder is local reproduction evidence. If that folder is not included in the public package, create it with the main procedure before the second command. The README gives the complete repeat procedure.
