# Review record

Date: 2026-10-13. Codex generated the study. Separate Codex agents checked sources, methods, and final reproduction. No human or external peer review occurred.

This record uses relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), accessed on this date. It is a review aid. It does not establish NeurIPS approval or submission compliance.

| Area | Check and evidence |
| --- | --- |
| Claims | All three planned rules and all seven sets are reported. Five class-level reversals and two conditional review failures are visible. No population safety, significance, causal, or first-discovery claim is made. |
| Limitations | Report states selected data, unknown label and item relationships, fixed source runs, previous exposure, small accepted counts, lack of reviewer data, and differences in policy. |
| Formal claims | System-error and break-even identities follow from count accounting. Exact random-selection probability is stated with its finite support. The independent validator checks fractions and quantile boundaries. |
| Reproducibility | Input, hashes, plan, code, item rows, 63 group rows, 944 probability rows, 378 scenario rows, controls, commands, versions, and logs are included. |
| Data and selection | All 1,398 common items and all five models are retained. Binary labels, key uniqueness, model completeness, and shared labels pass. No learned threshold, training split, or fresh model evaluation is claimed. |
| Uncertainty | Exact central random-routing ranges describe randomized selection on fixed data. They are not population confidence intervals. No p-values or significance claims are used. |
| Compute | Python standard library on the local CPU. Separate local plot environment. No model training, new model inference, paid API calls, or paid compute. |
| Ethics and misuse | No source text, attack instructions, or private records. The results give no deployment or demographic fairness approval. Deferred cases are not counted as corrected outcomes. |
| Licenses | Pinned upstream DATA_LICENSE.md was reopened. Its Git blob is b072612b2f026bd5fe10c53eecef3d9d5ecbe2e2. The reduced input retains CC BY 4.0 attribution. No new license is assigned to owner work. |
| AI use | Main Codex agent performed study design, code, calculation, and drafting. Separate source, method, and final-review agents checked their stated scopes. No human authorship, review, affiliation, or endorsement is implied. |
| Human subjects | No people were recruited or evaluated. Review performance is hypothetical. No ethics-board approval is claimed. |

## Separate review evidence

- Source review: [source_search.md](source_search.md) records primary sources, search terms, read scope, and access limits. Prior work already contains the methods and concerns used here.
- Method review: [method_review.md](method_review.md). Independent validator passed 53,852 checks, including 284 direct small-subset cases.
- Final review: [final_review.md](final_review.md) records a fresh reproduction and report checks. This file is completed before publication.
- Actual failures and repairs: [failed_checks.md](failed_checks.md).
- Release checks: [release_checks.json](release_checks.json), including input and plan hashes, relative links, and secret-pattern scan. Automated scans have limited scope; they are not a security certification.

## Text and source checks

The report uses short paraphrases with attribution. No source paragraphs, figures, tables, or code were copied into the study. Source titles and bibliographic fields are preserved for identification. The main input consists of attributed reduced labels. References are used only within their recorded read scope. A separate source agent read the relevant Jones and Mozannar sections; the root agent also read the relevant Geifman, Cheng, and Safety-Flag sections.

No material issue may remain unresolved at publication. Publication is confirmed separately by a fetched remote commit and matching file hashes.
