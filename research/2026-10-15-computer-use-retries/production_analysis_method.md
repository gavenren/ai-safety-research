# Production analysis method

This is the main analysis, written by the study-design agent. It is not an independent review. It uses only Python's standard library. It makes no network or browser calls.

Run these commands in the paper folder:

```sh
python3 production_analyzer_tests.py
python3 production_analyze.py --input-dir . --output-dir .
```

The five analysis outputs are `production_trials.csv`, `production_groups.csv`, `production_summary.json`, `production_analysis_checks.json`, and `production_analysis_log.txt`. The main outputs contain no run-time timestamp, random sampling, absolute path, or host-dependent value. Repeated runs on the same input bytes produce the same outputs.

## Inputs and count rules

The assignment CSV fixes all 24 rows. The two JSONL files contain full task-region observations, actions, decisions, audits, corrections, and images. The analysis does not use a runner's result table. It verifies the frozen plan hashes and records input hashes. It checks record IDs, reference identity, timestamp order, and action-to-observation links. A before-state for a baseline view change can refer to the prior trial's cleanup state in the same tab role. This does not supply the new trial's required baseline.

Notion rows are read from the table area after its Name header and before the New page control. A row starts at its own checkbox. Nested buttons and generic text do not add rows. Blank rows count as partial records. The parser requires the full saved readiness markers. A partially loaded positive row is unknown, just as a loading empty view is unknown. Page identity comes from native Open in full page links, including the stable public ID aliases. These links must be in audit observations after the decision and before the first Trash or delete request. A read-only cleanup menu does not end this audit window. A creation link alone is insufficient. A distinct-ID count must match the covered post-reload table count. If the counts differ, the raw row and ID counts remain in the output, but the complete audit count and duplicate outcome are unknown. Missing identity evidence does not prove a wrong field or a false confirmation.

Calendar rows are read once from each search-result row. Gridcell and button repetitions do not add records. The parser verifies the exact search token and date range in the observed native URL. It requires a complete search result and no loading marker. The later connector count comes from the raw service reply with a complete exact-token primary-calendar list, and distinct event IDs. The runner's declared count is not used to set the result. Detailed event reads supply actual event fields.

## Decisions and uncertainty

The initial clock is Calendar Save or Notion New, as defined in the frozen plan. Later title edits are part of the same Notion attempt. The analysis uses the first fully ready observer state after the common reload. It checks decision evidence against the saved decision time. A later audit cannot change an unresolved decision to confirmed.

A count confirmation is an on-time confirmation followed by exactly one audited target record and no partial record. A strict clean confirmation also requires all task fields to match. The Calendar form used noon in a displayed GMT-04 Eastern Toronto zone. The API reported 11:00 at -05 for the historical date. This experiment does not resolve the editor's date/time semantics. Calendar strict field consistency therefore remains unknown. A count confirmation is not reported as strict clean completion.

A confirmed wrong record count is a false confirmation even when another field is uncertain. A one-record Calendar confirmation with unresolved time fields is not labelled proven false or proven clean. Duplicate counts remain measurable independently of that time-field uncertainty.

The analysis includes every assigned trial. Known baseline and writer-view departures are policy flags. They do not erase observations or make a parsed duplicate unknown. They limit the interpretation of the supplied-rule comparison. Actual observer views are read from the states; assigned view labels do not override them.

The strict Calendar readiness rule applies to all saved progressbars, including a progressbar outside the extracted task region. A scope correction that starts from a read with such a marker remains an executed branch, but it is not a valid strict-gate activation. This does not remove a later valid decision row or an independent connector count.

Cleanup can use a later saved Calendar observation that still shows the previous exact token and covering date range. Such a read must follow that trial's deletion and reload, show a ready zero with no partial record, and precede the next trial's write. The output retains its actual observation ID and original trial label. `cleanup_in_trial_zero` keeps the earlier evidence separate from `cleanup_verified_later`. Later cleanup evidence cannot repair an earlier rule decision or remove an earlier readiness departure.

H-P1 uses the known duplicate-count outcomes. H-P2 needs known strict clean outcomes. H-P3 fails if a known All control is unresolved, late, false, or has a retry. Otherwise it remains unknown when strict field checks are unknown. Each site's rule-activation gate is separate from these outcome criteria.

## Validation status

`INCOMPLETE` means at least one assignment lacks a decision or cleanup observation. `NEEDS_REVIEW` means an input-reference, chronology, or required evidence check needs resolution. `PASS_WITH_RETAINED_CASES` means the evidence checks pass while reported policy departures or measured field uncertainty remain. This status does not mean that all trials succeeded or that the protocol was followed in every trial.

The author tests use constructed adversarial strings. They check loading states, false empty results, repeated labels, blank pages, missing scope, stable identity after a title change, field uncertainty, identity conflicts, and audit timing boundaries. They also check that a later audit cannot repair a decision. They are parser tests, not additional website trials or an independent scientific review.
