# Separate agent review

Date: 2026-10-22, America/Toronto.

Result: No material error found in the declared finite model, recorded traces, or report claims. The package can proceed to the coordinating agent's final publication checks. This is an agent review, not human review, external peer review, certification, or verification of a production system.

## Reviewer separation

The reviewer was the separate Codex agent `study_safe_order`. The reviewer did not write this study's plan, main program, raw results, or report. The reviewer first read only `plan.md`, `config.json`, and the raw row schema supplied by the author. It then wrote `separate_audit.py` and saved its hash in `separate_audit_freeze.json`. Only after that freeze did it audit the raw data and inspect `study.py` and `report.md`.

The evaluator derives states from event positions. It generates the expected schedule set by inserting C and O into the fixed control chain. It does not import or call the study program. It uses the same stated model assumptions, so separation does not remove the risk of a common specification error. No third full study run was made.

## Audit result

The command was:

```sh
python3 separate_audit.py
```

It can be run from the package directory. It audits the existing raw file and writes `separate_audit_result.json`.

- All 4,284 expected schedule/rule records are present exactly once. There are no missing or extra keys.
- All 51,408 top-level comparisons pass. These include each complete event trace, check state, pre-effect state, acceptance, effect order, final state, and every recorded error flag.
- All 56 CSV rows and every combined rule total match counts from the raw records.
- Every saved witness is the first stale case for its rule in the recorded deterministic order.
- Frozen plan/config/source hashes and both executed program hashes match the present files.
- The documented comparison program checked the saved repeat directory. All six deterministic files match byte for byte and match the recorded SHA-256 hashes.
- All local links in the report and README resolve in the workspace.

The separately written evaluator hash is `f97dd16dab862a0f1a741d1d2d78fe03c787919abe6df33ae61c4110f3ac6757`. The raw results hash is `774ef4df1faaaeee2aaa68690ef1ac126b5186af3061cdfa97f02118dbd2c06d`. The evaluator was not changed after its freeze.

## Method and claim review

The seven rules implement the frozen definitions. The schedule condition Rn before N makes N the final-generation control. The cached check cannot authorize a later old effect under the intended contract. The high-water rule is explicitly weaker than a cancellation barrier: it learns a new token only from an accepted newer write. Its measured failures do not refute its token-order guarantee. The two zero-count rules assume stronger receiver capabilities, as the report states.

The combinatorial count is correct. The control chain followed by N has 2n+1 events. C and O occupy two ordered positions among 2n+3 positions, giving choose(2n+3,2). The eight counts sum to 612. Exactly one schedule per n puts O before A1, so there are eight valid old-action schedules and 604 stale-attempt schedules per rule. This matches the report denominators.

The frozen plan, pre-run source record, implementation freeze, raw evidence, reproduction, and limits are supplied. The reported packaging error and checklist-reading timing correction remain visible. They do not alter the frozen model or measured results. No adverse case was discarded.

## Primary-source checks

The reviewer reopened the following primary sources on 2026-10-22:

- [Burrows, Chubby](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf): recipient validation of lock generations in Section 2.4 and the sequencer API in Section 2.6 support the report's limited prior-work statement.
- [Kleppmann, 2016](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html): the check/write gap and receiver token-order sections support the stated distinction.
- [Zhu and Wang, preprint v1](https://arxiv.org/html/2609.21284v1): abstract, Sections 4.4 and 6.2 distinguish the authority cut from the sink fence and describe stale-worker tests. The report correctly limits its own model and does not claim to have checked that source's implementation or proofs.

The sources are identified as prior work. The report makes no global novelty claim or claim to test those systems. The code and data are synthetic. No copied source passage, credential, personal record, third-party artifact, or harmful production instruction was found in the reviewed package. This is a bounded content check, not a general security scan.

## Final editorial action

The author can now replace the prospective statement that separate review is required with the actual outcome and a link to this file. The report must continue to state that no human review occurred. No numerical, model, or source correction is required by this review.
