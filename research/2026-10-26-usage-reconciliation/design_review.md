# Independent design review

Date: 2026-10-26. Reviewer: a separate Codex agent. This is AI review, not human or external peer review.

## Scope and decision

The reviewer read `plan_draft.md` before any main implementation or result. The design is suitable for the stated finite simulation. No material rule or method change is required.

All actual use of A has occurred before the delivery sequence starts. This avoids mixing a true finished charge with a forecast of possible later use. The controller cannot use the final value until T arrives. The scope must remain a delivery and accounting model, not a live provider test.

Distinct report IDs P and T are required even when their values are equal. Exact duplicate copies retain the same ID. Deduplication therefore cannot treat two equal-valued reports as one event. The planned input count is correct: 54 numeric settings and 60 distinct schedules produce 3,240 worlds and 19,440 rule outcomes. Identical copies are not artificially labelled.

The primary safety measure uses actual completed use. Final accounting error, temporary under-coverage, temporary excess accounting, and conservative refusals are separate measures. They can overlap. The report must not add them to form a total failure rate.

## Clarifications requested before freeze

1. Use event index -1 and label INITIAL for the initial state in first-bad records. Use zero-based indices for subsequent events.
2. Define before-first-T states by the sticky terminal flag being false. Include the initial state in that test.
3. Support the claim that deduplicated overcount caused a refusal with a receipt-sufficient refusal or a matched TerminalOnly admission. A generic feasible refusal can arise from an appropriate pre-T reservation.

These are reporting and comparison clarifications. They do not require an outcome-driven rule change.

## Controls and conditional checks

The eight named controls cover different cumulative totals, equal values with different IDs, an exact terminal replay, an exact progress replay, terminal arrival before progress, a zero progress value, a zero terminal value, and a decision before any report. Each control must retain all six outcomes, including unsafe and refused outcomes.

HighWaterHeld and TerminalOnly retain total A accounting R before T. After T they both retain z. Their component values can differ, but total accounting and all B decisions must agree. This equality is a useful independent check. It also sets an important limit: progress booking does not increase admission capacity when the residual reservation remains covered.

The maximum rule requires nondecreasing cumulative values from one fixed start. It is not valid without further rules for reset counters, independent increments, downward corrections, conflicting terminal reports, or multiple writers. The plan states these limits.

The independent specification will be written only after the plan freeze. It will use prefix formulas rather than the main transition implementation. Its source hash will be saved before any main code or result is read.

## Final-plan confirmation

The final plan applied all three requested clarifications before its freeze. Its SHA-256 is `0058dfdedd935767a88381ffe8bc655fc2dbb536e25f0fa4f4d8a8748fcee097`. No rule or input changed. The independent implementation and complete comparison are documented in `independent_review.md`.
