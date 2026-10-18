# Publication review checklist

Date: October 18, 2026. Status: PASS for local publication checks.

The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was read on this date. The relevant items below are a review aid. This is not conference approval or a claim of submission compliance.

| Check | Finding and evidence |
| --- | --- |
| Claims | The report separates finite model results, conditional proofs, and interpretation. A receipt is distinguished from a hypothetical exact-count claim. |
| Prior work | Six primary references were checked. Current preprints and limited reading are identified. Established finite-retention problems are attributed. No first-discovery claim is made. |
| Plan | The plan and configuration were frozen before implementation. Their hashes match. No frozen input changed. |
| Method and proofs | Atomic handling, exact expiry, stable identity, time origin, transport, and stop behavior are explicit. Source and independent proof checks passed. |
| Reproduction | All three README commands passed in a fresh folder. Ten generated data files match byte for byte. Code, inputs, full traces, logs, and environment records are included. |
| Separate review | The independent tick-loop program matches all 130,921 runs, 575,415 events, 427 aggregate rows, 427 paired rows, and 356 minimum examples. |
| Controls | Boundary, all-drop, immediate-success, reordered-arrival, same-tick, and correct-bound controls pass. Main tests include 22 malformed configurations. Independent checks include 34 malformed configurations and 1,029 extra bound-control runs. |
| Uncertainty | The finite counts are exact. No random sample, population inference, confidence interval, or statistical significance claim is made. Unused input multiplicity is stated. |
| Limits | No live website, account, provider, or model test is claimed. Stronger receiver capabilities and the lost completion opportunities are explicit. Main and broken-bound stress results remain separate. |
| Compute | Python 3.13.7 and the standard library were used locally. No new paid service was started. The immutable Codex model build was unavailable and is not invented. |
| Data and leakage | Inputs are synthetic. No training or model scoring occurs. This is a public regression corpus, not a held-out benchmark. |
| Ethics and privacy | Records contain no user account data. Release scanning includes decompressed traces. No credential pattern, email address, or private filesystem path was found. |
| Rights | Source review checked short attributed paraphrases. No full source papers or external source code are included. No new license is assigned. |
| AI use and review | Codex generation and separate agent roles are stated. No human review, peer review, affiliation, endorsement, or certification is claimed. |
| Failures | Authoring path errors, comparison-adapter error, and text corrections are retained. No result-dependent case removal occurred. |
| Files and links | Required files are present. Relative links resolve against this package or the existing repository tree. Source claims and reference metadata passed review. |

The release receipt binds the local file versions. It is not proof of publication. The task state records the later remote commit and checks of all package files and the root index. Earlier repository files must remain unchanged except for one new index row.
