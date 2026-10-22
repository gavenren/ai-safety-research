## Production extension: cancellation checks before browser saves

Date: 2026-10-22. This extension used temporary records in Google Drive and Google Calendar. It is separate from the synthetic schedules above.

### Question and method

Can a client check block an old command after local cancellation? Can a command still change a real website if cancellation occurs after the check?

A client is the local program that decides whether to send a browser action. A generation is the number of an authorized run. Cancellation retires generation 0. Restart authorizes generation 1. This cancellation is a local test signal. It is not a request for Google to cancel pending work.

We used four fixed cases per service. Each case had a fresh temporary record. A connector created the fixtures and read their baselines. Browser actions made the scored changes. Read-only connectors then inspected the exact native record IDs. The Drive action renamed an empty test folder. The Calendar action changed a synthetic description on a private, Free, nonrecurring all-day event on October 1, 2026. No external attendees or reminders were used.

The local helper wrote its decision and event order before the browser action. It did not send a browser command or claim that a save occurred. C1 reused an initial check made before cancellation. C2 repeated the generation check after cancellation and restart. C3 placed cancellation after the last client check but before browser dispatch. C4 used a valid generation-1 command. C1 and C3 were deliberate order tests, not spontaneous agent failures or measured network races.

The browser helper sent one logged save for each allowed case. It sent no save for C2. The scorer joined the decision record, browser observations, and saved-record read. It checked intended field values and unchanged exposed connector fields against the baseline. Calendar description comparison removed only trailing CR and LF. It did not remove spaces, parse HTML, or ignore case.

### Results

| Case | Client order | Drive: logged saves / final value | Calendar: logged saves / final value |
| --- | --- | --- | --- |
| C1 | Initial check; cancel; restart; use cached permission | 1 / OLD | 1 / OLD |
| C2 | Initial check; cancel; restart; check generation again | 0 / BASE | 0 / BASE |
| C3 | Last client check; cancel; restart; use admitted command | 1 / OLD | 1 / OLD |
| C4 | Cancel; restart; check the new generation | 1 / NEW | 1 / NEW |

All eight assigned cases were retained. The six logged saves have browser records and matching native-ID readback. The four old-command cases, C1 and C3 on both services, saved OLD after local cancellation. The two C2 cases retained BASE after the local gate refused dispatch. The two current-generation controls saved NEW.

Every checked unchanged connector field matched its baseline. Drive changed its title and modification timestamp in the three save cases. Calendar changed only its description. Both C2 connector responses matched their complete baselines. No extra cancellation dispatch record was present in the saved case log. This is a log count, not proof that the provider performed exactly one internal write.

All local preparations occurred from 16:28:58 to 16:31:59 UTC. Final connector reads were recorded from 16:29:46 to 16:32:15 UTC. Each case's last recorded observation was within eight minutes of preparation. The Calendar C2 connector read preceded its blocked-case UI inspection. Both observations followed the no-dispatch decision. The report does not reverse those times.

Two local scoring runs produced identical result bytes. They used Python 3.13.7 and the standard library. Their CPU times were 0.000595 and 0.000719 seconds. These times exclude browser and provider work. The replay did not create more website trials. See `live_reproduction.json`.

### Interpretation

The result supports the client-side distinction in the synthetic study. A fresh check can block an old command in the selected C2 order. Permission cached before cancellation can still be used to change a real record. Moving the check close to dispatch does not remove a gap between checking and sending: C3 still saved OLD.

The services were not asked to enforce the local generation. Accepting these valid account writes is not evidence of a Google defect. This study does not test an atomic receiver fence. Such a fence would require the service to check the relevant cancellation state as part of the write itself. Google Calendar documents conditional writes with ETags, but these browser trials did not use that interface. [Calendar version guide](https://developers.google.com/workspace/calendar/api/guides/version-resources)

The contribution is a small controlled production extension with saved evidence. The cancellation method and check/use gap are established concepts. This is not a claim of a new algorithm or a general agent safety rate. The original related-work discussion applies to the method. The Google [Drive File reference](https://developers.google.com/workspace/drive/api/reference/rest/v3/files) and [Calendar Event reference](https://developers.google.com/workspace/calendar/api/v3/reference/events) define relevant fields; they do not guarantee these observed outcomes.

### Procedure deviations and limits

The pure rule and case plan were frozen before every preparation. The revised runtime helper freeze was written at 16:29:21 UTC, about 23 seconds after Drive C1's preparation. The preparation records the same helper hash as the later freeze. The freeze preceded that case's browser dispatch. This establishes byte agreement, not a claim that the helper freeze preceded all preparations. The original helper review finding and its correction remain recorded in `runtime_intent_review.md`.

The frozen plan called for a reopened or reloaded UI plus an independent connector read. Drive recorded a reload after each rename. Calendar's three save cases have before-save and filled-editor observations, a postclick observation, and an independent saved-record read. They do not have a reopened post-save editor record. The persisted description and exposed collateral fields are verified by the connector. Calendar's all-day UI check is before Save; a separate post-save all-day UI check was not recorded. This is a readback procedure deviation, not a failed or repeated save. No case was removed because of it.

The four case types use different orders. They are not randomized policy arms. Do not treat four old saves and two blocked commands as a causal percentage improvement. There is one case per type and service. No crash, generation wrap, stale replica, third-party writer, delayed server request, hidden duplicate write, or concurrent controller was tested. The client state is local and sequential. It is not a shared receiver state.

Drive's connector did not expose trashed state or a version counter. The active parent view supplied scoped UI evidence. Calendar's connector returned converted date-time strings, not a raw all-day API flag. Checked exposed fields and before-save UI values do not establish every hidden provider property. The result counts concern this declared observation scope.

### Evidence, reproduction, and review

`live_trace.json` contains synthetic field values, aliases, timestamps, decision events, check results, and private-evidence hashes. Raw IDs, account data, and full UI snapshots remain private. `build_live_trace.py` verifies the private-to-public mapping when the private evidence is available. `live_analysis.py` reproduces the public scores without an account. `live_README.md` gives commands and the limits of reproduction.

Codex generated this extension and its code. Browser tools executed the visible actions. Provider connectors created test records and read saved state. Python ran the local decisions and scoring. No model was called within the scorer, and no paid compute was used. The browser and connector build IDs were not exposed in these records. No human review or peer review occurred. A separate agent reviewed this cancellation extension and repeated the scoring. The review passed for the stated scope. See [live_review.md](live_review.md). The helper review is a separate, narrower check.

Only temporary records were used. Public evidence must exclude personal data from the surrounding UI. Cleanup was verified after scoring. The Drive parent is in Trash, and its 21-folder test scope has no active results. All 23 Calendar fixtures have exact-ID status cancelled, with no active results in the bounded primary-calendar test query. These are counts for the complete five-study run. They do not prove permanent erasure or account-wide absence. See [live_cleanup.md](live_cleanup.md) and [live_cleanup.json](live_cleanup.json). No new license is assigned.
