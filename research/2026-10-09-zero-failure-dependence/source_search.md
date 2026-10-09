# Source search and citation record

Search date: 2026-10-09, America/Toronto. Codex and a separate source-review agent searched the web. This was a focused search, not a systematic literature review. A limited search does not establish first discovery.

## Main search terms

- AI safety evaluations correlated samples repeated attempts statistical confidence zero failures beta binomial
- site.arxiv.org safety evaluation sample size repeated prompts correlation 2025 2026
- LLM safety evaluation pass k repeated attempts statistical confidence zero failures
- correlated zero failures LLM evaluation
- safety test prompt allocation beta-binomial
- "zero failure" "moment" "correlation" beta binomial
- "same mean" "correlation" "zero" "beta-binomial"
- "zero failures" "effective sample size" beta
- exchangeable Bernoulli moments zero beta binomial bounds
- Sums of Exchangeable Bernoulli Random Variables for Family and Litter Frequency Data

## Sources used in the report

All sources below were accessed on October 9, 2026. No source dataset or model result is used as an input to our grid.

1. [Feng et al., version 2](https://arxiv.org/html/2601.22636v2), February 8, 2026. First version January 30. Preprint. Read relevant model sections 2 and 3, and appendices B.2 and C.2. The Beta hierarchy, zero-event formula, and related budget comparisons already exist. Our contribution is the specific three-distribution decision audit. Version 1 was also inspected at the start of the search; the final report cites version 2.
2. [Biroli, version 1](https://arxiv.org/html/2609.32116v1), September 26, 2026. Preprint. Read the abstract, Section 5, and Appendices B and C. The equal-cost independent-draw result and Beta survival expression are prior work. Our study does not claim these as new results.
3. [Gan et al., version 1](https://arxiv.org/html/2609.34320v1), September 28, 2026. Preprint. Read the abstract, relevant sections 3 and 4, and the audit discussion. This is current evidence that correlated task groups matter for AI evaluation. We do not reproduce its empirical results or use its measured correlation as our input.
4. [NIST handbook, Section 7.2.4.1](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). Read exact binomial tail equations. The source gives two-sided limits; our report explicitly uses a one-sided tail of 0.05 and derives the zero-failure case. Page date is not stated in the read page.
5. [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). Read claims, assumptions, proofs, reproduction, resources, uncertainty, limitations, ethics, and asset-rights guidance. It is a review aid, not an endorsement.
6. [Zaigraev and Kaniovski author manuscript](https://serguei.kaniovski.wifo.ac.at/fileadmin/pdf/kn_reliability.pdf), dated March 28, 2010. Journal article published in 2010. Read the abstract, introduction, Section 2, and theorem statement. Higher-order dependence and event bounds are established topics. Our examples are not claimed to be global sharp bounds.

## Other close work found

[Yu and Zelterman](https://www.sciencedirect.com/science/article/pii/S0167947307002162), 2008, gives different distribution shapes with equal first two moments. Indexed excerpts from Sections 1, 2, and 4.1 were read. Direct PMC access required a CAPTCHA, so the complete article was not inspected. This article supports the novelty limit; it is not used to prove our calculations.

[Hisakado et al.](https://arxiv.org/html/physics/0605189v1), 2006, gives standard beta-binomial moments and correlation. [Broadwater, version 2](https://arxiv.org/html/2602.11786v2), April 28, 2026, discusses repeated safety tests and the limits of independence. Relevant sections were read by the source agent. These reinforce that neither the model nor the general concern is new.

## Exact contribution and limits

The new work in this run consists of the saved design, 252 computed grid rows, 84 conditional boundaries, an explicit sample-size-substitution counterexample, and independent numerical checks. It is a small reproducible application of established probability methods. The search does not show that nobody has made the same comparison before.

The three-model sensitivity range is not a confidence interval or a global bound. Real AI performance, actual incident rates, and harm severity were not measured. The parameter values are hypothetical. All sources are paraphrased and linked. No paper text or figures are copied.
