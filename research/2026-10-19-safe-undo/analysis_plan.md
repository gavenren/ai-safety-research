# Plan: Undo after later edits

Date: 2026-10-19 (America/Toronto). Save this plan and its hashes before implementation or enumeration. This is a local record, not external preregistration.

## Question and contribution

Which of six undo rules remove one agent increment while preserving later fixed commands? Which visible states require different undo results despite equal field values and revision counts?

The contribution is an exact regression corpus, paired refusal costs, complete traces, small counterexamples and an observation-equivalence test. Compensation and commuting inverses are established methods. No new compensation algorithm or novelty priority is claimed. Search began before selection. Korth, Levy and Silberschatz (VLDB 1990) give hypothetical histories that omit a canceled transaction and sufficient commuting conditions. Microsoft guidance warns that old-state restoration can erase concurrent work. Planarian is related current agent work; its isolation assumptions differ. The source record will give exact read scopes.

## Model and target

The record has integer x and bit y. Each initial x and y is 0 or 1. The agent adds 1 to x, exactly once and successfully. It has the initial record and its own post-action state. The background then executes a fixed word of length L, where L is 0 through 5. The ordered alphabet is add1, sub1, set0, set1, flip_y. The first four commands change or assign x; flip_y changes y to 1-y. Every x command increments the x revision, including an assignment of the current value. Values are unbounded integers, with no overflow or lower bound.

The reference target replays the identical background word on the initial record without the agent increment. This is a fixed-command counterfactual: it specifies an alternative execution, not how a human would react. Background commands cannot read x to select a branch or parameter. Commands do not depend on y. They do not create external effects. State-dependent decisions, copied values, constraints and multi-record invariants are excluded.

After all background commands, one rule runs once. The observation, condition and undo are one atomic event. There are no concurrent writes during undo, retries, lost replies, crashes or partial effects. Permission is assumed. Each policy gets a fresh state and the same initial record and background word. The evaluator can see the target; rules cannot inspect it.

## Six fixed rules

1. Full restore: set both fields to their initial values; report complete.
2. Field restore: set x to initial x; preserve current y; report complete.
3. Subtract: decrease current x by 1; preserve y; report complete.
4. Value guard: if current x equals initial x+1, set x to initial x and report complete. Otherwise do not change the record and abstain.
5. Revision guard: if zero background x commands occurred, set x to initial x and report complete. Otherwise do not change the record and abstain. This uses a complete, non-reused revision for x; y changes do not block it.
6. Provenance control: retain a trusted bit that starts true after the agent action and becomes false at any set0 or set1. If true, subtract 1 from x; if false, make no change. Report complete in both cases. This requires complete operation-type history or equivalent atomic provenance. It is an ideal semantic control, not a capability supplied by a normal browser field read.

## Corpus and measures

Enumerate all four initial records and all five-command words for every L. There is one case per unique initial record and word. No random sample, training or parameter fitting. Do not interpret the equal enumeration weights as natural probabilities.

For each case save: initial record; word; all actual and reference states; x revision count; provenance bit; pre-undo state; reference target; each rule's status and final state. Save aggregate results separately by L and rule. Also save subgroups with/without a set command. All counts are exact integers.

Correct final means the complete final record equals the reference target. False confirmation means the rule reports complete but the final record is wrong. Wrong change means the rule changes the record and leaves a wrong final record. Collateral change means final y differs from pre-undo y. New damage means the pre-undo record already equaled the target, but the final record does not. Unresolved means the rule abstains and the final record is wrong. Abstain-correct means the rule abstains with a correct final record. Clean completion means the rule reports complete and the final record is correct. Clean completion, false confirmation, unresolved and abstain-correct partition all cases. Other labels overlap and must not be summed as disjoint outcomes.

For each weaker rule, count cases where the provenance control completes correctly but the rule abstains, separately for correct and incorrect pre-undo records. This measures missed completion or confirmation in this model, not latency or general availability.

Group histories by (L, initial x, initial y, current x, current y, x revision count). A group is ambiguous when its reference targets differ. Save all group sizes and target counts. These observations even include the history length and a complete x revision count. Save one minimum pair of histories in each ambiguous group. A deterministic rule that sees only the group key must choose the same action in both histories, so it cannot always complete with a correct target when targets differ. Abstention can avoid an unsupported completion claim. Do not extend this information limit to agents that have operation history.

## Minimum examples

Order histories by (L, initial x, initial y, alphabet-index tuple). Save the first history for each rule and each nonempty failure label: false confirmation, wrong change, collateral change, new damage, unresolved, abstain-correct. For ambiguous groups, choose the first history and the first later history with a different target. Select the global first pair by the same history order. Do not remove repeated or successful cases.

## Hypotheses and decisions

- H1: Full restore and Field restore each have at least one false confirmation. Full restore also has collateral change.
- H2: Subtract is correct for every no-set word, and wrong for every word with a set.
- H3: Value guard has at least one false confirmation, including a case with new damage.
- H4: Revision guard has zero false confirmations and wrong changes, but abstains on at least one case that Provenance control completes correctly.
- H5: Provenance control completes correctly in every case.
- H6: At least one observation group has multiple reference targets.

Report all six decisions. A failed hypothesis is a result; do not revise inputs to make it pass. The planned main table is L=3. Also report totals and the first ambiguity pair. No statistical significance test or confidence interval applies to complete enumeration of this finite corpus. Generalization beyond it remains unmeasured.

## Controls and validation

Check all no-background histories. Check y-only words. Check each one-command word, including same-value assignment. Check an add/sub cancellation and a set followed by an addition. Derive count identities from alphabet sizes. Check that y always agrees between the actual and reference worlds. Their x difference must be 1 without a set and 0 after a set. Check the outcome partition, policy field preservation, and input rejection.

A separate agent will implement the model from this plan without reading the main code. Compare all case outcomes, trajectories, aggregates, paired counts and ambiguity results. Run documented commands in a fresh directory. Inspect source claims, reproducibility, limits, privacy, rights, copied text and local links before publication. Use the relevant NeurIPS checklist items as a review aid. Record every failed check and correction. Do not publish while a material error remains.

## Ethics and disclosure

Use synthetic data and local standard-library Python only. No private account data, paid service, live website experiment or external code is needed. No new license will be assigned. Codex generates the study, code and report; separate agents check it. State that no human or peer review occurred. The study does not authorize automated undo of real user work.
