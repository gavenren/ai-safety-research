# Repeat the saved-data analysis

These commands read the public safe extracts. They make no network call and do not repeat account writes. Use Python 3.13 or another compatible Python 3 version with its standard library. The run used Python 3.13.7 and SQLite 3.50.4 on macOS 26.7.2. The exact original execution values are in [controller_freeze.json](controller_freeze.json).

From this folder:

```sh
python3 analyze_guarded.py --out /tmp/usage-guarded-analysis
cmp guarded_rows.csv /tmp/usage-guarded-analysis/guarded_rows.csv
cmp guarded_requests.csv /tmp/usage-guarded-analysis/guarded_requests.csv
cmp guarded_summary.json /tmp/usage-guarded-analysis/guarded_summary.json
python3 check_independent.py --out /tmp/usage-guarded-independent.json
cmp independent_live_checks.json /tmp/usage-guarded-independent.json
```

The analyzer reads `drive_traces.json`, `calendar_traces.json`, and the two record ledgers. It compares actual retained record aliases with settled ledger entries and checks every exported balance. It writes a row for each selected case, all request decisions, and aggregate counts. It reports `final_A_booking_error` only when terminal evidence was accepted. The invalid case instead retains a hold and has an observed-count comparison.

`accounting_checks_passed` is a narrow result. It does not certify every field proof. The injected `fields_verified:false` control is different from an unsupported `fields_verified:true` assertion. Calendar's initial true assertions lacked IANA zone evidence. The adapter files and execution notes preserve that negative result and the later checks. A later proof does not change the status of the earlier unsupported claim.

The independent checker derives states from accepted report prefixes and immutable allocated keys. It does not import the controller. Its case vector was frozen before source access; the full checker was written after source review. It checks the same account traces, not new trials. A separate raw-evidence audit is needed to check the provider-ID maps and source claims.

The following optional command repeats invented local probes, including two-connection races. It uses temporary local databases and does not contact Google:

```sh
python3 independent_probe.py --out /tmp/usage-guarded-probes.json
```

These probes are separate from the 16 production cases. The observed record counts and fields require the retained source evidence. Repeating the live test requires an authorized account, fresh markers, and the procedure in [README.md](README.md); it will produce new IDs and times. The frozen operator guide remains unchanged, so later deviations and field-adapter corrections must be read with it. Cleanup does not erase the historical creation count.
