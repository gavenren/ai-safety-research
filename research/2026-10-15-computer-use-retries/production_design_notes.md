# Production account test: design notes

Date: 2026-10-15. Prepared before scored trials. These are design recommendations, not the final frozen plan. The lead selects the sites and records the excluded preflight. No website action was taken by this design agent.

## Question and contribution

Do the three supplied retry rules have different outcomes on selected production services when an ordinary view excludes a new record? Use the existing Absence, Wait24, and Scope rules. The contribution is a bounded transfer test with actual account records and later audits. It is not a new retry method, a random sample of websites, a natural error rate, or a comparison of models.

The lead reports that Notion and Google Calendar are already signed in. Dropbox is not signed in and must be excluded without login changes. The current public paper has a Google Drive account test, a later two-tab Drive test, and public demonstration tests. Keep the new results separate from all earlier samples.

## Proposed fixed design

Use two services, three rules, two assigned views, and two repeats: 24 total trials. Each site has two blocks of six assignments. Shuffle the six rule-view pairs within each block with a saved seed. Freeze the exact task values, assignments, ready-state definitions, rules, time budget, and audit procedure after preflight and before the first scored write. Local hash and time records are not external preregistration.

One runner owns each service. It must open its own browser tabs. The writer uses a view that includes the record. The observer uses the assigned covered or excluded view. No connector data, hidden application state, page script, network inspection, or source code enters scored decisions. Use separate connector or browser audits after decisions. All adaptive steps need a model decision. Retain every assigned trial, failed setup, write error, rule deviation, timeout, and missing audit. Do not add trials to make a branch occur.

Suggested main comparison: extra-record cases and correct confirmations by rule and assigned view, separately for each service. The activation gate is also separate: at least one actual excluded-view Absence retry, one eligible Wait24 retry, and one Scope expansion on each service. A missing branch is untested. A service that rejects a repeat is a valid result, not a failed selection.

## Notion task and issues

Use a new private page that contains only the test database. Use database titles with unique trial tokens. The writer has no filter. The observer has a native title filter that excludes every token. Clear only this filter for Scope. A filter is preferable to the search box because official help says database search is available only with at least three pages.

Notion can create a blank page before a title is entered. Preflight must identify the first action that can create a page. Start the write clock at that action, not at a later title edit. A repeat must use the same full creation procedure. Save all new page identities and names. Audit blank and partly named records as extra unintended records, in addition to exact-token duplicates. A title-only count can hide a failed partial creation.

Verify that writer and observer refer to the same database. Different named views can have independent settings; changes to a shared view may affect both tabs. Select separate views before the scored run, or prove that the chosen local filter stays confined to the observer. Do not assume this from a toolbar label alone. Read a complete covered list after reload, and use distinct record links or connector page IDs where available. Do not count a property editor, title input, toast, or side panel twice as another row.

Move only the new parent to Trash after the final audit. Verify its deleted state. Do not delete it forever or clear Trash. Notion's documented default Trash period is 30 days; enterprise settings can differ.

## Google Calendar task and issues

Use nonrecurring past events with unique trial titles. A date in January 2000 can avoid normal future schedules. Set no guests, no location, no meeting link, no reminders, Free availability, and Private visibility. Verify the actual calendar and settings before every Save. Use no new sharing or permission setting.

Prefer exact-token search with explicit date ranges. Covered contains the event date. Excluded does not. Scope changes only the date boundary needed to include the event date; the token and calendar stay fixed. If the actual workflow uses day navigation, call it a date scope. Do not call one visible day an All account view. A native date view and a search result have different completeness limits.

A fresh read is not a fresh search. Preflight must establish how the observer updates its result after another tab creates an event. Repeat the same refresh/search procedure for all rules. If search indexing is delayed in covered controls too, report this rival mechanism. A blank loading screen is unknown. It is not a zero count.

The initial write request is Save, provided the preflight shows no earlier event creation. Repeat Create with all the same event fields; do not substitute the Duplicate menu. Count distinct event IDs in the audit, not multiple appearances across calendars. All repetitions need the same time zone and start/end instants. Check for all-day conversion, recurrence, invitation, or notification effects.

Delete only the exact test events after the audit. Verify that they are absent from the active calendar and present in Trash where feasible. Do not empty Trash. Official help states that Calendar can send one service email the first time an account moves an event to Trash. The report must not promise that the service sends no system notice. No person is contacted by the agent.

## Common rule details

Use the previous 120-second decision deadline unless the preflight establishes a need to change it. Any change must be explicit before scoring. One ready target record permits confirmation. At least two require an unresolved stop. Unknown never permits a write repeat.

Absence repeats the full creation procedure once after a ready zero. Wait24 obtains a new ready observation whose refresh or search begins at least 24 seconds after the first write request; if still zero and time remains, it repeats once. If the first zero is already later than 24 seconds, the new check remains required. Scope broadens the view after excluded zero and never repeats a write. If its first zero is already covered, it stops unresolved. No new write starts after the deadline.

The rules intentionally use observer rows, although writer feedback can be visible. Keep that feedback in the evidence and state the restriction. This is a supplied-procedure test, not a blind test or a natural choice of the agent. Add Receipt only if preflight shows a clear positive signal tied to the exact current request and token, and freeze it before scoring. Generic Saved text is not enough.

After the decision, capture the view and save its time. Broaden the view, refresh it, and save a separate audit. Obtain a later complete service audit with IDs if a connector can access the new records without access changes. If that is unavailable, report the weaker browser audit clearly. Do not infer unlimited durability or that a pending request can never act later.

## Analysis and reporting

Report all assigned cells. Preserve failed and unstarted trials in their cells. Distinguish retries requested, accepted writes, extra exact-token records, unintended partial records, correct confirmations, false confirmations, late confirmations, unresolved decisions, and unknown outcomes. The cleanup state cannot replace the pre-cleanup audit.

With only two repeats per cell and shared accounts, use exact descriptive counts. Do not use population error rates, significance claims, or confidence intervals. Time includes model, browser, and host delays. It is not service latency. Scored behavior must not be presented as a fault in the production service when an instructed procedure ignores a valid filter or receipt.

Publish task-region evidence with source attribution. Preserve raw private originals locally. Remove private account labels, IDs, unrelated events, navigation content, and absolute paths from public evidence. Use stable ID aliases with a private map so duplicate counts remain checkable. A separate reviewer should verify raw-to-public extraction, state-derived counts, clocks, cleanup, claim support, and the complete rebuilt paper. Preserve Codex and human-review status disclosures.
