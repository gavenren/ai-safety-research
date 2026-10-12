# Review record

Date: 2026-10-12. Status: PASS for publication checks. Remote publication is verified separately after upload.

Codex generated the report and code. Separate Codex agents performed source and method checks. No human or external peer review occurred.

## Relevant NeurIPS checklist items

This uses the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) as a review aid. It is not a submission, approval, or certification.

| Area | Evidence and result |
| --- | --- |
| Claims and scope | Report distinguishes measured saved votes from a hypothetical product model. It makes no forecast, harm-rate, global novelty, or causal training claim. |
| Limits | Report states policy differences, selected data, in-sample margins, hidden item difficulty, overlapping comparisons, endpoint bootstrap limits, and reference-label uncertainty. |
| Assumptions and calculation | Plan states the conditional independence reference and paired item-resampling assumptions. Report derives the disjoint-event sum. No new theorem is claimed. |
| Reproduction | Fixed input, hashes, scripts, result tables, seed, requirements, environments, and logs are included. |
| Settings and uncertainty | Fourteen full-panel cells are primary; all ten triples are planned sensitivity checks. Ranges are pointwise conditional percentiles with no population or family-wide coverage claim. |
| Compute | Existing local CPU tools only. No training, new model inference, paid compute, or API inference charge. Run time is saved. Peak memory was not measured. |
| Ethics and misuse | No source prompt, response, private record, or actionable attack detail is included. Report warns against universal safety rankings and guarantees. |
| Rights | Pinned source DATA_LICENSE.md confirms CC BY 4.0 for derived data. Attribution and transformation details are retained. No new owner-work license is applied. |
| AI and human review | AI roles are stated. Human and external peer review are explicitly absent. |

## Independent method review

The method agent reconstructed the input and used exact fractions for point calculations. It checked 154 point cells, 448 pattern rows, 28,000 seeded draws, fourteen percentile ranges, and eight saved controls. All 546,783 checks passed. Full evidence is in [validation_results.json](validation_results.json) and [method_validation_review.md](method_validation_review.md).

The agent found no method blocker. It required clear wording that the product baseline uses the same sample's margins, that shared difficulty can contribute, and that the comparisons overlap. Those limits are in the report.

## Sources and text

A separate source agent read the closest primary papers. Their exact scope and source-access limits are in [source_search.md](source_search.md). The study applies an established calculation to a fixed release. It does not claim a new method. Related-work summaries are short paraphrases; no paper passages or figures are copied. The data file and data attribution are intentionally retained from the previous release. The analysis and validator were written for this study.

## Final independent review

PASS. A separate agent ran the documented analysis, validator, and figure script in a separate copy. All numerical files, validation output, environment records, and the figure matched byte for byte. All fourteen printed table rows match the saved values. No material report or method issue remained. See [final_review.md](final_review.md) and [reproduction_check.json](reproduction_check.json).

The final package check found no broken relative link or secret-pattern match. The fixed input and plan hashes are unchanged. The figure was inspected for labels, units, range direction, and readable text. Source attribution and limited novelty statements were checked. See [release_checks.json](release_checks.json).

Publication status is kept in the task record. A local file or commit is not publication proof. The parent agent will compare each uploaded file with its local Git blob hash and preserve earlier files.
