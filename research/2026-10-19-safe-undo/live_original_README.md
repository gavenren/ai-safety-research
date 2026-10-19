# Repeat the safe undo study

Read [report.md](report.md) for the question, results and limits. The original simulation and the later production website tests are separate parts of this study. The live trials execute prescribed rules; they do not measure general model skill.

## Synthetic study requirements

Python 3.13.7 was used with its standard library. No package install, paid service, credential or random seed is needed. See [environment.json](environment.json). Other Python versions have not been validated; gzip bytes can depend on the implementation version.

## Synthetic study commands

Run these commands from this folder, one at a time. Stop if any command exits with an error.

```sh
python3 -m unittest tests -v
python3 analyze.py --input-dir . --output-dir .
python3 independent_audit.py --input-dir . --output-dir .
python3 compare_results.py --input-dir . --output-dir .
```

The first command runs nine main test methods. The next command checks frozen input hashes and enumerates every history. The independent program performs its own controls and malformed-input tests. The last command compares the two implementations. It is a schema adapter and checker, not a third model.

To use a clean directory, copy analysis_plan.md, config.json, input_manifest.json, analyze.py, tests.py, independent_audit.py and compare_results.py into an empty folder. Run the same commands there. Compare the generated files listed below with the published files. The saved [reproduction receipt](reproduction_check.json) records a clean local rerun.

## Synthetic study files

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

## Reading the synthetic results

The main table uses length three, with 500 histories per rule. Count units are histories, not distinct products, people, or natural failures. No-set means the command word contains neither set0 nor set1. Complete means the rule states that it has reached its target. It does not mean merely that a write API returned success.

Clean completion, false confirmation, unresolved and abstain-correct partition all histories. Wrong change, collateral change and new damage can overlap with these groups. Do not add them as separate error counts.

The observation-group key is [length, initial x, initial y, current x, current y, x revision count]. Target strings encode complete [x,y] values. Minimum pairs use the first two distinct targets in history order. A revision counts every x command, including a same-value assignment.

The provenance bit is trusted operation history supplied by the model. It is not inferred from field equality. Its complete access is a stronger assumption than the other rules receive.

## Review and rights

Codex generated the study and files. Separate agents checked the sources, results and proofs. No human or peer review occurred. No third-party code, private account identifiers, unrelated account content or source PDF is included. No new license is assigned. Follow the repository research protocol before any new publication.

## Production website extension

This extension used Google Calendar and Notion in connected production accounts. It has 48 planned core assignments, 43 valid core results, five unknown results, and four valid diagnostics. See the live section in report.md. The data are selected controlled cases, not a population sample.

### Repeat the saved analysis

Python 3.13.7 and Node v24.14.1 were used. No added library is needed. Run these commands from the package folder. They read the saved public extracts and do not access or change an account.

```sh
python3 -m unittest live_tests -v
python3 live_analyze.py --input-dir . --output-dir .
node live_rule_replay.mjs . .
python3 live_independent_selftest.py --package . --trials live_trials.jsonl --output live_independent_self_checks.json
python3 live_independent_audit.py --package . --trials live_trials.jsonl --output live_independent_results.json
python3 live_compare.py --main live_results.json --independent live_independent_results.json --output live_comparison.json
```

For a clean replay, copy this package into a separate empty directory, then run the same commands. The live reproduction receipt records the actual clean replay and output comparisons. It is separate from the original simulation receipt.

### Read the live files

- live_plan.md, live_assignments.json, live_input_manifest.json: prospective question, hypotheses, assignments, seed, evidence gates and frozen hashes.
- live_rules.js: the actual fixed decision function. It receives current fields and the permitted test log; no reference target is an input.
- live_trials.jsonl: all 52 terminal rows with selected saved fields, decisions, unknown cases and cleanup evidence. Each valid record has a stable alias. Calendar final cleanup updates retain cleanup_original and cleanup_adjudication.
- live_evidence.jsonl: selected action metadata and field extracts from the complete private logs. Whole DOM snapshots and private screenshots are omitted. Original line numbers resolve early reused Calendar IDs.
- live_extraction.json, live_cleanup.json: source hashes, privacy scope, cleanup findings and the possible unsaved Calendar draft limit. Cleanup labels are separate from scored outcomes. no_saved_record_found does not establish that no save was dispatched.
- live_results.json, live_rule_replay.json: primary grades and replay of all 43 observed fixed-rule decisions.
- live_independent_audit.py, live_independent_selftest.py, live_compare.py: separate evidence validation, rule model, malformed-record tests and exact comparison.
- live_independent_results.json, live_comparison.json, live_independent_review.md: independent result checks and their limits.
- live_helper_manifest.json and the live_calendar_* / live_notion_* helper files: actual generated browser helper versions. Account-name literals are replaced with <ACCOUNT_DISPLAY_NAME>; the manifest gives original and public hashes.
- live_source_notes.md, live_design_review.md, live_changes_and_failures.md: source read scopes, design review, failed actions and prospective helper corrections.
- live_environment.json, live_primary_log.json, live_reproduction_check.json, live_reproduction_log.json, live_review_checklist.md, live_release_check.json: measured environment and release checks.
- synthetic_preservation_check.json: verification of all 31 original release-receipt entries, using preserved originals where the combined text changed.

### Run a new browser study

A new study needs authorized test accounts and the supported Codex browser tools. The helper factories receive browser tab handles and local logging functions. This package does not include the browser client library or credentials. The live plan and runner instructions specify the fields, saved-state checks and action limits. Read the private-site interface first and test the mappings in an unscored preflight. Use a new run token, a new private Notion parent and fresh temporary records. Save a new plan before execution. Native website behavior can change.

Keep complete raw observations privately. The extraction commands below require your own private account-name list in private_redactions.json, with schema {"account_names": ["your test account display name"]}. The directory must contain calendar/ and notion/ trial logs and cleanup summaries. The supplied public package cannot reconstruct the omitted private DOM or screenshots.

```sh
python3 live_extract.py --private-dir PRIVATE_RUN_DIRECTORY --output-dir PUBLIC_OUTPUT_DIRECTORY
python3 live_export_helpers.py --private-dir PRIVATE_RUN_DIRECTORY --output-dir PUBLIC_OUTPUT_DIRECTORY
```

These two commands transform local files only. Inspect every public output before publication. They do not establish that a browser trial occurred; that requires the saved source evidence and review.

The original report, README and bibliography remain in synthetic_report_original.md, synthetic_README_original.md and synthetic_references_original.bib. The original review receipts describe that historical release at commit 699177c2926f94f6fc601d8a10bfcb811d1bc221. In particular, old report, README and bibliography hashes bind those originals. They do not bind the later combined report. Live checks are recorded separately.
