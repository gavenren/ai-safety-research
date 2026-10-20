# Undo with missing action records

Read [report.md](report.md) for the question, method, results, and limits. This is an exact synthetic study. It contains no new website trials.

## Repeat the analysis

Use Python 3.11 or later. Only the standard library is needed. The recorded version is in [environment.json](environment.json). No credentials, network calls, GPU, model API, paid compute, or random seed are needed.

From this study folder:

```sh
python3 reproduce.py
```

This command copies the required source files to a temporary directory, runs the procedure there, compares the deterministic results with the published results, and saves `reproduction_check.json`. It does not alter published result files. Runtime records contain timestamps and can differ on each run.

To regenerate the local `results/` files directly, run:

```sh
python3 analyze.py
python3 independent_check.py
```

## Files and data

- `plan.md`, `config.json`, `plan_freeze.json`: inputs, hypotheses, decisions, and pre-execution hashes.
- `analyze.py`: the main enumeration. It indexes all candidate words by their distinct visible subsequences.
- `independent_check.py`: a separately written check. It filters full words with a subsequence scan and uses an independent target formula.
- `results/cases.jsonl`: 44,444 raw cases. Each line has initial fields, full word, mask, visible word, current fields, true target, and missing count.
- `results/decisions.jsonl`: one row per unique observation. It has candidate count, distinct targets, and the four observation-based decisions. The full-history control is computed separately from each full case.
- `results/summary.csv` and `results/summary.json`: outcome counts by bound setting, length, and missing count. `L4_missing` includes L=4 and k>0.
- `results/witnesses.json`: first examples under the frozen order.
- `results/controls.json` and `results/output_hashes.json`: control checks and deterministic output hashes.
- `analysis_log.json`, `independent_run.log`, `results/independent_check.json`, `reproduction_check.json`: execution and check receipts.
- `source_search.md`, `references.bib`, `review_checklist.md`, `independent_review.md`, and `changes_and_failures.md`: source and release checks.

JSONL means one JSON object per line. A mask is a set of bits: bit i=1 retains command i. A candidate word can have several embeddings of the visible word, but is counted once. Distinct masks for an actual word remain separate cases. The bound is an upper bound, not an exact missing count.

The main code checks the frozen command set and length limits. This is a fixed regression artifact, not a general configuration framework. The candidate search includes length-five histories in the loose setting. Do not limit it to the length-four corpus when repeating the study.

## Data and rights

All case records are generated from the stated model. There is no external dataset. Source papers are cited, not redistributed. No new license is assigned; the repository owner has not selected one.

Codex generated the study. No human review or external peer review occurred.
