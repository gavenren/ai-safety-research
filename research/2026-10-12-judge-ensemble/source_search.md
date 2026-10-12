# Source review: Safety-Flag judge panels

Date: 2026-10-12 (America/Toronto). Codex prepared this source review before the new data analysis. This review did not run the proposed analysis.

## Proposed question and scope

Does an independent-vote model reproduce the false-positive and false-negative rates of majority votes on the pinned Safety-Flag records?

Use the five primary models from the October 10 study. Evaluate all ten three-model panels and the one five-model panel on each of the seven test sets. Keep each reference class separate. A false positive is a flag on a reference-negative item. A false negative is no flag on a reference-positive item. A panel is a fixed group of models. Majority vote selects the label chosen by more than half of the models.

For each set and class, use the observed error rate of each model. The reference calculation assumes that those errors occur independently after the test set and reference class are fixed. Compute its majority-error probability exactly. Compare that probability with the observed majority-error rate on the same items. Call the difference the independence gap, with its sign defined in the plan. This is a description of the released sample, not a forecast from a held-out calibration sample.

The useful contribution is a new secondary computation on this exact fixed release, with separate error directions and a complete list of the specified panels. The method and concern are established. A limited search cannot show that this exact computation has never been done.

## Search record

All searches and source reads below occurred on 2026-10-12. Search results were used to find original sources. Blogs, social posts, and paper summaries were not used as research evidence.

Search terms:

1. `LLM judge ensemble correlated errors majority voting safety moderation conditional independence`
2. `Safety-Flag benchmark ensemble majority judge correlated errors`
3. `LLM as a judge panel majority vote correlation errors 2026`
4. `site:proceedings.mlr.press "Dependence-Aware Label Aggregation"`
5. `"Safety-Flag" "ensemble"`

The first three searches found the four related papers below. The fourth search verified the ICML publication. The fifth search did not find a separate Safety-Flag panel analysis in the returned results. This absence is not evidence of global novelty.

## Sources read and exact support

### Safety-Flag

Yibo Hu. *Safety-Flag: A Unified Benchmark for the Reliability and Calibration of LLM Content Moderators*. arXiv:2609.19072v1. Preprint. The abstract page reports submission on 2026-08-06. The identifier and that reported date do not follow the usual month pattern; record the source metadata as shown and do not infer a new date.

- [Original full text](https://arxiv.org/html/2609.19072v1)
- [Abstract and version record](https://arxiv.org/abs/2609.19072)
- [Pinned release](https://github.com/yibo-hu-lab/safety-flag-benchmark/tree/82d39d018c5522dfbdf303b49c5d83a8444d03d2)
- Read: abstract; Sections 2, 3, 4, and 5.1–5.2; table of contents for the full analysis scope.
- Supported claim: the benchmark has fixed, approximately balanced items from seven safety sets. It retains each source policy. Its primary ranking excludes the mixed-precision Qwen2.5-32B run. It separates false alarms from misses and releases per-item outputs.
- Overlap: the source already measures the individual error directions. We must attribute these data and avoid presenting the source's individual-model findings as new.
- Difference: the source sections read do not evaluate majority panels against a product of class-specific error rates. A full-text search found no occurrence of `majority`. Its mention of `ensemble` describes Aegis source labels.
- Access note: the web tool could not open the pinned GitHub tree. The parent study must verify the release through Git or the GitHub connector. Do not claim this source review verified its file hashes.

### Closest method comparison

Guneet Kohli. *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels*. arXiv:2605.29800v1, submitted 2026-05-28. Preprint.

- [Original full text](https://arxiv.org/html/2605.29800v1)
- [Abstract and version record](https://arxiv.org/abs/2605.29800)
- Read: abstract; Sections 2, 3.1–3.5, 4.1–4.5, 5.2–5.4; limitations.
- Supported claim: the paper compares observed majority accuracy with independent draws from each judge's class-specific confusion matrix. It also groups items by human disagreement to account for measured difficulty. It uses item bootstrap intervals and a permutation check.
- Overlap: this is a direct prior example of an independent-vote reference for judge panels. The proposed study is not a new diagnostic method.
- Difference: the proposed study uses Safety-Flag's binary safety decisions. It reports each error direction for every specified three- and five-model panel. It has no human-disagreement measure that matches this paper's difficulty control.
- Limit: do not copy the paper's broader claims that no weighting method can recover useful information. The proposed computation cannot establish such a result.

### Published dependence-aware aggregation

Krishna Balasubramanian, Aleksandr Podkopaev, and Shiva Kasiviswanathan. *Dependence-Aware Label Aggregation for LLM-as-a-Judge via Ising Models*. ICML 2026, PMLR 306:5748–5785. The proceedings volume reports publication on 2026-09-29 and conference dates 2026-07-06 to 2026-07-11.

- [Proceedings record](https://proceedings.mlr.press/v306/balasubramanian26a.html)
- [Author full text read](https://arxiv.org/html/2601.22336v1)
- [Proceedings volume](https://proceedings.mlr.press/v306/)
- Read: proceedings abstract and citation; full-text abstract, introduction, Sections 3.1–3.2 and 4.1, and Appendix B example.
- Supported claim: conditional independence can produce a wrong label even when the individual class-specific probabilities are correct. The authors model dependence and compare aggregation methods on relevance, toxicity, and summary assessment.
- Overlap: failures of independence in safety-related judge aggregation are already studied. We must not claim to first identify this problem in toxicity or safety work.
- Difference: the proposed study audits a fixed reference model. It does not train an Ising model or propose an improved voting rule.
- Access note: the web tool could not parse the proceedings PDF because the server used an unsupported content type. Full text was read from arXiv. Do not imply that the proceedings PDF was read or that both versions were compared word for word.

### Recent consensus study

Elias Hossain, Niloofar Yousefi, and Ser-Nam Lim. *Agreement Overstates Evidence: Error Dependence in LLM Judge Consensus*. arXiv:2609.22512v1, submitted 2026-09-18. Preprint.

- [Original full text](https://arxiv.org/html/2609.22512v1)
- [Abstract and version record](https://arxiv.org/abs/2609.22512)
- Read: abstract; Sections 1, 2.1–2.3, 3, 4.1–4.2; Appendix E.3 result text.
- Supported claim: the paper measures shared judge errors on preference data, including PKU-SafeRLHF. It shows that error patterns, not only average correlation, affect consensus. It uses complete item vectors for item-level bootstrap checks.
- Overlap: judge dependence and safety preference panels are already studied.
- Difference: the proposed study reports binary moderation error rates by source test set and class. It does not evaluate filters, training effects, or effective panel size.
- Limit: its evidence does not identify a causal effect of shared training data. Neither would the proposed audit.

### Additional recent work

Gemma Zhang, Prachi Badarayani, Asmi Kumar, Sadid Hasan, and Sulaiman Vesal. *Can We Trust LLM Judges: A Study of Capability-Dependent Biases and Multi-Judge Ensemble for Bias Calibration*. arXiv:2609.12002v1, dated 2026-09-10 in the full text. Preprint.

- [Original full text](https://arxiv.org/html/2609.12002v1)
- Read: abstract, Sections 3.1–3.3, Table 2, Section 7 limitations.
- Supported claim: this work measures separate false-positive and false-negative rates for correctness judges and evaluates cross-judge majority votes. It proposes calibration from disagreement. Its stated limitation is that most panel members must be approximately correct on most items.
- Overlap: separate error directions and majority voting are not new research ideas.
- Difference: this proposed audit concerns moderation reference labels and the error of an independence calculation. It does not test the proposed calibration estimator. Do not use this paper's recommendation for weighted voting as a conclusion of the new study.

## Design limits to state before analysis

1. The same item must supply all five votes. Check model and reference-label alignment. Count the item once in each panel, not once for each vote.
2. Condition on both source test set and reference class. Pooled error correlation can contain a mixture effect from different tasks or classes.
3. A remaining gap can reflect common item difficulty, common policy interpretation, or reference-label error. It does not prove a direct interaction between models or shared training data.
4. The product calculation is an assumption check on this sample. Its margins come from the sample being described. Do not call it out-of-sample predictive validation.
5. Resample full item vote vectors within test set and class. Recompute individual margins and panel errors in each resample. This preserves the dependence under study and the paired comparison.
6. If many intervals are reported, mark them as pointwise descriptive intervals. Do not claim all panel gaps are significant from unadjusted intervals. A global planned summary can be primary; the full cell table can remain descriptive.
7. Do not select the best panel on the same test labels and then claim expected deployment benefit. All specified panels can be reported without this selection claim.
8. The reference labels encode different policies and include labels that are not all independent human assessments. This is an audit against those labels, not an estimate of actual harm.
9. A null result on these labels is useful. Do not change the question after viewing results to obtain a positive result.
10. No new model calls are needed. This is a secondary empirical analysis of saved decisions, with an exact hypothetical independent-vote calculation. It is not a new live model experiment.

## Suggested contribution statement

This study applies an established independent-vote comparison to the five primary models in a fixed Safety-Flag release. It reports observed and predicted false-positive and false-negative rates for every three-model panel and the full five-model panel on seven test sets. The contribution is this reproducible secondary audit and its complete results. It is not a new voting method or a first discovery of shared judge errors.

## Prior local study checked

Read `outputs/2026-10-10-judge-transfer/report.md` and `references.bib`. That study examined transfer of a single judge's rate correction between test sets. The proposed question uses the same saved data but studies joint errors within model panels. It must disclose this reuse.

Review status: Codex source review only. No human review. No data analysis was run for this review.

## Main-agent search and checks

The main agent also searched `LLM judge ensemble correlated errors majority vote safety evaluation 2026` and `Safety-Flag benchmark ensemble majority vote judges 2026` on 2026-10-12, before saving the analysis plan. It read the primary paper sections on the independent-vote model, Safety-Flag data and policy definitions, the consensus paper introduction, and the Ising paper proceedings record. The source review above supplies additional read scope.

The main agent fetched the pinned Safety-Flag DATA_LICENSE.md with the GitHub connector. Its Git blob hash is b072612b2f026bd5fe10c53eecef3d9d5ecbe2e2. It confirms CC BY 4.0 for derived labels and outputs. The unchanged local input matches the published October 10 data blob d0ed3f0d141bf9fbe29492deee3775fed2afc731. That report records the original extraction and checks.

The main agent read the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), including claims, limits, assumptions, reproduction, settings, uncertainty, compute, impacts, and license guidance. This was a review aid only.
