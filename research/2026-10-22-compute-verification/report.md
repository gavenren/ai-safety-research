# Bounding AI Compute with Attested Receipts: A Coverage-Aware Accounting Protocol

**Date:** 22 October 2026  
**Type:** Technical working paper; proposed protocol, conditional analysis, and synthetic demonstration  
**Review status:** AI-generated working paper; separate AI critical review and reproducibility checks completed. No human or external peer review is claimed.

## Abstract

A signed compute record can establish who reported a measurement. It cannot, by itself, establish that the measurement is correct, that all devices were reported, or that the activity trained a named model. This paper asks what additional conditions permit a defensible bound on AI compute. We propose an accounting protocol that keeps three quantities separate: activity in accepted device intervals, possible activity in gaps within an enrolled inventory, and possible activity outside that inventory. We give a conditional interval bound and an indistinguishability argument showing why observed receipts cannot establish a finite global upper bound when external capacity is unconstrained. A reproducible synthetic example shows that 95% coverage of device time can correspond to only 87.5% coverage of capacity. At a fixed illustrative threshold, this difference can change the result from within the threshold to unresolved. An exhaustive check of 4,096 small missingness patterns finds no containment failure under the stipulated assumptions. These are arithmetic checks, not hardware measurements or a security evaluation. The proposed contribution is a precise accounting interface between metering systems and decisions that depend on compute limits. Its central requirement is explicit treatment of missing evidence.

## 1. Research question and scope

**Research question:** Under which stated assumptions can authenticated accelerator records bound cumulative compute, despite missing records and incomplete inventory?

Compute verification can support oversight of large AI development efforts. Its value depends on the claim being checked. Evidence of an approved firmware state is useful. Evidence of how much arithmetic a device performed is a different claim. Evidence that a company used no additional devices is different again. A system that collapses these claims into one “verified” label can give false confidence.

This paper proposes a receipt and accounting interface. A receipt is an authenticated record of a measurement over a stated interval. The interface produces a lower bound, an upper bound, a scope statement, and an explicit list of assumptions. It does not certify model safety, model capability, data provenance, or legal compliance.

The proposed contribution has three parts. First, it makes inventory scope and missing device intervals part of the output rather than an informal caveat. Second, it gives simple conditional bounds that do not require missing records to be random. Third, it provides a small executable example that distinguishes device-time coverage from capacity-weighted coverage. The algebra is elementary interval accounting. We do not claim a new cryptographic primitive, a deployed metering design, or priority over all prior work.

The baseline is the sum of reported measurements. The proposed method adds uncertainty for accepted measurements and capacity budgets for missing activity. Its purpose is to reveal when the baseline cannot support an upper-bound claim.

## 2. Related work and available components

Remote attestation provides a useful division of roles. RFC 9334 distinguishes an attester that produces evidence, a verifier that appraises evidence, and a relying party that uses the result. It also treats freshness and appraisal policy as explicit concerns [1]. Our design uses these roles. The scope and meaning of a meter still require a separate argument.

NVIDIA's GPU claims documentation includes checks concerning report signatures, certificate status, firmware measurements, and nonce matching [2]. Those documented checks motivate identity and freshness fields. We do not infer from them that a commodity GPU exposes the complete, non-bypassable operation meter required below. That requirement remains a proposed component requiring validation.

O'Gara and colleagues survey hardware-enabled mechanisms for reporting AI activity, cluster configuration, location, and licensing. They identify physical attacks, privacy, and implementation constraints as research problems [3]. Petrie and colleagues propose flexible hardware-enabled guarantees built around an auditable processor and physical protection [4]. Their technical companion studies options including access to accelerator data paths [5]. These are close architectural antecedents. Our narrower focus is the accounting output when a verifier lacks full device or time coverage.

Certificate Transparency uses Merkle trees to support inclusion and consistency checks for an append-only log. RFC 9162 also explains that inconsistent views can defeat log auditing without further safeguards [6]. We borrow the log pattern, not the certificate protocol or a claim that transparency logs establish measurement truth.

Proof-of-learning addresses evidence relating a training process to resulting parameters [7]. A recent preprint by Peigné, Nguyen, and Wang proposes a training-verification architecture using commitments, network observations, and zero-knowledge machinery; it lists unresolved engineering and proof problems [8]. Such work concerns a richer execution claim than our physical accounting quantity. This paper does not treat its projected overhead or timeline as demonstrated performance.

Kimpson, Baker, and Graham study a closely related limit: how much covert computation a trusted power trace can exclude, conditional on energy-cost bands and declared-machine capacity [10]. Their analysis treats different workloads that yield the same observation and derives conservative bounds. Our account instead starts from accepted receipts, gaps in enrolled device time, and an explicit external-inventory budget. We do not claim a new general identifiability argument, and we do not adopt their hardware measurements or numerical bounds.

Ansari's 2026 preprint separates monitoring, verification, and enforcement mechanisms and assesses their feasibility [9]. Our contribution is complementary: an explicit conditional calculation and output format. The search was targeted and limited, not a systematic review. The search record lists the terms and closest works.

## 3. Define the quantity before measuring it

Let the assessment cover a named physical fleet and time window $[0,T]$. The fleet may be an enrolled facility, a group of devices, or an organization's specified hardware. The main accounting theorem bounds all included physical operations in this fleet. A development project is a different scope; Section 6 gives a separate attribution rule for it.

We define compute as the sum of specified executed arithmetic operations. A measurement specification must state its treatment of precision, integer arithmetic, fused multiply-add, tensor instructions, sparsity, padding, retries, and recomputation. For example, it may count a multiply-add as two scalar operations. A matrix instruction then needs a documented mapping from its actual executed work to those units. A dense-equivalent marketing figure is not automatically an actual-operation count.

The safest initial format is a vector of counts by operation class. A scalar total requires a published nonnegative weighting rule. All bounds below use one fixed rule. A policy that uses another definition must justify a conversion or retain separate quantities.

Physical operations do not equal useful algorithmic work. Repeated computation can increase the physical total without improving a model. A more efficient algorithm can improve a model while reducing that total. The calculation makes no claim about the capability associated with a count.

For each enrolled device $d$, divide the window into non-overlapping accounting intervals. Let $j$ identify one device-interval pair. Let:

- $x_j$ be its true operation count;
- $p_j$ be a valid maximum count for that interval;
- $y_j$ be an accepted reported count, when available;
- $\epsilon_j$ be a justified absolute measurement-error bound;
- $O$ be the set of accepted intervals;
- $G$ be the remaining intervals in the enrolled inventory.

Thus $0\leq x_j\leq p_j$. A valid accepted measurement also satisfies $|x_j-y_j|\leq\epsilon_j$. For continuous time, $p_j$ can be the integral of a valid maximum rate over the interval. Clock uncertainty must enlarge the interval capacity. It must not disappear through rounded timestamps.

Let $x_E$ denote all relevant compute outside the enrolled inventory. If there is a defensible bound $B_E$, then $0\leq x_E\leq B_E$. A declaration of completeness is evidence to appraise, not a mathematical reason to set $B_E=0$. A claim limited to enrolled devices excludes $x_E$ by definition and must say so prominently.

## 4. Threat model and assumptions

The adversary may control the host operating system and reporting network. It may withhold records, reboot devices, alter job names, present records twice, and seek to omit devices. It may choose missing intervals after seeing activity. The base model does not assume independent failures or honest self-reports.

The bound requires the following conditions:

1. **Measurement integrity.** For an accepted interval, the meter covers all operations included in its specification and its error does not exceed $\epsilon_j$. The signing key cannot authenticate arbitrary host-supplied counts as meter output.
2. **Identity and partition integrity.** Device identities are not cloned within the scope. Accepted intervals refer to distinct physical device time. The verifier does not double-count overlapping intervals.
3. **Capacity validity.** Each $p_j$ bounds every allowed configuration, including relevant arithmetic modes and clock settings. A typical throughput measurement is insufficient. A datasheet number needs a separate argument that it is an upper bound in the chosen units.
4. **Inventory scope.** The enrolled device set is fixed or changes through a reconciled event log. Any claim about a broader set carries a justified external budget $B_E$.
5. **Attribution, when claimed.** A project-level lower bound uses only activity whose association with that project is established. Operator-chosen job labels alone do not establish that association.

Physical compromise, a malicious manufacturer, a flawed meter, or a broken cryptographic implementation can violate these conditions. They are not covered by the arithmetic proof. A compromise report must trigger a reassessment of affected evidence and assumptions.

The base paper uses deterministic error bounds. A calibration interval derived from observed workloads is not automatically such a bound. If an implementation uses probabilistic guarantees, it must state its joint coverage probability. A sum of per-record failure probabilities gives a conservative union bound without independence; thousands of individually plausible intervals can still give a weak total guarantee. No real-world probability is estimated here.

## 5. Protocol proposal

### 5.1 Enrollment and a fixed scope

Before an assessment window, the operator registers devices, their capacity specifications, accepted meter versions, and the claimed organizational or project boundary. An auditor reconciles that list against independent records appropriate to the deployment. Possible records include purchases, leases, cloud allocations, transfers, and physical inspections. Such reconciliation can support an external budget but does not make completeness a cryptographic fact.

The verifier commits to a versioned enrollment record. Additions and removals have effective times and supporting evidence. An asserted removal without a supported time boundary leaves the device in the gap budget. A maintenance label by itself does not prove that a device could not execute work.

### 5.2 Establish the meter's identity and state

A fresh challenge binds the enrollment record, meter specification, and assessment window to the attestation session. The verifier checks the relevant trust chain and its appraisal policy. It must establish a secure binding between the attested meter and the receipt-signing key. An unrelated valid GPU quote attached to a host-generated count is insufficient.

Freshness must be interpreted within the appraisal model [1, Section 10]. A fresh state quote does not establish continuous measurement between quotes. Ordinary performance counters may be user-controlled and resettable; that is different from the secure meter required here [3, Section 4.4]. A complete implementation needs an isolated meter with access to every included execution path. It also needs an account of counter reset, overflow, device partitions, firmware changes, and accelerator engines outside the main tensor path. These requirements are open engineering work, not capabilities demonstrated by this paper.

### 5.3 Issue receipts and reconcile continuity

A proposed receipt contains the following fields:

| Field | Purpose |
|---|---|
| Protocol and measurement-specification versions | Fix interpretation of bytes and units |
| Enrollment and assessment identifiers | Bind the receipt to its scope |
| Device pseudonym and protected boot epoch | Distinguish devices and restarts |
| Sequence number and previous-receipt digest | Expose missing or conflicting records |
| Interval endpoints and clock-error bound | Bound covered device time |
| Start and end counters, or protected interval delta | State the measurement |
| Meter-state and attestation references | Bind the count to approved components |
| Optional protected project commitment | Support an additional attribution claim |
| Signature | Authenticate the complete canonical record |

A signed hash chain reveals omissions only relative to known anchors. It cannot reveal an entirely hidden chain or a hidden device. The verifier therefore reconciles each enrolled device against the entire assessment window, including time before its first receipt and after its last receipt. A reboot without a trustworthy continuity record creates a gap. A later receipt may recover a gap only if protected cumulative state and its timing establish continuous coverage.

Duplicate copies of an identical receipt count once. Conflicting records for one identity and sequence trigger quarantine of the affected period. The verifier uses a capacity budget for that period until the conflict is resolved. It must not choose whichever branch produces a preferred total.

### 5.4 Commit records and resist inconsistent views

Receipts are committed to an append-only log. Independent witnesses exchange signed log checkpoints and check their consistency. This makes some equivocation detectable. Witnesses do not establish that the meter was honest or that unregistered hardware was absent.

Full receipts can remain encrypted for authorized auditors. Public commitments should use a suitable hiding construction; a bare hash of a predictable count can disclose that count through guessing. A public release can include aggregate bounds, specification identifiers, unresolved exceptions, and a commitment to the evidence used. Disclosure policy must account for information leaked by timing, activity patterns, and device counts.

### 5.5 Produce a structured finding

The verifier validates records, forms a disjoint accepted interval set, accounts for every remaining enrolled interval, and computes the bounds below. Disjointness must hold after timing uncertainty is considered. Ambiguous overlap cannot support two lower-bound contributions; unresolved regions retain a capacity allowance. Its result includes scope, units, window, inventory commitment, accepted meter versions, lower and upper bounds, coverage measures, external-budget basis, and unresolved assumptions.

This is a retrospective evidence protocol. It does not include a remote shutdown mechanism. An enforcement system would need an additional authorization model, availability analysis, and error-recovery process.

## 6. Conditional results

### Proposition 1: Accounting interval

For accepted interval $j$, define

$$
\ell_j=\max(0,y_j-\epsilon_j),\qquad
u_j=\min(p_j,y_j+\epsilon_j).
$$

A record with $\ell_j>u_j$ is inconsistent with the assumptions and is not accepted. Under the conditions in Section 4, the total physical compute within the stated fleet scope

$$
C=\sum_{j\in O}x_j+\sum_{j\in G}x_j+x_E
$$

satisfies

$$
L=\sum_{j\in O}\ell_j
\;\leq C\leq\;
U=\sum_{j\in O}u_j+\sum_{j\in G}p_j+B_E.
$$

**Proof.** Each accepted true count lies within its clipped interval. Each gap contributes a nonnegative amount no greater than its capacity. External activity contributes a nonnegative amount no greater than its stated budget. Sum these inequalities over disjoint components. No randomness or independence of missingness is used. ∎

If $B_E$ is unknown and unbounded within the model, report $U=+\infty$ for the broader scope. The enrolled-scope upper bound can still be finite. This distinction belongs in the result itself.

### Proposition 2: Receipts alone cannot bound omitted inventory

Suppose the verifier observes only a transcript of enrolled-device receipts and receives no evidence constraining external computation. For any finite proposed global upper bound $U$, there are two executions with the same observed transcript: one with no external activity and one with external compute greater than $U$.

**Proof.** Hold every observed device and message fixed. Add unobserved devices performing more than $U$ operations within the window. By the premise, their activity does not change the verifier's observations. The same output therefore cannot be a valid global upper bound in both executions. ∎

This is an information-limit argument under an unconstrained-external-capacity model. It does not say that independent supply-chain or facility evidence can never bound external activity. It says the receipts do not supply that missing premise.

### Project-attribution variant

A fleet total is not a project total. For each enrolled interval, let $z_j$ be the activity included in a specified project, with $0\leq z_j\leq x_j$. Let $A$ contain intervals whose entire activity is certainly attributed to the project. Let $P$ contain every interval that could contribute to it, so $A\subseteq P$. The attribution evidence must establish $z_j=x_j$ for $j\in A$ and $z_j=0$ for $j\notin P$. Uncertain intervals stay in $P$. If no exclusion is justified, $P$ is the whole enrolled interval set.

With project-specific external budget $B_{E,P}$, the valid conservative bounds are

$$
L_P=\sum_{j\in A\cap O}\ell_j,\qquad
U_P=\sum_{j\in P\cap O}u_j+\sum_{j\in P\cap G}p_j+B_{E,P}.
$$

The proof sums $z_j=x_j$ on certainly attributed intervals and $0\leq z_j\leq x_j$ elsewhere. Ambiguous activity contributes zero to the project lower bound and its full possible amount to the upper bound. Tighter bounds for mixed-project intervals require separately justified attribution measurements. A fleet lower bound must never be used as evidence that one project exceeded a threshold.

### Coverage and threshold decisions

For intervals of duration $\Delta_j$, define

$$
q_{time}=\frac{\sum_{j\in O}\Delta_j}{\sum_{j\in O\cup G}\Delta_j},\qquad
q_{capacity}=\frac{\sum_{j\in O}p_j}{\sum_{j\in O\cup G}p_j}.
$$

If a denominator is zero, report that coverage measure as undefined (N/A), not 100%. These describe evidence coverage over enrolled inventory. Neither is the fraction of actual compute observed. Capacity coverage measures the part of the maximum enrolled budget backed by accepted records.

For a fleet rule $C\leq H$, report “within” only if $U\leq H$, “exceeds” only if $L>H$, and “unresolved” otherwise. For a project rule, use $L_P$ and $U_P$ instead. These labels are mathematical findings under assumptions. They do not prescribe a legal burden of proof or an automatic penalty.

Cross-provider aggregation uses the same rule. Providers must reconcile physical device identities, windows, units, and project scope before summing. A model passed between providers can create a project-attribution problem even when each provider's own device total is correct.

## 7. Reproducible synthetic demonstration

### Method

The companion script uses only the Python standard library. The plan was saved before the simulation was implemented or run; literature selection and the initial protocol idea preceded the plan.

There are 100 synthetic devices and 100 equal epochs. Twenty devices have capacity 400 abstract units per epoch. Eighty have capacity 100. For device $d$ and epoch $t$, activity is

$$
x_{d,t}=p_d\,[10+((17d+13t)\bmod81)]/100.
$$

These inputs produce integer counts. The reported value is $y_{d,t}=x_{d,t}+((d+t)\bmod3)-1$. The assumed error bound is two units per accepted record. The total true activity is 799,897 units, and the maximum capacity is 1,600,000. No external activity is included; all results concern this enrolled synthetic inventory.

We compare complete reporting with four missingness patterns. The random pattern removes 500 records with seed 20261022. Two adversarial patterns remove 500 records with the greatest capacity or greatest true activity. Ties use device and epoch order. The final pattern removes all 2,000 high-capacity intervals. The threshold is an illustrative 900,000 units, not a recommended policy threshold.

### Results

| Missingness pattern | Time coverage | Capacity coverage | Reported total | Lower bound | Upper bound | Threshold result |
|---|---:|---:|---:|---:|---:|---|
| None | 100% | 100% | 799,896 | 779,896 | 819,896 | Within |
| Random 5% | 95% | 94.83125% | 757,596 | 738,596 | 859,296 | Within |
| Highest capacity 5% | 95% | 87.5% | 699,837 | 680,837 | 918,837 | Unresolved |
| Highest activity 5% | 95% | 87.5% | 639,153 | 620,153 | 858,153 | Within |
| All high-capacity intervals | 80% | 50% | 399,933 | 383,933 | 1,215,933 | Unresolved |

All intervals contain the stipulated truth. The reported total alone understates activity whenever substantial records are missing. With no missing records it still differs from truth because of the synthetic meter error.

The two 95%-time adversarial cases have the same interval width, 238,000 units, but different positions. Removing the highest-activity records leaves a lower observed total. The capacity allowance still covers that hidden activity. Thus the table does not show that highest-activity withholding always maximizes the upper bound. It shows that missingness location matters and that a valid capacity budget preserves containment without assuming random missingness.

A separate 12-record instance enumerates all $2^{12}=4,096$ missingness patterns. There are zero containment failures under the specified bounds. This checks the implementation of the formula, not the probability of a real meter satisfying it.

A negative control deliberately breaks the error assumption. If true activity is 80, the reported count is 20, and the claimed error bound is two, the computed interval is [18,22]. It excludes truth despite a valid capacity of 100. Authentication would not fix this measurement error. The saved output preserves this failure case. Four additional deterministic checks validate classification at equality and above or below the interval: [10,20] is within at 20, unresolved at 10 and 19, and exceeds at 9. These checks were added after reviewer feedback and recorded as a plan change.

Run `python3 technical_simulation.py` to regenerate `technical_results.json`. The script contains the complete synthetic input-generation rules. No model calls, paid services, or accelerator hardware are needed.

## 8. Implementation tests still required

A useful prototype must first establish what its counters mean. It should compare measured counts against controlled kernels across arithmetic modes, sparse paths, device partitions, resets, power failures, and concurrent workloads. An empirical maximum error over a test suite must remain labeled an empirical result unless a stronger argument justifies a bound.

A second test stage should attack evidence continuity. It should cover omitted first and last intervals, replayed receipts, duplicate identities, conflicting chains, stale attestation, clock drift, and asynchronous log delivery. The required outcome is either a correct interval or an explicit loss of assurance. Producing a narrow interval after a violated assumption is a failure.

A third stage should evaluate inventory reconciliation and project attribution with independent operators. The relevant measures include unresolved capacity, time to reconcile gaps, privacy exposure, false exception rates, and cost per assessed device-hour. These measures require real data. This paper supplies no estimates for them.

## 9. Limits, ethical issues, and misuse

The result is conditional on difficult premises. A compromised meter can invalidate both bounds. An incorrect capacity cap can invalidate the upper bound. A cloned identity can invalidate both deduplication and inventory accounting. An inaccurate scope statement can turn a valid facility bound into a false organizational claim.

Per-project accounting is harder than fleet accounting. A protected project identifier binds activity to an identifier; it does not by itself establish all prior training, imported checkpoints, distilled knowledge, or work done under another identifier. A model-development claim needs an explicit aggregation and provenance rule. If attribution is ambiguous, assign no project lower bound to the ambiguous activity and account for its possible contribution to the upper bound.

The synthetic experiment contains no real hardware, network, or attacker measurements. Its simple load pattern and fixed capacities are explanatory choices. No conclusion about deployment overhead, adversarial detection rates, or frontier-scale feasibility follows from it.

Fine-grained records can expose commercial plans, worker behavior, and infrastructure locations. Systems should minimize collection, separate public and restricted evidence, limit retention, and provide a way to contest incorrect records. A verifier can become a surveillance or market-control point. Independent review and portable evidence formats can reduce, but not remove, that risk.

This proposal is limited to evidence. Remote interruption of workloads would add risks to availability and safety that the present analysis does not address. Compute counts also cannot replace model evaluation or analysis of how a system is used.

## 10. Conclusion

Compute verification needs a claim about measurement and a claim about coverage. Neither follows from a valid signature alone. A useful verifier should preserve that distinction in its output: an interval over a named scope, a capacity allowance for gaps, and a separately justified budget for activity outside the inventory. The synthetic results demonstrate the consequence of this discipline. They do not demonstrate a secure meter. The next research step is to test whether a concrete meter and enrollment process can justify the assumptions needed to make these bounds useful.

## References

[1] Birkholz, H., Thaler, D., Richardson, M., Smith, N., and Pan, W. (2023). *Remote ATtestation procedureS (RATS) Architecture*. RFC 9334, Informational. https://www.rfc-editor.org/rfc/rfc9334

[2] NVIDIA. *GPU Claims — Advanced Documentation*. Vendor documentation, accessed 22 October 2026. https://docs.nvidia.com/attestation/advanced-documentation/latest/claims-guide/gpu_claims.html

[3] O'Gara, A., et al. (2025). *Hardware-Enabled Mechanisms for Verifying Responsible AI Development*. arXiv:2505.03742v1, preprint. https://arxiv.org/html/2505.03742v1

[4] Petrie, J., Aarne, O., Ammann, N., and Dalrymple, D. (2025). *Flexible Hardware-Enabled Guarantees for AI Compute*. arXiv:2506.15093v1, preprint. https://arxiv.org/abs/2506.15093

[5] Petrie, J., and Aarne, O. (2025). *Technical Options for Flexible Hardware-Enabled Guarantees*. arXiv:2506.03409v3, preprint. https://arxiv.org/abs/2506.03409

[6] Laurie, B., Messeri, E., and Stradling, R. (2021). *Certificate Transparency Version 2.0*. RFC 9162, Experimental. https://www.rfc-editor.org/rfc/rfc9162

[7] Jia, H., Yaghini, M., Choquette-Choo, C. A., Dullerud, N., Thudi, A., Chandrasekaran, V., and Papernot, N. (2021). *Proof-of-Learning: Definitions and Practice*. IEEE Symposium on Security and Privacy; author preprint arXiv:2103.05633. https://arxiv.org/abs/2103.05633

[8] Peigné, P., Nguyen, K., and Wang, P. (2026). *Zero knowledge verification for frontier AI training is possible*. arXiv:2606.05433v1, preprint. https://arxiv.org/html/2606.05433v1

[9] Ansari, S. (2026). *Hardware-Level Governance of AI Compute: A Feasibility Taxonomy for Regulatory Compliance and Treaty Verification*. arXiv:2604.04712v1, preprint. https://arxiv.org/html/2604.04712v1

[10] Kimpson, T., Baker, M., and Graham, E. (2026). *Can Power Draw Constrain Covert Compute? Limits of Analogue Verification for AI Governance*. arXiv:2610.07476v1, preprint. https://arxiv.org/html/2610.07476v1

## AI use and review disclosure

Codex generated this study, report, and synthetic analysis code. AI assistance was used for literature retrieval, protocol drafting, mathematical exposition, and software checks. The mathematical claims are conditional accounting statements. The numerical outputs come from the included Python script. No human review, external peer review, certification, endorsement, or institutional affiliation is claimed. The separate AI review and its scope are recorded in [reviews/technical_review.md](reviews/technical_review.md).

**Governance companion:** [From Compute Claims to Contestable Decisions](https://github.com/gavenren/ai-policy-governance-research/blob/main/studies/2026-10-22-compute-verification/paper.md).

**Project-requested model attribution:** GPT-6.1 Sol. **Project-requested reasoning attribution:** Ultra. These are owner-requested attribution labels, not independently verified runtime metadata.
