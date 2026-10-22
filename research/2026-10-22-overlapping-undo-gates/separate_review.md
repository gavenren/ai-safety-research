# Separate agent review

Date: 2026-10-22, America/Toronto.

Result: No material error found in the declared model, saved evidence, proof, or report claims. The package can proceed to the coordinating agent's final publication checks. This is agent review, not human review, external peer review, or certification.

## Separation and method

The separate Codex reviewer `study_safe_order` did not write the study's plan, code, results, or report. It first read only `plan.md`, `config.json`, and the raw row schema supplied by the author. It wrote `separate_audit.py` and saved the source hash before inspecting `study.py`, raw data, summaries, or the report. `separate_audit_freeze.json` records this sequence.

The audit generates permitted histories through permutation filtering. It calculates each expected state from request prefixes and first-event positions. It does not call or import the study program. The count uses a reflected prefix sum. Active-ID membership uses each ID's last request. Registry state uses the first close and first release positions. Both implementations share the declared model assumptions; separate authorship cannot remove a common specification error.

No third full experiment run occurred. The reviewer audited saved files and compared the two existing run directories.

## Executed checks

From the package folder:

```sh
python3 separate_audit.py
```

The audit checks the existing raw file and saves `separate_audit_result.json`.

- All 1,603 expected histories are present exactly once, with no missing or extra history keys.
- All 11,417 event points match. This includes the complete state and scores for all four rules, or 45,668 rule/event points.
- Every saved history score, duplicate count, overlap label, and consecutive history ID matches the separate calculation.
- Primary, one-operation, duplicate-count, and work-overlap totals match sums from the raw records.
- The three report witnesses, histories 9, 90, and 267, match the saved event lists and states.
- Initial and corrected plan hashes match the retained files. The present program hash matches the pre-run record and both run receipts.
- All six deterministic files in the saved second run match the published-package candidates byte for byte and match the saved hashes.
- Report and README local links resolve. The primary result tables match the audited totals.

Audit source hash: `93f68865929118e14e336791b89abbc9b22bbd69c82500b87fcc51cc3c557b5e`.

Raw results hash: `a47f6856c94d839b62079b2fa6f2f381d93cd621022ceb32d1f73774e47384f4`.

The audit source was unchanged after its freeze. No difference or audit failure occurred.

## Proof and interpretation

The lifecycle argument is correct under the stated event constraints. Each ID starts absent, becomes active at its first close, and becomes completed at its first release. All duplicate requests preserve the appropriate active or completed state. The retained registry therefore matches the declared work intervals. This argument depends on no ID reuse, no removal of completed entries, no release before the first close, and atomic updates. The report states these conditions.

The active set cannot remove an unfinished ID because that ID has no release before completion. It can add a completed ID after a late close. The report correctly treats this as unnecessary refusal rather than an unsafe opening. It also correctly separates gate correctness from mutual exclusion and correctness of the protected writes.

The local-order count correction occurred before implementation. Both the initial plan and the revised freeze remain available. The correction changes the analytic check, not the specified history set. No post-result method change or excluded adverse result was found.

## Sources and claim support

The reviewer reopened the four technical primary sources on 2026-10-22:

- [Shahare, Chabbi, and Hegde, arXiv v1](https://arxiv.org/html/2304.11983v1): Section 3.1 describes unsafe Boolean release and an ownership check. The report correctly distinguishes a lock from its shared reader gate.
- [Redis documentation](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/): the single-instance release section requires the stored ownership value to match. No Redis performance or correctness experiment is claimed.
- [Amazon Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/): the late-request section describes retained request identity after resource removal. The note cites this as prior design guidance.
- [Atomix v2](https://arxiv.org/html/2602.14849v2): Section 2.2 describes transaction states, terminal outcomes, seal checks, and runtime-owned concurrency control. The note does not claim to implement Atomix.

The report does not use source measurements as its own evidence. It makes no global novelty claim. Source titles, author lists, and version labels match the accessed originals. Full papers, source programs, figures, and external data are not redistributed.

## Limits and final editorial action

The report clearly states its complete finite corpus, one duplicate per request, two operations, full gate compliance, lack of real users or providers, and no confidence-interval or population-rate claim. The unsafe/open and unnecessary/closed counts are not combined into a single success measure. No credential, private record, copied long passage, or actionable production exploit was found in the reviewed package. This is a bounded content check, not a security certification.

The author can replace the prospective separate-review wording with the actual result and link this file. Keep the statement that no human review occurred. No numerical, code, model, or source correction is required by this review.
