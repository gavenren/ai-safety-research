# Source search
Search and access date: 2026-10-22. Searches occurred before this plan was frozen.
Search terms:
- site.aws.amazon.com builders library making retries safe idempotent APIs same client request id different intent
- site.stripe.com docs idempotent requests parameters mismatch idempotency key

Primary sources read:
1. Malcolm Featonby. Making retries safe with idempotent APIs. AWS Builders Library. Undated page. https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
Read the substantive article, including client request IDs, late requests, and same ID with different intent. It describes caller-scoped IDs, atomic recording, and rejection of changed parameters. These are established methods.
2. Stripe. Idempotent requests. Current API reference. https://docs.stripe.com/api/idempotent_requests
Read the complete short reference. API v1 stores the first result and checks changed parameters. It also describes expiry, which this study excludes. The model does not claim Stripe uses a global namespace or has a fault.
3. NeurIPS. Paper Checklist. https://neurips.cc/public/guides/PaperChecklist
Read the guide as a review aid. It is not conference approval.

Repository comparison: The 2026-10-18 retry-retention study used fixed payloads. This study excludes retention and varies account scope, operation ID, and immutable payload. It is a distinct finite regression set, not a new idempotency method. A limited search cannot prove novelty.
No source text, figures, or code are redistributed. Sources are paraphrased and linked. No new license is assigned to the owner's work.
