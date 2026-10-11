# Source review for the 2026-10-10 study

Search and access date: 2026-10-10 (America/Toronto).
Prepared by a separate Codex source-review agent. No data analysis was run for these notes.

## Proposed contribution

Use the saved predictions and reference labels in Safety-Flag. For each model, fit a known rate correction on six source tasks. Apply it to the seventh task. Compare the corrected rate with the raw flag rate, using the seventh task's reference labels only to score the estimates.

This is a proposed secondary analysis of a public data release. It can test a known assumption in a specified setting. It is not a new correction method. It is not the first study of calibration transfer or judge error. The limited search below does not establish global novelty.

The closest Safety-Flag checks are different. Appendix B.2 removes one task and ranks models on the remaining six. Appendix C.3 fits temperature on pooled random splits. Neither check estimates the reference-label rate on a task held out from confusion-rate estimation.

## Sources read for the selected study

### 1. Safety-Flag

- Author: Yibo Hu.
- Title: *Safety-Flag: A Unified Benchmark for the Reliability and Calibration of LLM Content Moderators*.
- Status: preprint, arXiv:2609.19072v1.
- [Abstract and version record](https://arxiv.org/abs/2609.19072).
- [Full HTML, v1](https://arxiv.org/html/2609.19072v1).
- [Code and data repository](https://github.com/yibo-hu-lab/safety-flag-benchmark).
- Read: abstract; Sections 3–5 and 7–8; Appendices B.2 and C.1–C.3; task definitions and limitations.
- Date note: the live arXiv abstract and HTML state 6 August 2026. The identifier has the prefix 2609. Record the version and year; do not silently replace the displayed date with an inferred date.

The paper joins seven tasks with different meanings of an unsafe label. Most samples have about 200 items and a designed balance. It studies error direction, confidence calibration, and selection for human review. Its task removal check assesses rankings on the remaining tasks. Its temperature check uses pooled random half splits. Neither is the proposed held-out-task rate audit. Qwen2.5-32B has one seed and mixed precision across tasks; the paper excludes it from its primary ranking. Do not remove that caveat. Reference labels come from source tasks; do not describe all labels as new human annotations. Parent task separately checked the repository data card and its CC BY 4.0 terms.

### 2. How to Correctly Report LLM-as-a-Judge Evaluations

- Authors: Chungpa Lee, Thomas Zeng, Jongwon Jeong, Jy-Yong Sohn, Kangwook Lee.
- Status: ICML 2026, PMLR 306:65231–65252.
- [Official proceedings](https://proceedings.mlr.press/v306/lee26bl.html).
- [Version record](https://arxiv.org/abs/2511.21140).
- [Full HTML, v4](https://arxiv.org/html/2511.21140v4).
- Dates: first submission 26 November 2025; v4, 31 May 2026; proceedings, 6–11 July 2026.
- Read: abstract; Sections 3–8; Appendix A limitations; sample allocation discussion. The latest version was checked after an initial v2 read.

This paper supplies the direct method precedent. It corrects an observed positive rate with estimated sensitivity and specificity. It accounts for calibration and test uncertainty and studies allocation of annotation effort. Its shift guarantee requires the conditional confusion matrix to stay fixed. It allows a change in label prevalence, not arbitrary task shift. Appendix A states this condition and discusses length, style, and prompt type as possible violations. It suggests stratified confusion matrices. The proposed study tests this known condition across Safety-Flag source tasks. Do not claim a new Rogan–Gladen estimator, new sample allocation method, or general correction under task shift.

### 3. Bias and Uncertainty in LLM-as-a-Judge Estimation

- Author: James Fiedler.
- Status: preprint, arXiv:2605.06939v1, 7 May 2026.
- [Version record](https://arxiv.org/abs/2605.06939).
- [Full HTML, v1](https://arxiv.org/html/2605.06939v1).
- Read: Sections 1–5; Appendix C; shared-calibration and diagnostic sections.

The paper studies error from shared calibration across evaluated models. It includes simulations and an MMLU-Pro case. It derives bias when the sensitivity or specificity in the target differs from calibration. A shared correction can reverse a model comparison. The value sensitivity + specificity − 1 is not a complete transfer check: the two error rates can change while that value stays fixed. This is direct prior work on the proposed failure mechanism. The proposed difference is a fixed, public Safety-Flag task-transfer audit, with direct errors in estimated reference-label rates. It does not introduce the mismatch formula or establish the transfer problem for the first time.

## Other method sources checked

### 4. Efficient Inference for Noisy LLM-as-a-Judge Evaluation

- Authors: Yiqun T. Chen, Sizhu Lu, Sijia Li, Moran Guo, Shengyi Li.
- Status: preprint, arXiv:2601.05420v1.
- [Version record](https://arxiv.org/abs/2601.05420).
- [Full HTML, v1](https://arxiv.org/html/2601.05420v1).
- Read: Section 2 setup; comparison of Rogan–Gladen and prediction-powered methods; Section 7 discussion.
- Date note: the version record states 8 January 2026. The HTML body shows 24 August 2026. Use the version and year if a full date is not needed.

The paper compares correction and inference methods when a small labelled sample and a larger judge-labelled sample come from the same target population. It identifies instance-dependent error and distribution shift as further work. This supports the distinction between estimation error under a shared population and a task-transfer audit. Its real example uses Chatbot Arena rather than a safety benchmark. It is optional background, not required for the planned report.

### 5. Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges

- Authors: Chen Feng, Minghe Shen, Ananth Balashankar, Carsten Gerner-Beuerle, Miguel R. D. Rodrigues.
- Status: ICLR 2026; preprint dated 28 January 2026.
- [Official proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/08a67eb74bfb9ded9e949dd52973e997-Abstract-Conference.html).
- [Full HTML, v1](https://arxiv.org/html/2601.20913v1).
- Read: abstract; Sections 3–5; Section 7 limitations; related work.

The paper uses a labelled calibration set to estimate true-positive and false-positive rates and adjust an evaluation threshold. It discusses finite-sample error control. Its limitations include approximation quality for rare outcomes and small samples, the need for possible stratification, and imperfect reference labels. The proposed study must not claim a new noise-aware threshold test. It uses saved labels to examine how an established correction transfers across source tasks.

### 6. Partial Identification from LLM Prompts

- Authors: Xiaohong Chen, Ashesh Rambachan, Elie Tamer (v2 record).
- Status: preprint, arXiv:2606.15031v2.
- [Version record](https://arxiv.org/abs/2606.15031).
- [Full HTML, v2](https://arxiv.org/html/2606.15031v2).
- Dates: v1, 13 June 2026; v2, 24 June 2026.
- Read: Section 4, Proposition 2, Corollary 1, Remark 3; Sections 8 and 10.1; related work and conclusion.

This paper gives bounds from lower sensitivity and specificity guarantees. It also describes uncertainty bounds from independent calibration data, including simultaneous lower confidence limits. These results rule out a claim that a simple sensitivity or specificity bound is new. The source is useful if the planned study later uses partial identification. The current empirical design does not need it as a central reference.

## Data options considered but not selected

### C-SafeQA

- [Paper, v1](https://arxiv.org/html/2609.01210v1).
- [Data card](https://huggingface.co/datasets/SparkShieldLab/C-SafeQA).
- [Repository](https://github.com/SparkShieldLab/C-SafeQA).
- Date: 1 September 2026 preprint.
- Read: Sections 3.2, 3.8, 4, 5.4 and Table 8, and limitations.

The release lists 37,660 records, four target models, and seven judges. Reference labels use model votes, a further model for disagreements, and human audits at different rates. They are not all independent human labels. Access requires approval and contact sharing. No data were downloaded. The data card lists CC BY-NC 4.0. Published aggregates alone do not provide the proposed item-level transfer audit.

### SORRY-Bench human judgments, 202503

- [Data card](https://huggingface.co/datasets/sorry-bench/sorry-bench-human-judgment-202503).
- [Repository](https://github.com/SORRY-Bench/sorry-bench).
- Read: data card and access terms.

The card lists 7,040 records. Access requires contact sharing and acceptance of a dataset licence. No data were downloaded. The code licence does not replace the dataset terms.

### A Coin Flip for Safety: LLM Judges Fail to Reliably Measure Adversarial Robustness

- Authors: Leo Schwinn, Moritz Ladenburger, Tim Beyer, Mehrnaz Mofakhami, Gauthier Gidel, Stephan Günnemann.
- [Version record](https://arxiv.org/abs/2603.06594).
- [Full HTML, v1](https://arxiv.org/html/2603.06594v1).
- [Repository](https://github.com/SchwinnL/LLMJudgeReliability).
- [CSV](https://raw.githubusercontent.com/SchwinnL/LLMJudgeReliability/main/a_coinflip_judge_data.csv).
- [Licence](https://raw.githubusercontent.com/SchwinnL/LLMJudgeReliability/main/LICENSE).
- Read: methods, data selection, results and limitations in v1; current abstract/version record; CSV header; repository licence.

The ungated CSV has reference judgments and saved judge scores. The paper reports 6,642 labelled outputs from four models and five attack methods. The sample includes only outputs first selected by StrongREJECT as positive. It therefore cannot directly estimate a whole-population unsafe rate. The paper already studies differences across models, attacks, and harm groups, and uses judge precision to adjust attack success rates. This is a less suitable dataset for the proposed target-rate audit. Only the CSV header was retrieved for schema inspection; no data analysis was run. The licence file states MIT. Latest version record: v2, 15 March 2026; the full read was v1, not v2.

## Additional search leads, not full-paper evidence

- [Safer or Luckier? LLMs as Safety Evaluators Are Not Robust to Artifacts](https://aclanthology.org/2025.acl-long.970/), Hongyu Chen and Seraphina Goldfarb-Tarrant, ACL 2025. Read [v2 methods and human-agreement appendix](https://arxiv.org/html/2503.09347v2), dated 13 June 2025. It studies evaluator responses to artifacts across tasks. This can motivate an audit but is not essential to the planned calculation.
- [Know Thy Judge](https://arxiv.org/abs/2503.04474), Eiras et al., 2025. Abstract only; do not cite as a full-paper read.
- [Estimating Prevalence from the Results of a Screening Test](https://academic.oup.com/aje/article-abstract/107/1/71/104051), Rogan and Gladen, 1978, *American Journal of Epidemiology* 107(1):71–76, DOI 10.1093/oxfordjournals.aje.a112510. Metadata and abstract search result only. The full page did not open. Lee and Fiedler supply the directly read correction formulas.

## Search log

Search engine queries used on 2026-10-10:

1. LLM safety evaluator measurement error sensitivity specificity calibrated safety rate judge estimation paper
2. prediction powered inference LLM judge safety evaluation bias sensitivity specificity
3. LLM judge safety evaluation human annotations dataset safety judge benchmark license
4. "LLM-as-a-Judge" "subgroup" "calibration" error rates shift
5. "Noisy but Valid" github
6. "Safer or Luckier" dataset github
7. "Bias and Uncertainty in LLM-as-a-Judge Estimation"
8. "LLM judge" "calibration" "transport" misclassification
9. prevalence imperfect diagnostic test sensitivity specificity bounds partial identification Manski Molinari 2008
10. LLM judge sensitivity specificity bounded drift robust safety threshold uncertainty
11. "Estimating prevalence from the results of a screening test" Rogan Gladen
12. "partial identification" "sensitivity and specificity" bounds misclassification prevalence
13. site.economics.cornell.edu Molinari "Partial identification of probability distributions"
14. "Partial Identification from LLM Prompts" arxiv
15. "WildGuard" "judge" "predictions" "human" github
16. "safety judge" "predictions" "labels" "dataset" "license" github
17. "Know Thy Judge" github dataset
18. "Safety-Flag" "Rogan"
19. "Safety-Flag" "calibration transfer"

The last two queries did not identify a direct prior implementation of the proposed audit. Most matches were irrelevant. This is a limited negative search result, not proof of novelty. Only primary research and author repositories informed the study recommendation.

## Study constraints from the source review

1. Define sensitivity as the share of reference-positive items that the judge flags. Define specificity as the share of reference-negative items that the judge does not flag.
2. Define the target as the rate of the supplied reference label within a designed test sample. Do not call it a deployment harm rate.
3. State that source tasks have different label meanings. A transfer failure can reflect this change as well as a change in input language or content.
4. Fit all correction choices with the six calibration tasks only. The held-out reference labels are for scoring.
5. Check source IDs and duplicates before treating a task as held out. Keep item-level pairing if uncertainty comparisons use predictions from several models.
6. Report when sensitivity + specificity − 1 is small, non-positive, or leads to an estimate outside [0,1]. Do not hide failed corrections by reporting clipped values alone.
7. Retain the Qwen2.5-32B precision and seed caveat. Do not describe an empirical result as evidence for all versions of that model.
8. Do not claim that balanced task samples measure natural label prevalence. The known designed balance can also be a useful simple baseline; define the baseline before analysis.

## Recommended claim

"We apply an established correction for judge error to a fixed public benchmark. We test whether error rates measured on six source tasks improve the estimated reference-label rate on a seventh task. This is a new secondary computation on this release. We do not claim a new correction method or the first evidence of calibration shift."

## Parent-agent search and final scope

Additional queries on 2026-10-10:
- site.arxiv.org LLM safety judge measurement error calibration sensitivity specificity 2026
- site.github.com safety evaluation judge human labels predictions dataset benchmark license
- site.arxiv.org correcting LLM judge misclassification error safety evaluation 2025
- site.github.com safety judge evaluation human annotations predictions WildGuard benchmark results
- site.huggingface.co datasets judge safety human predictions ungated wildguardmix

The parent read Safety-Flag Sections 3–5, repository README, DATA_LICENSE, DATASHEET, build_leaderboard.py, and prevalence.py at the pinned commit. The parent checked Lee's official proceedings and Section 8, and Fiedler's transfer discussion. The separate agent read the wider source sections stated above.

The final design uses five primary models. It excludes the mixed-precision 32B reference. It tests controlled shares {1%, 5%, 10%, 25%, 50%}, using empirical class-conditional rates from saved outputs. Thus the final analysis is a transfer stress test with class reweighting, not a direct estimate of each source sample's natural prevalence. Target labels are used to construct and score the controlled mixture, but not to fit the source correction.

No paid service, inference, model training, or gated data access was used.
