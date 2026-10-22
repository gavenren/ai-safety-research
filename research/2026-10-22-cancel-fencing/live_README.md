# Reproduce cancellation scores

This package contains eight controlled production browser cases. It includes six logged browser saves and two blocked commands. It does not test native atomic cancellation at the receiver.

The original provider records and full UI snapshots remain private. Public data use aliases and synthetic field values. To repeat the local scores, use Python 3.13.7 or a compatible Python 3 release on a Unix system:

```sh
python3 live_analysis.py --trace live_trace.json --output reproduced_results.json --execution reproduced_execution.json
cmp live_results.json reproduced_results.json
```

The result bytes must match. Runtime timestamps and durations will differ. The script uses the standard library and a 30 CPU second process limit. It calls no account, model, or network service. No random seed is needed.

`live_trace.json` records what the saved private evidence supports. The `ui_gates` for Calendar C1, C3, and C4 describe the filled editor before Save. They are not a post-save editor check. The saved connector response confirms the intended description and unchanged exposed fields. `complete_for_declared_scope` means complete for these reported checks, not that every step in the initial plan was satisfied. The report discloses the missing reopened Calendar editor and the late helper freeze for Drive C1.

Files:

- `live_trace.json`, `live_results.json`: sanitized case evidence and all scores.
- `live_execution.json`, `live_execution_repeat.json`, `live_reproduction.json`, and logs: actual local runs and exact byte comparison.
- `build_live_trace.py`: private evidence validator and sanitizer. It needs the original private folder one directory above this package. It cannot fetch deleted records or independently reconstruct private source bytes from hashes.
- `live_analysis.py`: public scoring code.
- `analysis_freeze.json`: code and trace hashes before scoring. The analysis implementation was written after collection; declared case rules were fixed earlier.
- `live_plan.md`, `live_design.md`, `live_readiness_amendment.md`, `live_execution_freeze.json`: pre-execution plan and field limits.
- `live_intent.py`, `runtime_intent.py`, `runtime_intent_freeze.json`, `runtime_intent_review.md`: pure decisions, actual local event logger, helper freeze, and review history.
- `live_browser_helpers.txt`: the relevant browser helper definitions used during execution. It is an evidence and reproduction aid, not a standalone script with account access.
- `report_extension.md`: report text for the same existing paper.

The original runtime CLI needs a private manifest and evidence files. Do not run it against old real fixture IDs. A new production replication must use fresh temporary records, a new namespace, a new plan, and a supported connected browser. Freeze the new plan and implementation before the first preparation. Keep service account writes separate from local decision logs. Use the four defined C1–C4 orders, retain failed and unknown cases, and read the exact record after a save. Do not infer identity from a title alone. Keep the two blocked cases in the table.

Record the native-ID and field checks without publishing private IDs. Read every intended fixed field in the supported UI or connector. If an all-day flag or other field is absent, report that missing evidence. A success toast alone is not a saved-field check. Use recoverable Trash for known test records and verify cleanup separately. The parent run owns the current test records and cleanup receipts.

The two local runs in this package reused the same eight website cases. They do not add independent observations. The counts cannot estimate a general website or agent failure rate.
