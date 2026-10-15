# Independent final review

Date: 2026-10-15. Status: PASS.

A separate Codex agent made this review. No human or external peer review occurred. This review does not establish publication or deployment approval.

## Scope and reproduction

The reviewer read the repository protocol, report, saved plan, configuration, input manifest, code, derivations, result files, method review, source review, source record, README, and environment records. The plan and configuration hashes match the manifest. No study input or method was changed during this review.

The reviewer copied the study into a fresh folder and ran the documented commands:

```sh
python3 analyze.py > run_log.txt
python3 validate.py > validation_log.txt
```

These commands used CPython 3.14.7 on Darwin and the standard library. The optional figure command used the existing CPython 3.13.7 environment with Matplotlib 3.10.7 and NumPy 2.5.3:

```sh
python3 plot.py > plot_log.txt
```

All commands completed with exit code zero. Eight output files and all three logs matched byte for byte. The outputs include the three CSV tables, result summary, core environment, validation results, plot environment, and figure. [reproduction_check.json](reproduction_check.json) records the hashes. No package installation, model experiment, paid API call, or paid compute occurred.

## Numerical and proof checks

The reviewer checked all eight boundary-table rows, five example-table rows, and six control-outcome rows against the saved data. The conditional workload, no-launch probability, abstract values, and other result statements agree. The separate validator passes all 1,296 result rows and 1,536 policy branches. Its checks use different binomial, root, and integer-length calculations. Its largest saved-number difference is below 5.0e-31.

The probability mixture correctly averages over calibration outcomes. The one-sided binomial limit has the stated coverage. On the event that the lower limit does not exceed true sensitivity, each launched batch has a false-declaration probability at most .025. Bounding the complementary event by .025 gives the stated unconditional limit of .049375. This argument needs independent controls and targets, correct control labels, sensitivity transfer, fixed rates, and the fixed policy. It is not a guarantee for each observed control count.

The cap removes a whole batch when its required length exceeds the limit. Code, policy tables, proof, and report all use this rule. No batch is shortened to the cap. The two baselines do not need a positive calibration count. A skipped batch makes no declaration. The resulting launch, acceptance, and workload definitions are consistent.

The report does not treat low error as evidence of useful performance. It states the 0.856% launch probability and 0.2546% true-declaration probability in the capped example. It distinguishes unconditional from conditional workload and keeps control counts separate. It does not claim an optimized error split, control count, complete power curve, or practical cost estimate.

The reviewer inspected the corrected figure. Labels and data are legible. The workload axis includes the full range and starts at zero. The report states that lines only connect three chosen designs. It also explains which series uses the cap. No visual error remains from the recorded clipping issue.

## Sources, claims, and rights

The reviewer reopened [Feng et al. v1](https://arxiv.org/html/2601.20913v1), including Theorem 5.1 and the limitations. The report correctly notes the approximation term and the small-sample concern. It does not claim to test their full method.

The reviewer reopened [Cai et al. v1](https://arxiv.org/html/2011.14423v1), section 2.1. The report correctly describes the independent binomial samples and error allocation. It cites the read preprint version.

The reviewer reopened the [NIST exact binomial equations](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). The report distinguishes the source's two-sided equations from its own one-sided derivation. The source record states reading limits and access failures.

The report claims a bounded numerical comparison using established methods. It makes no claim of a new estimator, new theorem, first discovery, measured AI safety, or full literature coverage. The report discloses synthetic inputs, AI generation, and no human review. No source paper, external dataset, copied figure, private record, credential, or new license was found in the reviewed package.

The relevant [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) items were checked for claims, assumptions, proof, reproduction, uncertainty, limitations, compute, impacts, rights, and AI use. This is a review aid only. It does not establish conference approval or submission compliance.

## Outcome and remaining release steps

No material issue or new failure was found in this final review. The earlier summary, version-label, and figure repairs remain recorded in failed_checks.md. The work is suitable for publication as a synthetic probability audit with its stated limits.

The main agent must still complete release checks and verify the remote files after publication. This PASS result alone is not proof that the files are on GitHub.
