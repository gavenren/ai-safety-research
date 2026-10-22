# Repeat the live gate analysis

The live browser test used Google Drive and a connected account on 2026-10-22. The public replay does not access that account or repeat its browser actions. It scores the retained public evidence with Python 3.13.7 and its standard library.

From this folder:

```sh
python3 live_gate_analyze.py live_evidence.json live_results_replay.json
cmp live_results.json live_results_replay.json
```

The unchanged local controller is in `live_rules.py`. Its SHA256 is `7389d34fad62dac156f709032ba02b6722edb5ec1cd274d27fa515abff502d51`. `live_build.json` identifies the local sanitizer and builder that produced this extract. The public replay checks 200 rule/state comparisons. It does not create additional live cases.

`live_evidence.json` contains all eight cases and forty observed request boundaries, including timing deviations. `live_results.json` separates descriptive counts from timing eligibility and fresh metadata eligibility. `live_evidence_map.md` names the actual private source files and gives their hashes through the JSON references. Full private UI text and account identifiers are not distributed.

The synthetic corpus in the main report is a separate experiment. Do not add its case count to the live count. The repeated use of two folders means these live cases are paired controls, not independent samples. Cleanup and separate review are recorded in [live_cleanup.md](live_cleanup.md) and [live_review.md](live_review.md).
