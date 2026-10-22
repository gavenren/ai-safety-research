# A receipt must identify both the operation and its intended change

Date: 2026-10-22, America/Toronto. Extra study requested by the repository owner.

## Abstract

A repeated request can reuse an old operation ID with different data. A receipt can then confirm the wrong change, even when no extra effect occurs. We tested five receipt rules on all 256 ordered pairs from a 16-request alphabet. A key shared across accounts gave 112 false success replies. An account-scoped key without a payload check gave 48 false success replies, with zero incorrect effect histories. A rule that checked account, operation ID, and the stored payload matched the contract in all 256 pairs. These are exact counts in a synthetic model. They are not provider or AI-agent failure rates.


Twelve selected cases on Google Drive and Calendar added 12 first browser saves and no second saves. Key-only receipts made four false completion claims in six cases. Target-and-payload checks made none in six cases. One interrupted reload has uncertain timing compliance; the second requests used a local policy.

The sections below describe the original synthetic study. The dated production extension at the end gives the later live evidence, checks, and limits.

## Research question and safety relevance

How do receipt scope and immutable payload checks affect false success replies and repeated effects when a request ID is reused?

A **receipt** is a saved record of a completed effect. An **operation ID**, or key, identifies one intended operation. The **payload** is the target and numeric change. **Idempotency** means that retrying the same logical operation does not add another effect. A **scope** states where an ID has meaning. Here, each account has its own ID scope.

An AI agent can retry a command after a missing response. It can also change a target while retaining an ID. A success reply must support the current intent. Absence of duplicate effects alone does not prove that the reply is correct.

## Related work and contribution

The AWS Builders Library describes caller-scoped request IDs and checks for changed parameters. Stripe's API v1 reference describes replay of a saved result and rejection of changed parameters. These mechanisms are established. This study does not introduce a new idempotency algorithm. [Featonby, AWS](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) [Stripe](https://docs.stripe.com/api/idempotent_requests)

The repository's October 18 retry-retention study used fixed payloads. This note excludes retention and varies identity scope and payload. Its contribution is a complete, paired regression set with separate measures for false replies and effect errors. A limited [source search](source_search.md) does not prove novelty. No fault in AWS or Stripe is alleged or tested.

## Method

The [plan](plan.md), [configuration](config.json), and source log were frozen before implementation. The code hash was saved before the first execution. See [freeze.json](freeze.json) and [implementation_freeze.json](implementation_freeze.json).

Each request is `(account, key, target, delta)`. There are two accounts, two keys, two targets, and two deltas, −1 and +1. This gives 16 requests and 16² = 256 ordered pairs. Each rule receives every pair. There are 1,280 rule cases. The first request always commits. The second request has one of three contract outcomes:

- A new `(account, key)` applies one new effect.
- An existing identity with the same payload replays the first receipt.
- An existing identity with a changed payload returns a conflict and adds no effect.

This is the selected contract, not a claim about every provider. Receipts contain the full request and an effect sequence number. All operations are sequential and atomic. Receipts never expire. A conflict is a refusal, not a success.

The first four rules use different store keys. They replay an existing receipt when that key matches. Otherwise they apply a new effect. The fifth rule stores receipts by `(account, key)` and checks the original target and delta before replay.

The oracle classifies identity and payload equality directly. It does not use the receipt store. It compares the expected second action, full receipt, and ordered effect history. A false success is a conflict reported as success, or a success receipt for another intent. Missing and extra effects are counted separately. Ordered effects remain visible even when opposite deltas cancel in the final numeric state.

Named controls cover exact retries, equal keys in different accounts, changed targets, changed deltas, and new IDs with equal payloads. They are members of the full corpus, not extra independent cases. The hypothesis required the bound-receipt rule to match every case and each baseline to have an error. No random sampling, training, data split, or seed was used. A confidence interval would not describe uncertainty about this fully enumerated set.

## Results

All 1,280 rule cases completed. There were no unscored cases or failed assertions.

| Receipt rule | Pairs | False success replies | Missing effects | Extra effects | Wrong effect histories | Exact contract matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Key only, shared across accounts | 256 | 112 | 64 | 0 | 64 | 144 |
| Account and key | 256 | 48 | 0 | 0 | 0 | 208 |
| Account, target, and key | 256 | 48 | 0 | 32 | 32 | 208 |
| Full request as store key | 256 | 48 | 0 | 48 | 48 | 208 |
| Account and key, with stored payload check | 256 | 0 | 0 | 0 | 0 | 256 |

There are 192 new-identity pairs, 16 exact retries, and 48 payload conflicts. The checked rule applies, replays, and rejects those groups, respectively. It does not convert a conflict into a completed operation. [summary.json](summary.json)

For a concrete false reply, first apply `(A,0,x,+1)`, then request `(A,0,x,−1)`. The account-and-key rule returns the first receipt. Its effect history is correct under the contract because the changed payload must not execute. Its success reply is wrong. The full-request rule instead applies −1 as a new effect. The final numeric state returns to zero, but the forbidden second effect remains in the history. [controls.json](controls.json)

The following count check was derived after execution. For each first request, 12 second requests have another identity, one is identical, and three change its payload. Multiplication by 16 gives 192, 16, and 48. The global-key rule also confuses four requests in the other account for each first request, which gives 64 missing effects. Those 64 false replies plus the 48 conflicts give 112. This derivation agrees with the raw cases.

Both planned executions used unchanged Python 3.13.7 code on macOS 26.7.2 arm64. The first used 0.039504 CPU seconds; the repeat used 0.037740. All four deterministic result files matched byte for byte. The repeat is not a second sample. [reproduction.json](reproduction.json) records hashes. The execution receipts record exact commands, versions, and times.

## Discussion

The account-and-key rule has no incorrect effect history in this corpus, yet it gives 48 false success replies. Thus an audit that checks only duplicate effects can miss incorrect completion claims. Adding payload fields to the store key also has a limit: it can turn conflicting changes into distinct effects. Under this contract, the payload is a condition to validate, not an extension that creates a new identity.

The checked rule succeeds because it implements the declared sequential contract. The result is a regression test and a counterexample set. It does not prove a new general safety property.

## Limitations

The corpus has only two requests per case. Atomic writes, permanent receipts, correct account identity, and exact equality checks are assumptions. Crashes, races, expiry, hash collisions, authorization, transport faults, and uncertain effects are absent. The original model did not test a live service, browser agent, connected account, or language model. Counts depend on this artificial alphabet and are not real-world probabilities. A different API contract can correctly allow a different result.

## Ethical and misuse considerations

The study uses new synthetic values and local code. It has no private records or external effects. No service was purchased. The main misuse risk is to call these counts provider faults or a general safety guarantee. Sources are linked and paraphrased. No external code, figures, or dataset are redistributed. No new license is assigned to the owner's work.

## AI use and review status

Codex generated the study, code, analysis, and report. Web search checked primary sources; local Python executed fixed rules. No model was called inside a trial. The exact runtime model build was not exposed and is not an experimental variable. A separate Codex agent checked all 1,280 saved outcomes with its own evaluator, checked the report and original sources, and found no material error. The [review record](separate_review.md) states the review limits. No human review or external peer review occurred. The NeurIPS checklist is a review aid, not approval or certification.

## References and reproduction

See [references.bib](references.bib) and [source_search.md](source_search.md) for checked sources and read scope. Follow [README.md](README.md) to repeat the run. [cases.jsonl](cases.jsonl) contains every request pair, rule output, oracle result, and score. [checks.json](checks.json) records the built-in checks.

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
