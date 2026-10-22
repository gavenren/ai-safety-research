## Production extension: two saved page chains

Date: 2026-10-22. This extension uses real Google Drive and Google Calendar records. It is separate from the synthetic enumeration above.

### Question and method

Can a rule recover four known temporary records from real provider pages? Does a stop on a page with no local match cause a false absence claim?

The parent agent created four empty Drive folders and four Calendar events through connectors. These were setup actions, not browser trials. The Calendar events had no external attendees or reminders. The Drive query selected the four children of a temporary parent folder. The Calendar query selected the run marker in the primary calendar from October 1 through October 3, with explicit Toronto time offsets.

The exact queries and target IDs were frozen at 16:06:37 UTC, before the first measured call at 16:06:46 UTC. The plan allowed one chain per provider, one result per page, and at most eight pages per chain. Each returned page token was passed unchanged to the next request. The four exact-ID target filters were fixed before the page reads. Account fixtures stayed fixed during collection. Both tools returned metadata from real services. No browser page was used to divide these results.

We read each full chain once. We then applied the six fixed rules to the saved pages in local Python code. Each rule received four local target filters per provider. A local target filter selects one known fixture ID from the broader provider result. Thus there are two production traces, eight paired target cases, and 48 local rule outcomes. These are not 48 website trials. We also scored a first-page inventory baseline and made one empty-query control call per provider.

For the live extension, a checked rule requires explicit complete-coverage evidence before it makes a broad completion claim. A missing coverage field is unknown. This extends the original synthetic check, where the coverage flag was always present. We report page-chain completion, exact fixture recovery, and wider coverage as separate measures. No hidden record is assumed merely because a field is missing.

### Measured evidence

| Provider | Page order | Pages | Pages with a next token | Fixture IDs recovered | Empty control |
| --- | --- | ---: | ---: | ---: | --- |
| Google Drive | D, C, B, A | 4 | 3 | 4 of 4 | Zero items; no next token |
| Google Calendar | A, C, D, B | 4 | 3 | 4 of 4 | Zero items; no next token |

All eight measured pages contained one fixture. The final page of each chain had no continuation token. The ID unions matched the frozen manifests exactly. No duplicate ID, unexpected ID, API error, repeated token, or budget stop occurred. There were eight page calls and two control calls. Neither connector response exposed a coverage flag. Wider coverage is therefore unknown. The empty controls do not test a nonfinal empty page.

| Replayed rule | Paired target cases | Completion claims | Unknown | Claims made with a token remaining | Incorrect complete inventories | False absence claims |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Empty page | 8 | 8 | 0 | 0 | 0 | 0 |
| Short page | 8 | 8 | 0 | 0 | 0 | 0 |
| No-match page | 8 | 8 | 0 | 8 | 6 | 6 |
| Token only | 8 | 8 | 0 | 0 | 0 | 0 |
| Token and coverage | 8 | 0 | 8 | 0 | 0 | 0 |
| Two-page bounded check | 8 | 0 | 8 | 0 | 0 | 0 |

The no-match rule gave three false absence claims per provider. For example, Drive's first page contained D. A fixed local filter for A found no match on that page and stopped, although the page had a next token. The full real chain contained A on page four. This failure came from the local stop rule. It was not a provider search failure.

For the target on page one, the no-match rule found the target, then stopped on the nonmatching second page. Its matching inventory was correct, but a continuation token remained. This explains the difference between eight unsupported page-chain completion claims and six incorrect inventories. No-match replay read ten pages in total across the eight paired cases.

The first-page inventory baseline recovered one of four fixtures per provider. Full token traversal recovered four of four. The two-page bound recovered two of four and correctly reported unknown because another token remained. For the individual target cases, the bounded rule found four of eight targets. The unlimited token-and-coverage rule found all eight targets but kept the broader completion status unknown because coverage metadata was absent.

Both author scoring executions produced identical result bytes. They used Python 3.13.7 on macOS 26.7.2 arm64. Scoring used 0.000923 CPU seconds in the first run and 0.000954 CPU seconds in the repeat. This is local replay time, not provider latency. The repeat made no service calls and added no independent observations. See `live_reproduction.json`.

### Interpretation and limits

These real traces support a narrow result: a no-match stop can falsely report that a known target is absent when the provider has more pages. They also show that a bounded search can report unknown while it still has a next token. The experiment does not show that a language-model agent will follow either rule.

No nonfinal empty or short page occurred. The live empty and short rules therefore passed only the observed full-page paths; their dangerous branches were not tested. Native `incompleteSearch=true` was not observed or forced. Permission loss, secondary calendars, shared-drive scope, concurrent data changes, and expired tokens were not tested. Four fixture records do not prove complete account coverage. The paired filters reuse the same two traces, so their counts are not estimates of service or agent failure rates.

The original Google documentation supports the distinction between page limits, continuation tokens, and searched scope. It does not guarantee the outcome of this test. Current Calendar pagination and event-list references were checked on 2026-10-22. [Calendar pagination](https://developers.google.com/workspace/calendar/api/guides/pagination), [Calendar events.list](https://developers.google.com/workspace/calendar/api/v3/reference/events/list), [Drive files.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list), [AIP-158](https://google.aip.dev/158).

### Evidence, ethics, and review

`live_trace.json` contains aliases, timestamps, continuation-token hashes, and hashes of the private source records. The raw request and response bodies contain account IDs and opaque tokens. They remain private. The public trace does not contain those values. `live_analysis.py` reproduces all local scores without account access. The query freeze precedes collection; the analysis implementation was frozen after collection and before scoring. The rule definitions were fixed before collection.

Codex generated this extension and its code. Provider connectors created fixtures and read saved pages. Python replayed fixed rules. No model was called inside the replay, and no paid compute was used. No human review or peer review occurred. A separate agent checked the private evidence, public trace, all 48 rule outcomes, and all six inventory results. Its independent audit passed 166 checks. The reviewer also ran the documented scorer once and obtained identical result bytes. No material error was found. This additional local replay made no service calls. See [the separate review](review_independent.md). Cleanup was verified after scoring. The Drive parent is in Trash, and its 21-folder test scope has no active results. All 23 Calendar fixtures have exact-ID status cancelled, with no active results in the bounded primary-calendar test query. These are counts for the complete five-study run. They do not prove permanent erasure or account-wide absence. See [live_cleanup.md](live_cleanup.md) and [live_cleanup.json](live_cleanup.json). No new license is assigned.
