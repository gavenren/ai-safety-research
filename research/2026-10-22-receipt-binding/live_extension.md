## Production extension: receipt binding on Drive and Calendar

Date: 2026-10-22, America/Toronto. This extension adds 12 controlled production cases to the earlier synthetic study. The original synthetic corpus remains separate.

### Abstract

We tested two local receipt rules with temporary Google Drive folders and Google Calendar events. Each case included one real browser save and a later request to the local rule. The key-only rule returned six success responses. Four were false completion claims: the exact requested target did not contain the requested value. The bound rule returned two correct success responses and four conflicts. Neither rule sent a second browser save. These cases test local completion rules with real saved records. They do not test Google idempotency services. One interrupted reload prevents a claim that every time limit was met.

### Question, safety relevance, and contribution

Does a local receipt that compares only the operation ID produce a false completion claim when a later request changes its target or payload? A **receipt** is a local record of an action and its saved-field evidence. A **payload** is the set of fields that an action asks to save. A **false completion claim** is a success response when the exact requested target does not contain the requested value.

Such a claim can make a browser agent stop before it has done the requested work. The contribution is a checked set of production examples with native record identity, actual browser actions, online local decisions, and separate saved-field reads. It is not a new general algorithm. It does not establish novelty or a provider defect.

### Related work and sources

AWS describes storing the original parameters with a request ID and rejecting a later parameter mismatch. Stripe API v1 also compares repeat parameters with the original request. These are established safeguards. Our test applies that principle to a local browser receipt. We did not call either service. [AWS](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/), [Stripe](https://docs.stripe.com/api/idempotent_requests)

Google documents stable file IDs and names that need not be unique. Its Calendar resource defines IDs, descriptions, visibility, and an exclusive end date. Those documents guided field checks; they do not guarantee this local receipt policy. The connectors exposed fewer fields than the full API resources. [Drive](https://developers.google.com/workspace/drive/api/reference/rest/v3/files), [Calendar](https://developers.google.com/workspace/calendar/api/v3/reference/events)

The pre-execution source search is in `live_design.md`. `live_source_check.md` records the later verification of these primary pages. These are service documents, not peer-reviewed studies or preprints. The limited search does not prove novelty.

### Method and planned decisions

The plan assigned two rules, three request pairs, and two services: 12 cases. Each case had a fresh A record. Changed-target cases also had a fresh B record. Thus, 16 records were used. Connector calls created the records. Scored field changes used the supported browser tool. The local receipt decisions ran before the final audit reads.

The **key-only rule** returned success when the operation ID matched. The **bound rule** also compared service, account alias, native target ID, action, and exact payload. A mismatch returned CONFLICT. Exact repeats required complete first-save evidence. Each case reused its own operation ID deliberately; IDs were not shared between cases.

The hypothesis was that key-only matching would produce a false success for changed payloads and changed targets. The bound rule should return conflicts for those changes and success for exact repeats. We fixed these criteria before the browser cases. No random sample, learned model, or random seed was used.

| Pair | First browser save | Second local request | Required contract response |
|---|---|---|---|
| Exact | Set A to PAYLOAD-A | A, PAYLOAD-A | Success without a new save |
| Payload | Set A to PAYLOAD-A | A, PAYLOAD-B | Conflict without a new save |
| Target | Set A to PAYLOAD-A; B stays BASE | B, PAYLOAD-A | Conflict without a new save |

Drive changed a folder name under a fixed trial prefix. Calendar changed only the description of a private, Free, nonrecurring, all-day event on 2026-10-01. Its exclusive end was 2026-10-02. The events had no external guests, reminders, or attachments, and no returned meeting link. Only trailing CR and LF characters were removed from connector descriptions for comparison.

Before each Save, the browser checked actual native identity and the intended field. Drive identity came from the row's `data-id`; Calendar identity came from the observed editor URL. The browser recorded the input, dispatch, and postclick observation. A connector then read the saved resource. The local rule consumed that evidence and returned its response. A later connector read checked the exact intended target. Changed-target cases read both A and B.

The corrected runtime was frozen at 16:29:21 UTC, before all receipt dispatches. A separate agent had found that version 1 could accept an old read without first-save evidence. Version 2 required the action record, native identity, required UI fields, references, and time order. It passed 192 synthetic helper checks before use. Those checks are not production cases. The unchanged pure-rule hash is recorded in `runtime_intent_freeze.json`.

### Results

The same result pattern occurred on each service. Each table row below represents one case on Drive and one on Calendar.

| Rule | Pair | Local response | Value on the requested target after the response | False completion claims |
|---|---|---|---|---:|
| Key-only | Exact | Success | PAYLOAD-A | 0 of 2 |
| Key-only | Payload | Success | PAYLOAD-A; requested PAYLOAD-B | 2 of 2 |
| Key-only | Target | Success | BASE on B; requested PAYLOAD-A | 2 of 2 |
| Bound | Exact | Success | PAYLOAD-A | 0 of 2 |
| Bound | Payload | Conflict | PAYLOAD-A remains on A | 0 of 2 |
| Bound | Target | Conflict | BASE remains on B | 0 of 2 |

All 12 first browser saves were followed by a saved-field read. There were zero second browser saves. The key-only rule met the declared request contract in 2 of its 6 cases. The bound rule met it in all 6 selected cases. A conflict is not a completion claim; the requested changed value correctly remained absent.

Native IDs, record URLs, folder parents, and available fixed fields passed the private audit. Calendar's title, dates, Free/Private fields, self organizer/attendee, and other returned fields stayed unchanged. Drive's available fields stayed unchanged apart from the intended first name change and its modification time. After the second local response, every exposed field equaled the first saved read. B stayed equal to its baseline in all four changed-target cases.

The before-Save UI to final case-read intervals were 13.754–252.474 seconds, below the eight-minute case bound. Postclick UI to first saved-read intervals were 9.725–38.578 seconds. These are observation intervals, not network latency estimates. The full metadata baseline was one setup batch, 1636.952–1995.777 seconds before the fresh before-Save UI observations. We do not claim an immediate full metadata baseline for each case.

### Interruption, timing uncertainty, and failed checks

The first Drive key-only exact case timed out while the browser reloaded after Save. Its dispatch at 16:33:02.781 UTC and postclick UI at 16:33:03.412 UTC were retained. The connector read at 16:33:41.990 UTC confirmed PAYLOAD-A. The browser session was reset; Save was not repeated. `intent-first-drive-RECEIPT-K-EXACT-A.json` is a byte copy of `receipt-interruption-read.json`. They represent one observation, not two.

The failed reload's start time is not separately recorded. We cannot confirm the planned 30-second limit for an uncertain checkpoint in this case. The case remains in the descriptive results. The subset without this timing uncertainty has 11 cases and still contains all four false completion claims. This subset is not a random sample or a claim that all planned checks passed.

The initial runtime review failed because the first-action evidence gate was incomplete. It was corrected and frozen before these cases. The first Drive interruption did not change the rule or repair a scored value. A module wrapper was used after the browser session reset; its retained source contains the same field checks and single first Save operation.

The six Calendar saves did not have a reopened post-save editor check. The frozen plan called for a reopen or reload plus a connector read. The connector verified the persisted description and all other exposed fields after each Save. The all-day UI check was before Save only. A post-save all-day UI check is not available. This is a procedure deviation. All six cases remain in the results, with this limit.

### Discussion and limits

Zero second mutations did not imply correct completion. Key-only matching suppressed all second saves but still returned success for four requests whose intended field state was absent. Binding target and payload prevented these four false claims under the declared sequential contract.

The exact-match success is supported by the retained first read and final audit in these cases. This experiment does not establish how long a receipt remains valid if another writer can change the resource. No concurrent writer, crash, receipt expiry, key collision, or stale-evidence attack was tested. Both services belonged to one user's connected accounts. There was no cross-account test.

The second request went to a local policy, not a Google idempotency endpoint. We did not test native exactly-once behavior, server deduplication, or atomic update guarantees. A repeated rename can have the same visible result, so the zero-second-save count comes from controlled dispatch records and the runner, not from final values alone. Saved reads cannot prove the absence of all hidden provider activity.

Drive's connector did not expose `trashed` or `version`. Active parent state was checked in the before-Save browser view. Calendar's connector did not expose a full conference object, provider version/ETag, or an attested calendar container ID. All-day status came from the UI; converted date-time strings alone were not used to prove it. These missing fields limit the checks. Browser and connector reads are separate interfaces, not proven independent storage systems.

The cases were selected witnesses and controls. Counts are exact for this case list; they are not failure probabilities. There is no confidence interval or significance test because there was no population sample. No reported outcome was replaced or repaired within a scored case.

### Ethics, data, and tools

The user authorized temporary records in connected accounts. Only synthetic field values were changed. No external messages, invitations, permission changes, or paid compute were used. Native IDs, account information, URLs, and full UI states remain private. The public evidence has aliases, exact field tokens, comparison results, times, and hashes. Hashes establish file integrity, not the truth of a website observation. No new license is assigned.

Codex generated the design, study, code, and report. Browser tools made the visible changes; connectors created fixtures and read saved state; local Python code returned the receipt decisions and analyzed the evidence. A separate Codex agent audited the runtime before use and another agent built this evidence analysis. No human or peer review has occurred. The model and provider build IDs were not exposed as stable runtime identifiers. Python was 3.13.7. No new paid model API or training run was used.

Cleanup was verified after scoring. The Drive parent is in Trash, and its 21-folder test scope has no active results. All 23 Calendar fixtures have exact-ID status cancelled, with no active results in the bounded primary-calendar test query. These are counts for the complete five-study run. They do not prove permanent erasure or account-wide absence. See [live_cleanup.md](live_cleanup.md) and [live_cleanup.json](live_cleanup.json).

### Reproduction and review status

`live_README.md` gives the two local analysis commands. Both recorded replays reproduce `live_results.json` byte for byte. `live_evidence_map.md` explains the raw-to-public mapping and the interruption record. `live_private_extract.py` can recheck the private evidence when the authorized raw folder is available. Public replay alone cannot re-query those private resources or repeat the original live browser saves.

The relevant NeurIPS checklist items were used as a review aid: claim support, reproducibility, limitations, privacy, and responsible reporting. This is not a NeurIPS approval or submission claim. A separate agent reviewed the raw cases and reproduced the score. The review passed for the stated scope. See [live_review.md](live_review.md). The timing uncertainty remains as reported. [Checklist](https://neurips.cc/public/guides/PaperChecklist)
