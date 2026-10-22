# Separate review of the live gate study

Date: 2026-10-22. Result: **PASS within the stated evidence limits.**

A separate Codex agent reviewed the plan, both amendments, the frozen rules, the actual browser helpers, the public evidence, and the private source records. The reviewer wrote a separate evaluator after reading the submitted code and results. This was not a blinded or preregistered review. No human review or peer review occurred. The review made no account calls and changed no account data.

## Evidence and reproduction

The separate evaluator passed 1,266 comparisons. It checked 161 unique source references and their saved hashes. It checked the native folder identity, names, parent, dispatch sequence, gate state, guarded reads, and relevant saved times. It did not import the submitted rules or scorer. See `independent_review_audit.py` and `independent_review_audit.json`.

The documented public scorer ran successfully. Its result bytes match `live_results.json`. See `independent_reproduction.json` and `independent_reproduced_results.json`. This was a local score replay. It was not another production trial. The private-evidence evaluator needs the original parent workspace and its private records. It is not the public reproduction command.

The eight cases contain 40 boundaries and 32 browser rename dispatches. The local duplicate messages did not repeat provider writes. The records support these counts:

| Evidence set | Cases | Guarded reads | Unsafe permitted reads | Unnecessary refusals | Gates closed at the end |
|---|---:|---:|---:|---:|---:|
| All descriptive cases | 8 | 14 | 3 | 5 | 2 |
| Cases within the timing bound | 7 | 12 | 2 | 5 | 2 |
| Cases within the timing bound and with fresh full start metadata | 6 | 9 | 0 | 5 | 2 |

The lifecycle registry has no unsafe permitted read or unnecessary refusal in these selected cases. This is a result for the selected witnesses. It is not a population failure rate or a proof that the registry is always correct.

## Limits retained in the report

- G1 with the nonnegative count has one identity read at step 5 that took 52.773 seconds from the initial reload. This exceeds the 30-second bound. The descriptive result remains visible. The case is excluded from the timing subset. This interval is not a measurement of provider latency.
- The first Boolean case has setup metadata and fresh browser identity checks, but no fresh full connector read at its start. It is excluded from the six-case subset.
- Two earlier accessibility snapshots differ from the later DOM readings. The actual helper collected the snapshots in sequence. The later DOM records contain the native row identifiers. The evaluator uses these later records. It does not treat the two views as simultaneous.
- The records do not prove the exact number of internal read attempts under the two-inspection limit. The report does not claim that every frozen procedure check passed.
- The local gate controls a cooperating reader. It is not a native Drive lock or an atomic provider transaction. The two folder fixtures were reused.

## Source and publication checks

The reviewer reopened [Google Drive help](https://support.google.com/drive/answer/2375091?hl=en) and checked its narrow use for folder operations. The reviewer used the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) as a guide for claims, limits, reproduction, and ethics. This is not NeurIPS approval or a certification.

An exact-value scan tested 131 private values against 25 public text files. It found no match. See `independent_privacy.json`. This bounded check does not prove that every possible secret is absent. The final publication selection and manifest must include only public files.

No material error was found in the scored results or their stated limits. Cleanup and remote publication were outside this review. They need separate evidence. The final integration must replace pending-review text and refresh the package manifest after it adds this review.
