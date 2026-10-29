# Source search

Search and access date: 2026-10-29. Codex agents searched public primary sources during question selection and related-work review. The search is limited. It does not establish that this comparison is new.

## Exact queries

The following strings preserve the queries as sent, including the first two `site.` spellings. Unless stated otherwise, no domain filter was set.

1. `site.docs.stripe.com billing meters correct usage events adjustments cancellation ordering`
2. `site.cloud.google.com billing export corrections usage cost negative correction`
3. `site:opentelemetry.io metrics data model cumulative monotonic correction revision`
4. `site:docs.stripe.com billing subscriptions usage-based record-usage meter event adjustment correct usage`
5. `site:docs.stripe.com webhooks event ordering duplicate events`
6. `site:docs.stripe.com api billing meter event adjustment cancel`
7. `meter event adjustments cancel usage` — domain filter: `docs.stripe.com`.
8. `webhooks event ordering handling duplicate events` — domain filter: `docs.stripe.com`.
9. `external versioning out of order version deletes` — domain filter: `elastic.co`.
10. `"usage" "corrections" "revision" accounting agents arxiv`
11. `"last writer wins" "register" "timestamp" Shapiro 2011 CRDT`
12. `Lindley recursion reflected random walk max partial sums queue primary paper`
13. `site:arxiv.org Lindley recursion reflected random walk minimum partial sum`
14. `Lindley 1952 theory queues single server pdf`
15. `site:arxiv.org "Sn" "minimum" "Lindley" reflection`
16. `site.cloud.google.com billing export corrections usage cost adjustments negation remonetization`
17. `site:docs.stripe.com billing meter event adjustments cancel events`
18. `site:arxiv.org agent resource accounting corrected usage revision budget`

Queries 16–18 were made by the main agent. The response to a combined call containing queries 14–15 and an article open was truncated. It was not used as read evidence. The Boxma and Mandjes article was then opened separately.

## Selected sources and reading scope

These seven sources form the bibliography. See [source_review.md](source_review.md) for supported claims and rights.

| Key | Source and date | Reading scope |
| --- | --- | --- |
| googleStandardExport | [Google Cloud standard export](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/standard-usage), updated 2026-10-26 | Schema overview; adjustment fields; export time; Errors and adjustments; rights footer. |
| stripeWebhooks | [Stripe webhooks](https://docs.stripe.com/webhooks), live documentation | Event ordering; API versioning; Handle duplicate events. |
| elasticExternalVersion | [Elastic index API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-index), live documentation | Versioning; version and version_type parameters. |
| shapiro2011 | [Shapiro et al., EATCS 104](https://www.lip6.fr/Marc.Shapiro/papers/2011/CRDTs-beatcs-2011-06.pdf), June 2011 | Title and abstract; state-based convergence conditions; sections 3.1 and 3.1.1 with register specifications. Not a full proof audit. |
| boxma2022 | [Boxma and Mandjes](https://link.springer.com/article/10.1007/s11134-022-09863-7), 2022-08-29 | Abstract; introduction and related work; opening model definition; rights and metadata. Not the later analysis or proofs. |
| zhu2026 | [Zhu and Wang, arXiv v1](https://arxiv.org/html/2610.00349v1), 2026-09-29 | Abstract; section 4.7; section 11.5; appendix D.5; version metadata. Preprint; no full proof or implementation audit. |
| neuripsChecklist | [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), live guidance | Guidelines and items 1–16. Linked ethics and submission documents were not included in this read. |

The main agent also read Google errors and corrections, Stripe event order and duplicates, and the checklist. A separate source agent checked the scopes above. These are source checks, not independent empirical tests.

## Other leads

- [Stripe Meter Event Adjustment](https://docs.stripe.com/api/billing/meter-event-adjustment) and [create reference](https://docs.stripe.com/api/billing/meter-event-adjustment/create): read the overview, parameters, and pending example status. Not cited in the final paper.
- [Stripe recording usage](https://docs.stripe.com/billing/subscriptions/usage-based/recording-usage) and its linked `recording-usage-api.md`: read for asynchronous aggregation and event identifiers. Not cited.
- [OpenTelemetry Metrics Data Model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/): read the overview, sums, cumulative periods, monotonic flag, identity, and resets. Used to check terminology; not cited.
- [Comprehensive CRDT report URL](https://www.lip6.fr/Marc.Shapiro/papers/Comprehensive-CRDTs-RR7506-2011-01.pdf): direct open returned 404. Not treated as read. The accessible EATCS paper was used.
- [Stripe manage-billing-metrics URL](https://docs.stripe.com/billing/subscriptions/usage-based/manage-billing-metrics): inaccessible through the web tool. Unused failed lead.
- Other Lindley papers, secondary tutorials, Wikipedia, and a blog were discovery leads only. They were not used as evidence.

## Distinct scope

The October 26 repository study assumed monotone reports. October 27 added counter restarts and excluded downward corrections. October 28 changed the budget cap. This study fixes the cap and studies corrected charges for completed work. Its saved plan compares Net, GlobalClamp, ItemClamp, ArrivalReplace, MaxReplace, and RevisionReplace after complete closure.

Signed addition, reflection at zero, and ordered replacement are known mechanisms. The intended contribution is the declared comparison corpus, exact checks, and evidence. No source establishes the combined synthetic contract as a production service interface. No service, account, or physical compute meter was tested in this study.
