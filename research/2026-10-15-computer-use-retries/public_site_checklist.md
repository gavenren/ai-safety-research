# Review checklist for the live website extension

The NeurIPS Paper Checklist was used as a review aid. This is not a claim of conference approval, submission compliance, or certification. The original reviews and evidence remain in this folder.

| Review item | Evidence and limit |
| --- | --- |
| Claims and contribution | The report separates 13,440 simulation runs, an 18-trial local pilot, and 60 live-site trials. The new contribution is a bounded empirical check of observation scope. No new retry protocol, priority, general speed gain, or field failure rate is claimed. |
| Method and assumptions | Both plan versions, feasibility checks, assigned rules, views, order, stopping criteria, logs, and failures are saved. The amended plan preceded scored actions. Local hashes are not external preregistration. |
| Reproduction | live_analyze.py uses frozen UI evidence. The separate live_validate.py passes 7,199 checks. A fresh analysis gives identical output. Exact future browser trajectories can differ. |
| Uncertainty and selection | All 60 trials remain. The report states 10 duplicate outcomes, 10 zero-task outcomes, and nine failed All controls. Fixed repeated tests on two related apps do not support population error intervals. |
| Access and leakage | Runners were instructed to use visible UI. This was not secure isolation. Logs do not prove every model-turn boundary or absence of hidden access. |
| Time and versions | Wall time includes model and tool delays. The 24-second rule is a heuristic. Four metadata warnings remain and do not change classifications. Browser and Python versions are recorded. Exact model build is unavailable. |
| Resources | The test used existing Codex and browser services. No separate paid API or new paid compute service was started. Provider compute and token counts were not available. |
| Ethics and rights | Unique test tasks were created on public demo apps. No production account transaction was used. No source app code or paper was copied into the package. Public UI evidence is attributed. No new license is assigned. Font notices remain. |
| Provenance and review | Codex generated the work and ran the browser trials. Separate AI agents checked the analysis, images, and PDF. No human or external peer review occurred. |
| Presentation | All 60 final images agree with the result counts. All 15 PDF pages pass visual review. Text coverage and a deterministic PDF rebuild pass. |
| Publication | Local checks do not prove publication. Verify remote main-branch file hashes after upload. |
