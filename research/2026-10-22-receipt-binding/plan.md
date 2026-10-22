# Plan: Receipt scope and payload binding
Question: How do receipt scope and immutable payload checks affect false success replies and repeated effects when a request ID is reused?
Hypothesis: A receipt keyed by account and operation ID, with an exact stored payload check, will match the contract in every case. Other rules will give false success replies or incorrect effects in at least one case.
Corpus: All 16 requests (account, key, target, delta), followed by every possible second request: 256 ordered pairs. Each request uses one of two accounts, keys, and targets, and delta -1 or +1. The first request commits. No errors, expiry, races, or uncertain delivery occur.
Contract: Identity is (account, key). A new identity applies once. The same identity and same payload (target, delta) replays the original receipt. The same identity with a changed payload rejects the request and adds no effect. This is a selected contract, not a universal provider rule.
Rules: (1) key alone; (2) account and key; (3) account, target, and key; (4) the full request; (5) account and key with stored payload validation. Rules 1-4 replay an existing receipt if their key matches, otherwise apply a new effect. Rule 5 rejects changed payloads for an existing identity.
Oracle: Classify the pair by identity and payload equality, independently of the receipt store. Compare exact expected status, returned receipt, and ordered effect history. A receipt contains account, key, target, delta, and effect sequence number.
Measures: false success on the second request (a conflict reported as success or a success receipt for the wrong intent); missing authorized effects; extra effects; wrong effect history; exact contract matches. Record second action as apply, replay, or conflict. Effect history, not net numeric state, is the primary effect measure.
Controls: Exact retry; same key in another account; same identity with target or delta changed; new key with the same payload; and a changed delta which cancels the first effect in net state. Controls are selected named members of the full set, not extra independent cases.
Decision criteria: Hypothesis passes only if rule 5 has zero false success replies and exact contract matches in all 256 pairs, and each other rule has an error. Keep negative results if a prediction fails.
Boundaries: All effects and receipts are atomic and retained. No authorization, hash collision, provider API, browser, LLM, network, or crash claim. Counts are specific to the two-request, 16-request alphabet.

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
