# AI Safety Research

Small AI safety studies with checked sources, repeatable methods, and clear statements of research limits.

## Daily research task

The task starts each day at **7:00 a.m. America/Toronto**. The first scheduled run is **October 9, 2026**.

Each run seeks an original contribution. A new finding is not guaranteed each day. Work is published only after the checks in [the research protocol](RESEARCH_PROTOCOL.md) pass.

The task is scheduled in Codex. It is not a GitHub Actions workflow.

## Research reports

The first example study was completed on October 8, 2026.

| Date | Study | Main result | Review status |
| --- | --- | --- | --- |
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



