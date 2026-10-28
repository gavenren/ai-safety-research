# Initial design review

Date: 2026-10-28. Reviewer: a separate Codex agent. This is an AI review. No human review occurred.

Reviewed plan SHA-256: `3778f43c2c4edc030354091c46ea647acad325d39c31b086e40ef88bf4db7c05`.

The reviewer read only the written plan and prior/source material for this design check. The reviewer did not read main code or results and did not run the experiment.

## Result

No material ambiguity blocks implementation under the stated contract. The cap request is conditional. A refusal leaves the old cap active. This resolves the main claim risk: refusal of an impossible lower cap is not successful activation of that cap.

The five rules have distinct conditions. B always checks current covered use against the current cap in its own atomic transaction. Therefore a failure can be assigned to the cap-change path without an incomplete B guard. The experiment deliberately ends R before U. It does not ask SQLite to upgrade an old read snapshot.

The old job's settlement moves at most its held amount into spent use and releases the rest. It can expose actual excess after an earlier incorrect cap reduction, but it does not increase covered use. Settlement must remain observable when a prior rule is already unsafe.

## Interpretation requirements

- Use the applied cap for breach scores. Record requested-cap feasibility separately.
- Keep actual spent use and possible unresolved use separate. A case can have an invalid covered total while its eventual spent total fits.
- Every committed U, S, or B effect changes the revision, including settlement with an unchanged covered total. VersionedCover can therefore refuse a feasible change. That is its stated conservative behavior.
- AtomicCover must recompute even when R would have refused. Otherwise it would silently become a different rule.
- A refused operation must leave all ledger fields unchanged. R changes no ledger field.
- All input branches remain in the results. A does not reveal its eventual x before S.
- The schedule groups overlap. Do not add their counts as independent cases.
- First adverse examples use the declared order. They are not guaranteed globally smallest examples.

The saved controls are suitable for these distinctions. Reopened rows, full state records, SQL records, independent formulas, and two deterministic runs can detect implementation disagreement. They cannot validate shared assumptions about real providers.

## Limits

The corpus is a finite test of local application rules with one hold and one new job. It has no real agent action, external effect, price change, cancellation, crash, provider failure, or parallel stress load. Exact counts have no population failure-rate meaning. The study is a comparison artifact for known mechanisms. A final method and result review remains necessary after execution.
