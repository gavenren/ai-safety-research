# A locally valid undo step can block safe completion

Date: 2026-10-22, America/Toronto.

## Abstract

A step can preserve a state constraint while removing every safe route to the undo target. We tested this limit in a synthetic model with three Boolean fields. Undo clears one field at a time. We enumerated all 64 valid-state conditions that include the start and goal, all six field priorities, and three fixed controllers. The greedy controller kept every visited state valid. However, it reached an avoidable dead end in 24 of 384 cases. Complete search finished all 276 cases with a safe path and refused the other 108 before action. Fixed order restored the target in all 384 cases, but crossed an invalid state in 288. All 1,179 cases, including smaller-state controls, repeated with identical logical output. These exact counts describe the chosen model. They do not measure real AI agents or websites.

## Research question and safety relevance

Can a controller commit a locally valid undo step and then lose every safe path to completion, even though a safe path existed before that step?

An agent can need several actions to undo a task. Checking only the next action can protect the current state but still leave unfinished work. The relevant distinction is between a valid next state and continued ability to reach the goal. This note tests that distinction under known, fixed conditions.

A **Boolean field** has value zero or one. A **valid-state condition** lists the permitted complete records. An **invariant** is a condition that must remain true after every action. A **safe path** is a sequence of allowed actions whose states all satisfy that condition and that reaches the goal. A **dead end** is a non-goal state with no safe continuation. An **avoidable dead end** is one reached after action when a safe path existed from the start. A **controller** is a fixed program that selects actions. No language model selects actions in this experiment.

## Related work and contribution

Sagas requires each subtransaction to preserve consistency. Its compensation operations have application-specific meanings. This study does not show a defect in correctly designed Sagas. It tests three small controllers under a declared invariant. [Garcia-Molina and Salem, 1987](https://sigmodrecord.org/1987/12/09/sagas/)

Planning research already studies dead ends and goal order. The FF author's system page describes failure of local search and a fallback to complete search. Our greedy controller is much simpler. It commits the first valid action and cannot backtrack. It is not FF or greedy best-first graph search. [Hoffmann, FF Homepage](https://fai.cs.uni-saarland.de/hoffmann/ff.html)

UndoBench separates environment conditions from effect history when it evaluates recovery. Our study does not introduce that distinction or reproduce its model results. [Sah et al., preprint, 2026](https://arxiv.org/html/2610.05622v1)

The [earlier October 22 report](../2026-10-22-undo-visibility/report.md) tests the ordered decisions of readers during a two-field SQLite undo. This note uses a different contract: every intermediate state must remain valid, and undo should finish when a valid action order exists. Its contribution is an exact three-bit corpus, count checks, priority controls, and a saved witness. The mechanisms are established. The [source search](source_search.md) does not prove global novelty or priority.

## Method

The [plan](plan.md), [configuration](config.json), and [source search](source_search.md) were hashed before implementation. The code was hashed before the first execution. Both records are retained in [freeze.json](freeze.json) and [implementation_freeze.json](implementation_freeze.json).

### State and allowed action

The state is abc, where a is the leftmost bit. The start is 111. The undo goal is 000. Each action clears one bit that is still one. A cleared bit cannot be set back to one. There is one writer. Every action and state observation is exact. The validity function is fully known, correct, and static. There are no concurrent edits, failures, stale reads, hidden actions, or external effects.

Both endpoints must be valid. Each of the other six states can independently be valid or invalid. Thus there are 64 conditions. We test all six field priorities and the following three rules, for 64 × 6 × 3 = 1,152 primary rule cases.

| Rule | Action selection | Behavior when no safe full path is found |
| --- | --- | --- |
| Fixed | Clear fields in the prescribed priority, without a validity check | Does not search; always reaches the target |
| Greedy | Commit the first remaining field whose next state is valid | Stop if no next state is valid |
| Complete | Before action, inspect all six orders and select the first entirely valid path | Refuse before any mutation |

All rules have the same single-field action capability. Complete search has more planning work. The comparison does not establish that full search is affordable in a large system. A separate set-based graph traversal checks whether the goal is reachable. It does not use the complete planner's permutation list or results. The same Codex agent wrote both algorithms.

The program saves each state trace, action order, candidate-check count, and terminal status. It scores target restoration separately from path validity. A valid completion requires both. It records partial stops and refusals before action separately. The rules do not make natural-language completion claims.

### Controls and uncertainty

We also enumerate all one-bit and two-bit conditions, priorities, and rules. These give 27 additional cases. The program checks the all-valid set, the endpoint-only set, and one valid chain. It also relabels fields and priority together to check that names do not change the outcome. These checks are controls, not additional independent tasks.

The corpus is complete for the stated model. There is no random sample or random seed. Confidence intervals, significance tests, and population error rates would be inappropriate. Counts depend on the arbitrary inclusion of every state subset. No training, test split, or learned policy is used.

The resource gate was 60 CPU seconds and 120 wall seconds per run, with at most two full runs. A failed assertion or unexpected error would stop the run and preserve partial evidence. No case was replaced or excluded.

## Results

Every assigned case produced a valid record. There were no unknown cases or failed checks.

| Primary rule | Cases | Target reached | Valid completion | Invalid state visited | Partial stop | Refusal before action | Avoidable dead end |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed | 384 | 384 | 96 | 288 | 0 | 0 | 0 |
| Greedy | 384 | 252 | 252 | 0 | 84 | 48 | 24 |
| Complete | 384 | 276 | 276 | 0 | 0 | 108 | 0 |

There are 46 of 64 conditions with at least one safe path. Each appears under six priorities, which gives 276 feasible cases per rule. The greedy rule completed 252 of those cases and reached an avoidable dead end in the other 24. Its 60 other partial stops and all 48 refusals occurred where no safe path existed from the start. Nine conditions admit an avoidable dead end for at least one priority.

Each priority has the same aggregate result: 16 valid fixed paths, 42 greedy completions, four greedy avoidable dead ends, and 46 complete-search completions among 64 conditions. Priority can change an individual case. Equal aggregate counts follow from the field-name symmetry of the full corpus. [summary.json](summary.json) retains all priority results; [conditions.json](conditions.json) retains all condition results.

### A recorded witness

Condition 22 permits exactly {000,010,011,101,111}. The priority is bac. Cases 430–432 show the following paths.

| Rule | Committed state trace | Outcome |
| --- | --- | --- |
| Fixed | 111 → 101 → 001 → 000 | Goal restored, but 001 is invalid |
| Greedy | 111 → 101 | Valid state, but both next states 001 and 100 are invalid |
| Complete | 111 → 011 → 010 → 000 | Safe completion with action order acb |

The greedy rule's first step is valid. Its remaining permitted actions cannot reach the goal safely. It cannot return to 111 because the model does not allow a bit to be set back to one. See [witness.json](witness.json) for the complete paired records. This is the first witness in the frozen case order, not a claim of a globally minimal real workflow.

### Controls, derivation, and repeat

All 27 smaller-state rule cases passed their checks. Greedy has no avoidable dead end with one or two bits. With two bits, a valid first step leaves only one bit; clearing it reaches the required valid goal. Three bits are therefore the first size with this failure in the declared model.

All 6,963 field-renaming comparisons passed. The complete planner matched the graph oracle on all 393 conditions and priorities across the primary and smaller-state groups. All-valid, endpoint-only, and single-chain controls also passed. These are algorithm checks by the study author, not independent human review. [checks.json](checks.json)

The post-run [analytic derivation](analytic_checks.md) also matches the counts. It finds 18 conditions with no safe path and 46 with a path. For any priority, two required intermediate states give 16 valid fixed paths. The greedy rule has 8 initial refusals, 14 partial stops, and 42 completions. Four of those 14 stops are avoidable. Multiplication by six gives the primary table.

Both planned runs used unchanged code on Python 3.13.7, macOS 26.7.2, arm64. The first used 0.113071 CPU seconds and 0.209122 monotonic seconds. The second execution receipt records its own time. All five deterministic files matched byte for byte. The two runs repeat the same 1,179 rule cases; they are not 2,358 distinct test cases. See [reproduction.json](reproduction.json) and both execution receipts.

## Discussion

In this model, a next-step guard protects the invariant but does not preserve the ability to finish. A target-only audit has a different problem: every fixed order restores 000, even after an invalid state. Thus final restoration, state validity, and continued ability to finish are separate checks.

A controller with a complete and stable model can check an entire safe order before it starts. An agent on a website may not have that model or action control. The measured result therefore supports a small regression test and a design question: does this allowed step preserve a safe continuation? It does not establish a tested browser policy.

## Limitations

This is a synthetic simulation with three fields and deterministic one-way actions. The validity condition is assumed correct and fully known. Real constraints can be incomplete, hidden, or changed by other users. A plan checked in advance can become stale. This study does not test those cases.

The model excludes backtracking, atomic multi-field writes, temporary data structures, constraints on action history, costs, timing, and external side effects. With another action capability, a modeled dead end may be recoverable. A valid state need not mean absence of real harm. Complete search grows quickly with the number of possible orders; no scalability or efficiency claim is made.

The corpus weights all valid-state subsets and priorities equally for enumeration. That weighting is not a distribution of real tasks. No real computer-use agent, production website, connected account, or language model was tested. The core planning ideas are established. No general safety guarantee or new algorithm is claimed.

## Ethical and misuse considerations

All inputs and effects are synthetic local values. The study uses no private data, messages, or account records. No service was purchased. No external action was made. The main misuse risk is to present exact finite counts as real-world failure probabilities or to treat complete search as a general safety certificate. This report states the required assumptions and keeps refusals separate from completions.

Primary sources are cited and paraphrased. No source dataset, code, diagram, or full paper is republished. No new license is assigned to the owner's work.

## AI use and review status

Codex generated this study, its code, analysis, and report. The study agent used public web search to check sources and local Python to execute the fixed controllers. No language model was invoked inside a trial. The runtime model version was not exposed to the study agent; it is not a measured experimental variable.

No human review or external peer review occurred. A separate Codex agent checked all 1,179 saved cases, 4,042 trace states, and 6,963 field-name comparisons with its own evaluator. It also checked the analytic argument, original sources, and report. No material error was found. The [separate review](separate_review.md) and [validation record](validation.md) state the review limits. The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was used as a review aid. This is not conference approval, submission compliance, endorsement, or certification.

## References and reproduction

The [source search](source_search.md) gives URLs, dates, exact queries, read scope, and prior-work limits. [references.bib](references.bib) supplies the bibliography. The [README](README.md) gives the exact repeat command and comparison command. [cases.jsonl](cases.jsonl) contains every raw trace. [deviations.md](deviations.md) records changes and failures.
