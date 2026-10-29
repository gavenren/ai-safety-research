# A nonnegative balance can preserve an accounting error

Date: 2026-10-29, America/Toronto. Research note. Exact finite simulation with invented charges.

## Abstract

An AI task can receive a corrected charge after its work has ended. The correction can reduce an earlier amount. We compare six accounting rules on 11,664 delivery histories each. All rules remove exact repeated events. Forcing the shared partial balance to be at least zero overcounts 3,170 histories after every required report arrives. Applying that restriction separately to each item overcounts 4,014 histories. The second rule refuses 2,104 more feasible job branches than the first. A signed sum and replacement by the greatest source revision are exact in the declared closed model. Last-arrival replacement has the same total admissions as the signed sum, but exchanges 8,078 valid admissions for 8,078 excess-charge admissions. The contribution is a complete comparison corpus, matched outcomes, full traces, and a separate formula check. The accounting methods and reflection identity are known. These results do not measure production failure rates or prove a limit on physical compute.

## Research question and safety relevance

Can forcing each partial balance to be nonnegative corrupt final accounting when signed corrections arrive in a different order? Does the result depend on whether the rule acts on each item or on the shared total?

A **charge** is the amount assigned to completed work in the chosen accounting unit. A **correction** replaces an earlier charge. A **delta** is the signed change from one charge to the next. **Clipping at zero** replaces a negative partial balance with zero. A **revision** is a trusted source order number for one item. **Deduplication** ignores an exact repeated event ID. **Closure** means that the source has declared the final revisions and that the required reports are present.

An AI controller can use charges to decide whether more work fits a budget. Too little booked charge can permit an excess. Too much can cause a needless refusal. These are different failures. A rule can prevent excess and still give incorrect accounting.

This paper studies corrected net charges. It does not treat a credit as removal of tokens, tool effects, energy, or other physical use that already occurred. It tests decisions only after an assumed final accounting boundary. It makes no claim that a live billing service supplies that boundary.

## Related work and contribution

Google Cloud documents appended corrections that negate earlier charge lines and can add replacement lines [1]. Stripe documents unordered event delivery and duplicate event IDs [2]. These sources motivate correction and delivery handling. They do not define the combined protocol used here. In particular, Google's additive lines must not be treated as replacement snapshots without a valid conversion.

Elastic documents replacement using an external version that must exceed the stored version [3]. Shapiro and colleagues describe registers that retain the assignment with the greatest order metadata [4]. The greatest revision and the greatest numeric payload are different rules. Both identity and order remain trusted assumptions here.

The clipped recurrence is known as the Lindley recursion. Boxma and Mandjes give it and describe reflection at zero [5]. We derive its finite-prefix identity for our declared records; we do not claim a new mathematical method. Zhu and Wang's preprint distinguishes accounting from external effects and assumes a sound maximum charge [6]. Its immutable terminal decisions differ from this authorized-correction contract. We checked selected sections, not the full proofs or implementation.

The repository's [October 26 study](../2026-10-26-usage-reconciliation/report.md) assumed a monotone cumulative amount. The [October 27 study](../2026-10-27-counter-epochs/report.md) added counter restarts but excluded corrections. The [October 28 study](../2026-10-28-budget-reduction/report.md) changed the cap while spent use could not fall. This study keeps each decision cap fixed and permits a revised charge to fall.

The contribution is the declared six-rule corpus, paired accounting and admission scores, complete event traces, and separate formula implementation. Signed addition, clipping, and ordered replacement are established operations. The [limited source search](source_search.md) does not prove that this comparison is the first of its kind.

## Method

### Frozen plan and contract

The [plan](plan.md) froze at 13:36:07 UTC before implementation and execution. A separate agent froze its formula source at 13:37:17 UTC before main-source access. The main implementation froze at 13:39:00 UTC. The separate schema adapter froze at 13:40:15 UTC before its reviewer read main outputs. All four source hashes are retained. Shared assumptions can still produce shared errors.

Two completed items A and B each emit two revisions. Revision 1 gives an initial value u. Revision 2 gives a corrected final value v. Every u and v is in `{0,1,2}`; decreases, increases, unchanged amounts, and zero amounts are included. This gives 81 four-value settings. Final true charge is `Z=vA+vB`.

Every report contains an event ID, stable item ID, revision, replacement value, and delta. Revision 1 has delta u. Revision 2 has delta `v-u`. These encodings agree by construction. All rules receive the same fields but use their declared interpretation. They cannot use future report values. A separate scorer knows Z.

The four IDs are A1, A2, B1, and B2. Test the four-report set, the set with one extra A2, and the set with one extra B2. Exact copies have identical IDs and fields. The sets have 24, 60, and 60 distinct permutations. Crossing 144 orders with 81 settings gives **11,664 histories per rule**. Six rules give 69,984 rule cases. The selected histories are not random samples.

All rules filter repeated IDs before any amount update. A later exact replay cannot replace a balance again. Different duplicate groups weight first-occurrence orders differently. Differences between their aggregate frequencies do not isolate a causal effect of replay. The direct replay check is that a repeated ID leaves every accounting field unchanged.

### Six rules

All balances start at zero. The booked total is q.

| Rule | Update for a distinct report |
| --- | --- |
| Net | Add its signed delta to the shared q. Keep negative partial values. |
| GlobalClamp | Set shared q to `max(0,q+delta)`. |
| ItemClamp | Apply the same clipping to that item's balance; sum the two balances. |
| ArrivalReplace | Replace that item's value using the last distinct delivered report; sum. |
| MaxReplace | Keep the greatest delivered value for each item; sum. |
| RevisionReplace | Replace an item's value only when the report has a greater source revision; sum. |

No work is admitted during delivery. After delivery, a trusted external declaration says that revision 2 is final for both items and no later correction belongs to this period. A common gate also requires all four unique reports. Neither the greatest seen revision nor receipt of the four reports alone establishes external finality. The common gate is intentionally stronger than the minimum data a replacement rule could need; partial-data utility is outside this comparison.

After closure, test six independent new-job branches: `C ∈ {Z,Z+1,Z+2}` and demand `b ∈ {1,2}`. Admit if the gate passes and `q+b<=C`. An accepted job incurs exactly b charge units. There are 69,984 branches per rule, 419,904 in total. They are separate hypothetical choices, not six jobs run in sequence. Choosing C relative to Z tests boundary cases; it is not a practical forecast of unknown charges.

### Measures and controls

Final accounting error is `q-Z`. Record undercount, exact count, overcount, error extremes, and whether any intermediate q was negative. Final charge after a decision is `Z+b` if admitted and Z otherwise. An **excess-charge admission** has final charge greater than C. A **feasible refusal** refuses a job although `Z+b<=C`. A negative local balance is recorded separately; it is not proof of excess actual charge.

Save the initial state and every delivered-event state. These records contain seen IDs, duplicate flags, q, and applicable item values and revisions. Summary groups cover the full set, duplicate type, and both correction directions. Groups overlap. Matched comparisons retain decision differences against Net and between both clipping rules.

Six named controls cover an early negative correction, an old original after an upward correction, an offset across items, equal values at both revisions, zero values, and exact replay. These repeat selected primary histories. Two further controls separately remove a required report or the external finality declaration. Both must refuse all branches. No control tests whether a real provider can certify finality.

## Results

All planned cases completed. Every row below has **11,664 histories and 69,984 decision branches**. Case counts and branch counts must not be added.

| Rule | Final undercounts | Final overcounts | Excess-charge branches | Feasible refusal branches | Admitted branches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Net | 0 | 0 | 0 | 0 | 34,992 |
| GlobalClamp | 0 | 3,170 | 0 | 7,538 | 27,454 |
| ItemClamp | 0 | 4,014 | 0 | 9,642 | 25,350 |
| ArrivalReplace | 3,370 | 3,370 | 8,078 | 8,078 | 34,992 |
| MaxReplace | 0 | 6,480 | 0 | 15,984 | 19,008 |
| RevisionReplace | 0 | 0 | 0 | 0 | 34,992 |

Net and RevisionReplace are exact after every primary history. Their decisions match in all 69,984 branches. This supports H1 under complete closure and correct input semantics.

Net has a negative intermediate q in 3,170 histories, reaching minus four units. These partial values are retained as incomplete accounting; they are never used to admit work. GlobalClamp removes the negative values but overcounts those same 3,170 histories at closure. Clipping has discarded a valid negative contribution that later positive reports do not restore.

ItemClamp exceeds GlobalClamp in 1,164 matched histories and equals it in 10,500. It is never lower. The maximum extra booked amount is two units. It refuses 2,104 branches that GlobalClamp admits; all are feasible. Of the histories where ItemClamp is higher, some already overcount under GlobalClamp. Thus the 1,164 matched differences do not equal the difference between their overcount-case totals. These results support H2 and the declared partition comparison.

MaxReplace overcounts 6,480 histories and is exact in 5,184. It never undercounts because the final value is among the received values. Its greatest overcount is four units. Keeping a larger obsolete amount is conservative for this post-closure charge cap, but it is not exact corrected accounting.

ArrivalReplace is exact in 4,924 histories. It undercounts 3,370 and overcounts 3,370. Its largest error is four units in either direction; the largest excess charge on a new branch is two units. These results support H3. It admits the same total number of branches as Net, but the matched decisions differ in 16,156 branches: 8,078 extra admissions exceed the charge cap, while 8,078 valid admissions are lost. An equal aggregate admission count hides these two errors.

The six named controls produce 36 rule cases. The two boundary controls produce 12 rule cases and 72 refused branches. These planned refusals are outside the primary error totals. All retained first adverse examples are the first in the declared enumeration order, not global minimal examples. See [summary.csv](results/summary.csv), [paired.json](results/paired.json), and [witnesses.json](results/witnesses.json).

### Concrete controls

In the early-credit control, A's initial charge is two and its corrected charge is zero. B has zero charge. A2 arrives before A1. Its delta is minus two. GlobalClamp changes zero to zero and discards the negative amount. A1 then adds two. At closure q is two while Z is zero. Net retains minus two until the original arrives, then reaches zero. RevisionReplace keeps the authoritative revision-2 value of zero despite the late original.

In the offset-across-items control, A changes from two to zero while B stays at two. Delivery begins B1, A2, A1, B2. The shared total moves through two, zero, two, two and is exact. ItemClamp discards A's early negative correction because A's own balance is zero. It ends with two booked for A and two for B, although the final charge is two. The same records produce different accounting because the clipping boundary changed.

In the upward-correction control, A changes from zero to two. A2 arrives before A1. ArrivalReplace ends at zero after the old original and can admit a job above the final charge cap. A later exact A2 replay does not repair that rule because all rules ignore already seen IDs. Ordered replacement uses the greater revision on its first delivery and rejects the later older assignment.

## Conditional derivations

Let the distinct delivered deltas be `d1,...,dn`. Let `S0=0` and `Sk=d1+...+dk`. Define `mk=min(S0,...,Sk)`. Because the empty prefix is zero, `mk<=0`. GlobalClamp starts at zero and follows `qk=max(0,q(k-1)+dk)`.

Assume `q(k-1)=S(k-1)-m(k-1)`. Substitution gives

`qk = max(0,Sk-m(k-1)) = Sk-min(Sk,m(k-1)) = Sk-mk`.

The identity holds at k=0, so induction proves it for each prefix. Exact duplicates add no distinct delta and leave both sides unchanged. Complete receipt gives `Sn=uA+(vA-uA)+uB+(vB-uB)=Z`. The final clipping error is therefore `-mn`. It is nonnegative and is zero exactly when no shared prefix sum is negative. This is the known reflection construction applied to our records, not a new theorem.

For item i, define its partial signed sum `Si(k)` and minimum `mi=min_k Si(k)`, including zero. ItemClamp ends at `Z-mA-mB`. At each shared prefix, each item sum is at least its own minimum. Therefore `min_k(SA(k)+SB(k)) >= mA+mB`. It follows that ItemClamp's final q is at least GlobalClamp's. They can differ because the separate item minima can occur at different times, or one item's positive amount can cover the other's negative prefix.

MaxReplace ends at `max(uA,vA)+max(uB,vB)`. Its error is `max(uA-vA,0)+max(uB-vB,0)`. RevisionReplace selects revision 2 for each item and therefore ends at Z. Net also ends at Z by signed addition. These statements require correct IDs, correct deltas or revisions as applicable, and all specified reports.

When q equals Z, the branch guard is exactly `Z+b<=C`. When q is at least Z, it cannot admit an excess-charge branch, though it can refuse a feasible one. ArrivalReplace can fall below Z, so that argument does not apply. None of these results permits use of an incomplete signed sum as available spend. The external finality assumption is essential to the interpretation.

## Reproduction and uncertainty

Two full runs produced identical bytes for seven scientific files. The separate formulas matched each run's 11,664 inputs, 69,984 rule cases, 408,240 state records, 338,256 event steps and duplicate flags, and 419,904 branches. They also matched 78 summary rows, seven paired tables, 11 first adverse examples, and 48 control cases with 240 states and 288 branches. States include repeated values after duplicates and are not independent samples. The independent formula source preceded main-source access; the schema adapter was written after source access. See [independent_review.md](independent_review.md).

The runtime was Python 3.13.7 on macOS 26.7.2, arm64, with the standard library only. CPU times were 1.963610 and 1.929251 seconds. Wall times were 1.961260 and 1.925142 seconds. Each run saved 4,233,904 scientific bytes before its environment record. These are resource records, not speed benchmarks. The experiment made no network or model API call. There was no random seed, training step, or train/test split.

Both runs stayed within the 120 CPU-second limit and periodic 300 wall-second and 200 MB output checks. Periodic checks are not hard real-time bounds. Peak memory was not measured. No main-run failure, comparison failure, or source repair occurred. Failed source discovery links are recorded separately from experiment outcomes.

The enumeration gives exact counts for selected integers and delivery multisets. It does not justify a population failure rate, confidence interval, or significance claim. The six decision branches share each history and are not independent observations. [README.md](README.md) gives exact commands and file descriptions.

## Discussion and limitations

A nonnegative display is not proof that accounting is correct. Clipping removes information from an incomplete signed sum. If nonnegative display values are required, the ledger can retain the signed data while showing an explicitly incomplete view. This study does not test that interface or its effect on users.

Keeping every record and filtering duplicate IDs are not sufficient if the merge operation changes meaning. The sum of signed adjustments and replacement by revision are valid for their respective encodings here. The maximum payload is valid for a monotone counter, as in the earlier studies, but not for exact downward-correction accounting. Adapters must preserve these distinctions.

The corpus has two items, two revisions per item, exact integers, one optional repeated report, a fixed final period, and no missing primary record. It excludes conflicts, identity reuse, spoofed sources, clock-derived revisions, floating-point rounding, price conversion, taxes, crashes, atomic database writes, live job dispatch, and corrections after closure. The comparison does not establish that a billing, cloud, or agent service implements any tested rule.

All rules wait for complete closure. We do not test which can safely act earlier, how much capacity must be reserved, or how long finality takes. A source that can issue later corrections needs a different contract. Limits on physical compute and irreversible effects also require their own measurements and controls. No result here refunds that past use.

## Ethical issues, rights, and review status

Codex generated the study, code, analysis, and report. Separate Codex agents prepared formulas and reviewed sources, design, implementation, and results. The exact model build was not exposed. No human or external peer review occurred. No university affiliation, endorsement, or certification is claimed.

Inputs are invented. No private record, payment, connected-account mutation, paid compute, or new credential was used. No source code, external dataset, figure, or long passage was copied. References are attributed short paraphrases with explicit reading scopes. No new license is assigned. The principal misuse risk is to present charge-accounting results as a guarantee about real physical use or production reliability. Relevant NeurIPS checklist topics are a review aid only [7].

## References

1. Google Cloud. [Structure of Standard data export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/standard-usage). Correction schema and errors/adjustments sections.
2. Stripe. [Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks). Event order, immutable event records, and duplicate handling sections.
3. Elastic. [Create or update a document in an index](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-index). External versioning sections.
4. Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski. [Convergent and Commutative Replicated Data Types](https://www.lip6.fr/Marc.Shapiro/papers/2011/CRDTs-beatcs-2011-06.pdf). Bulletin of the EATCS 104, 2011. Selected convergence and register sections.
5. O. J. Boxma and M. R. H. Mandjes. [Queueing and risk models with dependencies](https://link.springer.com/article/10.1007/s11134-022-09863-7). Queueing Systems 102, 69–86, 2022. Introduction, recurrence, opening model, and metadata only.
6. Genliang Zhu and Chu Wang. [Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation](https://arxiv.org/html/2610.00349v1). Preprint v1, 2026. Selected abstract, assumptions, and external-effect sections; no full-paper proof review.
7. NeurIPS. [Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist). Review aid only.

All sources were checked on 2026-10-29. [references.bib](references.bib) and [source_search.md](source_search.md) give metadata, queries, rights, and precise reading limits.
