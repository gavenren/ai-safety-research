# Repeat the live order analysis

This package scores saved Google Calendar observations from 2026-10-22. It does not access an account or repeat the original browser actions. Use Python 3.13.7 and its standard library.

From this folder:

```sh
python3 live_order_analyze.py live_evidence.json live_results_replay.json
cmp live_results.json live_results_replay.json
```

`live_rules.py` is the unchanged controller. Its SHA256 is `7389d34fad62dac156f709032ba02b6722edb5ec1cd274d27fa515abff502d51`. `live_build.json` identifies the local sanitizer and builder. `live_evidence.json` retains all six paths, 22 editor observations, 16 browser field changes, metadata checks, and hashes of private evidence. `live_evidence_map.md` gives the file and time mapping.

The public replay checks the path against the same frozen rule and supplied valid-state set. It checks 36 case-level assertions, including field evidence and collateral checks. It does not independently re-query the private records. The synthetic corpus in the main paper remains separate.

The full baseline reads were a pre-run batch. Each case had a fresh browser baseline and final full connector read. Complete conference objects and server versions were not exposed. The witness greedy final connector read preceded its later browser stop check; both observed 101 after the only scored write.

Cleanup and separate review are recorded in [live_cleanup.md](live_cleanup.md) and [live_review.md](live_review.md).
