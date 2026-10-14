# Source search and reading record

Date: 2026-10-14. Main tool: web search and source-page reading. A separate Codex agent checked sources. The full private working note is not needed to repeat the numerical analysis. This record states the sources used and the reading limits.

## Search terms

The main agent searched:
- AI safety evaluations repeated testing optional stopping sequential risk certification 2026
- zero failures consecutive successes reliability demonstration testing stopping rule run length
- site.arxiv.org 2026 "safety" "anytime-valid"
- site.arxiv.org "AI" "optional stopping" evaluation
- site.projecteuclid.org time-uniform nonparametric nonasymptotic confidence sequences Howard 2021

The source agent searched:
- AI safety evaluation optional stopping repeated testing confidence sequences
- exact distribution waiting time consecutive successes Bernoulli runs Markov chain
- zero failures reliability demonstration testing repeated testing stopping rule
- "AI" "safety" "confidence sequences" evaluation
- "Time-uniform, nonparametric, nonasymptotic confidence sequences" Howard
- "Some conservative stopping rules for the operational testing"
- "safety evaluation" "optional stopping" AI
- "AI" "rolling window" "safety" evaluation statistics
- "sequential" "AI safety" evaluation statistical tests 2026

Search results were used to locate original papers. Secondary sites and search snippets are not evidence for report claims.

## Sources used in the report

| Source | Date and version | Verified URL and read scope | Use and limit |
| --- | --- | --- | --- |
| Littlewood and Wright, Some Conservative Stopping Rules for the Operational Testing of Safety-Critical Software | IEEE TSE 23(11), 673–683, 1997; repository calls the PDF an unspecified version | [Metadata](https://openaccess.city.ac.uk/id/eprint/1614/); [PDF](https://openaccess.city.ac.uk/id/eprint/1614/1/Some%20conservative%20stopping%20rules.pdf). Main: abstract and sections 1–2.1. Agent: same sections and section 4. | Direct prior warning about repeated clean tests. The audit does not implement its Bayesian repair policy. |
| Oh, Park, and Kim, Recurrence algorithms of waiting time for the success run of length k in relation to generalized Fibonacci sequences | 2022-10-17, arXiv v1, preprint | [Record](https://arxiv.org/abs/2210.08797v1); [HTML](https://arxiv.org/html/2210.08797v1); [PDF](https://arxiv.org/pdf/2210.08797v1). Main and agent: abstract, introduction, section 2.1.1. | Establishes prior run-probability methods. Other sections and older works cited there were not checked. |
| Howard, Ramdas, McAuliffe, and Sekhon, Time-uniform, nonparametric, nonasymptotic confidence sequences | Annals of Statistics 49(2), 1055–1080, 2021; read arXiv v9 revised 2022-08-06 | [Record](https://arxiv.org/abs/1810.08240); [Read PDF](https://arxiv.org/pdf/1810.08240v9). Main: introduction, properties P1–P4, section 1.1. Agent: also section 6 and Lemma 3. | Distinguishes fixed-time and time-uniform inference. Its full methods and proofs were not reproduced. |
| Yu, Zeng, Zhu, Huang, Zeng, and Jing, Anytime Safe PAC Efficient Reasoning | 2026-01-30, arXiv v1, preprint | [Read HTML](https://arxiv.org/html/2601.22446v1). Main: abstract and sections 1–3. | Current AI context on online risk control. Loss is relative to a thinking model. No experiment or theorem is independently verified here. |
| NeurIPS Paper Checklist Guidelines | Accessed 2026-10-14 | [Checklist](https://neurips.cc/public/guides/PaperChecklist). Relevant claims, assumptions, proofs, reproducibility, code, uncertainty, compute, limitations, ethics, rights, and AI-use items. | Review aid only; no conference approval or submission-compliance claim. |

## Other current primary work inspected

The source agent read Schirmer et al., [Online Safety Monitoring for LLMs](https://arxiv.org/html/2607.02510v1), submitted 2026-07-02: abstract, sections 3.3–3.4, Appendix C, and metadata. The record mentions an ICML 2026 workshop. No separate peer-review record was checked. It addresses monitoring within trajectories, a different decision from this audit.

The source agent read Zhou, Yang, and Morstyn, [Finite-Sample Probabilistic Safety Certification for AI-Based Grid-Edge Coordination](https://arxiv.org/html/2609.28182v1), submitted 2026-09-23, preprint: abstract, sections II-B, III-A, III-B through Corollary 1, V-E, and VI. It is context, not evidence that AI evaluations use the rule under audit.

Other search results were not used as verified report evidence. The search was limited. It found direct prior work that rules out a new-method or first-warning claim. It did not prove whether this exact grid has appeared elsewhere.

## Contribution and prior repository work

The main agent read the live protocol, index, complete remote tree, all five earlier reports, and task state. There was no October 14 report or unfinished study. The October 9 report fixes the decision time and varies trial dependence. The present audit fixes independence and varies the acceptance event over time. The October 10, 12, and 13 reports study saved judge decisions; this audit uses analytic inputs only.

The source agent found the bounded numerical comparison useful, subject to a clear scope limit. Acceptance below the target was not assessed. This limit is stated in the report. It is not evidence of good practical efficiency.

## Access, rights, and attribution

All report references were checked against original source text or metadata on this date. Read sections are stated above; no claim of reading all sources in full is made. Failed source requests are recorded in failed_checks.md. All report text is newly written with short attributed paraphrases. No source paper, table, figure, dataset, or source code is included. No new license is assigned to the owner's work.
