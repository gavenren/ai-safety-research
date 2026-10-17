# Six repair rules under concurrent edits: an exact regression audit

Date: October 17, 2026 (America/Toronto)  
Study type: exhaustive synthetic test set  
Review: separate agent checks; no human review or peer review

## Abstract

A repair can pass a fresh version check and still apply an old decision. We test six fixed repair rules on a four-field record. The task is to set one field from a current source value, with current permission, and preserve other fields. The test set includes 9,864 scenario assignments across nine settings, giving 59,184 policy assignments. In the two-attempt, two-write-per-gap setting, a rule that refreshes the version but retains its old decision succeeds in 100 of 676 assignments. In 32 of those successes, the effect violates the task contract. Replanning with a complete version check and a complete atomic dependency check have zero bad effects in the stated model. A guard that omits permission has 192 permission violations in that setting. The contribution is a reproducible regression corpus and exact comparisons. The underlying concurrency principles are prior work. These counts are not website or model failure rates.

## Research question and safety relevance

Which repair rules can overwrite unrelated fields, apply an invalid effect, or reject a valid effect after another writer changes the record?

A **repair** changes a saved record to meet a task. A **revision** is a value that tracks changes. A **dependency** is an input on which a decision depends. A **guard** is a condition that must pass before a write. A **regression corpus** is a fixed set of cases used to detect a known error when code changes.

An agent can retain the right record identity and still make an unsafe repair. For example, its source value or permission can change after planning. Checking only the payload or the latest version can miss the relation between the decision and its inputs.

The [October 15 account paper](../2026-10-15-computer-use-retries/report.md) tested same-record field correction. The [October 16 study](../2026-10-16-field-snapshot/report.md) tested separate reads without a repair effect. The present study adds explicit write and retry rules. It does not change earlier trial scores or claim another live account experiment.

## Related work and contribution

PlanFence v2 already distinguishes fresh memory from a current derivation. Its second validation uses a replacement plan, not a new head attached to the old plan. Its guarantee ends at owner responses and does not make a later external effect atomic. Our deliberately stale rule is not an implementation or test of PlanFence. [Chen et al., 2026, Sections 3–4 and Appendix C.3](https://arxiv.org/html/2609.03340v2)

CoAgent studies concurrent agents and repair of dependent actions. Its assumptions include correct identification and repair of affected premises. We replace that semantic judgment with one exact binary function. We therefore do not measure an agent's ability to replan. [Lyu et al., 2026, Sections 4–5](https://arxiv.org/html/2606.15376v1)

Khan studies concurrency anomalies, including a read whose use becomes stale before a recorded commit. The trace-level results have stated interleaving assumptions; deterministic generation affects their operational interpretation. Our current-value contract differs from a predicate that records an intervening change to a recorded input, even when a value returns. [Khan, 2026, Sections II-A–II-B, III-A, and IV-E](https://arxiv.org/html/2606.17182v1)

These three papers are preprints. We read the sections listed in the source record. We did not independently verify these papers' code, proofs, or experimental results. The [search record](source_search.md) records queries, dates, read scopes, and an inaccessible full-text lead. The exact corpus, five error labels, paired controls, and minimum examples form the proposed artifact contribution. The search does not prove novelty. We claim no new concurrency algorithm, first discovery, or improvement over a named system.

## Method

The [plan](analysis_plan.md) and [configuration](config.json) were frozen before execution. [input_manifest.json](input_manifest.json) records their hashes and time. This is a local plan record, not an external preregistration. No frozen input changed.

One record has bits `(A,X,Y,U)`. `A=1` permits the task now. `X` is the source value, `Y` is the output field, and `U` is unrelated. The task is: set `Y` to the value of `X` immediately before the effect, only when `A=1`, while preserving `A`, `X`, and `U`. Permission is a modeled task condition. It is not a provider access-control test.

The four initial records use `A=1`, both values of `X` and `U`, and `Y=1-X`. A repair is initially needed. A background write flips `A`, `X`, or `U` and increases revision `V` by one. The write and revision change are atomic: they occur as one indivisible event. A return to earlier field values still advances `V`. There are no background writes to `Y`.

A round starts with a complete authoritative read. A rule can stop there if permission is absent. Otherwise, an assigned sequence of background writes occurs, followed by an atomic guard and effect. Rejection permits another round within budget. Success or read denial ends the policy. Unused input sequences do not run.

| Rule | Payload and check |
| --- | --- |
| Replace | One unconditional full-record replacement from the first read, with `Y=original X`. |
| Patch | One unconditional write of `Y=original X`; preserve other fields. |
| Refresh CAS | Read a fresh revision each round, but keep the original output value and original permission decision. Write `Y` if the revision still matches. |
| Replan CAS | Each round, check current permission and recompute `Y` from the read `X`. Require the read revision at commit. |
| Dependency guard | Replan each round. Atomically require both current `A` and `X` to match that read before writing `Y`. |
| Source-only guard | Same procedure, but omit `A` from the commit guard. Permission is checked only at the earlier read. |

**CAS** means compare-and-set: the comparison and write are one indivisible event. A browser check followed by a separate Save does not supply this capability. These are prescribed abstract rules, not measured model behaviors.

The attempt budget `K` is 1, 2, or 3. Each gap permits zero through `b` writes, with `b` equal to 0, 1, or 2. There are `q=1+3+...+3^b` possible ordered words per gap. Each setting contains all `4*q^K` assignments. All six rules receive each same input program on a separate state copy.

Policies can consume different prefixes and stop at different events. Assignments with different unused suffixes remain distinct. These multiplicities are part of the fixed corpus. There is no common wall-clock horizon or natural probability distribution. Counts across budgets are not a causal estimate of another retry's benefit.

## Measures and planned decisions

A successful effect has a **permission violation** if `A=0` immediately before commit. It has a **source violation** if its proposed `Y` differs from the pre-commit `X`. Their union is a **semantic violation**. A **collateral overwrite** changes `A`, `X`, or `U` through the agent's effect. The total bad-effect label is the union of semantic violation and collateral overwrite. These sets overlap and must not be added as disjoint counts.

The oracle uses the pre-effect record. A full replacement can restore an old `X` and then make the final `Y=X` look correct. That appearance does not erase the lost edit.

We also count successes, read denials, exhausted retries, commit attempts, rejected guards, and consumed background writes. A harmless rejection blocks a proposed `Y` that meets the current-value contract. It is not necessarily a defect in a system with stricter history requirements.

The five hypotheses require: an invalid refreshed-token effect only after a retry is available; zero bad effects for the two complete rules; a permission error from the incomplete guard; a collateral error avoided by Patch; and accepted dependency-guard cases where Replan CAS exhausts its budget. The last comparison has two predefined subsets: unrelated-only changes, and a dependency change that returns before the first effect. All negative settings remain in the results.

## Results

All five hypotheses hold in the finite corpus. There are nine settings, 54 aggregate policy rows, nine paired rows, and 88 minimum-write witnesses across five error labels. The largest setting has 8,788 assignments per policy. The full 59,184 policy traces are saved in [traces.jsonl.gz](traces.jsonl.gz).

The table gives the complete `K=2, b=2` setting. Each rule receives 676 assignments. Success means that a write occurred; it does not itself mean the write was valid.

| Rule | Successes | Semantic violations | Collateral overwrites | Read denials | Exhausted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Replace | 676 | 416 | 468 | 0 | 0 |
| Patch | 676 | 416 | 0 | 0 | 0 |
| Refresh CAS | 100 | 32 | 0 | 0 | 576 |
| Replan CAS | 80 | 0 | 0 | 260 | 336 |
| Dependency guard | 320 | 0 | 0 | 260 | 96 |
| Source-only guard | 512 | 192 | 0 | 104 | 60 |

Source: [results.csv](results.csv). Replace has 468 total bad-effect cases; 416 also have a semantic violation. Refresh CAS has 20 permission violations and 20 source violations, with eight cases in both sets. Source-only guard has no source violation; all 192 semantic violations concern permission.

A one-change example explains Refresh CAS. Start at `(1,0,1,0)`. The first read proposes `Y=0`. A background writer changes `X` to 1. The first revision check rejects the write. The second read obtains the new revision, but the rule keeps `Y=0`. No further change occurs. The second revision check passes and writes the wrong output. Before that write, `Y` already equaled the new `X`. The old decision makes the now correct record wrong.

A permission change gives a separate example. If `A` changes to 0 after the read, Source-only guard still accepts when `X` is unchanged. Its earlier permission check does not cover the effect time. Complete Dependency guard rejects that effect.

Replan CAS and complete Dependency guard have zero bad effects in every setting. All three zero-write settings are clean controls for all six rules. Refresh CAS has zero semantic violations in all one-attempt settings. The corpus therefore retains cases where a weaker rule is sufficient.

For `K=2,b=2`, Dependency guard succeeds in 240 same-input assignments where Replan CAS exhausts its budget. Of these, 16 contain only unrelated `U` changes in every gap. Another 32 contain an `A` or `X` change and return in the first gap, with permitted returns or unrelated changes later. The other 192 paired cases are outside these two subsets. For `K=3,b=2`, the corresponding counts are 2,064, 32, and 128; 1,904 are outside the subsets. See [paired_results.json](paired_results.json). These are different-policy event outcomes, not measured speed or population gains.

## Why the complete rules pass

For Replan CAS, each round derives its candidate from a read with `A=1`. Every background write increments a non-reused revision. A matching revision therefore implies no write since that read. Permission and source are unchanged at commit. The rule writes only `Y`, so it cannot overwrite other fields.

For Dependency guard, the atomic condition directly establishes current `A=1` and current `X=candidate`. It also writes only `Y`. This proof permits a source or permission value to change and return before commit. That is allowed by the declared current-value contract. A contract in which a past revocation remains binding would require a different guard.

Refresh CAS succeeds at the first empty gap, if one occurs before the budget ends. Thus its success count is `4*(q^K-(q-1)^K)`. At `K=2,b=2`, this is `4*(169-144)=100`. Eight first-gap words change permission or source relative to the old decision. With an empty second gap and four initial records, they give `8*1*4=32` semantic violations. The [derivations](derivations.md) give full assumptions, further identities, and control proofs.

## Validation

A separate agent wrote an independent implementation from the frozen plan without reading or importing the main program. It enumerated the same assignments and checked handcrafted controls and bit complements. The main program passed nine semantic test methods, including 16 malformed configurations. The independent review records its own counts and exact comparisons; it is not a human review. See [independent_review.md](independent_review.md).

The reproduction commands and file roles are in the [README](README.md). All results use exact integers. No random sampling, confidence interval, p-value, or trained model is involved. The [failure record](failed_checks.md) preserves the initial file-path error and review corrections. No scenario was removed after its result was known.

## Discussion

There are three separate obligations: preserve fields outside the task, derive the action from valid inputs, and enforce the needed conditions at the effect. A smaller payload solves only the first. A fresh version can solve a race after its read, but cannot repair an old candidate by itself. A complete atomic dependency check can permit changes that do not alter the declared current-value task.

HTTP `If-Match` is an established way to condition a method on a current representation tag. Google Calendar documents conditional modification and a 412 response when the condition fails. Its sample re-fetches state and notes that conflict resolution can require more logic. These sources motivate version-aware repair; they do not supply our ideal non-reused counter or our task-specific permission bit. [RFC 9110, Section 13.1.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1); [Google Calendar version guide](https://developers.google.com/workspace/calendar/api/guides/version-resources)

The report does not establish that a production browser or connector exposes either atomic guard. Implementers must check the actual interface and the task contract. An unsupported client-side approximation cannot inherit the model's proof.

## Limitations

The four bits and exact function are deliberately small. All dependencies are known. Identity, fresh atomic reads, complete revision updates, and atomic checks with effects are assumed. The model omits caches, replicas, task interpretation, resource replacement, multi-record dependencies, external side effects, background output edits, and permission history. No real account, website, or language model was tested.

Policies stop at different events and consume different prefixes. Unused suffixes multiply some traces. The counts describe this corpus only. There is no claim of a natural error rate, general success-rate advantage, or lower latency. Both implementations share the same model; agreement cannot establish real-world applicability. No training or model scoring occurs, so train/test leakage is not applicable. The cases are disclosed and are not a held-out agent benchmark.

## Ethical issues, rights, and review status

All records are synthetic. No account content, credentials, messages, or private records are included. No service permissions were changed for this analysis. The small examples support defensive testing and do not provide instructions for serious harm. No paid compute or new paid API service was used. Sources are attributed, with no copied source code or full paper text. No new license is assigned to the user's work.

Codex generated the study, programs, and report. One separate agent reviewed primary sources and derivations. Another implemented the model independently and reviewed results and claims. The exact immutable model build is unavailable. The computation used Python 3.13.7 and the standard library; [environment.json](environment.json) records the environment. No human review, peer review, institutional affiliation, endorsement, or certification is claimed. The [review checklist](review_checklist.md) uses relevant NeurIPS guidance as an aid, not as conference approval.

## References and reproduction

Five supporting primary sources are linked above. [references.bib](references.bib) gives versions, authors, dates, and read scopes. An SSRN working paper was visible only through its abstract and metadata; it remains a search lead, not supporting evidence for a numerical or method claim. Use the [README](README.md) to reproduce this exact corpus and its checks.
