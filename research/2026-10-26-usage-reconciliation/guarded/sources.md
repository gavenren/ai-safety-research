# Sources for the guarded ledger extension

Checked on 2026-10-26 before production writes. This is an owner-requested repair and test of the same paper. A limited search does not establish novelty. The contribution is an implementation and a selected production-record check of known accounting and request-control principles.

## Search record

Queries: `site.opentelemetry.io specifications metrics cumulative monotonic sum start time`; `site.stripe.com idempotency request retries same parameters`; `site.sqlite.org isolation serializable transactions BEGIN IMMEDIATE`.

The search returned primary documentation and secondary copies. Only the original sources below support the extension. No claim depends on a secondary copy. The earlier paper and its source search were also read. No separate new research mechanism is claimed.

## Checked primary sources and uses

- [OpenTelemetry Metrics Data Model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/). Read the cumulative temporality, start-time, reset, and overlap sections. Cumulative points repeat a common start and contain overlapping use. This supports keeping the counter identity fixed and refusing to add every cumulative amount. The maximum rule assumes truthful monotone values in one unchanged counter; it is not a rule for arbitrary metric types or resets.
- [Stripe Idempotent requests](https://docs.stripe.com/api/idempotent_requests). Read the current API v1/v2 explanation. API v1 retains an executed request result for retries. API v2 has different completion semantics. This source motivates stable request identity only. Stripe was not used for these tests, and the local ledger does not supply a Google server-side idempotency guarantee.
- [SQLite Isolation](https://www.sqlite.org/isolation.html). Read isolation between connections, single-writer serialization, and BEGIN IMMEDIATE. The implementation uses one local database and a transaction to combine capacity check with reservation. The source does not prove correct use of the database or atomicity with a remote Google write.
- [Drive files resource](https://developers.google.com/workspace/drive/api/reference/rest/v3/files). Read ID, name, parent, created-time, and trashed fields. Names alone are not identities. A child can be in Trash through its parent.
- [Drive trash and delete guide](https://developers.google.com/workspace/drive/api/guides/delete). Read recoverable trash and permanent deletion distinctions. Test cleanup uses Trash and does not purge files.
- [Calendar events resource](https://developers.google.com/workspace/calendar/api/v3/reference/events). Read saved fields, visibility, transparency, reminders, attendees, and cancellation status. Exact-ID reads check actual event state. The primary calendar is the bounded test scope.
- [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). Read claims, limits, reproducibility, ethics, and transparency guidance. This is a review aid, not conference approval or a claim of submission compliance.

These are living documents, checked on the stated date. Publication dates are not assigned when the page does not provide a clear stable date. The study keeps the actual test data and code fixed. The source pages were read for the sections stated above; this file does not claim a full audit of each provider or specification.
