# Browser application method review

Date: 2026-10-15. Review status: PASS for the code-level checks listed below. This review does not score or replace browser-agent trials.

The reviewer read `browser_plan.md`, `browser_config.json`, and `browser_app.py`. The reviewer then wrote and ran `browser_app_checks.py`. Each fixture uses its own temporary database. No scored trial was started and no browser control was used in these checks.

Reviewed application SHA-256: `9f37c87e85dc85669ff18dbdb89d658fe3861feda88adb7542cb965ee4f7f705`.

## Checks

All eight checks passed on CPython 3.13.7 on Darwin:

1. A permanent drop has no effect and remains final when resolution is called again.
2. Two admitted successful attempts create two separate durable records. An independent SQLite connection can read the committed records and event rows. Repeated resolution of one attempt does not create another effect.
3. The count and first-attempt status use the same historical cutoff. A record remains hidden just before the lag boundary and becomes visible at the boundary. Re-rendering the page alone does not refresh the snapshot.
4. A stop event retains the exact latest snapshot, including its index and record IDs. A pending initial write can finish after a claim and create a second effect. The original stop snapshot does not change.
5. Trial records and snapshot identities stay separate. The two-attempt cap is enforced. An action after stop is recorded and rejected. One trial's stop does not stop another trial.
6. The server records a late completion claim with an observed duplicate. It does not hide this policy violation behind a client-side safety gate. The analysis must score the violation.
7. The shared trial-start budget rejects a new trial at its boundary. An existing data directory cannot be reused to overwrite a prior run.
8. A real timer persists its effect after an unresolved stop. A second database connection can read that effect. The measured delay in this smoke check is retained in `browser_app_checks.json`; it is not a benchmark result.

The first seven tests use a controlled clock and a manual timer queue. This makes equality boundaries and event order testable without long waits. The eighth uses the real timer and clock. No test uses a scored trial ID or data directory. Run `python3 browser_app_checks.py` from the package directory to repeat these checks. Runtime durations and the smoke-test delay will vary.

## Implementation assessment

The UI has explicit state requests. It keeps the last requested snapshot static and labels its observed elapsed time. The fixed-bound rule can therefore use a newly requested snapshot at or after its threshold. The terminal rule can use an attempt-specific permanent-drop state. Both count and status share the same lagged timestamp.

The server appends a distinct SQLite record for each successful attempt. It commits records and events with `PRAGMA synchronous=FULL`. The JSONL copy is flushed but not explicitly synced. Treat the SQLite event table and record table as the durable audit source. Compare the JSONL export against that source as an additional check.

The server records accepted attempts, configured outcomes, actual resolution times, requested snapshots, button actions, rejected actions, and stops. Timers continue after stop. The final scored audit must wait until `unresolved_attempts` is zero. Freeze the export only after that condition holds. Copy the SQLite database after all writes settle or use SQLite's backup API.

The UI does not decide retry timing or enforce a successful completion claim. It does enforce the shared attempt cap and prevents new UI actions after stop. These controls match the saved plan. An attempted third submission or a late or invalid claim must remain a scored violation.

## Limits and required report statements

Nominal timer delays are scheduler requests. They are not hard real-time guarantees. The application logs actual delays so the analysis can identify timing-contract breaches. The observed action delay includes database logging before the timer starts. The fixed 24-second threshold is a selected conservative baseline for the configured scenario combinations, not an estimated optimal timeout.

Code-level tests establish the exercised local behavior. They do not establish crash recovery, power-loss durability on all hardware, secure isolation of runners, or safety on third-party websites. In-memory attempt state is not recovered after process restart. A process crash would invalidate the uninterrupted-run assumptions and must be reported. The local audit endpoint exposes hidden state if deliberately opened; the runner instructions prohibit it. This is limited procedural blinding, not a security boundary.

A runner can miss the pending or stale window because browser and model calls take time. Retain these trials and report exposure from the actual requested snapshots. The instructed absence rule tests a selected unsafe policy. It does not estimate an uninstructed model's error rate.

The final analysis still needs an independent audit of actual browser actions, event order, snapshot identity, rule adherence, final records, and paired calculations. No browser result is implied by this code review. A separate Codex agent performed this review. It is not human or external peer review.
