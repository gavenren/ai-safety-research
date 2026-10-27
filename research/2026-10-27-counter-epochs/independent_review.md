# Independent method and result check

Date: 2026-10-27. Reviewer: a separate Codex agent. This is an AI review. No human review occurred in this check.

## Independence

The reviewer first read only `plan.md`. The independent code was saved and hashed at 14:32:24 UTC. Its SHA-256 is `2b3a0b635aba311e366426f3d803266b2072e58d2352664375f844dc8d56cadf`. The main code and its results had not been read at that time. The main source was then frozen at 14:33:46 UTC. Expected outcome counts were sent to the main agent only after this second freeze.

The reviewer next read the main source to map its file format and named control inputs. The comparison code was saved and hashed at 14:35:12 UTC, before the reviewer read the main results. Its SHA-256 is `06ebec615ced5f54149efe081a28d561aba81f75875d6e09170dbccd8a6b9965`. The frozen independent code did not change. The comparison code imports no main implementation.

## Independent method

The independent code calculates each state from the full prefix of delivered reports. It selects the first occurrence of each report ID. It then applies direct formulas to these distinct reports. This differs from the main code, which updates stored state after each delivery.

For a sequence of distinct delivered values, the total from the decrease rule is the last value plus the sum of all values just before a decrease. This follows by adding adjacent changes. A decrease adds back the previous value. The independent code applies this formula to arrival order or source order as required. It selects the last position or greatest value for each incarnation for the two identity-based rules.

Three separate end-state formulas were also checked for every history:

- GlobalMax error is `-min(z0,z1)`.
- SourceOrderDrop error is zero if `p1 < z0`; otherwise, it is `-z0`.
- EpochMax error is zero.

For SourceOrderDrop, the rule's booked total after the first two source reports is `z0`. If `p1 < z0`, the next report adds `p1`, and the final report adds `z1-p1`. Otherwise, the next report adds `p1-z0`, and the final report adds `z1-p1`. Thus, source order alone does not identify all resets with positive previous use.

## Results

Both saved main runs passed the full comparison. Each run had 5,184 input histories and 25,920 rule-history results. The check compared all 151,200 state records, 125,280 delivery steps, 21,600 duplicate decisions that ignored a repeated report, and 155,520 admission decisions. It also compared all 30 summary rows, five sets of matched decisions, 35 named control results, and ten first adverse examples. The example check required the first eligible history in the declared order, not just any example with an error.

| Rule | Exact totals | Totals too low | Totals too high | Decisions with excess use | Feasible refusals |
|---|---:|---:|---:|---:|---:|
| GlobalMax | 1,584 | 3,600 | 0 | 8,496 | 0 |
| ArrivalDrop | 2,806 | 1,400 | 978 | 3,276 | 2,194 |
| SourceOrderDrop | 3,888 | 1,296 | 0 | 3,024 | 0 |
| EpochLast | 2,646 | 2,538 | 0 | 6,198 | 0 |
| EpochMax | 5,184 | 0 | 0 | 0 | 0 |

Each total-count column uses 5,184 histories per rule. Each decision column uses 31,104 independent decisions per rule. A feasible refusal is a denied request whose true use would fit within the limit.

In the missing-final control, all five rules refused all requests because the closure condition was false. EpochMax recorded three units although true completed use was four units. Thus, exact final use depends on complete evidence. No main result or independent check required repair.

## Scope and limits

The check covers every input, output, control, and comparison required by the frozen computational plan. It does not verify a provider, website, live agent, or billing service. The study uses invented finite inputs. The reviewer did not make network calls or change an account. This check does not certify novelty, source quality, publication, or the full report text; these need separate checks.

The duplicate groups give different weights to distinct first-arrival orders. Their counts are properties of the declared corpus. They are not estimates of failure rates in production. Identity, source order, disjoint use, truthful reports, and complete closure evidence remain assumptions.

## Repeat this check

From the study folder, run:

```sh
python3 compare_independent.py --results results --out independent_comparison.json
python3 compare_independent.py --results reproduced --out independent_reproduction_comparison.json
```

Both commands completed with exit code zero in this review. The two JSON files retain the comparison results. The independent and adapter freeze records retain source hashes and access order.
