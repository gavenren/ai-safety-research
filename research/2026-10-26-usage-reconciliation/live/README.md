# Production record extension

Date: 2026-10-26. This folder extends the [existing paper](../report.md). The original simulation remains unchanged.

We tested six local accounting rules with temporary records in Google Drive and Google Calendar. Eight A fixtures supplied saved observations for 48 paired rule decisions. The rules permitted 22 B writes. Readback verified all 12 A records and 22 B records. One Drive parent was setup and is excluded from these counts.

The budget was a local limit of two records per branch. A branch counts the shared A records and only its own B record. Google did not supply or enforce that budget. Report order and replay were set by the test. These are controlled policy replays with real record writes, not Google billing tests or 48 independent website jobs.

| Rule | Decisions | B records saved | Scoped excess cases | Final overcounts | Final undercounts | Feasible refusals after T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| AddEvery | 8 | 0 | 0 | 6 | 0 | 4 |
| DedupSum | 8 | 2 | 0 | 4 | 0 | 2 |
| LastValue | 8 | 6 | 2 | 0 | 2 | 0 |
| HighWaterEarly | 8 | 6 | 2 | 0 | 0 | 0 |
| HighWaterHeld | 8 | 4 | 0 | 0 | 0 | 0 |
| TerminalOnly | 8 | 4 | 0 | 0 | 0 | 0 |

Each excess case contained three scoped records against the local limit of two. The overcounts and refusals are local accounting results. Counts overlap and must not be added into one failure total. All selected outcomes matched the pre-execution calculations. They do not estimate production failure rates.

## Repeat the saved-data analysis

Use Python 3.13.7 and its standard library. From the repository root, run:

```sh
python3 research/2026-10-26-usage-reconciliation/live/analyze_live.py --out /tmp/usage-live-analysis
```

The command writes `live_rows.csv`, `live_summary.csv`, and `live_checks.json`. Compare these files byte for byte with the files in this folder. [analysis_reproduction.json](analysis_reproduction.json) records two completed runs with identical outputs. These reruns use the same evidence and are not additional production trials. They take no service action and make no network or model call.

The analysis repeats every saved controller transition and checks receipt bindings, evidence hashes, record attribution, saved fields, pre-decision A checks, decision-before-write timing, refusal observations, unchanged pre-cleanup records, cleanup aliases, and the prior controls. A separate agent also checked the decisions with an independently written specification; see [independent_live_review.md](independent_live_review.md).

To repeat the independent calculation check, run these commands from this `live` directory:

```sh
python3 independent_expected.py --out /tmp/usage-expected.json
cmp independent_expected.json /tmp/usage-expected.json
python3 check_independent.py --out /tmp/usage-independent-checks.json
cmp independent_live_checks.json /tmp/usage-independent-checks.json
```

To repeat the local controller code checks from the repository root:

```sh
python3 research/2026-10-26-usage-reconciliation/live/check_controller.py
```

This command uses invented receipts. Its 48 check rows are separate from the 48 live policy decisions. [controller_cli.md](controller_cli.md) explains the prepare/finish commands and receipt format. Its workspace paths are examples; use the downloaded study path when you repeat them.

## Evidence files

- [plan.md](plan.md), [controller_freeze.json](controller_freeze.json), and [expected_controls.json](expected_controls.json): the saved plan, frozen code and plan hashes, and calculations made before live execution.
- [branches.json](branches.json): all 48 completed branches, with preparation and finish times, receipt envelopes, hashes, before/after states, decisions, actual B aliases, and scores.
- `drive_receipts.json` and `calendar_receipts.json`: the eight P/T pairs. P is a progress observation. T is a local final declaration after the controlled A producer stopped. T is not a Google usage certificate.
- `drive_record_ledger.json` and `calendar_record_ledger.json`: the 34 saved record aliases and evidence references. All Drive B writes used the browser UI. Six Drive A records and the setup parent used the Drive connector. All Calendar records used the Calendar connector. A separate browser audit inspected a Calendar B record.
- `drive_observations.json` and `calendar_observations.json`: sanitized saved observations. They retain relevant fields and evidence hashes. They do not contain account IDs, private URLs, account addresses, or unrelated account content.
- `drive_cleanup.json` and `calendar_cleanup.json`: cleanup results and exact evidence limits.
- `drive_evidence_index.json` and `calendar_evidence_index.json`: names, sizes, and SHA-256 hashes of retained private evidence. Some browser files are selected breadcrumb extracts or change-only views. The later full Drive read replaces the insufficient late-A1 cleanup observation as support. A hash identifies retained bytes; it does not independently prove service state.
- [sources.md](sources.md): primary documentation checked for the extension. [live_checks.json](live_checks.json) records the public analysis checks. [calendar_execution_notes.json](calendar_execution_notes.json) records Calendar read and export adjustments.

Raw private tool replies and account screenshots remain local. Public data permit the accounting analysis to be repeated. They do not let an external reader re-open the owner's account or independently inspect all private source content. Repeating live writes requires an authorized account and will produce different record IDs and times. Follow the plan's exact scope, write-ahead decisions, saved-field checks, and cleanup steps. Do not run writes in an account without authorization.

## Cleanup and limitations

All 17 Calendar records had exact-ID cancelled readback. A bounded primary-calendar query found no active test marker. All 17 Drive child locations were checked under Trash and the test parent. The parent was also under Trash. A subsequent active test-scope query returned zero results. No trash was emptied.

The Drive metadata connector omitted the requested `trashed` field. Thus the Drive evidence is browser location evidence, not 17 observed API `trashed=true` values. The Drive search packets do not contain pagination fields. Counts therefore rely on bounded query results and exact known-ID checks, not a claim about every item in the whole account. One initial Drive cleanup view was incomplete during loading. A later full exact-ID view resolved that evidence gap without a new mutation.

Calendar `fetch` omitted the free/busy field. A full `read_event` check supplied it before P capture. All later checks used that full read. A local cleanup exporter was corrected because delete acknowledgements lacked a structured response. No production delete was repeated for that export correction.

The selected cases share fixtures and were chosen to exercise known failures. The test contains no natural delivery failures, native billing units, concurrent writers, provider token costs, or general model-performance estimate. The two complete rules passed these selected controls; this does not prove universal production safety. Cleanup removes active temporary records but does not refund historical test use.

Codex generated the code, analysis, and report. Separate Codex agents performed design and final checks. The exact model build is not exposed. No human review or external peer review occurred. No new license is assigned.
