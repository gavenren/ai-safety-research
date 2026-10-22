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
