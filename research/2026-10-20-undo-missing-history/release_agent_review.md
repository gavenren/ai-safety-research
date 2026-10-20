# Separate release review

Date: 2026-10-20. Reviewer: a separate Codex agent. No human review occurred.

Status: PASS for the checked local research content. Publication and remote file checks remain the main agent's separate task.

## Scope

The reviewer read the frozen plan, configuration, report, source record, bibliography, main code, independent code, numerical review, saved summaries, examples, controls, and run records. The reviewer also read the final reproduction procedure and its PASS receipt.

This review did not run a new study. It checked the existing evidence and code. It did not test a website or use a connected account.

## Method and evidence

- The candidate search includes every word with the visible commands as an ordered subsequence and zero through B missing commands. It filters on both current fields. Length-five candidates are included when required.
- The main index removes duplicate embeddings of a candidate word. It does not remove distinct words that have the same target.
- B is used as an upper bound. The code does not require exactly B missing commands. The false-bound setting deliberately excludes the true history in some cases.
- Controller decisions do not use the true word, mask, evaluator target, or actual missing count. The generator uses the actual missing count to supply B. The report states this assumption.
- The independent implementation uses a different candidate search and a separate target formula. Its saved check covers all 44,444 cases, 16,146 observations, 64,584 saved decisions, and 170 main summary rows.
- The report's result tables agree with the saved summaries. Row totals, the 130,208 case/bound evaluations, and the 651,040 rule outcomes are consistent.
- The soundness and increasing-bound arguments follow from candidate inclusion. They require accurate inputs and the correct bound. They do not establish safe execution with new concurrent writes or failed writes.
- The report distinguishes correct completion from refusal with correct fields. It does not count a refusal as task completion.
- The three frozen input hashes match. The six saved main result hashes match. The clean reproduction receipt reports exact matches for all nine result files. Its recorded code hashes identify the checked procedure.

## Claims, sources, and limits

The reviewer opened the cited primary sources for Kushwaha and coauthors, Wang and coauthors, Amendola and Libkin, Korth and coauthors, and LogAct. The relevant source sections support the report's narrow uses. The reviewer checked the NeurIPS checklist as a review aid.

The report credits prior work on compatible histories, missing-event recovery, certain answers, and compensation. It claims a finite regression artifact and comparison. It does not claim a new general recovery method or priority over all related work.

The fixed-command target, small command set, generator-supplied bound, artificial case weights, and lack of production tests are explicit. The exact counts do not need sampling intervals. They do not establish a deployment error rate. Preprints are identified. Source read scopes and inaccessible leads are recorded.

## Correction made during review

The first draft did not state the bound setting used to select the small examples. The independent review had also identified this issue. The final text now states that the examples use the tight setting, except for the false-bound failure. It also states that an earlier several-histories example exists under loose bounds. The numerical results did not change.

The draft README contained commands and receipt names that did not match the independent program. The final README uses the supported commands and existing receipt names. The clean reproduction procedure is now present and passed.

## Release checks

All checked Markdown tables have a consistent number of columns. The report defines its main terms and discloses Codex's roles and the lack of human review.

The inputs are synthetic. A text scan found no common credential pattern, private key header, user filesystem path, or personal email address. Manual inspection found no private account record or harmful action instructions. This scan is not a guarantee against every possible secret pattern.

The package cites source papers without copying their text or distributing their files. It does not assign a new license. No material research error remains in the checked local content.

The main agent must complete its final package-link check, review record, upload, and remote verification before it reports publication.
