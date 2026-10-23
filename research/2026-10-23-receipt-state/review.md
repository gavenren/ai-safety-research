# Publication review

Date: 2026-10-23. Status: local research checks passed. Remote publication must still be verified separately. This document does not itself prove an upload.

The relevant [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) items were used as a review aid. This is not NeurIPS approval, submission compliance, or certification.

| Check | Decision and evidence |
|---|---|
| Claims | Pass. The abstract and results match all six rows of `results/summary.csv`. History, read-time truth, reply-time truth, and effects are separate. |
| Novelty and prior work | Pass for a bounded artifact contribution. AWS, RIFL, HTTP guidance, two recent preprints, and earlier repository studies are acknowledged. No new algorithm or priority claim is made. |
| Plan and assumptions | Pass. The plan hash matches its pre-execution freeze. The two bits, permanent receipts, atomic actions, non-reused revisions, and single-operation authority are explicit. |
| Derivations | Pass. The 8/5 word partition gives the reported totals. The independent evaluator and final reviewer checked the counts. |
| Reproducibility | Pass. The README commands were executed. Nine deterministic files matched byte for byte. All 2,028 records, 14,716 trace events, and 192,566 scalar values passed independent comparison. |
| Full evidence | Pass. All 338 input histories and 2,028 outcomes are saved, with actions, claims, states, and scores. Unknown states and extra writes are retained. |
| Uncertainty | Pass. This is a complete finite corpus. It has no sampling confidence intervals or population risk claims. Symmetry is not counted as an independent sample. |
| Compute | Pass. Python 3.13.7 and standard library only. Main and independent CPU times are saved. No paid compute or new API charge was used. No model was trained or evaluated. |
| Scope and negative results | Pass. No production trial occurred. Matching reads can become stale. A current-state guarantee is not inferred from correct dated claims. |
| Ethics and human data | Pass. All data are synthetic. No human participants, private account records, or credentials are used. No human-subject approval is claimed. |
| Misuse | Pass. The report warns against treating a new version as repair authority. No harmful operational method is supplied. |
| Rights and text | Pass. Sources are paraphrased and linked. No source PDF, provider example, third-party code, or substantial copied text is distributed. No new license is assigned. |
| AI and review status | Pass. Codex roles are stated. Three separate AI review roles checked design/evaluation, sources, and final method. No human or peer review occurred. |
| Security and privacy | Pass. The selected release contains only study files and invented data. Pattern checks found no credential or private-account material. No raw connected-account logs are included. |
| References and links | Pass. Cited source passages were checked by the source reviewer. Relative report links resolve to selected files or existing repository reports. Unread search leads are not used as evidence. |

## Review resolution

`final_source_review.md` and `final_review.md` record separate reviews. The final wording now says R5 sent 130 conditional write requests. The README and this checklist were added after the first final review and checked separately. These changes do not affect the frozen plan or result files. `changes.md` retains the instrumentation and review history.

The report's language uses short direct statements and defines research terms. No formal ASD-STE100 certification or external language review is claimed.

Publication is authorized only to the selected repository. The publisher will compare the final remote tree with the selected file hashes, check the report and index at the immutable commit, and confirm that unrelated repository blobs remain unchanged. Only that later check can support a publication claim.
