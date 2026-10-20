# Independent method and result check

Date: 2026-10-20. Reviewer: a separate Codex agent. No human review occurred.

## Scope

The reviewer read the frozen plan and configuration before it wrote the audit.
The reviewer did not read or import `analyze.py`. The audit reads the saved
case rows, decision rows, summaries, and examples. It checks the finite model.
It does not certify a browser agent or a production service.

The audit uses a different candidate procedure. It enumerates full command
words, groups them by current state and word length, and then tests whether
the visible commands form an ordered subsequence. The main procedure uses an
index of subsequences. The audit computes each true target in two ways:
step-by-step replay and a formula based on the last assignment to x.

## Checks

Run `python3 independent_check.py` from this folder. The complete output is
in `independent_run.log`. Machine-readable checks are in
`results/independent_check.json`. Independent outcome counts are in
`results/independent_summary.json`.

The independent summary has 200 joint groups. Each group fixes the bound
setting, command length, missing-command count, and rule. There are 75 tight
groups, 75 loose groups, and 50 false-bound groups. None has a zero
denominator. The main summary has 170 rows for separate length, missing-count,
and other scopes. These are different group definitions. The receipt field
was changed from `summary_rows` to `independent_joint_summary_rows` to make
this distinction clear. The audit reads the saved independent summary again
to check its row count. This metadata correction did not change any result.

The audit checks:

- The complete set of 44,444 cases, with no missing or duplicate cases.
- The current state, visible log, missing-command count, and true target of
  each case.
- All 16,146 distinct observation candidate counts and target sets.
- All 64,584 saved decisions from the four rules with the same inputs.
- All 170 summary rows, including all 850 count and denominator values.
- The case total, observation totals, target-set counts, and six hypothesis
  results in the JSON summary.
- True-history inclusion in 88,888 honest-bound case settings.
- Target-set and completion monotonicity in all 44,444 cases.
- Five first examples and the four candidate words shown in the examples.
- Ten negative or boundary controls. These include invalid bounds, an
  unknown command, an impossible current state, hidden-assignment ambiguity,
  an incorrect bound that causes a false completion, and several histories
  that share one target.

Each candidate target is also checked against the saved y field. The audit
checks the full-history reference through the independently expressed
target formula.

The first examples, apart from the false-bound example, use the tight-bound
setting. A many-histories example occurs earlier if the loose-bound setting
is included. The report must state this example-selection scope.

## Proof check

The soundness claim is valid under the stated model. If the missing-command
bound is true, the actual word is one of the candidates. Its true target is
therefore in the target set. If that set has one member, that member is the
true target.

The monotonicity claim is also valid. An increase in the bound retains every
candidate that the smaller bound allowed. Thus, it retains each target.
For honest bounds, the smaller set is nonempty. If the larger target set has
one member, the smaller set must have that same member.

These arguments do not prove safety when the bound is false. They also do
not cover an incorrect visible command, an incorrect saved-state read, a
new change during undo, or a failed write. The negative bound control is
useful because it shows a direct failure when a required assumption is false.

## Limits and research claims

The contribution is a finite corpus and a reproducible comparison for this
model. Reasoning over possible histories is an established method. This
study does not establish a new general undo algorithm.

The generator supplies the bound from the actual missing-command count.
The study does not show how a website can supply a trusted bound. The
controller receives an upper bound, not a statement that exactly that
number of commands is missing.

The completion counts apply to the defined enumeration. Different deletion
masks can produce the same observation. Counts are not independent samples
from production use. Confidence intervals and claims about natural failure
rates would be inappropriate.

The command set is small. An assignment to x removes the effect of the
earlier increment. This structure makes the counterfactual targets simple.
More general programs, adaptive human actions, and side effects can have
different properties.

This review covers the frozen method and the generated results. A separate
publication review must check the final report text, sources, packaging,
and remote upload.
