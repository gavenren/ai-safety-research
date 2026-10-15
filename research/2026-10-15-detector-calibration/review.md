# Review record

Date: 2026-10-15. These are Codex checks. No human or external peer review occurred.

## NeurIPS checklist as a review aid

- Claims: the report presents a synthetic probability audit. It claims no new method or empirical AI safety result.
- Assumptions and proof: independent controls and targets, correct labels, fixed rates, sensitivity transfer, one batch, and fixed policy are explicit. The derivations give the binomial limit, unconditional guarantee, and cap rule.
- Reproduction: the saved plan, inputs, hashes, full-precision brackets, policy branches, raw results, code, environments, and commands are included.
- Uncertainty: probabilities are deterministic model sums. Numerical error checks are separate from model uncertainty. No sampling interval or significance claim is used.
- Controls: the independent method review uses different root and integer calculations, exact small cases, endpoint cases, false-positive cases, monotonicity, cap inclusion, and workload checks.
- Limits: poor sensitivity transfer, noisy labels, dependence, drift, repeated testing, real cost, practical efficiency, and a full power curve are outside the study. Skipped batches are explicit.
- Compute: local CPU only. No model experiment, training, paid API call, paid compute, or installation occurred.
- Rights and ethics: no source asset or private record is redistributed. Attribution and reading limits are preserved. No new license is assigned. No harmful instructions are included.
- AI use: Codex generated the work. Separate agent review does not establish human or peer review.

The checklist does not establish NeurIPS approval or submission compliance.

## Completed method review

The separate method agent passed all bounds, policy branches, grid rows, summary ties, and planned-example values. See method_review.md and validation_results.json. The input and plan hashes are unchanged.

The main agent checked the figure visually. Its first version clipped a workload point; this was repaired and recorded in failed_checks.md. A separate final agent must reproduce the output files and confirm report support before publication. See final_review.md for the actual outcome.

## Release checks

Before publication, check package hashes, links, claim support, private information, secrets, copied-text risk, and licenses. Record outcomes in release_checks.json. Remote publication needs a separate file check after upload. A local file or attempted commit is not publication proof.
