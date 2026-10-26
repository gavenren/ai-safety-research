# Source search and reading scope

Date checked: 2026-10-26, America/Toronto. Prepared by a separate Codex source-review agent. The initial source search preceded selection of the final experiment. The final question and model limits below follow the saved plan. No experiment was run by the source-review agent. No claim of global novelty follows from this limited search.

## Selected question

Can event-ID deduplication alone make cumulative usage reports safe for reservation accounting? How do six rules differ under delayed, repeated, and reordered progress and final reports?

A cumulative report states the total from the start of an identified operation. It is not a new amount to add. A progress report need not be a final result. These distinctions are established. The contribution is a complete, finite comparison of six specified rules. It preserves full event histories and separates accounting error, uncovered actual use, budget excess, and unnecessary refusal. All provider work finishes before report delivery starts. The audit uses actual final use, not possible future exposure. It does not test a live stream or an unresolved provider.

## Search record

All queries below were sent to web search on 2026-10-26. Search-result snippets were leads, not evidence of a complete source read.

1. `site.opentelemetry.io metrics cumulative delta temporality reset data model`
2. `site.docs.stripe.com webhooks event ordering duplicate events billing meters usage`
3. `site.inria.fr conflict free replicated data types state based counter merge maximum Shapiro`
4. `site.arxiv.org AI agent budget cumulative usage reconciliation reservation receipts 2026`
5. `site.docs.stripe.com meter event aggregation last sum count`
6. `"cumulative" "reservation" "usage" "idempotent" agent budget`
7. `"cumulative usage" "out of order" API`
8. `"cumulative" "terminal" "budget" "agent" receipt`

9. `cumulative usage reporting out of order duplicate monotonic counters budget reservations distributed agents`
10. `site.stripe.com meter events cumulative usage timestamp idempotency asynchronous aggregation`
11. `site.arxiv.org agent budget conservation cumulative receipts settlement`

Queries 1–8 were sent by the source-review agent. Queries 9–11 were sent by the main Codex agent. The main agent also read the OpenTelemetry page, the Stripe usage introduction and idempotency text, the Zhu and Wang page, and the NeurIPS claims guidance. This record does not imply full-source reading from those additional checks.

The search returned informal discussions, mirrors, product documents, design proposals, and papers. Only the original sources below support claims. Search ranking was not treated as quality evidence. Dates from search snippets were not treated as publication dates.

## Checked original sources

### 1. OpenTelemetry Metrics Data Model

URL: https://opentelemetry.io/docs/specs/otel/metrics/data-model/

Type: official specification; page shows OTel 1.62.0. No publication date was established. Checked sections: Overview; Sums; Single-Writer; Temporality; Resets and Gaps; Cumulative streams: handling unknown start time; Sums: Delta-to-Cumulative and its alignment issues. Sums and Temporality are stable; Resets and Gaps and Stream Manipulations are marked Development.

Supported use: the data model distinguishes interval deltas from cumulative totals. A cumulative sequence retains its start time. Resets and overlapping writers require extra identity and timing information. This supports explicit input semantics and the exclusion of resets if a simple maximum rule is tested. It does not establish that telemetry is an authoritative billing ledger or that an observation closes an operation. No OTel implementation was run.

### 2. Stripe webhook guide

URL: https://docs.stripe.com/webhooks

Title: Receive Stripe events in your webhook endpoint. Type: official documentation, live page checked on the access date. No publication date was established. Checked sections: Event ordering; Handle duplicate events; the nearby retry and API-version text.

Supported use: generated order is not guaranteed to be delivery order. Event IDs identify repeated deliveries. Distinct snapshot events can have the same second-level creation timestamp. The guide also describes separate Event objects for some duplicate situations. These facts motivate distinct tests for duplication and ordering. They do not show a defect in Stripe or supply a terminal usage contract for this model. No Stripe account was accessed or changed.

### 3. Stripe usage API and meter summary

URLs: https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage-api and https://docs.stripe.com/api/billing/meter-event-summary

Titles: Record usage for billing with the API; Meter Event Summary. Type: official documentation. No publication date was established. Checked usage sections: introduction, Idempotency, Event timestamps, Usage values, and the opening of Handle meter event errors. The short summary page was read in full, excluding linked pages.

Supported use: reported meter events are processed asynchronously. Aggregate summaries may lag events already received. Idempotency protects a repeated event submission. These are separate properties. The model must not infer absent usage or finality from a temporarily low aggregate. Meter events can use different aggregation contracts; do not describe Stripe values as the study's cumulative progress protocol. No invoice, payment, provider endpoint, or billing result was tested.

### 4. Shapiro, Preguiça, Baquero, and Zawirski (2011)

Title: Conflict-free Replicated Data Types. INRIA Research Report 7687, version 2; original 2011-07-19, revised 2011-08-25, from the PDF title page.

URL: https://www.lip6.fr/Marc.Shapiro/papers/RR-7687.pdf

Checked: title and abstract; Sections 2.1 through the sufficient-condition statement in 2.3; Section 4.1. The whole proof and remaining sections were not checked.

Supported use: state-based merge can use an idempotent, commutative, associative operation. The integer-counter example uses per-index maximum. Thus taking the greatest cumulative value for one unchanged writer identity is established practice. It is not a new algorithm. Convergence alone does not certify reservation release, truthful source values, or a global spending bound. No copied code or figure is needed.

### 5. Zhu and Wang (2026), closest budget paper

Title: Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation. Authors: Genliang Zhu and Chu Wang. arXiv 2610.00349v1. Page header date: 2026-09-29. Preprint; no peer-review status was verified.

URL: https://arxiv.org/html/2610.00349v1

Checked: abstract; Sections 5.5, 6.6, 11.2, 11.4, 11.5; invariant 8; Appendix D.5. The source's full proofs, code, and experiments were not reproduced.

Supported use: a complete final receipt can settle actual use and return its authenticated remainder. Pending observations do not close the obligation. Appendix D.5 already contrasts a partial final charge, repeated receipt, and conflicting second receipt. Section 11.5 discusses separately reserved chunks for streaming. The proposed study must credit these conditions. Its possible contribution is a distinct progress-message comparison artifact, not the terminal-settlement principle or a defect claim about this preprint.

### Examined lead: Schrock (2026), related protocol draft

Title: Bounded Capability Receipts and Durable Spend Control for Agent Actions. Author: Iman Schrock. Internet-Draft draft-schrock-ep-bounded-capability-receipts-06, 2026-09-09. Individual experimental draft; not an IETF standard or endorsement.

URL: https://datatracker.ietf.org/doc/html/draft-schrock-ep-bounded-capability-receipts-06

Checked: abstract; trust statements in Section 3; Sections 9 and 10.1–10.4; Section 11.1; implementation limitations in Section 19. No implementation or conformance test was run.

Supported use: authoritative reserved and consumed state must be updated in one state domain. Reconciliation keeps unknown external effects charged, and repeated terminal reconciliation needs the same outcome and evidence binding. Its provider-entry accounting is a different contract from a variable final-charge model. It is an examined lead. It is omitted from the report bibliography because the report does not use its distinct accounting contract. The search also returned older version 04; version 06 was read instead.

### 6. AgentScope Go proposal, close streaming design note

Title: [RFC] Agent-side harness for higher task goodput on shared inference services. GitHub issue 11 in agentscope-ai/agentscope-go, opened by public handle AlanFokCo on 2026-09-20. The issue was open and its body said Proposed when checked. An issue is not a paper or implementation result.

URL: https://github.com/agentscope-ai/agentscope-go/issues/11

Checked: status and scope; Sections 4.1–4.3; Section 5.C on streaming; evaluation scope. Linked implementation files and PRs were not inspected.

Supported use: the proposal already requires separation of settled, reserved, and unknown usage, and warns against adding cumulative stream usage more than once. It also distinguishes stream assembly from final usage accounting. This directly limits any new-method claim. The proposed test can give a compact executable comparison of these known conditions, but cannot claim a defect or measured performance of AgentScope.

### 7. NeurIPS Paper Checklist

URL: https://neurips.cc/public/guides/PaperChecklist

Type: official review guide, current page checked on the access date. Checked guidance for claims, limitations, theory and assumptions, reproducibility, code/data, experiment settings, and statistical reporting. Use as a review aid only. No NeurIPS approval or submission compliance is implied.

## Difference from local prior studies

The October 25 reservation-release report was read for its method and limits. It uses one correct final receipt, excludes partial charges and duplicate receipts, and compares release evidence after acceptance fencing. The selected progress-message corpus tests a different accounting layer, after provider work has ended. The October 23 report's abstract, question, related work, and method were read. It concerns receipt history versus later record state and new-key writes. The October 18 report's question, measures, results, and discussion were inspected by targeted text search. It concerns finite request memory and later duplicate effects. Do not repeat those as new observations.

## Design boundaries to preserve

1. Keep progress and final messages distinct. A larger cumulative observation does not alone prove that no further usage can occur.
2. Use one exact operation identity and one unchanged counter epoch if testing a maximum rule. Counter reset, multiple writers, refunds, corrections, and changing prices need separate rules.
3. Define the reserved amount as an enforced upper bound, or clearly state that a real hard bound is not established.
4. Score known reported usage separately from the actual finished use. The final value is audit truth and must not enter a controller before its final report. This study does not score possible future use.
5. Treat zero-error finite results as conditional model results. They are not provider, website, or model-choice failure rates.
6. Do not use an idempotent merge as proof that its update and the budget release were committed atomically. State the atomicity assumption or test its failure separately.
7. Do not present max merge, retained unknown reservations, or at-most-once terminal settlement as new mechanisms.

## Final model limits

The model has one fixed operation identity and counter start. It has one progress report, one final report, exact duplicate deliveries, and one later job. Values are true and monotone, and the reservation is a correct enforced cap. The provider has completed before any delivery in the model. There are no resets, downward corrections, false reports, conflicts, missing final delivery, crashes, or concurrent local updates. Local bookkeeping and admission are atomic. These assumptions isolate report interpretation. They do not establish a production safety guarantee.

## Search limits and rights

This is a focused search. It cannot prove the absence of an earlier identical test corpus. Informal posts, documentation mirrors, and uninspected code results were excluded as evidence. Search leads include BAGEN, draft-hardt-aauth-budgets-00, AgentLedger, tinyagents, agent-sdk, OpenProgram, and other product notes; their source contents were not checked for this draft and must not be cited as if read.

Only links, bibliographic facts, and short paraphrases are needed. No source paper, source code, table, or figure is copied into the proposed package. This search assigns no new license to third-party material or the repository owner's work. Source access did not require a login, paid service, or account change.
