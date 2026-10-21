# Frozen analysis plan: undo after a crash

Run date: 2026-10-21, America/Toronto.
Status: save this plan, config.json, and source_search.md before model execution.
Question: Which progress-record rules can undo two completed increments after crashes, without removing later additive edits or making false completion claims?

## Contribution and prior work

The contribution is a fully enumerated regression corpus and exact comparison of seven fixed rules. Durable undo records, atomic effect records, idempotent operations, and compensation fault tests are established. RIFL and current UndoBench are close prior work. No new general recovery algorithm or global novelty claim is proposed. The October 18--20 repository studies assume atomic execution at the boundary studied here. The search record gives source dates, checked sections, and limits.

## State and reference

There are two unbounded integer fields, x and y. Each initial value is 0 or 1. A completed original agent action adds one to both fields. Every rule starts at initial + (1,1), with both durable done flags false. The desired undo removes those two increments while preserving all scheduled external additions. External commands are x_add1, x_sub1, y_add1, y_sub1. They add or subtract one. The reference final state is initial plus the sum of all external commands. This is an evaluator calculation; controllers do not read the future command list.

The assignment rules cache the initial values before the original action. They always assign those fixed values. All reads and writes are exact. Flags are durable, uncorrupted, unique to this task, and never expire. No other recovery worker exists. External commands never assign an absolute value. These additive commands commute with inverse subtraction. The model does not apply to arbitrary later commands.

## Attempts and crashes

Each attempt has four logical slots. Slots 1 and 2 concern x; slots 3 and 4 concern y. A cut c in {0,1,2,3,4} executes the first c slots, then crashes. Cut 0 is before any slot. Cut 4 is after all slots but before a final completion audit. For each interrupted attempt, the crash clears volatile pending flags. The assigned external word then runs. After all interrupted attempts, a final attempt runs all four slots without a crash. It has no later external word. The completion claim is evaluated only at this final horizon.

Atomic and unmarked rules have padding slots. Equal cuts are matched logical interventions, not equal time or equal instructions. Retain repeated prefixes caused by padding. The same external words run for every rule, including after all undo steps completed and after a rule stops. No case can end early. Durable refusal in stop_on_uncertainty prevents all undo work after the first crash. A recovery without another fault is an explicit assumption.

## Seven rules

For each field, call its first slot A and its second slot B. A volatile pending flag starts false on each attempt.

1. restart_inverse: A subtracts one, with no flag; B does nothing. Claim completion at the final horizon.
2. before_inverse: if done is false at A, set pending and durable done true. At B, subtract one if pending. A saved intent is incorrectly treated as completion by this baseline. Claim only if both done flags are true.
3. after_inverse: if done is false at A, set pending and subtract one. At B, set done true if pending. Claim only if both flags are true.
4. after_set: same slots as after_inverse, but assign the cached initial value instead of subtracting one. Claim only if both flags are true.
5. stop_on_uncertainty: use after_inverse until the first crash. Then keep a durable stopped flag and do no more undo work. At the final horizon, claim only if both done flags are true. Otherwise refuse. With no crash, finish the ordinary after_inverse attempt.
6. atomic_inverse: if done is false at A, subtract one and set done true in one indivisible durable transition. B does nothing. Claim only if both flags are true.
7. atomic_set: same atomic transition as atomic_inverse, but assign the cached initial value. Claim only if both flags are true.

Atomic rules have a stronger server capability. A local client record cannot provide this capability for an unrelated website. Per-field atomicity is not all-or-nothing visibility of both fields.

## Corpus and order

Enumerate settings in this order: no_fault (zero crashes, no words); one_crash (one crash, external word length 0 through 2); two_crashes (two crashes, each external word length 0 through 1). Initial pairs use lexicographic order over {0,1} squared. Cuts use lexicographic product order over 0 through 4. Words use length-first order, then the alphabet order in config.json. Iterate settings, initial pairs, cut tuples, then word-index tuples. Assign consecutive case IDs from 1. Run rules in config order.

Expected design sizes, not observed results: 4 no-fault cases; 4*5*(1+4+16)=420 one-crash cases; 4*25*25=2500 two-crash cases. Total 2924 cases and 20468 rule outcomes. The two-crash setting is primary. The no-external-edit subset is a planned control. The one-crash setting with up to two external commands is a planned sensitivity analysis, including edits that cancel. No seed is needed: all cases are enumerated.

## Measures and decision criteria

For every case and rule, retain final fields, done flags, stopped flag, claim, and the full trajectory. Count applied undo commands per field, including an assignment that leaves the value unchanged. Separately count commands that change the value. These are neither network invocation counts nor semantic effect counts. Repeated step means an application count above one; omitted step means a count below one. Record total applications and value changes as work measures, with no time interpretation.

Correct state means exact equality to the reference. Classify each outcome into correct completion, false completion, refusal with correct state, or refusal with incorrect state. Also report repeated steps, omitted steps, and command counts. State correctness and once-only application are separate measures. Summarize each setting, and each setting's no-external-edit subset. Save the first case in enumeration order for each rule and each nonempty outcome category as a reproducible witness. Save paired outcome counts against atomic_inverse.

Hypotheses: H1 restart_inverse and after_inverse have false completions with repeated steps. H2 before_inverse has false completions with omitted steps. H3 after_set has no false completion without external edits, but has false completions with them. H4 atomic_set can falsely complete with exactly one application per field. H5 atomic_inverse always completes correctly and applies each step exactly once. H6 stop_on_uncertainty has no false completion, but has fewer correct completions than atomic_inverse and some refusals with a correct state. Each claim is evaluated by exact counts in its declared finite set; retain contradictions. There are no estimated population rates, significance tests, or confidence intervals. Case fractions reflect the declared enumeration and artificial padding multiplicity.

## Checks and limits

Use hand-checked cases for both marker-order faults, repeated subtraction, assignments that remove later edits, atomic recovery, and refusal after an unmarked completed effect. A separate agent must build an independent evaluator from this plan before inspecting main code or outputs. Compare every case/rule final state, flags, counts, and classification. Check inverse state errors by the independent identity final-reference=(1-count_x,1-count_y). Check all corpus counts and distinct IDs. Run all documented commands in a clean output directory and compare deterministic result bytes. Review report claims and sources with a separate agent.

No training, model evaluation, data split, leakage, people, account records, websites, or external data are part of this experiment. All inputs are synthetic. No performance estimate for a real computer-use agent is allowed. No general protocol correctness claim follows from the finite corpus. Record changes, errors, and failed checks in deviations.md. Use at most ten local CPU minutes for model execution and checks; stop and preserve work if exceeded. No paid compute or new API charges.
