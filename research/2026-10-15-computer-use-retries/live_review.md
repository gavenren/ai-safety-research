# Independent review of the live website extension

Review date: 2026-10-15. Status: PASS within the scope below. No material error remains open.

This is an AI review. It is not human or external peer review. The review used saved files only. It made no browser action or external test.

## Evidence and checks

The reviewer read the saved plan, assignments, plan hashes, feasibility record, both action logs, and both result files. The reviewer wrote `live_validate.py` with a separate parser. It does not import `live_analyze.py`. It counts exact task labels and reads the adjacent task checkbox. It excludes input text and page counters from task counts.

The independent check passes 7,199 checks. It covers all 60 assignments, 302 scored UI observations, 428 scored action records, 20 design cells, and 120 rule pairs. It checks the assignment order, ready controls, initial zero counts, selected views, submissions, retries, decisions, audit order, active state, and time limits. It also checks that later audits retain earlier observed task rows.

All 60 trials have a decision and both audits. There is no missing or substituted assignment. Counts before and after reload agree in every trial. All matching task checkboxes in the final audits are unchecked. The 60 archived JPEG files match the available runner files. Both result files and both action logs match their frozen hashes and available source files.

The saved simulation inputs and outputs match the earlier reproduction hashes. The local pilot inputs, result tables, and raw evidence match its earlier hashes. The package retains 13,440 simulation runs and 18 local pilot trials. Their evidence was not replaced by the new 60-trial experiment.

The checker also ran the analyzer in a temporary copy. It removed `live_results.csv`, `live_pairs.csv`, and `live_summary.json` before that run. All three new files match the saved files exactly. The check used only local files and Python's standard library.

Run the independent check from this folder:

```sh
python3 live_validate.py --fresh-copy
```

This command writes `live_validation.json`. It does not edit the raw evidence. The saved JSON records the Python version, code hash, input hashes, results, and limits.

## Observed results

| Runner | Trials | Clean confirmations | Unresolved decisions | Duplicate outcomes | Zero-task outcomes | Retries | All controls passed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T, KnockoutJS | 30 | 11 | 19 | 4 | 10 | 10 | 6/15 |
| P, Microsoft demo | 30 | 18 | 12 | 6 | 0 | 6 | 15/15 |
| Total | 60 | 29 | 31 | 10 | 10 | 16 | 21/30 |

Forty final outcomes contain exactly one task. Eleven of these have no clean confirmation. All ten duplicate outcomes have unresolved decisions in Completed view. No success decision has a duplicate or zero-task final outcome.

H1 meets its saved direction on both sites. In Completed view, Absence and Wait24 each have two duplicate outcomes in three T trials. Each has three in three P trials. Closure and Scope have none.

H2 meets its saved direction on both sites. Scope confirms one of three T tasks and three of three P tasks in Completed view. Closure confirms none. Scope adds no duplicate outcome. The two unresolved T Scope trials have no task in either audit.

H3 fails. Nine All-view trials fail the required success without a retry. All nine are T trials. Four recover through their permitted retry. Thus, 25 All-view trials have clean final confirmations, but only 21 pass the control. The paper makes this distinction.

The T input retains its token after 16 initial submission actions. Six of these trials later have one task after a permitted retry. Ten still have no task. These observations do not identify the cause of the failed input actions. They do not show a lost server write.

The failed control and missing tasks are negative study results. They are not data-integrity failures. The review does not require the hypotheses or controls to succeed.

## Time and metadata

No scored decision exceeds 60 seconds. The largest interval is 44.431 seconds. The eight Wait24 observations start between 26.161 and 29.597 seconds after the initial action request. Each retry follows its fresh zero-count observation. All trials start before the 20-minute admission budget ends.

Three T rows have a one-millisecond difference between the saved result start time and the action start time: T02, T05, and T11. The earlier value comes from a separate clock read. Both values remain unchanged. They give the same deadline result. The eight Wait24 checks also give the same result under either start-time field.

One clock-only record made during T06 has a stale T01 label. A later raw correction identifies it. The analyzer excludes this diagnostic from scored action counts. It does not exclude a submission, observation, decision, or failed outcome.

These are the analyzer's four disclosed metadata warnings. They do not change any outcome or rule check. Both runners also retain setup error records from before scoring. The scored records contain no tool error or policy deviation. Some input actions still fail to create tasks; the paper reports that separate result.

## Image and PDF review

A separate AI image reviewer checked all 60 final images. The check covered every rule, view, repeat, missing outcome, and duplicate outcome. Every visible final token count agrees with its result row. All images show All selected. Each saved image contains the full task list and footer, including the later task rows. No cropped final list caused a count limit.

The images support final audit counts. They cannot prove the earlier decision view, retry count, time, or action order. Those checks use the saved UI observations and action records.

The image reviewer also checked all 15 rendered PDF pages. No clipped text, overlap, broken table, unreadable character, or cut chart label was found. Page 5 has a large blank area before the figure on page 6. No content is hidden. Section 5.4 starts on page 6, and its table starts on page 7. These are layout choices, not content errors.

## Final text and scope

The reviewer checked the final abstract, Section 7, interpretation, limits, AI-use statement, reproduction text, source scope, and repository index row. The table counts and main numeric claims agree with the independent results. The paper has no live-results placeholder. It states the failed control and does not claim a general success or speed gain.

The final text states that the sites are two public demos of one related workflow. It states that tasks use browser storage. Reload survival does not establish server storage or indefinite durability. The rules are supplied procedures; the results are not natural model error rates. The two contexts share one host and browser service. Site selection followed feasibility checks. The 24-second wait is a heuristic, not a proved bound. Closure and No retry have the same permitted retry actions on these sites.

The logs used for scoring contain rendered UI observations. They contain no logged app-source or storage-read action. They do not contain complete tool-call code or model-turn boundaries. Thus, these files cannot prove the absence of hidden reads or prove one model decision per action. The paper describes the instruction boundary and does not claim a secure access boundary. The separate design source check supplies no trial outcome.

The feasibility record is a manual summary. It is not a timed raw export of the preliminary checks. Local timestamps and hashes do not establish external preregistration. The source search supports a bounded comparison; it cannot prove novelty. Exact browser trajectories were not repeated. No human review or production safety certification is claimed.

## Reviewed versions

| File | SHA-256 |
| --- | --- |
| report.md | `19140e255cf75751d0f77ea0dafe2626bd7582ba5816bb6f5f231bb30ff0845c` |
| paper.pdf | `982db46171211bc69ce0cf9f73645b9263ed27feae31e7202806510e28788b53` |
| live_summary.json | `4d1cd293b5e3b594217315de2131aa0ea144de7191f58b407114969e0d71273b` |
| Repository index README.md | `2fef9aa1ad5e78e3da6623f2c3a3687993a668aecb5f581c1d9ce10514b4616e` |

PASS means that the saved evidence, analysis, stated claims, and reviewed PDF agree within this scope. It does not mean that every trial succeeded.
