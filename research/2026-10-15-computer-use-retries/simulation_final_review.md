# Independent final review

Date: 2026-10-15. Status: PASS.

Reviewer: a separate Codex agent. No human or external peer review occurred.

## Scope

I read the report, saved plan, configuration, input manifest, analyzer, independent validator, derivations, source record, bibliography, method review, research checklist, changes record, and reproduction instructions. I checked the report tables and quantitative claims against saved run rows and summaries. I inspected the PDF check record and confirmed that it names the current report hash. The separate PDF agent owns the full page inspection.

Report SHA-256: `cd9407e6ded1f851c2545c98f6dd2d3e5cca3951d140abff35759b9efb7ae47c`.

The plan, configuration, and implementation hashes are in [reproduction_check.json](reproduction_check.json). This review applies to those files and this report. It does not prove publication on GitHub.

## Fresh reproduction

I made two fresh directories. Each received only `analyze.py`, `validate.py`, `analysis_plan.md`, `config.json`, and `input_manifest.json`. No generated output was copied into either directory before execution.

I ran these documented commands with CPython 3.13.7 on Darwin:

```sh
python3 analyze.py > run_log.txt
python3 validate.py --input-dir . --output-dir . > validation_log.txt
```

All 13 checked output and log files matched the saved bytes. The exact file names and both hashes are in [reproduction_check.json](reproduction_check.json). They include all nine numerical files, the environment record, the validation record, and both logs. The validator passed all 13,440 runs and all saved traces.

I also ran the commands with the default CPython 3.14.7. The same numerical files and analyzer log matched exactly. The environment record, validation record, and validation log differed only in their Python version field. This was an expected metadata difference, not a result difference. The exact differences are retained in the reproduction record. No package result was changed.

## Claims and method

The following report claims match the independent rerun and row checks:

- The grid contains 256 main cases, 80 separate stress cases, and 13,440 total runs.
- Every-tick absence retry produces 60 main-grid duplicates. Of these, 56 follow a one-item completion claim and four are detected before a claim.
- Zero-lag every-tick absence retry produces 12 duplicates among 64 cases.
- Terminal status and Bound 12 have the same 192 clean cases for each main schedule. Both have no duplicate in this grid.
- On the every-tick matched clean cases, the mean falls from 9.500 to 7.333 ticks. The exact percentage reduction rounds to 22.81%. Mean query count falls from 13.125 to 11.500 across all 256 cases, a 12.38% reduction. Both rules use 1.500 submissions per case.
- The H3 paired comparison has 24 duplicates only with every-tick queries, zero only with every-four-tick queries, 36 in both, and 196 in neither. The increase is 9.375 percentage points.
- The stress table keeps the two suites separate. Every-tick Bound 12 has three duplicates in the 16-case late-execution suite and four in the 64-case stale-read suite. Terminal status has no duplicates but confirms only 9 and 41 cases, respectively.
- Ideal server deduplication has zero duplicates in all 6,720 matched runs.

I found no future outcome used by a controller before a query reveals it. Resolution order, delayed reads, one-retry admission, and post-stop effects agree with the plan. The safe rules recover exactly the main cases where at least one permitted attempt can commit. The report limits that claim to the chosen grid and deadline.

The proofs state the needed contracts. The two-world result is restricted to an immediate retry with no later fallback under that rule. It does not claim that all adaptive policies must fail. The terminal rule needs a truthful permanent drop state. The time rule needs valid execution and visibility bounds. The report does not present either assumption as an observed property of ordinary websites.

## Sources and originality

I checked the source record and its stated read limits. I reopened all six cited primary sources. I checked the passages used for fast observations, durable authorization and external idempotency, browser retry uncertainty, HTTP retry conditions, and the research checklist. The RStackBench direct PDF open first returned an access error. Its author page and linked PDF then opened. The source record's main distinctions agree with the relevant paper sections.

The report gives an original finite comparison and complete trace record. It credits established retry and idempotency principles. It does not claim that these principles, the terminal rule, or the local two-world argument are new general results. The limited search cannot establish first priority. The paper labels the new results as synthetic and does not claim a measured AI model or browser improvement.

The bibliography identifies preprints. The rights record does not infer reuse permission from public access. The package redistributes no source paper, benchmark task, or outside code. I found no copied source passage in the report's related-work prose. This is a bounded manual source comparison, not an exhaustive plagiarism-database check.

## Limits and release conditions

All results concern a chosen finite model. The study has no real browser test, learned policy, field error estimate, human subjects, or real transactions. Its assumptions and deadline can limit transfer. No human or external peer review occurred.

No material claim or method issue remains in the reviewed files. Local link, privacy, secret, package-hash, upload, and remote-file checks remain the lead agent's release steps. A successful local rerun does not prove that GitHub contains the package.
