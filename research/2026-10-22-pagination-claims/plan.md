# Plan: Page completion and search coverage
Question: When do page-size stop rules or token exhaustion give unsupported completion and false absence claims?
Hypothesis: Empty, short, and no-match page stop rules will have unsupported completion claims. Token-only traversal will fail when search coverage is incomplete. Token-plus-coverage and its two-page bounded version will make no unsupported completion claims, but the bounded version will leave some complete searches unknown.
Corpus: Page capacity 2. Enumerate all six (matching, unrelated) nonnegative count pairs with sum at most 2. Enumerate all streams of lengths 1 through 4: 1,554 streams. Give each stream three modes: complete with zero hidden matches; incomplete with zero hidden matches; incomplete with one hidden match. Total 4,662 worlds. Items have unique IDs. No duplicate results or mutations occur.
Metadata: Each nonfinal page has a truthful next token; only the final page has no token. The incomplete-search flag is true on every page in the two incomplete modes and false in the complete mode. Query scope is fixed. Hidden matches are outside the searched scope.
Rules: empty_page stops on raw size zero; short_page stops on raw size below 2; no_match_page stops when the page has zero matches. These three also stop at the final token and claim complete. token_only follows every token then claims complete. token_and_coverage follows every token, then claims complete only if no incomplete flag was seen. bounded_checked does the same but reads at most 2 pages; if a token remains or any incomplete flag was seen, it reports unknown.
Measures: Per rule, complete claims, unknowns, unsupported completion claims, incorrect inventories claimed complete, false absence claims, missing matches, and pages read. Unsupported completion means a complete claim with an unvisited token suffix or an incomplete-search flag. Incorrect inventory means a complete claim with a returned matching-ID set different from the world truth. False absence means a complete claim with no returned match when truth has a match. A correct count can still be an unsupported claim.
Oracle: Use the complete world list and truthful metadata, separate from each rule's stop test. Record every page input, returned matching IDs, stop index, token state, flag, and outcome.
Controls: Empty page then match; short page then match; full unrelated page then match; one complete empty final page; incomplete coverage with zero or one hidden match; and a two-page limit with a further token. These are named members of the main corpus.
Decision criteria: Each of the first four rules must have a counterexample for the stated claim; both checked rules must have zero unsupported completion and false absence claims. Complete unlimited checked search must complete every complete-mode world. Counts and failures must remain in the report if a prediction fails.
Proof aid: Under truthful finite tokens and truthful coverage, following all tokens enumerates all visible pages. Terminal token and complete coverage together cover the world. The claim does not hold if either metadata assumption fails.
Boundaries: Synthetic worlds only. No live API, website, agent, model, latency, mutation, token expiry, dishonest metadata, or real frequency estimate. This compares stopping evidence, not first-page ranking.

Date: 2026-10-22 (America/Toronto). This is an extra study requested by the owner.
Type: complete finite synthetic study. No account or website experiment. No trained model test.
Freeze this plan, config, and source search before code or trial execution. Later changes must be recorded.
Use Python standard library only. Enumerate all inputs, with no random seed and no data sampling.
Run once, then repeat once in a clean output folder. Compare every deterministic result byte for byte.
Stop if one execution exceeds 60 CPU seconds, a required assertion fails, or a required source is not checked.
Do not publish before a separate agent review and the relevant NeurIPS checklist checks pass.
No external data, private account data, paid compute, or additional model API calls.
Record Python and platform versions, code and input hashes, raw cases, summaries, logs, and actual runtime.
No confidence interval or statistical test: counts cover this finite set, not a sampled population.
No claim that the mechanisms are new. The contribution is the stated paired test set and its measured comparison.
Codex generates code and the report. No human review has occurred. No new license is assigned.
