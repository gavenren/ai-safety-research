## Production browser extension, 2026-10-22

This extension used six temporary events in Google Calendar to test execution of the three fixed undo rules. It is separate from the synthetic corpus above. The browser agent followed paths from the frozen controller. It did not choose a policy on its own. The contribution is a check of saved fields and actual path execution through a production website, with explicit limits on what the supplied condition means.

### Method

Each case used a fresh event. Bits a, b, and c were represented by exact tokens in title, location, and description. The title retained a unique trial prefix. A token ending in 1 meant one; a token ending in 0 meant zero. The events were private, Free, nonrecurring, and all-day on October 1, 2026. The connector end date was October 2, which is exclusive. A connector-added self attendee was retained under amendment 01. There were no external attendees, and no attendee list was changed.

Each rule ran once under the witness condition `{000,010,011,101,111}` and once with all eight states valid. Priority was bac. The only scored action changed one field token from 1 to 0 through the browser and saved the event. The supplied invariant, or condition required at every state, was `a implies c` and `c implies (a or b)`. Google Calendar does not enforce this condition. These are test markers, not real meeting dependencies or a natural Calendar validation rule.

The plan, assignments, rules, and amendments preceded scored browser actions. Connectors created the fixtures and read a full pre-run baseline batch. Setup was not counted as browser testing. Each case then had a fresh browser baseline. After each Save, the browser reopened the exact event editor and read all three DOM field values. The DOM is the set of page elements read by the browser. Title and location came from the elements' values; description came from its visible text. The observed editor URL was decoded and matched to the event's native ID. A title match alone was insufficient.

The intermediate checks also verified visible All day, Free, and Private fields. Full final connector reads checked the identity, all three tokens, dates, status, organizer, self-only attendee list, reminders, recurrence, available conference-link field, attachments, and event type. Every other field exposed by this connector remained equal to the full baseline. The connector did not expose a full conference object, a server version, or a calendar container ID in its returned event body. No stronger check is claimed.

Google documents event creation, all-day events, and edit-and-save actions. Its event resource documents separate summary, location, and description fields. Those sources support the interface description. The saved evidence supports the outcomes below. [Google Calendar Help](https://support.google.com/calendar/answer/72143?hl=en), [Google Calendar Events resource](https://developers.google.com/workspace/calendar/api/v3/reference/events)

### Observed results

All six assigned cases have saved paths. There were 16 browser field changes and 22 full editor observations, including the six baselines. No case was replaced. Five cases reached 000. Four reached 000 without a saved invalid state. The witness fixed-order case passed through 001, which violates the supplied condition. The witness greedy case stopped at 101.

| Condition | Rule | Observed saved path | Target reached | Every saved state valid |
| --- | --- | --- | --- | --- |
| Witness | Fixed | 111, 101, 001, 000 | Yes | No |
| Witness | Greedy | 111, 101 | No | Yes |
| Witness | Complete | 111, 011, 010, 000 | Yes | Yes |
| All states valid | Fixed | 111, 101, 001, 000 | Yes | Yes |
| All states valid | Greedy | 111, 101, 001, 000 | Yes | Yes |
| All states valid | Complete | 111, 101, 001, 000 | Yes | Yes |

The greedy stop record names the two rejected continuations, 001 and 100. Neither is permitted by the witness condition. The final connector read confirmed 101. Complete search used the same single-field action capability and followed 111, 011, 010, 000. Thus the saved website records show both the locally valid stop and a feasible alternative from the original start.

The stop is relative to the specified one-way action set. A later corrective edit could set a bit back to one. This test does not establish irreversible data loss. Likewise, saving 001 is a test-contract failure, not evidence of a defect in Calendar's own validation.

### Observation and execution limits

The full connector baselines were collected in one batch before the six cases. They were not separate immediate connector reads before each case. Fresh browser baselines checked the three tokens and the stated visible fields. No test write occurred to an event between its full baseline and its case. An unobserved external writer remains outside this test's scope.

The witness greedy case's final connector read occurred after its write but before its successful final browser read. The browser then read 101 and recorded the stop. There is one retained successful DOM read for that step; no earlier successful DOM read is assumed. This sequence is in the evidence map.

The first case had a pre-baseline navigation/loading issue. No Save preceded its verified baseline. The initial editor placeholder file was later overwritten by the verified baseline file. Other retained open and ready observations document that issue. The report does not claim that every pre-baseline UI snapshot remains available. No post-Save DOM read failed in the scored paths.

The recorded interval from the post-Save UI snapshot to the successful DOM read ranged from 1.935 to 33.588 seconds. This includes tool scheduling and is not a provider latency measure. The 30-second retry bound applies after an uncertain or failed observation; it does not start automatically at Save. No separately timestamped initial reopen/wait start was saved. The data therefore do not measure exact inspection latency. Every case's verified-baseline-to-final-read interval was below eight minutes.

The three field reads were sequential. They are not a proof of an atomic server snapshot. The supplied condition was fixed, and no concurrent edit or hidden side effect was tested. Complete search was calculated before execution. The small successful path does not establish that an agent can discover correct constraints or find an affordable plan in a large task. These are selected engineering cases, not independent samples or estimates of task failure rates.

### Reproduction, privacy, and review

The public package retains alias-only paths, actual write fields, chronology checks, full-contract comparison results, source hashes, frozen rule code, and analysis code. A local replay matched the saved results. It repeats analysis of retained evidence, not the original browser actions. See [live_README.md](live_README.md), [live_evidence.json](live_evidence.json), and [live_results.json](live_results.json).

Native account IDs, private event URLs, account names, and full UI records remain private. The private audit checked those identities before the public extract was made. Public readers can repeat the path scoring but cannot independently query the private events from this package. No new license is assigned. Only temporary records were used, with no external guests or messages.

Codex generated and ran this extension. Browser tools changed and read the visible fields; connectors created fixtures and read full saved events; Python checked and summarized the evidence. No human review or external peer review occurred. The exact model build was not exposed in the saved trial records. A separate agent reviewed the raw evidence and repeated the scoring. The review passed for the stated scope. See [live_review.md](live_review.md). Cleanup was verified after scoring. The Drive parent is in Trash, and its 21-folder test scope has no active results. All 23 Calendar fixtures have exact-ID status cancelled, with no active results in the bounded primary-calendar test query. These are counts for the complete five-study run. They do not prove permanent erasure or account-wide absence. See [live_cleanup.md](live_cleanup.md) and [live_cleanup.json](live_cleanup.json).
