# Independent review

Date: October 18, 2026.

Status: PASS. The model, evidence, derivations, reproduction commands, final report, and README pass this review within the limits below.

## Scope and independence

A separate Codex agent read only the frozen plan, config, and input manifest before it implemented and ran `independent_audit.py`. The program uses an integer-tick loop. It does not use an event heap. The reviewer did not read or import the main program or its tests. After the independent outputs were complete, the reviewer read the main output data to add a field-name conversion and a comparison. The main programs were later copied and executed in a clean temporary folder. Their code was not read by this reviewer.

This is an AI-agent check, not human review or peer review. No real account, website, service, or provider behavior was tested.

## Checks and findings

- All 130,921 complete policy rows match, including all 575,415 events and 3,534,867 scalar values.
- All 427 aggregate rows and 427 paired rows match.
- All 356 minimum witnesses match, including their complete traces and the frozen order for ties.
- All summary counts and all five hypothesis decisions match.
- The independent program has 26 named control groups and rejects 34 malformed configuration objects. One control group has 1,029 extra runs for correct or larger delay bounds. These extra checks are not part of the main or stress corpus counts.
- Closed-form counts for No retry and Permanent agree in every setting. The five-part outcome partition, event counts, matched schedules, and label implications pass.
- The four safe-rule proofs are valid under the declared receiver atomicity and timing assumptions. `derivations.md` and `independent_proofs.md` agree on these assumptions and results.
- A fresh folder received only the three programs and three frozen input files. The three reproduction commands passed. All ten generated data and comparison files match the published candidates byte for byte. The receipt is in `independent_reproduction.json`.

No numerical or model error was found in the main outputs.

The report preserves the distinction between the main grid and the broken-bound stress set. All displayed primary counts, paired costs, stress counts, and corpus totals agree with the independent results. The minimum `(7,2,0)` example and the cached-reply `(1,6,5)` example follow the exact event order. The report states that these are synthetic prescribed rules, not measured website or language-model failure rates. It states the stronger assumptions of the safe rules, the limited contribution, and the absence of human or peer review.

The main test author confirmed 22 malformed configurations: 14 missing required keys and eight invalid replacements. The independent reviewer checked that the frozen config has 14 required keys, but did not read the main test code. The eight replacements were slots set to true; retention ticks set to `[0]`; delay bounds set to `[true]`; spacings set to `[2,1]`; an empty policy list; drain-after-receipt set to integer 1; primary settings with missing fields; and an empty stress object. The clean execution log confirms that all 11 main test methods pass.

This review did not independently check every external reference or provider contract. A separate source review covers those claims. The code comparison establishes agreement with this model, not adequacy of the model for a real service.

## Changes and failed checks

Before enumeration, the lead agent clarified that each scheduled slot has a send or skip event. This includes slots after a first receipt. The last event time includes these decisions. This clarification is recorded in the independent receipt and proof file. No frozen input was changed.

After the first independent run, extra invariant assertions and closed-form checks were added. They passed and did not change any computed result.

The first output-comparison attempt failed on a text label in the comparison adapter. The main output calls the Receiver cutoff send-denial reason `send_cutoff`. The adapter first called it `receiver_cutoff`. The adapter was corrected to use the main output label. The model transition rules and computed outcomes did not change. The full comparison then passed.

The final text review found that the cached-reply example did not name its applicable rules. The report now names Stable key and Send cutoff. It also says that the initial request arrives before `T` only if delivered, and that each later arrival finds the first record. The report uses “correct bound” instead of “honest bound.” These corrections do not change a method, input, or result. The final report and README hashes below bind the resolved review.

## Evidence hashes

The hashes below bind this review to the checked evidence and final text.

| File | SHA-256 |
| --- | --- |
| `report.md` | `d29a0a893b918012ec39293ce52e79a06642c639ba81b71aedc8d574004522a4` |
| `README.md` | `31ef7f1fe540dcd823e9d45158b20e7a63b10c40e19cd014669e9041878a42a7` |
| `analysis_plan.md` | `221e7665b46898382f325fce76779c8e2a91c12051227685bb5a7d3b8e76cf7e` |
| `config.json` | `d8160d49b9d68e919903d504df51b8c2d5673658cf5fd734176f23b43200d577` |
| `input_manifest.json` | `d3635b9d019b3a32dbe0391ef0f3939e300a07c554e2342e1dd47bf6944bb345` |
| `independent_audit.py` | `c3e6aae7aa65d0e033ec818e7e0cf07029260210a13680447288d97dcb0acb5d` |
| `independent_proofs.md` | `b1c6231b75781c1e46b2291497f27bb07c5e7933dee267d57b05a73805dc4092` |
| `independent_comparison.json` | `29cd43c6c3a04eaaf119d877e3f50cbebeefe8a9831f6c70bb1e277d70391232` |
| `independent_reproduction.json` | `081a73a44e386ded426869d0f378ff50ef5d4979573252a9b6f8788ffe9cf863` |
| `results.csv` | `c28764dc3f722916968c445b4c62e7266a00a13f4f92718c664065e124c2002f` |
| `paired_results.json` | `52fb2eac2e06cb847a908bba4b25438123c0111a27700dba0ffaaa703d0387b3` |
| `witnesses.json` | `4b5a1bb6c0644d78e6b3b633a4be6003d95226466ccc7eadfab1145ae4417e8c` |
| `summary.json` | `60a2af57065bcd4016c25d1dd61bf1f2251178a5d90be4fb1dbd3771db5b3ea5` |
| `traces.jsonl.gz` | `f8f6f31720185d78fd18759449705e12aeb02473e76d14ca656c302fc8d091d5` |
| `derivations.md` | `038fef3484d781069a4dbfd7c20943fa0d347fdc92a579b95f1fe67639eaece1` |
