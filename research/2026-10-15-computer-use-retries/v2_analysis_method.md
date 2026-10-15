# V2 analysis method

The analysis reads saved evidence. It makes no website request. Run it with Python 3 and the standard library:

```
python3 -m unittest v2_policy_tests v2_analyzer_tests -v
python3 v2_analyze.py --input-dir . --output-dir .
```

The script imports the unchanged table and raw-event parsers from production_analyze.py, which is included with the earlier experiment. The new date ranges, title rules, identity comparison, fields, and outcome checks are in v2_analyze.py. The frozen reference policy is v2_policy.py. This reference policy was not an autonomous browser driver. The live runners applied the supplied rule and logged their facts. Analysis replays those facts and checks the cited evidence separately. Where an Absence record uses a compact schema, the script retains a schema departure and reconstructs its reference inputs from the cited observer state and earlier action counts. It does not treat omitted fields as positive evidence. Compact Guard facts are not granted a confirmation by this fallback.

The script writes v2_trials.csv, v2_groups.csv, v2_summary.json, and v2_analysis_checks.json. Counts in these files come from saved UI rows, native page or event identities, and raw connector replies. A declared runner total is not a count input. A supplemental connector file is loaded through its public file pointer and included in the input hash map.

## Counts and identities

A Notion data row starts with a table-level checkbox after Name. Its next button is one row. A button without text is a blank page. Nested text does not add rows. A ready table needs the full controls, selected view, and no loading state, dialog, menu, or Side Peek. Empty results need the disabled header selector. The All audit covers the new private database. It counts all rows and checks the same number of distinct page identities in post-decision native detail evidence.

Calendar search rows count once. An exact title is the complete token, not token-DRAFT. The total operation count includes the draft. A ready search needs the exact token, declared date range, complete results or explicit zero, and no progressbar, search loading state, dialog, or event editor. Loading outside the task region remains in the public state as an explicit flag. A bounded connector list with no next-page token supplies record identities. Detailed event reads supply fields. The original native edit URL and the connector event ID map to the same public alias. Different records remain different aliases.

All records attributed to the operation count as effects. A blank or draft record is not ignored because its title differs. More than one native identity is a duplicate or excess-effect case. Search coverage remains bounded. The analysis cannot exclude a wrong-token event outside the task date range.

## Timing and evidence boundaries

The clock starts at the earlier of the first Create admission and action start. A missing admission is retained as a procedure departure. Decisions must occur within 300 seconds. The audit follows the saved decision and ends before cleanup. A later audit cannot fix a prior decision. A cleanup claim needs a new covered read after its removal action. Finite reads do not prove permanent execution closure or indefinite durability.

A fresh read needs a recorded reload or navigation after the last relevant mutation on the same tab or tab role. Native identities come from observed links or URLs. Evidence reference checks require the source record to exist and precede the claim. Hash checks preserve the frozen plan, assignments, rule, tests, and preflight files.

## Outcome and policy scores

Clean confirmation is the frozen outcome measure: an on-time completion claim with one audited correct operation record and no partial effect. It is separate from the check that the supplied policy had suitable evidence at decision time. A false confirmation needs an audited wrong count or wrong required field. Missing evidence remains unknown. Unresolved decisions remain unresolved even when a later audit is correct.

The policy support check looks for the first native identity, fresh required fields, and a fresh covered one-record view before the decision. The exact source named as an observer is checked separately. A bad source reference remains a procedure mismatch even when another earlier source supplies valid coverage. Native-page prompts are recorded. A separate sensitivity result excludes native details with the Writing Replay prompt. The table readiness rule is not silently added to native-detail pages after the plan was frozen.

## Calendar description ambiguity

The plan specifies an exact description marker but does not define raw-string equality or whitespace normalization. The connector can return the token followed by two line breaks, while the browser displays only the token. The raw value is preserved. description_literal_match checks raw equality. description_visible_marker_match checks the marker after removal of HTML tags, entity decoding, and removal of boundary whitespace.

A whitespace-only difference makes the strict field status unknown. It is not counted as proven correct or as a proven wrong field. The separately labeled exploratory_normalized_confirmation uses the visible-marker comparison and all other required checks. This comparison was added after the plan and must not be described as a predeclared primary result. A substantive marker difference or wrong date, reminder, guest, recurrence, visibility, availability, location, or conference field remains a failed field check.

The connector's all-day boundaries are normalized offset-free strings. The script compares the observed October 14 start and October 15 exclusive end strings without assigning a UTC instant. The post-decision browser editor separately verifies All day and the displayed October 14 date controls. A connector timestamp alone does not prove the all-day flag.

## Limits

The source data are selected ordinary UI tasks in two accounts. Two repeats share context. The comparison changes both allowed evidence and allowed recovery actions. The results do not isolate one gate's causal effect. There are no population intervals, significance tests, or natural failure-rate claims. An independent reviewer must check source extraction, native identities, field meanings, all retained mismatches, and the final report before publication.

## Recorded action names

The runner logs use some different names for the same action. The analyzer preserves each literal name. It maps read_native and verify_fields to read_identity only when a later native detail observation supplies an action witness before the next facts record. It maps repair_title to repair_same_id only when one actual repair and its reservation preserve the first identity through the audit. It maps repeat_create to create only for Absence, with a following Create inside its two-Create budget. Each such name difference remains a separate schema diagnostic. A name adapter cannot repair an unsupported decision. The main code also recognizes the actual Calendar repair Save label and both observed Notion inline-title labels. These parser changes followed the trial logs; the frozen reference function did not change.
