# Publication review

Date: 2026-10-19. Use with release_check.json and the independent review files. A local pass does not establish remote publication.

The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was used as a review aid. This is not NeurIPS approval or a claim of submission compliance.

| Item | Evidence and limit |
| --- | --- |
| Claims | The abstract and planned main table use exact saved counts. Simulation, fixed commands and unequal information are explicit. No production rate, model result or priority claim is made. |
| Theory | derivations.md and independent_review.md state assumptions and conditional proofs. The information limit applies only to the stated observations. |
| Plan | analysis_plan.md and config.json were frozen before implementation. The manifest hashes are checked by both programs and the release check. |
| Reproduction | All four README commands pass in a clean directory. Ten result files match byte for byte. See reproduction_check.json. |
| Independent check | A separate implementation was complete before main-code access. Comparison checks every case, trajectory, outcome, main aggregate, main pair, observation group and witness. Schema differences are recorded. |
| Statistics | Complete finite enumeration uses exact integers. There is no random sample, confidence interval, p-value or claim about a natural population. |
| Controls | No-background, single-command, independent-field, same-value-write and operation-composition controls pass. Closed-form count identities and input-rejection tests pass. |
| Sources | source_search.md gives primary URLs, queries, dates, read scopes and metadata corrections. Preprints are identified. source_claim_review.md checks use and limits. |
| Failures | failed_checks.md records the wrong test-count assertion, report count correction, tool setup issues and schema differences. No frozen input changed. |
| Data and rights | The data and programs were made for this study. No external code, source PDF, private account data or real personal record is included. No new license is assigned. |
| Ethics | The model does not authorize real rollback or supply harmful access steps. Scope and misuse limits are explicit. |
| Compute | Local Python standard library. No new paid service or paid API compute. Exact immutable Codex build unavailable and disclosed. |
| Disclosure | Codex generation and agent roles are stated. No human review, peer review, endorsement, certification or affiliation is claimed. |
| Content | Short attributed source paraphrases; no copied source blocks, diagrams or data. The release scan checks private local paths, contact details, secret patterns and decoded trace text. |
| Links and index | Local links resolve against the new package and the checked prior remote tree. One new index row preserves the prior README bytes. |
| Publication | Publish only after all checks pass. Then fetch the commit and recursive tree. Compare every package Git blob and index with local bytes, and confirm prior files are unchanged. Keep this receipt outside the published package. |

No unresolved scientific or content error is known at release. The report does not claim to satisfy every professional standard or conference rule. Future work can test other command semantics and real interfaces under separate plans.
