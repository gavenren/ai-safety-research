# Source search and claim limits

Access date: October 18, 2026 (America/Toronto). Codex began this search before the plan was selected. Additional closest-work checks continued after selection. This record was completed after the plan freeze; it is not a frozen experimental input. No source code or provider experiment was run.

## Search method and terms

This was a limited primary-source search. It was not a systematic review. Search results from commentary sites were used only to locate primary work. The search does not prove novelty.

Queries used on October 18:

- `site.usenix.org RIFL implementing linearizability large scale low latency systems exactly once RPC leases`
- `site.docs.stripe.com idempotent requests 24 hours keys pruned`
- `site.aws.amazon.com builders library making retries safe idempotent APIs late arriving requests`
- `site.docs.stripe.com api-v2 idempotency 30 days 24 hours`
- `site.docs.aws.amazon.com SQS FIFO deduplication interval 5 minutes retry`
- `site.arxiv.org idempotency retry finite retention agent crash operation identity`
- `site.arxiv.org "idempotency" "retention" agent`
- `site.arxiv.org "retry" "expiry" "agent" transaction`
- `site.arxiv.org "idempotency" "crash" "agents"`
- `"CapLease" idempotency retry retention`
- `site.arxiv.org "idempotency" "retention" "2026"`
- `site.arxiv.org "idempotent" "expiry" "2026"`
- `site.arxiv.org "deduplication" "expiry" agent`

## Relation to prior reports

The [October 15 report](../2026-10-15-computer-use-retries/report.md) tests delayed append effects and delayed reads. Its positive control uses ideal permanent deduplication. The [October 17 report](../2026-10-17-repair-dependencies/report.md) tests repair decisions under concurrent field changes. Both were read. This study adds finite request-memory lifetime and the difference between send time and arrival time. It retains the earlier practice of checking all effects after the client stops.

The proposed contribution is this exact regression corpus, matched counts, boundary examples, and proofs under the stated model. Finite-retention failure, stable operation identity, and uncertain outcomes are established issues. No first discovery, new protocol, or improvement over a named system is claimed.

## Supporting references

The six supporting references are listed in [references.bib](references.bib). The stated read scope is the material used for claims, not a claim that every part of each paper was checked.

### RIFL: Lee et al., 2015

URL: https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf

*Implementing Linearizability at Large Scale and Low Latency*. SOSP 2015, October 4–7. DOI: 10.1145/2815400.2815416. Conference paper.

Read: abstract; Sections 1–3; Sections 4.1–4.2; opening of Section 4.3; Section 9. No code or performance experiment was reproduced.

RIFL couples an operation's completion record to its effect. Section 3 already explains that fixed record expiry can permit double execution after a long partition. Its lease checks reject stale retries, while some outcomes remain uncertain. Section 9 limits guarantees when a client loses state. Our fixed deadline rule does not implement RIFL.

### AWS: Featonby

URL: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

*Making retries safe with idempotent APIs*. Official engineering guidance. The read page body gives no publication date. Its linked PDF has a 2020 copyright notice; this is not treated as a verified publication date.

Read: article body, including unique request IDs, atomic token/effect storage, equivalent responses, late requests, and changed intent. Examples were not run or copied.

The article uses caller-supplied identity to state intent. It treats identity storage and mutation as one atomic operation. Retention requirements differ across services. Its EC2 example retains request knowledge for resource lifetime plus a further interval. It does not provide a universal fixed timeout. Changed parameters under an existing identity can cause a validation error.

### Stripe: API v1

URL: https://docs.stripe.com/api/idempotent_requests

*Idempotent requests*. Official live API reference. No page date is shown.

Read: all substantive text, retrieved Markdown lines 16–23. The introductory tool-installation text was not followed.

API v1 saves results after endpoint execution starts. A key can be removed after it is at least 24 hours old. Reuse after pruning creates a new request. This is not deletion at exactly 24 hours. Validation failures and concurrent conflicts can occur before a result is saved. Our exact expiry and instantaneous effect are model assumptions, not a Stripe model or measured defect.

### Stripe: API v2 scope check

URL: https://docs.stripe.com/api-v2-overview

*API v2 overview*. Official live guide. No page date is shown.

Read: Idempotency and Idempotency differences between API v1 and API v2, retrieved lines 129–152. The `.md#idempotency` URL first returned an internal access error; the ordinary page URL worked.

V2 requires the same key, API, and account or sandbox for the replay rule, within 30 days. Its response behavior differs from v1. The v1 24-hour statement must not be applied to all Stripe APIs. No API was called.

### CapLease: Xu et al., 2026

URL: https://arxiv.org/html/2608.01710v1

*Beyond Single-Use Tokens: Durable Authorization State for Replay-Resistant LLM Agent Actions*. arXiv:2608.01710v1, August 3, 2026. Preprint.

Read: abstract, introduction, Problem Formulation and Semantic Replay, and Transactional CapLease, including Proposition 1 and its proof sketch. Nearby experimental text was returned but was not independently verified.

The paper separates one authorization's identity from fresh token identifiers. Its external-effect bound requires sink idempotency with a stable key. A counterexample in our finite-memory receiver is not a CapLease defect or a test of its implementation. We do not reproduce or compare its numerical results.

### Cordon: Chen et al., 2026

URL: https://arxiv.org/html/2606.17573v1

*Cordon: Semantic Transactions for Tool-Using LLM Agents*. arXiv:2606.17573v1, June 16, 2026. Preprint. A future conference header in the manuscript is not independent evidence of acceptance.

Read: abstract; Sections 4.1–4.6; opening of Section 5 through its idempotency-table paragraph. No implementation or result was reproduced.

Cordon records task and effect state and separates local state promotion from external effects. Its recovery path treats a possible external effect conservatively. The present study does not introduce an effect outbox, durable task identity, or Cordon's recovery protocol.

## Additional primary search leads

These sources limit novelty claims. They are not the source of our numerical results.

- [Zhu and Wang, *Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation*](https://arxiv.org/html/2610.00349v1), arXiv:2610.00349v1, submitted September 29, 2026, preprint. Read abstract; Sections 3.3–3.6, 4.4–4.9, 6.6–6.7; the ambiguity-retention lemma; Section 11.3. It requires a fenced idempotent gateway and authoritative evidence for uncertain effects. A fence does not cancel prior acceptance. We did not verify its full proofs, code, or numerical results.
- [Amazon SQS SendMessage](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessage.html), official live API reference. Read MessageDeduplicationId, retrieved lines 82–107. Also read the short [Exactly-once processing](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html) guide and the [outage recovery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/designing-for-outage-recovery-scenarios.html) text returned by search. The five-minute queue deduplication interval does not establish exactly-once effects in a separate consumer. No queue was tested.
- [AcquireBound](https://arxiv.org/html/2609.14744v1), arXiv:2609.14744v1. Read abstract and scope, Section 2, and the returned crash/recovery definition and safety lemma. This is a less direct source about acquired authority, not a finite-retention test. No quantitative claim from it is used.
- [Jena and Dalal, Idempotency-Key draft-07](https://www.ietf.org/archive/id/draft-ietf-httpapi-idempotency-key-header-07.html), revision October 15, 2025. Read metadata and Sections 2.2–2.6. The [live tracker](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/) marks it expired and archived on April 18, 2026. It is not an RFC. Its resource-defined expiry discussion is a standards-work lead, not a conformance requirement for this study.
- [Mathew Stevens, durable-agent-outbox](https://github.com/mstevens843/durable-agent-outbox), live software README. Read its problem, identity, uncertain-state, and evidence sections; opened its [motivation page](https://github.com/mstevens843/durable-agent-outbox/blob/main/docs/WHY_THIS_EXISTS.md). The documentation already discusses finite provider memory and receipts. We did not check its code, run its tests, or verify its reported numbers. Its broad Stripe wording is not used as provider evidence.

## Use and rights

No source paper or code is copied into the package. The text above is a short paraphrase with attribution. No new license is assigned. The provider pages were checked for their stated contracts only. No production behavior, account record, or model behavior was measured. The source and claim review must check the final report against these read scopes.
