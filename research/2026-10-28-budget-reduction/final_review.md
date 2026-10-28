# Final method and result review

Date: 2026-10-28. Reviewer: a separate Codex agent. This is an AI review. No human or external peer review occurred.

## Decision and scope

No material error was found in the model, scores, saved results, report, or repeat procedure. The resource measurement issue below is now stated in the report, README, and change record. There is no open method or result issue from this review.

The reviewer read the plan, main source, independent formulas and comparison source, freeze records, design and source reviews, saved summaries, controls, comparison records, report, README, and change record. The reviewer checked the complete rule and score definitions against the source. The separate formula reviewer checked every saved trace and SQL statement; this reviewer checked that comparison procedure and its records. This was not a blind review of the final report.

The main experiment was not rerun for this review. The reviewer ran the existing byte-comparison program on the two completed result folders. It exited with code zero. All 11 scientific files matched. This output equals the saved `reproduction.json` record. The copy in `reproduction_environment.json` also matches the second run's environment file exactly.

The reviewed report has SHA-256 `b1726f64a8771d6f5eecf98a477c9e4ab81e3476ba742be03fe99e1de765673a`. All four source and plan hashes still match their freeze records: the plan, main source, independent specification, and comparison adapter.

## Method and claims

The selected corpus has 324 numeric settings and 12 event orders for each setting. This gives 3,888 histories for each of five rules, or 19,440 primary rule cases. The six named controls repeat selected primary settings. They are not 30 further independent samples. The report keeps these scopes distinct.

The saved read is one completed query. A later write does not keep its read transaction open. Each mutation uses `BEGIN IMMEDIATE`. Separate connections represent the cap caller, settlement caller, new-job caller, and audit reader. Events run in an imposed order. This tests selected schedules in a real local SQLite database. It does not test parallel request pressure, crash recovery, or a production provider.

The complete new-job guard uses current spent use plus the outstanding hold plus the new job cost. The cap rules differ only in their condition for the cap change. A refused reduction preserves the old cap. The report correctly states that this refusal does not fulfill the requested lower cap.

The scores use the applied cap, not an unaccepted request. An unsafe reduction is an accepted cap change that puts current covered use above that cap. A feasible refusal is a refusal when the current numeric state could fit the lower cap. This second score is a cost under the study's numeric contract. It is not a violation of the version rule's stricter condition. The report separates covered exposure, actual-use breaches, and the event where a breach first appears.

The preservation argument is correct under the stated assumptions. Settlement cannot increase covered use because its final charge does not exceed the hold. Accepted new work checks the complete resulting covered use. AtomicCover also checks current covered use when it changes the cap. VersionedCover is safe when every relevant committed effect advances the revision and the revision cannot wrap or be bypassed. The argument does not establish safety outside that protocol.

The conditional equation is also correct. Let d be the accepted B charge between the saved read R and the cap update U. Let h be the released unused hold in that interval. Then `L_U = L_R + d - h`. For CachedCover, an unsafe acceptance requires `L_R <= n < L_R + d - h`. A feasible refusal requires `L_R + d - h <= n < L_R`. The report defines these terms and uses the equation only within this event model.

## Results and evidence

The main result table matches the saved summaries. Unsafe accepted reductions are 2,811 for BlindSet, 576 for SpentOnly, 219 for CachedCover, and zero for both complete rules. Each denominator is 3,888. Actual-use breach counts are 2,523, 288, 189, zero, and zero in the same order. These are exact counts for the selected corpus. They are not estimated production rates.

The four planned hypotheses have direct support in this corpus. H1 has unsafe cap changes despite complete B guards, including actual breaches first seen at settlement. H2 has both unsafe cached acceptances and 201 feasible cached refusals. H3 has no covered-use breach for either complete rule, 507 feasible version refusals, and exact numeric acceptance for AtomicCover. H4 has exposure-only cases: 288, 288, and 30 for the three incomplete rules. The report does not present these finite observations as a population estimate.

The matched comparisons also agree with the saved records. VersionedCover accepts 507 fewer feasible cap changes than AtomicCover and admits 93 more B jobs on the same input histories. The report explains that refusal leaves the larger old cap active. It does not treat the extra B jobs as a general benefit. CachedCover differs from AtomicCover on 420 cap decisions: 219 unsafe acceptances and 201 feasible refusals. The total of 11,571 accepted B jobs across all five rules is correct. All use the same complete B guard.

The independent comparison checks the full states, conditions, decisions, scores, SQL sequence, controls, summaries, matched tables, first adverse examples, and reopened database rows. The check includes all 19,471 final rows. Both saved runs passed. Both reopened integrity checks returned `ok`. The rollback and refused-write controls support only the stated local transaction checks.

The repeat commands use the correct program arguments and new output folder names. The README states the Python, SQLite, and Unix requirements. It explains that environment records can differ and that a changed engine can change file bytes or SQL text. Local Markdown links in the report, README, and change record were checked and resolved at review time.

## Resource measurement issue

The frozen main source leaves a reopened SQLite connection without an explicit close before the directory size measurement. A connection context ends a transaction but does not itself close the connection. Thus an in-run footprint can include temporary reader files.

Each saved in-run footprint before the environment record is 6,536,149 bytes. The 11 durable scientific files total 6,503,381 bytes after process exit. The difference is 32,768 bytes. It is consistent with a SQLite shared-memory file. No separate capture identifies that file's contents. The final text now keeps the measures separate and makes no stronger claim. The frozen experiment and outcomes remain unchanged.

The stated CPU limit is an operating-system limit. Wall-time and output-size checks are periodic checks, not hard real-time limits. Peak memory was not measured. These limits are stated. No new experiment was needed to correct the reporting scope.

## Checklist review aid

The reviewer read the relevant parts of the official [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) on 2026-10-28. The checklist is a review aid. This is not NeurIPS approval or a claim of submission compliance.

| Topic | Review result |
| --- | --- |
| Claims and limitations | Claims are limited to the stated finite model and local database. No global novelty or production-rate claim is made. |
| Assumptions and arguments | State, event order, truthful hold, complete revision protocol, and non-refundable spent use are defined. The conditional argument is supported. |
| Repeat procedure and evidence | Code, generated inputs, logs, database, controls, formulas, versions, and commands are retained. The eleven-file byte check passed. |
| Settings and uncertainty | The corpus is fully enumerated. There is no random sample, random seed, or justified population confidence interval. These limits are stated. |
| Compute | Actual run records and bounds are retained. The temporary-file and peak-memory limits are disclosed. |
| Ethical effects | The study uses invented values and local files. It makes no external account changes. The report explains limits on use of the rules. |
| Sources and rights | Original-source verification and rights checks are assigned to the separate source review. This review did not independently repeat every original-source check. No new license is assigned. |
| AI use and human review | The report states that Codex generated the work and that separate Codex agents checked it. It states that no human or external peer review occurred. |

## Checks outside this review

The package manifest, broad privacy and secret scan, final external-link checks, and remote publication check remain separate tasks. Their completion is not established by this review. A local file or successful review is not proof of publication.
