# Notion retry v2 run summary

This file is a post-run summary. The original actions.jsonl is unchanged. All 12 fixed trials are complete. The empty temporary parent is in recoverable Trash. No permanent deletion occurred.

| Trial | Policy | Case | Decision | Creates | Repairs | Audit total | Correct | Partial | Decision record | Audit record | Cleanup record |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| N01 | Guard | Partial | confirm | 1 | 1 | 1 | 1 | 0 | NV2-00072 | NV2-00081 | NV2-00090 |
| N02 | Guard | Cancel | confirm | 1 | 0 | 1 | 1 | 0 | NV2-00157 | NV2-00165 | NV2-00177 |
| N03 | Absence | Hidden | unresolved | 2 | 0 | 2 | 2 | 0 | NV2-00215 | NV2-00234 | NV2-00254 |
| N04 | Absence | Partial | confirm | 2 | 0 | 2 | 1 | 1 | NV2-00283 | NV2-00300 | NV2-00345 |
| N05 | Absence | Cancel | confirm | 1 | 0 | 1 | 1 | 0 | NV2-00372 | NV2-00382 | NV2-00394 |
| N06 | Guard | Hidden | confirm | 1 | 0 | 1 | 1 | 0 | NV2-00447 | NV2-00455 | NV2-00467 |
| N07 | Guard | Partial | confirm | 1 | 1 | 1 | 1 | 0 | NV2-00537 | NV2-00547 | NV2-00559 |
| N08 | Absence | Cancel | confirm | 1 | 0 | 1 | 1 | 0 | NV2-00588 | NV2-00598 | NV2-00610 |
| N09 | Absence | Partial | confirm | 2 | 0 | 2 | 1 | 1 | NV2-00642 | NV2-00658 | NV2-00689 |
| N10 | Guard | Cancel | confirm | 1 | 0 | 1 | 1 | 0 | NV2-00738 | NV2-00746 | NV2-00758 |
| N11 | Absence | Hidden | unresolved | 2 | 0 | 2 | 2 | 0 | NV2-00799 | NV2-00817 | NV2-00841 |
| N12 | Guard | Hidden | confirm | 1 | 0 | 1 | 1 | 0 | NV2-00889 | NV2-00897 | NV2-00909 |

## Limits and departures

- N01 records NV2-00001 through NV2-00013 carry baseline phase due to a REPL closure binding issue. Original labels and times remain. NV2-00014 records the correction to shared mutable state.
- N01 had failed checkbox clearing (NV2-00040) and an ambiguous blank-row locator (NV2-00042). No extra create or title assignment occurred. The observed property-value test ID resolved the row.
- N01 final decision NV2-00072 cites observer NV2-00070 with a closing Side Peek. Separate pre-decision coverage NV2-00054 was a ready reloaded All table after repair. Keep the original decision and source departure. NV2-00076 records this.
- N02 made unplanned attempts to dismiss the GPTZero Writing Replay prompt. Clicking Page properties timed out (NV2-00128). A page-main click opened an empty body textbox, with no entered text (NV2-00135). Reload restored the empty-content view.
- At N02 verification, the lead clarified that the strict observer gate applies to the database result. A fresh native detail can be read with the nonmodal GPTZero prompt if the full title is visible and no edit is pending. NV2-00140 is the live clarification. No Turn on or Disable action was used. Keep this online clarification and a conservative sensitivity analysis.
- N01 through N05 use compact policy-facts objects and some nonstandard phase labels. NV2-00396 records the change to the full frozen schema before N06. The original compact records were not changed or retrofitted.
- N03 audit summary NV2-00234 lacks its intended audit_start_utc field because the helper used an absent property name. The original post-decision audit actions and state times remain, beginning NV2-00217. N02 audit-start field equals the decision time; actual audit actions occur later. Use raw action times for a derived audit interval and label it derived.
- N03 through N05 audit summaries use a shorter schema. Their full native title reads, links, raw states, and action times remain. N06 through N12 use the full audit schema plus count aliases.
- N04 cleanup record NV2-00319 incorrectly states zero while NV2-00317 and NV2-00318 show a blank row. NV2-00321 corrects this. The original cleanup image NV2-00320 is retained. A separate cleanup-verified image and NV2-00345 record the later zero state NV2-00342.
- N04 blank cleanup remained active after native reloads with no Restore receipt. A cleanup-only second recoverable Trash action on the known ID was logged at NV2-00337/00338. This did not change the scored decision. No new trial began before the later ready zero.
- N09 named cleanup showed a stale row after Trash. Native read NV2-00670 showed Restore page. There was no second Trash call for that identity. The first blank identity was removed separately via its native Actions menu.
- Hidden-view trials show a shared Notion view change: the writer was All before New and could become Hidden after New. These observed transitions remain in raw states. Before the baseline repeat in N03/N11 the writer was explicitly set to All; the observer retained Hidden after its reload.
- All images use valid full-viewport captures, not cropped task regions. The sidebar was closed for scored work. Private raw states and native IDs remain local for root review and redaction. N02-popup-inspect.png is an extra prompt diagnostic image.
- The helper archive is a live-run helper excerpt, not an unattended browser trial runner. It expects the supported CUA runtime, fs and crypto bindings, mutable N state, and claimed writer/observer tabs. Policy decisions were applied manually and must be labelled offline if checked later by v2_policy.py.
- The 12 scored trials created 16 records. Both excluded preflight records and all scored records were moved to recoverable Trash. The new empty parent was also moved to Trash. NV2-00923 shows Restore page. The old trashed parent was not restored. No permanent delete occurred.

## Final cleanup

The final trial has ready All zero at NV2-00907. Parent cleanup was confirmed at NV2-00919. The reloaded parent has Restore page at NV2-00923. The image is images/N12-parent-trash.png.

Guard audit outcomes: 6 of 6 have one correct record. This count does not remove N01 evidence-gate concerns or the online prompt clarification. Absence audit outcomes: 2 of 6 have one correct record; 4 of 6 have two records. The Partial baseline cases gave 2 false confirmations. The Hidden baseline cases returned unresolved. These are descriptive counts from one account and one setup.
