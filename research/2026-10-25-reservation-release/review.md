# Separate method and report review

Date: 2026-10-25. Reviewer: a separate Codex agent. This is AI review, not human review or external peer review.

## Decision

Pass for the stated finite model, saved results, report, and reproduction instructions. No material method, code, count, or claim error was found. One wording change was requested and checked: a fence blocks future acceptance; its receipt records this fact. No method or main-code change was required.

This decision covers the local research package. It does not prove remote publication. The release process must still check its final file list, private-data scan, links, and remote commit.

## Review scope

The reviewer read the frozen plan, freeze records, full main interpreter, results, controls, both run environments, reproduction record, independent specification and adapter records, source review, report, README, changes, bibliography, and reproduction checker. The reviewer did not run a third main experiment. Checks on saved evidence were read-only.

The plan and main-code hashes match the freeze records. The plan was frozen before the main implementation. The independent specification was frozen before its author read the main code or results. Its adapter was frozen after schema and sample inspection, but before complete comparison. The first full comparison passed before main-source inspection. The unchanged adapter then passed on the second saved run. This review uses that stated order and does not claim that all review work was blind.

## Model and measure checks

All six events occur once. The constraints A<E<T and O<D permit 60 orders. Four demand pairs and four capacity values leave 14 settings after a<=C. Two outcome branches give 1,680 worlds. Five rules give 8,400 outcomes. Duplicate branches after blocked acceptance are retained as controls. They are not independent samples.

All rules receive the same provider events. Thus the comparison measures use of evidence. It does not measure the cost or effect of choosing to install a fence. F blocks future acceptance but does not cancel accepted work. A saved closure certificate is true only if A was never accepted, or A has already resolved with zero charge. The latter is a stated model interface, not the source paper's never-accepted certificate format. A false certificate does not become true merely because later resolution occurs.

Liability is the largest A charge compatible with current provider state. It does not use the selected future charge/zero branch before resolution. Each B admission uses the same atomic local-balance check. T books the actual A result once, including after premature release. Thus late settlement can expose a negative balance; it is not discarded.

Actual excess, possible exposure, uncovered A liability, and blocked feasible work are different measures. Their counts can overlap and must not be added. Actual breach and eventual negative balance coincide here because all final receipts arrive, and charges do not decrease. This equivalence is not asserted for other models.

The conditional safety argument is sound under the stated assumptions. A retained reservation or correct booking covers maximum A liability. A sound closure certificate permits release only when that liability is zero. The B balance check then preserves the total bound. The argument requires correct maximum charges, complete acceptance control, job-specific evidence, sound certificates, and correct settlement. The simulation does not prove that a real service supplies these conditions.

## Evidence checks

The reviewer's read-only audit found 8,400 unique input/rule keys and 50,400 event transitions. Every before-state equals the previous after-state. Checks based on event positions matched attempted acceptance, accepted status, resolution, actual charge, fence status, final settlement, and settlement count. Final booked A charge equals actual A charge in every case. Saved case scores agree with the five rule summaries.

Seven named controls give 35 rows. They cover acceptance before and after fencing, early final settlement, a zero observation followed by charge, both orders of zero resolution and fencing, and exposure hidden by a final zero outcome. The main controls and separately specified controls passed.

The independent adapter checked both saved runs. Each comparison covers all 8,400 outcomes, 50,400 events, full saved states, decisions, observations, scores, summaries, paired differences, and saved adverse examples. These comparison counts measure coverage. Repeated state values are not additional statistical observations. The separate [independent review](independent_review.md) records the comparison structure and exact limits.

The report's counts match the saved outputs:

| Rule | Actual breach | Exposure breach | Uncovered liability | Exposure without final breach | B accepted | Feasible B refusal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Timeout | 130 | 200 | 560 | 70 | 1,465 | 0 |
| ZeroObservation | 105 | 175 | 490 | 70 | 1,440 | 0 |
| FenceOnly | 55 | 70 | 196 | 15 | 1,305 | 30 |
| ClosureCertificate | 0 | 0 | 0 | 0 | 1,215 | 50 |
| TerminalOnly | 0 | 0 | 0 | 0 | 1,105 | 160 |

Each row has 1,680 worlds. ClosureCertificate admits 110 more B jobs than TerminalOnly and does not reject a job admitted by TerminalOnly. The stated examples and the explanation for the 50 remaining feasible refusals match the traces.

The documented reproduction checker was run on the two saved result folders. All seven deterministic data files have identical bytes. The README commands match the supplied program interfaces. The reproduction record and independent comparisons pass. No new full run was made for this final review.

## Resources, sources, and release limits

The saved runs used Python 3.13.7 on macOS 26.7.2, arm64. Each used less than 2.5 CPU seconds and 2.5 wall seconds. Each primary result set used 1,390,317 bytes before its environment record. These are within the declared limits. The CPU limit uses Unix resource controls; wall-time and output-size checks are periodic. No Windows test is claimed. The simulator has no model API, network call, random seed, or paid-compute step.

The reviewer read the relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) for claims, assumptions, limits, methods, reproducibility, statistics, and ethics. It is a review aid only. This review makes no claim of approval or submission compliance.

Primary-source inspection supports the distinction between acceptance fencing and terminal evidence. The closest source is a preprint, and its full system was not reproduced. Google documentation supplies motivation, not study measurements. The separate [source review](source_review.md) checks the six references and stated reading limits. The earlier October 24 study concerns local allocation; this study adds acceptance, external charge, and delayed settlement. The report limits its contribution to the exact comparison artifact. It does not claim a new mechanism or establish global novelty.

The report states that this is a finite simulation. No live website, connected account, or model action-selection trial occurred. All final outcomes arrive. Permanent uncertainty, crashes, retries, partial charges, changing prices, and multiple budgets are outside the model. B is synchronous. The closure certificate is assumed sound and is not shown to exist in a production interface. No sampling confidence interval or operational failure rate is warranted.

The reviewed evidence is synthetic. No account record, credential, person-level measurement, copied source passage, source figure, or third-party implementation is needed by the study. The final release still requires the root agent's package scan. The report states the Codex role and absence of human review and peer review. It assigns no new license and makes no affiliation or endorsement claim.

## Reviewed file hashes

SHA-256 values for the final method and report review:

| File | Hash |
| --- | --- |
| `plan.md` | `0a3eab2beeac2da6bbec8ca66166b9583749b2864bdf55e88b742c0d9a106c1a` |
| `freeze.json` | `107c5990bfe3fa3c5d82db45a1168de52676fd8e010c97d5c9d0e4b068c99966` |
| `implementation_freeze.json` | `a119c64ae49bb68f47b8bc15915c385f836f03599d39c0c66a6b0bd8f97a94d7` |
| `run_study.py` | `80c6620f8d23347535b436d877822fc82e8f2e644c8b1fda7b6d871b680a3a75` |
| `report.md` | `e38acc1f209885e14e6bf2dcd1e10d45a90b7905aaff886c4a17ea32219f7d85` |
| `README.md` | `a89013c4a9f4beab070dab82c77109c6ee57b25756ce058d1c207718c8f6836b` |
| `changes.md` | `48d52a1f87bb2c9e91bc834d7fa2e4ddec54958f9214d7dd80ebe6242ef25491` |
| `check_reproduction.py` | `02c092a559d5d420bb888febf9c7ed912eff7eb8b7ededd3189734a53a94770d` |
| `independent_check.py` | `695722d9948192cb4ec077c2fb7d77ba582849b8c8ddbddd63fd3b64c8158fd3` |
| `compare_independent.py` | `643a85d5a0d504b7b3cbe349cb924a9d44f8fb6822175accfb3d57f0603200a3` |

The deterministic evidence hashes are in [reproduction.json](reproduction.json). Publication verification is separate from these local checks.
