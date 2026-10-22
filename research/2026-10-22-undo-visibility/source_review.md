# Source and design review: undo visibility

Date: 2026-10-22, America/Toronto.
Scope: primary-source search and design review before selection of the final question.
No experiment was run. No account data was changed. The proposed corpus below is not a frozen plan.

## Decision

The proposed gap is distinct from the repository's October 21 experiment. That experiment measures final fields and exactly-once undo steps. It explicitly does not establish simultaneous visibility of those steps.

The underlying isolation problem is established work. Do not present unsafe intermediate reads, a durable gate, safe ordering, or a whole-record atomic write as new inventions. Atomix v2 is especially close. It distinguishes provider visibility from the view supplied to readers that use its runtime.

A useful limited contribution is an exact regression corpus. It can classify when an undo order preserves a declared state condition, when a local next-step check stops unnecessarily, and when a gate protects only the readers that use it. Save small witnesses and report final correctness separately from intermediate-state and observation correctness.

## Repository overlap check

Read the full October 17 report and targeted method, contribution, and limitation sections of the October 19 improved report and October 21 report.

- `outputs/2026-10-17-repair-dependencies/report.md`: one forward repair effect after a read/plan gap; version checks and dependency guards. It does not test visibility between several undo effects.
- `outputs/2026-10-19-safe-undo-improved/report.md`: remove an old effect while preserving later fixed commands; one atomic synthetic undo. It excludes intermediate-read branches, copied values, external effects, and multi-record constraints. Its live extensions concern target evidence and saved-field confirmation.
- `outputs/2026-10-21-undo-retries/report.md`: two-field undo with crashes and progress-record rules. It excludes application constraints and irreversible effects. Its proof establishes final additive state, not simultaneous visibility.

## Primary sources read

All access dates below are 2026-10-22. Read scope is explicit. None of the source programs or measurements was independently reproduced. No source text or code needs to be copied into the study.

### 1. Sagas

- Authors: Hector Garcia-Molina and Kenneth Salem.
- Publication: 1987; ACM SIGMOD Record 16(3), pages 249–259. The publisher record shows 1 December 1987. The Princeton technical report is January 1987; do not mix its page count with the published paper.
- Publisher page: https://sigmodrecord.org/1987/12/09/sagas/
- Primary PDF: https://sigmodrecord.org/?download_id=11106&smd_process_download=1
- Publisher DOI shown: https://doi.org/10.1145/38714.38742
- Read: Section 1, especially published page 250; Section 9, pages 257–258. The PDF has OCR errors, but these passages are readable.
- Use: the paper allows other transactions to see partial work. Later compensation does not notify or abort those readers. It also requires each subtransaction to preserve database consistency. Section 9 explains a transfer with missing funds and adds stored funds-in-transit data so an audit can remain valid.
- Limit: a model that permits invalid partial states tests a weak implementation or a different observation contract. It does not refute correctly designed Sagas. The paper already discusses data-layout changes that make safe subdivision possible.
- Rights: publisher copyright. Cite and paraphrase; do not republish the PDF.

### 2. Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows

- Authors: Bardia Mohammadi, Nearchos Potamitis, Lars Klein, Akhil Arora, Laurent Bindschaedler.
- Version: arXiv:2602.14849v2, revised 29 May 2026; first submission 16 February 2026. Treat the accessed arXiv copy as a preprint.
- Metadata: https://arxiv.org/abs/2602.14849
- Full text: https://arxiv.org/html/2602.14849v2
- Read: abstract; Sections 2.1–2.5; Section 3.3; Section 4; Appendix B.3; selected Appendix C.2 tables and their notes.
- Use: Section 2.4 explicitly separates provider visibility and runtime-mediated visibility. Eager reversible effects are visible outside the runtime before settlement. Compensation cannot erase that past observation. Readers inside the runtime obtain stronger ordering under its scope and frontier contracts. Section 4 states that complete adapter mediation and correct metadata are required.
- Limit: do not label the proposed toy gate as an Atomix implementation. Its richer runtime already tests isolation, side effects, scope errors, and partial commits. Do not claim a new discovery about gates or compensation. The paper has separate bounds for multiple irreversible effects and distributed deployment.
- Rights: cite the source; no source code or figures are reused.

### 3. Saga distributed transactions pattern

- Author: Microsoft, Azure Architecture Center.
- Accessed title: Saga distributed transactions pattern. No publication date was exposed in the fetched text.
- Current URL: https://learn.microsoft.com/en-us/azure/architecture/patterns/saga
- Old URL redirects to it: https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga
- Read: Context and problem; Solution; Problems and considerations; Potential data anomalies; Strategies to address data anomalies; When to use.
- Use: the guide explicitly states the lack of built-in isolation across services. It describes incomplete-step reads, application-level locks, commutative updates, ordering changes, re-reads, and version histories.
- Limit: this is provider design guidance. It is not evidence that a browser or a connected provider exposes a suitable lock. Each proposed guard must be defined in the model.
- Access note: a generic authorization banner was shown, but the substantive article text was returned in full.

### 4. Managing data consistency in a microservice architecture using Sagas — part 1

- Author: Chris Richardson.
- Date: 9 July 2019, from the dated primary URL and search metadata.
- URL: https://microservices.io/post/microservices/2019/07/09/developing-sagas-part-1.html
- Read: all substantive sections through the semantic-lock example.
- Use: the application uses a pending state to block a conflicting cancellation while an order is being created. This is a direct example of an application-level lock.
- Limit: the check protects operations that follow the pending-state rule. It does not establish all-or-nothing visibility for arbitrary external readers.
- Rights: site copyright; no code or diagram reused.

### 5. Coordination Avoidance in Database Systems

- Authors: Peter Bailis, Alan Fekete, Michael J. Franklin, Ali Ghodsi, Joseph M. Hellerstein, Ion Stoica.
- Publication: Proceedings of the VLDB Endowment 8(3), pages 185–196, 2014. The paper was invited for presentation at VLDB 2015. Use 2014 for this article.
- DOI: https://doi.org/10.14778/2735508.2735509
- Primary PDF: https://www.vldb.org/pvldb/vol8/p185-bailis.pdf
- Read: abstract and introduction; Sections 3 and 4.1–4.2, including the definitions of valid states, convergence, and invariant confluence.
- Use: safety depends on both operations and declared valid-state conditions. Convergence alone does not establish that all intermediate states are valid. The work gives a criterion for coordination-free execution in a stated replicated-database model.
- Limit: the proposed sequential undo graph has no replica merge or network partition. It is not a new invariant-confluence result and should not apply that theorem outside its assumptions.
- Rights: CC BY-NC-ND 3.0. Cite and paraphrase; no PDF or figure copied.

### 6. UndoBench: Separating Task Competence from Recovery Capability in Tool-Using AI Agents

- Authors: Dolly Sah, Tanmay Sah, Harshul Jain, Tanya Sah.
- Version: arXiv:2610.05622v1, submitted 4 October 2026; preprint.
- Metadata: https://arxiv.org/abs/2610.05622
- Full text: https://arxiv.org/html/2610.05622v1
- Read: abstract; introduction; Sections 2.1–2.4; failure-boundary and environment limits in Section 6.
- Use: the benchmark already separates final environment conditions from effect history. It distinguishes physical invocations, committed mutations, and semantic effects. Its taxonomy includes faults during compensation.
- Limit: the report says its evaluated boundaries do not include compensation faults. Do not reuse its numerical results. A fixed-controller state graph is not a language-model recovery benchmark, nor a new proposal to evaluate side effects.
- Rights: arXiv metadata links a Creative Commons license. No text, data, or code copied.

### 7. Agentic Transaction: Towards ACID-Compliant Agent Systems

- Authors: Zhaoyan Sun, Xiaoxiao Wang, Guoliang Li.
- Version: arXiv:2608.13900v1, 14 August 2026; preprint.
- Metadata: https://arxiv.org/abs/2608.13900
- Full text: https://arxiv.org/html/2608.13900v1
- Read: abstract; introduction; Sections 2.1–2.2.4; Section 4. Experiment text was displayed, but its measurements are not used.
- Use: the paper explicitly treats semantic atomicity, isolation, and durability as different obligations. It describes staged workspace updates and isolation of failed attempts.
- Limit: the proposed study should not claim that separating recovery from isolation is new to agent systems. It does not test this data-agent implementation.
- Rights: arXiv non-exclusive distribution license. No content is redistributed.

### 8. The Escrow Transactional Method

- Author: Patrick E. O'Neil.
- Publication: ACM Transactions on Database Systems 11(4), pages 405–430, December 1986.
- Primary author-hosted PDF: https://www.cs.umb.edu/~poneil/EscrowTM.pdf
- DOI: https://doi.org/10.1145/7239.7265
- Read: abstract; Sections 1.1–1.4; start of Section 2.1 through the recovery-mode example.
- Use: recovery and concurrency are separate concerns. Escrow establishes conditions that remain valid under permitted subsets and orders of outstanding updates, with explicit resource and journal support.
- Limit: a Boolean visibility gate is not escrow. Escrow is a useful related design family if a later experiment reserves bounded resources. No claim about the full implementation or proof is needed here.
- Rights: ACM copyright. No PDF or code is redistributed.

## Search record

Search tool: public web search. Date: 2026-10-22. The following strings were submitted. Result snippets were leads. Supporting claims use the primary sources read above.

1. `Garcia Molina Salem Sagas 1987 transactions isolation compensation pdf`
2. `Bailis Fekete Franklin Ghodsi Hellerstein Stoica coordination avoidance database systems invariant confluence 2014 pdf`
3. `saga semantic lock compensation countermeasures anomaly primary source`
4. `site.cs.princeton.edu "Sagas" Garcia Molina Salem pdf`
5. `site.cs.cornell.edu "Sagas" pdf`
6. `site.vldb.org "Coordination Avoidance in Database Systems"`
7. `site.microservices.io saga semantic lock lack isolation`
8. `"Sagas" "Garcia-Molina" "pdf" -"studocu" -"reddit"`
9. `"agent" "compensation" "isolation" "2026" paper`
10. `"UndoBench" "recovery" "side effects"`
11. `"semantic lock" "saga" site:microservices.io/post`
12. `Atomix "progress-aware" "frontier" agent paper`
13. `"UeRbEpSVUz" Atomix`
14. `site.sigmodrecord.org "sagas.pdf"`
15. `site.arxiv.org "Stop Means Stop" enforcement gap`
16. `O Neil 1986 escrow transactional method original pdf`
17. `compensation invariant safe ordering undo partial visibility exhaustive model checking`

The search is limited. It does not establish global novelty or priority.

## Access failures and excluded leads

- Princeton technical-report page, https://www.cs.princeton.edu/research/techreps/598: direct access returned HTTP 403. Search metadata was visible. The publisher PDF above was then read.
- Cornell Sagas mirror, https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf: timeout through the web tool. The publisher PDF was available.
- OpenReview Atomix PDF, https://openreview.net/attachment?id=UeRbEpSVUz&name=pdf: verification page. The current arXiv v2 was available and read instead.
- An initial click on the Sagas PDF link failed because the web tool could not resolve the supplied reference. A later click using the returned page reference succeeded. This was a tool-reference error, not a source failure.
- Stop Means Stop, https://arxiv.org/abs/2607.14166: search metadata and abstract only. It is a close lead for gate completeness and cancellation. Do not cite its detailed implementation, proofs, or numerical results from this review.
- Robust Agent Compensation, arXiv:2605.03409: a search lead only. No primary full-text reading was completed. Exclude it as supporting evidence.
- Secondary summaries, web forums, thesis summaries, and general reference pages were not used as technical evidence.

## Proposed finite contribution

The cleanest small question is: given a complete valid-state condition, when can fixed-order, local-guard, and full-path undo controllers finish without exposing an invalid state?

Use three Boolean fields. Start at `111`; the undo target is `000`. Each ordinary undo step clears one field once. The valid-state condition must include both endpoints. The other six states can be valid or invalid independently. This gives 64 declared conditions by design. This is corpus arithmetic, not a measured result.

Possible comparison rules:

1. Fixed order: clear fields in a preset order; ignore the condition until final audit.
2. Greedy guarded order: choose the first remaining field whose immediate result is valid. Stop if none is safe.
3. Complete safe-order search: search all field orders before execution. If a full valid path exists, use the first such path; otherwise refuse before any write.
4. Durable read gate: close a gate before any change, use fixed-order undo, and open it only after the complete target is verified.
5. Early-open gate: same rule but open the gate after an incomplete prefix, as a deliberate fault.
6. Whole-record atomic control: replace all three fields at once.

The first three compare planning under the same single-field write capability. The last three have different enforcement capabilities. Do not rank all six as equal-capability AI methods.

Three fields make a useful distinction possible: a locally valid step can lead to a state with no safe remaining step, although another complete order exists. A complete path check can identify this before mutation. Save the smallest such witness if it exists in the planned corpus. Do not assert its frequency before enumeration.

Observe after each atomic state transition. Define two observation modes: a reader that checks the gate and a reader that bypasses it. The gate can return `blocked`, not a fabricated value. Keep these separate measures:

- Final fields equal the undo target.
- The internal record ever leaves the valid-state set.
- A returned read is invalid.
- A read is blocked.
- Undo stops without the target.
- A completion claim is made despite an invalid returned read, if that is part of the declared completion contract.

A gate does not make hidden invalid storage valid. It only limits disclosure to readers that follow it. If an internal integrity constraint must hold at every transition, the gate is not a solution. Also, do not call a visible intermediate state a harmful side effect unless the model supplies an action that consumes it. A read-only audit has a narrower observation error.

Optional delayed recovery or crash-prefix experiments can test whether gate state survives restart. They must be frozen before execution. Avoid adding both crashes and arbitrary external writers in the first version: that would make target semantics and rule comparisons harder to interpret.

Use canonical endpoint orientation for the main corpus. Field renaming and bit complement can be symmetry checks. Do not count them as independent real tasks. Retain valid-state conditions with no safe path; refusal is expected there. Report exact counts, not failure probabilities, confidence intervals, or inferred website risk.

## Claims that would be supportable

After execution and validation, the report may claim a specific reproducible finite corpus, exact classification, differences between prescribed controllers, and small counterexamples. It may say that the corpus tests an explicit assumption excluded from the October 21 study.

It should not claim a new isolation algorithm, a new general impossibility theorem, a result about arbitrary services, a refutation of Sagas or Atomix, or measured language-model improvement. No source search can by itself prove that the finite artifact is the first of its kind.
