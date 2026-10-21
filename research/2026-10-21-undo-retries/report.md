# Undo after a crash: progress records and later edits

Date: 2026-10-21, America/Toronto.

Research note. This is a finite simulation of fixed rules. Codex generated the study and report. No human review or external peer review occurred.

## Abstract

An undo process can stop between a data change and its saved progress record. A restart can then omit a required step or repeat a completed step. We compare seven rules in 2,924 fully enumerated cases. Each case asks a rule to remove two completed increments and preserve later additive edits. The primary set has two crashes and 2,500 cases per rule. Saving progress before subtraction caused 1,300 false completion claims. Saving it after subtraction also caused 1,300 false claims, through a different failure. A fixed assignment with an atomic progress record caused 896 false claims, although each undo step ran exactly once. Atomic subtraction completed all primary cases correctly. This control needs a stronger storage capability and additive later edits. A rule that stopped after uncertainty made no false claim, but completed only 500 primary cases. These counts describe the declared model. They do not estimate website failure rates or AI agent skill.

## Research question and safety relevance

Which progress-record rules can undo two completed increments after crashes, while preserving later additive edits and avoiding false completion claims?

A computer-use agent can lose a reply after a write. Its own progress file can also lag behind the saved website state. A wrong completion claim can hide an omitted undo or an extra change. A repeated fixed assignment can remove later work. The model isolates these execution risks after the intended original action is known. It does not test how an agent selects the right object or undo target.

## Terms

- **Undo:** remove the two specified increments while preserving the scheduled later additions.
- **Durable:** survives a modelled crash.
- **Progress record:** one saved done flag per field.
- **Atomic:** the field operation and its done flag are saved together. No model state contains only one of those two changes.
- **Inverse:** subtract one to remove one completed increment.
- **Idempotent:** repeating an operation in isolation has the same final effect as applying it once. Assignment to a fixed value has this property. It can still remove an intervening edit.
- **False completion:** the rule claims completion, but the final fields differ from the reference.
- **Refusal:** the rule makes no completion claim. A refusal is not counted as task success.

## Related work and contribution

Microsoft describes compensation that can fail and resume. It also warns that restoring an old state can remove concurrent work. AWS states that request identity and its mutations need atomic recording. These are established requirements, not new proposals in this report. [Microsoft documentation](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction), [AWS guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).

RIFL gives a direct prior example of a repeated absolute write that overwrites another client's intervening write. It also requires a durable operation result and completion record to be saved atomically. Our atomic control illustrates this requirement in a small undo model. It does not implement or improve RIFL. [Lee et al., SOSP 2015, Figure 2 and Section 4.1](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf).

UndoBench is the closest current agent-evaluation study found. Its fault classes include interruptions during compensation and after a reply but before a checkpoint. It separates calls, saved mutations, and semantic effects. Thus compensation fault tests and separate state/effect checks are not new here. UndoBench is a preprint; its code and results were not reproduced for this study. [Sah et al., arXiv:2610.05622v1, Sections 2.1–2.4](https://arxiv.org/html/2610.05622v1).

The specific contribution is a complete finite regression corpus for seven progress-record rules, with matched crash cuts, later additions, raw traces, refusal counts, and small failure examples. The [October 18](../2026-10-18-retry-retention/report.md), [October 19](../2026-10-19-safe-undo/report.md), and [October 20](../2026-10-20-undo-missing-history/report.md) studies assumed atomic execution at the boundary tested here. This study adds interruption within a two-field undo. It does not repeat their main questions. The limited search does not establish global novelty. [Search terms, dates, read scopes, and unavailable leads](source_search.md) are retained.

## Method

### Frozen plan

The [plan](plan.md), [configuration](config.json), and source search were saved before implementation and execution. [freeze.json](freeze.json) records their hashes and time. Six hypotheses concern repeated steps, omitted steps, fixed assignments, the atomic inverse control, and refusal costs. All were tested with exact case counts. There was no training set, test-set selection, random sampling, or fitted model.

### State and reference

Initial fields x and y are each 0 or 1. The original action has already added one to each. Both progress flags start false. Later external commands add or subtract one from one field. For each case, the reference is the initial state plus every scheduled external command. It excludes the two original increments. Only the evaluator uses the full external schedule.

All fields are unbounded integers. Reads and writes are exact. Progress flags are unique to this task, durable, and uncorrupted. The model has one recovery worker. No external command sets an absolute value. This matters: additive edits commute with inverse subtraction. The result does not extend to arbitrary later assignments.

### Fault schedule

An attempt has four logical slots, two per field. A crash cut executes zero through four slots. A crash clears temporary state but preserves fields and durable flags. The assigned external word then runs. A word is a list of zero or more external commands. After all crashes, one final attempt runs without a fault. All rules receive the same cuts and external words.

A cut after slot four still has an external word and a later audit. A stopped rule also receives all later external commands. Claims are scored only at the common final horizon. No rule leaves a case early. A fault-free final attempt is an explicit assumption.

Atomic and unmarked rules use padding slots. A common cut is a matched logical intervention, not equal time or equal instruction count. Different cuts can therefore produce identical prefixes for a rule. We retain that multiplicity. Counts are not probabilities for natural failures.

### Rules

For each field, A is its first slot and B its second. Assignment always uses the initial value cached before the original action. A done flag makes later attempts skip that field.

| Rule ID | Slot A | Slot B | Claim at final horizon |
| --- | --- | --- | --- |
| restart_inverse | Subtract one on every attempt | No operation | Always |
| before_inverse | Save done if not already done; set temporary pending | Subtract if pending | Both flags are done |
| after_inverse | Subtract if not done; set pending | Save done if pending | Both flags are done |
| after_set | Assign initial value if not done; set pending | Save done if pending | Both flags are done |
| stop_on_uncertainty | Use after_inverse until the first crash; then stop permanently | Same stopping rule | Both flags are done; otherwise refuse |
| atomic_inverse | Subtract and save done atomically, if not done | No operation | Both flags are done |
| atomic_set | Assign initial value and save done atomically, if not done | No operation | Both flags are done |

The early-marker baseline incorrectly treats an intent record as proof of completion. The atomic rules have a stronger server capability. A client-local log cannot make a separate website write atomic. Per-field atomicity also does not make the two-field undo an all-or-nothing transaction.

### Corpus and measures

| Setting | Crashes | Maximum commands after each crash | Cases per rule |
| --- | --- | --- | --- |
| No fault | 0 | 0 | 4 |
| One crash | 1 | 2 | 420 |
| Two crashes, primary | 2 | 1 | 2,500 |

The full corpus has 2,924 cases and 20,468 rule outcomes. A planned control uses only empty external words. Its primary subset has 100 cases. The one-crash sensitivity set includes pairs of external commands that cancel.

Each result gives the final fields, flags, claim, and full trajectory. An application count records each applied undo command, including an assignment that leaves the value unchanged. A separate count records actual value changes. These are not network-call counts or semantic effect counts. A repeated step has more than one application. An omitted step has none. Correct final fields and once-only application are distinct checks.

All outcomes are classified as correct completion, false completion, refusal with correct state, or refusal with incorrect state. Full enumeration removes sampling error within this corpus. There is no justified population distribution, confidence interval, or significance test. The uncertainty is whether this model represents a real task. No website or connected account was tested in this run.

## Results

### Primary comparison

Each row contains the same 2,500 case schedules. The four outcome columns sum to 2,500.

| Rule | Correct completion | False completion | Refusal: correct state | Refusal: incorrect state |
| --- | --- | --- | --- | --- |
| restart_inverse | 100 | 2,400 | 0 | 0 |
| before_inverse | 1,200 | 1,300 | 0 | 0 |
| after_inverse | 1,200 | 1,300 | 0 | 0 |
| after_set | 1,172 | 1,328 | 0 | 0 |
| stop_on_uncertainty | 500 | 0 | 500 | 1,500 |
| atomic_inverse | 2,500 | 0 | 0 | 0 |
| atomic_set | 1,604 | 896 | 0 | 0 |

Saving the marker earlier and later produced the same number of false claims, with different causes. Early markers omitted required steps. Late markers repeated steps. Assignment reduced neither problem to a simple duplicate count: atomic_set applied both steps once, but still removed later work in 896 cases.

### Applied work

These are exact primary-set counts. Repeated and omitted columns count cases. The last two columns total commands across all 2,500 cases. They are not latency or service-call measures.

| Rule | Cases with repeated step | Cases with omitted step | Applications | Value-changing applications |
| --- | --- | --- | --- | --- |
| restart_inverse | 2,400 | 0 | 11,000 | 11,000 |
| before_inverse | 0 | 1,300 | 3,600 | 3,600 |
| after_inverse | 1,300 | 0 | 6,600 | 6,600 |
| after_set | 1,300 | 0 | 6,600 | 5,264 |
| stop_on_uncertainty | 0 | 1,500 | 3,000 | 3,000 |
| atomic_inverse | 0 | 0 | 5,000 | 5,000 |
| atomic_set | 0 | 0 | 5,000 | 4,560 |

### Controls and sensitivity

All seven rules completed all four no-fault controls correctly. Without external edits, both assignment rules completed all 100 primary subset cases correctly. In that subset, after_set still repeated a step in 52 cases. State equality alone therefore did not show once-only application.

| Rule | False claims: primary, no external edits (100 cases) | False claims: one crash (420 cases) |
| --- | --- | --- |
| restart_inverse | 96 | 336 |
| before_inverse | 52 | 168 |
| after_inverse | 52 | 168 |
| after_set | 0 | 224 |
| stop_on_uncertainty | 0 | 0 |
| atomic_inverse | 0 | 0 |
| atomic_set | 0 | 160 |

The stop rule made no false claim in either fault setting. With two crashes, it refused 2,000 cases. In 500 of those cases, the fields were already correct but the last progress record was absent. Its refusal prevented an unsupported claim, but did not complete the task.

### Small failure examples

Cases start with initial (0,0), then the original action produces (1,1).

- Case 26 has a cut after slot 1 and no external edit. before_inverse records x as done without subtracting. Its final state is (1,0), and it claims completion. after_inverse instead subtracts x before the crash, then repeats it. Its final state is (-1,0), with a completion claim. The reference is (0,0).
- Case 6 crashes before any undo slot, then an external command adds one to x. atomic_set applies both undo assignments once and ends at (0,0). The reference is (1,0). There is no duplicate step; the fixed target is wrong for the later state.
- Case 68 crashes after slot 3 with no external edit. stop_on_uncertainty has already subtracted both fields, but the y done flag is absent. It refuses with the correct final state (0,0).

The [witness file](results/witnesses.json) retains the first case for every nonempty rule/outcome category. The [paired counts](results/pairs.json) compare each rule with atomic_inverse on the same schedules. All six frozen hypotheses held in the stated tests. Negative results include zero false claims for the stop rule and zero failures for both assignment rules without external edits.

## Derivation for the additive model

Let b_f be an initial field, E_f the sum of all external additions on it, and n_f the number of applied inverse commands. The original action adds one. Every inverse subtracts one. Hence the final value is b_f + 1 + E_f - n_f. The reference is b_f + E_f. Their difference is 1 - n_f. This identity was checked 29,240 times across both fields for the five inverse-only rules.

For atomic_inverse, a field starts with n_f=0 and done=false. The sole enabled undo transition changes both to n_f=1 and done=true. Subsequent attempts skip it. Crashes preserve both values, and external additions do not change either. Thus n_f is at most one. The final complete attempt applies any remaining enabled step, so n_f is at least one at the final audit. Therefore n_f=1 and the state error is zero for each field. This derivation assumes exact atomic durable transitions, the declared additive commands, completed original increments, and a final attempt without a fault. It does not establish a browser implementation or simultaneous visibility of both undo steps.

Assignment lacks this sum identity. An assignment can erase earlier external additions, even with one application. This is why atomic progress recording alone does not establish the correctness of the undo command.

## Discussion

The evidence separates two obligations. A recovery system must establish which undo steps occurred. It must also use an undo operation that preserves the relevant later work. Atomic progress recording addresses the first obligation in this model. It does not make a stale fixed assignment satisfy the second.

Stopping after uncertainty avoided false completion, but left many tasks unresolved. A real system could gather more evidence or seek help. Those actions were not modelled. A correct final state with no receipt is also different from proof that an operation happened exactly once.

## Limitations

This is a small, selected finite corpus. It uses two fields, additive commands, four initial states, up to two crashes, and one final attempt without a fault. It excludes assignments by later writers, adaptive users, overlapping recovery workers, stale reads, delayed requests, flag expiry, ID reuse, corrupted records, constraints, irreversible actions, and communication failures during the final attempt. Initial values largely test translation consistency; they are not independent real tasks.

Padding affects case multiplicity. Equal weighting gives no real-world event distribution. The atomic control has a stronger capability than the other rules. It is not an equal-capability comparison of reasoning skill. The rules are fixed programs, not a sampled language-model agent. There is no evidence here about production frequency, latency, throughput, general agent skill, or whether a connected service exposes the required atomic operation. The study does not solve the earlier reports' missing-history or field-observation problems.

## Ethical and misuse considerations

All data are synthetic. This run created no account records, sent no messages, and used no human participants. The package contains no private account data. Treating its counts as a deployment guarantee could cause harm by encouraging unsafe automatic undo. The report limits the recommendation to systems that can establish the stated command and storage assumptions. The examples contain no actionable harmful content.

No source code, dataset, paper text, or image was copied from the cited work. Sources are attributed. Third-party rights remain with their owners. No new license is assigned to this repository.

## Reproduction and review

See the [README](README.md) for exact commands and file roles. The full inputs, outcomes, and compressed trajectories are included. The experiment uses Python 3.13.7 and the standard library on macOS arm64. The first main run used 2.45 CPU seconds and 4.31 wall seconds; its reported peak resident memory was 23,805,952 bytes. [Execution metadata](results/execution.json) retains exact values. No GPU, paid compute, or model API call was part of the experiment. No random seed applies.

The [review record](review.md) gives the separate implementation comparison, clean reproduction, source checks, and release checks. The [NeurIPS Paper Checklist](https://nips.cc/public/guides/PaperChecklist) was used as a review aid. This is not a claim of conference approval, submission compliance, or certification.

## AI tools and human review

Codex generated the model plan, programs, analysis, and report. A separate Codex agent checked primary sources and the question. Another agent built an evaluator from the frozen plan before reading the main implementation or results. A further agent reviewed the report and evidence. The chat system identified the assistant as GPT-6 based; an exact serving build was not exposed. The evaluated rules contain no language model. Browser tools were used for GitHub publication only. No human reviewed this study. Agent checks are not external peer review.

## References

1. Microsoft Azure Architecture Center. *Compensating Transaction pattern*. Page updated 2026-04-20. [Official page](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction).
2. Malcolm Featonby. *Making retries safe with idempotent APIs*. AWS Builders' Library. The page gave no publication date; the PDF indicates 2020 copyright. [Official page](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
3. Collin Lee, Seo Jin Park, Ankita Kejriwal, Satoshi Matsushita, and John Ousterhout. *Implementing Linearizability at Large Scale and Low Latency*. SOSP, 2015. DOI: 10.1145/2815400.2815416. [Author-hosted paper](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf).
4. Dolly Sah, Tanmay Sah, Harshul Jain, and Tanya Sah. *UndoBench: Separating Task Competence from Recovery Capability in Tool-Using AI Agents*. arXiv:2610.05622v1, 2026-10-04. Preprint. [Checked text](https://arxiv.org/html/2610.05622v1).
5. NeurIPS. *Paper Checklist Guidelines*. Retrieved 2026-10-21 through the official mirror after the first neurips.cc request failed. [Guide](https://nips.cc/public/guides/PaperChecklist).

All external references were retrieved on 2026-10-21. The search record states exactly which sections were read. Unread results are not used as evidence.
