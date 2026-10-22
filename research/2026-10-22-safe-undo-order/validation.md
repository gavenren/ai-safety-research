# Validation record

Status: Author checks and separate agent review passed. No material error was found. The main agent must complete final package checks and verify remote publication.

## Executed evidence

The plan was saved before implementation. The code hash was saved before execution. Two complete runs used unchanged code. All five deterministic output files match byte for byte. Each run contains 1,152 primary and 27 smaller-state rule cases. No case is unknown, replaced, or excluded. All declared graph, field-renaming, and hand-control checks passed. The post-run count derivation matches the recorded summary.

The graph oracle uses a separate algorithm but was written by the same study agent. It must not be described as an independently authored evaluator. No human review occurred.

## NeurIPS review aid

- Claims: The report states exact finite counts and limits them to the declared model.
- Limitations: The report lists complete knowledge, static constraints, one-way actions, and excluded real-world behavior.
- Theory: The count derivation and the one-bit/two-bit argument state their assumptions and reasoning.
- Reproduction: Standard-library source, all inputs, raw traces, configurations, hashes, commands, and two execution receipts are supplied.
- Uncertainty: This is exhaustive enumeration, so no population estimate or confidence interval is reported.
- Compute: Both runs stayed within the frozen local resource limits. No model API or paid compute was used.
- Ethics and rights: Data are synthetic. Primary sources are paraphrased and linked. No new license, source artifact, personal record, secret, or harmful service instruction is included.
- AI use: Codex's roles and the absence of human review are stated.

The checklist is a review aid. It does not establish NeurIPS approval, submission compliance, or certification.

## Completed separate review

A separate Codex agent checked the code, report, analytic derivation, and original technical sources. Its own evaluator uses sets of field names and a bottom-up reachability calculation. It matched all 1,179 saved rule cases, 4,042 trace states, and 6,963 name transformations. All group totals, report table cells, witnesses, frozen hashes, and five deterministic reproduction hashes passed. See [separate_review.md](separate_review.md), [separate_audit.py](separate_audit.py), and [separate_audit.json](separate_audit.json).

The reviewer read the main implementation before writing its evaluator, so the review was not blind. No third full experiment run occurred. No human review or external peer review occurred. After review, only review-status wording was changed; no model, code, input, or result correction was needed.
