# When correct undo leaves an incorrect decision history

Date: 2026-10-22, America/Toronto.

## Abstract

An undo can restore every field and still leave decisions that do not fit one complete undo in time. We tested this limit with real local SQLite files and synthetic data. The experiment used 1,536 primary trials, 512 forced-opening trials, and 768 serial controls. A child process exited at a declared boundary. Two ordered reader jobs then saved decisions before recovery finished. Separate field commits restored the source in all 512 primary cases. However, 256 cases failed the joint decision-order check. Of these, 32 passed each separate decision check. A durable gate prevented accepted decisions during incomplete undo, but refused all 1,024 primary reader jobs. One transaction for the complete undo accepted those jobs and had no decision-order violations. These counts describe the selected finite corpus. They do not estimate website risk or measure an AI agent's performance.

## Research question and safety relevance

Can correct final fields conceal an invalid ordered decision history? Can each saved decision be compatible with a complete state while the pair is incompatible?

An agent can act on data while another operation is being undone. A later correct screen cannot erase an earlier decision. A completion statement must therefore name what was checked. This study separates source restoration, individual decision validity, ordered decision validity, and reader service.

A **transaction** is a set of database operations that commits as one unit. **Atomic undo** means that the whole undo is visible as one transition. A **receipt** is a saved record that one field step was applied. A **gate** is a saved flag that prevents a reader from using fields while undo is incomplete. A **predicate** is a fixed function that returns zero or one. An **oracle** is the rule used to decide whether an observed result is permitted.

## Related work and contribution

Sagas already permits partial work to be visible and explains limits of later compensation. Its subtransactions must preserve the required consistency conditions. This test does not refute that design. [Garcia-Molina and Salem, 1987](https://sigmodrecord.org/1987/12/09/sagas/)

Atomix v2 distinguishes provider-visible effects from views supplied to readers that use its runtime. Compensation cannot remove past observations. Its stronger guarantees require complete mediation and correct scope information. Our small gate is not an Atomix implementation. [Mohammadi et al., preprint, 2026](https://arxiv.org/html/2602.14849v2)

Microsoft's Saga guidance describes missing isolation across services and application-level locks. UndoBench separates final conditions from effect history and distinguishes several kinds of recovery faults. These ideas are established; this study does not claim to introduce them. [Microsoft](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga), [Sah et al., preprint, 2026](https://arxiv.org/html/2610.05622v1)

The [October 21 repository study](../2026-10-21-undo-retries/report.md) tests progress receipts and final additive fields. It excludes simultaneous visibility. The present contribution is a small, repeatable database test of that excluded condition. It adds an exact two-reader oracle, all 16 Boolean predicates, physical database evidence, and a witness that passes separate checks but fails a joint check. The [source review](source_review.md) and [supplement](source_supplement.md) record searches, dates, reading limits, and excluded leads. The limited search does not prove novelty or priority.

## Method

The [plan](plan.md) and [configuration](config.json) were frozen before implementation or execution. The question, hypotheses, baselines, measures, exit boundaries, corpus, and stop rules were specified in advance. [freeze.json](freeze.json) records their hashes and save time. No hypothesis or case was selected after observing results.

### State and rules

Each case has a fresh database. Its source fields start at P=(1,1). Undo must reach Q=(0,0). It subtracts one from each field and saves a unique receipt with the subtraction. Both field orders, xy and yx, are tested. There is one source writer. Readers only append decision and action records.

| Rule | Commit boundary | Reader behavior during incomplete undo |
| --- | --- | --- |
| Separate | One field and its receipt per transaction | Read the committed partial state |
| Durable gate | Saved closed gate, then separate field commits | Refuse until recovery verifies both fields and receipts and opens the gate |
| Whole transaction | Both fields and both receipts in one transaction | Read the last complete committed state |
| Forced open gate, sensitivity only | Same field commits as the durable gate | Driver deliberately opens the gate before recovery; readers can use partial fields |

The forced opening is an intentional invalid release. It is not a natural timeout, a lease test, or a provider defect. The first audit occurs before this intervention; a separate audit records the opened gate.

The first worker calls `os._exit(73)` after its first field step. For separate commits, the first step has committed. For the whole transaction, the step has executed but has not committed. These are matched logical boundaries, not equal commit boundaries, amounts of work, times, or failure probabilities.

The parent waits for the exit. Reader job 0 completes before reader job 1 starts. Each uses a new connection and one transaction to check the gate, read both fields, compute its predicate, and save its decision. A decision of one also saves a synthetic action row. Zero decisions are retained. A refusal saves no decision or action and is not retried. Both jobs occur within the larger undo interval, from its first invocation to recovery completion.

A new worker then completes missing steps. Final source completion requires Q, exactly one receipt per field, and an open gate. New probe jobs 2 and 3 run after recovery. They check that Q is readable and the gate is open. These probes are not replacements for refused jobs and do not enter the primary score. All effects are local test records; no external action is sent.

### Decision oracle

Predicate p has output `(p >> (2*x+y)) & 1`. The 16 values p=0 through 15 cover every Boolean function of two bits. For accepted jobs with functions f then g, an atomic undo can occur before both, between them, or after both. The permitted pairs are:

`(f(Q), g(Q))`, `(f(P), g(Q))`, `(f(P), g(P))`.

Duplicate pairs are removed. A **serial violation** means that the saved ordered decision pair is absent from this set. A **local endpoint check** accepts each decision separately if it matches its function at P or Q. A **joint-only violation** fails the ordered check but passes both separate checks. An empty accepted sequence passes the oracle but supplies no reader service.

The oracle scores the declared predicate outputs. It does not score the full stored x,y audit columns. Every accepted reader under separate commits observes a mixed state, even when its predicate output has a permitted explanation. Passing this output check does not establish general serializability of all observations. SQLite's individual transactions remain within its documented isolation model. The larger application undo spans several transactions. [SQLite isolation documentation](https://sqlite.org/isolation.html)

### Corpus, controls, and uncertainty

Each primary rule has 2 orders × 16 first predicates × 16 second predicates = 512 cases. Three primary rules give 1,536 cases. Forced opening adds 512. Controls place an uninterrupted whole undo before, between, or after the two jobs: 3 × 16 × 16 = 768 cases. The total is 2,816. Nineteen additional hand checks include function identities, logical witnesses, a rolled-back reader, and eight exits before the first update.

This is complete enumeration of a designed corpus. It is not random sampling. No seed, confidence interval, significance test, or population failure rate is appropriate. One truth-table input is unused for each selected order, so some cases have identical behavior. These are not independent natural tasks.

Unexpected process, SQL, logging, schema, or integrity failures would stop the run and remain unknown. An unexpected but fully observed outcome would remain a valid adverse result. No case was replaced or excluded. The resource gates were 600 cumulative local CPU seconds and 1,200 wall seconds per full run, with at most two full runs.

## Results

### Primary results

All 2,816 assigned cases were valid. None was unknown. All reached the required final source state and passed both later probes. Counts below are cases, except for the accepted and refused job columns.

| Primary rule | Cases | Correct final source | Accepted jobs | Refused jobs | Serial violations | Local endpoint failures | Joint-only violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Separate | 512 | 512 | 1,024 | 0 | 256 | 224 | 32 |
| Durable gate | 512 | 512 | 0 | 1,024 | 0 | 0 | 0 |
| Whole transaction | 512 | 512 | 1,024 | 0 | 0 | 0 | 0 |

The gate's zero violations came from refusal during the interrupted interval. It did not complete those reader jobs. Whole-transaction readers observed P after SQLite discarded the uncommitted first step. Recovery later reached Q. Correct final fields alone would have missed every earlier serial violation.

### Sensitivity and controls

| Group | Cases | Correct final source | Accepted jobs | Refused jobs | Serial violations | Local endpoint failures | Joint-only violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Forced open gate | 512 | 512 | 1,024 | 0 | 256 | 224 | 32 |
| Serial boundary controls | 768 | 768 | 1,536 | 0 | 0 | 0 | 0 |

Forced opening matched separate commits for every paired decision outcome. All 768 controls matched the outputs for their exact known cut. All 19 hand checks passed. These results support H1 through H6 in the frozen plan within the stated scope.

### A saved witness

Case 203 uses order xy, f=x (predicate 12), and g=y (predicate 10). The first committed step leaves M=(0,1). Both readers observe M.

| Check or observation | Result |
| --- | --- |
| First saved decision, x | 0; permitted separately because x(Q)=0 |
| Second saved decision, y | 1; permitted separately because y(P)=1 |
| Saved ordered pair | (0,1) |
| Permitted atomic-undo pairs | (0,0), (1,0), (1,1) |
| Final fields after recovery | (0,0) |

The pair needs undo to be before the first job and after the second job. That cannot fit their observed order. The second job's synthetic action remains in the final database. This is evidence of a failed declared output contract, not evidence of real downstream harm. See [witnesses.json](results/witnesses.json) and the physical database `trial-0203.sqlite3` in the archive.

### Analytic and execution checks

For one field order, use the endpoints and the partial state as three distinct inputs. Across the 16 endpoint assignments for two predicates, the total number of permitted pairs is 32. Separate endpoint checks permit 36 pairs. Two unused truth-table bits multiply each count by four. Thus one order has 256 cases, 128 serial violations, 112 local failures, and 16 joint-only failures. Two orders double these counts. The [independent review](independent_review.md) gives the complete derivation.

The independent evaluator was saved before its author read the main code, schema, or results. It matched all 2,816 logical cases. A separate comparison reopened all 2,825 physical databases from the archive, including hand-control databases. It checked their tables, integrity, SQL dumps, and all 4,872 worker logs. The first comparison recorded 127,899 checks without a difference. These checks are automated evidence, not independent human review.

The second full run used fresh directories and unchanged source. All six deterministic logical files matched byte for byte. It repeated all 2,816 cases and all hand checks. The second run used 374.62 CPU seconds and 397.73 monotonic seconds. Its UTC stamps also span 397.73 seconds. Worker logs and both execution receipts are retained. The [reproduction review](reproduction_review.md) states what was compared. These are two executions of the same corpus, not 5,632 different test cases.

## Discussion

The result identifies three different obligations. A receipt can prevent a repeated field effect. A final audit can establish source restoration. A joint history check can establish compatibility of selected earlier decisions with a single complete undo. None of these statements should be substituted for the others.

The gate and whole-transaction rules use different capabilities. A gate requires every relevant reader to obey it and may withhold service. A whole transaction requires one atomic boundary across all fields. The experiment does not rank them as equal-capability AI methods. The forced opening shows that an incomplete-release error removes the gate's protection in this test.

A practical completion statement should state the checked scope. For example: the source fields were restored; earlier decisions were not retracted. A stronger statement about the complete operation needs evidence about those decisions and the interfaces that can observe partial work. This is an interpretation of the finite result, not a tested browser policy.

## Limitations

The workload has two bits, two readers, one source writer, two field orders, and one controlled exit boundary. SQL statements run in a deliberate schedule, not under timing contention. The worker exit is real, but the workload and failures are designed. There is no operating-system crash, power loss, distributed service, arbitrary crash time, external irreversible action, or language-model benchmark.

Readers run between a terminated first attempt and recovery. Complete gate mediation, correct schema, unique receipts, and reliable local database transactions are assumptions. The test excludes gate-bypassing readers, later source edits, changing predicates, missing history, and failures during recovery. Post-recovery probes show later availability only at the scheduled point. They do not measure latency or recovery availability in general.

The output oracle is deliberately narrower than all stored observations. Correct Boolean outputs can conceal mixed input fields. The corpus's counts depend on its complete truth-table enumeration and repeated behavioral cases. They must not be reported as rates for real agents or websites. The mechanisms are known. No general novelty, optimality, or universal safety guarantee is claimed.

## Ethical and misuse considerations

All data and actions are synthetic local records. No private account data, messages, or real user events were used. No production website was tested in this run. The released code demonstrates a bounded local consistency check and does not include an exploit of a real service. Misuse of the result could include treating a zero count as a general safety certificate or hiding refusals as successes. The report keeps those outcomes separate.

No source dataset, code, figure, or paper is republished. SQLite is public-domain software. No license has been selected for the user's new code or report; this package does not add one. [SQLite copyright statement](https://sqlite.org/copyright.html)

## Reproduction and resources

Use the commands in [README.md](README.md). The implementation uses Python 3.13.7, SQLite 3.50.4, and zlib 1.2.12 on Darwin 25.6.0, arm64. Only the Python standard library is required. WAL and FULL synchronous mode are set explicitly; private-cache connections use BEGIN IMMEDIATE and a 5,000 ms busy timeout. Physical files are checkpointed before archiving. [SQLite WAL documentation](https://www.sqlite.org/wal.html)

The first run used 375.59 measured CPU seconds for the parent and exited children. Its monotonic duration was 400.69 seconds. Its saved UTC stamps span 533.74 seconds. The cause of that difference was not established. Both recorded durations are below the wall gate. These values record resource use; they are not a performance comparison. The receipt preserves both clocks. No paid compute or new model API call was used for the experiment.

## AI use and review status

Codex generated this study and report. The main agent selected the question, managed the work, wrote the report, and checked publication. Separate Codex agents searched sources, reviewed the design, wrote and ran the database implementation, wrote the independent evaluator, and reviewed the final package. These are distinct AI roles in one session, not human authors. The exact model build was not exposed in the experiment record. No model was queried inside a scored trial. No human review or external peer review occurred.

The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was used as a review aid. The [checklist](checklist.md) maps the relevant items to evidence. This is not NeurIPS approval, certification, or a claim of submission compliance.

## References

Full records are in [references.bib](references.bib). The report links each external technical claim to its primary source. The source review states which sections were read and which leads were not used.
