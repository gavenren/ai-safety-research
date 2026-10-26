# Separate method and report review

Date: 2026-10-26. Reviewer: a separate Codex agent. This is AI review, not human review or external peer review.

## Decision

Pass for the frozen finite model, both saved main runs, report, and reproduction instructions. No material code, count, proof, or method error was found. One wording change was requested and checked: the LastValue paragraph now calls an intermediate coverage gap an uncovered state. It does not count every coverage gap as an unsafe admission. No experiment change was required.

This review is a local method and report check. The separate source review, final package scan, selected-file manifest, and remote publication verification remain release requirements. A local pass is not proof of publication.

## Scope and evidence

The reviewer read the frozen plan, main source, freeze records, saved controls, traces, summaries, paired results, witnesses, both run environments, reproduction checker, independent specification and adapter, their freeze and comparison records, source search, bibliography, change record, report, and README. The reviewer did not run the main experiment again.

A read-only audit independently generated the schedule set using event positions. It confirmed 54 numeric settings, 60 schedules, and 3,240 unique input worlds. It checked 19,440 unique world/rule outcomes and 85,536 transitions. Before-state continuity, report values, duplicate labels, terminal status, local balance, and the single B decision matched the saved data. The audit recalculated all case scores, maximum values, and first-bad events. All 30 summary rows, six paired comparisons, and 12 first adverse examples matched. This is a check of saved evidence, not another trial.

The plan and main-source hashes match their freeze records. The plan was frozen before implementation, and the main source was frozen before its first run. Two full main runs completed without a main-source correction. All seven deterministic output files match byte for byte. The gzip data also match exactly.

## Model and interpretation

The model starts after all provider use has occurred. Actual A use is fixed at z. The controller does not receive z until the terminal report T. This distinction is maintained in the implementation and report. No live-provider exposure or future-use forecast is measured.

Progress P and terminal T have different IDs even when x=z. Repeated copies preserve both ID and content. All rules retain a terminal flag once T arrives. LastValue can still lower the booked amount after T. Thus a terminal status check and a correct amount check are separate conditions.

The six rules match the frozen plan. Main code uses event updates; the independent specification uses formulas over received prefixes. Both retain the same initial reservation, numeric settings, report contracts, and B admission test. The adapter compares full records rather than only headline counts. Each saved-run comparison covers 19,440 outcomes, 85,536 transitions, 209,952 state records, all decisions and scores, 30 summary rows, six paired comparisons, 48 named controls, and 12 first adverse examples. The state count includes repeated before/after records and is not a statistical sample count.

The independent specification was frozen before main-code or main-result access. Its author sent expected totals after that freeze and before main execution. The main implementation was already written and did not change in response. The report states this order. This is separate implementation from one shared model, not fully blind interpretation. A shared model error remains possible.

## Claim checks

Each rule has 3,240 worlds. The report values match the saved results:

| Rule | Actual overrun | Final overcount | Final undercount | Refusal after sufficient final evidence | B admitted |
| --- | ---: | ---: | ---: | ---: | ---: |
| AddEvery | 0 | 2,196 | 0 | 448 | 1,495 |
| DedupSum | 0 | 1,440 | 0 | 252 | 1,701 |
| LastValue | 112 | 0 | 720 | 0 | 2,065 |
| HighWaterEarly | 72 | 0 | 0 | 0 | 2,106 |
| HighWaterHeld | 0 | 0 | 0 | 0 | 1,953 |
| TerminalOnly | 0 | 0 | 0 | 0 | 1,953 |

All four hypotheses are supported within the declared corpus. H1 uses refusal after final evidence and a matched TerminalOnly decision. It does not classify all pre-T feasible refusals as mistakes. The two complete rules have 207 feasible refusals each, all before T.

The report correctly separates accounting error from budget safety. AddEvery and DedupSum cause no real overrun, but they have 1,661 and 690 local-deficit cases. These deficits can arise from excess booking. HighWaterEarly has exact final booking in every world, but 72 earlier unsafe admissions. LastValue has 1,056 coverage-gap cases, which are distinct from its 112 unsafe admissions. These measures can overlap and must not be added.

The three worked examples match the saved controls. The largest final additive overcount is six units. The largest actual overrun is two units. None of these counts is a provider or model error rate.

## Conditional arguments

For HighWaterHeld and TerminalOnly, total A accounting q+h equals R before T and z after T. R is at least z. Both therefore have the same available balance at D. Their atomic admission check preserves z+b<=C for every accepted B. Later deliveries do not change true A use or B use. This proves the stated safety and decision-equivalence claims under the model assumptions.

For AddEvery and DedupSum, q+h is at least R before T. After T, their sum includes z and adds only nonnegative values. They also cover true use. This explains their zero-overrun result without making final booking correct. The report does not infer an exact ledger from a safe upper bound.

The proof requires true reports, a correct cap, fixed job and counter identity, final evidence, and atomic local processing. The report does not extend the result to resets, corrections, conflicting reports, partial commits, or real services.

## Reproduction, resources, and review aid

The README commands match the supplied program interfaces. It states that an output directory must be empty or absent. It distinguishes a new main run, the independent enumeration, and comparisons against saved evidence. Environment metadata are outside the byte-equality test. The published package can omit the duplicate reproduced data while retaining the second run log and environment record.

The two main runs used Python 3.13.7 on macOS 26.7.2, arm64. Each used less than one CPU second and one wall second. Each deterministic result set used 996,223 bytes before environment metadata. These are below the declared limits. The CPU limit uses the Unix resource module; wall and storage checks are periodic. Windows was not tested. No model API, network call, random seed, or paid-compute step occurs inside the simulator.

The reviewer read the relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) for claims, limitations, assumptions, proof, reproducibility, experiment details, statistical treatment, resources, ethics, and rights. The checklist is a review aid. This is not a claim of NeurIPS approval or submission compliance.

Full enumeration makes sampling intervals unnecessary within this finite input space. It does not remove model uncertainty. There is no training split or learned model, so training leakage is not applicable. The report states the small scope and its designed schedule distribution.

## Disclosure and release limits

The contribution is a comparison artifact for established mechanisms. The report distinguishes official documentation, a preprint, a research report, and an open design proposal. It makes no unsupported priority or defect claim. The separate source review must confirm reference use against the checked originals before release.

The experiment uses invented integers and event names. It contains no account trial, person-level data, credential, copied source implementation, or source figure. The report identifies Codex generation and separate AI review. It does not claim human authorship, human review, peer review, affiliation, endorsement, or certification. It assigns no new license. The primary misuse risk is treating a simplified model as a deployment guarantee; the report explicitly limits that inference.

## Reviewed hashes

SHA-256 values at this review:

| File | SHA-256 |
| --- | --- |
| plan.md | 0058dfdedd935767a88381ffe8bc655fc2dbb536e25f0fa4f4d8a8748fcee097 |
| run_study.py | 702a57dbe625ff3076479aa4ee79853c3c26fb8e9204285e75be5bf4b1a3d6b2 |
| report.md | d57cb1e3bd2c46c7c461ce3c01c107339a282392418accc15e2785ad52be249b |
| README.md | aee3a4d8d568e177ef1f71ac626ffb1b625b452f5857ade5bf5501d30ed85186 |
| changes.md | daac72881bfe659169c80eb289f9c2e5d6a6365301044faf500f0d692fd29f70 |
| independent_spec.py | 13c219825ca9343074087f7390603cb95539aabd905443d64018fbe5454ec9cc |
| compare_independent.py | cb089cc2f57a187016a0c7eefa4d802a9c8b4e29715b4c55e1b6c57f1f3d62bf |
| check_reproduction.py | 8add5246ae5aea22a4da1407f726dc53bc636ac728b776b0b4a2addac0b2aa8b |

Exact deterministic evidence hashes are in reproduction.json and both independent comparison records. Remote publication verification is separate.
