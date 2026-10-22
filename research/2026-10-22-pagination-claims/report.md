# A final page does not prove complete search coverage

Date: 2026-10-22, America/Toronto. Extra study requested by the repository owner.

## Abstract

An agent can stop too early on an empty page, or finish a page chain whose search scope is incomplete. We compared six stopping rules on 4,662 synthetic search worlds. The token-only rule read every page but made 3,108 unsupported completion claims and 120 false absence claims. The rule that checked both tokens and coverage made no unsupported completion claims. It completed 1,554 searches and marked 3,108 as unknown. With a two-page limit, that checked rule completed only 42 searches. The exact counts describe this finite model. The original enumeration did not test a real service or language model.


Two real provider page chains each returned four temporary records. Local replay of the no-match stop made six false absence claims in eight paired target cases. Full token traversal recovered all known fixtures. These were connector page reads and local replay, not 48 browser trials; wider coverage stayed unknown.

The sections below describe the original synthetic study. The dated production extension at the end gives the later live evidence, checks, and limits.

## Research question and safety relevance

When do page-size stopping rules or token exhaustion give unsupported completion and false absence claims?

**Pagination** divides a result list into pages. A **continuation token** identifies a further page. **Coverage** describes which parts of the requested search scope were searched. An **unsupported completion claim** says the search is complete while a token remains or an incomplete-coverage flag is set. A **false absence claim** says there are no matches when the complete world contains a match.

An agent can use a search result to decide that an object does not exist or that a cleanup is complete. Such a claim needs evidence about both the page chain and the search scope. An empty response is not always evidence of absence.

## Related work and contribution

Google AIP-158 permits pages smaller than the requested size, including empty pages, before the end. Google Drive's `files.list` reference exposes a continuation token and a separate `incompleteSearch` field. Those documented semantics motivate this model. No Drive behavior is measured here. [AIP-158](https://google.aip.dev/158) [Drive reference](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)

Petrova, Mazniak, and State study first-chunk selection and file localization in *Agents Don't Paginate*, an arXiv preprint. This note studies the evidence required to stop and claim full coverage. It does not reproduce their model results or infer universal agent behavior from their observations. [Preprint, v1](https://arxiv.org/html/2608.26130v1)

Earlier repository browser trials noted pagination limits but did not enumerate these stopping rules against incomplete-search flags. The contribution is a paired finite regression set that separates an unsupported claim from an actually incorrect inventory. The stopping mechanisms are established. The [limited search](source_search.md) does not prove novelty.

## Method

The [plan](plan.md), [configuration](config.json), and source record were frozen before implementation. The code was hashed before execution. See [freeze.json](freeze.json) and [implementation_freeze.json](implementation_freeze.json).

A page contains at most two items. Each item either matches the query or is unrelated. The six possible count pairs are `(0,0)`, `(0,1)`, `(0,2)`, `(1,0)`, `(1,1)`, and `(2,0)`. We enumerate all page streams of lengths one through four. There are 6 + 36 + 216 + 1,296 = 1,554 streams.

Each stream has three coverage modes: complete with no hidden match; incomplete with no hidden match; and incomplete with one hidden match. Thus there are 4,662 worlds and 27,972 rule outcomes. Item IDs are unique. Every nonfinal page has a truthful token. The incomplete flag is true on every page in the two incomplete modes. Other query parameters remain fixed. A hidden match is inside the requested task scope but outside the portion searched. Matching is the task's local test on listed items. Unrelated items do not imply that Drive ignored a server query.

| Rule | Stop condition | Completion condition |
| --- | --- | --- |
| Empty page | Raw page has zero items, or final token | Always claims complete |
| Short page | Raw page has fewer than two items, or final token | Always claims complete |
| No-match page | Page has no matching item, or final token | Always claims complete |
| Token only | Final token | Always claims complete |
| Token and coverage | Final token | No incomplete flag was seen |
| Bounded checked | Final token, or two pages read | No token remains and no incomplete flag was seen |

The checked rules report unknown when their completion condition fails. The oracle reads the complete synthetic world. It separately scores unsupported completion, incorrect matching-ID inventory claimed complete, and false absence. The last two require an actual missing match. A claim can be unsupported even when its returned inventory happens to be correct.

Named controls include an empty page before a match, an unrelated full page before a match, an empty final page, incomplete coverage with and without a hidden match, and a budget stop with another token. These controls are corpus members. Every rule receives every world. No case is sampled or excluded. There is no random seed, learned policy, data split, confidence interval, or population significance test.

## Results

All 27,972 outcomes were scored. There were no failed assertions or unscored cases.

| Rule | Worlds | Complete claims | Unknown | Unsupported completion | Incorrect complete inventory | False absence | Pages read, total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Empty page | 4,662 | 4,662 | 0 | 3,726 | 2,442 | 993 | 13,932 |
| Short page | 4,662 | 4,662 | 0 | 4,422 | 3,570 | 1,632 | 8,604 |
| No-match page | 4,662 | 4,662 | 0 | 4,422 | 3,570 | 2,091 | 8,604 |
| Token only | 4,662 | 4,662 | 0 | 3,108 | 1,554 | 120 | 17,730 |
| Token and coverage | 4,662 | 1,554 | 3,108 | 0 | 0 | 0 | 17,730 |
| Bounded checked | 4,662 | 42 | 4,620 | 0 | 0 | 0 | 9,306 |

For example, a complete world can have an empty first page with a token and a match on its second page. The empty, short, and no-match rules claim absence after the first page. Both unlimited token rules read the match. In a different one-page world, the final page can be empty with `incompleteSearch=true` and one hidden match. The token-only rule then falsely claims absence; the checked rules report unknown. [controls.json](controls.json)

The token-only rule has 3,108 unsupported completion claims because two of the three modes have incomplete coverage. Only the 1,554 one-hidden-match worlds give an incorrect inventory. The zero-hidden-match incomplete worlds show why a correct answer alone does not establish sufficient evidence.

The bounded checked rule completes the 6 + 36 = 42 complete-mode worlds of at most two pages. It marks the other 1,512 complete-mode worlds unknown, along with all 3,108 incomplete-mode worlds. Thus zero false claims comes with a clear loss of completion. Unknown does not mean completed or empty.

Both executions used unchanged Python 3.13.7 code on macOS 26.7.2 arm64. The first used 0.470428 CPU seconds; the repeat used 0.466033. All five deterministic files matched byte for byte. [reproduction.json](reproduction.json) records those checks. The repeat does not add independent worlds.

## Conditional argument and discussion

Under the model's assumptions, the checked unlimited rule is sufficient. The first read returns page one. If a token exists, the next read returns the next page. By induction, the rule visits every page in the finite chain before it sees a final token. An incomplete flag with value false then means the searched scope covers the world. The returned matching IDs therefore equal the truth. If the incomplete flag is true, the rule refuses to claim complete. The two-page version adds refusal when a token remains.

This argument depends on truthful metadata, fixed scope, unique IDs, and a finite stable chain. It does not establish those properties in a real service. A production agent also needs to handle failed calls, expired tokens, mutations, and query changes. Pages read is a logical work count, not measured network latency or cost.

## Limitations

This is a synthetic enumeration, not an API, browser, connected-account, or language-model test. All six page compositions and all three coverage modes have equal representation by construction. That is not a real workload distribution. Streams have at most four pages and one hidden match. The model excludes inconsistent flags, missing tokens, changing data, duplicates, token expiry, and errors. It does not test whether an agent understands or follows these rules. The exact failure counts cannot be used as provider or agent failure rates.

## Ethical and misuse considerations

All records in the original enumeration are synthetic and local. That experiment read no private account content, purchased no service, and changed no account. The main misuse risk is to treat zero finite-model errors as a general certificate, or to call unknown a completed search. External text, figures, code, and datasets are not redistributed. Sources are paraphrased and linked. No new license is assigned to the owner's work.

## AI use and review status

Codex generated the study, code, analysis, and report. Web tools checked primary sources. Python executed fixed rules. No model was called within a trial. The exact runtime model build was not exposed and is not an experimental variable. No human review or external peer review occurred. A separate agent wrote and froze an evaluator before reading the main code or results. It checked all 4,662 worlds, all 27,972 rule outcomes, the summary counts, sources, and report claims. The review found no material error after three scope clarifications. See [separate_review.md](separate_review.md). The NeurIPS checklist is a review aid, not approval or certification.

## References and reproduction

See [references.bib](references.bib), [source_search.md](source_search.md), and [README.md](README.md). [worlds.jsonl](worlds.jsonl) contains all page inputs and truth sets. [cases.jsonl](cases.jsonl) contains all outputs and scores. [summary.json](summary.json) includes separate results for each coverage mode. [checks.json](checks.json) records built-in checks.

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
