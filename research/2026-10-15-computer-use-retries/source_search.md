# Source search and contribution record

Date: 2026-10-15, America/Toronto.

Codex searched current sources before the study plan was saved. A separate Codex agent read the closest sources. The lead Codex agent also read the main source passages. This record states what was read. It does not imply that source code, raw data, or all paper claims were checked.

## Question fixed in the plan

How do action completion delay and read delay interact with computer-use retry rules? Does a truthful terminal failure signal improve safe completion and confirmation time over absence-based retries and a conservative fixed timeout?

The saved [plan](analysis_plan.md) defines one initial append action and at most one retry. An append action adds one durable item. A query returns historical item counts and attempt states with a stated read delay. A terminal drop means that the attempt failed and can never commit later. All admitted actions finish before final scoring, including actions that finish after the controller stops.

The main comparison has 256 constructed cases, four observation schedules, five rules, and two server modes. There are 10,240 main runs. Two separate stress suites break the execution bound or read-delay bound. The plan specifies no real browser or model test.

The plan was clarified before analysis. An observed count of one permits a completion claim. An observed count of two causes a detected-duplicate stop with no completion claim. This does not remove later effects from final scoring.

## Exact proposed contribution and its limits

The contribution is an original, bounded comparison of explicit retry rules, with a complete event record. It separates a current negative read from evidence that a prior write cannot still take effect. It measures final duplicate effects beside safe completion, unconfirmed outcomes, query calls, write calls, and time in model ticks.

RStackBench already separates visible success from persistent state and distinguishes delayed writes from tasks that need further action. This study instead combines pending append actions with delayed negative reads. It scores all later effects and uses matched server deduplication as a control. It does not copy the RStackBench task templates or code.

CUA-Speedrun already shows that faster observations can precede a UI update. CapLease, RIFL, and HTTP semantics already explain important retry and duplicate-effect limits. Thus, the study does not introduce verification, waiting, terminal status, idempotency, or exactly-once execution. Its formal cases are special cases of known systems reasoning.

This search does not establish that this is the first such comparison. Its result can support only the stated finite event model. It cannot show a measured improvement in an AI model, browser, or production service. Constructed-case fractions are not population failure rates.

## Search queries

All searches were made on 2026-10-15 with the web search tool. No date or domain filter was used. Only primary sources support the paper. Search results also included commercial posts, mirrors, social media, and issue discussions. Those results were not treated as scientific evidence.

The separate source agent used these exact queries:

1. `computer use agents asynchronous actions stale observations retry action verification benchmark paper`
2. `browser agents latency adaptive observation polling asynchronous environment paper`
3. `computer use agent action verification duplicate actions delayed feedback paper`
4. `"computer-use" "idempotent" paper`
5. `"browser agent" "duplicate" "retry" paper`
6. `"UI" "polling" "optimal" completion observation paper delay`
7. `"GUI" "duplicate actions" "agent" research`
8. `"agent" "action confirmation" "retry" arxiv`
9. `"computer use" "waiting" "benchmark" arxiv`
10. `"Implementing Linearizability at Large Scale and Low Latency" RIFL`
11. `"RStackBench"`
12. `"negative read" "retry" "pending" distributed systems`
13. `"fresh" "read" "pending write" "linearizability" retry`

The lead agent used these exact queries:

14. `computer use agents stale observation delayed confirmation retries idempotency browser benchmark`
15. `computer use agent adaptive observation action execution latency reliable retry 2026 paper`

The lead agent also supplied the RStackBench author page for direct inspection. The NeurIPS guide was opened directly for the publication review.

## Sources cited in the paper

Full author lists and bibliographic fields are in [references.bib](references.bib). All URLs below were read on 2026-10-15. Paper titles and technical names retain their source wording.

### CUA-Speedrun

- Key: `aggarwal2026cuaspeedrun`.
- Primary text: https://arxiv.org/html/2609.40284v1
- Version record: https://arxiv.org/abs/2609.40284v1
- Date and status: 2026-09-30, arXiv version 1, preprint.
- Read scope: abstract, Introduction, Sections 2.1-2.3, 3.1, 3.2, and 3.3. The lead agent also checked Sections 2.3 and 3.2. Appendices and raw trajectories were not audited.
- Supported use: fast input/output can return a screenshot before the interface changes. The paper reports a case where faster environment input/output increased agent interaction and total task time. This motivates controlled timing tests. It does not establish the results of our retry model.
- Rights: the arXiv page states CC BY 4.0. No text, figures, code, or data were copied into the study inputs.

### RStackBench

- Key: `calanza2026rstackbench`.
- Primary paper: https://exzilcalanza.info/wp-content/uploads/2026/08/rstackbench-browser-agent-reliability-preprint.pdf
- Author page: https://exzilcalanza.info/rstackbench-browser-agent-reliability/
- Date and status: August 2026, independent author preprint. The page is dated 2026-08-14. The PDF gives no numbered version. It does not claim external peer review.
- Read scope: abstract; Sections I-V; the results and interpretation of the pilot; Sections VII-X. The lead agent also read the author report. The reproduction archive was not run.
- Supported use: the study distinguishes visible success from persisted state. Its tests separate delayed writes from tasks that need another confirmation action. It tests fault layers separately and lists compound faults as future work.
- Rights: a redistribution license was not established. Only citation and short paraphrase are used. No task templates, figures, code, or data were reused.

### Beyond Single-Use Tokens

- Key: `xu2026caplease`.
- Primary text: https://arxiv.org/html/2608.01710v1
- Version record: https://arxiv.org/abs/2608.01710v1
- Date and status: 2026-08-03, arXiv version 1, preprint.
- Read scope: abstract; Introduction; Related Work; Problem Formulation; Transactional CapLease, including the proposition and proof sketch; Experimental Setup and results through Authority and Durable Consumption. The lead agent also read the formulation. Supplementary code and data were not run.
- Supported use: uncertain action outcomes can lead to repeated effects. The paper separates bounded admission from bounded effects and states the required idempotent-sink contract. This prevents a new-mechanism claim for a pending-action guard or duplicate suppression.
- Rights: arXiv perpetual non-exclusive license. Only citation and short paraphrase are used. No source text, figures, code, or data were reused.

### RIFL

- Key: `lee2015rifl`.
- Author-hosted paper: https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf
- DOI: https://doi.org/10.1145/2815400.2815416
- Date and status: SOSP 2015, October 4-7, 2015; conference paper.
- Read scope: abstract, Introduction, the architecture passages returned by the source, Section 9, and parts of Sections 8 and 10. The performance experiments and full implementation were not audited.
- Supported use: ambiguous retries and exactly-once execution are established systems problems. RIFL stores completion results for retries. Section 9 discusses browser failures, uncertain effects, and recognition of completed actions.
- Rights: the PDF permits stated personal or classroom uses and reserves other uses. Only citation and short paraphrase are used. The PDF, figures, code, and data are not redistributed.

### HTTP Semantics

- Key: `fielding2022http`.
- Primary text: https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2
- Date and status: June 2022; RFC 9110, Internet Standard STD 97.
- Read scope: source metadata, copyright notice, and Sections 9.2.1-9.2.2.
- Supported use: idempotence concerns the intended effect of repeated requests. Section 9.2.2 limits automatic retries for non-idempotent methods unless suitable semantics or evidence that the first request was not applied are available. A missing visible result is not itself this evidence.
- Rights: IETF Trust terms apply. Only citation and short paraphrase are used. No RFC text or code component is reproduced.

### NeurIPS Paper Checklist

- Key: `neuripschecklist`.
- Primary text: https://neurips.cc/public/guides/PaperChecklist
- Date and status: online guide, read 2026-10-15. No publication date is stated.
- Read scope: checklist guidance and items 1-16. These include claims, limits, assumptions, proofs, reproducibility, code and data, experimental detail, statistical reporting, compute, ethics, rights, human studies, and AI-use disclosure.
- Supported use: a review aid for the paper and its supporting files. Use does not imply NeurIPS approval, review, submission, or compliance.
- Rights: the checklist was read and applied. Its text is not republished. The study uses original review prose.

## Other primary work inspected during the search

These papers informed the search boundary. They are not part of the six-source paper bibliography. The stated read scope is narrower than a full-paper audit.

| Source | Date and status | Read scope | Relation to the question |
| --- | --- | --- | --- |
| [Learning to Wait](https://arxiv.org/html/2512.16262v1), She and colleagues | 2025-12-18; version 1 preprint | Abstract, Introduction, all Sections 2-4, and Limitations | Already studies chosen waits, check count, and delay in a simulated asynchronous setting. No claim that waiting or adaptive timing is new is justified. |
| [When Agent Context Goes Stale](https://arxiv.org/html/2610.05281v1), Liu, Fang, and Qian | 2026-10-04; version 1 preprint | Abstract, Introduction, Section 2, start of formal model, Sections 3.2-3.4 and 4.1-4.4, start of Related Work | Studies source-linked context repair. Read freshness and closure of a pending write remain distinct properties in our model. |
| [Desktop-Delta Bench](https://arxiv.org/abs/2607.26041v2), Pillai, Nayak, and Chen | 2026-07-29; version 2 preprint | Abstract, Introduction, contributions, and Related Work through the EvoGUI comparison in the linked PDF | Tests temporal ordering and action reconstruction. Our study does not test screenshot understanding. |
| [Step-level Optimization for Efficient Computer-use Agents](https://arxiv.org/html/2604.27151v1), Wei and colleagues | 2026-04-29; version 1 preprint | Abstract, Introduction, start of Related Work, and method passages on policy selection, recent history, stuck monitoring, and milestone monitoring | Shows prior work on selective stronger-model calls and sparse verification. Our policies do not use a learned monitor. |
| [On the Reliability of Computer Use Agents](https://arxiv.org/html/2604.17849v1), Gonzalez-Pumariega and colleagues | 2026-04-20; version 1 preprint | The lead agent read through Section 5. The source agent checked metadata and the returned main-text passages. | Background on repeated-run reliability. No source performance result is used as evidence for the retry model. |
| [AOSpec: Action and Observation Co-Speculation for Low-Latency Agent Serving](https://arxiv.org/html/2608.00881v1), Chen and colleagues | 2026-08-01; version 1 preprint | The lead agent read the Introduction and verification Sections 4.2-4.3. The source agent checked metadata and the returned abstract and Introduction. | Background on action and observation timing. Our study does not implement speculative execution or claim its latency gains. |

## Access problems and source limits

- Desktop-Delta Bench HTML versions 1 and 2 returned internal errors. Its arXiv abstract and linked PDF opened. The read scope above refers to the PDF.
- Two PDF link calls first used the wrong page-reference form and returned argument errors. Correct page references opened the PDFs.
- Local text extraction was used to read complete selected HTML sections. No source cache is included in this public package.
- The search was not exhaustive. It did not cover all conferences, proceedings, standards, patents, or repositories.
- No source experiment was reproduced. Source measurements remain attributed source findings, not results of this study.
- No outside code, data, screenshots, or model outputs were used as study inputs. No new license is assigned by this record.
