# Separate review of the live undo-order study

Date: 2026-10-22. Result: **PASS within the stated evidence limits.**

A separate Codex agent reviewed the plan, both amendments, the frozen rules, the actual browser helpers, the public evidence, and the private source records. The reviewer wrote a separate evaluator after reading the submitted code and results. This was not a blinded or preregistered review. No human review or peer review occurred. The review made no account calls and changed no account data.

## Evidence and reproduction

The separate evaluator passed 408 comparisons. It checked 90 unique source references and their saved hashes. It derived the event identity from each actual editor URL. It checked field values, dispatch order, final connector fields, and the fixed event settings. It found controller paths with a separate recursive search. It did not import the submitted rules or scorer. See `independent_review_audit.py` and `independent_review_audit.json`.

The documented public scorer ran successfully. Its result bytes match `live_results.json`. See `independent_reproduction.json` and `independent_reproduced_results.json`. This was a local score replay. It was not another production trial. The private-evidence evaluator needs the original parent workspace and its private records. It is not the public reproduction command.

The six cases use six temporary Calendar events. The records contain 16 browser field changes and 22 editor observations. They support these paths:

| Condition | Rule | Saved path | Target reached | All states valid |
|---|---|---|---|---|
| Witness | Fixed | 111, 101, 001, 000 | Yes | No |
| Witness | Greedy | 111, 101 | No | Yes |
| Witness | Complete | 111, 011, 010, 000 | Yes | Yes |
| All states valid | Fixed | 111, 101, 001, 000 | Yes | Yes |
| All states valid | Greedy | 111, 101, 001, 000 | Yes | Yes |
| All states valid | Complete | 111, 101, 001, 000 | Yes | Yes |

Five cases reached the target. Four completed with valid states throughout. One reached the target through an invalid state. One stopped before completion. The validity conditions were supplied by the researcher. Calendar did not enforce these synthetic conditions. The results are not evidence of a native Calendar defect.

## Limits retained in the report

- Full connector baselines came from one batch before the cases. Each case also has a fresh browser baseline. The report does not call the connector baseline immediate for each case.
- The W-G final connector read occurred after the save and before the retained final DOM read. There is one retained successful final DOM read. The review does not infer another successful read or an overwritten W-G read.
- The runner disclosed an overwritten W-F pre-baseline placeholder. Its former contents cannot be reconstructed from the retained files. This is separate from the verified W-F baseline and all scored post-save reads.
- The records do not contain an exact initial reopen time for every read. Post-save intervals include scheduling time and do not measure provider latency. The 30-second uncertain-read rule cannot be checked by treating every save as a failed-read start.
- Fields were read in sequence. The study does not prove an atomic snapshot. Some server fields were not exposed. The report limits its final checks to the exposed fields.
- A public direct-ID flag is false where the raw DOM object has no direct `id` property. The separate URL identity flag is true. This missing property is not an observed event-identity mismatch.

## Source and publication checks

The reviewer reopened [Google Calendar help](https://support.google.com/calendar/answer/72143?hl=en) for edit and save behavior, and the [Calendar event reference](https://developers.google.com/workspace/calendar/api/v3/reference/events) for the fields used in the checks. The reviewer used the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) as a guide for claims, limits, reproduction, and ethics. This is not NeurIPS approval or a certification.

An exact-value scan tested 131 private values against 24 public text files. It found no match. See `independent_privacy.json`. This bounded check does not prove that every possible secret is absent. The final publication selection and manifest must include only public files.

No material error was found in the scored results or their stated limits. Cleanup and remote publication were outside this review. They need separate evidence. The final integration must replace pending-review text and refresh the package manifest after it adds this review.
