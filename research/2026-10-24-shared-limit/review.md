# Final separate review

Date: 2026-10-24. Reviewer: a separate Codex agent. This is AI review. It is not human review or peer review.

## Decision

Pass for the stated local experiment and bounded report claims. No material error remains in the reviewed method, code, evidence, or report. Final package checks and verified remote publication remain separate duties. This review does not confirm that an upload occurred.

The reviewer read the final report, reproduction README, plans and correction record, code, source review, summaries, trace evidence, database, freezes, and comparison records. The reviewer did not run a third complete SQL experiment. Additional work used read-only database queries, saved-trace analysis, hash comparisons, text checks, and primary-source reads.

Two wording issues were corrected before this pass. The report now calls a worker a logical caller. It also distinguishes row-version and epoch-accounting checks from guard decisions, which can correctly refuse a write.

## Method and evidence

The reviewed plan hash matches the final freeze. The initial plan and freeze also match. The metadata-scope correction occurred before implementation and execution. The preserved correction is necessary because a SharedEpoch refusal can change the other worker's later input. No case was removed after a result.

Each worker read uses one complete SELECT. The cursor is consumed and closed before the later write. Each attempted write uses BEGIN IMMEDIATE. The guard, allocation update, and epoch update share that transaction. The current aggregate check uses the selected case ID. All other reads and writes also use that ID. Prescribed event order is clear. The report does not claim uncontrolled parallel execution or a defect in SQLite isolation.

Read-only database inspection confirmed 5,184 unique quota rows, 10,368 allocation rows, no orphan allocation rows, and an integrity result of `ok`. All 5,184 traces have distinct case IDs and valid zero initial states. Across 25,056 recorded events, allocation versions and epoch counts were consistent. The saved code hash matches the code used for the run.

The stale same-row CAS and retained-snapshot controls exercise real SQLite behavior. The expected snapshot error is code 517. The rollback control uses allocation and epoch fields in one control row. It does not by itself test a two-table rollback. Main-code inspection separately confirms that the allocation and quota changes share one transaction. The report now states this control boundary correctly.

The independent evaluator was frozen before main-code or result access. Its hash remains unchanged. The later adapter reads the evidence format but imports only that evaluator. The saved comparison passed for all 5,184 cases, 10,368 worker decisions, 350,784 event-state values, 72,576 read values, 62,208 score values, and 137,132 logged SQL statements. It also checked the logical dump and all physical quota and allocation rows. The comparison passed on the second full run and on the database extracted from the saved compressed file.

All nine table rows, the adverse example `c00060`, the three algebraic breach counts, and the paired metadata statements match the saved evidence. Across the nine pairs there are 6,902 accepted jobs, 3,466 refusals, 330 breach cases, and 1,000 feasible refusals. Seven deterministic output files match across the two completed runs. The report correctly explains why final excess equals maximum excess and why breach and bad-admission counts coincide in this monotone two-job model.

## Checklist review aid

The current [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was read and used as an aid. This is not a formal submission checklist, approval, or certification.

| Area | Review result |
| --- | --- |
| Claims and contribution | Counts and scope match the evidence. The new contribution is the exact corpus and artifact. No new general protocol or priority claim is made. |
| Assumptions and argument | The bound argument states writer participation and epoch conditions. It does not cover hidden writers, external effects, retries, crashes, or changing capacity. |
| Reproduction | Code, inputs, commands, environment, database evidence, trace logs, controls, and both run records are available. No third main run was needed for review. |
| Statistics | The finite corpus is exhaustive for its stated inputs. No sampling interval or significance claim is invented. Paired controls reuse each no-U case five times. |
| Resources | Recorded main-run CPU times are 2.55068 and 2.815194 seconds. Wall times are 3.303924 and 3.708462 seconds. Both are below the saved limits. The runner has no model API call or network call. These times are not a performance comparison. |
| Limitations | One engine/version and selected schedules are stated. No production website, AI-action selection, deployment safety, portability, fairness, or eventual-completion result is claimed. |
| Ethics and rights | Records are invented. Sources are attributed through links and short paraphrases. No source implementation, figure, or paper is redistributed. No new license is assigned. |
| Disclosure | Codex generation and separate AI review are explicit. No human review, peer review, affiliation, or endorsement is claimed. |

## Sources and publication boundary

The final reviewer checked the cited write-skew and sum examples in Berenson et al.; the abstract and introduction of Vandevoort et al.; SQLite isolation and transaction documentation; PostgreSQL application-consistency guidance; the complete-mediation assumption in Zhu and Wang; and the declared read/write scope in CoAgent. These primary sources support the limited related-work statements. The fuller search and reading scope is preserved in `source_search.md` and `source_review.md`. Recent preprints are identified. Their systems were not reproduced or refuted.

A local text scan found no credential markers or private account identifiers in the reviewed text assets. Trace and database fields contain only invented case data. No extended copied source passage was found in the report. This is a review check, not a guarantee of complete plagiarism detection.

The lead must exclude Python cache files, SQLite WAL/SHM sidecars, and unrelated workspace files; check the final file manifest and relative links; preserve the repository history; and verify the remote commit after upload. This pass applies to the reviewed report and evidence. It does not establish production behavior or remote publication.

## Reviewed file hashes

```text
report.md: 1a501cc0b56b2c5824cf8247b1a47a287f468a26df3ebbc967c62ac62cbcb4a4
README.md: 5efb90a537519b93d14cf18ba5c2b6d5347a62f5de1fd708ea318f6fda3574ce
run_study.py: fceb57819ff174beff21f60617f2c9d237177c9182052f546c333575001fef94
independent_check.py: 50538bb607624eb2d56cd9440a97419adf294f4a70e7222f6c685848792cd8ff
compare_independent.py: 1ffbef834bb89af005a9557b2cc6980def1c41e82cfc316c74f58b7afe315c32
```
