# Independent browser evidence review

Date: 2026-10-15. Status: PASS for the fixed evidence and the report text listed below. No material correction is open.

This review does not mean that every trial succeeded. Four trials made duplicate records. Two trials stopped without a completion claim. One trial made a late claim. All trials remain in the data.

A fresh Codex agent made this review. The reviewer did not write the application, analyzer, or method review. The reviewer first read the saved design files. It did not read live trial data or runner logs before the lead declared the evidence fixed. This is AI review. It is not human or external peer review.

The reviewed report SHA-256 is `dfac57c142a8379363610e036b362798b70515e0d2bbdf07720e86a327562d75`. The review also covers README.md, browser_changes.md, references.bib, browser_environment.json, browser_source_search.md, and the updated repository index. Their hashes are in browser_reproduction_check.json. A later text change needs a check of the changed text. PDF layout and remote publication are separate checks.

## Evidence and repeated analysis

The reviewer opened the frozen SQLite database in read-only mode. Its integrity check passed. All 380 event rows agree with browser_audit.json and browser_events.jsonl. All 23 stored rows agree with the audit. These counts include warm-up W01. Each accepted attempt has one resolution. Each successful attempt has one stored row. The final audit has zero unresolved attempts.

Separate code rebuilt all 18 scored trial rows from the committed events and stored rows. It did not import the app or analyzer. It checked all 846 reported fields, or 47 fields per trial. It also recomputed all six planned timing pairs. The values agree with browser_results.csv and browser_pairs.csv. Snapshot IDs, historical counts, record IDs, status, submit order, resolution order, stop state, and post-stop flags agree.

The reviewer ran browser_analyze.py again in a separate output folder. These four output files matched byte for byte: browser_results.csv, browser_pairs.csv, browser_summary.json, and browser_analysis_log.txt. This repeats the fixed-input analysis. It does not repeat the model or browser trajectory.

The independent checker is browser_validate.py. It uses only the Python standard library. To repeat it, use a separate output folder:

```sh
python3 browser_validate.py --input-dir . --output-dir validation-output
```

It writes browser_validation_results.json. The package contains the raw result from the review run. Its code hash and raw result hash are in browser_reproduction_check.json. It checks all 846 trial fields, 107 task actions, and 61 scored snapshots. It runs the analyzer in a separate process and a temporary folder. It never imports the app or analyzer.

## Retained outcomes

| Rule | Assigned trials | Duplicates | Clean claims by 60 seconds | Unsafe claims | Unresolved stops | Late claims |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Absence | 6 | 4 | 1 | 4 | 1 | 0 |
| Bound24 | 6 | 0 | 5 | 0 | 1 | 0 |
| Terminal | 6 | 0 | 5 | 0 | 0 | 1 |

A04 has one final record. Its completion claim arrived at 69.230 seconds. Its last requested snapshot was at 20.076 seconds. It is a retained deadline failure. A02 and B05 have one record each, but both stopped unresolved. The server-visible rule checks pass for 17 trials and fail for A04. A rule check is separate from a safe final outcome: the four unsafe absence claims follow the supplied weak rule.

The three absence trials with an empty observation before a later initial commit all made duplicates. This meets the saved H-B1 test. A09 also made a duplicate after a stale empty observation. All four duplicate trials had two stored records before the claim. There are zero post-stop effects and zero duplicates created after a claim. H-B3 therefore has zero observed cases.

Terminal and Bound24 each have five clean claims and no duplicates. Four pairs are clean under both rules. Terminal is faster in two pairs and slower in two. Their differences are -4.739, -15.491, +1.673, and +37.124 seconds. The median is -1.533 seconds; the mean is +4.642 seconds. Only the B failure pair supports a clean failure-condition time comparison. The report preserves the two excluded pairs and does not claim a general browser speed gain.

## Times, budget, and saved design

The current plan, configuration, and app bytes match the saved design and execution manifests. Both manifest times precede the warm-up and scored submissions. The server-start event precedes the execution manifest by about one second; the manifest does not claim to precede server startup. These local hashes and times are consistent. They are not an external preregistration or an independently certified time stamp.

All 18 assigned trials started once, in the specified runner order. All 18 stopped. The last scored stop was 609.965 seconds after the first scored submission, within the 720-second budget. No rejected extra action or replacement trial is present. All accepted attempts resolved before the final audit. The selected 24-second resolution-plus-lag bound was not breached.

The logs report context recovery or compaction delays in A02, A04, B05, and B07. Repeated Statsig HTTP 403 notices are telemetry notices in the supplied record. All logged task actions have matching server actions. These data do not separate time spent on model inference, tools, telemetry, recovery, or shared host load. They cannot support a causal speed estimate or a natural model error rate.

## Browser logs and screenshots

Runner A has 140 log rows; runner B has 135. All 107 task-action entries match the server button actions in order. All 61 scored Check state entries match the server snapshot number, rounded elapsed time, count, and status. The largest absolute log-to-server action time difference is 0.264 seconds. Each log shows only its assigned trials. No hidden condition value or audit response appears in the reviewed UI states.

The logs contain actions and returned states. They do not contain tool code or model turn boundaries. They cannot alone prove UI-only access, no hidden-state access, or one separate model decision per action. The report states this limit. The procedure uses instructions for separation; it has no secure boundary between the two contexts.

The archive has 20 unique images: one for each stopped trial and one for each completed runner. The reviewer checked contact sheets containing all 20 images. Each source image is 1512 by 771 pixels. They show the local task or runner completion page. The visible trial IDs, stop types, and snapshot fields agree with the logs. They show saved viewports; lower page content can be outside the viewport. All 20 original .png filenames contain JPEG data. The images open correctly. Their original names and bytes remain fixed. Use a viewer that detects the format from the bytes. A screenshot is not proof of the final stored count.

## Claims, sources, and private data

The current report, package README, and repository index keep the constructed task separate from public-web performance and natural agent behavior. They keep browser seconds separate from simulation ticks. They retain failed trials, timing limits, the AI-use statement, and the absence of human review. The original simulation was not re-audited in this review; its retained review records cover that evidence.

The reviewer opened the [added author source](https://exzilcalanza.info/rstackbench-browser-agent-reliability/). Its title, date, controlled local scope, and model planning pilot agree with the added citation. The review did not repeat the original full literature search.

The text check found no absolute user-home paths, private keys, token values, or email addresses in the reviewed browser files. The screenshots show no private account content or unrelated page. This is a bounded check of the supplied package. It does not prove that every possible private-data form is absent. The final release must keep any unreviewed raw tool transcript outside the package.

See browser_reproduction_check.json for hashes, independent per-trial values, timing pairs, and check counts. No publication action was performed by this reviewer.
