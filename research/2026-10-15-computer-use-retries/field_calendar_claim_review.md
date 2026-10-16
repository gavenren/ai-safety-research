# Calendar claim review

Review date: October 15, 2026, America/Toronto.

Report SHA-256: `9d8290b5e449abd96afee1738dbe4760ff97e21e664bd65fa70ea518de89f842`.

Result: No material claim error found in the reviewed scope. This review did not change the report or any trial evidence.

## Scope and review limits

The Calendar runner reviewed Section 13, its abstract and related-work claims, the relevant Section 12 results, cleanup statements, and references 22, 24, and 25. This is a check by the agent that ran the Calendar cases. It is not an independent review of that agent. Codex generated this review. No human review occurred.

The review used the frozen contract and checker, saved Calendar evidence, trial and field results, source notes, change record, and independent comparison outputs. It also opened the three original sources below. It made no new browser or account action. It did not repeat the live study or review every claim from the earlier studies. Notion outcome totals were checked against the saved analysis; this review did not re-derive all Notion source values.

## Field and result checks

The contract has 25 Calendar field comparisons, in addition to evidence and identity gates:

- 12 native UI values: title, description, All day, start date, inclusive end date, availability, visibility, recurrence, guests, location, conference, and reminders.
- 13 connector values: summary, description, status, start, exclusive end, attendees, transparency, visibility, location, hangout link, recurrence, recurring-event ID, and reminders.

All 36 Calendar checkpoints contain these 25 results. Initial checks contain 276 MATCH and 24 MISMATCH field results across 12 cases. The 24 mismatches represent 10 deliberately wrong cases; one error can affect more than one field comparison. The 300 final and 300 audit field results are MATCH. These are repeated checks, not 900 independent trials.

The five wrong-field conditions each have two observed cases. C01/C10 have Busy and opaque. C02/C06 have October 13 dates. C03/C09 have the wrong marker. C05/C08 have empty descriptions. C07/C11 have the wrong end date. C04/C12 are correct controls. All 10 corrections retain the first native identity. There are 12 Calendar completion claims, no extra audited record, and no decision beyond 300 seconds. This supports the Calendar row in the results table. It does not show detection of every possible error in all 25 fields.

The empty description evidence agrees with the report: native innerText is a line feed, textContent is empty, diagnostic innerHTML contains a blank div, and the connector has two line feeds. Both checked values fail against the nonempty token. The contract removes only trailing CR/LF from the connector string. It does not strip native text or interpret arbitrary HTML.

The all-day checkbox and native dates are separate from the connector's no-offset strings. The report correctly avoids a UTC or raw API date-schema claim. C07 and C11 retain two displayed rows, with matching rendered event identities and one distinct connector identity. A two-row heading alone is not used as a record count.

## Errors, cleanup, and earlier results

The evidence retains the Calendar helper errors, loading/read errors, C07 plural-row selector error, and earlier adapter versions. C01's immediate identity source still has a search URL; the later native read supports the identity before the decision. The report and change record disclose this reference error. C12 also retains an intermediate UNKNOWN observation gate. No earlier failed observation was converted into a successful source.

The main analysis has 380 passing consistency checks. The separate comparison reports no outcome differences. This review inspected those outputs; it did not independently rerun the full analysis. Their success does not remove the original procedure or reference errors.

Only the 12 known scored Calendar events were moved to recoverable Trash. The excluded Calendar preflight event has separate cleanup evidence. Each scored case has later active-zero UI and connector reads. The final prefix check covers the primary calendar, October 1 to November 1, 2026, in America/Toronto. It returns no events and no next page. The native search covers October. This is bounded active-record evidence; it does not prove all-time absence or prevent a future effect. No Trash was emptied.

The copied earlier `v2_trials.csv`, `v2_summary.json`, `v2_groups.csv`, and `v2_policy.py` are byte-identical to the previous study package. Section 12 still reports eight Calendar single-record claims as strict UNKNOWN. The new equality rule is not used to rescore them. The original Calendar action-log SHA-256 is unchanged: `012cd335dec698e980bec36a6ca0de3e2640e745db757016f58cbcc51c17ea33`.

## Source and interpretation checks

- [22: Google Events resource](https://developers.google.com/workspace/calendar/api/v3/reference/events): supports HTML descriptions, all-day date fields, an exclusive end, and transparency/visibility definitions. The exact native Free label and normalized connector strings come from the saved observations. The report does not treat the local CR/LF rule as a Google guarantee.
- [24: StateAct v1](https://arxiv.org/html/2607.22798v1): Sections 4.2 and 6.1 support a separate final artifact check and the stated limit of structural checks for wrong values. The reference title, authors, version, and July 24, 2026 date agree. The report identifies a preprint and selected reading. It makes no benchmark replication or general verifier-improvement claim.
- [25: Notion Database properties](https://www.notion.com/help/database-properties): supports formatted text and Boolean checkbox property types. It does not establish persistence or commit timing. The report uses it only for the property definitions.

The novelty claim is bounded. The report describes a specific rule and selected tests of established principles. It does not claim firstness or a new exactly-once protocol. It labels the title/count comparison as an offline classifier. It separates the live Calendar checker from the Notion agent's recorded judgments and does not claim an unattended browser controller. These limits are consistent with the evidence.
