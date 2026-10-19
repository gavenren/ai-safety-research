# Repeat the safe undo study

Read [report.md](report.md) for the question, results and limits. This is a synthetic study of fixed rules. No real website or model is tested.

## Requirements

Python 3.13.7 was used with its standard library. No package install, paid service, credential or random seed is needed. See [environment.json](environment.json). Other Python versions have not been validated; gzip bytes can depend on the implementation version.

## Commands

Run these commands from this folder, one at a time. Stop if any command exits with an error.

```sh
python3 -m unittest tests -v
python3 analyze.py --input-dir . --output-dir .
python3 independent_audit.py --input-dir . --output-dir .
python3 compare_results.py --input-dir . --output-dir .
```

The first command runs nine main test methods. The next command checks frozen input hashes and enumerates every history. The independent program performs its own controls and malformed-input tests. The last command compares the two implementations. It is a schema adapter and checker, not a third model.

To use a clean directory, copy analysis_plan.md, config.json, input_manifest.json, analyze.py, tests.py, independent_audit.py and compare_results.py into an empty folder. Run the same commands there. Compare the generated files listed below with the published files. The saved [reproduction receipt](reproduction_check.json) records a clean local rerun.

## Files

- analysis_plan.md, config.json, input_manifest.json: frozen design, inputs and hashes.
- analyze.py, tests.py: main model and semantic tests.
- results.csv: 102 nonempty aggregate rows, split by word length, set/no-set subgroup and rule. Empty has-set groups at length zero are omitted.
- traces.jsonl.gz: 15,624 complete histories in plan order. Each line has actual/reference trajectories and all six outcomes. The first actual state is after the agent action; the first reference state is the original record.
- paired_results.json: 30 comparisons against Provenance control, using all histories at each length.
- observation_groups.json: 364 groups defined by equal observations; 140 contain different required targets. Each ambiguous group has a minimum pair.
- witnesses.json: 17 first failing or abstaining examples under the frozen order.
- summary.json: totals, hypotheses, observation counts and the first ambiguous pair.
- independent_audit.py: separately written implementation.
- independent_cases.jsonl.gz: complete independent histories and outcomes.
- independent_results.json: independent aggregates, paired groups, observation groups and witnesses. It includes six explicit zero-count aggregate rows and subgroup paired rows, so its row counts differ from the main display.
- independent_checks.json: independent count controls, direct checks, input rejection and hashes.
- compare_results.py, comparison.json: exact schema comparison and receipt.
- derivations.md, independent_review.md: conditional proofs and independent review.
- source_search.md, references.bib, source_claim_review.md: source queries, dates, read scope, attribution and claim review.
- analysis_log.txt, test_log.txt, reproduction_log.txt, reproduction_check.json: actual command logs and reproduction evidence.
- failed_checks.md: failed checks and changes retained before release.
- review_checklist.md, release_check.json: publication checks. A local pass is not proof of remote publication.

## Reading the results

The main table uses length three, with 500 histories per rule. Count units are histories, not distinct products, people, or natural failures. No-set means the command word contains neither set0 nor set1. Complete means the rule states that it has reached its target. It does not mean merely that a write API returned success.

Clean completion, false confirmation, unresolved and abstain-correct partition all histories. Wrong change, collateral change and new damage can overlap with these groups. Do not add them as separate error counts.

The observation-group key is [length, initial x, initial y, current x, current y, x revision count]. Target strings encode complete [x,y] values. Minimum pairs use the first two distinct targets in history order. A revision counts every x command, including a same-value assignment.

The provenance bit is trusted operation history supplied by the model. It is not inferred from field equality. Its complete access is a stronger assumption than the other rules receive.

## Review and rights

Codex generated the study and files. Separate agents checked the sources, results and proofs. No human or peer review occurred. No third-party code, private account data or source PDF is included. No new license is assigned. Follow the repository research protocol before any new publication.
