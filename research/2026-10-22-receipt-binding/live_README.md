# Repeat the live receipt analysis

This package covers 12 selected receipt cases from 2026-10-22. It keeps the original synthetic study separate. The commands below use Python 3.13.7 and its standard library. They make no account or network calls.

From this folder:

```sh
python3 live_receipt_analyze.py --evidence live_evidence.json --output replay_1.json
cmp live_results.json replay_1.json
python3 live_receipt_analyze.py --evidence live_evidence.json --output replay_2.json
cmp live_results.json replay_2.json
```

`live_evidence.json` contains aliases, exact synthetic values, the actual local responses, times, checks of private native IDs, and raw file hashes. `live_results.json` is the deterministic score. `live_reproduction.json` records actual local run times, Python version, and output hashes. No random seed is needed.

`live_intent.py` is the frozen pure policy. `runtime_intent.py` is the frozen local receipt runner. The browser helper source records the actual before-Save checks and first Save calls. The source uses runtime-supplied tabs and private manifests. It is not a standalone replay command. Do not run the account helper as part of local analysis.

The independent private audit uses `live_private_extract.py --base PATH_TO_PRIVATE_RUN`. That folder must have the original `private/` evidence and frozen source files, and `live_receipt_analyze.py`. The audit checks exact native IDs, field contracts, file and envelope hashes, action/read order, available collateral fields, and original source references. Its output goes to `PATH_TO_PRIVATE_RUN/receipt/`. Private raw evidence is not included in this public package because it contains account data.

Public replay checks the retained extract. It does not independently authenticate the original raw observations or repeat the website trial. Full browser reproduction needs an authorized connected account, fresh fixtures, and the frozen plan. The baseline metadata was a setup batch; fresh before-Save UI observations followed. One interrupted reload has unknown 30-second uncertainty-limit compliance. Cleanup and separate review are recorded in [live_cleanup.md](live_cleanup.md) and [live_review.md](live_review.md).


The six Calendar saves did not have a reopened post-save editor check. The frozen plan called for a reopen or reload plus a connector read. The connector verified the persisted description and all other exposed fields after each Save. The all-day UI check was before Save only. A post-save all-day UI check is not available. This is a procedure deviation. All six cases remain in the results, with this limit. The 11-case subset without timing uncertainty does not mean that every planned procedure step passed.
