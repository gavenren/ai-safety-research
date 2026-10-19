# Independent model review

Date: 2026-10-19.

Status: PASS. The independent model, exact comparison, proofs, final report, and clean reproduction passed.

Codex made this independent implementation. It is an agent check. No human or peer review occurred. The check uses synthetic histories only. It does not test a browser, an account, or a service.

## Independence and scope

Before implementation, the reviewer read only the frozen plan, configuration, input manifest, repository protocol, and the implementation skill. The reviewer did not read or import the main analysis or its tests. The first independent run finished before the main results were read. The model code and its output were then fixed for comparison.

The actual world uses direct integer updates. The reference world uses a separate table of tuple functions. The reference world does not call the actual-world mutation function. It starts without the agent action and executes the same fixed commands. Both worlds save each state.

The code is `independent_audit.py`. Full case evidence is in `independent_cases.jsonl.gz`. Each line gives one history, both state trajectories, the pre-undo record, the target, the revision count, the provenance bit, and all six rule outcomes. `independent_results.json` has all group results and minimum examples. `independent_checks.json` records input hashes and checks.

## Executed checks

Run this command in the study folder:

```sh
python3 independent_audit.py --input-dir . --output-dir .
```

The command passed. Python 3.13.7 and the standard library were used. No random sample, training, or paid compute was used.

- 15,624 unique histories and 93,744 rule outcomes were checked.
- 89,844 actual/reference state pairs were checked.
- 108 aggregate rows and 90 paired rows were saved. These include zero-count with-set rows at length zero.
- All 364 observation groups were saved. Of these, 140 groups have more than one reference target.
- Ten groups of direct checks passed. They cover all five one-command words, all four initial records without background commands, same-value assignment, add/subtract cancellation, assignment followed by addition, and all y-only lengths.
- All 33 malformed configurations were rejected. These include absent keys, null values, wrong types, booleans used as integers, wrong corpus values, list-order changes, extra keys, and an invalid top-level type.
- The invariant for the two worlds, the outcome partition, field preservation, no-change abstention, and the exact rule conditions were checked for every case.
- A clean temporary directory run reproduced all three generated independent files byte for byte. Only the independent code and the three frozen input files were copied to that directory.

All six planned hypotheses passed in the independent results. These exact counts describe the finite corpus. They are not estimates of real-world probabilities.

## Count controls

For length L there are four initial records and five choices per command. Thus the total is N = 4 times 5^L. A word without a set has only three choices per command. Its count is A = 4 times 3^L. The with-set count is N minus A.

The following identities passed separately for each length from zero to five:

- Subtract has A clean completions. Its N minus A remaining cases are false confirmations and new damage.
- Provenance control has N clean completions. It changes the record in exactly A cases.
- Revision guard has four clean completions: the y-only word for each initial record. It has N minus A correct abstentions and A minus four unresolved cases. It has no false confirmation or wrong change.
- Full restore changes y in 2 times (5^L minus 3^L) cases. This follows from the number of words with an odd number of y flips.

Summing the six lengths gives 15,624 histories, 1,456 without a set, and 14,168 with a set. These identities check the enumeration independently of individual saved examples.

## Conditional proof

Consider only the x part of a fixed background word. It defines a function f(x) = a times x plus b, where a is either zero or one. Addition and subtraction preserve a. Any set makes a zero, and later commands keep it zero. Thus a is one exactly when the word has no set command.

Let x0 be the initial value. The reference value is f(x0). The actual value before undo is f(x0 + 1). Their difference is a. The y values are equal because the agent does not change y and both worlds execute the same flips.

Provenance control has the correct a value under the stated trusted-history assumption. It subtracts one when a is one. It does nothing when a is zero. It therefore reaches the complete reference record in both cases. This proof covers arbitrary finite words in the stated alphabet, not only the enumerated lengths. It does not cover state-dependent background decisions, missing history, external effects, or concurrent writes during undo.

Subtract always removes one. Its final x difference from the reference is a minus one. It is correct for every no-set word and wrong for every with-set word. In the latter case, the pre-undo record was already correct, so subtraction makes new damage.

Revision guard completes only when there are no background x commands. In that case, the x part of the word is the identity function. Restoring x0 is correct and preserves all y flips. If the guard abstains, it changes nothing. Thus it makes no wrong change or false confirmation under a complete, non-reused revision count.

When Value guard completes, the actual x is x0 + 1. With a equal to one, the reference x is x0 and restoration is correct. With a equal to zero, the reference x equals the actual x. Restoration then makes new damage. This explains why its false-confirmation, wrong-change, and new-damage counts agree in the corpus.

## Information limit

The minimum ambiguous pair starts at (x, y) = (0, 0). The agent changes x to one. The background then executes either `sub1` or `set0`.

Both histories have length one, current record (0, 0), and one background x revision. Their initial records are also equal. In the reference world without the agent, `sub1` gives (-1, 0), while `set0` gives (0, 0).

A deterministic rule that sees only the planned group key sees the same input in these two histories. It must choose the same action, status, and final record. It cannot report completion with the correct record in both histories because the two targets differ. A rule can abstain instead. A rule with complete operation history has more information, so this limit does not apply to that rule.

The complete enumeration records 140 such ambiguous groups and a minimum pair in each one. This argument depends on the stated observation restriction. It does not establish that all forms of undo are impossible.

## Failures and changes

No independent model test failed before the first saved run. No model change was made to fit the main results. A repository status check found that the task folder is not a Git checkout; this did not affect the model or the output files.

## First-run hashes

These hashes were saved before the main results were read:

| File | SHA-256 |
| --- | --- |
| independent_audit.py | 28163f8205412aec05317938b45e584b7fd855db7d7eced5c8ee9acd775267b4 |
| independent_cases.jsonl.gz | 45fb8712a7efeb25255d721343918b4d72107f6f0674bcb5001583ceed8f0614 |
| independent_results.json | 92b11919749912a0d5000b3c20594fbd7d16f0f6bd87c698acc7e90ccec21171 |
| independent_checks.json | 97e228866efb71df67800aa182240ef811e5fc05b012b82915360e70e8cfd239 |

## Exact comparison with the main results

After the independent code and outputs were fixed, the reviewer read the main output schemas. The reviewer wrote `compare_results.py` as a schema adapter. It does not call either model. The adapter compares complete saved content, not only selected reported counts.

The comparison passed on its first run. It checked 1,886,271 scalar values, with exact value and type checks. Its scope covers all 15,624 histories and all 93,744 outcomes, both complete trajectories, every revision and provenance step, 102 main aggregate rows, all 30 main paired rows, all 364 observation groups, all 140 minimum ambiguity pairs, all 17 minimum failure examples, and every main summary field. See `comparison.json` for the receipt and input hashes.

The independent output includes six zero-count aggregate rows at length zero and 60 additional subgroup paired rows. The main display omits these. The adapter records this difference. It converts case identifiers, field names, record shapes and complete/abstain forms. It uses the frozen history order for every minimum example. No model logic or independent output changed to make the comparison pass.

## Full clean reproduction and final text check

The reviewer copied only the three frozen input files and four code files to an empty temporary directory. All four README commands ran there and exited with code zero. All ten generated result files matched the package byte for byte. The command logs, Python version, exit codes, times and file hashes are in `reproduction_log.txt` and `reproduction_check.json`.

The reviewer then read the final report, README, derivations, and failure record. The tables, total counts, examples, count identities, proof assumptions and reproduction commands agree with the checked data. The report correctly states the stronger information given to the provenance control. It restricts its claims to fixed commands and the stated observation set. It does not claim real-site measurements, natural failure rates, human review or novelty priority. The initially reported group count of 464 was corrected to 364 before this final check and is recorded in the failure file.

The central-coefficient formula in the derivations is also correct. In a no-set word that returns x to its post-agent value, j additions need j subtractions and L minus 2j y flips. Summing the corresponding multinomial coefficients gives the stated count. Multiplication by four gives the clean Value guard count.

This review checks the model, numerical claims, proof, limits and commands. The separate source reviewer checks the external references. Publication and remote verification remain separate root-agent steps.

The final text and code reviewed have these SHA-256 hashes:

| File | SHA-256 |
| --- | --- |
| report.md | 932067e82ccf33b41afcd1a8c328d5795915addfac0ce18069ff8a4b37c5128e |
| README.md | f97206e4542167171ee9dc131078e2450fd90412835000c68d18f84feb2a27b5 |
| derivations.md | 0632974d0bce623590f30a64a1845dd97743d9aff283b9da0af67087f370b6e5 |
| analyze.py | de72ddcbef2b67ed3824cf3179798f5a0d9d569bf80cb260c72b0a2805ea255e |
| tests.py | 84874026d18684ec164feee65f70525e2d6c7be6fecf8d0efa0de84ddf798507 |
| compare_results.py | 05c55203c5d2c9fdf4eb76ca03bec8265abe0d0487450b991c260dbdaf73777f |
| comparison.json | dd9344a626b039137f997d22e55b2960704d103563886b303395827e677e3682 |
| reproduction_check.json | 4e58641d80f4b0568facbe23f1e49c5796601f56142a8bb8cce75804c75347fa |
| reproduction_log.txt | c25865784d3f11ae3ad48eaa3d683d7acb3ace5d9884550c3ef00c27136ef8ad |
