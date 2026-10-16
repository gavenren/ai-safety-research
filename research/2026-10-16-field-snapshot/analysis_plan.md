# Saved analysis plan

Date: October 16, 2026 (America/Toronto).
Status: Freeze before calculation. Hashes and UTC time will be in input_manifest.json.

## Question and contribution

Can repeated exact field reads confirm a target that never existed as one complete record? What do complete, reused, and incomplete revision guards change?

This is an exact synthetic state-model audit. No website, agent, language model, or user account is tested. The contribution is a fixed comparison of six checks, exact counts over a declared finite history set, and shortest counterexamples. It is not a new snapshot algorithm, a natural failure rate, or an exhaustive novelty claim. The October 15 paper checked wrong saved values in selected accounts. This study isolates concurrent field changes that its live tests did not measure.

## Model and grid

There are d required fields, where d is 2 or 3. Each field is a bit: 1 means that its saved value equals the fixed target; 0 means that it does not. The complete target is all ones. A record identity is fixed. A write flips one selected bit and takes effect atomically. Every such write has a unique position in the history. The bit flip and its revision increment occur in the same atomic event. Readers see fresh authoritative state; caches, delays, missing fields, and torn individual reads are excluded.

The scanner first reads a revision, then reads fields 0 through d-1 in order for r complete passes, then reads the final revision and makes its decision with no intervening write. r is 1, 2, or 3. In each of the r*d+1 gaps between those operations, the writer performs an ordered word of length 0 through b, where b is 0, 1, or 2. A word lists which field is flipped at each step. Repeated writes to the same field are distinct writes and can restore an earlier value. There are no extra writes before the initial revision or after the final decision in the scored interval.

Include every initial bit vector and every allowed word in every gap. Each distinct history has one count. The history count is 2^d*(sum from k=0 to b of d^k)^(r*d+1). The grid has 18 settings. These are exhaustive combinatorial counts in each finite model, not equally likely production events. The sample space changes with r and b. Do not compare fractions across those spaces as a causal benefit of extra reads.

## Six policies on the same history and decision point

- Values: every field read equals its target. Thus all repeated collected vectors are the same target vector.
- Full revision: Values plus equal initial and final revisions. The revision increments on every field write, never repeats, and is read from the same authoritative record. It starts at zero.
- Modulo 2 revision: Values plus equal initial and final total-write count modulo 2.
- Modulo 4 revision: Values plus equal initial and final total-write count modulo 4.
- Partial revision: Values plus equal initial and final counts of writes to field d-1 only. This counter does not repeat, but omits writes to the other fields.
- Atomic final snapshot: accept exactly when the entire final record is the target. This is an ideal comparison capability, not a claim about a browser screenshot or an actual service.

All policies are scored after the same final gap. This isolates evidence rules. It does not measure policy runtime or the cost of adding revision reads. The scanner has no repair or retry actions.

## Measures and decision criteria

For every setting and policy, save total histories, accepted histories, accepted histories in which the complete target never existed anywhere from the initial revision through the final revision, and accepted histories whose final state is wrong. Also save rejected histories with a correct final state. Call the two false outcomes no-common-target and wrong-at-decision. They are different; the first implies the second. Rejection has no safety declaration and is not proof of an incorrect record.

Save minimum write counts and a complete witness history for each nonempty false-outcome set. Ties use deterministic lexical order on initial bit tuples in field order, then on the tuple of gap words. Store integer counts, exact fractions when useful, and state-by-state witnesses. No confidence interval or p-value applies to exhaustive synthetic counts. State assumptions next to every guarantee.

H1: Values has a no-common-target witness for d=2, b=2, at each r=1,2,3. Its minimum write count is 2*(2*r-1). Prove the lower bound and give a matching path.
H2: A complete non-reused revision guard and the atomic final snapshot have zero false outcomes throughout the grid. Prove this under the stated atomic-write, complete-revision, and fresh-read assumptions.
H3: At least one modulo-revision setting and one partial-revision setting have a no-common-target witness. Retain a negative result if not.
H4: At least one full-revision setting rejects a correct final state. Count this cost separately from false confirmations.

## Calculation and validation

Use integer dynamic programming to merge histories only when all future outcomes and metrics are identical. Save the recurrence and state definition. Save the complete terminal count distribution for each setting, not only selected successful examples. Save stage totals, policy results, and witnesses. The main implementation must include all intermediate write states when computing whether the target ever existed.

Before release, a separate agent must derive counts without importing the main implementation. Direct brute-force enumeration must cover all settings with b=0, all d=2,r=1 settings, d=2,r=2,b=1, and d=3,r=1,b=1. Compare every policy and witness classification. Check the full grid with an independently written recurrence or generating-function method. Verify conservation, the zero-write controls, full-revision and snapshot claims, the two-field minimum-write theorem, and label/field symmetry where applicable. Test missing or malformed model input rejection. Reproduce all deterministic outputs in a fresh directory.

The report must retain failures, corrections, limitations, and AI/review status. No source paper or private data will be redistributed. No new license will be assigned. Use the relevant NeurIPS checklist items as a review aid, not as certification.
