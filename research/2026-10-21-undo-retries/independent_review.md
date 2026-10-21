# Independent implementation record

Date: 2026-10-21.

A separate Codex agent wrote `independent.py` from `plan.md` and `config.json`. The agent did not read the main code or results before saving its implementation and hash. `independent_implementation.json` gives the saved time and input hashes. The implementation uses whole-field prefix equations. It does not use the main evaluator's slot transitions or pending flags.

The first run checked 2,924 cases and 20,468 outcomes. It passed nine hand controls, 29,240 inverse-field identities, and 2,924 atomic-inverse case checks. These checks concern this finite model only. They do not verify a website or an agent model.

The compare option checks all 21 fields in the same case and rule order. The observed comparison passed for all 20,468 rows and all 429,828 field values. There were no mismatches. `independent_comparison.json` records the result and file hashes. The implementation was unchanged from its saved hash.

```sh
python3 independent.py --out /tmp/undo-independent --compare results/outcomes.csv
```

The independent implementation does not emit a separate full trajectory. It verifies final states, durable flags, stopped flags, claims, classifications, application counts, value-change counts, repeats, and omissions. The main evaluator retains the full trajectories. Both programs use the same frozen plan and configuration. They can therefore share an error in those inputs. No human review occurred.
