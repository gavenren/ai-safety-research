# Review record

Date: 2026-10-14. This is a Codex check. No human or external peer review occurred.

## NeurIPS checklist as a review aid

- Claims: the report states a finite synthetic model, not measured AI risk. It claims a numerical audit, not a new probability method.
- Assumptions and proof: independence, stable p, correct labels, unchanged system, strict declaration, and fixed horizon are explicit. Full event and recurrence arguments appear in derivations.md.
- Reproduction: saved plan and configuration, input hashes, code, result tables, versions, and commands are included. Core calculation uses only Python's standard library.
- Uncertainty: deterministic model probabilities have no Monte Carlo interval. Decimal precision checks are separate from uncertainty about model assumptions.
- Controls: the method agent used independent high-precision coefficients, exact binary enumeration, run states, candidate/predecessor checks, event nesting, and monotonicity.
- Limitations: no drift, model repair, dependent trials, imperfect labels, practical efficiency, or acceptance below the target is assessed.
- Compute: local CPU only. No model experiment, paid API call, paid service, or training occurred.
- Rights: no external dataset or source text is redistributed. Sources retain their rights. No new repository license is assigned.
- Ethics: no private records or harmful instructions are included. The report does not authorize hiding failed tests or deployment.
- AI use: Codex generated the work. Separate agent checks do not constitute human or peer review.

The checklist is not a claim of NeurIPS approval or submission compliance.

## Independent checks

The source agent checked related work and reading limits before the numerical report. The method agent wrote validate.py without importing analyze.py. Its results and proof review are in method_review.md and validation_results.json.

The main agent checked the figure visually and checked report table values against the saved CSV files. A separate final agent review must confirm a fresh reproduction and report support before publication. Its outcome is recorded in final_review.md.

## Release checks

Before publication, check all package file hashes, relative links, reference uses, copied-text risk, secrets, private information, license conflicts, and unsupported claims. Store the actual check outcomes in release_checks.json. Remote publication must be verified separately after upload.
