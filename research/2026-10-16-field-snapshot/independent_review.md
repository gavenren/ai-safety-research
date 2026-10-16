# Independent numerical and logical review

Date: October 16, 2026 (America/Toronto).
Status: PASS for the finite model and files named in `independent_comparison.json`.

## Work done

A separate Codex agent reviewed the plan before the calculation. It asked for two explicit premises: each atomic flip includes the revision update, and no write occurs between the last revision read and the decision. Both premises are in the frozen plan. The agent checked the frozen manifest hash and all three input file hashes before comparing results.

The agent wrote `independent_audit.py` from the plan. It did not read, import, or call the main calculation code. It completed its 18-setting result before it read the main data files. It then wrote `independent_compare.py`, which reads those files as data. Both calculations use exact integers and the declared state recurrence. Independence of implementation is not independence of the common mathematical model.

## Exact comparisons

All checks passed:

- 108 policy rows and 756 numeric or null values agree.
- All 13,744 terminal state counts agree.
- All 108 stage totals and merged-state counts agree.
- All 71 nonempty false-outcome sets have the same minimum-write witness. Initial states, all gap words, lexical tie choices, and all event states agree.
- Direct enumeration agrees with the independent recurrence in all 10 required small settings. This includes every zero-write setting, every two-field one-pass setting, two fields with two passes and one write per gap, and three fields with one pass and one write per gap. The complete distributions and the lexical path retained for every terminal state agree.
- 34,720 small-history transformations preserve results. These checks move field labels, read order, and the partial counter's covered field together. They also exchange the all-one and all-zero target coding. They do not claim that a changed read order alone has the same result.
- The independent input validator rejects 28 missing, extra, or malformed model inputs. This checks the independent validator. It is not a substitute for tests of the main validator.
- Every stage count equals `2^d * q^g`, where `q` is the number of allowed gap words and `g` is the number of completed gaps.

The programs, the full independent distributions, and the comparison receipt are included. They use only the Python standard library. The receipt records file hashes. No random sample, network service, user account, or paid model call is part of this calculation.

## Proof checks

### Complete revision

Each write adds one to a counter that starts at zero. The counter does not wrap or reset. Its update and the field flip form one atomic event. Equal first and last revisions therefore imply zero writes in the guarded interval. All field reads then see one constant record. If all required reads are one, that record is the complete target. The final revision read and decision share one atomic event in this model, so the record is also correct at the decision.

This rule accepts exactly one history per setting: the initially correct record with an empty word in every gap. The result is safe but conservative. It is not an algorithm that guarantees completion under continuing writes. It says nothing about a later claim after a new, unguarded gap.

### Atomic final snapshot

The policy accepts only when the full record at the decision is the target. It cannot accept a wrong final record or a target that never existed. For any fixed sequence of gap words, bit flips map initial vectors bijectively to final vectors. Exactly one of the `2^d` initial vectors ends at the target. Thus it accepts `total_histories / 2^d` histories. This capability is an ideal control, not a browser screenshot or a measured provider feature.

### Two-field lower bound

For two fields, no-common-target means that the state `(1,1)` is absent at every write and read state. A target-valued read of field zero must therefore occur in `(1,0)`. A target-valued read of field one must occur in `(0,1)`. Consecutive reads alternate these states. Each of the `2r-1` intervals between reads needs at least two flips. The intermediate state must avoid `(1,1)`; a path through `(0,0)` meets the bound. The gap bound `b=2` permits this path. Empty initial and final gap words add no writes. The exact minimum is `2(2r-1)`, or 2, 6, and 10 writes for the three tested pass counts.

This is a lower bound for no-common-target histories with target-valued reads. It is not a lower bound for wrong-at-decision histories. One final flip can make a previously correct record wrong at the decision.

### Reused and partial revisions

A modulo counter can return to zero after a nonzero number of writes. It cannot support the complete-revision proof. A partial counter equal to zero only rules out writes to its covered field. It does not rule out other flips.

For two fields, the partial counter's no-common-target count is zero in this model. To accept, its last field must be read as one. No covered-field write can occur, so that field remains one for the whole interval. A target-valued read of the other field then supplies a time when both are one. This argument does not extend to three fields: two uncovered fields can alternate their correct values while the covered field stays one. The result files retain both the zero and nonzero settings.

### Distinct error measures

If the target never existed anywhere in the scored interval, it is also absent at the final decision. Thus no-common-target is a subset of wrong-at-decision. The reverse implication is false. A correct initial target followed by one late flip gives a wrong final state even though the target existed earlier. The results and witnesses keep these outcomes separate.

## Limits and contribution

These are exact counts over selected finite history sets. The sets change with the number of reads and the gap bound. Their fractions are not estimates of production event probabilities. Comparing those fractions across settings is not a causal estimate of an extra scan's benefit.

For example, Values has 16 no-common-target histories in each of the two-field, two-writes-per-gap settings for one, two, and three passes. Their minimum write counts differ, and their total history counts also differ. The result supports the stated finite-model counterexamples and lower bound. It does not prove that a production retry policy reduces a real failure rate.

This review does not establish the novelty of snapshot reasoning. The proposed contribution is a bounded, reproducible audit with explicit outcomes and complete finite counts. The review used the source review notes for context. It did not independently re-read every external source or perform a new literature search.

No material calculation error was found in the compared files. The proof scope requires the fresh authoritative reads, fixed identity, complete atomic writes, revision rules, and common decision point in the frozen plan. The calculation excludes stale caches, separate revision updates, missing fields, record replacement, network failures, and later writes. It does not update the scores of the prior live account study.

Codex generated this review and its programs. This is a separate agent review. No human review or peer review is claimed.
