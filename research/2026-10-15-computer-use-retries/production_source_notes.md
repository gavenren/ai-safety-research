# Source notes for the production account extension

Search and access date: 2026-10-15. This design agent did not operate any website. Live account eligibility and scored states must be established by the lead and runners. This limited search does not prove novelty. Source findings do not substitute for experiment results.

## Exact queries

1. `site.support.airtable.com filter records view records hidden filters create record`
2. `site.notion.com help views filters sorts database filters`
3. `site.help.dropbox.com create folder same name folder already exists`
4. `site.support.microsoft.com OneDrive create folder name already exists`
5. `site.arxiv.org browser agent production website reliability retries filters duplicate records 2026`
6. `site:support.google.com/calendar "Search for events"`
7. `site:support.google.com/calendar "Delete an event" "Trash"`
8. `site:support.google.com/calendar "Create an event" "Notifications"`
9. `site:notion.com/help "trash" "30 days"`
10. `site:support.google.com/calendar/answer/ "Search" "Date from"`
11. `site:support.google.com/calendar/answer/ "Search for events in Google Calendar"`
12. `site:support.google.com/calendar/answer/ "Duplicate" "event"`

The first five queries use periods after `site`, as written. They did not use the search engine's `site:` operator. Only original provider or author pages below support the design. Forum results and commercial summaries were not used as evidence.

## Selected service sources

- Notion, [Views, filters, sorts & groups](https://www.notion.com/help/views-filters-and-sorts), undated help page. Read the view settings, filters, delete filter, and database search sections. A view shows records that meet its filter. Views can have separate settings. Search checks titles and properties and requires at least three pages. This supports the planned native view manipulation; it does not establish persistence, duplicate acceptance, or current account behavior.
- Notion, [Delete & restore content](https://www.notion.com/help/duplicate-delete-and-restore-content), undated help page. Read Delete pages, What happens when a page is deleted, and Find pages in Trash. The default Trash period is 30 days. Enterprise settings can differ. Restore and permanent delete are distinct actions. Use reversible Trash cleanup and verify the actual state. No retention setting is changed.
- Google, [Use Google Calendar with a screen reader](https://support.google.com/calendar/answer/6101541?hl=en), undated help page. Read the search instructions and create/manage event sections, including notification removal. Advanced search can restrict calendar, included/excluded terms, participants, location, and dates. The guide also explains result navigation. This supports date-scope tests and notification checks. It does not prove that exact duplicate creation will succeed or that a returned search is complete immediately after Save.
- Google, [Delete an event](https://support.google.com/calendar/answer/37113?hl=en), undated help page. Read deletion of owned events, Trash, restore, and the system-notice paragraph. Deleted events stay in calendar Trash for 30 days. Some recurrence deletion paths are not recoverable; use nonrecurring test events. Google states that the first Trash deletion can send one service email. Avoid an absolute no-email claim. Do not empty Trash or delete forever.

## Method sources and relation to prior work

- Fielding, Nottingham, and Reschke, [RFC 9110, section 9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2), June 2022, Internet Standard. Re-read sections 9.2.1 and 9.2.2. Repeated requests can be safe under known idempotent semantics; automatic retry of a non-idempotent request needs suitable evidence or semantics. A filtered absence does not establish this. The browser study does not observe the websites' HTTP request semantics.
- Aram Vardanyan, [Building Browser Agents: Architecture, Security, and Practical Solutions](https://arxiv.org/html/2511.19477v1), arXiv v1, 2025-11-22, preprint. [Metadata](https://arxiv.org/abs/2511.19477). Read abstract, Introduction, and the section on state divergence and versioning. The paper discusses operation with authenticated sessions and stale element references. It already treats execution context as relevant to reliability. Its broad architectural claims and performance measurements were not reproduced or adopted. Our proposed narrow comparison changes observer scope and follows fixed retry rules. No claim that production browser testing is new is justified. The source lists CC BY 4.0; no text, figure, code, or data is reused.

The prior paper's source records preserve its closest retry, timing, and reliability sources, including RIFL, WAREX, and CUA-Speedrun. This extension adds selected production account evidence. It does not introduce a retry protocol or establish a general model improvement.

## Other candidates inspected

- Airtable, [Filtering records using conditions](https://support.airtable.com/articles/9290731839-filtering-records-using-conditions). The search extract gives 2026-10-13; the opened page says updated one day ago. Read overview, condition types, and removal instructions. Filters hide records from views rather than delete them. This supports Airtable as a candidate only. No browser or account check was done by this agent.
- Dropbox, [How to create and use Dropbox folders](https://help.dropbox.com/create-upload/creating-using-folders-on-dropbox), updated 2025-11-07. Read the folder-create steps. The documented Only you option supports private folder setup. The page does not establish duplicate-name behavior. The lead reports a login page, so Dropbox is excluded without account changes.
- Microsoft, [Fix problems uploading files on the OneDrive website](https://support.microsoft.com/en-us/onedrive/fix-problems-uploading-files-on-the-onedrive-website). Read only the search extract. It describes a same-name file conflict with Replace or Keep both. This is not proof of same-name folder behavior, and it is not used as a study result.

## Rights and limits

Use original prose and necessary attributed task evidence. Provider pages, code, papers, and figures are not redistributed. No new license is assigned. Search snippets for other papers were not treated as full reads. This was not an exhaustive literature review and no source experiment was reproduced.
