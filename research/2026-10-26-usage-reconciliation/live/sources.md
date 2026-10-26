# Source check for the production extension

Read on 2026-10-26. This extension tests the four selected controls in the existing paper. It does not add a novelty claim. The main paper's `source_search.md` records the earlier literature search on the same date.

New search terms:

- `site.developers.google.com drive api files id trashed list empty incompleteSearch`
- `site.developers.google.com calendar api events status cancelled transparency private reminders`

Only the official Google results below were used. Other search results were not treated as checked sources.

| Source | Read scope and use |
| --- | --- |
| [Drive file resource](https://developers.google.com/workspace/drive/api/reference/rest/v3/files) | `id`, `name`, `mimeType`, `parents`, `trashed`, `explicitlyTrashed`, timestamps. Names are not unique. A file can be trashed through its parent. This supports exact-ID readback and child cleanup checks. |
| [Drive list](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list) | Page tokens, result limits, and incomplete searches. Read the response-field definitions. Last updated 2026-07-07. A short list alone does not prove completeness. |
| [Drive trash guide](https://developers.google.com/workspace/drive/api/guides/delete) | Trash versus permanent deletion, restore window, and exact-ID trash fields. Read the introduction and trash-property section. The test uses recoverable Trash only. |
| [Calendar event resource](https://developers.google.com/workspace/calendar/api/v3/reference/events) | IDs, status, time, attendees, reminders, visibility, and transparency. Read the field definitions used by this test. Cancelled ordinary events represent deleted events. They can later disappear. Transparent events do not block time. |
| [Calendar reminders](https://developers.google.com/workspace/calendar/api/concepts/reminders) | Per-event overrides and attendee updates. Read the reminders and notifications sections. Last updated 2026-09-03. Use no reminder and no attendees. |
| [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) | Claims, limitations, reproducibility, resources, ethics, and asset attribution are review aids. No conference approval or submission compliance is claimed. |

These sources define record fields and recovery behavior. They do not establish that Google provides the cumulative test reports, enforces the local budget, or guarantees a complete connected search. Those distinctions must remain explicit in the report. No source text, figure, or code is copied into the test package.
