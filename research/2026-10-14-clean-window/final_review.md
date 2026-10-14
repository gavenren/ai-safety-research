# Separate final review

Date: 2026-10-14. Reviewer: a separate Codex agent.

Result: **PASS for the stated mathematical audit.** No material error was found. This is an agent check. No human or external peer review occurred. Remote publication must still be checked after upload.

## Scope and fixed report

The reviewer read the repository protocol, report, saved plan, configuration, derivations, analysis code, independent validator, results, source record, source review, method review, reproduction instructions, and review records. The report checked here has SHA256:

```
36dbe2a30578ca26f8fa919b9ede55b9503201e9027ff15b37664415572af0d0
```

The review covers the fixed synthetic model. It does not establish the assumptions for an AI system. The report clearly states that no AI model was tested.

## Fresh reproduction

The reviewer copied the package into a new local folder and ran the documented sequence:

```sh
python3 analyze.py
python3 validate.py
python3 plot.py
```

The first two commands used CPython 3.13.7 with the standard library. The figure command used the existing CPython 3.13.7 environment with Matplotlib 3.10.7 and NumPy 2.5.3. No package was installed. All three commands returned exit code 0 with no standard-error output.

The following eight files match the supplied files byte for byte:

- results_grid.csv
- results_calibration.csv
- results_trajectory.csv
- results_summary.json
- environment.json
- validation_results.json
- figure_windows.png
- plot_environment.json

[reproduction_check.json](reproduction_check.json) gives the commands, hashes, and comparisons. The saved plan and configuration hashes passed both program checks.

## Mathematical and numerical checks

The first-hit argument is valid under the stated independent, constant-rate model. A first clean run ending at trial n requires no earlier run, a failure at n-k, and k clean final trials. This gives the reported recurrence. The coefficient expression follows from the stated generating function. It supplies a different calculation from the time recurrence.

The event nesting, separate-block formula, and union bound are correct. The report does not treat overlapping windows as independent. The shared-uniform argument correctly makes p0 the worst case for the strict declaration p<p0. The event argument also proves monotonicity in window length and horizon. Candidate and predecessor checks establish the minimum length within the stated rule family. The unlimited-horizon limit is valid for every fixed finite k and 0<=p<1.

The fresh validator passed all 36 grid conditions, 12 length calibrations, and 5,982 time rows. It also passed 198 exhaustive small cases and 84 exact state cases. The largest saved-probability difference was below 5.0e-31. No statistical significance or sampling interval is inferred from these deterministic calculations.

The reviewer separately parsed all 12 report table rows. All 96 cells match the saved inputs and results, including rounding. Twelve numerical percentages in the prose also match. The stated row counts, control counts, and nine primary conditions match the output files.

In the selected 1% example, the checks confirm 4.9536% for one window and 80.4935% for any rolling window within 2,990 tests. Length 616 gives 4.9943%; length 615 gives 5.0459%. The difference establishes the stated integer threshold. The separate-block and union-bound examples also match.

The reviewer inspected the generated PNG. The axes, units, titles, markers, legend, and caption are clear. Nothing is clipped. The plotted values match the saved design rows. The report explains that the corrected series uses a different fixed length at each horizon.

## Sources and contribution

The reviewer reopened the following original sources on 2026-10-14:

- [Littlewood and Wright](https://openaccess.city.ac.uk/id/eprint/1614/): source metadata and manuscript sections 1 through the start of section 2. The earlier warning about repeated tests of an unchanged faulty system is explicit. The report attributes this warning and does not claim to reproduce the Bayesian policy.
- [Oh, Park, and Kim, v1](https://arxiv.org/html/2210.08797v1): metadata, abstract, introduction, and section 2.1.1. The report correctly treats run probabilities as established theory. The final reviewer did not check the later dependent-trial results.
- [Howard and colleagues, v9](https://arxiv.org/pdf/1810.08240v9): abstract, introduction, properties P1–P4, and the start of section 1.1. These support the distinction between fixed-time and time-uniform inference. The full proofs were not checked by this final reviewer.
- [Yu and colleagues, v1](https://arxiv.org/html/2601.22446v1): metadata, abstract, introduction, section 2, and the start of section 3. These support the narrow context claim about online selection, partial feedback, and loss relative to a thinking model. No experimental performance claim is used as evidence for this audit.
- [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist): relevant claims, limits, proof, and reproduction guidance. The checklist is a review aid only.

The source agent's wider search and reading limits are recorded in [source_search.md](source_search.md). The report identifies preprints and avoids a claim that all cited papers were read in full. The contribution is a bounded calculation table and its reproducible checks. It is not presented as a new theorem or the first warning about repeated testing. The limited search cannot prove that the exact table is new.

## Limits, rights, and release status

The report states the important assumptions: independent trials, fixed p, an unchanged system, correct immediate labels, and a horizon fixed before outcomes. It states that acceptance below the target, practical efficiency, repairs, drift, dependent trials, and imperfect labels were not assessed. It does not turn a 5% false-declaration limit into a posterior safety probability or deployment approval.

The package contains synthetic inputs and new calculations. The inspected text contains no copied source passage, private test record, credential, harmful prompt, or attack procedure. It retains source attribution and assigns no new license. No third-party paper or dataset is included. These are bounded content checks, not a guarantee that a text scanner can detect every secret or rights issue.

The relevant checklist items have adequate support for this audit: claims match the method; assumptions and proofs are present; results can be reproduced; limits and ethical issues are stated; AI use and the lack of human review are clear.

No correction was required by this final review. The main agent must complete the final package hash and link checks, update the repository index, and verify the remote files before it reports publication as complete.
