# Response to the separate AI review

Date: 22 October 2026. The reviewer was a separate AI agent, not a human or an external peer-review process.

| Finding | Change and outcome |
|---|---|
| Fleet totals do not establish a project's lower bound | Section 3 now limits the main derivation to physical fleet accounting. Section 6 gives a separate conservative project interval based on certainly and possibly attributable activity. The reviewer checked the revised inequalities. |
| Empty coverage denominator | Section 6 specifies undefined/N/A rather than perfect coverage. |
| Overlap under clock uncertainty | The manuscript explicitly requires a partition of physical device time. Timing uncertainty cannot justify counting one interval twice. |
| Threshold equality and positive exceedance | Four boundary checks supplement the original simulation; the plan records that they were added after the initial run. |
| Recent related work | Added Kimpson, Baker and Graham's October 2026 power-draw paper. The comparison distinguishes its analogue-channel bounds from this receipt/inventory interface; it makes no general identifiability novelty claim and imports no hardware performance numbers. The reviewer checked this addition. |

The reviewer reproduced the saved simulation, independently reconstructed the five scenarios, and checked 135 clipped measurement cases with three external-budget values each. These checks concern a mathematical model with stipulated assumptions. They do not test real attestation hardware or establish a real-world security probability.

After the reviewed author version, the coordinating agent changed only review-status/disclosure text, added the companion-paper link and project-requested attribution labels, and mapped `technical.md` to `report.md`. The equations, simulation and reported numerical results were preserved. The release manifest records final bytes separately from the review's author-version hashes. The requested model/reasoning labels are not asserted as runtime attestation.

The source ledger was read and the public primary-source descriptions were spot-checked. No unresolved substantive review finding remains within the documented scope. Unmeasured hardware integrity, completeness, attribution, costs and real-world effectiveness remain limitations and future work.
