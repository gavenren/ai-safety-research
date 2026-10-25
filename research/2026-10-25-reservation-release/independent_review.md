# Independent specification and evidence review

Date: 2026-10-25. Reviewer: a separate Codex agent. This is AI review. No human review or external peer review occurred.

## Review order

The reviewer first read the frozen plan. It then wrote `independent_check.py` without reading the main interpreter or its results. The independent code includes 35 expected named-control rows. The code and plan hashes were saved in `independent_freeze.json` before execution. The pure specification passed on its first run. No correction was needed.

The main interpreter uses filtered permutations and an event-by-event state update. The independent code chooses positions for A,E,T, then O,D, with F in the remaining position. It derives each prefix state directly from those positions. This supplies a different schedule generator and implementation structure.

After the pure code was frozen and run, the reviewer read the main evidence schema and selected sample records. The separate `compare_independent.py` adapter maps the specification to that schema. It imports only `independent_check.py`. Its hash was saved in `independent_adapter_freeze.json` before the complete comparison. It does not import or read the main runner.

The first complete comparison passed before the reviewer read `run_study.py`. The subsequent main-source inspection found no semantic mismatch. The unchanged adapter also passed on the second saved main run, after that source inspection. Neither independent code file was changed after its freeze. The comparison JSON fields about main-source access describe the adapter program itself; the review order in this paragraph records the reviewer's access.

## Comparison result

All 8,400 outcomes and 1,680 distinct input worlds matched. The check compared:

- All 50,400 scheduled events.
- 2,220,400 scalar values in the complete states before and after events.
- 386,400 scalar values in initial and final states.
- 176,400 case score values.
- Every saved observation, fence receipt, release decision, and B admission decision, as part of those full states.
- All 15 summary rows, including 255 numeric values.
- All 10 policy-pair rows, including 120 signed score differences and each B-decision disagreement count.
- All 35 main named-control traces and their declared expectations.
- All 12 first adverse examples in the main record order.
- Input uniqueness, world-ID consistency, and the saved property-check counts.

The independent pure evaluator also passed 35 separately specified control rows. It checked 58,800 initial/post-event bookkeeping states, 3,360 complete-rule outcomes, 4,800 ample-capacity outcomes, 2,100 fence-before-acceptance outcomes, 4,200 paired pre-resolution branch traces, and 672 terminal-before-decision worlds.

The scalar counts include repeated initial/final states and repeated evidence in later snapshots. They measure comparison coverage, not independent statistical observations. Exact file hashes and counts are in `independent_comparison.json` and `independent_reproduction_comparison.json`. Each saved run passed the same complete comparison; the table counts are not doubled by reproduction.

## Count structure

Among the 14 valid demand/capacity settings, five permit either demand alone but not both: `(a,b,C)` is `(1,1,1)`, `(1,2,2)`, `(2,1,2)`, `(2,2,2)`, or `(2,2,3)`. Eight settings have capacity at least a+b. In the remaining setting, `(1,2,1)`, B cannot fit even after A is fully released.

Only the five contentious settings can have an actual or exposure breach. The occurrence of premature release depends on the event positions and branch, not on the positive demand values. Thus each premature-release schedule has 14 numeric copies. An uncovered-liability error can occur even when spare capacity prevents a total-budget breach.

For a contentious setting, exposure breach occurs exactly when D removes a positive A hold while provider liability is positive. B then consumes the returned capacity. Actual breach additionally requires accepted A work to charge. A must precede F, the branch must charge, and D must precede T. Otherwise common terminal settlement prevents the unsafe B admission.

The position-based specification predicted the following counts before main-evidence access. The full comparison then confirmed them. Each rule has 1,680 outcomes.

| Rule | Actual breach | Exposure breach | Uncovered liability | Exposure without final actual breach | B accepted | Safe-feasible B refusal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Timeout | 130 | 200 | 560 | 70 | 1,465 | 0 |
| ZeroObservation | 105 | 175 | 490 | 70 | 1,440 | 0 |
| FenceOnly | 55 | 70 | 196 | 15 | 1,305 | 30 |
| ClosureCertificate | 0 | 0 | 0 | 0 | 1,215 | 50 |
| TerminalOnly | 0 | 0 | 0 | 0 | 1,105 | 160 |

The complete-rule argument depends on coverage. TerminalOnly retains the maximum A charge until a correct terminal result settles it. ClosureCertificate permits earlier return only from a sound proof that no A charge can remain. The acceptance fence makes a no-acceptance proof stable. A fence alone does not close already accepted work. The local B admission check is sufficient only when A's outstanding liability remains covered.

## Main-source inspection after comparison

The main code keeps the local hold and booked charges separate from actual provider charge. T records the actual result even after an early refund, so a late charge can produce a negative available balance. No outcome is silently discarded to preserve the budget claim.

The audit computes liability from provider state. It does not use a preselected future zero branch to lower unresolved liability. The rule decisions use the declared O, F, and T evidence. The B admission uses the local available-balance expression. Truth fields added to decision records are scores, not extra permission inputs.

The snapshot at F records acceptance, resolution, and charge with the fence. Certificate validity is evaluated from that snapshot. No main rule refreshes a false saved certificate after later resolution. This matches the frozen model and explains the remaining safe-feasible refusals.

The first adverse examples are the first in the fixed record order. They are not claimed to be globally minimal counterexamples. The actual-breach and final-deficit counts coincide because every final receipt arrives and both jobs have nonnegative one-off charges. This does not establish that the same labels coincide in a larger system.

## Reproduction and limits

Run this from the study folder to check saved evidence:

```sh
python3 compare_independent.py --results results --output repeat_comparison.json
```

To run the pure specification alone, use a new directory:

```sh
python3 independent_check.py --output repeat_independent
```

The pure program's internal `independent_summary.json` sums each numeric per-case score. This includes sums of per-case maxima. The published `summary.csv` instead reports the maximum across cases for its `_max` columns. The adapter explicitly checks that latter operation. These two internal summary formats must not be treated as identical tables.

The review establishes agreement between a frozen finite specification and the saved synthetic evidence. Both implementations share the written assumptions. Agreement cannot validate those assumptions or prove that a real service supplies the required certificate and settlement interface. No real provider, browser, account, or model action-selection behavior was tested. The separate final report and source reviews remain required before publication.
