# Source and claim review

Date: 2026-10-24. Review by a separate Codex agent. No human review. The initial review checked the frozen question, source use, and required evidence. The final source review below checks the completed report and README. This is not an independent numerical audit or a publication receipt.

## Initial decision before the results

The frozen composition question is suitable as a bounded artifact study. The source search found direct prior work on the failure mechanisms and on mixed-rule safety. The report must credit that work. There is no basis to claim a new concurrency protocol or the first discovery of this failure.

The final plan has three caller rules, nine ordered pairs, and 576 scenarios per pair. The candidate with a separate last read was not selected. The search record now preserves both the earlier candidate history and the final choice. The plan was not changed by this review.

## Claim checks

| Proposed claim | Review boundary |
| --- | --- |
| Own-row CAS can leave a shared bound unprotected | This is an established cross-record condition. Cite Berenson et al.; report new observed counts only from the saved experiment. |
| One stronger caller need not protect a mixed pair | Existing mixed-isolation research and PostgreSQL application guidance already require joint reasoning. The new result is this exact caller matrix. |
| SharedEpoch can refuse a feasible job after irrelevant metadata changes | This mechanism overlaps with the October 17 repository report. Feasibility is defined by the frozen numeric contract; another contract may require that refusal. |
| AtomicSum preserves the limit in complete-rule pairs | Report the tested scope and full assumptions. The SQL check, allocation, and epoch update must commit together. |
| The experiment tests real SQLite operations | Valid only after the runtime, SQL log, and database evidence confirm this. An imposed schedule is not a natural race sample. |
| One rule is safe in general | Unsupported. Other writers, schema changes, external effects, crashes, refunds, and retries are outside the declared test. |

Every caller uses SQLite's same serialized writer mechanism. The report must not call the policy matrix mixed engine isolation levels. The unsafe application reads end before the later write transaction. This distinction prevents a false claim about SQLite isolation.

## Closest sources

The reference file includes direct URLs and reading limits. All sources used for technical claims are primary papers or official documentation. The report should cite the classical failure mechanism, the SQLite transaction contract, the recent budget boundary, and the mixed-rule literature. CoAgent and the PostgreSQL transaction-isolation page are optional if the report makes no separate claim that needs them. Remove uncited bibliography entries only after the report is final.

The recent budget paper explicitly requires complete mediation. The new experiment does not test that complete protocol. It also has no remote gateway, delegated credit, authenticated settlement, or external cost. A caller that omits the global condition is a selected rule in our own test, not evidence that the cited protocol fails.

No full source text, figure, table, or code was copied into the proposed experiment. Source URLs and short paraphrases preserve attribution. No new license is assigned to the repository owner's work. The cited PVLDB paper reports CC BY-NC-ND 4.0; linking and limited discussion do not republish its assets.

## Checklist items for the final reviewer

The current NeurIPS checklist was read as a review aid. It gives no approval to this study. Final checks must confirm:

- Claims match observed cases and stated assumptions.
- Limitations include selected schedules, one engine, and no agent performance estimate.
- Any general proof states its full assumptions.
- Code, inputs, exact commands, versions, and evidence permit repetition.
- All baselines, refusals, failures, and negative cases remain visible.
- Exact finite counts are explained without invented sampling intervals.
- Compute, storage, and failed-run costs are recorded.
- Rights, privacy, misuse, and artifact documentation are addressed.

There are no planned human participants or model releases. The report must still state actual AI use and review status. Results, reproduction, integrity, and publication checks remain the responsibility of the final review after execution.

## Final source review of the completed report

The reviewer read the completed `report.md`, `README.md`, and `references.bib` on 2026-10-24. No experiment was run for this review. No source or plan change was made.

**Outcome: source claims and bounded contribution pass.** No material source error was found. One small scope wording correction was sent to the lead: define a worker as a logical caller, not as an operating-system process. The method uses separate connections with scheduled events and does not establish a multiple-process experiment. This does not affect the source claims or reported counts.

- The report credits established write skew, mixed-rule analysis, and complete mediation. It limits the new contribution to the fixed test corpus and evidence.
- All nine numbered references have matching bibliography entries and direct primary-source URLs. Each is used in the text. No reference needs removal.
- The statements about SQLite match the checked official documentation. The report clearly says that the application read ends before the write transaction. It does not claim a SQLite isolation defect.
- The statement about PostgreSQL concerns documentation. The report explicitly says that PostgreSQL was not run.
- The current budget and CoAgent papers are labeled preprints. The report states that only selected sections were checked and that their protocols were not reproduced or refuted.
- The Vandevoort paper is used only for established joint analysis of mixed assignments. The report does not claim to test its method, performance, or full theory.
- The report distinguishes invented inputs, real local SQL execution, and prescribed schedules. It excludes production agent error rates and website results.
- Broad-revision refusal is credited as overlap with the earlier repository study. The numeric feasibility definition is clear.
- The rights section uses source links and limited paraphrases. It assigns no new license and makes no claim of source endorsement. No source asset is included in the report or README.
- Codex generation and separate AI review are explicit. No human review, external peer review, university affiliation, or certification is implied.
- NeurIPS is described only as a review aid. The report states the limits of that use.

The earlier source requirements are satisfied by the final text. The numerical comparison, runtime logs, privacy scan of the full package, and remote publication remain separate review steps. This source pass must not be reported as proof that those steps passed.
