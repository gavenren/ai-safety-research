# Independent specification and saved-result review

Date: 2026-10-26. Reviewer: a separate Codex agent. This is AI review. No human review or external peer review is claimed.

## Decision and scope

Pass for both saved main runs under the frozen finite model. No field, decision, score, summary, or witness mismatch was found. No main implementation was imported, read, or executed by this reviewer. The first comparison adapter passed without a correction. A third main run was not made.

The reviewer read the design draft, requested three measure clarifications, and then read the final frozen plan. The clarifications define the initial-state event, the period before terminal evidence, and the comparison needed to attribute a refusal to overcount. They do not change any rule or input. The plan SHA-256 is `0058dfdedd935767a88381ffe8bc655fc2dbb536e25f0fa4f4d8a8748fcee097`.

## Independence and order of work

The independent specification uses formulas over complete report prefixes. It computes additive totals from report counts, deduplicated totals from distinct IDs, replacement totals from the last received value, and maximum totals from the set of received values. It computes the B decision once from the prefix before D. It does not call the main transition procedure.

The specification was frozen at 17:35:33 UTC, before main result access. Its SHA-256 is `13c219825ca9343074087f7390603cb95539aabd905443d64018fbe5454ec9cc`. It then ran its own 48 hand-specified control rows and complete finite enumeration. Expected headline counts were sent to the root agent after this freeze and before main execution. The main code had already been written and was not changed after those counts were sent. This is a disclosed partial separation of work, not a claim that all interpretation was blind.

After the two main runs, the reviewer read one trace and small samples of the saved input, control, witness, and summary formats. Identifier lists and check metadata were also read. The adapter only maps representation: it removes an extra independent accepted-state field, expands decision metadata, flattens metric keys, and maps summary names. It was frozen before the full comparison. Its SHA-256 is `cb089cc2f57a187016a0c7eefa4d802a9c8b4e29715b4c55e1b6c57f1f3d62bf`.

The independent code shares the written model with the main code. It can detect implementation differences, but it can still miss a common model error.

## Complete comparison

Each of the two comparisons checked:

- All 3,240 input records in the declared order.
- All 19,440 unique world/rule outcomes.
- All 85,536 event transitions and report metadata.
- All 209,952 initial, final, and event before/after state records.
- All 19,440 B decisions, including available balance, feasibility, and prior terminal status.
- All score fields, including first-bad event labels and indices.
- All 30 rule/group summary rows and all six paired-admission rows.
- All 48 named main control outcomes and the 48 separate expected control outcomes.
- All 12 saved adverse examples, including the first occurrence in the declared enumeration order.
- Input, transition, and invariant-check counts.

The state count includes repeated before/after values. These are coverage counts, not independent statistical samples. The exact evidence hashes and comparison counts are in `independent_comparison.json` and `independent_reproduction_comparison.json`.

## Supported distinctions

AddEvery and DedupSum do not admit an unsafe B in this finite model. They can still produce excess accounting, false local deficits, and refusals after sufficient final evidence. Before T, their booked use plus hold is at least R. After T, their sum includes z. This covers actual use, but it does not make the booked total correct.

DedupSum has 1,440 final overcount cases and 252 receipt-sufficient refusals. The same worlds are admitted by TerminalOnly when final evidence and actual capacity permit admission. Exact duplicate removal therefore does not solve overlap between different cumulative reports.

LastValue has 112 unsafe admissions. Its terminal flag remains true, but later P can replace z with a lower value. A sticky status alone does not preserve the amount.

HighWaterEarly has 72 unsafe admissions before T. Its final booked amount is correct in every world. Correct final bookkeeping does not undo an earlier unsafe admission.

HighWaterHeld and TerminalOnly both admit 1,953 B jobs. Their total A accounting is R before T and z after T. They have no unsafe admission, uncovered actual use, excess accounting, or local deficit. They have 207 feasible refusals before sufficient final evidence. Their identical decisions support the stated limit: progress booking does not release safe additional capacity while the residual reservation remains held.

## Limits of this review

This review covers the frozen model and both saved result sets. It does not certify production correctness or global novelty. The experiment has one fixed counter start, correct immutable reports, complete delivery, one final value, a known cap, and one additional job. Resets, corrections, conflicting reports, concurrent ledger transitions, and live provider execution are absent.

Source attribution, final prose, privacy, packaging, and remote publication require separate final checks. An exact local comparison is not proof that the files are published.
