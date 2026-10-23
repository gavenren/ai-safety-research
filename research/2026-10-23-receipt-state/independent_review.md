# Independent model review

Date: 2026-10-23, America/Toronto.
Status: passed for the frozen finite model and the saved main result file.

## Scope and method

A separate Codex agent read `plan.md` and `plan_freeze.json`. It did not read or import `analyze.py`. It wrote `independent_check.py` from the plan. The evaluator computes a word's final target from its last assignment, its unrelated bit from flip parity, and its revision from word length. It computes every prefix in a trace with that same closed-form rule. This differs from a state-transition loop.

The first independent run completed before the reviewer read main result rows. Its code hash and time are in `independent_freeze.json`. The root agent supplied predicted aggregate counts before that run. The reviewer checked these values from the 8/5 word partition; the review is independent of the main implementation, but was not blind to the author's predictions.

After the first independent run, the root supplied the output schema. The reviewer read sample JSONL records to implement a field-name adapter. The rule evaluator did not change. The final adapter compares the complete nested records, including types, keys, states, receipts, claims, scores, actions, and trace events. No main policy code is imported or executed by the checker.

## Results

All 338 histories and 2,028 rule outcomes matched. The comparison checked 192,566 scalar values in complete records, including 14,716 trace events. No missing or duplicate case was found. All 4,428 manual, symmetry, cost, and invalid-input checks passed. The comparison record is `independent_check.log`; the structured record is `independent_verified/execution.json`.

The checked main result SHA-256 is:

`49849726e2ff6b470d8224d0622877d653adc1059b71b31d4206ff4907c5133b`

| Rule | False positive reply claims | False negative reply claims | Extra effects | Target-value overwrites | Condition refusals |
|---|---:|---:|---:|---:|---:|
| R0 ReceiptNow | 160 | 0 | 0 | 0 | 0 |
| R1 ReadNow | 80 | 50 | 0 | 0 | 0 |
| R2 ReadDated | 0 | 0 | 0 | 0 | 0 |
| R3 ReplayNow | 160 | 0 | 0 | 0 | 0 |
| R4 NewKeyNow | 80 | 0 | 130 | 80 | 0 |
| R5 FreshCASNow | 80 | 0 | 10 | 10 | 120 |

Each row has 338 assigned histories. R2 makes no reply-state claim in all 338 histories. R5 gives an unknown reply state in 120 histories. These are not false claims. All historical claims and dated read claims are correct. No rule changes the unrelated field.

## Controls and limits

The checks cover unchanged-value writes, unrelated writes, changed values, change-and-return, no-background histories, target-label symmetry, and each rule's dispatch cost. Dispatches equal receipt hits plus accepted new writes plus condition refusals in each case. R5 evaluates a condition only after a mismatching read. Thus it can make a false reply claim after a matching read without ever invoking its condition.

The paired examples in `independent_verified/paired_examples.json` have an identical receipt or read with different later truth. Another pair has an identical mismatching read, followed by either an accepted new write or refusal after an unrelated revision change. These are selected examples from the frozen corpus, not extra trials.

The comparator does not establish that the model matches a production service. Both implementations share the plan and declared authority contract. Every extra write is unauthorized because the plan authorizes only the original effect. The model uses an ideal non-reused revision, atomic reads, and an atomic condition with its write. A browser read followed by Save does not supply those properties.

The review found no implementation discrepancy. It did not check a final report, source bibliography, publication package, remote upload, or real account state. Those checks remain with the root and source reviewer. No human or peer review occurred.

## Reproduction

From this study folder, run:

```sh
python3 independent_check.py --main-results results/results.jsonl --out independent_reproduced
```

This command uses only Python's standard library. It writes a new output directory and does not change the main evidence. Deterministic `rows.jsonl`, `summary.json`, and `paired_examples.json` should match `independent_verified`. Execution timestamps and measured CPU time can differ.
