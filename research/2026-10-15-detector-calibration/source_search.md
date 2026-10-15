# Source search and read record

Date: 2026-10-15. Time zone: America/Toronto.

Codex searched primary sources before selecting the question. A separate Codex agent checked the closest sources. This was a focused search, not a systematic review. No human review occurred.

## Scope and contribution

The study calculates how finite detector calibration affects a planned zero-flag decision. It compares point sensitivity, a lower confidence limit, and two baselines. It includes a fixed target-test cap, acceptance below the failure threshold, and workload. A **positive control** is an item with a known failure label. **Sensitivity** is the probability that the detector flags such an item.

The contribution is the complete numerical audit and its checks. Binomial confidence limits, detector correction, and allocation of error across uncertain quantities are established. This search does not prove that the exact comparison is new. No new estimator or first discovery is claimed.

The October 10 report tested transfer across benchmark sets. This study assumes transfer and isolates finite calibration uncertainty. The October 14 report tested repeated stopping windows with correct labels. This study has one final target decision and imperfect detection. Earlier reports and the repository protocol were read before selection.

## Sources used in the report

### Feng et al. (2026), arXiv v1

[Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges](https://arxiv.org/html/2601.20913v1). Version date: 2026-01-28. Preprint version read.

Read: abstract; sections 1, 3, 4, and 5.1; Theorem 5.1; section 7 limitations. The paper adjusts judge tests for calibration uncertainty. Its theorem includes an approximation term. Its limitations name Normal approximations and rare-event problems. It proposes exact binomial limits as future work for such cases. This audit uses a narrower zero-flag decision. It does not evaluate their full method. The abstract's broad finite-sample claim is not used as an exact error guarantee.

Rights: arXiv perpetual non-exclusive license, as shown in the HTML. No text, figure, data, or code from the paper is redistributed.

### Cai et al. (2020), arXiv v1

[Exact Inference for Disease Prevalence Based on a Test with Unknown Specificity and Sensitivity](https://arxiv.org/html/2011.14423v1). [PDF](https://arxiv.org/pdf/2011.14423v1). Version date: 2020-11-29. Preprint.

Read: abstract, introduction, and all of section 2.1. The method uses separate binomial samples for test-positive rate, sensitivity, and specificity. It adjusts test error for uncertainty in these quantities. Its numerical implementation uses a grid and simulation. This is prior work for calibration uncertainty and error allocation. The present study is a simpler exact calculation for one decision rule. It does not reproduce their general method.

Rights: arXiv perpetual non-exclusive license, as shown in the HTML. No source assets are redistributed.

### NIST/SEMATECH e-Handbook

[Section 7.2.4.1: Confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). Accessed 2026-10-15; no publication date is assigned here.

Read: the exact binomial section and its tail equations. The page gives exact limits by inversion of binomial tail probabilities. It explains why a Normal approximation can be unsuitable for a small sample or count. The study defines its one-sided tail equation and checks it independently.

Rights: public official documentation. The study cites the page and independently implements the formula. No source program, table, or page text is redistributed.

### NeurIPS Paper Checklist

[Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist). Accessed 2026-10-15.

Read: the items on claims, limitations, theory, reproduction, code, settings, uncertainty, compute, ethics, impacts, safeguards, licenses, and assets. The checklist is a review aid. Its use does not establish conference approval, submission compliance, or peer review. The completed checks are recorded separately.

Rights: a public checklist was consulted. Its full text is not reproduced.

## Other leads and read limits

- [NIST Dataplot: EXACT BINOMIAL](https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm). Read the purpose, description, equations, and one-sided syntax. The page gives an implementation date of March 2008. This is an additional method reference, not a separate report result.
- [Fiedler (2026), arXiv:2605.06939v1](https://arxiv.org/html/2605.06939v1). Read the abstract and sections 1–4.4. This is a lead on calibration transfer and uncertainty. No empirical claim from it supports the report. The HTML shows CC BY 4.0.
- [Lee et al. (2026), ICML proceedings](https://proceedings.mlr.press/v306/lee26bl.html). Read metadata and abstract only. The linked PDF returned a tool error. No detailed method comparison is made. The page identifies copyright of the authors and PMLR.
- [Larremore et al. (2021), eLife](https://elifesciences.org/articles/64206). A search result showed Appendix A4 on zero positive tests with known detector errors. Direct eLife and [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7979159/) access reached browser checks. The full article was not read or used as a report reference.
- [Cai et al., later journal record](https://pubmed.ncbi.nlm.nih.gov/37529562/). Metadata was checked. The later PMC article and PDF reached browser checks. The report cites the arXiv v1 that was read.
- [Clopper and Pearson (1934), publisher record](https://academic.oup.com/biomet/article-abstract/26/4/404/291538). Only the record was accessible. The report uses the NIST equations and does not imply that this original full text was read.
- An indexed OpenReview PDF for Feng et al. stated ICLR 2026. Direct access reached a browser check. The report identifies the arXiv version actually read as a preprint.

The package contains synthetic inputs and independently written code. It does not contain source papers, external data, copied code, or external figures. No new license is assigned to the repository owner's work.

## Queries

All queries were run on 2026-10-15. Search results were leads. Only the read scopes above support source claims.

1. `AI safety evaluation imperfect detector sensitivity finite calibration zero observed failures 2026`
2. `LLM judge prevalence confidence interval finite calibration sensitivity 2026`
3. `zero positive diagnostic tests unknown sensitivity confidence upper bound prevalence validation sample`
4. `LLM judge uncertainty prevalence sensitivity specificity calibration confidence interval 2026 arxiv`
5. `prevalence imperfect diagnostic test sensitivity estimated calibration exact confidence interval zero positives`
6. `"exact" "prevalence" "imperfect" "2019687"`
7. `"confidence" "zero" "sensitivity" "freedom" binomial imperfect tests prevalence`
8. `"Clopper" "Bonferroni" prevalence sensitivity confidence interval`
9. `"Estimating SARS-CoV-2 seroprevalence and epidemiological parameters" eLife`
10. `"2019687" prevalence exact inference`
11. `"LLM" "judge" "calibration" "zero" "2026" confidence`
12. `"PMC10388830" exact prevalence`
13. `"confidence interval" "prevalence" "sensitivity and specificity" "exact inference" 2022`
14. `site.arxiv.org "LLM-as-a-Judge" "finite-sample" "2026"`
15. `"Exact inference for disease prevalence based" arxiv`
16. `"Clopper" "Pearson" "1934" "fiducial" pdf`
17. `"Larremore" "Fosdick" "64206" authors`
18. `site.itl.nist.gov binomial one sided lower confidence bound exact`
19. `site.arxiv.org "Noisy but Valid" "2601.20913v2"`
20. `"zero flags" "sensitivity" "confidence" AI`
21. `"zero failures" "calibration" "Clopper-Pearson" judge`
22. `"positive controls" "sensitivity" "Bonferroni" prevalence`
