# Review record

Date: 2026-10-10. Human review: none. External peer review: none.
Publication is permitted only after the final checks below pass.

## Separate agent checks

- A source-review agent checked the selected paper and the closest method studies. It found a narrow contribution: a secondary transfer audit on the saved Safety-Flag release. It rejected claims of a new correction method or first discovery of calibration shift.
- A methods agent reviewed the plan before rate analysis. It confirmed the mismatch identity. It requested explicit class-count pooling weights and conditional bootstrap limits. The plan amendment and report include these points.
- The methods agent wrote an independent validator. It uses exact fractions for point calculations. It checks all 35 confusion rows, all 175 grid cases, all 70,000 saved bootstrap rows, all reported percentile intervals, singular cases, and the input hash. The checks passed. It did not independently repeat the random index generation. The parent ran the documented validator again.
- A final review agent passed the scientific review. It independently ran analyze.py, plot.py, and validate.py in a separate temporary copy. The four numeric result files and the figure matched byte for byte. It verified the central source claims and data terms. Requested term definitions were added.

## NeurIPS checklist review aid

The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was read on 2026-10-10. These checks use its relevant topics. This is not a NeurIPS submission, approval, or certification.

| Topic | Check and evidence |
|---|---|
| Claim support | The abstract and results give the full planned comparison and the clipped comparison. The grid contains all 175 cases. |
| Limits | The report separates measured source errors, controlled class shares, interpretation, and deployment limits. |
| Theory | The standard correction and mismatch identity are given with their assumptions. They are credited to read prior work. |
| Repeatability | The reduced data, source hashes, code, pinned dependencies, seed, saved draws, logs, and commands are supplied. |
| Setting | Five model rows, seven task splits, class-count pooling, five mixture shares, and all exclusions are stated. |
| Uncertainty | Conditional item-bootstrap sensitivity intervals are defined. Hidden dependence and boundary limits are stated. Five unstable intervals are suppressed and counted. |
| Compute | Local CPU analysis only. No model inference, training, GPU, or paid API service. The actual analysis time and runtime versions are in run_log.txt. |
| Data rights | Safety-Flag derived labels use CC BY 4.0. Attribution, modification notes, and source terms are included. No new license is assigned to the owner's work. |
| Ethics | The reduced release has no source content or harmful instructions. It does not certify deployment safety. |
| Human participation | This study collected no new human labels or personal records. Source label limitations remain explicit. |
| AI use | Codex generated the study and report. Agent review is not human or external peer review. |

## Content and release checks

The parent checked the figure at its saved resolution. Labels and values are readable. The report gives the full numeric table, including unbounded errors above 100 percentage points.

No source paragraphs were copied into the report. The correction formula and source facts have references. The reduced input schema permits only task, item ID, model name, reference label, and decision.

A pattern scan found no credential pattern or local user path in the release. This is a limited automated check, supported by review of the reduced schema and report. Source examples, prompts, and outputs with harmful content are not included.

The first relative-link check ran while this file was still being written and reported its absence. The completed link check passed. All seven report and license URLs returned HTTP 200. Source-link results are recorded in release_checks.json.

## Final status

PASS. Scientific, independent reproduction, source, data-rights, content, and release checks passed. The validator passed 650,700 checks. Publication still requires a verified remote commit; this local review record is not publication evidence.
