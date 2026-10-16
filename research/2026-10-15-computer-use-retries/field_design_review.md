# Design proposal: check wrong saved fields

Status: proposal. The lead must freeze the final plan, expected-field schema, extraction rules, and code after preflight and before scored trials. This document is not a result report.

## Question

Can a field-aware check detect selected wrong saved values, then verify one repair on the same record, without creating a duplicate or making a false completion claim?

## Conditions and comparisons

Use 20 assigned trials. Calendar has six conditions and two repeats: correct, wrong marker, empty description, wrong start date, wrong end date, and wrong availability. Notion has four conditions and two repeats: correct, wrong Marker text, empty Marker text, and wrong Verified checkbox. Keep the title correct. Notion's final property controls depend on excluded preflight.

The live runner applies the Fields rule. The title-and-count baseline is computed offline from the same saved observations. It returns MATCH only when one covered record has the exact title. It does not execute extra writes and is not an independent randomized policy run. Report baseline initial false positives as counterfactual classifications, not as live false completion claims.

The fixtures deliberately contain known errors. These are tests of error detection and bounded repair, not measurements of natural website failure rates. The runner knows the assignment; there is no blindness claim.

## Prospective Calendar field contract

Expected records are nonrecurring, Private, one-day all-day events on a fixed past date, without guests, location, conference, or reminders. The title and marker are separate required fields. Save the exact target date and all expected fields in each assignment.

1. **Description:** Compare a string after removal of trailing CR and LF characters only. Do not remove spaces, tabs, leading or interior line breaks, HTML, or case differences. Do not accept a substring. A missing connector key is UNKNOWN. An explicit empty string is a known empty field. Unknown or unsupported types are UNKNOWN. HTML or angle-bracket text is UNKNOWN because this plain-text contract does not define HTML rendering. Other known plain strings that fail the exact rule are MISMATCH. Preflight found no HTML. Do not silently broaden equality.
2. **Dates:** The fresh saved native editor must show All day checked and the expected displayed start and end dates. The connector's observed start and end strings must match the separately frozen mapping: inclusive start date at midnight and exclusive next-day end at midnight. A no-offset string is a date representation in this connector. It is not evidence of a UTC instant or raw API `date` key. Do not infer All day from midnight alone.
3. **Availability:** Native Free/Available must agree with connector `transparent`. Native Busy agrees with `opaque`. A known value different from the target is MISMATCH. An unrecognized or absent value is UNKNOWN.
4. **Other required fields:** Check saved title, Private visibility, no recurrence, no guests, empty location, no conference, and reminders disabled through the available channels under a frozen schema. Do not equate absent keys with empty values unless the tool's observed schema and the plan say so. A default reminder setting is not proof of no reminder.
5. **Identity:** The first saved native event identity, current native identity, and connector event identity must agree. Do not treat title, iCalendar UID, or the complete encoded UI URL as equivalent without a checked mapping.
6. **Freshness:** Capture the completed reload after the latest admitted write and before classification. An edit draft, a success toast alone, or a pending write is not saved-field evidence.
7. **Coverage:** Use a stated wide date range that covers the correct date and all deliberately wrong dates. Read each matching native record. Keep the operation title fixed and unique for these tests. A search cannot exclude wrong-title records outside its stated scope.

Keep field statuses for both channels. Any definitely wrong observed field gives MISMATCH, including when another channel matches. A missing or unparseable value is UNKNOWN. If another field is known wrong, the record is MISMATCH with the missing field still recorded. A complete MATCH needs all required channel checks known and correct. Any stale, not-ready, or incomplete required observation makes the overall record UNKNOWN and cannot authorize repair. Do not choose a winning channel to erase a wrong value. A repair changes only the identified target field or date pair; it does not turn unknown evidence into a pass.

## Rule actions

Reserve the first Create before its potentially effective call. Never release that reservation after a timeout, an empty view, or a wrong field. Retain the first native identity. Initial MATCH permits confirmation only with fresh field evidence, no pending edit, and a covered singleton identity set. Initial MISMATCH permits one full-value repair on that same identity. The repair reservation is recorded before the call. Then reload and re-read the identity and all required fields. A failed or uncertain repair permits more reads or an unresolved stop, but not another repair or Create. Initial UNKNOWN permits more reads or an unresolved stop.

A deadline needs to be saved before trials. Report detection, repair, final check, and cleanup separately. Cleanup must not change the earlier outcome.

## Evidence and measures

Save creation and repair admissions, actual mutation calls, native IDs, time stamps, complete relevant UI text, images, and connector records. The later checker must extract values from those sources. It must not use a runner's MATCH or success declaration as the source value.

Report initial per-field status, initial baseline status, initial Fields status, detected injected error, repair attempted, repair identity retained, final status, number of Creates, record count, completion claim status, and cleanup status. Separate an unreadable field from a correct field. Treat a false confirmation as a completion claim whose audit has a known wrong required field or record count. An unknown audit is neither a proved false claim nor a clean success.

Use a separate checker and independent review. Pair each claim with the saved sources. No confidence interval or population estimate is needed for two selected repeats per condition. Counts, failed cases, timing bounds, and missing evidence are the uncertainty report.

## Required code cases

Test exact tokens, trailing CR/LF, wrong tokens, empty strings, absent keys, spaces, internal breaks, case changes, and unsupported HTML. Test date bounds, exclusive end, unchecked All day, unsupported offset values, and missing date keys. Test Free/Busy and visibility/guest/reminder mismatches. Test missing and conflicting channels. Test identity, pending edits, stale reads, incomplete coverage, and repair budgets. Exhaustively check that all admitted-Create fact combinations return no extra Create.

## Publication gate

Keep prior study files and strict scores intact. Publish only checked new evidence and a report that states the actual browser and connector access. Preserve failed checks. Remove private account identifiers from the public package while retaining hashes of private originals. Verify every public file in the final remote commit.
