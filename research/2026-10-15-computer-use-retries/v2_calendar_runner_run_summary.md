# Calendar retry study run summary

All 12 scored trials are complete. Each trial has a terminal decision, a separate audit, and cleanup evidence. The final prefix query found zero active test records. Deleted records remain in recoverable Trash.

The raw action log is private. Do not publish it without a privacy review.

| Trial | Live decision | Creates | Title repairs | Audit records | Active after cleanup | Seconds to decision |
|---|---:|---:|---:|---:|---:|---:|
| C01 | confirm | 1 | 0 | 1 | 0 | 60.987 |
| C02 | unresolved | 2 | 0 | 2 | 0 | 52.983 |
| C03 | confirm | 1 | 0 | 1 | 0 | 31.137 |
| C04 | confirm | 1 | 0 | 1 | 0 | 21.489 |
| C05 | confirm | 1 | 1 | 1 | 0 | 43.008 |
| C06 | confirm | 2 | 0 | 2 | 0 | 38.594 |
| C07 | confirm | 1 | 0 | 1 | 0 | 39.731 |
| C08 | unresolved | 2 | 0 | 2 | 0 | 38.004 |
| C09 | confirm | 1 | 1 | 1 | 0 | 50.194 |
| C10 | confirm | 1 | 0 | 1 | 0 | 28.983 |
| C11 | confirm | 2 | 0 | 2 | 0 | 38.421 |
| C12 | confirm | 1 | 0 | 1 | 0 | 12.712 |

Guard confirmed one record in all six cases. Absence confirmed four cases and left two Hidden cases unresolved. The two Absence Partial confirmations had two operation records in the later audit. These are constructed trigger cases, not failure rates for normal website use.

## Evidence limits

Browser popup rendered the exact marker. Raw connector descriptions contain token followed by two newline characters, also seen in preflight. Literal byte equality fails; do not silently strip or count this as exact stored-string match.

Read_event start/end are naive strings 2026-10-14T00:00:00 and 2026-10-15T00:00:00. No offset, timezone, or explicit all-day flag is returned. Browser re-opened native editors independently show All day checked and both inclusive UI dates Oct 14, 2026.

Manual rule application in CUA; v2_policy.py was not run live. Later policy replay must be labeled offline.

Three manual action names differ from the reference function names. Map verify_fields to read_identity, repair_title to repair_same_id, and repeat_create to create. Preserve the original log.

UI action wrapper start/end times bracket each call. Its after-state record is appended before the action record, so sort action intervals by timestamps rather than file line order. Decision elapsed time starts at the first mutation_admitted record. Images have their own start/end capture times and source observation IDs. Connector audit end time is after read_event replies. One C01 wait error was logged at detection time with equal start/end, not measured wait duration.

Some records with ready in phase names still contain Searching/progressbar. Those raw observations were retained. Only subsequent fully loaded states support decisions.

Raw snapshots include account details, calendar items, and opaque event URLs that encode the account. A normal unrelated reminder appears near C07 audit and C08 setup/audit. Review and redact any public extracts or images.

## Errors and departures

- V2CAL-00001 (C01, baseline): Helper load failed before any scored browser action. Helpers were then entered as direct CUA JavaScript.
- V2CAL-00095 (C01, verification): Search results heading wait timed out after Cancel on reloaded native detail; no mutation requested
- V2CAL-00139 (C01, cleanup): A same-cell var redeclaration hid the prior trial before a cleanup read. The call failed before browser I/O. Explicit assignment restored the correct trial.
- V2CAL-00478 (C04, initial_identity): Error: Error: Playwright selector deadline exceeded
- V2CAL-00529 (C05, prepare): Error: Error: Playwright selector deadline exceeded
- V2CAL-01154 (C10, cancel_prompt_read): Local helper attempted vlast[tab].state, but vlast stores state reference rather than a full observation. No browser action occurred.

- Helper load via eval failed before browser I/O. Direct JavaScript definitions were used.
- C04 close used wrong Cancel event creation locator once. Fresh state showed Cancel event changes; corrected read-only close.
- C05 leave-search used wrong Exit search locator once. Fresh state showed Go back; corrected before effective Create.
- C10 local vlast lookup failed before browser I/O. Fresh full snapshot was read.
- C10 first post-Discard snapshot retained transition editor nodes. Later empty search snapshot verified closed form; this is noted in appended baseline record.
- Guard Partial repair ledger was reserved before title fill, then linked to the single Save. Same native ID verified afterward.

All errors remain in the append-only record. No earlier decision or raw audit was changed. All decisions were within 300 seconds of the first Create reservation.

## Files

- actions.jsonl: raw browser actions, observations, facts, decisions, image captures, and audit/cleanup references.
- C01 through C12 audit JSON files: raw read-only search and detail replies.
- C01 through C12 cleanup JSON files: raw bounded zero-result replies.
- final-prefix-cleanup.json: final bounded query for the shared test prefix.
- 36 JPG files: decision, audit, and cleanup images for each trial.
- browser_helpers.js: original helper snapshot.
- browser_helpers_final.js: function text as held at the end. Some earlier helpers retain earlier closures. This is a helper archive, not a standalone browser driver.
- run_summary.json: private identity-level audit fields, time boundaries, and evidence IDs.
- raw_manifest.json: SHA-256 hashes of all files except the manifest itself.

Final actions.jsonl SHA-256: `6cfb1cea8b5749389bf666896b3e7cd3be462b7c82b2f64638481a2e704f7fe8`.
