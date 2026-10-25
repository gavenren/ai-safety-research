# Source and claim review

Date: 2026-10-25, America/Toronto. Review by a separate Codex agent. No human review occurred. This review first covered the frozen plan and proposed source use. It then checked the final report, README, and bibliography. It does not independently validate experiment code or result counts.

## Final decision

Pass for source use, contribution limits, certificate meaning, publication scope, and disclosure. No material error was found in those areas. The separate experiment and publication checks remain necessary.

The report correctly treats the five rules as established mechanisms. Its claimed contribution is the exact test corpus and comparison artifact. It identifies the closest paper as a preprint and states the limits of the reading and search. AADP is absent from the report and final bibliography. It remains only a question-selection lead in the search record.

The report distinguishes the model's accepted terminal-zero case from the source's never-accepted certificate. It states the stronger information requirement beside the rule definition. The provider examples supply motivation only; they do not support numerical results or claims about live tests. The report states that no production trial occurred, all final receipts arrive, and the counts do not estimate operational risk.

All six numbered references match the bibliography and the checked source scopes. The report uses short paraphrases and links. No quoted source passage, source figure, or source implementation appears in the reviewed report or README. Both files state the actual Codex role, absence of human and external peer review, and absence of a new reuse license. No unsupported affiliation or approval claim was found.

Reviewed file hashes, SHA-256:

| File | Hash |
| --- | --- |
| `report.md` | `e38acc1f209885e14e6bf2dcd1e10d45a90b7905aaff886c4a17ea32219f7d85` |
| `README.md` | `a89013c4a9f4beab070dab82c77109c6ee57b25756ce058d1c207718c8f6836b` |
| `references.bib` | `a931fa9159707df67ce835167701e3a41327d3088f48b880923467f4e37db07f` |

## Initial decision before the report

The plan supports a useful, limited regression artifact. A regression artifact is a fixed set of cases that can detect an incorrect rule. The study can report its exact corpus, full traces, matched rule comparisons, and independent checks. It cannot claim a new release mechanism, a new impossibility result, a production failure rate, or global priority. The limited source search does not prove novelty.

## Certificate meaning

The plan defines `ClosureCertificate` as a saved receipt from event F. F closes future acceptance and records the current provider state. Its certificate is true in two cases: A was never accepted, or A was accepted and has a final zero-charge outcome. The second case is an explicit model assumption. A point observation of zero charge does not meet it.

Zhu and Wang's exposed-obligation no-effect certificate requires proof of non-acceptance and no possible effect, with a gateway fence. The paper treats complete charge receipts separately. Its general settlement framework allows an authenticated remainder to return. Our combined certificate is not a reproduction of that interface. Do not describe the accepted terminal-zero case as their never-accepted certificate, or claim it is a new finding. [Sections 6.1, 11.5, and Appendix B](https://arxiv.org/html/2610.00349v1).

The plan and final report state the difference correctly. The report retains the interface assumptions beside the rule definition. `ClosureCertificate` has a stronger information interface than `FenceOnly`. Any advantage depends on that interface being sound. No real provider is shown to supply it.

## Permitted source uses

| Source | Supported use | Required limit |
| --- | --- | --- |
| [Zhu and Wang, preprint v1](https://arxiv.org/html/2610.00349v1) | Direct prior work for uncertain reservations, fences, settlement, and budget coverage | Identify it as a preprint. State that the mechanisms are established. Do not claim to reproduce its full protocol or results. |
| [AWS timeout guidance](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | A failed or timed-out call can still have effects | This motivates uncertainty. It does not prove our policy counts. |
| [Google long-running operations](https://docs.cloud.google.com/translate/docs/reference/rpc/google.longrunning) | Cancellation is an asynchronous request whose result needs a check | Apply this to the documented interface only. No Google trial was run. |
| [Google Cloud Run timeout](https://docs.cloud.google.com/run/docs/configuring/request-timeout) | A connection can end while processing continues | Use as a concrete example only. No Cloud Run service was tested. |
| [Chubby](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf) | Background on recipient checks for delayed requests | No Chubby implementation, benchmark, or guarantee is tested. |
| [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) | Review aid for claims, limits, methods, and release | No approval or submission-compliance claim. |

AADP-04 remains a search lead. The selected model does not test execution deadlines or a conforming AADP implementation. Omit AADP from the main argument. A claim that this study finds an AADP defect would not be supported.

## Report checks required after the run

1. Separate measured corpus counts from assumptions and interpretations.
2. Use every-event exposure and coverage measures. Final charge alone can hide an earlier uncovered obligation.
3. Keep blocked feasible work separate from unsafe behavior. Measures can overlap.
4. State that all final receipts arrive in this model. The model does not test permanent uncertainty, crashes, authentication, partial charges, or agent action selection.
5. State that no live website or connected-account trial was run for this study.
6. Check the reported numbers against saved outputs. This source review cannot supply that check.

Source text and code were not copied. The review uses links and short paraphrases. No new license is assigned to the user's work. Read scopes and excluded leads are in [source_search.md](source_search.md).
