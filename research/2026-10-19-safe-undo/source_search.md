# Source review: undo after later edits

Date: 2026-10-19, America/Toronto.

This is a source and design review. No experiment was run for this review. Codex performed the search and wrote these notes. No human review occurred.

## Proposed question

For one completed agent change and a fixed sequence of later commands, which undo rules reach the state that the later commands would produce without the agent change? When does a value check permit a wrong undo? What useful outcomes does a revision check reject?

An undo rule is an operation that attempts to remove an earlier effect. A counterfactual target is the result of a specified alternative execution. Here, the alternative omits one agent increment but keeps each later command and its order fixed. This is a narrow mathematical target. It is not an estimate of how people or agents would behave if the earlier action had not occurred.

The proposed new artifact is the exact six-rule regression corpus, its refusal accounting, and its smallest failing examples. Compensation, operation inverses, history-based correction, and preserving later work are established ideas. This search does not establish that the corpus is the first such corpus.

## Search record

All searches and source reads below occurred on 2026-10-19. The web search service was used. Search queries were:

1. `saga compensating transactions concurrent updates undo compensation semantic lock original paper`
2. `AI agents compensating transactions rollback concurrent edits undo arxiv 2026`
3. `Sagas Garcia Molina Salem 1987 pdf Stanford`
4. `A Formal Approach to Recovery by Compensating Transactions Korth Levy Silberschatz pdf 1990`
5. `Planarian Managing Agent State with Statepoints 2609.35366 arxiv`
6. `"sagas" "garcia-molina" pdf compensating 1987 stanford`
7. `site.arxiv.org "SagaLLM"`
8. `site.arxiv.org "LogAct"`

The first two queries identified the compensation literature and current agent work before the experiment plan was fixed. Later queries resolved source metadata and read scope. Detailed source reads and metadata checks continued after the plan was fixed. They did not change the experiment inputs. Secondary summaries and social posts were search leads only. Their claims are not evidence for the study.

## Closest primary sources

### 1. Formal compensation and later effects

Henry F. Korth, Eliezer Levy, and Abraham Silberschatz. *A Formal Approach to Recovery by Compensating Transactions*. Proceedings of the 16th VLDB Conference, 1990, pages 95–106.

Original proceedings PDF: <https://www.vldb.org/conf/1990/P095.PDF>.

Read scope: abstract; Sections 1–2; Section 3.1; the operation commutation definition in Section 3; Sections 4.1–4.2; Section 5.1 through its definition and explanation; Section 6 opening discussion and fixed-program definition. The full paper was not read.

Applicable claims: Section 2 distinguishes semantic compensation from restoration of old data. Section 4.2 defines a correctness comparison with a history that omits the canceled transaction. Its Theorem 1 gives a sufficient condition based on commuting operations, under the paper's constraints. Section 5.1 already specifies compensation by which transactions updated each entity. Section 6 explains why changes in later program behavior complicate the comparison.

Use: this is the closest formal precedent for the study target and history-aware control. Cite it directly. The six-rule comparison does not introduce that target or the provenance principle. The planned fixed commands deliberately exclude state-dependent control flow. No theorem from this source is claimed to cover arbitrary agent behavior.

Rights: link and paraphrase only. Do not republish the source PDF or copy its proofs.

### 2. Current provider guidance

Microsoft. *Compensating Transaction pattern*. Azure Architecture Center. Page update date: 2026-04-20.

<https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction>

Read scope: full substantive page from Context and problem through Example, including Problems and considerations and When to use this pattern. The access notice did not block the article text.

Applicable claims: restoring an old state can overwrite concurrent work. Compensation must account for later changes and application rules. It need not reproduce the original state. Recovery steps can themselves fail, so the page recommends progress records and repeat-safe steps.

Use: practical motivation for the wrong-undo risk. The proposed study models one atomic undo only. It does not test recovery retries, multistep orchestration, or the Azure implementation.

Rights: brief attributed paraphrase only. No copied diagram or code.

### 3. Current agent state recovery

Jinnan Guo, Hao (Mark) Chen, Kapil Vaswani, Andrew Paverd, and Peter Pietzuch. *Planarian: Managing Agent State with Statepoints*. arXiv:2609.35366v1. Submitted 2026-09-28. Preprint.

<https://arxiv.org/html/2609.35366v1>

Metadata: <https://arxiv.org/abs/2609.35366>

Read scope: abstract; Sections 1, 2.3, 3.1, 4.3–4.4, 6.1–6.3; Section 7.1 setup. Also read parts of Sections 4.1–4.2 and 4.5 during adjacent page extraction. Evaluation results were not audited.

Applicable claims: the remote proxy makes supported SQL calls compensable by recording prior row data and affected keys inside one transaction. It records undo actions and applies them in reverse request order. Proxy locks serialize its requests. The consistency discussion states a tenant-isolation assumption and coordinates sandbox activity around recovery.

Use: close agent-recovery context. The proposed corpus studies additional later writers under an explicit record contract. It is not a test of Planarian's implementation and does not refute its conditional consistency claim. Do not quote its speed or task-quality numbers as results of this study.

Rights: source states CC BY 4.0. Cite authors and version; no source text or code is copied.

### 4. Agent action logs and semantic recovery

Mahesh Balakrishnan, Ashwin Bharambe, Davide Testuggine, David Geraghty, David Mao, Vidhya Venkat, Ilya Mironov, Rithesh Baradi, Gayathri Aiyer, and Victoria Dudin. *LogAct: Enabling Agentic Reliability via Shared Logs*. arXiv:2604.07988v1, 2026-04-09. Preprint.

<https://arxiv.org/html/2604.07988v1>

Read scope: abstract; Sections 1–2; Section 3 introduction and Section 3.1; Section 3.2 opening paragraphs. No benchmark audit or implementation test.

Applicable claims: LogAct records intended actions before execution and uses logged history for recovery. Its introduction describes exploratory checks and compensating actions. It explicitly limits guarantees for LLM-based semantic recovery. Section 3.1 starts from exclusive execution, then discusses external actions and the need for operation logic that correctly controls concurrent changes.

Use: motivates separating a recovery record from proof that an undo is correct. The present fixed rules test one small effect model. They do not reproduce or compare LogAct agents or its voter system.

Rights: arXiv perpetual non-exclusive license. Link and short paraphrase only.

### 5. Multi-agent dependency records

Edward Y. Chang and Longling Geng. *SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning*. arXiv:2503.11951v3, 2025-07-09. Preprint version used here.

<https://arxiv.org/html/2503.11951v3>

Metadata: <https://arxiv.org/abs/2503.11951>

Read scope: Section 3.1.2; Section 3.2; Section 3.3; Sections 4.3.1–4.3.3 from the primary HTML. The v1 compensation discussion was read first, then v3 was checked. No empirical claims are used.

Applicable claims: the framework records operation and dependency information for compensation planning. Its recovery process uses logs and stored compensation specifications. The use of operation history for agent undo therefore predates this study.

Use: related work only. The six-rule corpus is not an implementation or test of SagaLLM. Do not infer general ACID guarantees from the title or reuse its empirical claims.

Rights: link and brief attributed paraphrase only. No implementation copied.

### 6. Removal of incorrect LLM transactions

Jinghan Zeng, Eugene Wu, and Sanjay Krishnan. *A Simple and Fast Way to Handle Semantic Errors in Transactions*. arXiv:2412.12493v1, 2024-12-17. Preprint.

<https://arxiv.org/html/2412.12493v1>

Metadata: <https://arxiv.org/abs/2412.12493>

Read scope: abstract, Sections 1 and 2 through the consistency and recoverability definitions. This source was a lead from query 2. Its detailed read occurred after the plan was fixed. No model change resulted.

Applicable claims: the work studies later removal of transactions generated by LLMs. It uses transaction dependencies and buffering to preserve database constraints. Its introduction distinguishes preservation of constraints from exact equality of database states.

Use: direct prior work on agent undo. Our target is exact equality under fixed commands, and our model has no database constraint. It does not reproduce this middleware or compare its performance. No source benchmark results are used.

Rights: CC BY-NC-SA 4.0. Only a brief attributed summary is used. No source text, code, or data is copied.

### 7. Review aid

NeurIPS. *NeurIPS Paper Checklist Guidelines*. Current page accessed 2026-10-19. No page publication date was stated in the read text.

<https://neurips.cc/public/guides/PaperChecklist>

Read scope: introduction and checklist items 1–15. The relevant items cover claims, limitations, theory assumptions and proofs, reproducibility, code and data, experimental details, uncertainty, resources, ethics, impacts, safeguards, licenses, and new assets.

Use: a review aid for this package. This is not a claim of NeurIPS approval or submission compliance. Exact finite enumeration does not estimate a natural failure rate, so sampling error bars are not appropriate. The package must explain that scope.

## Historical lead with partial access

Hector Garcia-Molina and Kenneth Salem. *Sagas*, 1987. The original Princeton technical report is dated 1987-01-07: <https://www.cs.princeton.edu/techreports/1987/070.pdf>. ACM proceedings DOI: <https://doi.org/10.1145/38713.38742>.

Read scope: original-report abstract in the search result and publisher search metadata only. Direct Princeton PDF fetch returned HTTP 403. Direct ACM PDF and article fetches failed. The source was not treated as fully read. The abstract supports only the general saga structure: smaller transactions can interleave with other work, and compensating actions amend partial execution. Use the fully read relevant Korth sections for the detailed theory.

## Relationship to the frozen study

The study uses the exact inputs in analysis_plan.md. It adds an observation test: histories with the same initial state, length, current state, and target revision can require different correct final states. Such a pair limits what a rule with only those inputs can decide. This is a direct mathematical consequence of equal inputs and different required outputs. It is not a new general information theory theorem.

The proposed new work is the fully enumerated corpus, paired refusal costs, complete traces, and smallest failing examples under the declared order. The comparison omits one increment while fixing later commands. It does not model changed human choices or conditional branches. The operation-type history control is an ideal control, not a claim that website interfaces expose the required history. A limited search does not prove that this artifact is globally novel.

## Access and metadata corrections

The preliminary work note had an incorrect SagaLLM author first name; primary arXiv metadata corrected it to Longling Geng before release. Attempts to open unlisted v4 URLs for SagaLLM and the semantic-errors paper failed; verified versions v3 and v1 are used. The Sagas full-text access failure is retained above. No claim depends on unread full text. No source benchmark was rerun.
