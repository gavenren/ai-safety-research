# Reproduce the finite-retention retry audit

Read [report.md](report.md) for the question, results, and limits. All records and request schedules are synthetic. The programs make no network or account calls.

## Environment and commands

The calculation uses Python 3.13.7 and its standard library. No package installation, paid compute, or model inference is required. There is no randomness. Exact immutable Codex build information was unavailable. See [environment.json](environment.json).

Download this complete folder at one fixed Git commit. From the folder, run:

```sh
python3 -m unittest tests -v
python3 analyze.py --input-dir . --output-dir .
python3 independent_audit.py --input-dir . --output-dir . --compare-main .
```

All three commands must exit zero. Main output files are results.csv, paired_results.json, witnesses.json, summary.json, and traces.jsonl.gz. The summary must show 60 main settings, one stress setting, 128,520 main rows, 2,401 stress rows, 575,415 events, and 356 witnesses. All five planned hypotheses pass in this fixed corpus. Independent comparison must report no mismatch.

For a fresh reproduction, copy only analyze.py, tests.py, independent_audit.py, analysis_plan.md, config.json, and input_manifest.json into an empty folder. Run the three commands there. Compare the five main output files and the independent generated data files named in reproduction_check.json byte for byte. Logs can have different times. Gzip output uses a fixed timestamp and no stored filename. The frozen inputs must remain unchanged.

## File roles

- analysis_plan.md, config.json, input_manifest.json: frozen method, inputs, time, and hashes. This is a local freeze, not external preregistration.
- analyze.py, tests.py, test_log.txt, analysis_log.txt: event-queue calculation, tests, and logs.
- traces.jsonl.gz: complete assigned input and consumed events for every policy run.
- results.csv: exact aggregate outcomes and resource counts.
- paired_results.json: same-assignment comparisons with Permanent.
- witnesses.json: minimum examples under the frozen order: sends, arrivals, final event time, then the full three-code tuple.
- independent files: separate tick-loop calculation, controls, data comparisons, proofs, and review.
- derivations.md: analytic safety arguments, count identities, and worked cases.
- source_search.md, references.bib: queries, source dates, read scopes, and source-access limits.
- failed_checks.md, reproduction_check.json, review_checklist.md: retained errors, fresh-run check, and publication review.

## Trace schema

Each row identifies suite, retention T, actual delay bound D, declared delay bound B, spacing s, policy, and the three transport codes. Code 0 drops permanently. Code 1+2d delivers after d ticks with a lost reply. Code 2+2d delivers after d ticks with a visible success. Unused codes remain in the assignment but have no events.

Events are send, skip, and arrival. A receipt is part of an arrival event. An arrival records append, cache_hit, or reject_deadline. It also records whether an expired key was encountered, effect count, returned effect identifier, and success visibility. Each scheduled slot has a send or skip event, including slots considered after a receipt. The final event time includes these decisions. Effects are separately listed with their event indices.

The first receipt's time, effect ID, event index, and count are null when there is no receipt. Effect IDs are synthetic audit identifiers, not a real service's global count. All labels use the drained final state. A later event at the same tick counts as later. The five disjoint outcome labels are missed, unconfirmed_one, unconfirmed_duplicate, clean_confirmed, and false_exact_claim. The other labels overlap.

Main and stress remain separate. The stress bound is deliberately false. A false exact claim is the hypothetical inference from a success receipt to exactly one final effect; it does not mean a service reply was false. The rules are prescribed programs, not measured language-model behavior.

## Scope and rights

A stable key alone does not establish permanent receiver memory. Receiver cutoff needs atomic receiver enforcement. Delay margin needs a correct delay bound. The proofs do not transfer to a browser that lacks these capabilities.

Codex generated this package. Agent review is recorded. No human review or peer review is claimed. No external source text or source code is redistributed. No new reuse license is assigned.
