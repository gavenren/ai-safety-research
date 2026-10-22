# Repeated gate requests during overlapping undo

Date: 2026-10-22, America/Toronto.

## Abstract

A reader gate must remain closed while any protected undo operation is incomplete. A single flag can open when only one of several operations finishes. Repeated requests add a different problem: a late close can block readers after its operation has finished. We compared four gate rules in a complete synthetic corpus of 1,596 two-operation histories. The Boolean rule opened too early in 1,196 histories. A nonnegative count did so in 180. An active-ID set never opened too early, but remained closed at the end of 850 histories. A registry that retained both active and completed IDs matched the declared oracle at every point. Seven one-operation controls and a second full run supported the checks. This is an exact model comparison. That original corpus is not a production test, a new locking algorithm, or a measurement of AI-agent performance.


Eight selected Google Drive cases added 40 observed boundaries. The flag and count rules admitted three reads while another operation remained pending. The registry matched the selected checkpoints. One late read and one missing fresh metadata baseline limit the full-set claim.

The sections below describe the original synthetic study. The dated production extension at the end gives the later live evidence, checks, and limits.

## Research question and safety relevance

How do shared reader gates behave when two undo operations overlap and their close or release requests repeat?

A **gate** is a rule that permits or refuses a reader. An **operation ID** names one complete undo. A **history** is an ordered sequence of delivered requests. A **prefix** is the part of a history up to one selected request. The **oracle** is the test rule for a correct gate decision. An **atomic** update takes effect as one model step. An **idempotent** request has no additional effect when it repeats.

An AI agent can use a gate before it reads a changing record. If the gate opens too early, a read may use incomplete work. If it stays closed without a reason, the agent cannot complete the read. These are different failures. This study measures them separately. It does not simulate the record's fields or the reader's later action.

## Related work and contribution

Shahare, Chabbi, and Hegde study unbalanced release in shared-memory locks. Their Boolean-lock analysis explains how an unowned release can admit work incorrectly, and how an owner check can prevent it. We read the arXiv v1 preprint, including its Boolean-lock section. Our gate permits several undo operations to be active. It is not a mutual-exclusion lock. [Shahare et al., 2023](https://arxiv.org/html/2304.11983v1)

Redis documentation also uses an ownership value for safe release. Amazon's retry guidance describes retained request identity and late requests after a resource was removed. These are established reasons to track more than a current flag or current set membership. We do not test Redis or AWS services. [Redis documentation](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/), [Featonby, Amazon Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

Atomix v2 uses a transaction lifecycle and runtime-owned concurrency control for agent tools. Its scope is much larger than this gate model. We do not implement it, import its results, or claim a new lifecycle mechanism. [Mohammadi et al., preprint, 2026](https://arxiv.org/html/2602.14849v2)

The earlier [October 22 visibility study](https://github.com/gavenren/ai-safety-research/blob/main/research/2026-10-22-undo-visibility/report.md) tests one gate owner and interrupted field changes. The present note adds multiple gate owners and repeated gate requests. The [October 18 retry-retention study](https://github.com/gavenren/ai-safety-research/blob/main/research/2026-10-18-retry-retention/report.md) varies memory expiry. This note has no expiry. Its limited contribution is the complete gate corpus, exact comparison, and saved witnesses. The [source record](source_search.md) gives search terms and reading limits. A limited search does not prove novelty.

## Method

The [plan](plan.md), [configuration](config.json), and source search were saved and hashed before code or trials. A count-check sentence was corrected before implementation. The initial files and the correction record are retained. The event constraints and hypotheses did not change. See [freeze.json](freeze.json) and [deviations.md](deviations.md).

### Operations and delivery

There are two operations, A and B. Each has a first close, C0, and a first release, R0. C0 begins the modeled work interval. R0 completes that interval. Each can also have one duplicate delivery, C1 or R1. For each ID, C0 must precede R0 and C1; R0 must precede R1. A duplicate close can arrive after release. A duplicate request does not restart or finish the actual work.

Work starts only after its first close. Completion and first release share one model boundary. Thus the model excludes a delayed first release after actual completion. Each rule sees only the ID and the request type. It is not told whether the delivery is a duplicate. IDs do not expire or get reused. Every gate update and reader check is atomic. All readers obey the gate. These assumptions are part of the model, not measured provider guarantees.

### Four rules

| Rule | Close request C | Release request R | Closed condition |
| --- | --- | --- | --- |
| Boolean | Set flag true | Set flag false | Flag is true |
| Nonnegative count | Add one | Subtract one, with a floor of zero | Count is positive |
| Active-ID set | Add ID | Remove ID if present | Set is not empty |
| Lifecycle registry | Change absent ID to active; otherwise keep its state | Change active ID to completed; otherwise keep its state | Any ID is active |

The count is a declared baseline, not a library semaphore. The lifecycle registry retains completed entries throughout the test. None of these rules prevents two undo operations from writing at the same time. The gate only governs readers.

### Oracle, corpus, and measures

After each request, the oracle requires a closed gate exactly when at least one operation has passed C0 but not R0. An **unsafe-open history** has at least one point that permits a reader during active work. An **overblocked history** has at least one point that refuses a reader when no work is active. A **final-closed history** ends with the gate closed after both operations and all included duplicate deliveries are complete. These categories can overlap.

We enumerate all 16 duplicate-presence patterns and every request order permitted by the constraints. The primary corpus has 1,596 histories and 11,394 checked points. Seven one-operation histories give 23 control points. Four rules give 6,412 rule-history outcomes across both groups. Five additional hand histories check known cases, including the empty history. No history is sampled, excluded, or replaced.

The count is checked in two ways. An operation has one local order without a duplicate close, two with only a duplicate close, and three with both duplicates. For two local histories of lengths a and b, there are `choose(a+b,a)` interleavings. Multiplying by their local-order counts and summing the 16 patterns gives 1,596. A separate permutation-and-filter enumerator matches the recursive generator for every pattern.

This is complete enumeration of a designed corpus. Counts depend on the selected delivery constraints and multiplicities. They are not probabilities, time fractions, or estimates of website failure. No random seed, confidence interval, or significance test is needed. No model training or data split is involved.

## Results

### Primary comparison

All 1,596 primary histories were valid. None was unknown. All work was complete by the last request. The table reports gate failures, not incomplete undo work.

| Rule | Histories | Unsafe-open histories | Overblocked histories | Final-closed histories |
| --- | ---: | ---: | ---: | ---: |
| Boolean | 1,596 | 1,196 | 978 | 512 |
| Nonnegative count | 1,596 | 180 | 1,478 | 888 |
| Active-ID set | 1,596 | 0 | 1,170 | 850 |
| Lifecycle registry | 1,596 | 0 | 0 | 0 |

| Rule | Unsafe-open points | Unnecessary-closed points |
| --- | ---: | ---: |
| Boolean | 1,520 | 1,310 |
| Nonnegative count | 180 | 2,614 |
| Active-ID set | 0 | 2,108 |
| Lifecycle registry | 0 | 0 |

Without any duplicate, the Boolean rule failed in four of six histories. The other rules had no failure in those six histories. The full corpus contains 1,064 histories in which A and B were active together, and 532 in which their actual work did not overlap. The Boolean rule had 132 unsafe-open histories even in the latter group. A delayed release duplicate from completed work can open a gate during later work.

Among the seven one-operation controls, none of the rules opened too early. The Boolean and active-ID rules each had two final-closed histories; the count had three. The lifecycle registry had none. All five hand histories passed their 40 expected unsafe/final-state checks. The frozen criteria for H1 through H4 were met. Complete duplicate-count and overlap groups are in [summary.json](summary.json).

### Saved witnesses

In history 9, the requests are `A_C0, B_C0, A_R0, B_R0`. After `A_R0`, B is still active. The Boolean gate is open. No duplicate is needed for this error.

History 90 shows the count failure even without overlapping actual work:

| Request just delivered | Active work | Count | Gate |
| --- | --- | ---: | --- |
| A_C0 | A | 1 | Closed |
| A_R0 | None | 0 | Open |
| B_C0 | B | 1 | Closed |
| A_R1 | B | 0 | Open, incorrectly |
| B_R0 | None | 0 | Open |

History 267 is `A_C0, A_R0, A_C1, B_C0, B_R0`. The active-ID set removes A at the first release, then adds it again at the late close. It ends with A in the set, although both operations are complete. The lifecycle registry keeps A's completed state and ignores that close. See [witnesses.json](witnesses.json).

### Checks and reproduction

Every saved point was checked against a second set of formulas. That checker derives active work from first-event positions. It derives the count from a reflected prefix sum and active-set membership from each ID's most recent request. It does not share the main evolving state. The run recorded 226,149 comparisons, schedule-count checks for 20 patterns, and A/B symmetry checks for all 1,596 primary histories. The same Codex agent wrote both evaluators, so these are alternate implementation checks, not an independent author evaluation.

A second full run used unchanged code and fresh output paths. Six deterministic files matched byte for byte, including all raw results. These are two executions of the same 1,603 histories, not 3,206 distinct cases. [checks.json](checks.json), [reproduction.json](reproduction.json), and both execution records retain the evidence.

## Discussion

Tracking active IDs prevents one ID's release from removing another active ID. It does not identify an ID that was active and then completed after its entry was removed. A late close can therefore create a false active entry. Keeping a completed state removes that ambiguity under the model's no-reuse rule.

The registry result has a simple induction. Before C0, an ID is absent. C0 makes it active. A duplicate C leaves it active. R0 makes it completed. A later C or R leaves it completed. Thus an ID is active exactly during its declared work interval. The gate takes the union of these active states, so it equals the oracle after every request. This reasoning requires the declared event order, complete retained state, unique IDs, atomic updates, and full reader compliance.

The active set also cannot omit an unfinished ID under these assumptions. After C0 adds an ID, there is no release for that ID until its work is complete. This explains its zero unsafe count. The set's problem is unnecessary refusal after completion. That is a service failure and must not be counted as successful reader completion.

A practical gate claim therefore needs both ownership and lifecycle scope. “The gate is open” alone does not prove that protected work is complete. “No unsafe read occurred” alone does not show that readers could finish. These are design implications from the finite model, not a tested browser policy.

## Limitations

The corpus has at most two operations and one extra delivery of each request. It has no threads, network, database, crash, lost request, expiry, ID reuse, wrong ID, or malicious request. All operations eventually complete. The first release exactly marks completion. Real deployments can violate these assumptions.

The registry stores completed IDs without a limit. This study does not propose a retention policy or measure storage cost. If an entry is removed while an old request can still arrive, the late-close problem can return. If IDs are reused, refusing every close for a completed ID can refuse valid new work. Neither case was tested here.

No claim is made about correctness of the underlying undo writes, lock fairness, wait time, provider APIs, AI performance, or production safety. The experiment tests gate decisions at discrete boundaries. It cannot estimate how long a false gate state would last. Equal weight for all enumerated histories is a corpus choice, not a distribution of real traffic.

## Ethical and misuse considerations

The original corpus is synthetic. That experiment used no account record, user message, production site, or private data. It made no external action. The code is a small model of gate states, not an exploit of a service. The main misuse risk is treating a zero failure count as a general safety guarantee or treating blocked work as completed work. The report states those limits.

Original sources are attributed. No source code, dataset, figure, or paper is redistributed. No new license is assigned to the repository owner's work.

## Reproduction and resources

Follow [README.md](README.md). The study uses Python 3.13.7 and its standard library on Darwin 25.6.0, arm64. The first run used 0.416110 CPU seconds and 0.458064 wall seconds. The second used 0.383866 CPU seconds and 0.391303 wall seconds. The configured limits were 60 CPU seconds and 120 wall seconds per run, with at most two full runs. Both passed. There was no paid compute or model API call inside a trial.

The package retains the complete JSONL histories, summaries, control traces, code, versions, hashes, commands, logs, and both execution records. Before execution, one analytic count-check sentence was corrected. No trial failed and no post-result method change occurred. The [failure record](deviations.md) preserves that distinction.

## AI use and review status

Codex generated this study and report. A Codex study agent searched sources, specified the model, wrote and ran the code, and wrote the report. The main Codex agent coordinates the batch and publication. A separate Codex agent wrote an evaluator before it read the implementation or results. It matched all 1,603 histories and all 11,417 event points, and checked the sources and report. The [review record](separate_review.md) states its scope and limits. The exact model build was not exposed in the experiment record. No AI model was queried by the experiment. No human review or external peer review occurred.

The [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) was used as a review aid. [checklist.md](checklist.md) maps the relevant checks to evidence. This does not establish conference approval, certification, or submission compliance.

## References

The original source links appear next to the claims they support. [references.bib](references.bib) gives complete records. [source_search.md](source_search.md) gives reading limits, and [source_checks.md](source_checks.md) records later metadata checks.

## Production browser extension, 2026-10-22

This extension tests the four fixed gate rules with saved temporary folders in Google Drive. It is separate from the synthetic corpus above. A browser agent executed prescribed actions. It did not select its own policy. The contribution is a small check of how these rules control real browser reads, including an audit of failed timing checks. The rules are established mechanisms; no new general algorithm is claimed.

### Method

Eight cases applied four rules to two prescribed request schedules. The same two private test folders were reused. Their native identities stayed fixed. At each case start both names ended in DONE. A first close instructed a browser rename to PENDING. A first release renamed the folder to DONE, read the saved name, and then proceeded to the recorded reader check. Gate states were computed from the frozen rules before the cases; each probe used its prescribed state. A repeated request changed only this local decision state. It did not repeat the provider rename or restart work.

G1 was `A_C0, B_C0, A_R0, A_R1, B_R0`. It tests overlapping work and a repeated release. G2 was `A_C0, A_R0, A_C1, B_C0, B_R0`. It tests a late close after completed work. The gate began empty for each case. A and B were local operation names within that case. State was not shared between cases.

The plan, rules, assignments, and two amendments preceded the browser cases. The second amendment required a page reload and saved DOM identity and name checks after each changed folder. DOM means the page elements that the browser reads. A permitted guarded read inspected both exact folder rows. An audit read had a separate role and could inspect a closed gate's folders. No guarded read was dispatched for a refusal.

The saved reader extracts contain the actual row `data-id`, exact name, role, and time. The audit matched each actual ID to the setup identity. It checked the parent URL and retained hashes of the full private UI records. Full connector metadata at each later case boundary checked both IDs, DONE names, folder types, parent, and not-shared status. The connector did not expose `trashed` or `version`; neither field is claimed as checked. The first case has setup metadata and fresh UI identity evidence, but lacks the planned fresh full connector start read.

An unsafe permitted read is an actual guarded browser read while at least one saved folder name is PENDING. An unnecessary refusal blocks a reader while both names are DONE. These terms refer to the supplied test contract. PENDING names do not establish a harmful real workflow, and a local gate is not a Drive access control. Google documents the folder and organization interface; the saved records establish what this test actually observed. [Google Drive Help](https://support.google.com/drive/answer/2375091?hl=en)

### Observed results

All eight assigned cases remain in the record. Forty request boundaries have saved identity and state evidence. There were 32 browser rename dispatches and 14 completed guarded browser reads. Three reads occurred while B was PENDING. The Boolean rule admitted two after A's first and repeated releases in G1. The count admitted one after A's repeated release. There were five unnecessary refusals in G2. Both folders ended DONE in every case.

| Rule | Cases | Boundaries | Actual guarded reads | Unsafe permitted reads | Unnecessary refusals | Final-closed cases |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Boolean | 2 | 10 | 5 | 2 | 1 | 0 |
| Nonnegative count | 2 | 10 | 3 | 1 | 2 | 1 |
| Active-ID set | 2 | 10 | 2 | 0 | 2 | 1 |
| Lifecycle registry | 2 | 10 | 4 | 0 | 0 | 0 |

This table is descriptive. The two folders were shared fixtures, and the cases were selected witnesses. The counts are not independent task results or failure probabilities. A zero in the registry row applies only to these ten observed boundaries under the stated rules.

### Failed checks and observation limits

One checkpoint exceeded the frozen 30-second uncertain-read bound. In G1 with the nonnegative count, the step-5 reload was recorded at 16:13:33.112 UTC. The first authoritative correct DOM read was at 16:14:25.885 UTC: 52.773 seconds later. The later DONE result is retained as a descriptive observation. The case is not treated as a completed result under the strict timing rule. No replacement case or repair write was added.

The seven other cases met the measured observation timing limit. All eight case intervals, measured from first staged decision to final probe record, were below eight minutes: 58.225 to 140.003 seconds. Six cases also have the planned fresh full connector reads at both boundaries. This smaller set excludes G1 Boolean for its missing fresh start metadata and G1 count for its late read. It contains no unsafe permitted read, five unnecessary refusals, and two final-closed cases. This is a restricted description, not evidence that the omitted failure patterns are absent.

The first Boolean case used saved `recheck` files for steps 1–3 and a guarded-read file for step 5. Step 4 was a local repeated release followed by a guarded read. These actual files are mapped in [live_evidence_map.md](live_evidence_map.md). Delayed probe bookkeeping did not establish a timeout: the limit check uses the first authoritative DOM read. The first count case also required later saved checks after steps 3 and 5. No absent audit file was invented.

Two earlier accessibility snapshots differ from their later DOM reads: G1 active-ID step 5 and G1 registry step 1. The executed helper captures accessibility text first, then reads the actual row ID and text. The later DOM read supplies the checkpoint value. Both observations and their times remain in the evidence. The analyzer was corrected to preserve this sequence, rather than require two sequential observations to be simultaneous. It made no change to raw evidence or account state.

The browser run also had a refused helper-loading attempt and a helper-closure issue. The execution notes retain these issues. They are test-runner issues, not naturally observed provider retry failures. The saved files do not establish an exact count of every internal browser read needed to enforce the two-inspection cap. The report therefore does not claim that every frozen execution check passed.

Staged decisions were saved before dependent writes. A release decision's time is not its activation time. The probe record follows the saved row read and any permitted reader. There is no separate activation clock, and no probe was made inside a Save interval. These data do not establish atomicity between a gate check and a website read.

### Interpretation and limits

The selected browser cases show the same qualitative distinctions as the small model: a flag can discard another operation's protection, a repeated release can reduce a count incorrectly, and a late close can restore an already completed ID to an active set. Retained completion state avoided those observed errors in the selected cases.

The gate was a local cooperating-reader rule. Other browser tabs, clients, and users did not obey it by construction. A verifier could still read while the local gate was closed. The study did not install or test a native provider lock, inject a server race, measure uncontrolled network retries, or test autonomous agent policy selection. Fixture creation used connectors and was not counted as browser testing. No statistical interval or significance claim is justified.

### Reproduction, privacy, and review

The public package retains alias-only observed states, source hashes, exact request schedules, frozen controller code, and analysis code. A second local scoring run produced identical output and matched 200 controller/state checks. This repeats analysis of saved evidence; it is not a second live trial. See [live_README.md](live_README.md), [live_evidence.json](live_evidence.json), and [live_results.json](live_results.json).

Raw account IDs, private URLs, account names, and full UI records remain private. The public extract cannot independently reveal or re-query those identities. The private audit checked them before removal from the public extract. No new license is assigned. Only temporary records were used, and no external person was messaged.

Codex generated and ran this extension. Browser tools executed the visible actions; connectors made setup records and read saved metadata; Python audited and summarized the evidence. No human review or external peer review occurred. The exact model build was not exposed in these trial records. A separate agent reviewed the raw evidence and repeated the scoring. The review passed for the stated scope. The procedure deviations above remain. See [live_review.md](live_review.md). Cleanup was verified after scoring. The Drive parent is in Trash, and its 21-folder test scope has no active results. All 23 Calendar fixtures have exact-ID status cancelled, with no active results in the bounded primary-calendar test query. These are counts for the complete five-study run. They do not prove permanent erasure or account-wide absence. See [live_cleanup.md](live_cleanup.md) and [live_cleanup.json](live_cleanup.json).
