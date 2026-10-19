# Live undo extension: design review

Date: 2026-10-19, America/Toronto. This note precedes the live scored plan. It does not record a completed experiment.

## Scope

Test the six fixed rules from the October 19 paper on temporary records in Google Calendar and Notion. The useful contribution is a traceable small case series of browser actions and saved field checks. The browser has no assumed atomic undo, complete field revision counter, or trusted operation provenance. Preserve the original exhaustive simulation as a separate result.

A browser agent executes a rule selected in advance. This is not a test of whether an autonomous model discovers the rule. Later commands are controlled test actions under one user's authority, not natural human changes or concurrent traffic. These selected trials share accounts and a driver. Do not treat them as independent population samples.

## Agreed matrix

Each trial starts x=0,y=0, then the agent sets x=1. Save and reload after each phase. Each rule receives a fresh temporary record.

| Later history | Pre-undo fields | Fixed-command target | Purpose |
| --- | --- | --- | --- |
| No command | (1,0) | (0,0) | Completion control |
| flip_y | (1,1) | (0,1) | Independent field preservation |
| add1 | (2,0) | (1,0) | Preserve arithmetic intent |
| set0, then set1 | (1,0) | (1,0) | Same final value after visible assignments |

Four histories crossed with six rules on two sites give 48 planned rule trials. Each intermediate set0 and set1 must have its own saved reload. Add sub1 and set0 as two diagnostic histories per site, for four additional histories. Both leave actual (0,0); their intent-based targets are (-1,0) and (0,0). These diagnostics do not count as six-rule trials unless the frozen plan expressly requires all policies. Record native metadata separately; do not claim equal native revision counters.

The driver implements arithmetic by reading a value, calculating, and setting a literal. That preserves the controlled command's specified meaning under this sequential test. It does not establish a remote arithmetic primitive or how an independent human would act in the alternative world.

## Rules and information boundary

Full restore resets x and y. Field restore resets x only. Subtract sets x to its observed value minus one. Value guard restores x only when x=1. Rename the last two live rules **Log-assisted revision guard** and **Log-assisted provenance control**. They use the experiment log of later x writes and command types. They do not receive native field revisions or server provenance. Do not claim browser-only inference.

The rule executor must not receive the reference target. The grader computes that target from initial fields and the prescribed commands. Keep rule status (complete or abstain), actual mutation result, and saved-state grade separate. A successful save does not establish correct undo semantics.

The guarded read and write are distinct browser operations. There is no intentional outside writer during undo. Thus these tests do not validate atomicity or race safety.

## Same-value edits

An attempted set1 on x=1 can be suppressed by the UI or server. An unchanged saved field or generic saved message does not prove a new x revision. Do not use such an attempt as the main assignment injection. The agreed set0 then set1 history has two changed saved values and must be named as a two-command history. If same-value attempts are later added, label them separate capability probes and record dispatched intent, saved values, and available version evidence separately.

## Site contracts

Calendar: x is a plain description integer (0,1,2, or -1 where required). y is availability, Free=0 and Busy=1. The unique trial title is the marker. Use a past one-day all-day private event without guests, reminders, conference, recurrence, or location. Verify title, native identity, date, all-day status, availability, privacy, and the absence of extra fields. Description permits HTML. For this plain-text encoding, accept only a prospective narrow parser, with boundary CR/LF removal if preflight supports it; preserve all interior characters. Calendar updated and sequence are not field revisions. An event ETag is not a field version, and API If-Match support does not prove that browser Save used it.

Notion: use a new temporary private database with Number X and Checkbox Y. A fallback to prior Marker text and Verified checkbox must be selected and documented before scored trials. Verify property types, field labels, page identity, and marker title. Close property editors before saved reads. Last edited time is page metadata, not a complete x-write count.

## Evidence gate

1. Record a unique synthetic marker, native identity, field identities, planned commands, and saved initial fields.
2. Record the saved agent increment on that same identity.
3. Record each later command, intended value, dispatch result, error, and saved reload. An edited textbox alone does not pass.
4. Read both fields immediately before rule evaluation; verify native identity and marker. Record which evidence the rule can use.
5. Record rule status, selected mutation or abstention, and actual tool result. After uncertain dispatch, inspect saved state before retry. Do not repeat a toggle or add/sub action blindly.
6. Close editors, let native saving finish, reload, and read both fields again. Capture source evidence IDs and times. Read-only connectors may corroborate the browser but do not fill absent fields by inference.
7. Grade the complete selected record against the fixed-command target. Retain saved wrong values. Stop on unexpected identity, user data, outside writes, access failure, or unresolved parsing.

Every planned trial has a terminal status: completed valid trial, invalid injection, interrupted, access failure, or unknown observation. Count each status. A saved wrong result is a failure result, not an exclusion. Invalid injection means the prescribed history was not established before undo. Keep the original row if a predeclared replacement trial runs. Freeze the replacement bound before scored work.

Save raw local logs and screenshots. Publish only synthetic evidence. Remove account names, emails, unrelated records, private sidebar contents, sessions, and unrelated tab details. Use stable pseudonymous native IDs in public evidence and retain the private mapping locally. A second agent must check extraction and counts.

## Cleanup

Cleanup follows final evidence capture and is separate from scoring. Move only this run's temporary objects to recoverable Trash. Do not empty Trash. Record each created identity and cleanup status. Verify the same identity is trashed or unavailable as an active record, then run a bounded complete search for the run's markers. Delete a new temporary container only when all its trial evidence is saved and it contains no other user work. A failed cleanup remains an open item.

## Prior failure lessons

The October 15 Calendar preflight found two appended LF characters in a connector description and required the native editor for all-day status and displayed dates. The Notion preflight found that an immediate reload after Enter could show the old value. A checkbox command returned an error, while later saved state showed that it took effect. Therefore inspect saved state before retry, require closed editors and fresh reloads, and retain all misleading capture labels and failed actions. These are prior observations, not provider guarantees.

## Decision

This extension is suitable after root freezes the site mappings, matrix, retry bounds, evidence gates, and exclusions. It can support a small controlled account case series. It cannot establish native revision safety, atomicity, general operation provenance, natural error rates, or a provider defect.
