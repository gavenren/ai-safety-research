# Review before publication

Date: October 16, 2026. Status: required local checks passed. Remote publication needs a separate receipt after upload.

The review uses the relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), read on October 16, 2026. It is a review aid. It does not claim NeurIPS approval or submission compliance.

| Area | Result and evidence |
| --- | --- |
| Claims | PASS. Abstract and result table match exact counts. Both separate reviews checked scope. No new algorithm, natural failure rate, provider defect, or real-agent improvement is claimed. |
| Theory | PASS within assumptions. Full derivations give the state recurrence, count conservation, target-state bijection, two-field bound, complete guard, and partial guard distinction. Both reviewers checked the proofs. |
| Plan | PASS. Inputs were saved before calculation and their hashes still match. This was a local freeze, not external preregistration. The stronger summary check for H3 is recorded in failed_checks.md. |
| Reproduction | PASS. The four README commands exit zero in a fresh directory. All ten generated data files, the comparison receipt, and four frozen inputs match. See reproduction_check.json and reviewed_commands.json. |
| Independent check | PASS. A separate implementation matches all 108 policy rows, 13,744 terminal rows, 108 stages, and 71 minimum-write witnesses. Ten small settings also pass direct enumeration. |
| Tests | PASS. Eight main test methods; 28 independent malformed-input checks; 34,720 relabel checks. Negative settings remain in the data. |
| Uncertainty | Appropriate for the design. This is exhaustive integer counting, not a random sample. No confidence interval, p-value, or natural event probability is claimed. Model fit remains uncertain. |
| Compute | Local Python 3.14.7 and standard library. No paid compute, training, model inference experiment, or external account trial. There is no random seed because there is no random sampling. |
| Limits | Explicit binary-state, read, identity, revision, write-order, cache, and timing assumptions. Same recurrence in both implementations remains a shared modeling limit. |
| Prior work | Eight primary sources checked for the cited claims, with read scope and dates. StateAct is labeled as a preprint. No priority claim follows from the limited search. |
| Data and rights | Synthetic inputs. Source text and code are not redistributed. New text was checked for copied passages during source review. References preserve attribution. No license is assigned to the user's work. |
| Privacy and misuse | No account trial or private data in this package. A local scan found no home paths, account email addresses, token strings, or private keys. Content review found no actionable serious-harm instructions. A pattern scan alone cannot prove absence of every secret. |
| Links | Relative links checked against this package and the existing remote file tree. External citations were opened in source review. There is no promise that links will remain available. |
| AI and review | Codex roles and model-version limit are stated. Agent review is distinct from human and peer review. No affiliation or endorsement is claimed. |
| Publication | Authorized for the existing public repository. Main branch and all previous files must be checked after upload. A local PASS does not prove publication. |

The report and README hashes are in [final_report_review.md](final_report_review.md). Source and proof checks are in [source_claim_review.md](source_claim_review.md). The calculation review is in [independent_review.md](independent_review.md). All material review issues were resolved before this release check. The initial command failure and later wording corrections remain in [failed_checks.md](failed_checks.md).
