# Source and search record

Search and access date: 22 October 2026. This was a targeted search, not a systematic review. Notes below are original paraphrases for claim checking, not source snapshots. No full source paper is redistributed. No direct quotations are used apart from bibliographic titles and standard identifiers.

## Search queries executed

Search service, first pass:

1. `site.arxiv.org hardware enabled mechanisms verification AI compute governance proof of training compute verification`
2. `site.rfc-editor.org RFC 9334 remote attestation architecture`
3. `site.docs.nvidia.com confidential computing GPU attestation overview H100`

Search service, second pass:

4. `site.docs.nvidia.com attestation gpu verifier evidence measurements nonce confidential computing`
5. `site.arxiv.org Proof of Learning Definitions and Practice Jia 2021`
6. `site.arxiv.org 2506.15093 Flexible Hardware Enabled Guarantees for AI Compute`
7. `site.arxiv.org 2606.05433 zero knowledge verification frontier AI training possible`

A final closest-work check, supplied by the governance research agent, identified arXiv:2610.07476v1. Its original HTML was opened directly on the same date; no new search query was used for that retrieval.

Primary results were opened directly. Vendor marketing and secondary summaries were not used as evidence for performance claims. The proposed protocol, definitions, conditional bounds, and synthetic data are original analysis, not claims extracted from these sources.

## Primary sources checked and claim map

| Ref | Original source | Locator checked | Claim supported and limit |
|---|---|---|---|
| 1 | https://www.rfc-editor.org/rfc/rfc9334 | Introduction; Section 10 and 10.2 | Defines attester, verifier, relying party, and policy appraisal. Nonce-based freshness gives a limited time association. It does not establish the continuous compute meter proposed here. Informational RFC. |
| 2 | https://docs.nvidia.com/attestation/advanced-documentation/latest/claims-guide/gpu_claims.html | Version 3 detached claims, especially report-signature check, certificate status, `measres`, and report-nonce match | Documents checks of attestation evidence. Does not establish complete operation-count metering. Vendor documentation is mutable; accessed 2026-10-22. |
| 3 | https://arxiv.org/html/2505.03742v1 | Executive summary; Sections 3 and 4.4 | Surveys hardware governance mechanisms and challenges. Section 4.4 distinguishes user-resettable profiling counters from protected meters. Supports the proposed secure meter's status as a requirement, not an off-the-shelf guarantee. Preprint. |
| 4 | https://arxiv.org/abs/2506.15093 | Author abstract and metadata, v1 | Describes a proposed guarantee processor and secure enclosure with flexible verification capabilities. Used only for this architectural antecedent; no performance claim adopted. Preprint. |
| 5 | https://arxiv.org/abs/2506.03409 | Author abstract and metadata, v3 | Describes proposed implementation options and accelerator data-path access. Used only to identify related hardware architecture work. Preprint. |
| 6 | https://www.rfc-editor.org/rfc/rfc9162 | Introduction, append-only Merkle log and inconsistent-view discussion | Supports inclusion/consistency log patterns and their equivocation limit. Does not establish receipt completeness or count truth. Experimental RFC. |
| 7 | https://arxiv.org/abs/2103.05633 | Author abstract and metadata | Introduces proof-of-learning as evidence connecting training effort to model parameters. Used to distinguish training-history claims from physical resource accounting. Paper appeared at IEEE Security and Privacy 2021; cited link is author preprint. |
| 8 | https://arxiv.org/html/2606.05433v1 | Abstract, Introduction, and Appendix A headings | Proposes commitments, network observations, and zero-knowledge verification, with listed open problems. Treated as a proposal. Projected deployment time and overhead are not adopted as established results. Preprint. |
| 9 | https://arxiv.org/html/2604.04712v1 | Abstract; taxonomy outline and scope/method | Separates monitoring, verification, and enforcement and presents feasibility classifications. Used to position the contribution; its legal statements and forecasts are not used. Preprint. |
| 10 | https://arxiv.org/html/2610.07476v1 | Sections 2.2–2.3 and 3 | Conditions covert-compute bounds on trusted power observations, energy bands, and capacity assumptions. Closest formal antecedent for observational ambiguity and conservative bounds. No numerical results adopted. Preprint, dated 2026-10-05. |

## Closest works and distinction

References 3–5 are the closest architectural works. They already propose or discuss protected metering and hardware-based claims. Reference 8 is close to training-specific verification. Reference 9 is close to the function/readiness distinction. Reference 10 is the closest formal antecedent: power-trace ambiguity and conditional covert-compute bounds. We make no new general identifiability claim. This study contributes a precise conditional accounting interface, two elementary arguments, and a reproducible missing-evidence example. It does not claim invention of attestation, secure metering, interval arithmetic, or transparency logs. This search cannot establish priority or exhaustive novelty.

## Retrieval limits

The search tool could not open the HTML rendering of arXiv:2506.15093v1; its original arXiv abstract page was successfully read. The initial generic NVIDIA `attestation/overview.html` path did not resolve; the specific GPU Claims page did. The arXiv abstract route for 2606.05433 returned an error in one open call; its original HTML full-text route was read successfully. No substantive claim relies on those failed retrievals.

## Source-use boundaries

Literature summaries are short paraphrases. Protocol choices, assumptions, threat analysis, equations, and synthetic results are the study's own proposed analysis. There are no copied figures, datasets, or source code. Bibliographic metadata and URLs support independent checking. Original-source licenses remain with their owners; this package assigns no new license to them.
