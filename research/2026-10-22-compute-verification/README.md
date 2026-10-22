# Compute verification: technical paper

Read [Bounding AI Compute with Attested Receipts: A Coverage-Aware Accounting Protocol](report.md).

This working paper proposes a compute-accounting interface that reports measurement uncertainty, gaps in enrolled device time, and a separate budget for activity outside the inventory. It derives conditional fleet bounds and a conservative project-attribution variant. It does not implement a secure hardware meter or establish that existing hardware meets the assumptions.

The companion [governance paper](https://github.com/gavenren/ai-policy-governance-research/blob/main/studies/2026-10-22-compute-verification/paper.md) specifies how scoped findings can inform decisions, with a separate recordkeeping track and a process for challenge.

## Reproduce the example

From this directory, using Python 3.9 or later and the standard library:

```sh
python3 technical_simulation.py
python3 reviews/technical_check.py
```

This regenerates [technical_results.json](technical_results.json). The original execution used Python 3.13.7 and seed 20261022. It contains five synthetic missingness scenarios, an exhaustive check of 4,096 small missingness patterns, four threshold boundary checks, and a deliberately invalid meter example. No accelerator, network service, or model call is needed. All numerical quantities are synthetic abstract operation units.

The independent check is documented in [reviews/technical_review.md](reviews/technical_review.md); run its checker from this directory as described there. It validates the finite arithmetic examples and the stated assumptions, not hardware security.

## Files and evidence

- [report.md](report.md): full manuscript and references.
- [technical_plan.md](technical_plan.md): analysis plan and recorded changes.
- [technical_simulation.py](technical_simulation.py): complete input generator and accounting calculation.
- [technical_results.json](technical_results.json): executed synthetic results.
- [technical_sources.md](technical_sources.md): search terms, primary-source locators, and original paraphrase notes.
- [references.bib](references.bib): bibliographic metadata.
- `reviews/`: separate AI review, independent arithmetic checks, and response to findings.
- [release_checks.json](release_checks.json): final artifact hashes and release checks.

The small package uses a flat layout for its analysis files. In the original working plan, `technical.md` refers to the manuscript published here as `report.md`, and `technical_references.bib` refers to `references.bib`. The plan was recorded before simulation; additional boundary checks and project-scope clarification are disclosed revisions.

## Attribution and limits

Codex generated the paper and analysis, with a separate AI agent conducting critical review. No human review or external peer review is claimed. The project-requested attribution is **GPT-6.1 Sol**, reasoning level **Ultra**. These are owner-requested attribution labels, not independently verified runtime metadata.

Only bibliographic metadata, links, and short original source summaries are included. Source notes are not original-source snapshots. No copied figures, third-party datasets, or new reuse license are included. This is an exploratory technical working paper, with elementary conditional results and synthetic validation.
