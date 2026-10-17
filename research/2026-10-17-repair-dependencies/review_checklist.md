# Publication review checklist

Date: October 17, 2026. Result: PASS for local publication checks.

The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was read on this date. The relevant items below serve as a review aid. This is not a claim of conference approval or submission compliance.

| Check | Result and evidence |
| --- | --- |
| Claims and scope | PASS. The report states the exact question, current-value contract, six rules, finite corpus, and limits. No production rate or new algorithm is claimed. |
| Prior work and sources | PASS. Five primary sources support the claims. Three are preprints. The source record states versions, dates, read limits, and a blocked full-text lead. See source_claim_review.md. |
| Plan and assumptions | PASS. The plan and configuration were frozen before execution. Hashes match. The report states atomicity, complete dependencies, fresh reads, and revision assumptions. |
| Proofs | PASS. Separate review checked both safe-rule arguments and exact count identities. They apply only under the stated assumptions. See derivations.md and independent_review.md. |
| Reproduction and evidence | PASS. All three documented commands passed in a fresh folder. Ten generated files match byte for byte. Code, inputs, logs, raw traces, and environment records are included. |
| Controls and comparisons | PASS. All cases and weaker-rule successes remain. The independent program matches all 59,184 policy rows and 379,596 events. The report preserves prefix and unused-suffix limits. |
| Statistical uncertainty | Not applicable to these exact finite counts. There is no random sample or population inference. No confidence interval or statistical significance claim is made. |
| Compute and models | PASS. Local Python 3.13.7 and the standard library were used. No paid service was started. Exact immutable Codex build information was unavailable and is not invented. |
| Data leakage | No training or model evaluation occurred. The synthetic cases are public regression cases, not a held-out benchmark. |
| Limitations and negative results | PASS. Zero-error settings, denied writes, exhausted retries, source-access failure, and authoring errors are retained. No real account experiment is claimed. |
| Ethics, privacy, and security | PASS. Inputs are synthetic. The file scan found no private paths, email addresses, credential patterns, or account records. Examples support defensive tests. |
| Rights and copied text | PASS. Source review checked brief attributed paraphrases. No source paper text or external source code is redistributed. No new license is assigned. |
| AI and review status | PASS. Codex generation and agent roles are explicit. No human review, peer review, affiliation, endorsement, or certification is claimed. |
| Release files and references | PASS. Required files exist. Local links resolve against the package or the existing repository tree. Source links and metadata were checked by the source reviewer. |

The release receipt binds the local files by SHA-256. This local checklist does not prove publication. The task state records the later remote commit and byte checks. Existing repository files must be preserved, except for one new row in the research index.
