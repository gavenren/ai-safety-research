# Safe undo with missing action records: an exact finite study

Date: 2026-10-20, America/Toronto.

## Abstract

An agent may need to undo its action after later edits. A partial action log can support more than one correct undo target. We apply established reasoning over compatible histories to a small undo model. The model includes 44,444 cases with up to four later commands and every possible deletion mask. At the planned length-four setting, a target-agreement rule completes correctly in 26,380 of 40,000 cases and makes no false completion claims when the missing-command bound is correct. A rule that requires no possible loss completes 2,500 cases. A visible-log replay check makes 1,808 false claims. With a deliberately false bound, target agreement makes 1,130 false claims across 41,320 missing-log cases. These are exact counts for a defined model, not measured website or AI-agent error rates.

## Research question and safety relevance

Can an agent select a safe undo target when some action records are missing, but the number of missing commands has a trusted upper bound?

A **history** is an ordered list of commands. A **compatible history** agrees with the visible log, the missing-command bound, and the current fields. A **counterfactual target** is the record that the same later commands produce if the original agent action is omitted. A **false completion** is a completion claim with fields that differ from that target. A **refusal** leaves the current record unchanged and makes no completion claim.

The [October 19 study](../2026-10-19-safe-undo/report.md) found that its improved controller needs trusted complete history. A hidden assignment can leave the current value unchanged while changing the correct undo target. Today's study replaces the complete-history premise with an explicit bound on missing commands. It tests target selection only. It does not test browser execution.

## Related work and contribution

Korth, Levy and Silberschatz study semantic compensation using hypothetical executions that omit an earlier transaction. They also address the effect of later program behavior. Our target keeps the later commands fixed, so it has a narrower meaning. [Korth et al., 1990](https://www.vldb.org/conf/1990/P095.PDF)

The closest method is the treatment of lossy event streams by Kushwaha, Purandare and Dwyer. Their checked preprint represents an observation through compatible executions and tracks possible states. It includes dropped-count and silent-drop models. Our agreement rule applies this established direction to undo targets and a global loss bound. We do not claim to improve their general monitor construction. [Kushwaha et al., 2020, preprint](https://arxiv.org/html/2004.04214v1)

Wang and coauthors require a recovered sequence to contain the observed sequence as an ordered subsequence. Their work seeks minimum-change and top-k recovery under process constraints. We retain every compatible history within the bound, rather than select one reconstruction. Agreement also follows the established idea of answers that hold across possible complete worlds. [Wang et al., 2013](https://sxsong.github.io/doc/13vldb.pdf), [Amendola and Libkin, 2018](https://www.ijcai.org/proceedings/2018/233)

Current agent recovery work also uses shared action logs. LogAct states limits on semantic recovery and discusses external changes. Our model does not test its system. [Balakrishnan et al., 2026, preprint](https://arxiv.org/html/2604.07988v1)

The contribution is a complete regression corpus, a comparison of five rules, a bound-sensitivity check, and small failure examples for a fixed undo model. Possible-world reasoning, compensation, and agreement across candidate histories are not new methods. The [source record](source_search.md) gives the search terms, dates, checked sections, and inaccessible leads. This limited search does not establish global novelty.

## Method

The [plan](plan.md) and [configuration](config.json) were saved before execution. Their hashes and the freeze time, 2026-10-20 at 15:05:49 UTC, are in [plan_freeze.json](plan_freeze.json).

A record contains an integer x and a bit y. A bit has value 0 or 1. Each initial field ranges over {0,1}. The agent adds 1 to x. Later commands are:

| Command | Effect |
| --- | --- |
| add1 | Add 1 to x. |
| sub1 | Subtract 1 from x. |
| set0 | Set x to 0. |
| set1 | Set x to 1. |
| flip_y | Replace y with 1-y. |

For each initial record, enumerate all later words of length L=0 through 4. For each word, enumerate all 2^L masks that retain or omit its commands. Mask bit i=1 retains command i, starting at bit 0. The visible commands remain accurate and in order. There are 4*sum(10^L)=44,444 cases. Distinct masks remain separate cases even if their visible logs match.

Let k be the actual number of missing commands. The tight upper bound is B=k. The loose upper bound is B=k+1. The stress test uses the false upper bound B=k-1, only when k>0. A tight upper bound does not mean an exact-count constraint: the controller must consider zero through B missing commands. B is an assumed trusted input in the first two settings. The test generator provides it; this study supplies no way to obtain it from a website.

The controller receives the initial fields, current fields, visible commands, and B. It does not receive the full history, actual length, mask, missing count, or evaluator target. A candidate word must contain the visible word as an ordered subsequence. Its length can exceed the visible length by at most B. It must reproduce both current fields after the agent increment. Candidate length reaches five in the loose setting, although actual corpus histories end at length four.

Let C be the candidate-history set. Let T contain the distinct counterfactual targets of C. **Target agreement** completes only when C is nonempty and T contains exactly one record. It writes that record. An empty C means inconsistent evidence; it is never agreement.

The comparison uses these five rules:

| Rule | Decision |
| --- | --- |
| Visible compensation | Keep current x if a visible command assigns x. Otherwise subtract 1. Keep current y. Claim complete. |
| Replay guard | Use visible compensation only if replay of the visible commands after the agent increment matches both current fields. Otherwise refuse. |
| No-loss guard | Complete only if B=0 and visible replay matches current fields. Use the visible log's counterfactual target. |
| Target agreement | Complete only if all compatible histories have one target. Otherwise refuse. |
| Full-history reference | Use the true full history to select the target. This is an ideal control with more information. |

All reads, decisions, and writes are exact and atomic: they occur as one indivisible operation. No other write can occur between observation and action. A selected write is applied correctly. There are no stale reads, wrong record identities, lost replies, or retries. These assumptions isolate target selection from execution faults.

The four outcomes are correct completion, false completion, refusal with correct current fields, and refusal with incorrect current fields. The last two distinguish a safe refusal from a completed task. The primary comparison uses all L=4 cases. A separate table includes only L=4 cases with missing commands.

## Results

### Planned length-four comparison

Each row contains the same 40,000 cases with the tight upper bound. The four outcome columns sum to the case count.

| Rule | Correct completion | False completion | Refusal, correct fields | Refusal, incorrect fields |
| --- | ---: | ---: | ---: | ---: |
| Visible compensation | 28,800 | 11,200 | 0 | 0 |
| Replay guard | 12,600 | 1,808 | 21,456 | 4,136 |
| No-loss guard | 2,500 | 0 | 32,640 | 4,860 |
| Target agreement | 26,380 | 0 | 10,120 | 3,500 |
| Full-history reference | 40,000 | 0 | 0 | 0 |

Source: the tight/L4 rows in [summary.csv](results/summary.csv). Target agreement gives 23,880 more correct completions than the no-loss guard in this corpus. It still refuses 13,620 cases. Refusal is not evidence that undo was completed.

The separate missing-command subset has 37,500 cases:

| Rule | Correct completion | False completion | Refusal, correct fields | Refusal, incorrect fields |
| --- | ---: | ---: | ---: | ---: |
| Visible compensation | 26,300 | 11,200 | 0 | 0 |
| Replay guard | 10,100 | 1,808 | 21,456 | 4,136 |
| No-loss guard | 0 | 0 | 32,640 | 4,860 |
| Target agreement | 23,880 | 0 | 10,120 | 3,500 |
| Full-history reference | 37,500 | 0 | 0 | 0 |

### Full corpus and bound sensitivity

This table reports target agreement across all lengths. The false-bound row excludes the 3,124 cases with no missing command.

| Bound setting | Cases | Correct completion | False completion | Refusal, correct fields | Refusal, incorrect fields |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tight upper, B=k | 44,444 | 29,178 | 0 | 11,246 | 4,020 |
| Loose upper, B=k+1 | 44,444 | 26,658 | 0 | 12,270 | 5,516 |
| False upper, B=k-1 | 41,320 | 19,624 | 1,130 | 15,678 | 4,888 |

The honest looser bound loses 2,520 correct completions. Its target set contains the tight target set in all 44,444 paired cases. Each loose completion is also a tight completion with the same target. A false bound can exclude the true history and support a wrong completion.

Across the full tight corpus, the replay guard makes 2,052 false claims. The no-loss guard completes correctly 3,124 times. The full-history reference completes correctly in all 44,444 cases. All rule, length, and missing-count summaries are in [summary.csv](results/summary.csv).

### Distinct observations

Case counts weight initial records, full histories, and masks equally. They do not represent independent sampled trials. For a second view, count each unique `(initial,current,visible,B)` observation once:

| Setting | Unique observations | No target | One target | Multiple targets | Multiple histories, one target |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tight upper | 7,318 | 0 | 6,482 | 836 | 2,730 |
| Loose upper | 7,318 | 0 | 5,624 | 1,694 | 5,484 |
| False upper | 4,194 | 2,836 | 1,134 | 224 | 400 |

The last column is a subset of the one-target column. It shows that selecting a target need not require recovery of one exact history. Observations can occur in more than one setting. The union has 16,146 unique observations. An observation with one target under a false bound can still be wrong for an actual history that the bound excludes.

### Small examples

The following are the first tight-bound examples under the plan's fixed ordering, plus the first false-bound failure. A several-histories example occurs earlier if loose bounds are included. All start at `(0,0)`; the agent first changes the record to `(1,0)`. Full machine-readable examples are in [witnesses.json](results/witnesses.json).

- **Safe despite a missing record:** a hidden add1 leaves `(2,0)`. With an empty visible log and B=1, only add1 fits. Its target is `(1,0)`. Target agreement completes; the no-loss guard refuses.
- **Fields match an incomplete replay:** a hidden set1 leaves `(1,0)`. The empty visible log also leaves `(1,0)` after the agent increment. The replay guard subtracts 1 and claims completion at `(0,0)`. The true target is `(1,0)`. With B=1, target agreement sees both the empty history and set1, and refuses.
- **False bound causes a false claim:** use the same hidden set1 but supply B=0. The only admitted history is empty. Target agreement now selects `(0,0)` incorrectly. A current-field match does not prove that the loss bound is correct.
- **Two histories, two targets:** current `(0,0)`, empty visible log, and B=1 fit hidden sub1 and hidden set0. Their targets are `(-1,0)` and `(0,0)`. A rule with only this observation cannot choose one target that is correct for both.
- **Several histories, one target:** actual add1 followed by set0, visible set0, and B=1 give five compatible histories. All have target `(0,0)`. Examples are set0 alone and add1 followed by set0. Exact history recovery is unnecessary here.

## Why the rule works under its assumptions

These are direct applications of established set reasoning, not new general theorems.

If the loss bound is correct, the true history belongs to C. Its true target therefore belongs to T. If T has one member, that member must be the true target. Exact execution of that target gives correct completion.

Increasing B can only add candidate histories. It cannot remove targets. A nonempty larger target set with one member therefore has the same member as the smaller nonempty target set. This proves the paired completion condition tested in the study.

If two compatible histories have different targets, both produce the same controller inputs. One fixed target cannot be correct for both. The controller must refuse, obtain additional evidence, or accept the possibility of an error. This statement concerns a zero-error target guarantee under the stated observation model.

For this command alphabet, if a later set0 or set1 occurs, it removes the agent's increment from all subsequent x values. Otherwise the increment remains exactly 1. Thus the target x is either current x or current x minus 1. Target y is always current y. This also gives the independent checker a separate target formula.

## Validation and reproduction

All six planned hypotheses pass in the generated corpus. The main program checks true-history inclusion in 88,888 honest-bound case evaluations and target-set inclusion in all 44,444 tight/loose pairs. It also checks 14,844 zero-bound evaluations and twelve operation, invalid-input, and empty-candidate controls. There are 130,208 case/bound evaluations and 651,040 rule outcomes. These counts include repeated observations, not additional independent trials.

The [README](README.md) gives the reproduction steps. The [analysis log](analysis_log.json) records the first run. The [independent audit](results/independent_check.json) matches all 44,444 cases, 16,146 observations, 64,584 saved decisions, and 170 main summary rows. It also passes ten negative and boundary controls. The [clean rerun](reproduction_check.json) matches all nine deterministic result files byte for byte. The [change record](changes_and_failures.md) retains implementation and review corrections.

The first main run took 2.50 seconds of elapsed time on the local Apple M4 computer. The clean rerun took 3.03 seconds for the main program and 4.93 seconds for the independent check. These are run records, not performance benchmarks. The machine had 24 GiB of memory; peak process memory was not measured. Python 3.13.7 used only its standard library. No GPU, training, or paid compute was used.

## Discussion

Known loss need not always force refusal. A correct loss bound and current fields can leave one undo target even when several histories remain possible. This can increase task completion in the defined model.

The gain depends on the information contract. In the false-bound setting, agreement is an agreement among the wrong set of possibilities. More matching reads cannot repair a missing candidate that contains the true history.

The practical next step is to test how an application can supply a trustworthy loss bound and a consistent current record. A production controller would also need protected writes and saved-field checks. This study does not establish either.

## Limitations

The model contains only two fields, five commands, and at most four actual later commands. Its command set makes the target particularly simple. Longer logs, dependent fields, nondeterministic commands, inserts, altered commands, out-of-order records, and hidden side effects are not tested.

The real loss count is used by the evaluator to construct B. No website service was shown to expose such a bound. The observed log and current fields are assumed accurate. False-bound tests deliberately violate one premise; they do not refute the honest-bound guarantee.

The primary and loose settings supply different information. They are not equal-information algorithm comparisons. The full-history reference is a stronger-information control. Refusal costs and incorrect-completion costs are not assigned a common utility.

Every finite case is enumerated; there is no sampling uncertainty within this corpus. Confidence intervals and p-values would not quantify deployment uncertainty. Corpus weights are artificial. No claim about production failure probability, average user behavior, or AI-model competence follows.

No production websites or connected-account records were used in this study. The October 19 website evidence remains a separate study. No concurrency, stale-read, actuation, identity, or post-write completion fault is tested here. Removing the agent action does not cause later commands to change.

## Ethical and misuse considerations

The intended use is to prevent incorrect undo claims and unwanted removal of later work. A false sense of safety is the main foreseeable risk: a developer could use an unverified loss bound or treat a successful local test as permission to overwrite real data. The false-bound results make this limit explicit.

All inputs are synthetic. There are no human subjects, private account records, credentials, or harmful action instructions. No external code, dataset, model weights, or source-paper text is redistributed. Sources retain their rights. The repository owner has not selected a reuse license, and this study does not assign one.

## AI use and human review

Codex generated the study and report. The main agent selected the model, wrote and ran the analysis, and prepared the report. Separate Codex agents checked primary sources, wrote the independent numerical check, and reviewed the release. The runtime identifies the GPT-6 model family; the exact serving build is not exposed. The experiment itself is deterministic Python and makes no model calls.

No human review or external peer review occurred. Agent review is not human review. This work claims no university affiliation, endorsement, certification, or conference approval.

## References

Checked source versions and read scopes are listed in [source_search.md](source_search.md). Bibliographic entries are in [references.bib](references.bib).

1. Korth, H. F., Levy, E., and Silberschatz, A. 1990. [A Formal Approach to Recovery by Compensating Transactions](https://www.vldb.org/conf/1990/P095.PDF). VLDB, 95–106.
2. Kushwaha, P., Purandare, R., and Dwyer, M. B. 2020. [Optimal Runtime Verification of Finite State Properties over Lossy Event Streams](https://arxiv.org/html/2004.04214v1). arXiv:2004.04214v1. Preprint.
3. Wang, J., Song, S., Zhu, X., and Lin, X. 2013. [Efficient Recovery of Missing Events](https://sxsong.github.io/doc/13vldb.pdf). PVLDB 6(10), 841–852.
4. Amendola, G., and Libkin, L. 2018. [Explainable Certain Answers](https://www.ijcai.org/proceedings/2018/233). IJCAI, 1683–1690.
5. Balakrishnan, M., and coauthors. 2026. [LogAct: Enabling Agentic Reliability via Shared Logs](https://arxiv.org/html/2604.07988v1). arXiv:2604.07988v1. Preprint.
6. NeurIPS. [Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). Accessed 2026-10-20. Used only as a review aid.
