# Final report review

Date: October 16, 2026 (America/Toronto).
Status: PASS for the report and README hashes below.
Reviewer: separate Codex agent. No human or peer review is claimed.

## Scope

I checked the final report and README against the frozen plan, the complete independent calculation, the saved main results, and the derivations. I checked each numeric claim in the abstract, table, results, validation, and reproduction instructions. I also ran all four documented commands in a fresh folder. The command logs and output hashes are in `reviewed_commands.json`.

All ten generated main and independent data files reproduced byte for byte. The main semantic tests passed all eight test methods. The independent comparison again passed all 108 policy rows, 13,744 terminal counts, 108 stage rows, and 71 full witness paths. The separate main reproduction receipt also records success.

## Findings

No material error remains in the reviewed report or README.

- The full displayed six-policy table matches the independent result for two fields, two passes, and at most two writes per gap.
- The 18 settings, 108 policy rows, 13,744 terminal rows, 71 witnesses, and largest history count of 1,102,867,934,792 are correct.
- Values and both modulo rules each have a no-common-target outcome in seven settings. Partial revision has this outcome in three settings, all with three fields.
- The partial-revision example has 340 no-common-target histories out of 501,988,136 histories in its stated setting.
- Full revision rejects some correct final records in all 12 settings that permit writes. The six zero-write settings are clean controls.
- The four planned hypotheses are supported. The report uses the planned H3 scope: at least one modulo setting and one partial-revision setting with a counterexample.
- The minimum-write result of 2, 6, and 10 follows the stated two-field proof and matches the saved witnesses. It is not applied to the distinct wrong-at-decision outcome.
- The report states the atomic write and revision assumptions, fresh authoritative reads, fixed identity, common decision point, and stronger final-snapshot interface. It does not claim persistence after a later write.
- The report states that the result is synthetic. It does not claim live provider tests, a production failure rate, causal improvement from more scans, or a new snapshot algorithm.
- The README gives the four required scripts, the three frozen plan/source files, the input manifest, and the four successful commands. It distinguishes five generated main data files from five independent data files.

The author corrected the draft's six-main-file wording, made the copied manifest explicit, aligned the H3 wording with the frozen plan, and marked the content-validator conclusion as an inference. These changes did not change the experiment or its results. No frozen input was edited.

## Limits of this review

This review checks the stated finite model, numeric claims, proof scope, and reproducibility instructions. The main and independent calculations share the same plan, so agreement cannot establish that the plan models a live service correctly. I used the saved source-review notes for reference context. I did not re-read all external references in this final review. The separate source review supplies the original-source read scope.

The report retains the Codex role and the absence of human or peer review. The review is not a certification. It does not verify a future GitHub upload. Publication and remote-file verification remain separate checks.

## Reviewed file hashes

These hashes identify the reviewed versions. If the report or README changes, review the changed text and update this receipt.

| File | SHA-256 |
| --- | --- |
| `report.md` | `6781f3b41d347f61433f44444b059e2cda4caaacfffd20203fe4309af0572c35` |
| `README.md` | `0f7f124c5e8cc850589a6624ca312b376e42f0b2bbe5aace617ebd7bc0c08420` |
| `analysis_plan.md` | `4624ae4b04f9d3d26682e5b08d88ad1f0ee47d6bdc79e4b7b46c4f374ca3279d` |
| `config.json` | `936494f659fa4a21b174fba0fab08b0a793978a92ce8c759a1e95c3103f6a616` |
| `input_manifest.json` | `a8f1149beb8e613dc96a896400ea593f42e0122d4cf361b392724478d544e8c8` |
| `results.csv` | `fdb43a553c4d4fb996b75790ac621f60b4b991b6aa976c57fdcf8bb9b6faaacb` |
| `summary.json` | `3f3ad172251114382540eba56404d41c82ac2787633e54ffa530fde294548f07` |
| `terminal_counts.jsonl.gz` | `5f87dca4127678d273003e7ccf690b7cde18dd508c7810bb2d6743e8cd657665` |
| `stage_totals.json` | `03b8e041c65a0e6677e24653729bfe5f519aba8ef30ccf8df65da179c19f1cfc` |
| `witnesses.json` | `a5f9e8ff8784f878d884a4b47c2a34146438c6350b2c6b1093f5bab89f65c3ff` |
| `derivations.md` | `ccd8c077d14297ffdc29077f39f5b27e941e04d261aef32cd68e0ffd8d556a3d` |
| `independent_comparison.json` | `0fad825ad22b5d52f1665992e58f1b86bb020e9d8e186669d88bdfb2077799bc` |
| `reviewed_commands.json` | `43b48357fff7b5596571e35e090f5928628ce4cc30187dd8e666139a67267417` |
| `reproduction_check.json` | `bb4a5c4281a3df0dd03ff25540647910939ba9bda551e4373eafba5242b04601` |
