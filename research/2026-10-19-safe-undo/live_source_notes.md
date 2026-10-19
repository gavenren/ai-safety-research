# Primary sources for live undo tests

Search and access date: 2026-10-19, America/Toronto. This search preceded the live scored plan. It is limited and establishes no novelty priority. No third-party code or full source text is copied.

## Queries

- `site.developers.google.com calendar API versioned resources etags If-Match`
- `site.support.google.com docs Google Sheets version history individual cell edit history`
- `site.developers.notion.com page last_edited_time properties`

The first and third query strings used site. rather than site:. Exact provider pages were then opened and read. Community search results were not used as technical authority.

## Selected Calendar sources

Google. *Get specific versions of resources*. https://developers.google.com/workspace/calendar/api/guides/version-resources . Page states last updated 2026-09-11 UTC. Read introduction, conditional modification, conditional retrieval, and their caveat; inspected the code for explicit If-Match use. ETags describe resource versions. Conditional API modification uses an earlier ETag and returns 412 on mismatch. This is a provider API capability, not evidence of native browser behavior. It does not provide an x-field revision count.

Google. *Events*. https://developers.google.com/workspace/calendar/api/v3/reference/events . Page states last updated 2026-07-07 UTC. Read representation and definitions for id, etag, description, location, start/end, reminders, sequence, updated, transparency, and visibility. Descriptions can contain HTML. Updated describes main-event modification time; reminder changes do not update it. Sequence is an iCalendar sequence number. Neither is documented here as a complete field write count. Transparency maps opaque to Busy and transparent to non-blocking availability. The available browser/connector must be checked for its actual exposed fields.

## Selected Notion sources

Notion. *Page*. https://developers.notion.com/reference/page . Read page object properties and schema context. The page has a unique ID and page-level last_edited_time/last_edited_by metadata. Last edited time describes when the page was updated. It is not documented here as a field-specific counter or atomic compare-and-set condition. Property values follow the parent data source schema. No publication date was shown.

Notion. *Database properties*. https://www.notion.com/help/database-properties . Read property types and editing values. Number stores numeric values; Checkbox represents a true/false condition. Last edited time and editor metadata are automatic. These definitions support field selection, but do not establish save timing or complete revision history. No publication date was shown.

Failed lead: https://developers.notion.com/changelog/last-edited-time-is-now-rounded-to-the-nearest-minute returned an internal fetch error. Its content was not read. Do not claim minute rounding based on this run. A community search excerpt is not a substitute for the provider source.

## Unselected Sheets source

Google. *Find what's changed in a file*. https://support.google.com/docs/answer/190843?hl=en . Read file versions, named versions, cell edit history, and unavailable versions. File revisions can be merged. Cell history omits some changes, including formula-driven changes. Restoring an earlier spreadsheet version clears earlier cell history. This supports caution about treating visible history as a complete field counter. Sheets was considered before root selected Calendar and Notion; do not cite it as evidence of a tested site.

## Scope

None of the reviewed sources establishes that a same-value UI edit always makes a new field version. This is a limit of the reviewed evidence, not proof that a provider never records such an edit. Each account trial must record the browser's actual capabilities and saved fields. No native atomicity or provider defect claim follows from these documents.
