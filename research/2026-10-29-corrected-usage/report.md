# A nonnegative balance can preserve an accounting error

Date: 2026-10-29, America/Toronto. Research note. Exact finite simulation and a controlled production website extension with invented charges.

## Abstract

An AI task can receive a corrected charge after its work has ended. The correction can reduce an earlier amount. We compare six accounting rules on 11,664 delivery histories each. All rules remove exact repeated events. Forcing the shared partial balance to be at least zero overcounts 3,170 histories after every required report arrives. Applying that restriction separately to each item overcounts 4,014 histories. The second rule refuses 2,104 more feasible job branches than the first. A signed sum and replacement by the greatest source revision are exact in the declared closed model. Last-arrival replacement has the same total admissions as the signed sum, but exchanges 8,078 valid admissions for 8,078 excess-charge admissions. The contribution is a complete comparison corpus, matched outcomes, full traces, and a separate formula check. The accounting methods and reflection identity are known. These results do not measure production failure rates or prove a limit on physical compute.

A later production website extension used 25 temporary Google Drive and Calendar records. It added 36 matched decisions, 18 saved output renames, and 18 checked refusals. Four rules refused feasible saves after a reduction. ArrivalReplace saved an output above the invented test-credit limit on both services. These controlled inputs do not measure provider billing.

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

## Simulation reproduction and uncertainty

Two full runs produced identical bytes for seven scientific files. The separate formulas matched each run's 11,664 inputs, 69,984 rule cases, 408,240 state records, 338,256 event steps and duplicate flags, and 419,904 branches. They also matched 78 summary rows, seven paired tables, 11 first adverse examples, and 48 control cases with 240 states and 288 branches. States include repeated values after duplicates and are not independent samples. The independent formula source preceded main-source access; the schema adapter was written after source access. See [independent_review.md](independent_review.md).

The runtime was Python 3.13.7 on macOS 26.7.2, arm64, with the standard library only. CPU times were 1.963610 and 1.929251 seconds. Wall times were 1.961260 and 1.925142 seconds. Each run saved 4,233,904 scientific bytes before its environment record. These are resource records, not speed benchmarks. The experiment made no network or model API call. There was no random seed, training step, or train/test split.

Both runs stayed within the 120 CPU-second limit and periodic 300 wall-second and 200 MB output checks. Periodic checks are not hard real-time bounds. Peak memory was not measured. No main-run failure, comparison failure, or source repair occurred. Failed source discovery links are recorded separately from experiment outcomes.

The enumeration gives exact counts for selected integers and delivery multisets. It does not justify a population failure rate, confidence interval, or significance claim. The six decision branches share each history and are not independent observations. [README.md](README.md) gives exact commands and file descriptions.

## Production website extension: saved corrections and output actions

Extension date: 2026-10-29. This section adds controlled tests on Google Drive and the primary Google Calendar account. The earlier simulation and its results remain unchanged.

### Question, related work, and contribution

Can the same six rules control real browser saves when their input values come from saved website records? This extension tests that connection. It does not test an actual billing system. A **test credit** is an invented accounting unit stored in a folder or event name. The value has no financial meaning.

Google Drive documents stable file IDs and non-unique names [8]. Google Calendar documents event fields and conditional version checks [9,10]. We use exact provider IDs to join reads of the same record. We do not use names alone as identity. The revision labels in this test are assigned by the study. They are not Calendar sequence numbers, sorted etags, or verified Drive version counters. The browser writes do not test native conditional-update protection.

WebVoyager evaluates browser tasks on live public websites [11]. The text checked for this comparison was its arXiv version 4; the ACL publication metadata was checked separately. Its selected tasks exclude login-required access. This extension has a narrower purpose: it connects controlled accounting inputs to changes in owned account records. It is not a broad agent benchmark. The contribution is the saved integration evidence and matched decision checks. The rule examples were selected from the earlier simulation, so their arithmetic outcomes are expected. The [source record](live/source_notes.md) gives search terms, rights, and read scopes. This limited search does not establish global novelty.

### Plan and procedure

The [extension plan](live/plan.md) froze at 13:59:15 UTC before account writes. A separate formula implementation froze at 13:59:04 UTC. Its author had seen an original-study code excerpt, but had not seen the new implementation or results. The wrapper froze at 13:59:46 UTC. It calls the unchanged original `evaluate` function. The wrapper converts checked saved names into the original integer inputs; it does not change a rule.

Connector tools created 25 temporary records: one private Drive parent, six source folders and six output folders, and six source events and six output events. Calendar requests used Private and Free settings, no other guests, no reminders, no recurrence, and no meeting link. The saved attendee list included the owner as a self attendee. The requested interval was November 4, 2026, from 12:00 to 12:05 in America/Toronto. The audit checked the saved numeric interval and browser Free/Private fields. It did not verify a named saved time zone.

Each source record first stored revision 1. The browser then changed that same record's name to revision 2. All twelve corrections had a reopened or reloaded browser observation and an exact-record connector read. Thus the inputs contain 24 saved versions of twelve real records. The source charges, signed deltas, and revision labels are still study data.

The local controller delivered copies of those observations in the orders below. It also supplied the study operator's period-closure declaration. The changed delivery order, exact repeat, and closure are controlled conditions. They were not Google delivery faults or Google finality guarantees. All six rules received the same captured inputs and filtered repeated event IDs before accounting.

| Selected case, on each service | Values (uA,vA,uB,vB) | Delivered order | Cap C | Demand b |
| --- | --- | --- | ---: | ---: |
| credit | (2,0,0,0) | A2,A1,B1,B2 | 1 | 1 |
| upward | (0,2,0,0) | A2,A1,B1,B2 | 2 | 1 |
| replay | (1,1,1,1) | A2,A2,B2,A1,B1 | 3 | 1 |

Each rule had one output marker per service. The three cases reused that marker in the listed order. Each case started a fresh local accounting state. Earlier output changes were baseline fields, not charges in the next case. Before each decision, the exact marker was read. An admission permitted one browser rename to a unique case name. A refusal permitted no Save action. All markers were read again after the case, before later reuse. Each admitted rename cost one test credit by definition. This cap excluded setup, source edits, cleanup, and physical provider use.

### Measured outcomes

There were six selected service cases and 36 matched rule decisions. The browser saved twelve source corrections and eighteen output renames. The other eighteen decisions made no Save call. All 36 output before/after checks matched the intended action or unchanged field. These are counts of observed test actions. They are not independent population samples.

Each row below has six rule decisions, three per service. Final accounting compares the locally computed q with the final credits in the saved source names. An excess is above the invented study cap.

| Rule | Final undercounts | Final overcounts | Saved output renames | Excess-credit saves | Feasible refusals |
| --- | ---: | ---: | ---: | ---: | ---: |
| Net | 0 | 0 | 4 | 0 | 0 |
| GlobalClamp | 0 | 2 | 2 | 0 | 2 |
| ItemClamp | 0 | 2 | 2 | 0 | 2 |
| ArrivalReplace | 2 | 2 | 4 | 2 | 2 |
| MaxReplace | 0 | 2 | 2 | 0 | 2 |
| RevisionReplace | 0 | 0 | 4 | 0 | 0 |

In each credit case, Net and RevisionReplace booked zero and saved the permitted output. The other four rules booked two and refused a feasible one-credit save. In each upward case, ArrivalReplace booked zero after the old report. Its browser rename was saved, with a final test charge of three, which exceeds the cap of two by one. The other five rules booked two and refused. In both replay cases, all six rules booked two and saved one output each. All twelve repeated-event steps left the accounting state unchanged.

These three cases do not distinguish GlobalClamp from ItemClamp. The earlier simulation's offset-across-items case does distinguish them. This extension does not add live evidence for that difference.

### Checks, failures, and cleanup

A separate audit matched all 24 source versions to private exact-ID reads and retained hashes. It checked all 36 rule decisions and 192 prefix states against the frozen formulas; 1,674 assertions passed. A portable public-data check passed 1,701 assertions. It also checked source and output action counts, duplicate steps, and sequential marker reuse. Two saved-data re-executions of the controller produced the same bytes as the original `decisions.json`. This was repeated analysis of one website test, not a second live run. A separate output audit checked the final website actions and cleanup. See the [reproduction guide](live/README.md), [source audit](live/independent_review.md), and [output audit](live/output_review.md).

The browser had loading and navigation problems. An early Drive reload showed an old name before the saved state loaded. Some Calendar edit controls were not ready, and one Close selector matched both a window and a notice. These were resolved by fresh reads and exact record controls. No uncertain Save was repeated. The first Drive cleanup scan read incomplete pages and failed its path checks. A later scan waited for each record's own name before checking its path. The earlier failed evidence was retained. An independent audit adapter also needed a correction for the null field used on refused decisions. The accounting rules and observed test data did not change. [changes.md](live/changes.md) records these failures.

All twelve exact Calendar IDs returned cancelled status. The primary-calendar marker query for November 4 returned no active result and no next page. The Drive parent and all twelve exact child URLs showed a recoverable Trash path. The active Drive marker query returned no result. Trash was not emptied. These checks establish removal from the stated active test scopes, not permanent deletion or removal of provider audit history.

### Interpretation and limits

The original arithmetic errors affected real browser dispatch in these selected cases. A correct saved name does not mean that its accounting rule made a correct admission decision. ArrivalReplace's two excessive test-credit actions were saved successfully. Conversely, a local refusal can preserve a valid website state while needlessly blocking work.

This is an instrumented Codex workflow with fixed cases and checked inputs. It is not an independent unsupervised-agent evaluation. Test credits, order, finality, and trusted source revisions were supplied by the study. There was no real invoice, credit refund, provider quota, resource-meter test, concurrent writer, crash test, or native exactly-once guarantee. No new paid service or model API call was started. The selected counts do not justify a confidence interval, statistical significance, or a production failure rate.

The public files contain test-only names, local decisions, saved-field extracts, action records, and raw-evidence hashes. Exact account IDs, addresses, unfiltered pages, and screenshots remain private. Public readers can repeat the analysis and use the procedure in an authorized account. They cannot query the removed private fixtures from these files. A hash links retained evidence; it does not prove a provider action by itself.

The browser was Chrome 156.0.8078.48. Analysis used Python 3.13.7 and the standard library. Connector builds and the exact Codex model build were not exposed. No random seed or timing benchmark applies. Codex generated and ran this extension. Separate Codex agents checked sources, formulas, outputs, and claims. No human or external peer review occurred. No new licence is assigned.

## Discussion and limitations

A nonnegative display is not proof that accounting is correct. Clipping removes information from an incomplete signed sum. If nonnegative display values are required, the ledger can retain the signed data while showing an explicitly incomplete view. This study does not test that interface or its effect on users.

Keeping every record and filtering duplicate IDs are not sufficient if the merge operation changes meaning. The sum of signed adjustments and replacement by revision are valid for their respective encodings here. The maximum payload is valid for a monotone counter, as in the earlier studies, but not for exact downward-correction accounting. Adapters must preserve these distinctions.

The finite simulation corpus has two items, two revisions per item, exact integers, one optional repeated report, a fixed final period, and no missing primary record. It excludes conflicts, identity reuse, spoofed sources, clock-derived revisions, floating-point rounding, price conversion, taxes, crashes, atomic database writes, live job dispatch, and corrections after closure. The comparison does not establish that a billing, cloud, or agent service implements any tested rule.

All rules wait for complete closure. We do not test which can safely act earlier, how much capacity must be reserved, or how long finality takes. A source that can issue later corrections needs a different contract. Limits on physical compute and irreversible effects also require their own measurements and controls. No result here refunds that past use.

## Ethical issues, rights, and review status

Codex generated the study, code, analysis, and report. Separate Codex agents prepared formulas and reviewed sources, design, implementation, and results. The exact model build was not exposed. No human or external peer review occurred. No university affiliation, endorsement, or certification is claimed.

The original simulation uses invented inputs and made no account mutation. The later extension used owner-authorized temporary account records. It used no payment, paid compute, or new credential. Its private account evidence is excluded from public files. No source code, external dataset, figure, or long passage was copied. References are attributed short paraphrases with explicit reading scopes. No new license is assigned. The principal misuse risk is to present charge-accounting results as a guarantee about real physical use or production reliability. Relevant NeurIPS checklist topics are a review aid only [7].

## References

1. Google Cloud. [Structure of Standard data export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/standard-usage). Correction schema and errors/adjustments sections.
2. Stripe. [Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks). Event order, immutable event records, and duplicate handling sections.
3. Elastic. [Create or update a document in an index](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-index). External versioning sections.
4. Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski. [Convergent and Commutative Replicated Data Types](https://www.lip6.fr/Marc.Shapiro/papers/2011/CRDTs-beatcs-2011-06.pdf). Bulletin of the EATCS 104, 2011. Selected convergence and register sections.
5. O. J. Boxma and M. R. H. Mandjes. [Queueing and risk models with dependencies](https://link.springer.com/article/10.1007/s11134-022-09863-7). Queueing Systems 102, 69–86, 2022. Introduction, recurrence, opening model, and metadata only.
6. Genliang Zhu and Chu Wang. [Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation](https://arxiv.org/html/2610.00349v1). Preprint v1, 2026. Selected abstract, assumptions, and external-effect sections; no full-paper proof review.
7. NeurIPS. [Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist). Review aid only.

8. Google. [Drive files resource](https://developers.google.com/workspace/drive/api/reference/rest/v3/files). Identity, names, versions, and trash fields.
9. Google. [Calendar events resource](https://developers.google.com/workspace/calendar/api/v3/reference/events). Event identity and saved fields.
10. Google. [Get specific versions of resources](https://developers.google.com/workspace/calendar/api/guides/version-resources). Conditional etag checks.
11. Hongliang He and colleagues. [WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models](https://aclanthology.org/2024.acl-long.371/). ACL 2024. Metadata checked; selected methods, limits, and ethics text read from [arXiv version 4](https://arxiv.org/html/2401.13919v4). The ACL PDF could not be retrieved.

All sources were checked on 2026-10-29. [references.bib](references.bib) and [source_search.md](source_search.md) give metadata, queries, rights, and precise reading limits. The extension source record is [live/source_notes.md](live/source_notes.md).
