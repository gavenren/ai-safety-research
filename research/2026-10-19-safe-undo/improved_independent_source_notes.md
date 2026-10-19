# Source notes for the improved-rule design

Search date: October 19, 2026. This is a limited design search, not a novelty proof. Prior related research and the original source record remain applicable. No source text was copied into the controller.

Searches:

- site:learn.microsoft.com azure architecture compensating transaction pattern record information undo retry idempotent
- site:aws.amazon.com builders library making retries safe with idempotent APIs same request intent

Primary sources read or rechecked:

1. Microsoft, Compensating Transaction pattern. https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction . The search returned the English content through the th-th and ar-sa URLs as well. The en-us result reports April 20, 2026 as its update date. Read the solution, problems/considerations and workload-design sections returned by search. Used for the limits of old-state restoration and the need for retained operation information. It does not validate the proposed browser controller or supply provider guarantees.
2. Malcolm Featonby, Making retries safe with idempotent APIs, Amazon Builders' Library. https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/ . Read the returned introduction, same-client-request-ID/different-intent section and conclusion scope. Official announcement: January 15, 2021, https://aws.amazon.com/about-aws/whats-new/2021/01/new-abl-article-making-retries-safe-with-idempotent-APIs/ . Used for uncertain effects and explicit request intent. No claim that Calendar or Notion browser controls implement its API contract.
3. Google Calendar, Get specific versions of resources. https://developers.google.com/workspace/calendar/api/guides/version-resources . Opened again; also read in the earlier design review on this date. API ETags concern resource versions and conditional modification. This is not a native X-field command history or proof of browser atomicity.
4. Notion, Page object. https://developers.notion.com/reference/page . Opened again; also read in the earlier design review on this date. Page identity and edit metadata do not supply the complete command history assumed by the test log.

The new contribution, if the tests pass, is a reproducible paired production-account case series that includes incomplete log, post-seal field mismatch, and faulty browser actuator cases. The controller is built from established ideas. The study must keep the complete-log assumption and limited final-state guarantee visible.
