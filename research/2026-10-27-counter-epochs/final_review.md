# Final method, result, and report review

Date: 2026-10-27.

Reviewer: a separate Codex agent. This is an AI review. No human or external peer review occurred.

Result: no material method, result, or report error remains within the scope below. The review supports release of this bounded simulation artifact after the separate final package checks. It does not establish research priority, production safety, or remote publication.

## Scope and files

The reviewer read the plan, main code, design review, separate formula specification, comparison adapter, both comparison records, both run records, result summaries, controls, retained examples, reproduction record, report, README, change record, and independent review. The reviewer also read the final source-review record and the official NeurIPS checklist page.

The reviewer did not rerun the main simulation. The reviewer ran `check_reproduction.py` on the two existing result folders. This command passed. The reviewer also checked the saved result hashes and file sizes, the environment-record copy, the frozen-source hashes, and relative links in the report and README.

Reviewed report SHA-256:

`6c3e43dcd1f15665c7f2815fb79b7f8bb2e26bc48c2a93bc707b3944d6c6b3ad`

This report keeps the source claims checked by the source reviewer. Its later change adds the completed independent comparison counts. The reference file remains unchanged. Source identity and source support rely on that separate original-source check; this reviewer did not repeat all source reads.

## Frozen records

All current sources match their saved freezes.

| File | SHA-256 |
| --- | --- |
| plan.md | `3a5e4cf870e4c2aa800441ab97fc9750f1ce2758cb1ad683f11284ada411f75d` |
| run_study.py | `6295cfe08c8ebcc13797664b84037a98ce47bda18c986c2f4beb0371b2c77354` |
| independent_spec.py | `2b3a0b635aba311e366426f3d803266b2072e58d2352664375f844dc8d56cadf` |
| compare_independent.py | `06ebec615ced5f54149efe081a28d561aba81f75875d6e09170dbccd8a6b9965` |

## Method and result checks

The corpus has 36 value settings and 144 schedules for each setting. Each rule receives 5,184 histories and 31,104 alternative admission branches. The six branches for one history are alternatives, not consecutive jobs. Summary groups overlap and must not be added together.

The common duplicate check discards exact repeated report IDs before any state change. Each rule agrees with its frozen definition. The admission measures use true completed use as ground truth. The missing-final control is separate from the primary totals and refuses admission under a false closure condition.

The separate prefix specification uses a different calculation from the main state updates. Static review found no missing numeric decision field in the comparison. Both saved comparisons pass all 151,200 state records and 155,520 admission branches. They also check inputs, replay flags, 30 summary rows, five matched-rule tables, 35 control rows, ten first adverse examples, and the checks file.

The seven scientific files from the two main runs have identical bytes. Their sizes and hashes agree with `reproduction.json`. Only the environment records differ. The separate copy of the second environment record is exact. The reported times and output sizes match the two run records.

The report table, source-order split, error bounds, hidden-reset example, first ArrivalDrop example, and missing-final example agree with the saved data. The conditional arguments state the assumptions needed for their conclusions. In particular, the no-decrease case is exact when the old total is zero.

## Reproduction and inventory

The README commands match the programs' arguments. They use new result folders and preserve the saved evidence. A comparison failure stops with a nonzero exit code. Successful comparison output sets `passed` to `true`. The README explains the environment exception and possible compression-byte differences across versions.

The platform requirement is now explicit: the main script uses the Unix `resource` module. macOS or another Unix-like system is required; native Windows is unsupported. This resolved the review's only reproduction wording issue.

All listed scientific files, source files, freeze records, comparison records, and run records are present locally. The second full result folder can be excluded from publication because the exact-byte check passed and one complete raw result set remains. Local cache files are not part of the intended package. The final package manifest and broad privacy/link scan are separate main-agent checks after this file is saved.

One earlier prose issue is also resolved. The independent review now states that the rule's booked total after the first two source reports is z0. It no longer says that the two report values themselves sum to z0. No code or result changed.

## NeurIPS checklist review aid

The reviewer used the relevant topics from the [official checklist](https://neurips.cc/public/guides/PaperChecklist). This is not approval, peer review, or a claim of submission compliance.

| Topic | Review result |
| --- | --- |
| Claims and limits | Pass for the finite model. No production or global novelty claim. |
| Assumptions and arguments | Pass. Identity, truth, disjoint use, and closure are explicit. |
| Reproduction and assets | Pass locally. Code, inputs, traces, commands, and checks are supplied. Remote availability needs a separate check. |
| Experimental detail | Pass. Rules, orderings, controls, measures, and denominators are stated. |
| Statistical evidence | No confidence interval is supplied. Exact enumeration has no population inference. |
| Compute | Times, system, output size, and bounds are recorded. Peak memory was not measured. |
| Ethics and impacts | Invented inputs; no account trial or human participants. Misuse of synthetic counts is discussed. |
| Rights | No copied dataset or external implementation is included. No new license is assigned. Source checks are separately recorded. |
| AI roles | Codex roles are disclosed. No human review is claimed. |

## Remaining limits

This review does not validate a live provider, website, billing service, or computer-use agent. It does not establish a real closure signal or trusted incarnation identity. No work is admitted while reports arrive. Small invented input ranges and artificial schedule weights limit the result. Separate AI implementations can share a model error.

No account action, publication action, or remote verification was performed by this reviewer. This review file is not evidence that GitHub contains the final package. The main agent must check that separately.
