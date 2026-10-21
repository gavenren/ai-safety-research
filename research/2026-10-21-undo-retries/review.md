# Review and release checks

Run date: 2026-10-21. No human review or external peer review occurred.

## Method and numerical checks

- The plan, configuration, and search record hashes match the pre-execution freeze.
- Main run: 2,924 cases and 20,468 outcomes. Twelve hand-checked controls passed. All six frozen hypotheses held within their declared test sets.
- Separate implementation: nine hand controls, 29,240 inverse-field identities, and 2,924 atomic-inverse case checks passed. It was written from the frozen plan before reading main code or results. All 20,468 rows and all 429,828 field values matched. Its file hash did not change. See independent_review.md and independent_comparison.json.
- Evidence checks: 328,076 trace events, all result rows, 42 summary rows, 35 paired rows, 14 witnesses, and 70 numeric result-table cells passed the documented consistency checks. These trace checks are not an independent replay of every transition.
- Clean reproduction: all three README commands passed in a separate copied folder. Eight deterministic result files matched byte for byte. Timing and resource metadata are intentionally variable. See reproduction.json and validation.json.

The first main experiment used 2.447712 CPU seconds. Its clean repeat used 2.141434 CPU seconds. The model and review scripts took seconds, below the ten-minute model CPU gate. The receipts record individual runs. Source search, agent writing, and browser publication time are outside that model execution measure. No paid compute, GPU, or model API call was part of the experiment. The surrounding Codex work used AI agents, as disclosed in the report.

## Source and novelty checks

A separate source agent read the primary passages listed in source_search.md. The main agent also read the RIFL atomic-record and repeated-assignment passages, the Microsoft pattern, the UndoBench fault taxonomy, and the NeurIPS checklist. The sources support established mechanisms and context. No external benchmark number was used. Read scopes and unsuccessful access attempts are retained. UndoBench and other preprint leads are identified as preprints.

Additional main-agent search terms on 2026-10-21:

- `site.learn.microsoft.com compensating transaction pattern idempotent commands resume failed compensation`
- `site.aws.amazon.com builders library making retries safe idempotent APIs atomic recording token mutation`
- `agent undo compensation crash recovery idempotent 2026 paper`
- `site.neurips.cc/public/guides/PaperChecklist claims reproducibility limitations code ethics`

No first-method, first-failure, first-benchmark, or general protocol novelty claim is made. The contribution is the declared finite corpus and comparison. A limited search does not establish global novelty.

## NeurIPS checklist review aid

The official guide at https://nips.cc/public/guides/PaperChecklist was read on 2026-10-21. The first neurips.cc request failed. This review does not claim submission compliance, approval, or certification.

| Relevant item | Finding |
| --- | --- |
| Claims and limitations | Claims are bounded to the finite additive model. Server atomicity and final fault-free recovery are explicit. |
| Assumptions and derivation | The integer-state identity and atomic-inverse invariant are given with assumptions. No general browser proof is claimed. |
| Reproduction and code | Code, synthetic inputs, full traces, exact commands, versions, and output checks are included. |
| Experiment settings | Plan and configuration precede execution. No post-result model change or selected seed is used. |
| Uncertainty | No sampling interval is supplied for full enumeration. Population generalization is unsupported. Padding multiplicity is disclosed. |
| Compute | Main and repeat resources are recorded. The experiment uses the Python standard library and no model calls. |
| Ethical issues and harm | Only synthetic records are used. A deployment guarantee would exceed the evidence. No human-subject study is claimed. |
| Rights and new assets | Sources are cited; their files and code are not redistributed. The owner has not selected a reuse license, and this study adds none. |
| AI use | Codex roles and lack of human or peer review are explicit. |

## Release status

Separate content review, local release checks, and remote publication verification are recorded in their respective files and task state. A local package is not proof of publication. The final remote receipt is saved in task state after upload, to avoid a file that must contain its own future commit hash.
