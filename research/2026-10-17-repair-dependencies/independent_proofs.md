# Independent checks and conditional proofs

Date: October 17, 2026. This is an automated review by a separate Codex agent. It is not human review or peer review.

The reviewer read the frozen plan and configuration. The reviewer did not read, import, or call the main program before deriving the independent implementation. The independent program directly visits every assigned scenario. It uses a four-element state list and an integer revision. It saves the five bad outcomes, policy stopping points, aggregate counts, and selected witnesses.

## Preconditions

The claims below use the exact task contract in `analysis_plan.md`. Each read returns the whole current record. Each background write changes one bit and its revision in the same indivisible event. The guard and the agent's effect are also one indivisible event. The revision does not repeat. The only dependencies are permission A and source X. The authorized effect changes Y only. These are model assumptions, not facts about a website.

## Correctness of the two complete rules

For `replan_cas`, a round first reads A and X. It denies the operation if A=0. Otherwise it chooses Y from that read X. Any background write in the gap increases the revision. Thus the revision guard can pass only when that gap has no background writes. At commit, A is still 1 and X is still the value used for Y. The effect changes Y only. Therefore a successful commit has neither a semantic violation nor a collateral overwrite.

For `dependency_guard`, the read also requires A=1 and derives Y from read X. The atomic guard requires current A and X to equal those read values. Thus A=1 and candidate Y=current X immediately before the effect. Changes to U and changes which return A or X do not invalidate this current-value contract. The effect changes Y only. Therefore the same two bad outcomes are absent. This proof does not cover historical revocation, an omitted dependency, or a separate client-side check followed by a save.

## Failures of incomplete rules

A first-round `refresh_cas` success has no background writes in its only gap. The original permission and source are therefore valid. This explains its zero semantic violations at K=1. With a second attempt, the first gap can flip X and cause a rejected guard. An empty second gap permits the fresh revision to pass, although candidate Y still comes from the initial X. A corresponding flip of A gives a permission violation. One background write is necessary and sufficient for each witness, with two rounds. No failure exists in a zero-write setting.

`source_only_guard` can read A=1, then receive a single A flip in the gap. X is unchanged, so its guard passes. The permission at commit is 0. The rule cannot have a source-value violation in this model because its guard checks exactly the source used for the candidate. The permission check at the earlier read does not cover an intervening permission change.

A one-bit background change to U is enough for `replace` to restore old U at commit. `patch` leaves U unchanged on the same input. A change to A or X before either unguarded rule's commit can violate the task contract. The replacement can make the final state appear correct by restoring old A and X. This does not remove its violation, because the contract is evaluated immediately before the effect.

## Independent counting checks

There are q=sum(3^j, j=0..b) words per gap and four initial records. Each setting therefore has 4*q^K assignments. Each policy receives every full program even if it stops before its suffix. These suffixes are distinct assignments. This is a corpus convention, not a claim that each program is equally likely outside the model.

For b=2, q=13. Exactly nine first-gap words change at least one of A, X, or U at the unguarded commit. Thus the replacement has 4*9*13^(K-1) collateral assignments. Exactly eight words change A or X at that point. Thus both unguarded rules have 4*8*13^(K-1) semantic violations. These formulas reproduce the independent results at K=1,2,3.

For b=1, the unrelated-only H5 subset has one possible word, U, in every gap. Its count is four for each K. For b=2, the allowed unrelated-only words are U and UU. Its count is 4*2^K. The returned-dependency subset has AA or XX in the first gap. Each later gap can be U, AA, XX, or UU. Its count is 4*2*4^(K-1). These subsets are disjoint. Both have complete-guard success in round 1 and replan-CAS exhaustion after K rejected guards. All of their rejected CAS effects are valid under the stated current-value contract. Other paired outcomes are reported separately.

## Test scope

The independent program has ten handcrafted controls. They include stale source, stale permission, read denial before a gap, replacement collateral, an unrelated-field conflict, a return to an earlier source value, omitted permission, revision increments on return, unused suffixes, and the first-word condition for H5.

It rejects 27 malformed configurations. It also checks 118,368 transformed policy rows. The transformations complement X and Y together, or complement U. These transformations preserve all decisions, work counts, and bad-outcome flags. The final state changes by the same complement.

The independent comparison passed for all 59,184 policy-scenario rows and all 379,596 recorded events. It also passed for all 54 aggregate rows, 756 aggregate scalar values, nine paired rows, and 88 minimal witnesses. The comparison includes the full witness traces and the lexical tie rule. `independent_comparison.json` records hashes of the checked inputs and outputs.

Repeat the check from the study folder with `python3 independent_audit.py --input-dir . --output-dir . --compare-main .`. Independent software can still share conceptual mistakes with the plan. These checks do not measure live systems or establish a general rate of failure.
