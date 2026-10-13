# Source review: selective safety panels

Date: 2026-10-13 (America/Toronto). Search and reading complete at 12:46 UTC.
Reviewer: Codex source agent. No human review occurred.
Scope: primary sources on selective prediction, judge agreement, and error under a change of data. No new experiment was run in this review.

## Recommendation before analysis

Use a narrow question: Does a fixed agreement threshold reduce the error among accepted safety decisions in every saved test set and reference class?

This can be a useful secondary audit of Safety-Flag votes. It is not a new abstention method. Related work already combines multiple judges and abstention. Other work already shows that an average gain can hide a loss in one group. Do not claim that the idea, the metrics, or this failure mode are new. The limited search below does not prove that nobody has done the exact data audit.

Predefine all three possible agreement levels for five binary votes: at least 3, at least 4, and all 5. Keep the majority decision fixed. Report all levels. Use the reference class only for evaluation, not to choose whether to accept an item. Distinguish an accepted negative decision from a correct negative decision.

For each set and class, report total items, accepted items, wrong accepted items, and abstained items. Define coverage as accepted / total. Define selective error as wrong accepted / accepted; leave it undefined when accepted is zero. Also report wrong accepted / total. That last rate can only stay the same or fall as a fixed predictor accepts fewer items. This mathematical property does not prove that accepted decisions become more accurate.

Use a fixed threshold study unless a separate calibration and test design is saved in the plan. A descriptive test of all thresholds does not give a certified error bound. Do not claim transfer under distribution shift from differences between saved test sets alone. Do not assume that a human would correct all abstained decisions. No human review data are available in the proposed input.

## Search record

Search engine: web tool. Search date: 2026-10-13. No date filter.

1. `LLM judge ensemble agreement selective prediction abstention risk coverage safety`
2. `selective prediction risk coverage distribution shift model agreement abstention paper`
3. `"Selective Classification Under Distribution Shifts" arxiv`
4. `"selective classification" "group" "disparities" Jones`

Non-primary results, such as blogs and social posts, were not used as evidence. The first search also found Rao and Callison-Burch, *Agreement Metrics for LLM-as-Judge Evaluation: What to Report and Why*, arXiv:2606.00093. Only its search abstract was read. Do not cite its full method as checked.

## Three closest sources

### 1. Cheng and colleagues: multi-judge abstention

Ming Cheng, Yusheng Dai, Qiuhong Ke, Zhaolin Chen, and Lizhen Qu. *Multi-Expert Conformal Risk Control for Pairwise LLM Judging in Open-Ended Dialogue*. arXiv:2608.26529v1, 27 August 2026. Preprint.

URL: https://arxiv.org/html/2608.26529v1

Read scope: full relevant text in Sections 1–4, experimental setup and results in Section 6, discussion, limitations, and ethics statement. The appendix proofs were not independently checked.

The paper combines judge scores or decisions with abstention. It studies three-judge panels for pairwise dialogue preference. Its formal loss is the fraction of all items that are both accepted and wrong. Abstention has zero loss. Section 6 states this denominator. It is not the conditional error among accepted items. The bound requires exchangeability and a monotone loss. The limitations state that data shift can break exchangeability. The method uses judge logits, which are not needed for the proposed hard-vote audit.

Use: establish that panel abstention is prior work and distinguish the two error denominators. Do not import the paper's guarantee into a threshold audit.

Rights: the HTML states CC BY 4.0. No paper figure, table, code, or dialogue data was copied. Its benchmark has separate source-data terms; that benchmark is not an input to this study.

### 2. Jones and colleagues: group effects

Erik Jones, Shiori Sagawa, Pang Wei Koh, Ananya Kumar, and Percy Liang. *Selective Classification Can Magnify Disparities Across Groups*. ICLR 2021. The read PDF identifies this publication status. arXiv:2010.14134v3, 14 April 2021.

URL: https://arxiv.org/pdf/2010.14134v3

Read scope: abstract, introduction, Sections 2–4, and the opening of Section 5; PDF pages 1–6. Appendix experiments and proofs were not independently checked.

The authors test selective accuracy and coverage by group. Across five vision and language data sets, an average gain can occur with poor or worse results in a group. The study includes groups formed from labels and related attributes. It also notes that low coverage can leave few predictions and noisy estimates.

Use: motivate set-and-class reporting. A decline in one class would extend an established concern to this saved safety panel. It would not discover a new general failure of abstention. The proposed groups are test sets and reference classes, not demographic groups. Do not make a fairness claim from this audit.

Access note: the OpenReview PDF URL returned a browser check. The arXiv PDF was read instead. No paper content or data was copied into the input.

### 3. Liang and colleagues: risk and coverage under shift

Hengyue Liang, Le Peng, and Ju Sun. *Selective Classification Under Distribution Shifts*. Read version: arXiv:2405.05160v1, 8 May 2024. The final publication is listed as TMLR, October 2024; its full version was not read in this search.

Read URL: https://arxiv.org/html/2405.05160v1

Final publication URL: https://openreview.net/forum?id=dmxMGW6J7N

Read scope: introduction, Sections 2.1–2.5, and the opening of Section 3.1. The final OpenReview PDF returned a browser check. An attempted arXiv v3 HTML URL failed. These failures do not invalidate the readable v1, but its version must be explicit.

The read version defines coverage and error conditional on acceptance. It evaluates risk-coverage curves under several forms of shift. Section 2.4 says to keep the predictor fixed when comparing confidence scores. Section 2.5 separates descriptive test-set evaluation from the selection of a deployment threshold.

Use: define the audit measures and its limits. The proposed study has only three discrete agreement levels. Show those points and counts rather than an interpolated curve that suggests observed intermediate policies.

Rights: the HTML states CC BY 4.0. No code or data from this paper is an input.

## Additional source read for method caution

Sher Badshah, Ali Emami, and Hassan Sajjad. *Judge, Retrieve, or Abstain: Uncertainty-Guarded LLM Judging with Provable Risk Guarantees*. arXiv:2608.17994v1, 18 August 2026. Preprint.

URL: https://arxiv.org/html/2608.17994v1

Read scope: introduction; method Sections 3.4–3.5; Appendix A.1–A.2; calibration details in Appendix B.2. Other experiments were not fully checked.

The paper treats accepted-judgment error and routes uncertain cases to retrieval or abstention. Its displayed probability bound is for fixed thresholds and independent, identically distributed items. It separately describes an adjustment for a search across many threshold pairs. Appendix A discusses changes to retrieval, task, and model.

Use: if this audit later chooses a threshold to meet a target, it needs a separate design and must address selection and data changes. This source does not justify a bound from a descriptive table.

Rights: the HTML states CC BY 4.0. No code, figure, table, or QA input was copied.

## Data rights and claims

The panel input is to come from the pinned Safety-Flag labels already used by the project. This source review did not independently reopen that repository license. The main agent must verify the pinned input, attribution, and license before publication. Do not treat the licenses of the four papers above as licenses for the Safety-Flag data.

No study result is asserted in these notes. The contribution should be stated after the planned analysis: a reproducible, class-specific secondary audit of one saved panel with explicit coverage and error denominators. Search scope remains limited. No claim of global novelty, safety certification, or future performance is supported.

## Extension after the question was selected: review error

The main agent selected a related question before analysis: Does low agreement route more panel errors to review than uniform random selection at the same workload, and how accurate must review be to reduce total error?

Two additional searches on 2026-10-13:

5. `learning to defer human expert errors selective prediction Mozannar Sontag consistent estimators 2020`
6. `learning to defer fallible human expert cost abstention error review performance paper`

### Closest source for a fallible reviewer

Hussein Mozannar and David Sontag. *Consistent Estimators for Learning to Defer to an Expert*. ICML 2020, PMLR 119:7076–7087.

Publication and metadata: https://proceedings.mlr.press/v119/mozannar20b.html

Full paper read: https://proceedings.mlr.press/v119/mozannar20b/mozannar20b.pdf

Read scope: Sections 1–3, system loss Equations 1–2, and Proposition 2 in Section 4 (PDF pages 1–4). The full experiments and appendix proofs were not checked.

The authors define total system loss from model decisions on retained items and expert decisions on deferred items. Their method can learn from samples of expert decisions. They distinguish a fixed cost of rejection from the actual cost of expert mistakes. Their optimal pointwise rule compares model and expert correctness. This is direct prior work for the reviewer-error comparison. The proposed audit has no expert-decision samples, trains no routing rule, and measures no human performance.

Rights: the paper states copyright 2020 by the authors. Only this short paraphrase is used. No source code, data, figures, or tables are copied.

### Accounting and claim checks for the selected question

Let E be all panel errors, D the number sent to review, and E_D the panel errors within those D items. If review replaces the panel decision on every deferred item, and q is the review error fraction on those items, final error is (E - E_D + q D) / N. For D > 0, this improves on E / N exactly when q < E_D / D. The equivalent condition on review accuracy is accuracy > 1 - E_D / D. Equality gives no change. For D = 0, review accuracy has no effect and the break-even value is undefined.

This arithmetic identity does not require independent panel and reviewer errors. It does require the stated replacement policy. A reviewer who only approves or corrects selected panel decisions can have a different policy. Do not claim a new theorem for this identity.

Under uniform random selection of exactly D out of N fixed items with E errors, the number of selected panel errors has a hypergeometric distribution. A central range describes that random routing mechanism conditional on this finite set. It is not an interval for future test error or reviewer ability. Report exact counts and the definition of any discrete quantiles.

A scenario grid that assigns the same review error q to agreement-based and random routing is a hypothetical equal-performance comparison. A real reviewer can find one set harder. The saved votes cannot establish that q is equal, small, or stable. Review workload, review error, and model error should remain separate measures.


## Main-agent search and source verification

Date: 2026-10-13. Searches before the saved analysis plan:

- `LLM judge ensemble agreement abstention selective prediction risk coverage safety 2026`
- `selective classification risk coverage reject option Geifman El Yaniv 2017`

Additional primary source: Yonatan Geifman and Ran El-Yaniv, *Selective Classification for Deep Neural Networks*, NIPS 2017. URL: https://papers.nips.cc/paper_files/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf . Read Sections 1–4, with particular attention to the coverage and conditional risk definitions in Section 2. The report uses the definitions and prior-work status, not the risk guarantee or experiments.

The main agent read selected passages in Safety-Flag Sections 4 and 5 and Appendix D, including the distinction between individual confidence and sampled-answer agreement. URL: https://arxiv.org/html/2609.19072v1 . This is a preprint. Its individual-model abstention is direct prior work. The present contribution is the joint five-model routing audit and conditional review scenarios on a fixed release.

The main agent read Cheng Sections 2–3 and the experimental measure definition. The denominator is all items for its formal loss. This study reports both all-item residual error and conditional accepted-item error.

The Mozannar–Sontag proceedings record and full-paper URL were reopened by the main agent. The source agent read the relevant system-loss sections. Jones's arXiv PDF was also reopened; the source agent's recorded section read supports the report claim. Liang and Badshah inform the search limits but are not cited as evidence for a result in the report.

The NeurIPS Paper Checklist was read as a review aid: https://neurips.cc/public/guides/PaperChecklist . Its use does not imply approval or submission compliance.

The upstream data license was fetched on 2026-10-13 at commit 82d39d018c5522dfbdf303b49c5d83a8444d03d2. URL: https://github.com/yibo-hu-lab/safety-flag-benchmark/blob/82d39d018c5522dfbdf303b49c5d83a8444d03d2/DATA_LICENSE.md . Git blob b072612b2f026bd5fe10c53eecef3d9d5ecbe2e2. It assigns CC BY 4.0 to the derived records. Attribution is retained. The unchanged reduced input also matches the recorded SHA256.

The repository protocol, index, four prior reports, and run state were read. Main was 5da968d9c12edc82e1f0030d7e61f91233c509cd. The complete tree contained no October 13 report or unfinished report. Previous studies were published and verified.
