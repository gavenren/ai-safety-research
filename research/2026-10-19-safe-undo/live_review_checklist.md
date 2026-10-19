# Review aid for the production website extension

Date: 2026-10-19. Use of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) is a review aid. This is not a submission, conference approval or certification.

| Check | Finding and scope |
| --- | --- |
| Claims | Separate exact synthetic results from selected production cases. No claim of general model skill, natural failure rate, a provider defect or novelty priority. Final numeric check is recorded in live_release_check.json. |
| Limitations | State fixed later commands, two selected sites, shared account owner, prescribed rule execution, incomplete assignments, private evidence limits and non-atomic browser actions. |
| Assumptions | The target omits the agent action but holds later commands fixed. The two log-assisted controls receive stronger test-log inputs. Native provider history is not assumed. |
| Reproduction | Publish frozen inputs, rule code, saved synthetic fields, action extracts, helper versions, analysis code, commands and result checks. Public replay cannot recreate private account history. |
| Experimental detail | Record field encodings, identity checks, waits, assignment order, no-replacement rule, bounded corrections, cleanup and helper changes. Keep failed starts and corrected assertions. |
| Uncertainty | Give exact counts and denominators. No confidence interval or p-value is used because these selected dependent cases are not a population sample. |
| Compute | Existing browser tools and local Python/Node only. No training, purchased service or new paid model API call. Immutable model and browser product builds were not exposed. |
| Ethics and rights | Only user-authorized temporary data changes. No invitations, messages, access changes, payments or permanent deletion. No third-party code or dataset is copied. No new license is assigned. |
| Assets and privacy | Public extracts use record aliases. Keep account details, native private URLs, unrelated UI and full screenshots local. Record extraction and independent privacy checks. |
| Human subjects | No recruited participant, human behavior study or private human record analysis. Background edits are controlled test commands. This is not a claim of institutional ethics approval. |
| AI use and review | Codex generated the study, code and report. Browser agents executed the fixed rules. A separate agent checked evidence and analysis. No human or external peer review occurred. |
| Publication | Update the same dated paper and index. Verify the remote tree and file hashes after upload. A local pass or upload attempt alone is not publication proof. |

Final status: Local method, evidence, reproduction, privacy and claim checks pass within the stated limits. Five core assignments remain unknown. Calendar trial 23 can still have an unsaved browser form. This result does not establish complete browser cleanup. Remote publication must be checked separately against the saved files.
