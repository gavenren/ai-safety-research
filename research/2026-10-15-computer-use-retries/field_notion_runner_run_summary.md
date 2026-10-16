# Notion saved-field trials

Run date: 2026-10-15 in Toronto. All work used the supported browser tool. The private database and all known test pages were moved to recoverable Trash. No permanent delete was used.

| Trial | Assigned condition | Initial check | Final decision | Repair writes | Seconds to decision |
|---|---|---|---|---:|---:|
| N01 | wrong_checkbox | UNKNOWN | UNRESOLVED | 0 | 28.887 |
| N02 | correct | MATCH | CONFIRM | 0 | 126.775 |
| N03 | empty_marker | MISMATCH | CONFIRM | 1 | 37.048 |
| N04 | wrong_marker | MISMATCH | CONFIRM | 1 | 30.294 |
| N05 | empty_marker | MISMATCH | CONFIRM | 1 | 27.967 |
| N06 | correct | MATCH | CONFIRM | 0 | 19.464 |
| N07 | wrong_checkbox | MISMATCH | CONFIRM | 1 | 26.513 |
| N08 | wrong_marker | MISMATCH | CONFIRM | 1 | 26.218 |

## Evidence

Each packet links the first native page ID, Create admission, repair admission when used, initial fields, final fields, later audit, and cleanup. The raw log is append-only. Native title text, Marker text, checkbox DOM value, and the empty-body prompt were read after reload. The covering Table had no query or filter. The row Copy link action supplied the actual native ID.

The five observed saved mismatches were MISMATCH. One assigned field repair was used for each. Final and later audit values matched for N02–N08. N01 remained UNKNOWN and UNRESOLVED.

Final empty parent: NF-01137. Same parent in Trash after reload: NF-01157. Parent cleanup record: NF-01159.

## Method and log departures

- N01 helper closures kept old scalar values. Some phase labels and the elapsed value were wrong. NF-00033 records the correction from original timestamps. Original raw records remain unchanged. The mutable S object fixed the helper context before N02.
- The old image helper routed one N01 image to the preflight folder and appended NFP-00163 to its log after freeze. The first 162 preflight records did not change. The frozen package files did not change.
- N02 title icon and side-peek navigation failed. The failures remain in the log. Later identity reads used the visible row Copy link menu and the clipboard. This changed the read procedure, not the saved-field rule.
- N03 audit table header wait failed at NF-00325. NF-00336 supplied a fresh ready table before the audit check. The final decision had already been recorded at NF-00308; the later audit is separate.
- N04 decision NF-00475 omitted field_check_record_id. Its packet and preceding NF-00474 supply the link. NF-01160 records this schema note. Decisions from N05 include the reference.
- N04 cleanup showed one row after the first reload, then an active native page, then Trash. No second Trash action was sent. The first N04-cleanup-zero image is wrongly named and shows a row. NF-00515 records this limit. Use N04-cleanup-zero-confirmed.png for the later empty state.
- The parent immediate Trash view said it was moved more than 30 days ago. The fresh reload showed just now and a 30-day recovery period. Use NF-01157 as the settled state.

## Helper code

actual_helpers.js preserves the final function bodies with their REPL variable names. actual_helpers_anonymous.txt preserves the first raw function export. These are helper code, not a stand-alone unattended runner. The agent inspects the evidence before ncheck. ncheck records the agent judgment; it does not enforce the gates by itself. The root process applies the frozen checker to the cited evidence.

The earlier context helper defect and read navigation failures are retained in raw records. No trial was repeated for better results.

## Limits

- One account, one private temporary database, eight assigned trials.
- N01 Create was admitted but no page identity appeared. No retry occurred. Absence at read times does not disprove a later effect.
- All parent baselines included unnamed rows. No carryover row was seen before later Creates.
- Five saved mismatches were observed and repaired once. The other assigned wrong-checkbox trial (N01) was unresolved.
- The comparison based on title and count is offline. No separate control policy made live writes.
- These checks are agent-led. Raw values and IDs support independent recomputation.
- No broad reliability or general product performance claim is supported.
