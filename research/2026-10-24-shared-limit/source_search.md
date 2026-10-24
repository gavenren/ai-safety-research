# Source search for the shared-limit study

Search date: 2026-10-24, America/Toronto. Agent role: source review before the plan was frozen. No experiment was run for this review.

## Search terms

The web search used these exact queries. The first batch used site terms. Later batches also used domain filters.

1. `site.sqlite.org isolation BEGIN IMMEDIATE snapshot SQLITE_BUSY_SNAPSHOT`
2. `site.postgresql.org docs current transaction isolation write skew serialization anomaly`
3. `AI agents shared budget concurrency write skew invariant transaction 2026 arxiv`
4. `AI agent shared budget concurrency invariant write skew` (arxiv.org)
5. `"BEGIN AI TRANSACTION" "Semantic Isolation"` (arxiv.org)
6. `"Multi-Agent Systems Should Prioritize Concurrency Control"` (arxiv.org)
7. `agent shared budget atomic reservation limit concurrency` (arxiv.org)
8. `"write skew" "agents" concurrent` (arxiv.org)
9. `"A Critique of ANSI SQL Isolation Levels" Berenson Microsoft`

Only primary sources support the proposal. Search results from blogs, Reddit, aggregators, and copies on unrelated hosts were not used as evidence. Search absence is not proof of novelty. This was a limited search, not a systematic review.

## Primary sources checked

### 1. Berenson and colleagues: A Critique of ANSI SQL Isolation Levels

- Date: June 1995, MSR-TR-95-51. The title page identifies the SIGMOD 1995 paper.
- Original author-hosted PDF: https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf
- DOI: https://doi.org/10.1145/223784.223785
- Checked: title and abstract; A5A and A5B definitions; the constraint examples; the discussion of separate inserted tasks and first-committer-wins. These occur on printed pages 8-9, PDF pages 9-10.
- Use: write skew is established prior work. Separate records can pass individual conflict checks while a condition over their sum fails. The paper already gives a task-hours example. A new report must not call that mechanism a new discovery.
- Limit: the full paper and its proof relations were not independently checked. No source code was reproduced.

### 2. SQLite: Isolation In SQLite

- Date: live documentation, read 2026-10-24. No page publication date was shown.
- URL: https://www.sqlite.org/isolation.html
- Checked: Isolation Between Database Connections; Isolation And Concurrency; the WAL snapshot example, failed read-to-write upgrade, and BEGIN IMMEDIATE guidance. The same-connection cursor section was read only to identify an excluded hazard.
- Use: SQLite permits one writer at a time. In WAL mode, a read snapshot cannot upgrade after a conflicting committed write. A failed upgrade requires a new transaction. Successful BEGIN IMMEDIATE obtains the write transaction before the later reads.
- Limit: the study must report its actual SQLite version and settings. It must not describe separate application transactions as a defect in SQLite isolation.

### 3. SQLite: Transaction

- Date: live documentation, read 2026-10-24. No page publication date was shown.
- URL: https://www.sqlite.org/lang_transaction.html
- Checked: Sections 2, 2.1, and 2.2 on implicit transactions, read and write transactions, and deferred/immediate/exclusive starts.
- Use: a completed standalone SQL statement can commit separately. Thus, an application read-check followed by a later write can cross a transaction boundary even though each statement has a transaction. BEGIN IMMEDIATE can return SQLITE_BUSY when another writer is active.
- Limit: no throughput or timing claim follows from the documentation.

### 4. PostgreSQL 18: Transaction Isolation

- Date: version 18 documentation, read 2026-10-24. The unversioned current URL resolved to version 18 on this date.
- URL: https://www.postgresql.org/docs/18/transaction-iso.html
- Checked: definitions and Table 13.1; Read Committed statement snapshots; Repeatable Read restart guidance; Serializable sum-and-insert example and the rule to retry the whole failed transaction.
- Use: two transactions can write separate rows yet create a result that has no serial explanation. The source distinguishes this from write-write conflict. This is a comparison of documented contracts, not a PostgreSQL experiment.
- Limit: PostgreSQL was not run. A SQLite result cannot establish another engine's behavior.

### 5. Zhu and Wang: Fault-Tolerant Budget Conservation in Distributed Multi-Agent Delegation

- Status: preprint, arXiv:2610.00349v1. The source page reports 2026-09-29 as the submission date. The identifier and date are recorded as shown by that source.
- Abstract and version metadata: https://arxiv.org/abs/2610.00349v1
- Full text: https://arxiv.org/html/2610.00349v1
- Checked: abstract; Sections 2.4, 4.1-4.6, 8.2 (SQLite executable binding), 8.5-8.7, 9.3-9.4, and Appendix F.2-F.3. Other sections were not read in full.
- Use: the closest current work already treats shared budgets as an authority condition, read-check double spending, exclusive credit, and SQLite evidence. Its local row checks apply to exclusive credit generations. This does not justify row checks over unallocated copies of a shared total.
- Limit: no code, proof, or result was reproduced. The proposed study is not an evaluation or refutation of this protocol. It excludes delegated credit, crashes, settlement, uncertain external effects, authentication, and partitions.

### 6. Lyu and colleagues: CoAgent

- Status: preprint, arXiv:2606.15376v1, 2026-06-13.
- URL: https://arxiv.org/html/2606.15376v1
- Checked: abstract; Sections 4.2 and 5.1 on declared read/write sets, atomic tool calls, and agent assumptions; Section 6 interface summary. Earlier repository work already cites this paper.
- Use: conflict scope includes inputs that a tool reads, not only the object it writes. Our deterministic decision code would remove the semantic judgment that this system gives to agents.
- Limit: no reproduction of its code, proof, or reported performance. Do not name a simplified row-check rule as CoAgent.

## Leads checked but not required as report citations

- Yang et al., `Position: Multi-Agent Systems Should Prioritize Concurrency Control`, https://arxiv.org/html/2608.18092v1 . Read abstract and Section 3.2.1-3.2.2. It already discusses write skew, isolation, and transaction scope for agents. Metadata gives a June date with an August-style identifier; retain source wording if cited. Do not infer peer review from its keywords or format.
- Mozafari, `BEGIN AI TRANSACTION: Semantic Isolation for Durable AI Workflows`, https://arxiv.org/html/2608.05412v1 . Read abstract and introduction only. It concerns changes to prompts, models, indexes, and tool meaning. Those changes are outside this proposed numeric-limit experiment. Do not cite it as a checked full paper.
- Khan, `Token Budgets`, https://arxiv.org/abs/2606.04056 . Search-result abstract only. Not checked in full and not used to support the proposed results.
- `When Should Agents Check External State?`, https://arxiv.org/abs/2609.37125 . Search-result abstract only. Observation allocation is outside the chosen boundary. Not used as evidence.

## Repository overlap check

Read local copies of the repository protocol and these reports:

- `2026-10-17-repair-dependencies/report.md`: one four-field record; one repair with later background changes; exact dependency and version guards. It explicitly excludes multi-record dependencies.
- `2026-10-22-undo-visibility/report.md`: one undo writer, interrupted multi-step undo, and two reader jobs. It scores the order of reader decisions. It does not test two independent admission writes against one capacity bound.
- `2026-10-23-receipt-state/report.md`: permanent receipt after a completed operation, later record edits, and new operation authority. It does not test simultaneous budget admission.

The proposed difference is a local executable test of two or more admission jobs that each have their own output record but depend on one common aggregate. The code, exact schedules, SQL boundaries, and saved database evidence can be new artifacts. Write skew, atomic checking, and serializable transactions are established methods. The limited search does not establish a new algorithm or a first result.

## Later design clarification, still before the plan freeze

The lead narrowed the candidate to four SQL caller rules: own-row CAS, the same rule with one separate final read, a shared revision check, and an atomic sum condition. An unrelated metadata edit tests refusal by a revision with too broad a scope. Section 9.3 of Zhu and Wang lists analytical comparisons, not measured versions of these four SQL rules. Its Section 8.5 uses exclusive credit generations; that differs from the proposed common unallocated capacity. The inspected sections did not contain this exact paired comparison. This observation is a limited read result, not proof that the comparison is absent from all prior work.

## Final frozen selection: caller composition matrix

After the candidate review, the lead selected the question in `plan.md`: can one caller with a complete shared-limit check protect the whole task when the other caller checks only its own row? The final rules are OwnCAS, SharedEpoch, and AtomicSum. The separate final-read candidate was not selected or run.

The plan contains nine ordered caller-rule pairs. Each pair receives 576 scenarios: 36 schedules, four demand pairs, and four capacities. The schedules cover both worker orders, all six read/attempt orders, and zero or one unrelated metadata event. The planned total is 5,184 case outcomes. These are design counts, not measured results in this source record.

The contribution is the complete local caller-pair test set, SQL evidence, checks after each effect, and matched unrelated-edit control. The SQL engine uses the same writer isolation for every rule. The rules differ in which application condition they check inside that transaction. Thus, this is not an experiment with mixed SQLite isolation levels. The earlier four-rule and separate-read notes remain above as candidate history.

### Added search terms after the final selection

10. `site.postgresql.org/docs/18 "all transactions" "serializable"`
11. `site.arxiv.org "complete mediation" "Fault-Tolerant Budget Conservation"`
12. `"mixed isolation" "robustness" transactions research`

Search date remains 2026-10-24. No outcomes were examined for this source update.

### Added primary sources and reading

- **PostgreSQL 18, Data Consistency Checks at the Application Level**, https://www.postgresql.org/docs/18/applevel-consistency.html . Read Sections 13.4.1 and 13.4.2. The first requires consistent coverage of writes and relevant reads for its stated Serializable guarantee. The second distinguishes row locks and wider validity checks. This directly supports the need to state which writers follow a rule. It is documentation of PostgreSQL, not evidence from our SQLite run.
- **Vandevoort, Fekete, Ketsman, Neven, and Vansummeren, Using Read Promotion and Mixed Isolation Levels for Performant Yet Serializable Execution of Transaction Programs**, PVLDB 18(9), 2846-2858, 2025. DOI: https://doi.org/10.14778/3746405.3746412 . Primary paper: https://www.vldb.org/pvldb/vol18/p2846-vandevoort.pdf . Read title, abstract, and Introduction through the template assumptions and read-promotion explanation (printed pages 2846-2847). This work already analyzes joint safety under mixed transaction assignments. We did not read or check all proofs, run its code, or reproduce its performance results. Our three caller rules are not its database isolation levels or its RePMILA implementation.
- **Zhu and Wang, additional read scope:** Sections 3.1, 3.5 Assumption 9, 7.8-7.9, 11.6, and 13.7. Its external-effect guarantee requires every effect route to pass the enforcement boundary. A weak route lies outside that guarantee. This supports the composition question but does not make our local test a refutation or reproduction of its protocol.
- **NeurIPS Paper Checklist**, https://neurips.cc/public/guides/PaperChecklist . Read the current questions and guidance on claims, limitations, theory, reproducibility, code/data, settings, statistics, compute, ethics, impacts, safeguards, licenses, assets, and human participants on 2026-10-24. This is a review aid only. No submission or NeurIPS approval is claimed.

### Final novelty limit

Partial participation, write skew, broad version checks, complete mediation, and atomic admission are prior work. Mixed-rule safety analysis is also prior work. The tested pair matrix and its physical SQLite evidence are the proposed artifact contribution. The inspected sources did not supply this exact corpus, but the limited search cannot establish priority. The study cannot establish that a capable AI agent would choose any tested rule. It can test the effect of those declared rules under the fixed schedules.
