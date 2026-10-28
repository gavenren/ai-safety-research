# Source search and prior work

Date: 2026-10-28, America/Toronto. Codex performed this source check. No human review occurred.

## Question and search sequence

The search examined a lower total budget while prior work still holds capacity. It preceded the frozen experiment plan. Later reads checked source metadata and the final plan's use of those sources. No source supplies the experiment's measurements.

Exact queries from the source-review agent:

1. `site:kubernetes.io ResourceQuota lower quota existing resources`
2. `site:docs.aws.amazon.com budgets not real time hard limit budget actions`
3. `site:arxiv.org agent budget conservation reservations cap reduction`
4. `site:pkg.go.dev/golang.org/x/time/rate SetLimitAt reserved not acted violated limit`
5. `site:cloud.google.com quotas decrease quota existing usage resources`
6. `site:arxiv.org "budget" "reservation" "limit" "change" agents`

Exact queries reported by the main agent:

7. `site.kubernetes.io resource quota lowering quota existing resources`
8. `site:docs.aws.amazon.com service quotas lower than current usage existing resources`
9. `AI agent budget decrease outstanding reservations cap reconfiguration invariant resource accounting`

The first main-agent query contained the literal `site.` typo. It is preserved here. A limited search does not prove global novelty.

## Checked primary sources

| Source and URL | Version or date evidence | Sections checked |
| --- | --- | --- |
| Kubernetes, [Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/) | Current navigation showed v1.37. Page revision date not established. | Introduction, caution, quota enforcement, infrastructure quota types. |
| Go, [rate package](https://pkg.go.dev/golang.org/x/time@v0.16.0/rate) | v0.16.0; page shows publication on 2026-08-19 and BSD-3-Clause. The page warns that this is not the latest module version. | Overview, Limiter, ReserveN, SetLimitAt, Reservation, CancelAt. |
| Zhu and Wang, [Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation](https://arxiv.org/html/2610.00349v1) | Preprint v1. The [original abstract page](https://arxiv.org/abs/2610.00349) reports submission on 2026-09-29 and both authors. | Abstract; trust boundary; assumptions; goals and non-goals; sections 4.1–4.9; root-right definition; selected durable-record and reissue text. Not the full paper or reproduced proofs. |
| SQLite, [Isolation In SQLite](https://www.sqlite.org/isolation.html) | Page revision date not established. | Separate connections, writer serialization, WAL snapshots, stale upgrades, BEGIN IMMEDIATE. |
| SQLite, [Transaction](https://www.sqlite.org/lang_transaction.html) | Page revision date not established. | Read and write transactions, transaction modes, cursor completion, rollback and errors. |
| NeurIPS, [Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist) | Current site year 2026. Page revision date not established. | Claims, assumptions, reproduction, code/data, settings, uncertainty, compute, ethics, impact, rights, human subjects, and LLM use. |

All access dates are 2026-10-28. These are source observations, not measurements of a running source system.

## Source use and boundaries

Kubernetes distinguishes quota enforcement for new changes from existing resources, which a quota change does not alter. This motivates the difference between a changed setting and an achieved total bound. Its resource quotas do not define our cumulative-use contract.

Go's documented SetLimitAt behavior accounts for reservations made before the new rate. They can leave use above or below the new limit. This is established behavior, not a defect found by this study. The experiment does not implement Go's token bucket.

Zhu and Wang distinguish issued rights, unresolved external obligations, and terminal settlement. Their fence can stop new acceptance while accepted work remains live. Their stated guarantees require several trusted boundaries. This supports the need to retain obligations. Our local cap-change test does not reproduce or refute that protocol.

SQLite documents a single writer and transaction isolation. It supports a check and update in one write transaction. Application data saved after an earlier read can still be stale. A wrong application guard is not an engine isolation defect.

The transaction guide supplies the read-lifetime and rollback rules used in the plan. The read cursor and read transaction end before the later cap attempt. The NeurIPS checklist is a review aid; it does not establish approval or submission compliance.

## Difference from prior repository studies

The source reviewer read four prior reports. The October 24 [shared-limit report](../2026-10-24-shared-limit/report.md) explicitly excludes changing capacity. The October 25 [reservation-release report](../2026-10-25-reservation-release/report.md) tests when a hold can be released under a fixed cap. The October 26 [usage report](../2026-10-26-usage-reconciliation/report.md) tests cumulative reports and residual holds under a fixed cap. The October 27 [counter report](../2026-10-27-counter-epochs/report.md) tests restart interpretation after work has finished.

The selected plan instead changes the cap while a hold or past use remains. It tests five cap-change rules with the same complete admission rule for new work. It separates successful cap changes, refused requests, actual use, and maximum unresolved use. The contribution is the declared exact comparison corpus and its repeatable evidence. Guards, reservations, and revision checks are established methods. No new protocol or research-priority claim is made.

## Excluded evidence and rights

AWS and Google Cloud results were search leads only for the final paper. The search also returned Token Budgets, The Irreversibility Budget, and an audit-budget paper. Their full contents were not checked for this study. Do not cite these leads as read evidence or treat the search as complete.

The package needs no external implementation, dataset, figure, table, or long quotation. Use original code and invented records. Source summaries are short paraphrases. Source licenses remain with their owners. No new license is assigned to the repository. Final source claims need a check after the report is written.
