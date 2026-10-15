# Review and release summary for the live website extension

Date: 2026-10-15. Prepared by the lead Codex agent. The fresh independent review is [live_review.md](live_review.md). This summary is not another independent review. No human or external peer review occurred.

## Evidence and results

All 60 assigned trials have a decision and two audits. The test used two live public TodoMVC apps, five supplied procedures, two views, and three repeats per cell. The saved plan was amended after feasibility checks and before scored actions. Both versions and all failures remain.

The trial evidence gives 29 clean confirmations and 31 unresolved decisions. Final outcomes include 40 single tasks, 10 duplicates, and 10 missing tasks. All ten duplicates have unresolved decisions. Counts agree before and after reload in all 60 trials. Reload survival is browser retention, not proof of server storage.

In Completed view, Absence and Wait24 each produce five duplicates in six trials. Scope produces none and confirms four tasks in six trials. Nine of 30 All controls fail their direct-success requirement. Ten trials have no task before or after reload. The cause of the failed input actions is unknown. The paper keeps these negative results and makes no general performance claim.

## Separate checks and reproduction

[live_validate.py](live_validate.py) uses a separate parser. It passes 7,199 checks of all 302 scored UI observations, 428 action records, 60 trial rows, 20 cells, and 120 pairs. It also checks plan and evidence hashes, timings, active state, and unchanged earlier study evidence. A fresh analysis in a temporary copy matches all three saved result files. See [live_validation.json](live_validation.json).

Four metadata warnings remain in [live_summary.json](live_summary.json): three one-millisecond start-time differences and one corrected clock-only diagnostic label. They do not change any outcome, deadline, or wait classification. Setup errors remain in the raw logs. Failed controls are study results, not reasons to remove trials.

A separate image reviewer checked all 60 final screenshots. Counts agree with the saved results. The images show final All-view audits; they cannot prove earlier decision views or timing. See [live_image_review.md](live_image_review.md). All 15 PDF pages pass visual review. The build covers every source text chunk and repeats with identical bytes. Font notices are unchanged. See [pdf_check.json](pdf_check.json) and [live_pdf_image_review.json](live_pdf_image_review.json).

## Sources, rights, and release limits

[live_source_search.md](live_source_search.md) gives current primary sources, exact searches, and read limits. The report states the relation to earlier work. A limited search does not prove novelty. The study adds evidence about filtered views; it does not claim a new retry protocol.

The package uses original prose, original analysis code, synthetic task names, and attributed public test-app screenshots. It does not redistribute app source code, source papers, or private task data. No new license is assigned. Earlier simulation and local pilot evidence remain unchanged.

[review.md](review.md) records the relevant checklist items. [release_checks.json](release_checks.json) records local link, secret-pattern, privacy, hash, and history checks. These bounded checks do not establish the absence of every defect. A separate receipt must verify remote file hashes before publication is reported complete.
