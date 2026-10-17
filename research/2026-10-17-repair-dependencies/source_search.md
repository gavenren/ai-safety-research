# Primary source review for the October 17 repair audit

Review date: 2026-10-17, America/Toronto. Source agent: Codex. The review was done before the study plan was fixed and before experiments started.

## Search record

Search tool: web search. Search date: 2026-10-17. Exact queries:

1. `"State Consistency in Concurrent LLM Agent Workflows"`
2. `LLM agent concurrency stale plan compare and swap replan retry state dependency`
3. `"7472480" "pdf"`
4. `"State Consistency in Concurrent LLM Agent Workflows" "SVBE"`
5. `computer use agent safe retry stale state lost update optimistic concurrency conditional writes benchmark` (root agent)
6. `site.developers.google.com calendar modify resources atomically etag If-Match` (root agent)
7. `site.rfc-editor.org RFC 9110 If-Match lost update` (root agent)

The search returned blogs, summaries, repositories, and discussion posts. None of those secondary sources supports a claim in this review. The primary sources below were opened. The search is limited. It cannot establish that a proposed method or result is new.

## Closest source: PlanFence

Evan Chen, Shiqiang Wang, and Christopher G. Brinton. *Fresh Memory, Stale Plans: Derivation Currency for Distributed LLM-Agent Memory*. arXiv:2609.03340v2. First submitted September 3, 2026; v2 dated September 27, 2026. Preprint. The v1 title uses “Dependency-Scoped Validation” in place of “Derivation Currency.” Use the v2 title and version.

Sources: https://arxiv.org/abs/2609.03340 and https://arxiv.org/html/2609.03340v2 .

Read scope: abstract; Sections 2–4; Sections 6.1–6.2; Appendix A; Appendix B.1–B.2; Appendix C.3; Appendix E.1–E.3. Some v1 sections were read first. The review then checked v2. The full code and experiments were not reproduced.

The paper already separates fresh observed state from a plan based on old inputs. Its validator uses recorded input versions. Appendix C.3 requires a replacement plan for the second check. It does not permit a new head to be put into the old plan. The stated guarantee ends at owner responses. It does not make validation and an external effect atomic. Recorded version validity also does not establish semantic task correctness.

Thus fresh tokens with old actions, dependency validation, and the check-to-effect gap are prior work. A new finite audit must claim only its specific artifact and comparisons.

## CoAgent

Hongtao Lyu, Dingyan Zhang, Mingyu Wu, Xingda Wei, and Haibo Chen. *CoAgent: Concurrency Control for Multi-Agent Systems*. arXiv:2606.15376v1, June 13, 2026. Preprint. The entry says submitted to ATC 2026; it does not establish acceptance.

Sources: https://arxiv.org/abs/2606.15376 and https://arxiv.org/html/2606.15376v1 .

Read scope: abstract; introduction; Section 4; Sections 5.1–5.3; opening Section 6; conclusion. The evaluation and full implementation were not independently checked or rerun.

CoAgent uses declared tool read/write sets, ordered reads, notifications, and compensation for speculative writes. Its model assumes that the agent correctly identifies affected premises and repairs the dependent actions. It also assumes that tools obey their declared sets. Its stated serial result applies when all work and notifications finish. It is not a protocol that only refreshes a revision token. Therefore an audit of a deliberately stale retry is not a test of CoAgent. Relevant prior principle: repair must cover the actions that depend on changed inputs. The proposed audit replaces that semantic judgment with a fully specified small function, so it cannot measure agent repair ability.

## Verified anomaly study

Sajjad Khan. *Verified Detection and Prevention of Concurrency Anomalies in Multi-Agent Large Language Model Systems*. arXiv:2606.17182v1, June 15, 2026. Preprint.

Sources: https://arxiv.org/abs/2606.17182 and https://arxiv.org/html/2606.17182v1 .

Read scope: abstract; Sections II-A–II-B; III-A; IV-E–IV-F; VI-E ending and VI-F; conclusion. Full proof artifacts, appendices, and empirical claims were not reproduced.

The model separates read, generation, and atomic write phases. The stale-generation predicate detects a changed read value during generation. Section IV-E states that a correct snapshot at the initial read does not establish validity at commit. Its operational interpretation discusses deterministic generation. Section II-B states that the trace-level proofs do not require that determinism assumption. The runtime results use specific atomic-interleaving assumptions. The paper itself identifies the underlying anomalies as classical. Its history predicate is not the same as a current-value task contract: a value can change and return before an effect, yet an intervening change can still satisfy the history predicate. The new audit must define its own effect-time contract and must not relabel this existing anomaly as new.

## SSRN source: abstract only

Bhuvin Gowda Mysore Basavaraju. *State Consistency in Concurrent LLM Agent Workflows: An Experimental Evaluation of Concurrency Control and Semantic Effect-Time Validation*. SSRN 7472480, posted September 16, 2026. Working paper; peer review not established.

Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7472480 . DOI: https://doi.org/10.2139/ssrn.7472480 .

Direct opens returned HTTP 403 or an internal error. Search returned the source page's abstract and metadata. The full paper was not read. The abstract describes comparisons of unsafe execution, locks, OCC, CAS, serializable transactions, and semantic validation before an effect. It explicitly distinguishes a state change from invalidation of an action's assumptions. This is a close lead that further limits novelty claims. Do not use its numerical results, method details, or guarantees as checked evidence in the new report. It can appear in the search log as an abstract-only related-work lead.

## Recommended question and contribution boundary

Proposed question: In a fixed finite model, which repair rules prevent (1) replacement of unrelated saved fields and (2) an accepted effect that violates the current permission or input-value contract?

Use a single record with permission A, source X, output Y, and unrelated value U. The contract permits Y = f(X) only when A = 1 and preserves A, X, and U. Define each policy, its read set, payload, guard, and retry budget before execution. Use identical external changes for matched cases.

Keep these outcomes separate:

- Collateral overwrite: the repair replaces a current field outside Y with an old value.
- Invalid accepted effect: immediately before the atomic effect, permission is absent or the planned Y differs from f(current X).
- Conservative rejection: the policy blocks an effect that satisfies this value-based contract.

A useful edge case is a changed value that later returns. A complete revision counter still records the changes. A value guard can accept the current-value contract. That is a contract difference, not a defect in a stricter version rule. A history-sensitive permission rule would need a different model.

Compare fixed implementations, not named papers or deployed products. A whole-record replacement, Y-only update, refreshed-token retry with the old Y, complete replan plus CAS, and atomic dependency-value guard form a useful regression corpus. Add an incomplete guard that checks X but omits A if the budget permits. That case tests whether the permission dependency is recorded. Keep no-change and unrelated-change controls.

The contribution can be the exact case set, outcome counts, smallest examples, and tests that distinguish these implementation errors. The search found no evidence that this exact package already exists, but it found the core principles in prior work. Do not describe the package as a new concurrency algorithm, a discovery of stale plans, a refutation of PlanFence, or evidence of a production failure rate. No experiment, code, or result was produced in this source review.

## Rights and quotation record

No source code or full paper is copied into this note. The text is a short paraphrase with source links. The source license is not applied to the user's work. No new license is assigned. No direct quotation is used.


## HTTP and Calendar context checked before the plan was fixed

Roy T. Fielding, Mark Nottingham, and Julian Reschke. *HTTP Semantics*. RFC 9110, STD 97. June 2022. Internet Standard. Source: https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1 . Read metadata and Section 13.1.1 on October 17, 2026. The root agent also read that section today. If-Match uses strong entity-tag comparison before the method. A false condition prevents the method, with a possible successful response when an equivalent change was already applied. The standard describes lost-update protection. It does not infer whether a submitted action still satisfies the caller's task. This study's non-reused integer revision is an abstract assumption; it is not a general property claimed for every ETag.

Google. *Get specific versions of resources*. Google Calendar API documentation. Source: https://developers.google.com/workspace/calendar/api/guides/version-resources . Page last updated September 11, 2026 UTC. The full guide and its two code samples were read on October 17, 2026 by the source agent. The root agent also read the full guide today. It describes conditional updates and deletes, failure code 412, and retrieval of the latest resource before changes are applied again. The sample retains a fixed summary when it retries; its comment allows more complex conflict logic. This is not an error for a fixed-summary task. It does not establish safety for a derived or permission-dependent task. The guide also states that some calendarList read-only field changes, including ACLs, do not change its ETag. No Calendar call, account trial, sample execution, or defect test was done in this study.

The Google page identifies CC BY 4.0 for prose and Apache 2.0 for code samples. The RFC has IETF Trust terms. The package copies neither source code nor full source text and assigns no new license.

## Pre-execution plan review

The source agent read analysis_plan.md and config.json before the freeze. No enumeration or result was read or run. The plan correctly limits its claim to a synthetic regression corpus and distinguishes current-value validity from exact version history. It names PlanFence as prior work. The A bit denotes an explicit modeled task permission. It is not a Google ACL and does not show an API bypass. The current-value contract can permit a value after it changes and returns; a contract that preserves revocation history needs a different rule. The six policies are abstract implementations, not replicas of the cited systems.
