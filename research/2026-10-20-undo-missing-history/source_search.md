# Source search: undo with an incomplete action log

Search and access date: 2026-10-20 (America/Toronto).
Scope: focused primary-source search for the proposed daily study. No model or numerical experiment was run by this source reviewer. No source text or data is redistributed.

## Result of the search

The proposed rule is an application of established reasoning with incomplete information. A safe target must agree across all compatible histories. This is not a new general algorithm. A useful contribution can be a complete, executable regression set for the prior paper's exact undo target, with a comparison of trusted exact and upper loss counts, observed command order, and current fields. The report must state that this is a finite model. A limited search cannot establish global novelty.

The source reviewer read the abstract, question, related work and model in the local October 19 paper. That paper removes one agent increment and replays fixed later commands. Its complete-history rule can be defeated by a false completeness flag. Today's question must retain that target definition and distinguish a true information bound from an unverified claim about missing commands.

## Search terms

1. `incomplete event logs possible worlds process mining uncertain event logs`
2. `semantic undo compensation incomplete history transaction counterfactual`
3. `certain answers incomplete databases possible worlds all worlds query`
4. `"incomplete" "event logs" "missing events" conformance checking uncertain`
5. `"undo" "partial knowledge" "history" transactions`
6. `"compensation" "possible worlds" database`
7. `"D’Iddio" "incomplete" conformance`
8. `"Managing and Anticipating Out-of-Order Events"`
9. `"runtime verification" "missing events" "sound"`
10. `"Monitoring with uncertainty" "2012"`
11. `"runtime verification" "lossy" "sound"`
12. `"Uncertainty in runtime verification" Taleb Hallé Khoury pdf`
13. `"agent" "undo" "incomplete" "history" 2026 research`
14. `"compensation" "partial observation" "agent"`
15. `"selective undo" "incomplete" log`

## Primary sources checked

### 1. Closest method: monitors with missing events

Peeyush Kushwaha, Rahul Purandare and Matthew B. Dwyer. *Optimal Runtime Verification of Finite State Properties over Lossy Event Streams*. arXiv:2004.04214v1, submitted 2020-04-08. This checked version is a preprint; a later publication status was not established.

- Metadata: https://arxiv.org/abs/2004.04214
- Read text: https://arxiv.org/html/2004.04214v1
- Read scope: abstract; Sections 1 and 2; Section 3 definitions; Section 4 through Definition 10. No experimental result is reused.
- Bounded attribution: The paper represents a lost-event observation by its possible full executions. It includes loss with retained counts and silent drops. Its monitor tracks possible states and makes definite violation claims only under the specified conditions on those states.
- Relation: This directly precedes the proposed all-compatible-histories test. Our output is an exact undo target, rather than a Boolean property verdict. Our small enumeration uses a global missing-command count or upper bound and current fields.
- Limit: Do not reuse the paper's labels for soundness and completeness without definitions. Its formal definitions are tied to violation monitoring. Do not claim that our enumeration improves its algorithms or bounds.

### 2. Missing-event repair and the subsequence relation

Jianmin Wang, Shaoxu Song, Xiaochen Zhu and Xuemin Lin. *Efficient Recovery of Missing Events*. Proceedings of the VLDB Endowment, 6(10), 841–852, 2013.

- Author-hosted paper: https://sxsong.github.io/doc/13vldb.pdf
- Read scope: abstract; Introduction; Section 2 including Definition 6 and Problem 1; Section 3 opening through Lemma 2. Publication metadata was checked on the PDF first page. No performance result is reused.
- Bounded attribution: A recovered event sequence must contain the observed sequence as a subsequence and meet a process specification. Several recoveries can fit one observation. The paper seeks minimum-change recovery and top-k candidates.
- Relation: Our command-subsequence constraint is established. Our decision retains all compatible histories within a trusted bound; it must not treat one shortest or likely reconstruction as established truth.
- Limit: The paper studies Petri-net process constraints. We do not reproduce its general algorithm or claim its computational-complexity result for our smaller model.

### 3. Certain answers over possible worlds

Giovanni Amendola and Leonid Libkin. *Explainable Certain Answers*. IJCAI 2018, 1683–1690. DOI: 10.24963/ijcai.2018/233.

- Proceedings: https://www.ijcai.org/proceedings/2018/233
- Paper: https://www.ijcai.org/proceedings/2018/0233.pdf
- Read scope: abstract; Introduction; Section 2 opening, including possible-world semantics and query answers. The paper's later proofs were not reviewed.
- Bounded attribution: Incomplete data can denote several complete worlds. Query answering can identify information that is common to all of them. The paper distinguishes intersection-based answers from more general information-based answers.
- Relation: Agreement of every possible undo target is a simple certain-answer test. We do not claim that possible-world reasoning or unanimous-target selection is new.

### 4. Compensation and the counterfactual target

Henry F. Korth, Eliezer Levy and Abraham Silberschatz. *A Formal Approach to Recovery by Compensating Transactions*. VLDB 1990, 95–106.

- Paper: https://www.vldb.org/conf/1990/P095.PDF
- Read scope: abstract; Sections 1 and 2; Section 3.1 opening on transactions, programs and hypothetical executions.
- Bounded attribution: The paper studies semantic compensation after other transactions have used an earlier result. It compares compensation with an execution that omits the canceled transaction. It also shows why later program behavior matters.
- Relation: Our target deliberately keeps later commands fixed. It is narrower than changing the original program execution. Incomplete logs do not remove this limit.

### 5. Explicit uncertainty in event logs

Marco Pegoraro and Wil M. P. van der Aalst. *Mining Uncertain Event Data in Process Mining*. ICPM 2019, 89–96; checked author version arXiv:1910.00089v4, updated 2022-04-08. Initial arXiv submission 2019-09-20. DOI listed by arXiv: 10.1109/ICPM.2019.00023.

- Metadata: https://arxiv.org/abs/1910.00089
- Read text: https://arxiv.org/html/1910.00089v4
- Read scope: abstract; opening discussion and related work; event uncertainty categories; Definitions 7 and 9 for realizations.
- Bounded attribution: The paper represents explicitly uncertain logs through realizations and studies best- and worst-case conformance. Its indeterminate-event case concerns recorded events that may not have occurred. It distinguishes this from unmarked missing data.
- Relation: This supports keeping uncertainty explicit. It is adjacent to, but not identical to, our omission model. Do not describe its indeterminate events as missing commands in our sense.

### 6. Current operational guidance

Microsoft. *Compensating Transaction pattern*. Page last updated 2026-04-20.

- URL: https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
- Read scope: Context and problem; Solution; Problems and considerations; When to use this pattern.
- Bounded attribution: Returning to old values can overwrite later work. Compensation requires application-specific information and can itself fail. The system must keep the information needed for compensation.
- Relation: This is operational context, not a new theorem or a benchmark baseline.

### 7. Current agent recovery context

Mahesh Balakrishnan and coauthors. *LogAct: Enabling Agentic Reliability via Shared Logs*. arXiv:2604.07988v1, 2026-04-09. Preprint.

- URL: https://arxiv.org/html/2604.07988v1
- Read scope: abstract; Introduction paragraphs on semantic recovery and its limits; Section 3.1 paragraphs on concurrency and external changes; Section 3.2 executor recovery. No benchmark result is reused.
- Bounded attribution: LogAct puts agent actions in a shared log and uses recovery components. The authors state that semantic recovery by inference does not give an unconditional clean-state guarantee. They also discuss external writers and conditional or locked operations.
- Relation: Our bounded-log test is a small rule study. It neither reproduces nor refutes LogAct. A current field read is not a lock or an atomic check-and-write.

## Checked leads not used for research claims

- *Runtime Verification of LTL on Lossy Traces*, Yogi Joshi, Guy Tchamgoue and Sebastian Fischmeister (SAC 2017), DOI 10.1145/3019612.3019827. University primary metadata and abstract were read at https://uwaterloo.ca/embedded-software-group/references/runtime-verification-ltl-lossy-traces . No full-text result is cited.
- *Uncertainty in runtime verification: A survey*, Rania Taleb, Sylvain Hallé and Raphaël Khoury (2023). Search results helped find primary papers. The survey was not used as primary evidence.
- *Toward Uncertainty-Aware and Structure-Sensitive Repair of Missing ...* (2026 Scitepress lead): https://www.scitepress.org/publishedPapers/2026/152303/pdf/index.html returned an internal tool error. It was not read and is not cited as evidence.
- *Evidence-Guided Recovery for AI Agents with Ambiguous Tool Outcomes and Partial Execution*, SSRN lead 7609459: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7609459 and its delivery PDF both returned internal tool errors. Search text suggests adjacent work, but full text was not checked. Do not use its numerical claims or treat absence of access as evidence of novelty.
- https://github.com/evoundo/evoundo was opened as a current software lead. No implementation or test was reviewed. It is not used to support a claim.
- Commercial commentary, a DEV post, Wikipedia, and search summaries were used only as search leads. They are not cited as technical evidence.

## Recommended contribution statement

This study applies established compatible-history reasoning to a fixed-command undo model. It supplies an exact regression artifact for omitted commands, trusted loss bounds, current-state filtering, and refusal decisions. It measures the extra correct completions available under these assumptions. It does not introduce possible-world reasoning, semantic compensation, or a new general recovery algorithm.

## Assumptions to make explicit before testing

- An observed log is an ordered subsequence of the actual log, with no inserted or altered commands.
- A count bound must include all missing commands in scope. It is not inferred merely from a visible edit count or a short log.
- The operation alphabet, initial record and original agent operation are correct.
- Current fields are accurate and belong to the same record.
- At least one compatible history must exist. An empty candidate set is inconsistent evidence, not unanimous agreement.
- If all compatible targets agree, that target is sound only when the actual history belongs to the candidate set.
- New writes after the state read require a separate concurrency safeguard. This study must not imply that two browser reads create one.
- Preserve candidate-set size and distinct-target count. Agreement on one target can occur while several histories remain possible.
