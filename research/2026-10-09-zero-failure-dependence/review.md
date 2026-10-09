# Publication review

Date: 2026-10-09. Codex completed these checks. This is not human or external peer review.

## Required checks

- Claims: the report states the model assumptions and does not claim real AI measurements. All table values match the saved results. The nine substitution failures and largest gap match the full grid.
- Prior work: a separate agent checked the closest sources and the final source claims. The report credits established methods. It does not claim a new model, theorem, or first discovery. Sources are paraphrased and linked. The search scope and access limits are recorded.
- Mathematics: a separate agent checked matched moments, within-group correlation, zero-failure formulas, monotonicity, and limits. Derivations are included. The three examples are not claimed to be global bounds.
- Procedure: the README calculation and validation commands were run from this folder. The full design gives 252 probability rows and 84 boundaries.
- Independent calculation: validate.py uses 60-digit Decimal arithmetic and does not import analyze.py. All checks passed. The largest absolute P0 difference is 1.41035e-13. The largest boundary difference is 5.69846e-16. The tolerance for saved results is 5e-13.
- Controls: 486 independent moment, correlation, small-group, and limit controls passed. The independent numerical check also passed 10,500 monotonicity comparisons. Analytical proofs supply the general monotonicity claim.
- Figure: the chart was generated from the CSV and visually checked. Labels state the hypothetical parameter values and distinguish the approximation.
- Rights: no source text, dataset, model weights, or third-party code is redistributed. No new license is assigned to the repository owner's work.
- Privacy and misuse: text was checked for secrets, personal data, private paths, copied source passages, and actionable harmful details. No such material was found. Mathematical attack-risk papers are cited without reproducing attacks.
- Files: internal Markdown file links were checked. Only the flat study files are included. Bytecode caches and local environments are excluded.

## Failed check and correction

The first main implementation used subtraction from one in the zero-atom formula. A reviewer found that it could fail when p was the largest floating-point value below one. This did not affect the planned grid or roots. The implementation was changed to a positive sum evaluated in logarithms. Twenty-one near-one checks were added. The full calculation and independent validation were repeated and passed. Rounded report values did not change.

The reviewer also found that an earlier validation log described the first implementation. The log was replaced after the code change. Current hashes are in validation_log.txt. A sentence about values selected before analysis was narrowed to grid parameters. The largest-gap example remains marked as selected after inspecting the grid.

## Relevant NeurIPS checklist items

The [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) was used as a review aid. This is not a conference submission or approval.

| Item | Result and evidence |
| --- | --- |
| Claims and scope | Pass. Report Sections 1, 2, and 6 distinguish a numerical study from real AI evidence. |
| Assumptions and proofs | Pass. Report Section 3 and derivations.md. |
| Reproduction | Pass. README commands, code, complete results, and logs are included. |
| Resources | Pass. Python 3.13.7 and plot dependencies are recorded. No paid service or live model run. |
| Uncertainty | Pass. Numerical tolerance and sensitivity are separate. No sampling error bars are claimed for deterministic calculations. |
| Limitations | Pass. Synthetic parameters, atom distributions, unknown real correlation, and missing deployment validation are stated. |
| Ethics and rights | Pass. Report Section 7; no private or third-party dataset. |
| Human subjects | Not applicable. No subjects or participant data. |
| AI assistance | Disclosed. Codex generated and checked the work. No human review occurred. |

Publication must still be confirmed from the remote files. A local completed check is not proof of upload. The task state records the verified commit after publication.
