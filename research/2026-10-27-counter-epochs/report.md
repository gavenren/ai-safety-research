# Sorting usage reports does not reveal every counter restart

Date: 2026-10-27, America/Toronto. Exact finite simulation. Research note.

## Abstract

A cumulative counter can restart at zero. Its first reported value after restart need not be lower than the old final value. We compare five accounting rules on 5,184 designed delivery histories each. A separate closure condition confirms that both counters finished and all final reports arrived. Only then do we test admission of another job. A rule that treats a delivery decrease as a restart undercounts 1,400 histories and overcounts 978. Sorting by the correct source order removes its overcounts but leaves 1,296 undercounts. Those undercounts cause 3,024 excess-use decisions among 31,104 matched admission branches. A maximum for each stable counter incarnation gives the exact completed total in every primary history. The contribution is a reproducible comparison corpus and a stated failure condition for known rules. These are synthetic results, not production failure rates or a new accounting protocol.

## Question and safety relevance

Can a rule infer counter restarts from numeric decreases and correctly enforce an agent's total-use limit? Does sorting delayed reports by source order solve every error?

A **cumulative counter** gives total use since one start. A **counter incarnation** is one such accumulation period with a stable unique identifier. A **report ID** identifies one observation. A repeated report keeps the same ID. **Booked use** is the amount stored by the accounting rule. **Admission** permits a new job to use a stated amount. A **closure condition** confirms that the prior work ended and its required final reports arrived.

An AI agent can read resource reports from workers that restart. Incorrect accounting can allow use above a limit or refuse a job that fits. These outcomes differ. This study tests the accounting rule after completed work. It does not test a language model's choice of action, provider billing, or a live service.

## Related work and contribution

OpenTelemetry separates counter start identity, observation time, cumulative values, resets, and overlapping writers [1]. Its Temporality section is Stable; Resets and Gaps and Overlap are Development. Prometheus documents decrease-based reset handling in ordered range samples, with extrapolation in its rate and increase functions [2]. Our simple rules are not implementations of those functions. No defect in either project is claimed.

Zhu and Wang's preprint separates uncertain work from final settlement and places limits on guarantees at the provider boundary [3]. Only selected relevant sections were checked. Its authority epochs concern resource rights. Our counter incarnations identify separate accumulation periods. These concepts must not be substituted for each other.

The repository's [October 26 study](../2026-10-26-usage-reconciliation/report.md) fixed one counter start and explicitly excluded resets. Its maximum rule was valid under that contract. The [October 25 study](../2026-10-25-reservation-release/report.md) examined when uncertain work can release a reservation. This study instead supplies closure and tests how to combine reports from two completed counter incarnations.

The contribution is the complete declared small corpus, five matched rules, full state traces, separate accounting and admission measures, and an independent implementation. Identity-aware maxima and reset detection are established ideas. The limited [source search](source_search.md) does not establish priority or a new protocol.

## Method

### Saved plan and source separation

The [plan](plan.md) was frozen at 14:31:24 UTC before main implementation. The main source was frozen at 14:33:46 UTC before its first run. A separate agent read only the plan and froze a prefix-based specification at 14:32:24 UTC. It withheld its computed totals until the main source was frozen. The main source did not change in response. The later comparison code maps its independent states to the main output schema. This separation reduces implementation copying but does not remove a shared model error.

### Provider contract

Two non-overlapping counter incarnations, E0 and E1, consume disjoint integer amounts z0 and z1. E1 starts a new counter at zero after E0 ends. Each incarnation emits progress Pi with value pi and a final report Ti with value zi. We require `0 <= pi <= zi <= 2`. True total use is `Z=z0+z1`.

The source order is P0, T0, P1, T1. Each point has a distinct trusted order number, an incarnation ID, a report ID, a value, and a final flag. Reports are truthful and immutable. Copies preserve all fields. All use is complete before reports arrive at the controller. Report arrival can have any order. There is no clock error, false identity, downward correction, missing primary report, or third incarnation.

Each incarnation has six possible progress/final pairs. The 36 pair combinations are crossed with three report multisets: no copy, an extra T0, and an extra T1. Their distinct arrival orders number 24, 60, and 60. Thus each rule receives `36 × 144 = 5,184` histories. Copies are not given artificial labels.

### Rules and common duplicate check

All rules first ignore an exact repeated report ID. This common step isolates how they interpret cumulative values and restarts. The numeric total starts at zero. Some baselines deliberately ignore available incarnation IDs or final flags. This is a comparison of specified rules, not a claim that these are the only reasonable methods.

| Rule | Booked use after distinct reports |
| --- | --- |
| GlobalMax | Greatest value across both incarnations |
| ArrivalDrop | Process distinct arrivals in delivery order. Add the increase from the last value, or add the new value when it is lower. |
| SourceOrderDrop | Sort distinct received reports by trusted source order, then apply the same decrease rule. |
| EpochLast | Sum the last distinct delivered value for each incarnation. |
| EpochMax | Sum the greatest received value for each incarnation. |

The word Epoch in the last two code labels means counter incarnation only. It grants no new authority. The code saves the initial state and every delivered report's duplicate flag and resulting state. Intermediate totals are estimates; no new work is admitted during delivery.

### Admission branches and measures

After the complete history, a separate closure condition confirms that the work ended and both registered final reports arrived. Presence of both final IDs is the modeled gate, under the truthful-source contract. This is supplied evidence, not a property inferred from counter values. A new job requests b units. For each history, test `C ∈ {Z,Z+1,Z+2}` and `b ∈ {1,2}`. Admit if `C-q >= b`, where q is booked use, then consume exactly b.

The six decisions are independent hypothetical branches. They are not six jobs run in sequence. Each rule has 31,104 branches. Across all five rules, there are 25,920 rule-history outcomes and 155,520 branches.

The final accounting error is `q-Z`. A negative error is an undercount; a positive error is an overcount. Actual excess is `max(0,Z+b-C)` for an admitted job. A feasible refusal occurs when a refused job satisfies `Z+b <= C`. Local balance is `C-q-b` after admission, or `C-q` after refusal. A negative local balance does not by itself establish actual excess.

Seven named controls cover a visible reset, a hidden reset, late old progress, equal values, zero use, exact replay, and a missing final report. The last control is outside the primary corpus. It omits T1 while true use is four. The gate is false, so every rule refuses. This tests the declared gate in code; it does not establish a real provider closure guarantee.

## Results

All planned histories and branches completed. Each accounting row below has 5,184 histories. Each admission row has 31,104 branches.

| Rule | Exact totals | Undercounts | Overcounts | Excess-use branches | Feasible refusals | Admitted branches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GlobalMax | 1,584 | 3,600 | 0 | 8,496 | 0 | 24,048 |
| ArrivalDrop | 2,806 | 1,400 | 978 | 3,276 | 2,194 | 16,634 |
| SourceOrderDrop | 3,888 | 1,296 | 0 | 3,024 | 0 | 18,576 |
| EpochLast | 2,646 | 2,538 | 0 | 6,198 | 0 | 21,750 |
| EpochMax | 5,184 | 0 | 0 | 0 | 0 | 15,552 |

GlobalMax loses the smaller incarnation total when both use amounts are positive. This supports H1. ArrivalDrop has both types of accounting error, which supports H2. Correct source ordering eliminates overcounts in this model, but does not expose every reset. This supports H3. EpochLast can replace a final total with a late progress value. EpochMax keeps the exact final total in every case, which supports H4 under the stated identity and closure assumptions.

The source-ordered rule is exact in all 3,024 histories where `p1<z0`. Of 2,160 histories with `p1>=z0`, it undercounts 1,296. The other 864 have `z0=0`, so the missed old amount is zero. The absence of a decrease is not, by itself, an accounting error. It is an error here only when a positive old total is lost.

ArrivalDrop has 2,432 branches with a negative local balance. These arise from excess booking. They are distinct from its 3,276 actual-excess branches. The largest actual excess is two units. EpochLast can undercount by four units; each other undercounting rule has a maximum of two. ArrivalDrop can overcount by two. Detailed group counts are in [summary.csv](results/summary.csv).

Exact repeated IDs changed no state in all 21,600 duplicate deliveries across the five rules. This does not make each report multiset's aggregate outcome share equal. Enumerating permutations with an extra copy changes the frequency of first-distinct arrival orders. These weights describe this corpus, not real delivery frequencies.

### Concrete retained cases

In the hidden-reset control, E0 ends at one. E1 first reports two and ends at two. The source-ordered values are 1,1,2,2. The decrease rule sees no fall and books two, but actual use is three. With `C=3` and `b=1`, it admits a job that brings use to four. Sorting cannot recover the missing counter identity from this value sequence.

The first ArrivalDrop overcount witness has `p0=z0=0` and `p1=z1=1`, delivered P0,P1,T0,T1. The values are 0,1,0,1. The delayed old zero looks like a reset. The rule books two for one unit of actual use. With `C=2,b=1`, it refuses work that fits. See the retained first [witnesses](results/witnesses.json). These are synthetic examples selected by the declared enumeration order, not claimed global minima.

In the missing-final control, EpochMax has only three observed units while actual use is four. The closure gate refuses every branch. This negative control shows why a sum of observed maxima is not sufficient evidence that every charge arrived.

## Conditional arguments

Let `D(v1,...,vn)` be the decrease rule's total, starting from zero. Each nondecreasing step adds the difference. Each strict decrease adds the new value instead. Its equivalent prefix form is

`D = vn + sum of vi over all i where v(i+1)<vi`.

This form follows by telescoping ordinary differences and restoring the old value at each decrease. It makes clear why an arrival-order decrease can add a false reset amount.

For the complete trusted source order `p0,z0,p1,z1`, the only possible strict decrease is between z0 and p1. Therefore

`q_source = z0+z1` if `p1<z0`, and `q_source = z1` otherwise.

Thus the error is zero in the first case and `-z0` in the second. It is never positive. Sorting alone still undercounts whenever `z0>0` and `p1>=z0`. This is a property of the declared heuristic, not an impossibility result for every algorithm with these fields. Final flags and incarnation IDs are also available in this model.

For GlobalMax, the final total is `max(z0,z1)`, so its error is `-min(z0,z1)`. For EpochMax, every incarnation's final report is present and every earlier value is no greater. Its maximum is zi, and the disjoint sum is Z. Consequently `C-q>=b` is equivalent to `Z+b<=C`, so it has neither unsafe admissions nor feasible refusals. This argument requires truthful complete reports, non-reused identities, disjoint costs, and atomic local decisions. It does not establish these conditions in a production system.

## Reproduction and uncertainty

Two complete main runs produced byte-identical deterministic files: inputs, compressed traces, summary, paired comparisons, controls, witnesses, and checks. They used Python 3.13.7 on macOS 26.7.2, arm64, with the standard library only. CPU times were 1.381587 and 1.397986 seconds; wall times were 1.488690 and 1.428012 seconds. Each saved result set used 1,361,311 bytes before its environment record. Gzip headers have zero time and no path. The declared bounds were 120 CPU seconds, 300 wall seconds, and 200 MB saved output. Wall and output checks are periodic, not hard real-time guarantees.

No model is called inside the simulation. There is no random seed, training data, or train/test split. There is no sampling confidence interval or statistical significance claim. Enumeration gives exact counts for these inputs, with no population interpretation. Read [README.md](README.md) for commands and [reproduction.json](reproduction.json) for exact hashes.

The independent specification uses formulas on distinct report prefixes. Both runs passed its comparison of all 151,200 states and 155,520 admission branches, plus summaries, controls, matched outcomes, and first adverse examples. Read [independent_review.md](independent_review.md) for the scope and result. Agreement can reduce code error but cannot validate an incorrect shared assumption.

## Discussion and limitations

Delivery order, numeric reset detection, incarnation identity, and closure answer different questions. A correct source order does not always show a numeric fall at a reset. A correct duplicate filter does not identify disjoint accumulation periods. An identity-aware maximum does not prove that all final reports arrived. The complete result here requires all of these contract conditions.

The corpus has two incarnations, small integers, fixed source order, truthful immutable reports, and one end-of-history decision. It excludes live concurrency, requests before closure, counter corrections, missing identities, identity reuse, malicious reports, counter wraparound, unknown initial values, clock errors, and finite retention. Stable labels and closure are assumed. No experiment uses a production website or connected account. No result measures agent behavior or provider failure rates. The chosen heuristics are explicit baselines, not full OpenTelemetry or Prometheus implementations.

The artifact can help test an accounting implementation against specified reset cases. A deployment needs separate validation of identity, source completeness, authorization, durable state, and concurrency. This study makes no general deployment guarantee.

## Ethical issues, rights, and review status

Codex generated the study, implementation, analysis, and report. Separate Codex agents prepared the independent specification and reviewed sources and methods. The exact model build was not exposed. No human or external peer review occurred. No university affiliation, endorsement, or certification is claimed.

The inputs are invented. No private account data, credentials, personal records, paid service, or new permission is used. The study can help prevent excessive agent resource use; its counts must not be used as unsupported claims about real systems. Source text is paraphrased. No third-party code or dataset is copied, and no new license is assigned. Relevant items from the NeurIPS checklist are review aids only [4].

## References

1. OpenTelemetry. [Metrics Data Model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/). Selected cumulative, identity, temporality, reset, and overlap sections checked on 2026-10-27. Section statuses differ.
2. Prometheus. [Query functions](https://prometheus.io/docs/prometheus/latest/querying/functions/). `increase`, `rate`, and `resets` sections checked on 2026-10-27.
3. Genliang Zhu and Chu Wang. [Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation](https://arxiv.org/html/2610.00349v1). Preprint v1. Selected trust, terminal-settlement, recovery, epoch, and provider-boundary sections checked; not a full-paper review.
4. NeurIPS. [Paper Checklist Guidelines](https://neurips.cc/public/guides/PaperChecklist). Selected review topics checked on 2026-10-27. No approval or submission claim.
