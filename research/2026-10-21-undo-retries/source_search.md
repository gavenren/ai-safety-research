# Source and scope review: undo retries

Review date: 2026-10-21, America/Toronto.
Reviewer: a separate Codex source agent. No human review.
Status: question review before the model plan and experiment. No model experiment was run for this source review.

## Recommended question

How does the position of a durable progress record affect a two-step undo after a crash or lost reply? How does an unrelated edit during recovery change the safety of retrying a fixed assignment?

A **durable record** survives the modelled crash. An **effect** is a saved data change. A **receipt** records that an effect completed. An **atomic step** saves its effect and receipt together, with no state in which only one is saved. These terms require exact definitions in the analysis plan.

The useful contribution is a small, complete regression corpus. It can compare progress-record placement, inverse commands, fixed assignments, conservative refusal, and an ideal atomic control on the same declared fault cases. Report final state, actual effects, completion claims, refusal, and work costs separately. The general methods and failure modes are established. Do not call this a new exactly-once protocol or a new theory of compensation.

## Difference from this repository

The October 18 report, `outputs/2026-10-18-retry-retention/report.md`, tests request-memory expiry and requests still in transit. Its receiver effect and key record are atomic. It excludes process crashes and other writers. The report was read in full.

The October 19 report, `outputs/2026-10-19-safe-undo-improved/report.md`, tests one undo target after later commands and selected browser checks. Its synthetic method runs one atomic undo. It excludes crashes and retries. Its browser extension checks saved fields and action-history limits. The abstract, related work, method, production-extension method and result passages, discussion, and limitations were read. Source and result text was also searched for crash, retry, atomic, history, and receipt.

The October 20 report, `outputs/2026-10-20-undo-missing-history/report.md`, tests target selection with missing action records. Its method assumes an atomic correct write and excludes lost replies, retries, and external writes during undo. The abstract, question, related work, and complete method were read. Later result and limitation passages were searched for the relevant scope terms. It does not test the completion of a previously selected multi-step undo target.

The proposed study can isolate interrupted execution of compensation, after a valid target has been selected. It must state how later edits change that target. Do not mix the cost of a conservative refusal with an incorrect completion claim.

## Primary sources checked

### 1. Microsoft compensation guidance

- Title: *Compensating Transaction pattern*.
- URL: https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
- Author: Microsoft Azure Architecture Center.
- Page update shown: 2026-04-20. Retrieved 2026-10-21.
- Type: official architecture documentation, not a research experiment.
- Read scope: Context and problem; Solution; Problems and considerations; When to use this pattern. The page footer supplied the update date.
- Checked support: compensation can fail, so a system must retain progress and enough information to resume. Steps must be safe to repeat. Old-state restoration can remove concurrent work. Compensation is application-specific and may require manual recovery.
- Use: motivation and established design requirements. This source does not validate the new model or any browser implementation.

### 2. AWS retry guidance

- Title: *Making retries safe with idempotent APIs*.
- Author: Malcolm Featonby.
- URL: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- PDF: https://d1.awsstatic.com/builderslibrary/pdfs/making-retries-safe-with-idempotent-apis-malcolm-featonby.pdf
- Date: the PDF search result shows copyright 2020; the current page did not show a publication date. Retrieved 2026-10-21.
- Type: official engineering guidance.
- Read scope: introduction, Retrying and side effects, Reducing client complexity, and the opening of Retries and semantic equivalence. The atomicity passage was reopened directly.
- Checked support: recording the request identity and all mutations must be one ACID operation. Recording identity without the effect, or applying an effect without the identity, leaves different failure states. Retried requests also need an appropriate response meaning.
- Use: direct prior support for both marker-order failures. Do not claim that a client-local record makes a remote write atomic.

### 3. RIFL

- Title: *Implementing Linearizability at Large Scale and Low Latency*.
- Authors: Collin Lee, Seo Jin Park, Ankita Kejriwal, Satoshi Matsushita, John Ousterhout.
- Venue: SOSP 2015.
- URL: https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf
- Retrieved 2026-10-21.
- Type: published systems research paper.
- Read scope: abstract, Section 2, Section 3 opening, Section 4.1 completion-record and retry passages. The Section 6.2 version-check passage was returned by the atomicity search and read. Other implementation details and experimental results were not checked or reproduced.
- Checked support: Figure 2 shows a write that commits before a crash, another client's intervening write, and a retry that repeats the old assignment. Thus a repeatable assignment can still violate concurrent behavior. Section 4.1 requires the operation effect and completion record to become durable atomically before reply. A retry uses the same identity.
- Use: this is the closest established system mechanism for the atomic effect-plus-receipt control and the fixed-assignment concurrency example. The finite study is not an implementation, improvement, or refutation of RIFL.

### 4. UndoBench

- Title: *UndoBench: Separating Task Competence from Recovery Capability in Tool-Using AI Agents*.
- Authors: Dolly Sah, Tanmay Sah, Harshul Jain, Tanya Sah.
- Version: arXiv:2610.05622v1, 2026-10-04.
- Abstract URL: https://arxiv.org/abs/2610.05622
- Checked text: https://arxiv.org/html/2610.05622v1
- Retrieved 2026-10-21.
- Type: preprint. Peer review was not verified.
- Read scope: abstract; introduction; Sections 2.1–2.4; opening of Section 3; Section 5; Section 6; opening of Section 7. Code and data were not executed or audited.
- Checked support: the fault taxonomy includes both a crash after reply but before checkpoint, and a fault during compensation. It separates invocations, saved mutations, and semantic effects. The displayed experiments focus on pre-mutation, partial-mutation, and post-mutation/pre-reply faults.
- Use: the closest current agent-evaluation work. Its taxonomy already covers the proposed failure family. The new artifact differs by exhaustive fixed-controller tests of progress-record placement within an undo. Do not claim that paired evaluation, effect-history grading, or compensation-fault tests are new. Do not import its numerical results as evidence for this study.

### 5. Cordon

- Title: *Cordon: Semantic Transactions for Tool-Using LLM Agents*.
- Authors: Zheng Chen, Hanqing Liu, Duling Xu, Dong Dong, Jialin Li, Bangzheng Pu, Jidong Zhai.
- Version: arXiv:2606.17573v1, 2026-06-16.
- Abstract URL: https://arxiv.org/abs/2606.17573
- Checked text: https://arxiv.org/html/2606.17573v1
- Retrieved 2026-10-21.
- Type: preprint. The HTML includes 2027 conference metadata; acceptance was not independently verified.
- Read scope: abstract, introduction, Sections 2.1–2.3, and Sections 4.3–4.6. No code or benchmark replication.
- Checked support: Cordon separates local promotion from external release. Its recovery protocol records manifests, receipts, and release states. Partial execution evidence can require manual review. Uncertain external dispatch does not receive unconditional retry.
- Use: current agent-runtime context for conservative recovery. Do not imply that a local durable log controls an unrelated provider's atomicity.

### 6. ARIES, limited read

- Title: *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging*.
- Authors: C. Mohan, Don Haderle, Bruce Lindsay, Hamid Pirahesh, Peter Schwarz.
- Venue: ACM Transactions on Database Systems 17(1), March 1992, pp. 94–162.
- Original paper copy: https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F19/handouts/papers/Aries.pdf
- Retrieved 2026-10-21.
- Read scope: abstract and opening Section 1.1, through the write-ahead-log protocol on printed page 97. The later detailed recovery procedure was not read.
- Checked support: the abstract already describes logging rollback work and chaining records to bound repeated recovery work. This is older precedent for durable undo progress. The proposed model is not ARIES.
- Access limits: the F21 course copy timed out. A later request for more text from the F19 copy returned HTTP 401. Keep the citation within the checked opening material or omit it.

## Additional primary artifact lead

The author README at https://github.com/ShreyAC962/saga-chaos-lab/blob/master/README.md was read on 2026-10-21. It describes a small crash-at-step-boundary harness, a compensation record in the same transaction as its effect, and concurrent recovery tests. Its displayed source has an MIT license. The code and run receipts were not checked, so its claimed results are not adopted. This lead further limits any first-artifact claim. No code or text was copied into this study. A primary paper and official documentation are sufficient for the main related-work section.

## Search record

All searches below used web search on 2026-10-21. Search snippets were used to locate sources, not as experimental evidence.

1. `compensating transaction pattern idempotent resume point failure concurrent changes site:learn.microsoft.com`
2. `Making retries safe idempotent APIs atomicity recording token mutation AWS builders library`
3. `RIFL exactly once semantics durable completion record side effects SOSP 2015`
4. `"AI agents" "compensation" "idempotent" recovery paper`
5. `"durable" "receipt" "agent" "retry" Cordon CapLease`
6. `"saga" "compensation" "idempotence" "crash" paper`
7. `"UndoBench" "Separating Task Competence"`
8. `"UndoBench" arxiv`
9. `"Cordon" "external" agent arxiv compensation`
10. `"CapLease" arxiv`
11. `"compensation" "marker" "crash" idempotency experiment`
12. `"Sagas" Garcia Molina Salem 1987 pdf compensation log failures`
13. `"ARIES" "compensation log records" "undo" IBM paper`

CapLease, arXiv:2608.01710, was found through abstract metadata. Its full text was not reopened for this review. Sagas metadata was found, but its original paper was not read in this review. These are leads, not checked support for detailed claims. Non-primary blog summaries and search-generated paper summaries were not used as factual support.

## Design cautions before the plan is saved

1. A progress record written before an effect is an intent record, not proof of completion. If the baseline deliberately treats it as done, state that choice.
2. A record written after an effect has an uncertain interval. A client-local record does not remove that interval.
3. A repeatable assignment can overwrite a later writer. RIFL already demonstrates this. Fix the later-writer schedule and evaluator target before enumeration.
4. Use a declared read boundary for a completion claim. A receipt proves the identified effect occurred; it need not prove that current fields still equal an old target.
5. Define the intended property for a multi-step undo. Per-step exactly-once execution does not imply all-or-nothing visibility across both fields.
6. If the atomic control has server support that other rules lack, label the stronger capability. Do not present this as equal-information agent reasoning performance.
7. Retain refusals and unresolved states. Do not count them as task success. Count a correct state without a claim separately if the metric needs it.
8. State the finite limits and whether faults can happen during the recovery attempt. One recovery with no further fault is a useful narrow test, but not proof for unbounded crashes.
9. This limited search does not establish global novelty.

## Review of the narrowed candidate

The parent proposed two fields that each receive one completed agent increment. Later edits add or subtract one from either field. The undo attempts to remove both agent increments. Each attempt has two declared slots per field, with explicit padding for an atomic rule. One or two crashes can stop an attempt at a declared slot cut. A final attempt has no fault. This was a design review only; it produced no experimental result.

This narrower design can isolate progress-record placement. Freeze the target as the initial state plus all scheduled background additions. Fix each assignment baseline's saved desired values before execution. The additive external commands commute with inverse subtraction; this removes the assignment/provenance ambiguity in the October 19 study. A result for this command set does not justify subtraction after an arbitrary later assignment.

Treat equal slot numbers as matched abstract intervention points. They are not equal elapsed time or equal instruction counts. Padding can give an atomic rule repeated observations with the same state; retain and disclose that multiplicity. Do not interpret assigned case fractions as crash probabilities. An external edit after the fourth slot must still occur and remain in the final audit. The final recovery without a fault is an assumption, not proof for unlimited crashes.

For the conservative no-resume rule, define persistent refusal explicitly. All declared background edits must still occur after refusal. A later recovery attempt must not silently revive a refused task. This gives every rule the same external edit schedule.
