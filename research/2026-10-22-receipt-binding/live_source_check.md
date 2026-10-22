# Primary source verification

Date: 2026-10-22. The pre-execution search terms and source scope are retained in `live_design.md`. This later verification checks the citations in the production extension. It does not move the experiment plan's freeze time or claim a new novelty search.

- Malcolm Featonby, AWS Builders' Library, *Making retries safe with idempotent APIs*. Read the sections on stored request IDs, parameters, retention, and different intent under the same ID. Used only for the established parameter-binding principle. https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- Stripe, *Idempotent requests*. Read current API v1 request matching, saved response, and parameter conflict guidance. Version 2 behavior was not used in the experiment or the claims. https://docs.stripe.com/api/idempotent_requests
- Google Drive, *REST Resource: files*. Read ID, name, parent, sharing, trashed, and version fields. The public API's complete schema is not asserted to be the connector's output. https://developers.google.com/workspace/drive/api/reference/rest/v3/files
- Google Calendar, *Events*. Read native ID, description, all-day start/end, exclusive end, attendee, visibility, and reminder fields. Description can contain HTML; the experiment does not normalize HTML. https://developers.google.com/workspace/calendar/api/v3/reference/events
- NeurIPS, *Paper Checklist*. Used claim support, reproducibility, limitations, ethics, and disclosure items as a review aid. No approval or compliance certification is implied. https://neurips.cc/public/guides/PaperChecklist

These sources are primary service or conference documents. No preprint is cited in the extension. No source text was copied into the report beyond short technical labels and field names. All additional statements about observed records come from this experiment's retained evidence.
