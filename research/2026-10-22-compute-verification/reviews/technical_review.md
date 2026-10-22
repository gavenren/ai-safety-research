# Independent AI technical review

**Reviewer:** Separate AI agent that did not author the study or its central analysis. This is not human or external peer review.
**Scope:** Manuscript, mathematical claims, proposed protocol assumptions, analysis plan, simulation source and saved results. The source dossier was still being prepared when this core review was completed.
**Disposition:** Core argument and reported synthetic results pass after the revisions below. Final source-dossier, disclosure, publication and file-identity checks remain with the coordinating agent.

## Findings and disposition

1. **Project attribution required a separate formal rule (material clarification; resolved).** The initial manuscript allowed a project scope while its main equation summed physical device counts. A fleet lower bound cannot establish that a particular project crossed a threshold. The revised manuscript restricts the main proposition to physical activity and gives a separate project interval, using certainly attributed intervals for the lower bound and every possibly contributing interval for the upper bound. I checked the revised argument: its inequalities follow from the stated attribution assumptions. The project rule remains conditional; no attribution system is implemented.
2. **Zero-denominator coverage needed a defined outcome (minor; resolved).** The revised manuscript reports N/A, rather than perfect coverage, for an empty time/capacity denominator.
3. **Timing uncertainty must preserve a physical partition (clarification; resolved).** The manuscript now explicitly warns against counting overlapping uncertain device-time intervals twice. The disjointness assumption is necessary to the proof. No interval-reconciliation implementation is provided or claimed.
4. **Hardware guarantees are assumptions, not measured results (limitation retained).** The paper correctly distinguishes a valid signature, a fresh attestation, an accurate non-bypassable meter, an inventory boundary, and a project attribution claim. Its proof is conditional on the difficult meter and capacity premises. The code tests arithmetic only.
5. **Contribution and synthetic claims are bounded (passes).** The interval sum and omitted-capacity indistinguishability argument are elementary, not a claimed new cryptographic primitive. The paper does not infer deployment performance, security, or detection rates from its constructed examples. The chosen adverse-missingness results are described accurately, including why withholding highest-activity records does not maximize the calculated upper bound.

## Checks actually performed

- Read the full manuscript, plan, code and JSON results.
- Re-ran an isolated copy of the author's simulation. The saved JSON matched exactly, including all five scenarios, 4,096 missingness patterns and four equality/exceedance boundary checks.
- Independently reconstructed the five scenario totals using complementary sums rather than calling the author's accounting function. All reported truth, observations, lower bounds and upper bounds matched.
- Independently enumerated 135 valid clipped-interval cases, including negative reports and capacity overshoot within the stated error bound; checked three possible external contributions for each. No containment failure occurred.
- Read and checked the revised project-attribution equations and the unconstrained external-capacity argument. The latter is an information limitation within the stated unbounded model, not a claim about physically infinite resources.
- Confirmed that the strict crossing convention is lower bound > threshold, and a within-threshold finding permits upper bound = threshold.

The executable check and detailed results are `technical_check.py` and `technical_check_results.json`. That JSON records the initial reviewed manuscript hash; the final revised manuscript hash is recorded below. The code and numerical results were unchanged by the scope clarification.

## Primary-source spot checks

The reviewer separately read RFC 9334 §§10–12 (freshness, privacy and trust assumptions), O'Gara et al. §§2.3 and 4.4 (cluster-boundary challenges and secure-meter requirements), NVIDIA's GPU Claims page (reported signatures, certificate state and freshness fields), RFC 9162 (Merkle inclusion/consistency and Experimental status), and the arXiv metadata/abstracts for both flexHEG papers. These checks support the narrow source descriptions used in the manuscript. The reviewer did not reproduce hardware claims, exhaustively verify the literature, or establish novelty.

- https://www.rfc-editor.org/rfc/rfc9334.html
- https://arxiv.org/html/2505.03742v1
- https://docs.nvidia.com/attestation/advanced-documentation/latest/claims-guide/gpu_claims.html
- https://www.rfc-editor.org/rfc/rfc9162.html
- https://arxiv.org/abs/2506.15093
- https://arxiv.org/abs/2506.03409

## Remaining limitations

No GPU, secure meter, signature scheme, transparency-log witness network or real operator was tested. The finite checks supplement, rather than prove, the conditional mathematics. No real-world confidence level, evasion success rate or legal-compliance determination follows. Release labels and source provenance must accurately preserve these limits.

## Final reviewed content identities

Reviewed at 2026-10-22T16:25:01.766205+00:00

```json
{
  "technical.md": "7615d81b7d6ff0906f2e0ae88c7577a22a2fe98943e40dceeb64d7c1e9ae54ad",
  "technical_plan.md": "fca0a6bb0e149aefe1edac14d3abf0949880f6c3a19de936a8b495b0a986b4c5",
  "technical_simulation.py": "ccee60d8ae27cabdf608702fcad73aa4457bdd466d2ea7e085647c3bd668ece8",
  "technical_results.json": "5fd9b11dd82592538cd838276764055d6289a5b23b6c6eee45b98d8039eacfd3"
}
```

## Literature and source-dossier follow-up

The reviewer read the completed source/search record and bibliography, then checked the added Kimpson, Baker and Graham preprint against its original Sections 2–3 at https://arxiv.org/html/2610.07476v1. Its use of observational ambiguity and conservative power-based bounds is accurately summarized. The manuscript distinguishes those antecedents from receipt/inventory accounting, does not claim a new general identifiability theorem, and adopts none of the source's hardware numbers. This literature-only addition passes. Numerical code and results did not change.

The dossier explicitly identifies paraphrases, source versions, locators and access limitations; it does not mislabel paraphrases as retained source snapshots. Minor limitation: some architectural antecedents were checked at the author-abstract level, disclosed in the dossier, and the corresponding manuscript descriptions are appropriately narrow. Bibliographic metadata for the proof-of-learning authors and conference status agrees with the original author preprint. No unresolved substantive blocker remains within this review's stated scope.

Follow-up at 2026-10-22T16:27:13.896101+00:00

```json
{
  "technical.md": "7a27d7ffda620eed1128a4cd5c4728fb3684a4e0655ef0c776ceaae54309adf0",
  "technical_sources.md": "2f12bb18330bd292764874c11f3f5125fc4ddf6cec6b46661b2bd85374aa5292",
  "technical_references.bib": "0f9af342c4fa3cb9d2e38fe4ce741d8c728158703b16150891485d76ead96a0e"
}
```
