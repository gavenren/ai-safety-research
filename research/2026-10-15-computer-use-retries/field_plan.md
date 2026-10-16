# Prospective field-check experiment

Status: FROZEN before scored execution. Freeze time: 2026-10-16T01:04:50.301036+00:00.
Date: October 15, 2026. This is an extension of the same paper.

## Question and contribution

Can explicit expected-field comparisons detect deliberately incorrect saved values and support correction of the same record in Google Calendar and Notion? The contribution is a prospective field contract and a small live test. It is not a new retry protocol, an unrestricted agent benchmark, or an estimate of natural service errors. Earlier scores remain unchanged.

## Design

Twenty fixed assignments: six Calendar conditions and four Notion conditions, each repeated twice. Each assignment creates one temporary record. Each initial saved record is checked after a reload. A definite mismatch permits one correction to that same native record. A second Create is never permitted. A correct control receives no correction. Missing evidence requires reads or an unresolved stop. No assignment is replaced.

Calendar conditions: correct control; wrong description marker; empty description; wrong one-day date; wrong inclusive end date; wrong Free/Busy value. The expected event has the unique token as its title and plain description, all-day start and inclusive end October 14, 2026, Free, Private, no guests, no location, no conference, no reminder, and no recurrence. The service's exclusive end is October 15. A wrong date uses October 13 for both UI dates. A wrong end uses October 15 as the UI inclusive end. Wrong availability uses Busy. Wrong marker appends -WRONG. All other requested fields remain correct.

Notion conditions: correct control; wrong Marker text; empty Marker text; wrong Verified checkbox. The expected title and Marker are the unique token. Verified is false. The record body is empty. Wrong Marker appends -WRONG. Wrong Verified is true. These records use a new private test database.

The order uses a fixed local random seed, 2026101509. It randomizes assignment order within each service only. This is not random sampling of websites or users. One runner context is assigned to each service. Both use the same host and browser service. Service, account, and runner are not independently varied. Each runner knows the intended condition. The initial injection is deliberate, not an agent accident.

## Decisions

The live runner records MATCH, MISMATCH, or UNKNOWN for every required field from actual saved evidence. MATCH means the observed field meets the saved contract. MISMATCH means an observed value conflicts with it. UNKNOWN means the evidence cannot resolve it. A known field mismatch takes precedence over another unknown field only when the required readiness, freshness, identity coverage, and no-pending-edit evidence gates pass. A failed evidence gate makes the record verdict UNKNOWN, even if a stale value looks wrong. Full confirmation requires all fields to match, one native identity in the covering audit, the same identity in the native detail, no pending edit, and a ready read after the last mutation.

The Calendar description contract permits only trailing carriage-return and line-feed characters after the exact token in the connector value. No spaces, case changes, token substrings, or internal newlines are equivalent. The visible saved description must also be the exact token. HTML or an unsupported output form does not pass; it remains unknown. Date checks combine the explicit saved UI all-day control and calendar dates with the connector's normalized date strings. A midnight string alone does not prove all-day or a UTC instant.

The initial field decision must be recorded before correction. A same-ID correction changes only the assigned wrong field or date pair to the full expected value. It is admitted before Save or the effective property write. The final decision follows a new native read and covered record count. Each trial has a 300-second limit from the initial Create admission to the final decision. Late, unresolved, failed, or unknown cases remain in the results. Read errors do not permit another mutation.

## Baseline and measures

The title-and-count baseline is an offline counterfactual: it would confirm when the same initial audit has exactly one exact-title record. It is computed from the same observations. It is not a separately executed or randomized policy. The main measures are initial known-wrong detection, false matches, correct-control matches, unknown verdicts, same-ID repairs, final full-field matches, extra records, and verified cleanup. Initial injected conditions must be confirmed from saved values; intended input alone does not establish that a wrong value was saved.

H-F1: every verified wrong-field case gets MISMATCH before repair. H-F2: every correct control gets MATCH with no repair. H-F3: every admitted correction retains the original native identity, ends with all required fields matching, and leaves exactly one record. H-F4: no final confirmation contradicts the later audit. Evaluate each service separately. Report exact finite counts and every failure. No population interval or p-value is justified by this selected small set.

## Evidence, safety, and cleanup

Save action timestamps, mutation reservations, native IDs, full private DOM snapshots, evidence references, connector replies, decisions, errors, and images. Calendar uses bounded October 2026 searches, all pages, and detailed read-only event reads. Notion uses an unfiltered complete test database and reloaded native detail. The observation channels have different limits. An agent declaration alone is not evidence. A second parser must derive the results from saved records.

Only temporary test records may change. No messages, guests, invitations, purchases, new access, or permanent deletion. Use past Calendar dates. After each audit, move the record to recoverable Trash and verify no active matching record. Preserve original errors and cleanup corrections. At the end, trash the empty temporary Notion parent and verify its restore state. Keep private raw evidence local. Publish only task evidence with private identities replaced by stable aliases. Check images separately.

## Release

Save and hash this final plan, assignments, instructions, field checker, and checker tests before scored execution. Record any later changes. Run the saved analysis in a fresh directory, obtain a separate review, inspect all public images and final PDF pages, use the NeurIPS checklist as an aid, preserve earlier study evidence, and verify every published file against the remote Git tree.
