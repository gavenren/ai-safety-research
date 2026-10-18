# When a success reply arrives before a duplicate: finite memory in agent retries

Date: October 18, 2026 (America/Toronto)  
Study type: exact synthetic event audit  
Review: separate agent checks; no human review or peer review

## Abstract

A stable request key prevents duplicates only while the receiver can recognize it. We test seven fixed retry rules with finite request memory, lost replies, delayed requests, and reordered arrivals. The main corpus contains 18,360 assigned scenarios across 60 settings, giving 128,520 policy runs. A separate broken-bound test adds 2,401 runs. In the planned primary setting, sending retries only before a cutoff still produces 162 duplicate cases among 729 assignments. In 36 cases, the count is one at the first success reply and becomes two later. The rule with a correct delay margin and the rule with a receiver-enforced deadline prevent duplicates in the main corpus, but can lose completion opportunities. An incorrect delay bound permits 14 duplicate cases in the stress set. The contribution is this reproducible regression corpus and exact comparison. The finite-retention problem is established prior work. These are not website or language-model failure rates.

## Research question and safety relevance

Can a send-time cutoff prevent duplicate effects when the receiver forgets old requests? Does one success reply establish that no request still in transit can create another effect?

An **effect** is one saved change made by a request. A **request key** identifies retries of the same logical operation. **Deduplication** uses that identity to avoid another effect. **Retention** is the period for which the receiver keeps the request record. A **receipt** is a success reply about one completed effect. A **regression corpus** is a fixed set of cases that can detect a known error after code changes.

An agent can receive a truthful receipt and still make an unsupported statement that the task had exactly one effect. The missing fact is whether other sent requests can still execute. This distinction matters for tools that create records or start external work. We test prescribed controller rules, not a model's ability to choose or follow them.

The [October 15 paper](../2026-10-15-computer-use-retries/report.md) already retained effects after a controller stopped. Its synthetic deduplication control was ideal and permanent. The [October 17 report](../2026-10-17-repair-dependencies/report.md) tested repair decisions under concurrent field changes. The present study adds finite request-memory lifetime and distinguishes sending before a deadline from arrival before that deadline. It does not revise earlier account results or add live account trials.

## Related work and contribution

RIFL already states that deleting completion records on a fixed expiry can permit double execution after a long partition. Its lease and stale-request checks address this risk and can leave a detected uncertain outcome. Our small deadline model is not an implementation of RIFL. [Lee et al., 2015, Sections 3, 4.1–4.2, opening of 4.3, and 9](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf)

The AWS Builders' Library explains caller-provided identity, atomic recording of identity with effects, late requests, and service-specific retention. It also distinguishes repeated intent from an intentionally new operation. We keep one fixed payload and one intended effect. The New key baseline deliberately replaces identity; it does not test a process crash. [Featonby, *Making retries safe with idempotent APIs*](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

Current Stripe documentation illustrates why the contract must be version-specific. For API v1, keys can be pruned after at least 24 hours, and reuse after pruning starts a new request. This does not promise deletion at exactly 24 hours. API v2 describes a different 30-day replay contract, including updated responses and retries of failed or partly failed work. Neither API is tested here. Our exact expiry at `T` is an explicit model assumption. [Stripe API reference](https://docs.stripe.com/api/idempotent_requests), [API v2 overview](https://docs.stripe.com/api-v2-overview)

CapLease's effect guarantee depends on a suitable idempotent sink, which is the service that makes the external change. Cordon separates durable local state from uncertain external effects and uses conservative recovery rules. These works already cover stronger identity and recovery mechanisms. We do not test, improve, or refute them. Both cited versions are preprints; conference acceptance was not independently checked. [Xu et al., 2026, Problem Formulation and Transactional CapLease](https://arxiv.org/html/2608.01710v1), [Chen et al., 2026, Sections 4.1–4.6 and opening of 5](https://arxiv.org/html/2606.17573v1)

The [source record](source_search.md) gives queries, dates, exact read scopes, and further leads. The source reviewer read only the listed sections; code and empirical results from these papers were not reproduced. Our contribution is the explicit transport corpus, paired costs, complete event traces, boundary controls, and minimum examples. No new protocol, first discovery, provider defect, or general novelty priority is claimed. A limited search cannot prove novelty.

## Method

The [plan](analysis_plan.md) and [configuration](config.json) were frozen before implementation. The [manifest](input_manifest.json) records their hashes and time. No frozen input changed. This is a local plan record, not external preregistration.

One client wants one append effect. There are three send slots at times `0`, `s`, and `2s`. Time is measured in integer **ticks**, which are synthetic units. Each slot is assigned either a permanent drop or arrival after a delay from zero through `D`. Each delivered request also has a lost or immediately visible success reply. The controller cannot inspect future outcomes. Transport does not copy requests.

A received request either appends one effect or returns the stored result for its key. The receiver checks identity and saves the effect and request record as one **atomic event**, with no intervening operation. A finite record created at time `c` is valid only while `arrival time - c < T`. At equality it expires. A hit does not renew its retention period. A reused key after expiry can create another effect.

A visible first success stops later sends. It does not cancel messages already sent. Every sent request is processed or permanently dropped before the final audit. Arrivals from earlier sends run before a send at the same tick; tied arrivals use slot order. A zero-delay arrival follows its own send. All three slot decisions, including skipped slots, remain in the trace. The final event time includes those decisions. This bookkeeping convention was fixed before enumeration.

The model has no separate queue after admission, partial effect, crash, other writer, payload change, key collision, or clock error. Rejected receiver deadlines produce no success feedback. Effect numbers are synthetic audit identifiers. They are not a real service's global count field.

## Seven rules

The initial request is always sent. All rules stop new sends after the first visible success.

| Rule | Retry and receiver behavior |
| --- | --- |
| No retry | Send only the initial request. |
| New key | Permit all three slots; use a distinct key for each attempt. |
| Stable key | Permit all slots; reuse one key with finite retention. |
| Send cutoff | Reuse one key; send a retry only at `t<T`. |
| Delay margin | Reuse one key; send a retry only at `t+B<T`, where `B` is the assumed delay bound. |
| Receiver cutoff | Use Send cutoff; also reject every arrival at `t>=T`, including a late initial request. |
| Permanent | Permit all slots; reuse one key whose record never expires. |

Receiver cutoff uses one absolute deadline from the operation's origin, not a renewed deadline per retry. It requires receiver support. Permanent assumes permanent receiver memory. Delay margin requires a correct bound from send to the atomic handling event. A client-side label or browser check does not create these capabilities.

The main grid uses `T` in `{1,2,3,4,5}`, `D` in `{0,1,2,3}`, and `s` in `{1,2,3}`, with `B=D`. There are `q=2D+3` transport codes per slot and `q^3` assignments per setting. Seven rules run each assignment on separate fresh states. Different unused slot codes retain their multiplicity. Counts describe this corpus, not a natural distribution of delays or failures.

The separate stress set uses `T=3,D=2,s=1,B=1`. It deliberately violates the assumed delay bound. It is not included in the main results. The primary display and the cost example below were selected in the frozen plan.

## Measures and decisions

A **duplicate** means final effect count greater than one. **Confirmed** means a success receipt was seen. **False exact claim** scores a hypothetical controller that promotes that receipt into a terminal claim of exactly one effect, when the final count is greater than one. The service receipt itself remains truthful.

A **future-only false claim** has count one at the first receipt and more than one after all sent requests finish. A **late duplicate** is a second-or-later effect after that receipt in event order, including a later event at the same tick. A **clean confirmation** has a receipt and exactly one final effect. A **miss** has no effect. We also retain unconfirmed outcomes and resource counters. These labels overlap; they must not be added as disjoint failures.

Five planned tests ask whether stable identity and a send cutoff can fail; whether the four complete controls avoid duplicates under their assumptions; whether a false exact claim can arise only after a receipt; whether safe cutoffs lose completion opportunities; and whether a broken delay bound defeats Delay margin. All five pass in the declared corpus.

## Results

There are 128,520 main runs and 2,401 stress runs. The full package contains 130,921 traces, 575,415 logged events, 427 aggregate rows, 427 paired rows, and 356 minimum examples. The main grid has 18,360 scenarios; stress has 343. Full results are in [results.csv](results.csv) and [traces.jsonl.gz](traces.jsonl.gz).

### Planned primary setting

Use `T=2,D=3,s=1`, with 729 assignments per rule.

| Rule | Duplicate cases | Receipts seen | False exact claims | Future-only false claims | No effect | Clean confirmations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| No retry | 0 | 324 | 0 | 0 | 81 | 324 |
| New key | 520 | 604 | 408 | 168 | 1 | 196 |
| Stable key | 272 | 604 | 198 | 78 | 1 | 406 |
| Send cutoff | 162 | 504 | 99 | 36 | 9 | 405 |
| Delay margin | 0 | 324 | 0 | 0 | 81 | 324 |
| Receiver cutoff | 0 | 225 | 0 | 0 | 315 | 225 |
| Permanent | 0 | 604 | 0 | 0 | 1 | 604 |

Source: the complete primary rows of results.csv. In this setting, Delay margin permits no retry because `D>=T`. It is therefore equivalent to No retry. Receiver cutoff can also reject the first request; its much larger miss count follows from its different acceptance contract.

The Send cutoff result includes 63 cases already duplicated at the first receipt and 36 that become duplicated later. These disjoint groups sum to its 99 false exact claims. Another 63 duplicate cases have no visible receipt. No retry, Delay margin, Receiver cutoff, and Permanent have zero duplicates and false exact claims in every main setting. Zero-error settings for weaker rules are retained in the data.

### A success before a later duplicate

The primary minimum example for Send cutoff uses codes `(7,2,0)`. Code 7 gives the first request delay three and a lost reply; code 2 gives the retry immediate arrival and a visible reply. The last slot is unused.

| Time | Event | Total effects |
| --- | --- | ---: |
| 0 | Send the first request. It remains in transit. | 0 |
| 1 | Send a retry before the cutoff. It arrives, creates effect 1, and returns success. | 1 |
| 2 | Skip the last slot. The first request is still in transit. | 1 |
| 3 | The first request arrives. The record created at time 1 has expired. It creates effect 2. | 2 |

There is no false service reply and no transport duplication. The unsupported step is treating the receipt as proof that no earlier sent request can still act.

Stable key and Send cutoff also have a cached-reply case in this corpus. At `T=4,D=2,s=1`, codes `(1,6,5)` create effect 1 at time 0 with a lost reply. Retries are sent at times 1 and 2. At time 3, the second request returns a cached success. That hit does not renew the record. At time 4, the third request arrives at exact expiry and creates effect 2. This example was read from the already enumerated corpus to illustrate the same failure, not added as a new test condition.

### Cost and broken-bound tests

The planned cost setting uses `T=4,D=2,s=1`, with 343 matched assignments. Permanent has an effect in 342 and a visible receipt in 279. Delay margin has no effect in six assignments where Permanent has one, and no receipt in 48 where Permanent confirms. Receiver cutoff loses two effect opportunities and 16 confirmation opportunities on the same comparisons. [paired_results.json](paired_results.json) records all settings. These are finite paired outcomes, not general availability rates or measured time savings.

In stress, actual delay can be two while Delay margin assumes one. Among 343 assignments, it produces 14 duplicate cases and seven false exact claims. All seven are already duplicated at the first receipt. Receiver cutoff and Permanent still have zero duplicates. The safe-margin proof does not apply when its bound is false.

## Why the complete controls pass

No retry permits only one arrival, so it cannot produce two effects. Permanent retains the first effect's record for every later arrival with that key.

For Delay margin with `B>=D`, consider whether a retry is permitted. If none is permitted, only the initial request is sent. Otherwise, some positive send time satisfies `t+B<T`, so `D<T`. The initial request, if delivered, arrives before `T`; every allowed retry arrives by `t+D<=t+B<T`. The first effect time `c` is nonnegative, so its record cannot expire before `c+T>=T`. Every later arrival finds that record before expiry.

Receiver cutoff permits effects only before absolute time `T`. The same first-effect argument prevents expiration between accepted requests. This proof needs a fixed origin and atomic admission with effect. It does not cover work queued before a deadline and executed later.

The [derivations](derivations.md) also give closed-form controls. With `q=2D+3`, No retry has `q^2` misses and `(D+1)q^2` clean confirmations. Permanent has one miss and `q^3-(D+2)^3` clean confirmations per setting. New key, Stable key, and Permanent have identical send schedules and first-receipt times on each assignment. Their different effect counts are not a speed improvement.

## Validation and reproduction

The main event-queue program passed 11 test methods, including 22 malformed configurations. A separate agent wrote a tick-loop implementation from the frozen plan before reading the main results. It did not read or import the main code. Its controls include expiry equality, reordered arrivals, same-tick effects, complete draining, and larger valid delay bounds. The [independent review](independent_review.md) records the exact comparisons and review limits.

Run the commands in the [README](README.md). The release includes full raw traces, input hashes, minimum examples, proofs, environment details, and logs. The [failure record](failed_checks.md) retains authoring failures and corrections. No case was removed after its result was known. The fresh-copy reproduction record states which output files match byte for byte.

## Discussion and limitations

A retry decision needs both an operation identity and a valid receiver contract for that identity. A client stop is not cancellation of requests already sent. A success receipt proves one observed effect; further evidence is needed for terminal uniqueness when request memory can expire.

The tested retention and delays are small integer values. Exact expiry, instant visible replies, atomic effects, stable identity, and one client are assumptions. There is no provider-specific cache implementation, queued work after admission, task change, clock uncertainty, process restart, malicious transport, or other writer. Dropped requests never return. No real website, account, or language model was tested.

The equal weights of assigned codes do not give real failure probabilities. Unused suffixes multiply some event histories. Two programs can agree on a model that omits an important real behavior. The corpus is public and is not a held-out agent benchmark. There is no training or train/test leakage, statistical sample, p-value, or population confidence interval. Stronger receiver rules have stronger capabilities; their conditional safety is not proof that a browser can implement them.

## Ethical issues, rights, and AI use

All records are synthetic. No user records, credentials, private account data, or source paper text are included. No paid service or new paid API call was used. The examples support defensive tests and do not provide instructions for serious harm. Source claims are attributed. No external source code is redistributed and no new license is assigned to the user's work.

Codex generated the study, programs, and report. Separate agents reviewed sources and proofs and independently computed outcomes. The exact immutable model build was unavailable. Python and platform details are in [environment.json](environment.json). No human review, peer review, university affiliation, endorsement, or certification is claimed. The [review checklist](review_checklist.md) uses relevant NeurIPS guidance as a review aid, not conference approval or submission compliance.

## References

The six supporting sources are linked in Related work. [references.bib](references.bib) records authors, versions, dates, and read limits. Additional primary leads remain in source_search.md and do not supply experimental evidence for this study.
