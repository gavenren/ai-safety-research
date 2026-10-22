# Frozen plan: safe undo order

Date: 2026-10-22, America/Toronto.

## Question and contribution

Can a greedy next-step validity check reach a dead end when a complete safe undo order exists? The contribution is an exact, small regression corpus and its measured classification. Planning through valid states and search for dead ends are established ideas. No new general algorithm or global novelty is claimed.

The earlier October 22 study tests ordered reader decisions during a two-field SQLite undo. This study tests three-field undo order under a declared state constraint. It has no database, reader job, crash, or external action.

## Model and corpus

A state has n Boolean fields. A Boolean field is zero or one. The start is all ones; the goal is all zeros. One action clears one remaining one bit. No action can set a cleared bit back to one. Fields are named a,b,c from left to right. States are stored as binary integers, with a as the most significant bit. A valid-state set includes both endpoints. Each other state can independently be included or excluded. There is one writer, full state knowledge, a correct and static validity function, and deterministic actions. Every post-action state is checked by the scoring oracle.

Primary corpus: n=3, all 64 endpoint-containing valid-state sets, all 6 permutations of field priority, and three rules. This gives 1,152 rule cases, or 384 cases per rule. Priority permutations are sensitivity controls within the full corpus, not independent real tasks. Condition ID is a six-bit mask over states 1,2,3,4,5,6 in increasing integer order. Cases are ordered by condition ID, lexicographic priority, and rule order below.

Controls: all endpoint-containing state sets for n=1 and n=2, all priorities, and all three rules. This gives 3 and 24 rule cases respectively. They are kept separate from the primary corpus. Also check the all-valid set, endpoint-only set, a single valid chain, and all field renamings.

## Rules and baseline

1. `fixed`: clear all fields in the prescribed priority. Do not check validity before execution. It always reaches the target, but can pass through invalid states.
2. `greedy`: at each step choose the first remaining field in the priority whose resulting state is valid. Commit that step. If no such step exists, stop. No backtracking or new capability is allowed.
3. `complete`: before changing state, inspect all full permutations in priority-relative lexicographic order. Choose the first path whose every state is valid. If none exists, refuse before mutation. Execute the selected path. This rule has the same single-field action capability, but performs full planning before action.

The complete planner enumerates all orders. A separate oracle uses graph reachability, without using the planner's permutation list or result. It checks whether the goal can be reached through valid states from the start and from each final state. A rule does not make a natural-language completion claim. We measure target restoration and path validity separately.

## Measures and hypotheses

Record condition, priority, rule, full state trace, actions, candidate checks, terminal status, target reached, every state valid, valid completion, partial stop, refusal before action, initial safe-path existence, final safe-path existence, and avoidable dead end. An avoidable dead end is a non-goal final state with no safe continuation, reached after at least one action when a safe path existed from the start.

H1: Fixed order reaches every target but has at least one invalid intermediate state.
H2: Greedy never enters an invalid state, but has at least one avoidable dead end in the three-bit corpus.
H3: Complete search reaches the target with a valid path exactly when the graph oracle finds an initial safe path; otherwise it refuses before action.
H4: For one and two bits, greedy has no avoidable dead end.
H5: Relabeling fields and the priority together preserves rule outcomes and relabels the state trace exactly.

Count results for each rule, condition, and priority. Save the first avoidable-dead-end witness in deterministic case order. Save its complete-path comparison. Report counts as a finite classification. There is no sampling distribution, random seed, confidence interval, population failure rate, or significance test. No trained model, dataset split, or data leakage issue is part of this model.

## Checks and resource gate

Save this plan, configuration, source search, and hashes before implementation or execution. Save the code hash before the first run. Stop on a failed assertion or unexpected exception. Preserve the error and completed evidence; do not replace cases. An observed adverse rule result is valid evidence. Code corrections must be logged, with old code hashes, before a repeat.

Use Python standard library only. Use at most 60 local CPU seconds and 120 wall seconds for each full run, and at most two full runs. First run creates original evidence. The second uses unchanged source and new output paths; compare all deterministic results byte for byte. Save actual commands, Python and platform versions, UTC stamps, monotonic elapsed time, CPU time, source hashes, and exit status. No paid service, model API, connected account, or external mutation is permitted. The parent will arrange separate agent review before publication.

## Rights and review

Inputs are all synthetic and generated by the code. Cite primary sources, without copying source code, data, images, or long passages. Do not assign a new license to the repository. Use the relevant NeurIPS checklist items as review aids. Disclose Codex's role and the absence of human review. This plan has no external registration or certification.
