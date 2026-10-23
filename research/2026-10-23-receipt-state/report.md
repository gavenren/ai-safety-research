# A valid receipt does not prove the record is still correct

Date: 2026-10-23. Study type: complete finite model and regression test set.

## Abstract

A receipt can correctly prove that an operation occurred while the record now has another value. We test six caller rules on 338 fixed histories each (2,028 outcomes). Every first operation succeeds and has a permanent receipt with the correct identity and payload. Two groups of later writes can occur before and after an atomic record read. A rule that treats the receipt as proof of current state makes 160 false positive claims in 338 histories. An exact same-key retry adds no effect, but the tested caller still makes the same 160 false claims. A fresh compare-and-set rule permits 10 new effects that are outside the original operation's authority. A rule that reports history and read-time state separately makes no false claims and adds no effect, but leaves reply-time state unknown. These are exact model counts, not measured website or agent failure rates. The contribution is a reproducible comparison and test corpus for established failure mechanisms, not a new retry algorithm.

## Research question and safety relevance

After a successful operation and later edits, what evidence supports a historical claim, a read-time state claim, or a reply-time state claim? What happens if a caller tries to resolve a mismatch by sending the operation again?

A **receipt** records an identified operation and its result. A **retry** repeats that same logical operation. A **new-key repeat** uses a new request identifier and therefore creates a new operation in this model. An **atomic read** observes all record fields at one point. A **revision** is a non-reused integer that increases after every write. **Compare and set (CAS)** checks an expected revision and writes in one indivisible step.

An assistant can report that a task is complete from an old success response. It can also try to make an old result true again and change later work. This study separates the two errors. A truthful provider response is not itself a false completion claim.

## Related work and contribution

[AWS's retry guide](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) describes a late retry after another actor removes the resource. Its response can retain the original identity and show the later terminated state. [RIFL](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf), Section 2 and Figure 2, already shows how a repeated fixed write can overwrite a later write. Its completion records prevent a second execution.

[Stripe API v1](https://docs.stripe.com/api/idempotent_requests) can replay the saved status and response body. [Stripe API v2](https://docs.stripe.com/api-v2-overview) can return an updated response. Thus, a frozen response is a declared model choice, not a universal API property. [RFC 9110 Section 13.1.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1) separates conditional execution from a possible success response for an already applied change. It also discusses a later GET to resolve state confusion. Our integer revision is not a claim about every provider's ETag.

Two recent preprints are close conceptual work. [Authority at Commit Time, v1](https://arxiv.org/html/2609.31490v1) separates a canonical receipt from workflow closure. [Revocation Is Not Complete at Receipt, v1](https://arxiv.org/html/2610.15991v1) separates receipt stages from later effect outcomes in distributed revocation. Only the sections listed in `source_search.md` were checked. Their code, proofs, and experiments were not reproduced, and peer review was not verified.

The repository's [October 22 receipt study](../2026-10-22-receipt-binding/report.md) varies receipt binding but does not deliberately add a later writer. Here, binding is correct throughout. [October 16](../2026-10-16-field-snapshot/report.md) studies mixed reads; all reads here are atomic. [October 17](../2026-10-17-repair-dependencies/report.md) studies repair dependencies; this note isolates receipt history and new-operation authority. [October 18](../2026-10-18-retry-retention/report.md) studies lost request memory; receipts here never expire.

The contribution is the fixed corpus, separate claim and effect scores, paired comparisons, and independent evaluator. The central mechanisms are known. The limited source search cannot establish global novelty or priority.

## Method

The plan was saved and hashed before implementation and enumeration at 14:02:57 UTC on October 23. See `plan.md` and `plan_freeze.json`. The question, rules, grid, and measures did not change after the run. Instrumentation was later extended to record CPU time; no outcome rule changed.

The record contains `(x,y,v)`: a target bit, an unrelated bit, and a revision. The authorized first operation changes `x` to the target value and stores its receipt with the effect. Only this operation is authorized. A later mismatch does not give permission for another write. Under this explicit contract, each accepted new-key operation is extra, even if it writes the same value. A separate request to repair would be a different contract.

Targets are 0 and 1. The first operation starts from the opposite target value, `y=0`, and `v=0`. Each external group is a word of length zero, one, or two over `set0`, `set1`, and `flip_y`. Each command increments the revision, including a same-value assignment. Group A runs after the first effect and before the read. Group B runs after the read and before the optional final request and reply. Both groups run in every assigned case for every rule. There is no later write between the optional request and reply.

Each group has `1+3+9=13` words. Thus each rule has `2*13*13=338` histories. The second target checks label symmetry; it is not an independent population sample. All rules correctly report the first operation as applied from its bound receipt.

| Rule | Optional action after group B | State claim |
|---|---|---|
| R0 ReceiptNow | None; no new read | Target holds at reply, from the old receipt. |
| R1 ReadNow | None | Target holds or does not hold at reply, based on the read after A. |
| R2 ReadDated | None | Report match or mismatch only at the named read point and revision. |
| R3 ReplayNow | If the read mismatched, send the original key and payload. | Target holds at reply, from original or replayed success. |
| R4 NewKeyNow | If the read mismatched, assign the target under a new key. | Target holds at reply. |
| R5 FreshCASNow | If the read mismatched, assign under a new key only if the read revision still matches. | Target holds after acceptance or a matching read; otherwise reply-state unknown. |

R3 replays the receipt without an effect. R5 uses the revision from the read after A. Its condition tests change after that read, not permission to reverse a change already observed. Neither rule is presented as a deployed service implementation.

The main measures are false historical claims, false read-time claims, false positive and false negative reply claims, unknown reply state, extra effects, target-value overwrites, and unrelated-field damage. A false positive says the target holds when it does not. A false negative says it does not hold when it does. An overwrite is an extra write that changes the target value left by the external commands. It is a subset of extra effects. Every row also records reads, dispatches, receipt hits, accepted writes, and refused conditions.

## Results

All 2,028 outcomes completed. The table uses 338 histories per row. Counts overlap across columns and must not be added into one failure total.

| Rule | Reply claims | False positive | False negative | Reply state unknown | Extra effects | Target overwrites |
|---|---:|---:|---:|---:|---:|---:|
| R0 ReceiptNow | 338 | 160 | 0 | 0 | 0 | 0 |
| R1 ReadNow | 338 | 80 | 50 | 0 | 0 | 0 |
| R2 ReadDated | 0 | 0 | 0 | 338 | 0 | 0 |
| R3 ReplayNow | 338 | 160 | 0 | 0 | 0 | 0 |
| R4 NewKeyNow | 338 | 80 | 0 | 0 | 130 | 80 |
| R5 FreshCASNow | 218 | 80 | 0 | 120 | 10 | 10 |

All historical claims were correct. R2 made 338 read-time claims, all correct. No rule changed the unrelated field. R0 used no read; each other rule used 338 reads. R3 sent 130 requests and received 130 receipt replays. R4 sent and accepted 130 new writes. R5 sent 130 conditional write requests, accepted 10, and refused 120. Initial operation and receipt costs are common to all rules and excluded from these extra costs.

R1 made 208 positive and 130 negative reply claims. Therefore its false-positive count is 80 out of 208 positive claims, and its false-negative count is 50 out of 130 negative claims. R5's 80 false positive claims are out of 218 positive claims. These conditional denominators differ from the 338 assigned histories. They are corpus ratios, not risk estimates.

### Count derivation and paired checks

From a matching value, 8 of the 13 words leave a match and 5 leave a mismatch. From a mismatch, 5 leave a match and 8 leave a mismatch. The empty word is included in each count.

R0 and R3 always claim a match, so their false positives are `2*(8*5+5*8)=160`. R1 has `2*8*5=80` false positives and `2*5*5=50` false negatives. R4 sends a new operation in `2*5*13=130` histories. It changes an external target value in `2*5*8=80` of them. In the other 50, it adds an effect with no target-value change.

R5 accepts a dispatched write only when B is empty, because every external command increases the non-reused revision. Thus it accepts `2*5=10` extra writes and refuses `2*5*12=120`. Its 80 false positive claims occur when the read matched but B later changes the target. The write condition is not evaluated in that branch. R2 does not assert reply state; its correct claims therefore do not establish current-state availability.

These derivations matched the program and a separately written evaluator. Full pairwise count differences are in `results/paired_differences.csv`.

### Minimum examples

For target 1, the following cases isolate the errors. All start with a correct receipt for `x=1`.

| A | B | Evidence and outcome |
|---|---|---|
| Empty | Empty | Every current claim is correct; no rule dispatches another operation. |
| `set0` | Empty | The receipt stays true about history. R3 replays it with no effect while x remains 0. R5 accepts a new write and replaces the later 0. |
| Empty | `set0` | The read sees 1, but the reply state is 0. R2's dated statement remains true; R1's current statement does not. |
| `set0` | `set1` | R1 reports a mismatch after it has been removed. R4 adds a same-value effect. R5 refuses because the revision changed. |
| `set0` | `flip_y` | The target remains 0. R5 refuses on an unrelated revision change. This is a condition result, not a successful repair. |
| `set0,set1` | Empty | The target has returned to 1. A matching read is correct at this point despite the two later writes. |

The first and third cases have the same receipt and the same read, but different reply truth. A statement about reply truth cannot be derived from those identical observations alone. This is an illustration of an established information limit, not a new impossibility theorem.

## Discussion

The provider's receipt remains correct in every case. The error arises when a caller changes its meaning from “the operation occurred” to “the record still matches.” A same-key retry protects against another effect but does not by itself strengthen the caller's current-state evidence.

A fresh version check has a narrower role. It can stop a write after the observed revision changes. It cannot grant authority to erase an edit already present when the read occurred. R5's accepted writes show that limit under the original-operation-only contract. Its unguarded matching-read branch also retains a state-claim race.

A practical claim format can separate `original operation applied`, `observed target at revision v`, and `current state not verified`. This is a design implication of the model. It is not tested production guidance or a guarantee that all interfaces supply reliable receipts, revisions, or atomic reads.

## Limitations and uncertainty

This is a deterministic finite model with one record, two bits, two short groups of writes, and six selected rules. It has no live browser or account test. It measures no language model or website performance. The weak claim rules are explicit constructed baselines; their error counts do not show how often an agent would select them.

All first operations succeed and all receipts are available, correctly bound, and permanent. The corpus does not test whether a matching current value proves which operation caused it. Reads and writes are atomic, observations are authoritative, and revision numbers never repeat. It excludes deletion, replacement identity, permissions, expiry, stale caches, partial failures, multiple resources, and writes after the reply. It also excludes an authorized repair contract.

There is no random sampling or model fitting. No seed, confidence interval, or significance test is appropriate for these exact corpus counts. Uncertainty concerns model scope and external validity. The two target settings are a symmetry control. The independent evaluator reduces implementation risk but does not validate the assumptions or supply independent human review.

## Ethical and misuse considerations

Inputs are invented bits and identifiers. No private account data, human-subject data, credentials, or third-party code is included. No external account was changed by this study. A wrong deployment claim could cause extra writes or erase later work; the report therefore states the authority and timing limits. Source ideas are attributed and paraphrased. No new license is assigned to the owner's work.

Codex generated the study design, code, analysis, and report. Separate Codex agents checked sources, designed an independent evaluator, and reviewed the work. No human review or peer review occurred. This report does not claim institutional endorsement or certification.

## Reproduction and references

Use `README.md` for exact commands. `plan.md` and its freeze record define the inputs and decisions. `results/cases.jsonl` contains all input histories. `results/results.jsonl` contains every state trace, observation, action, and score. Summary, paired differences, examples, environment, and run logs are included. The scripts use Python standard library only and no paid or remote compute.

`references.bib` gives reference records. `source_search.md` gives search terms, access dates, read limits, and source URLs. The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was used as a review aid. `review.md` records the applicable checks. This is not a claim of NeurIPS approval or submission compliance.
