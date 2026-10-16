# Calendar field-check run

Run date: October 15, 2026, America/Toronto. Action times use UTC.

All 12 assigned cases are complete. The live runner recorded MISMATCH for all 10 deliberately wrong saved fields. Both correct controls gave MATCH and received no repair. Each wrong case had one repair on the same event. All 12 final checks and later audits gave MATCH. Each final decision was within 300 seconds. These are recorded runner results. The root analysis must verify them from the cited raw evidence.

There were 12 Create saves and 10 repair saves. There was no second Create for any case. All 12 temporary events are now in recoverable Trash. Each case has a ready zero UI search and a zero connector search. The final prefix search is FCCAL-01281; its separate connector result is final-prefix-cleanup.json. Both show zero active test records. Only the 12 known scored test event records were moved to recoverable Trash. No unrelated record was deleted. The excluded preflight event has separate cleanup evidence. No guests, invitations, messages, conference links, new access, or permanent deletion were used.

The final service query used the primary calendar only, prefix FIELD-CHECK-20261015-C, time_min 2026-10-01T00:00:00-04:00, time_max 2026-11-01T00:00:00-04:00, and America/Toronto. It returned events=[] and next_page_token=null. The native search used October 1 through October 31, 2026.

## Per-case record

| Case | Condition | Initial | Final / audit | Repairs | Final decision seconds | Cleanup UI |
| --- | --- | --- | --- | ---: | ---: | --- |
| C01 | wrong_availability | MISMATCH | MATCH / MATCH | 1 | 92.42 | FCCAL-00135 |
| C02 | wrong_date | MISMATCH | MATCH / MATCH | 1 | 49.042 | FCCAL-00232 |
| C03 | wrong_marker | MISMATCH | MATCH / MATCH | 1 | 32.586 | FCCAL-00343 |
| C04 | correct | MATCH | MATCH / MATCH | 0 | 35.442 | FCCAL-00440 |
| C05 | empty_marker | MISMATCH | MATCH / MATCH | 1 | 35.013 | FCCAL-00542 |
| C06 | wrong_date | MISMATCH | MATCH / MATCH | 1 | 32.756 | FCCAL-00643 |
| C07 | wrong_end | MISMATCH | MATCH / MATCH | 1 | 83.099 | FCCAL-00749 |
| C08 | empty_marker | MISMATCH | MATCH / MATCH | 1 | 36.743 | FCCAL-00848 |
| C09 | wrong_marker | MISMATCH | MATCH / MATCH | 1 | 33.984 | FCCAL-00947 |
| C10 | wrong_availability | MISMATCH | MATCH / MATCH | 1 | 39.011 | FCCAL-01050 |
| C11 | wrong_end | MISMATCH | MATCH / MATCH | 1 | 46.468 | FCCAL-01152 |
| C12 | correct | MATCH | MATCH / MATCH | 0 | 58.979 | FCCAL-01268 |

## Evidence and field limits

Each packet points to the native saved UI, visible Description DOM read, complete October query, native identity, full read-only connector replies, field-check record, decision, and cleanup. The frozen checker ran live after each source collection. The model then admitted each repair or made the final decision. The checker is not an autonomous browser driver. The title/count baseline was not executed as another browser policy.

Native Description text was read from the visible contenteditable textbox. The accessibility snapshot alone omits it. Ordinary saved text appears exactly in innerText. The connector appends two LF characters. Empty Description appears as innerText LF, textContent empty, innerHTML <div><br></div>, and connector two LF characters. The comparison keeps these raw values. Only the frozen connector comparison removes trailing CR/LF. The UI comparison uses exact innerText.

All-day status comes from the explicit native checkbox. The native start and inclusive end dates are separate evidence from the connector start and exclusive end. The connector strings have no offset, time zone, or all-day flag. They do not prove UTC instants.

C07 and C11 each display two search rows for one two-day event. The heading says 2 events found. Both Day 1 and Day 2 rows expose the same data-eventid. The raw row reads and mapping files retain this distinction. Distinct native IDs exactly match the connector ID set. Do not count the display rows as separate created records.

## Retained errors and adapter changes

C01 had two local helper errors before its Save. The first helper retained a null trial variable; only Search options had opened. The second used a variable whose earlier failed initializer had not created a binding. Both errors remain in the raw log. The corrected helpers pass the trial as an explicit argument.

C01 also had a saved-event open error while the search was loading. A fresh read showed the owned record and supported another read attempt. No Save was repeated. C03 had an audit read error because Edit returned before native navigation. The next helper required the Title control and a native entry state before capture of the URL and reload. C07 had a strict selector error because the two-day event has two displayed rows. The explicit Day 1 row was then used after the row-ID read. These were read failures.

The adapter was corrected for native combobox indentation before the first field verdict. After C01, it was narrowed to use visible innerText for the UI contract, without an extra innerHTML equality gate. No earlier value was affected. Before the C07 initial verdict, its search-heading parser was changed to accept plural headings. The frozen field checker and plan were not changed. Prior adapter files are retained.

Some snapshots still showed a progressbar or a Searching announcement. They were retained. Fresh observations supplied the cited ready states. C12 has an explicit UNKNOWN observation gate before its final complete read. Loading captures do not supply final field decisions. Images with a loading source must not be described as completed evidence.

## Private data and images

Keep actions.jsonl, raw connector files, event URLs, native IDs, account names, and full images private. Public extraction must use stable identity aliases and omit unrelated account contents. Native screenshot clips are original CUA captures, not edited images. Root must inspect each image before use. The runner viewed C03-final-description-clip.jpg, C07-initial-date-clip.jpg, and RUN-END-final-prefix-settled-zero.jpg; these show task fields without the owner name. Other candidate clips still require separate review.

The two agent-created field-test tabs were closed after cleanup. No pre-existing tab was closed.

## Reproduction and scope

Use the frozen package in outputs/2026-10-15-computer-use-field-checks. freeze_verification.json records each matching hash. browser_helpers_effective.js retains the helper versions used through CUA. run_checkpoint.py parses the saved raw evidence and calls the frozen fieldcheck.py. run_checkpoint_v1.py and run_checkpoint_v2.py retain earlier adapter forms. finish_trial.py builds source packets without changing original records. A rerun of run_checkpoint.py appends a new record; use a copy of the raw directory for reproduction.

This is a small test of selected saved fields in one Calendar account. The wrong values were deliberate. The result does not estimate natural website error rates or prove a service-level exactly-once guarantee. Codex generated the test actions and this summary. No human review occurred.

Original actions.jsonl: 1285 records. SHA-256: 012cd335dec698e980bec36a6ca0de3e2640e745db757016f58cbcc51c17ea33.
