# Source review for the production website extension

Review date: 2026-10-29, America/Toronto. Reviewer: a separate Codex agent. No account records were read or changed by this reviewer. These notes give source scope and design limits. They do not verify any experiment result.

## Search record

Four search queries were run on 2026-10-29:

1. `site.developers.google.com drive api files version modifiedTime update etag`
2. `site.developers.google.com calendar api events sequence etag updated update`
3. `site.arxiv.org browser agent benchmark production websites state verification WebArena WebVoyager`
4. `site.rfc-editor.org rfc 5545 sequence revision significant changes`

The search found primary provider documentation, RFC 5545, and browser-agent research. Only the checked primary sources below support these notes. Third-party summaries and benchmark scores from search results were not used. This search is limited. It does not prove that the proposed extension is new.

## Checked sources

### D1. Google Drive files resource

- URL: https://developers.google.com/workspace/drive/api/reference/rest/v3/files
- Page date: last updated 2026-07-14 UTC. Read on 2026-10-29.
- Read scope: file ID, name, description, trash fields, modification time, quota bytes, version, ownership, and page license.
- Supported claims: a file name need not be unique in a folder. The `version` field is output only. It increases with server changes, including changes that a user cannot see. The `modifiedTime` field can be set. `quotaBytesUsed` concerns storage bytes and retained revisions.
- Study use: bind observations to the stable file ID. Do not use a name or a modification time alone as a safe revision key. A number in a folder name is study data. It is not a Drive charge or storage quota.
- Rights: page text is CC BY 4.0, except where stated otherwise. Code samples are Apache 2.0. Use short attributed paraphrases. No source code was copied.

### D2. Google Drive files.update

- URL: https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update
- Page date: last updated 2026-03-20 UTC. Read on 2026-10-29.
- Read scope: operation description, request type, response, and license.
- Supported claim: the API can change metadata or file content. It uses patch semantics. A caller should supply only the fields to change.
- Study limit: this API document does not show that a particular browser save succeeded. A fresh saved read is still required.
- Rights: CC BY 4.0 page text; Apache 2.0 code samples. No code was copied.

### C1. Google Calendar events resource

- URL: https://developers.google.com/workspace/calendar/api/v3/reference/events
- Page date: last updated 2026-07-07 UTC. Read on 2026-10-29.
- Read scope: event ID, etag, sequence, updated, start and end, reminders, transparency, visibility, and page license.
- Supported claims: `sequence` is a writable iCalendar sequence number. `updated` records changes to the main event data; a reminder change does not change it. `transparent` is the free-time setting. The event resource has separate start and end zone fields.
- Study use: a study revision label in the title must remain separate from `sequence`, `etag`, and `updated`. An event title is not a provider invoice. The rule does not measure Google billing or physical resource use.
- Rights: CC BY 4.0 page text; Apache 2.0 code samples. No code was copied.

### C2. Google Calendar resource versions

- URL: https://developers.google.com/workspace/calendar/api/guides/version-resources
- Page date: last updated 2026-09-11 UTC. Read on 2026-10-29.
- Read scope: etag description, conditional modification, conditional retrieval, error example, and page license.
- Supported claim: an etag can be used with `If-Match` to permit an update only when the retained version still matches. A mismatch can produce HTTP 412.
- Limit: this is an equality test. The page does not specify numeric or lexical ordering of etags. Do not sort etags to implement RevisionReplace. Browser tests without an explicit conditional API request do not test `If-Match` protection.
- Rights: CC BY 4.0 page text; Apache 2.0 code samples. No code was copied.

### C3. Google Calendar events.update

- URL: https://developers.google.com/workspace/calendar/api/v3/reference/events/update
- Page date: last updated 2026-07-07 UTC. Read on 2026-10-29.
- Read scope: operation description, primary calendar parameter, request, and page license.
- Supported claim: this API operation replaces the whole event resource. Google recommends a read before update and an etag check for a protected partial change.
- Limit: a connector can implement its own partial-update interface. Its parameters alone do not establish which underlying API request or conditional header it used.
- Rights: CC BY 4.0 page text; Apache 2.0 code samples. No code was copied.

### R1. RFC 5545, section 3.8.7.4

- URL: https://www.rfc-editor.org/rfc/rfc5545.html#section-3.8.7.4
- Author/editor: Bernard Desruisseaux. Date: September 2009. Read on 2026-10-29.
- Read scope: title, copyright notice, and the sequence-number section.
- Supported claim: the organizer's calendar agent increases the sequence number for a significant event revision. This is narrower than a documented counter for every stored field change.
- Rights: the page states IETF Trust and BCP 78 terms. Only a short attributed paraphrase is needed. Do not copy the standard or its code.

### W1. WebVoyager

- Published reference: Hongliang He and colleagues. *WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models*. ACL 2024, pages 6864-6890. DOI: 10.18653/v1/2024.acl-long.371.
- Metadata URL: https://aclanthology.org/2024.acl-long.371/
- Text read: https://arxiv.org/html/2401.13919v4 (preprint version 4, 2024-06-06).
- Access date: 2026-10-29. Read scope: sections 4.1-4.3, experiment setup, section 5.1, limitations, and ethics statement. The ACL PDF retrieval failed because the tool rejected its 18,384,116-byte length. Do not claim to have compared the full ACL PDF with the preprint.
- Related work: WebVoyager tests browser tasks on live public websites. Its chosen tasks exclude login-required access. Evaluation uses task outcomes judged from browser trajectories.
- Difference in scope: the proposed extension uses owned account records to supply controlled inputs to six accounting rules. It does not replace a broad browser-agent benchmark. Saved record checks and rule decisions are different measures from WebVoyager's task success measure.
- Rights: the arXiv text specifies its perpetual non-exclusive license. Do not redistribute the paper text or figures. No code, benchmark data, or figures were copied.

### N1. NeurIPS Paper Checklist

- URL: https://neurips.cc/public/guides/PaperChecklist
- Access date: 2026-10-29. No page update date was shown in the retrieved text.
- Read scope: claims, limitations, assumptions, reproducibility, experiment detail, statistical uncertainty, compute, ethics, impacts, licenses, released assets, human subjects, and LLM use.
- Apply as a review aid: state the small selected sample and all induced conditions; give the frozen procedure and actual evidence; distinguish website observations from local replay; show cleanup limits; record AI roles and human-review status. Counts from chosen cases do not estimate a population failure rate. State why no confidence interval is used.
- No NeurIPS approval or submission-compliance claim is supported. No checklist text needs to be copied. No reuse license was verified.

## Required claim limits

1. Call these controlled tests on production websites. Do not call them live billing tests.
2. Give the exact account surface, browser actions, connector actions, and readback methods. An API-created fixture is not a browser-created fixture.
3. Derive study revision 1 and revision 2 only from successful sequential saves and saved reads. State that the experiment assigns these revision labels. Provider metadata can be supplemental evidence, only if returned and checked.
4. Delay and repeat delivery of saved observations in the local test controller. State this induced condition. Do not attribute the changed order or duplicates to Google unless the service actually produced them.
5. A conditional browser rename of a pre-created output marker can test the local rule's effect on saved website state. The plan uses six output markers per service. A rename does not create a real billable charge equal to the study units.
6. Source field edits, admission records, and cleanup calls are distinct operations. A credit or deletion does not refund physical use or erase audit history.
7. Fresh observed fields support the bounded record check. They do not prove general provider consistency, complete historical retrieval, exactly-once writes, or permanent removal.
8. The new contribution can be a reproducible controlled integration trace. Do not describe the six existing rules or selected examples as a new accounting protocol.

## Search leads not used as evidence

WAREX (arXiv:2510.03285), WebArena (arXiv:2307.13854), and WebSP-Eval (arXiv:2604.06367) appeared in results. Their full papers were not read for this extension. Do not cite them as fully reviewed work. Commercial benchmark score pages and forum posts were excluded.
