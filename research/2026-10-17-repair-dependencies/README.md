# Reproduce the repair-rule regression audit

Read [report.md](report.md) for the question, results, and limits. This package uses synthetic four-bit records. It does not run a browser or call a user account, model API, or network service.

## Environment and commands

The run used Python 3.13.7 with the standard library on macOS. No package installation is needed. There is no randomness. Exact immutable Codex model-build information was unavailable. See [environment.json](environment.json).

Download this folder at one fixed Git commit. From the folder, run:

```sh
python3 -m unittest tests -v
python3 analyze.py --input-dir . --output-dir .
python3 independent_audit.py --input-dir . --output-dir . --compare-main .
```

All three commands must exit zero. Main outputs are `results.csv`, `paired_results.json`, `witnesses.json`, `summary.json`, and `traces.jsonl.gz`. The summary must show 9 settings, 54 aggregate rows, 9,864 scenario assignments, 59,184 policy assignments, and 88 witnesses. All five planned hypotheses pass in this fixed model.

The independent procedure is documented in `independent_review.md`. Its program is `independent_audit.py`. The independent comparison reads the main files as data; it must not import the main program. The comparison checks each policy-scenario result against separate reconstruction.

For a fresh main reproduction, copy `analyze.py`, `tests.py`, `analysis_plan.md`, `config.json`, and `input_manifest.json` into an empty folder, then run the first two commands above. To repeat the independent check in that folder, also copy `independent_audit.py` and run the third command. Compare the five generated data files byte for byte. Gzip output has a fixed timestamp and no source filename. The frozen files must remain unchanged. Logs can contain different execution times. The reproduction receipt records the actual checks.

## File roles

- `analysis_plan.md`, `config.json`, `input_manifest.json`: plan, fixed model inputs, freeze time, and hashes. This is a local freeze, not external preregistration.
- `analyze.py`, `tests.py`, `test_log.txt`, `analysis_log.txt`: main calculation, semantic checks, and logs.
- `results.csv`: exact outcome and resource counts for each setting and rule.
- `paired_results.json`: same-input comparisons and the two H5 subsets.
- `traces.jsonl.gz`: one JSON object per policy assignment, including the complete input program and every consumed event.
- `witnesses.json`: minimum consumed-write examples for each nonempty bad outcome; ties use rounds, initial tuple, then integer gap words.
- `summary.json`: corpus sizes and planned hypothesis decisions.
- `independent*`: separate calculation, comparisons, proofs, controls, and review records.
- `derivations.md`: conditional proofs and exact count identities.
- `source_search.md`, `references.bib`: source queries, dates, access limits, read scopes, and metadata.
- `failed_checks.md`, `reproduction_check.json`, `review_checklist.md`: retained failures, fresh-copy check, and publication review.

## Data schema

`K` is the round budget. `b` is the maximum background writes in one gap. State order is `(A,X,Y,U)`. A gap word uses indices `0=A`, `1=X`, `2=U`; those are not indices into the four-field state. The full program has K words. Unused words remain in the input but do not run.

Each trace records `decision`, `rounds`, `attempts`, `rejections`, `harmless_rejections`, `background_writes`, five bad-outcome labels, final state, final revision, and event details. Decisions are `success`, `read_denied`, or `exhausted`. Success means a write occurred, not that its effect was correct. `before_effect` is null if no write succeeded. Permission and source violations use the successful commit's pre-effect state. `collateral_fields` lists fields outside Y whose values the agent actually changed.

`results.csv` sums binary outcome flags and event counters. Semantic invalidity is the union of permission and source violations. Bad union adds collateral overwrite. Do not add overlapping outcomes as separate failures. `assignments` is the exact setting denominator, not a sample size for a production probability.

## Scope and rights

This is a fixed regression corpus. Policies may stop at different times and consume different prefixes. Distinct unused suffixes retain multiplicity. The result is not a live account benchmark, a causal speed estimate, or a guarantee for an interface without atomic guards. The source and permission contract concerns current values; a binding past revocation requires a different model.

Codex generated this package. Separate agent review is recorded; no human or peer review is claimed. All inputs are synthetic. No external source text or code is redistributed. No new reuse license is assigned.
