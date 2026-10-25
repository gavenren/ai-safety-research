# Source search: reservation release after uncertain execution

Date: 2026-10-25, America/Toronto. Search and reading by a separate Codex agent, with three search terms supplied by the lead. The final choice below was updated after the lead saved the plan. No experiment or external account change was performed by this source agent.

## Candidate question and decision

Candidate: When is it safe to make a reserved unit available again after the controller stops waiting for an external action?

The search found direct prior work on almost every proposed mechanism. A generic demonstration that timeout refunds can exceed a budget would be a repetition. A useful contribution must be limited to a new, fully specified regression corpus and its comparison of evidence boundaries. Do not claim a new release algorithm, impossibility result, or priority.

Final choice: [the frozen plan](plan.md) compares Timeout, ZeroObservation, FenceOnly, ClosureCertificate, and TerminalOnly over one common set of event orders. It separates acceptance, charge, observation, fencing, and receipt delivery. It scores actual budget breaches, exposure, uncovered liability, and safe-feasible refusals separately. The proposed contribution is the exact, independently checked test corpus and its traces. The rules are established mechanisms. This study does not test execution deadlines or a named protocol implementation. Its certificate includes a model-specific terminal zero-charge case for accepted work; it is not the cited preprint's never-accepted certificate. See [the source review](source_review.md).

## Search terms

The web search used these exact terms on 2026-10-25:

1. `AI agent budget conservation reservation timeout release external side effects cancellation settlement`
2. `site.aws.amazon.com builders library timeout does not mean side effects not happened`
3. `distributed reservation release timeout fencing external effect budget conservation`
4. `"agent" "reservation" "no-effect" "timeout"`
5. `"budget" "reservation" "fence" "settlement" AI`
6. `"timeout" "budget" "reservation" "formal" agent safety`
7. `site.arxiv.org agent budget reservation timeout reclaim late settlement conservation`
8. `site.aws.amazon.com builders library timeout retry side effects idempotent cancellation`
9. `site.research.google.com Chubby sequencer lock delayed request lease`

The source agent ran searches 1–6. The lead supplied searches 7–9 from its work on the same date.

The first broad results included commercial advice and source mirrors. Technical claims below use original papers or official documentation. The search is limited and cannot establish global novelty.

## Closest primary sources and exact reading scope

### 1. Zhu and Wang, 2026

[Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation, v1](https://arxiv.org/html/2610.00349v1). Preprint. Source header reports 2026-09-29. Accessed 2026-10-25.

Checked title/abstract, Sections 4.4–4.9, 6.1, 6.5, 9.3–9.5, 11.4–11.5, 13.2–13.4, Appendix B actions, and Appendix D.5. These sections directly cover timeout refunds, uncertain holds, terminal evidence, fences, partial charges, and maximum-charge assumptions. The paper already reports timeout-refund mutants and two-process SQLite fault tests. It distinguishes internal accounting from external effects and says a fence alone does not release accepted work. A weak rule selected for our model is not evidence that its full protocol fails. The proofs, artifact code, and numerical results were not independently reproduced.

### 2. Saha, AADP draft 04, 2026

[The Agent Action Decision Protocol (AADP): Per-Action Authorization for AI Agents](https://datatracker.ietf.org/doc/html/draft-saha-aadp-04). Canonical IETF-hosted individual Internet-Draft, published 2026-09-27; work in progress, not an RFC or IETF-endorsed standard. Accessed 2026-10-25.

Checked abstract, status, Sections 1.1–1.2, 2, 4–4.1, 5.3, 6–7, 9, and relevant Section 17 paragraphs. Section 4 calls for explicit expiry release when an `execute_within` deadline passes without a report. Section 4.1 commits reservations on reported timeouts. Section 7 acknowledges uncertain downstream effects and forbids blind reissue. This was a question-selection lead. The frozen plan does not model the deadline or test this protocol. Keep this source in the search record, without a main-result claim about AADP. We have not tested a conforming implementation or resolved every interpretation of the deadline. No source code or normative text is copied into our artifact.

### 3. AWS Builders' Library, 2019

[Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/), Marc Brooker. The current page redirects to [AWS Builder Center](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter). The page gives 2019-12-05 as publication and modification date. Accessed 2026-10-25.

Read the introduction, timeout section, and opening retries discussion. A timeout bounds a caller's waiting; failure does not prove an absence of side effects. This supports the uncertainty premise. It does not specify the candidate budget algorithm or establish our result counts.

### 4. Google Cloud long-running operations

[Package google.longrunning](https://docs.cloud.google.com/translate/docs/reference/rpc/google.longrunning). Official API reference. Accessed 2026-10-25; no publication date used.

Read Operations, CancelOperation, DeleteOperation, GetOperation, and WaitOperation. Cancellation starts an asynchronous best-effort attempt. Clients must check its result. Deleting the operation record does not cancel the action. A successful wait response can still precede completion. These statements concern this API contract, not all Google products or the user's connected accounts. No live Google operation was created or cancelled.

### 5. Google Cloud Run request timeout

[Configure request timeout for services](https://docs.cloud.google.com/run/docs/configuring/request-timeout). Official documentation. Accessed 2026-10-25; no publication date used.

Read the opening timeout semantics and timeout-period guidance. An HTTP timeout closes the connection but need not terminate the container. Processing can continue. This is a concrete supported example of why response termination differs from execution termination. No Cloud Run service was tested. Timeout values are not needed for the proposed model.

### 6. Burrows, 2006

[The Chubby lock service for loosely-coupled distributed systems](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf). OSDI 2006. Accessed 2026-10-25.

Checked title/abstract and Section 2.4, including the delayed request example, sequencers, and lock-delay. A recipient can reject an invalid generation; a delay without such a check is described as imperfect. This supplies established background for fencing. The proposed study does not implement Chubby or evaluate its service guarantees.

### 7. NeurIPS checklist

[Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). Accessed 2026-10-25. Read the current claims, limitations, assumptions/proofs, reproducibility, experiment details, statistics, and ethics/release guidance as a review aid. No NeurIPS approval or submission-compliance claim follows.

## Other checked pages and excluded leads

- [AIP-151: Long-running operations](https://google.aip.dev/151), created 2019-07-25: guidance checked. It points toward a progress token but is less direct than the operation API reference. Optional background, not required in the final bibliography.
- [Stripe Cancel a PaymentIntent](https://docs.stripe.com/api/payment_intents/cancel): opening cancellation semantics and return behavior checked. It specifies terminal behavior for eligible PaymentIntents. This is a contrasting endpoint contract; we did not perform a payment test. Exclude if the report has no Stripe-specific claim.
- Cloud Run troubleshooting was opened first; the configuration page was used for the direct timeout claim.
- Commercial articles, arXiv mirrors, and forum examples appeared in search results. Their snippets were not used as technical authority. No claim is based on them.

## Difference from repository studies

The October 24 shared-limit report ends at atomic local allocation and explicitly excludes external effects, expiry, and refunds. The October 22 cancellation report tests run tokens, restarts, and receiver order. It scores stale actions, not cumulative resource reuse after a prior accepted action remains unsettled. The candidate extension can join these boundaries while retaining that distinction. It must not relabel the older cancellation corpus as a new experiment.

## Design cautions for the lead

- Define the budget dimension. Cumulative use is not concurrency. Completed use must remain charged under a cumulative contract.
- Separate provider acceptance, occurrence, response delivery, and accounting settlement. A fence may stop new acceptance while leaving old accepted work live.
- A negative query is an observation at one instant unless the provider also closes the future acceptance path.
- A final zero-use result must be an explicit trusted assumption. Neither a local timer nor a sent cancellation request supplies it.
- Keep unsafe release and overspend separate. A bad release can occur without an observed breach when no competing job arrives.
- Preserve no-effect and early-completion controls. Measure conservative holds as an availability cost, not as a safety failure.
- Do not claim that finite schedules are natural failure rates or that a model measures an AI agent's choices.
- If the final model stays close to Zhu and Wang, state that the contribution is the exact comparison artifact, not the underlying mechanism.

## Rights and review scope

Use source links and short paraphrases. No source paper, figure, normative excerpt, or implementation was copied. No new license is assigned to the user's work. The AADP draft is subject to IETF Trust terms; linking to it does not apply those terms to independently written code. This source review does not validate code, counts, or publication.
