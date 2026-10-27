# Source search: counter resets and usage totals

Run date: 2026-10-27 (America/Toronto). Sources checked on 2026-10-27.

Codex performed this search. This file records a limited source check before the study. It contains no experiment results. No human review occurred for this source search.

## Search questions and terms

The candidate question is: How do usage total rules behave when one counter restarts and old reports arrive late?

Exact web search queries:

1. `site:opentelemetry.io docs specs metrics data model cumulative streams StartTimeUnixNano reset overlap`
2. `site:prometheus.io docs querying functions increase counter resets`
3. `AI agent budget cumulative usage reservation accounting terminal settlement arxiv`
4. `site:opentelemetry.io docs spec metrics data model cumulative starttime reset overlap`
5. `site:prometheus.io counter reset rate increase detection`

The search used current public web results. The selected sources below are from the maintainers or the paper authors. A limited search cannot establish that a method is new.

## Checked sources

### OpenTelemetry: Metrics Data Model

- URL: https://opentelemetry.io/docs/specs/otel/metrics/data-model/
- Maintainer: OpenTelemetry.
- Version shown in the page navigation: OTel 1.62.0.
- Page date: no page revision date was established in the checked text.
- Checked sections: cumulative sums, Single-Writer, Temporality, Resets and Gaps, Overlap, and Delta-to-Cumulative.

A cumulative value covers the sum since a start. `TimeUnixNano` records the observation time. `StartTimeUnixNano` identifies the start of an unbroken sequence and helps interpret restarts. Missing writer identity can merge separate instances into one stream. This can make samples look like resets. Single-Writer and Temporality are marked Stable. Resets and Gaps and Overlap are marked Development. The reset discussion distinguishes known and unknown starts. The overlap discussion does not fully specify selection among competing writers.

Use in this study: justify explicit stream and counter-start identity. This source does not establish exact budget settlement or prove that telemetry readings contain every charge.

### Prometheus: Query functions

- URL: https://prometheus.io/docs/prometheus/latest/querying/functions/
- Maintainer: Prometheus.
- Page date: no publication or revision date was established in the checked text.
- Checked sections: `increase()`, `rate()`, and `resets()`.

For float counters, `resets()` treats a decrease between consecutive samples as a reset. `increase()` and `rate()` adjust counter breaks. They also extrapolate over the selected time range. Thus an increase can be noninteger even when counter changes are integers. The guide says to calculate rates before aggregation so that reset detection remains possible.

Use in this study: explain why a total decrease can have meaning under a specified sample order. Do not name an arrival-order drop rule “Prometheus.” The documented functions use time-series samples in a range vector. They are not an exact-charge ledger for arbitrary delivery order. This study does not test Prometheus software or show a Prometheus defect.

### Zhu and Wang: Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation

- Authors: Genliang Zhu and Chu Wang.
- URL: https://arxiv.org/html/2610.00349v1
- Stable identifier: https://arxiv.org/abs/2610.00349
- Version: v1, cs.AI. The HTML version line shows 29 September 2026.
- Status: preprint. No external peer review was verified.
- Read scope: abstract, trust assumptions, terminal settlement, selected recovery text, epoch fencing, and stated provider-boundary limits. The full paper was not checked or reproduced.

The paper separates reserved, uncertain, and settled resource rights. Its settlement procedure uses terminal evidence and does not repeat the external effect. An unknown result leaves the reservation unresolved. Its epoch fencing section states that a new authority epoch alone does not recover old rights. The old generation must first close under its stated conditions. It also limits guarantees at the provider boundary.

Use in this study: distinguish counter identity from permission and settlement. A counter incarnation is one accumulation period. It is not the same as the paper's credit authority epoch. A reset-aware total alone cannot establish safe budget release.

### NeurIPS Paper Checklist Guidelines

- URL: https://neurips.cc/public/guides/PaperChecklist
- Site year shown: 2026. No separate revision date was established.
- Read scope: claims, limitations, proofs, reproduction, code and data, experiment settings, uncertainty, compute, ethics, impact, licenses, assets, human subjects, and LLM use.

Use this as a review aid. Match each claim to evidence. State assumptions, method, scope, and reproduction commands. Distinguish a complete finite test set from a random sample. State source rights and actual review status. This use does not imply NeurIPS approval, submission, or compliance.

## Rights and source use

The arXiv HTML states an arXiv perpetual non-exclusive license. This does not give this project a general right to relicense the paper. The exact documentation licenses were not established from the checked OpenTelemetry and Prometheus page text. No external code, table, figure, dataset, or long quotation is needed for the planned comparison. Use original code and synthetic inputs. Cite these sources with short original paraphrases. Do not copy or relicense their assets. This search adds no license to the repository.

## Check against prior repository work

The local report inventory was checked with `rg --files outputs` and a report filename filter. The following reports received a focused text check:

- `outputs/2026-10-26-usage-reconciliation/report.md`: its model requires one job and one counter start. It explicitly excludes counter resets and downward corrections. Its high-water result applies only to the stated monotone counter contract.
- `outputs/2026-10-24-shared-limit/report.md`: its epoch is a shared allocation version for a local database guard. It does not study cumulative counter restarts.
- `outputs/2026-10-23-receipt-state/report.md`: receipt history and current record state.
- `outputs/2026-10-25-reservation-release/report.md`: safe release of reserved capacity after uncertain work.

The search of these reports used `epoch|reset|incarnation|counter start`. This is a focused local comparison, not a full review of every source cited by the repository.

## Proposed contribution and limits

The selected contribution is a reproducible, finite comparison of five counter rules after the input contract changes to allow restarts: GlobalMax, ArrivalDrop, SourceOrderDrop, EpochLast, and EpochMax. The proposed corpus has two disjoint completed incarnations. Each has one progress report and one final report. Each total is from zero through two. Include distinct arrival orders and one repeated final report. The plan gives 36 value configurations and 144 arrival histories for each configuration, or 5,184 histories. These are planned counts, not results in this source file.

Assess budget decisions only after an independent barrier establishes that both incarnations are complete and all their reports have arrived. This scope does not test admission with incomplete evidence. ArrivalDrop infers resets from value decreases in arrival order. SourceOrderDrop applies the same heuristic in trusted source order. Neither rule is named or tested as Prometheus. A new incarnation can have a first value at least as large as the old final total; there is then no value decrease to expose its reset. EpochLast retains the last distinct received value for each incarnation. EpochMax retains each incarnation's maximum and adds these maxima. Define the identity and closure assumptions before execution.

This extends the October 26 test boundary. It is not a new counter merge protocol. Do not claim that explicit identity, maximum merge, reset detection, or terminal settlement was invented here. Do not call a finite synthetic failure share a production failure rate. The planned closure barrier supplies a strong assumption; it is not established by a counter value. Do not treat a sum of received maxima as the final charge unless completeness is separately established. The search does not establish research priority.

## Leads not used as checked evidence

The broad query returned other agent-budget and settlement leads, including AgentBudget, BAGEN, and `arXiv:2610.01138`. Their contents were not read for this search. They must not be cited as checked evidence or used to claim that this search is exhaustive.
