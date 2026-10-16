# When correct field reads do not form a correct record

Date: October 16, 2026 (America/Toronto)  
Study type: exact synthetic analysis  
Review: separate agent calculation and review; no human review or peer review

## Abstract

A computer-use agent can read each required field correctly and still make a false completion claim. The values may come from different record states. We count all allowed histories in 18 small models with two or three fields, one to three scans, and zero to two writes between reads. We compare value checks with four revision checks and an ideal whole-record read. For two fields and two scans, at most two writes per gap give 67,228 histories. Value checks accept 4,410 histories. In 16 of these histories, the complete target never exists. A revision that covers every write and never repeats prevents both defined false outcomes. It also rejects 16,806 histories that end with a correct record. An independent program matches every result. These are finite-model counts, not website failure rates. The contribution is a repeatable comparison with complete witnesses; the underlying snapshot principles are established.

## Research question and safety relevance

Can repeated saved-field checks accept a target that never existed as one complete record? How does the answer change when a revision is complete, reused, or incomplete?

A **target** is the full set of required field values. A **revision** is a value used to track record changes. A **snapshot** contains values that were valid together at one time. A **mixed read** combines observations from different states.

A false completion claim can cause an agent to stop before a task is correct. A retry can also change a correct record or create a duplicate. This study concerns the evidence for completion of one fixed record. It does not measure duplicate prevention.

The [October 15 account study](../2026-10-15-computer-use-retries/report.md) checked saved fields. It did not deliberately schedule a second writer between those reads or establish a shared revision for them. This study isolates that gap. It does not alter the earlier trial scores.

## Related work and contribution

Atomic snapshot research already distinguishes a set of reads from a consistent snapshot. Afek and colleagues use marked values and increasing sequence numbers; their complete algorithms contain more machinery than the guard tested here. [Afek et al., 1993, Section 3](https://groups.csail.mit.edu/tds/papers/Shavit/JACM93.pdf)

RAMP transactions address atomic visibility in databases. That is related to mixed observations, but our model has no multi-field database transaction. Linux sequence counters also require a defined writer protocol and ordered reads. These are prior methods, not inventions of this study. [Bailis et al., 2014, Section 3](https://www.bailis.org/papers/ramp-sigmod2014.pdf); [Linux sequence-counter documentation](https://docs.kernel.org/locking/seqlock.html)

StateAct uses checks of saved outputs to assess task completion. Its version 1 is a preprint. Our question concerns whether separately supplied field observations describe one state. We do not test StateAct or claim a new completion-check method. [StateAct, Section 4.2](https://arxiv.org/html/2607.22798v1)

The proposed contribution is an exact six-policy comparison, with two distinct error measures, minimum-write examples, full result data, and a separate implementation. The [search record](source_search.md) gives terms, dates, URLs, and the parts read. This limited search does not prove novelty. The bounds and proofs apply established consistency reasoning to the stated model.

## Method

The [plan](analysis_plan.md), [configuration](config.json), and source search were saved before calculation. Their hashes are in the [input manifest](input_manifest.json). There were no changes to these frozen inputs after calculation began.

Each record has `d` binary fields. A value of 1 means that a field matches its fixed target. A value of 0 means that it is wrong. The target is the all-one vector. A write flips one field. The flip and revision increment form one atomic event: no read occurs inside that event.

Each history starts with a revision read. The agent then scans fields in order for `r` passes. A final revision read and the decision occur with no write between them. Each of the `r*d+1` gaps contains an ordered word of zero to `b` writes. Initial and final gaps are included. The grid is `d in {2,3}`, `r in {1,2,3}`, and `b in {0,1,2}`. All initial vectors and all allowed gap words are included.

With `q = sum(k=0,...,b) d^k`, the number of histories is `N = 2^d * q^(r*d+1)`. A history is counted once. No probability distribution over production histories is assumed.

| Rule | Condition for acceptance |
| --- | --- |
| Values | Every field read in every pass equals 1. |
| Full revision | Values passes, and a complete, non-reused revision is unchanged. |
| Modulo 2 | Values passes, and total writes are divisible by 2. The revision repeats every two writes. |
| Modulo 4 | Values passes, and total writes are divisible by 4. |
| Partial revision | Values passes, and no write changes the last field. Only that field is covered. |
| Atomic final | An ideal whole-record read is the target at the common decision point. |

Atomic final uses a stronger interface. It is a reference condition, not a claimed browser feature. All other reads are also assumed fresh and authoritative. Identity is fixed. There are no missing values or failed writes.

We score **no-common-target** when a rule accepts but the target never exists in the interval. Every intermediate write state counts. We score **wrong-at-decision** when a rule accepts but the final record is wrong. The first outcome is a subset of the second. We also count rejected histories whose final record is correct. Rejection is not a false completion claim.

The four planned hypotheses concern: the two-field minimum write count; zero false outcomes for the complete revision and ideal snapshot; at least one modulo-revision setting and one partial-revision setting with a counterexample; and rejection of some correct final records by the complete revision.

The main program groups history prefixes that have the same current vector, read-success flag, target-existence flag, total writes, and covered-field writes. It sums exact integer counts. It retains a minimum-write example, called a **witness**, for each nonempty false-outcome set. The [derivations](derivations.md) prove why this grouping preserves the counts.

## Results

All four planned hypotheses hold in the declared grid. There are 108 policy rows, 13,744 terminal count rows, and 71 witnesses. The largest history set contains 1,102,867,934,792 histories. This is an exact grouped calculation; it is not a run of that many browser trials.

The table shows the complete two-field, two-pass, two-write-per-gap setting. Each rule uses the same 67,228 histories and the same decision point.

| Rule | Accepted | No-common-target | Wrong-at-decision | Rejected correct final |
| --- | ---: | ---: | ---: | ---: |
| Values | 4,410 | 16 | 3,010 | 15,407 |
| Full revision | 1 | 0 | 0 | 16,806 |
| Modulo 2 | 2,250 | 10 | 1,475 | 16,032 |
| Modulo 4 | 1,197 | 5 | 787 | 16,397 |
| Partial revision | 135 | 0 | 60 | 16,732 |
| Atomic final | 16,807 | 0 | 0 | 0 |

Source: [results.csv](results.csv), rows with `fields=2`, `passes=2`, and `writes_per_gap=2`.

A six-write history explains the Values error. Start at `(1,0)`. Read the first field as 1. Change through `(0,0)` to `(0,1)`, then read the second field as 1. Change through `(0,0)` to `(1,0)` for the next first-field read. Change through `(0,0)` to `(0,1)` for the last second-field read. Both scans return the target vector. The record is never `(1,1)`.

For two fields, adjacent successful reads must alternate `(1,0)` and `(0,1)` if the target never exists. Each transition needs at least two single-field writes. There are `2r-1` transitions. The minimum is therefore `2*(2r-1)`: 2, 6, and 10 writes for one, two, and three passes. The saved witnesses attain each bound. A wrong-at-decision error can need only one final write; it is a different outcome.

Across all 18 settings, Values, Modulo 2, and Modulo 4 each have no-common-target errors in seven settings. Partial revision has them in three settings, all with three fields. With two fields, its unchanged covered field stays correct. A correct read of the other field then implies that the target exists at that moment. With three fields, two uncovered fields can alternate. In the three-field, two-pass, two-write setting, Partial revision has 340 no-common-target histories out of 501,988,136 total histories.

Full revision and Atomic final have zero false outcomes in all 18 settings. Full revision accepts exactly one history per setting: the target initial record with no writes. It rejects some correct final histories in all 12 settings that permit writes. All six zero-write settings are clean controls for every rule.

## Validation

A separate agent wrote a second program from the plan without reading or importing the main program. All terminal counts, policy counts, stage totals, and minimum-write witnesses agree. Direct enumeration also agrees in ten small settings. The independent program checked 34,720 field and target relabelings and rejected 28 malformed inputs. The main program passed eight semantic test methods. See the [independent review](independent_review.md).

The documented procedure reproduced the result files exactly in a fresh directory. This is computational verification, not human review. The [failed-check record](failed_checks.md) retains an initial path error before the main program was created. No failed result was removed from the analysis.

## Discussion

Repeated correct values provide less evidence than a shared record version. A full revision guard has a conditional guarantee here: equal revisions imply zero intervening writes, so every read concerns one constant record. Its cost is conservative rejection. An ideal final snapshot can accept a correct final record despite earlier changes.

A field called “updated” need not cover all task fields. Google states that reminder changes do not change the Calendar event's `updated` value. Since the prior account contract checks reminders, that timestamp alone cannot provide the full-revision premise. This is a documentation-based limit, not a newly observed provider fault. [Google Events reference](https://developers.google.com/workspace/calendar/api/v3/reference/events)

Google documents conditional requests with ETags. This study does not measure their concurrency behavior. A content-based validator can return the same token when content returns. This is an inference from the permitted content-hash design in RFC 9110, not a measured Calendar result. Equality alone does not establish a never-reused history counter. Cache freshness also does not prove that the origin stayed unchanged. [Google version guide](https://developers.google.com/workspace/calendar/api/guides/version-resources); [RFC 9110, Section 8.8.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8.1); [RFC 9111, Section 4.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.2)

A practical completion rule must state its record identity, field coverage, observation source, and time claim. Without verified shared-state evidence, separate field matches do not establish a coherent snapshot. A later write can also invalidate a correct snapshot after its observation time.

## Limitations

These are synthetic finite sets, not sampled users, agents, or websites. No confidence interval or significance test is appropriate for these exact counts. Uncertainty concerns model fit and omitted behavior. History sets change when scans or write bounds change. Their ratios do not estimate the causal benefit of another scan.

Binary fields omit wrong-value types. The model omits caches, replicas, record replacement, permissions, parsing errors, missing fields, multi-field transactions, and network faults. A delayed revision update would break a key premise. No later write occurs before the scored decision. No rule proves indefinite persistence. There is no measured latency, production failure rate, or general agent improvement. There is no training or test-set leakage because no model is trained or scored; the shared modeling assumptions can still make both implementations wrong about real systems.

## Ethical and misuse considerations

All inputs are synthetic. No user account data, event titles, credentials, or private records are included. The work gives small consistency examples, not exploit instructions. No paid service was used. Third-party sources are linked and attributed; their full text is not redistributed. No new reuse license is assigned.

## Reproduction and review status

Follow the [README](README.md). It lists commands, environment, file roles, and result schemas. The complete evidence includes code, the frozen inputs, raw terminal counts, witnesses, logs, and independent checks. The [review checklist](review_checklist.md) uses relevant NeurIPS guidance as a review aid. It does not claim conference approval or submission compliance.

Codex generated the study, code, and report. One separate agent reviewed sources and proofs. Another wrote the independent calculation and checked results and claims. The exact immutable model build was not exposed. Python 3.14.7 and the standard library ran the calculation. No human review or external peer review occurred. No university affiliation, endorsement, or certification is claimed.

## References

The linked primary sources above support the stated claims. Full bibliographic records and read scopes are in [references.bib](references.bib). The search record identifies the sections read; it does not imply a full-paper review of every source.
