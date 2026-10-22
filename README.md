# AI Safety Research

Small AI safety studies with checked sources, repeatable methods, and clear statements of research limits.

## Daily research task

The task starts each day at **7:00 a.m. America/Toronto**. The first scheduled run is **October 9, 2026**.

Each run seeks an original contribution. A new finding is not guaranteed each day. Work is published only after the checks in [the research protocol](RESEARCH_PROTOCOL.md) pass.

The task is scheduled in Codex. It is not a GitHub Actions workflow.

## Research reports

The first example study was completed on October 8, 2026. The owner requested five additional studies on October 22. The first five rows below are that extra batch; the daily schedule is unchanged.

| Date | Study | Main result | Review status |
| --- | --- | --- | --- |
| 2026-10-22 | [Repeated gate requests during overlapping undo](research/2026-10-22-overlapping-undo-gates/report.md) | In 1,596 synthetic histories, a flag opened too early in 1,196; an active-ID set stayed closed at the end in 850. Retained lifecycle states matched every checked point. | AI-generated; separate agent review passed; no human review. |
| 2026-10-22 | [A locally valid undo step can block safe completion](research/2026-10-22-safe-undo-order/report.md) | Greedy undo reached 24 avoidable dead ends in 384 primary cases. Complete search safely finished all 276 feasible cases. Synthetic model. | AI-generated; separate agent review passed; no human review. |
| 2026-10-22 | [Cancellation across restarts: when an old worker can still act](research/2026-10-22-cancel-fencing/report.md) | In 612 synthetic schedules per rule, a unique token checked before use still allowed 80 stale effects. Atomic checking and an installed fence each allowed zero. | AI-generated; separate agent review passed; no human review. |
| 2026-10-22 | [A receipt must identify both the operation and its intended change](research/2026-10-22-receipt-binding/report.md) | In 256 synthetic request pairs per rule, an account-scoped key alone gave 48 false success replies with no incorrect effect history. Stored payload checks matched every case. | AI-generated; separate agent review passed; no human review. |
| 2026-10-22 | [A final page does not prove complete search coverage](research/2026-10-22-pagination-claims/report.md) | In 4,662 synthetic worlds per rule, token-only search gave 3,108 unsupported completion claims. Token and coverage checks gave zero, with 3,108 unknowns. | AI-generated; separate agent review passed; no human review. |
| 2026-10-22 | [When correct undo leaves an incorrect decision history](research/2026-10-22-undo-visibility/report.md) | In 512 local SQLite cases with separate undo commits, all final fields were correct, but 256 decision histories failed the order check. Of these, 32 passed each separate decision check. Synthetic workload; no website trial. | AI-generated; agent checks completed; no human review. |
| 2026-10-21 | [Undo after a crash: progress records and later edits](research/2026-10-21-undo-retries/report.md) | In 2,500 primary model cases, atomic subtraction completed all cases correctly. Atomic fixed assignments made 896 false claims despite once-only steps. Simulation only; no new website trials. | AI-generated; agent checks completed; no human review. |
| 2026-10-20 | [Safe undo with missing action records](research/2026-10-20-undo-missing-history/report.md) | In 40,000 finite model cases, target agreement gave 26,380 correct completions and no false claims with a correct loss bound. Incorrect bounds can cause false claims. No new website trials. | AI-generated; agent checks completed; no human review. |
| 2026-10-19 | [Undo after later edits: six rules, an information limit, and production website tests](research/2026-10-19-safe-undo/report.md) | Synthetic study and two production extensions. New 32-case comparison: old rule 6 incorrect claims from 15 valid cases; checked rule 0 from 15, with 7 correct completions and 8 refusals. Each rule has 1 unknown. Selected cases require trusted history. | AI-generated; agent checks completed; no human review. |
| 2026-10-18 | [When a success reply arrives before a duplicate: finite memory in agent retries](research/2026-10-18-retry-retention/report.md) | A send-time cutoff had 162 duplicate cases in one 729-case setting; 36 became duplicated only after the first success reply. Safe cutoffs can lose completion opportunities. Exact synthetic study. | AI-generated; agent checks completed; no human review. |
| 2026-10-17 | [Six repair rules under concurrent edits: an exact regression audit](research/2026-10-17-repair-dependencies/report.md) | A fresh version with an old decision caused 32 invalid writes among 100 successes in one 676-case setting. Complete recomputation and guards had no bad effects in the finite model. Exact synthetic study. | AI-generated; agent checks completed; no human review. |
| 2026-10-16 | [When correct field reads do not form a correct record](research/2026-10-16-field-snapshot/report.md) | Two field scans can accept a target that never existed. A complete, non-reused revision blocks modeled false claims but rejects many correct final records. Exact synthetic study. | AI-generated; agent checks completed; no human review. |
| 2026-10-15 | [When a fresh screen is not enough: retry timing and view scope for computer-use agents](research/2026-10-15-computer-use-retries/report.md) | Nine separate studies. New 20-case saved-field test: 15 observed errors corrected on the same record; 4 correct controls; 19 confirmations with no audit contradiction; 1 unresolved injection. Earlier strict Calendar uncertainty remains. | AI-generated; agent checks completed; no human review. |
| 2026-10-15 | [Detector calibration and zero-flag tests](research/2026-10-15-detector-calibration/report.md) | A sensitivity point estimate exceeded the chosen 5% error limit in 41 of 54 boundary cases. The corrected rule controlled error but often skipped testing. Synthetic model. | AI-generated; agent checks completed; no human review. |
| 2026-10-14 | [Repeated clean windows and false declarations](research/2026-10-14-clean-window/report.md) | At a fixed 1% failure rate, passing any 299-test clean window within 2,990 tests had probability 80.49%, versus 4.95% for one window. Synthetic model. | AI-generated; agent checks completed; no human review. |
| 2026-10-13 | [Agreement and safety review routing](research/2026-10-13-selective-panel/report.md) | Unanimity lowered error for each whole set but raised it in five class groups. Review benefit depends on reviewer error. | AI-generated; agent checks completed; no human review. |
| 2026-10-12 | [Independent votes and safety panel errors](research/2026-10-12-judge-ensemble/report.md) | Independence understated five-judge error in 13 of 14 class groups. Three-judge gaps had both signs. Fixed saved-data audit. | AI-generated; agent checks completed; no human review. |
| 2026-10-10 | [Safety judge correction across test sets](research/2026-10-10-judge-transfer/report.md) | Correction increased error in 93 of 175 controlled mixtures. Clipping reduced mean error, but 64 cases became worse. | AI-generated; agent checks completed; no human review. |
| 2026-10-09 | [Zero observed failures and test dependence](research/2026-10-09-zero-failure-dependence/report.md) | Equal mean and correlation can give different zero-failure probabilities. Exact synthetic model study. | AI-generated; agent checks completed; no human review. |
| 2026-10-08 | [AI incident counts and severity](research/2026-10-08-incident-trends/report.md) | Recorded counts rose; a severity trend cannot be established from the selected labels. | AI-generated; agent checks completed; no human review. |

## Report files

Each completed study uses a folder such as `research/YYYY-MM-DD-topic/`. It includes the report, references, reproduction instructions, and applicable code, data, and results.

## AI use and review

Codex prepares the automated studies and reports. Each report must describe the AI tools used and the actual human review status.

Automated checks and agent review do not establish human review or external peer review. This repository makes no claim of university endorsement or certification.

## Research quality

The protocol uses relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) as a review aid. Reports must state their evidence, assumptions, methods, and limits. The checklist does not establish conference approval or submission compliance.

## Rights

No reuse license has been selected for this repository. Third-party material remains subject to its source license and attribution requirements.







