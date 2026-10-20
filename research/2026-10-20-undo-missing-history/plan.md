# Plan: undo with missing action records

Date: 2026-10-20, America/Toronto. Save and hash this plan before execution.

## Question and contribution

When the number of missing commands has a trusted upper bound, how often can all compatible histories select one safe undo target in a finite model?

This extends the October 19 study's complete-history requirement. The method follows established reasoning over possible histories. The contribution is an exact test corpus, comparison, bound-sensitivity result, and reproducible examples for this undo model. It is not a new general recovery algorithm. Source selection precedes this plan; see source_search.md.

## Model and inputs

A record is `(x,y)`, where x is an integer and y is 0 or 1. The initial values each range over {0,1}. The agent adds 1 to x. Later commands are add1 (x+1), sub1 (x-1), set0 (x=0), set1 (x=1), and flip_y (y=1-y). Commands have no other effects.

Enumerate every later word of length L=0 through 4. For each word, enumerate each of its 2^L deletion masks. A mask says which commands remain visible. The visible log is an ordered subsequence; it has no altered or invented commands. Different masks remain distinct cases even when they give the same visible log. There are 4*sum(10^L,L=0..4)=44,444 cases. This count defines the corpus; it is not a measured result. No random seed is used.

The true undo target is the result of the same later commands from the initial record, without the agent increment. Later commands do not change when the agent increment is removed. This is a fixed-command counterfactual, not a claim about how real users would have acted.

Let k be the number of omitted commands. Evaluate three bound settings: tight upper B=k; loose upper B=k+1; false upper B=max(k-1,0), only on k>0 cases. Tight means an upper bound with zero slack. It does not tell the controller that exactly B commands are missing.

The controller receives only the initial record, the current record, the visible commands, and B. It does not receive k, L, the true word, the mask, or the true target. B is supplied by the test generator as a trusted-input assumption, not estimated from a website. The false-bound setting deliberately violates this assumption.

For an observation, candidate histories contain the visible log as a subsequence, have zero through B added commands, and reproduce the current record when run after the agent increment. Retain all such histories and their targets. The largest required candidate length is 5 in the loose setting. Do not restrict candidates to the corpus's actual maximum length 4. Deduplicate command words, not their distinct targets. A candidate count and a target count are different measures.

## Rules

1. Visible compensation: if a visible command assigns x, retain current x; otherwise subtract 1 from current x. Retain current y. Always claim complete.
2. Replay guard: if replay of the visible log after the agent action differs from current, refuse. Otherwise apply visible compensation and claim complete.
3. No-loss guard: complete only when B=0 and replay of the visible log matches current. Then use its counterfactual target.
4. Target agreement: complete only if the candidate set is nonempty and every candidate has the same target. Write that target. Refuse otherwise.
5. Full-history reference: use the complete true word and complete. This is an ideal stronger-information control, not an implementable baseline with the same inputs.

All reads, decisions, and writes are exact and atomic. A completion applies the selected literal target correctly. There are no actuator faults, new concurrent writes, identity faults, stale reads, or retries. Refusal leaves current fields unchanged. This study tests target selection, not browser execution or successful saved-field verification.

## Measures and comparisons

For each case, bound, and rule, retain the action and one of four outcomes: correct completion; false completion; refusal with correct current state; refusal with incorrect current state. A false completion claims completion with fields different from the true target. Report totals by L, missing count, bound setting, and rule. Primary comparison: all length-four cases in the tight setting, with a separate k>0 table. Also report the full corpus.

Keep one raw case row per initial/word/mask. Keep one decision row per unique observation `(initial,current,visible,B)` and applicable rule. Summaries count cases, not independent statistical trials. Also report unique observation counts and how many have one, multiple, or zero targets. Observation rows can be shared across bound settings; retain that distinction.

No confidence interval or p-value applies to these exact finite counts. Do not interpret enumeration weights as natural frequencies.

## Hypotheses and decision criteria

H1: Target agreement has zero false completions with either honest bound. A counterexample rejects this claim.

H2: In the tight setting, target agreement gives at least one correct completion with k>0, more than the no-loss guard. If not, report no completion benefit.

H3: The replay guard has at least one false completion in the tight setting. If not, reject this expected failure.

H4: For each case, the loose target set contains the tight target set. Every loose completion must also be a tight completion with the same target. No violation is allowed.

H5: The false-bound setting produces at least one false completion under target agreement. If not, report that this stress test did not reveal the expected fault.

H6: At least one honest observation has multiple candidate histories but a single target. If not, report that full-history recovery was required in this corpus.

Find the first example for each result in fixed order: initial x, initial y, L, word in the listed alphabet order, numeric mask. Also retain a two-history witness for the first ambiguous observation and a false-bound witness. These are descriptive examples, not selected success-rate estimates.

## Checks and resource limit

Check operation semantics, empty log, B=0 equivalence, y preservation, true-history inclusion for honest bounds, no empty honest candidate set, target-set inclusion, and the full-history reference. Test inconsistent current values with an empty candidate set and reject malformed bounds/commands. Confirm the controller has no evaluator-target input.

Use a separately written implementation to compare candidate counts, target sets, every decision, and all outcome summaries. It must not import the main analysis implementation. Test at least one independently expressed reference-target formula. Re-run the documented procedure in a clean directory and compare deterministic output bytes. Record actual failed checks and changes; do not alter inputs to remove failures.

Use local CPU, Python standard library, and public primary sources only. Stop and preserve a draft if the bounded enumeration cannot finish within ten local CPU minutes, if independent results disagree and cannot be resolved, or if a material source or evidence check remains open. No paid models or compute.

## Publication

Use relevant NeurIPS checklist items as a review aid. Get separate agent review. Check claims, references, reproducibility, limitations, table structure, secrets, private data, copied text, and licenses. Publish to the selected repository only after checks pass. Verify the remote tree and bytes. Record AI roles and the lack of human review. No source license is changed.
