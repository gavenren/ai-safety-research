# Frozen plan: cancellation, restart, and old worker effects

Date: 2026-10-22, America/Toronto. This is a local plan record. It is not an external preregistration.

## Question and contribution

When can a worker from a retired run still create an effect after cancellation and restart? Compare token reuse, a check-use gap, and the delay before a receiver sees a new generation. The contribution is one exact finite regression corpus and saved witnesses. Fencing, epoch numbers, cancellation barriers, and the ABA problem are established ideas. No new algorithm or production-system flaw is claimed.

## Model

One old worker holds generation 0. The controller starts active at generation 0. The receiver starts with high-water mark 0. There is one synthetic receiver and no omitted effect path.

For n in 1 through 8, the control chain is A1,R1,A2,R2,...,An,Rn. Ai is an atomic cancellation acknowledgement: set active=false and current generation=i. Ri starts the new generation: set active=true. The first cancellation permanently retires the old worker. Restarts do not grant it new authority.

Three extra events are interleaved with that chain. C checks the old worker's unique generation against the current active generation. O attempts the old worker's one effect. N attempts one effect of the final new worker with generation n. C must precede O. Rn must precede N. All other interleavings are included. Events are indivisible model steps. C remains in every schedule for a paired corpus even when a rule does not use it. The check does not itself grant permission to commit later.

For the fence rule only, Ai also advances the receiver's high-water mark to i in the same event. This models an acknowledgement issued only after the receiver barrier is installed. It is a stronger interface than a controller-only acknowledgement. It assumes no time gap between barrier and the modeled acknowledgement. No network, crash, lost acknowledgement, or physical action is simulated.

At each accepted action the receiver appends its worker label to an inert effect list. No real task or website action occurs. N is always attempted after Rn; it performs the same rule's check at commit with token n and no earlier cached check. It must be accepted in all schedules. It advances the high-water mark for either high-water rule. The study tests one delayed old worker and one current-worker control, not many simultaneous new workers.

## Seven rules

1. active_commit: at O, accept if the controller is active. This forgets which run was cancelled.
2. modulo2_commit: at O, accept if active and current generation modulo 2 equals old token 0.
3. modulo4_commit: same, modulo 4.
4. unique_precheck: C records active and current generation==0. At O, use that saved Boolean without another check.
5. unique_commit: at O, atomically check active and current generation==0 with the effect. This assumes authoritative controller state at the receiver commit boundary.
6. highwater_commit: at O, accept token 0 if it is at least the receiver high-water mark. Only accepted writes advance that mark. Cancellation does not contact the receiver. This protects against older writes after the receiver has seen a new token; it does not promise immediate cancellation enforcement.
7. cancel_fence_commit: same receiver rule, but each Ai also advances the mark. Thus cancellation acknowledgement includes the receiver barrier.

These rules use different capabilities. The comparison must state them. It is not an equal-resource performance contest or an implementation of a cited system.

## Hypotheses and scoring

For each schedule and rule record C state, O state, acceptance, effect sequence, N acceptance, and final state. An old effect is permitted only when O precedes A1. A stale effect is accepted O after A1. Also count stale effects after N, stale effects while inactive, and rejected old actions before A1. An accepted old effect after Ai remains stale even if the active flag later returns to true.

H1 active_commit has stale effects after restart. H2 modulo rules have their first stale witness at their wrap horizon (n=2 or n=4). H3 unique_precheck has a stale effect when C precedes A1 and O follows it. H4 unique_commit and cancel_fence_commit have no stale effects. H5 highwater_commit can have stale effects before N but has none after N. H6 every rule accepts N and all pre-cancellation old actions.

No result is removed if a hypothesis fails. Unexpected program, data, or file errors stop the run and remain recorded. No silent replacement. Failures with fully observed states remain valid adverse cases.

## Corpus and controls

Generate all linear extensions of the stated partial order for each n. Do not randomly sample. Save every schedule-policy result as a JSON line, including an event-by-event trace. Count schedules by n and compare with an independent insertion enumeration: insert C and O in a control chain ending with N, retaining C<O. The schedule count is choose(2n+3,2), because C and O occupy an ordered pair of positions in a length-(2n+3) sequence; all other positions hold the fixed control chain ending in N. This equality is a prediction to check, not a measured result.

Before the full corpus, check hand witnesses: old action before cancellation, old action while inactive, restart with active flag reuse, modulo-2 reuse at second restart, modulo-4 reuse at fourth restart, C before cancellation and O after it, high-water before N, high-water after N, and fence rejection after cancellation. Use direct index-based formulas, written separately from the state transition code, to check each policy result. The independent formulas still share the model assumptions and are not an independent agent review.

## Evidence, repeat procedure, and stop gate

Use Python and the standard library only. No model API, external mutation, paid compute, or connected account. Save plan/config/source hashes before implementation; save implementation hash before execution. The program takes --out DIRECTORY and refuses to overwrite existing result files. Retain inputs, code, raw traces, deterministic summaries and checks, actual environment, command, timing, and logs. A clean second run must match deterministic output files exactly. Resource gate: at most 60 process CPU seconds and 120 wall seconds per full run; at most two complete full runs before a new plan. No seed applies.

Report exact finite counts, not confidence intervals or real-world rates. No statistical independence or model-learning claim applies. Limited source search does not prove novelty. Name Codex's role and state no human review. Root will obtain a separate agent review before publication.
