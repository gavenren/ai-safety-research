# Independent review of the guarded usage extension

Date: 2026-10-26. Reviewer: a separate Codex agent. No human review or external peer review occurred.

## Decision and scope

Pass for publication of the stated accounting results and the recorded field-proof failure. This is not a declaration that every original integration check passed. The accounting and write-allocation checks passed. Seven initial Calendar completion outputs lacked one required field check. The report states that failure and preserves the initial traces.

The supported claim is narrow: the retained local rules and decisions produced the selected saved-record counts without a duplicate allocation or a count above the declared case limit. The experiment does not establish a native Google quota, a natural failure rate, or a general agent-safety guarantee. Remote publication needs its own later check.

## Separation and pre-live checks

The reviewer first read the prior paper and live plan. It received only the new written contract and eight-case matrix from the design agent. The reviewer wrote a mathematical set-based accounting specification and froze expected case results at 18:20:52 UTC, before reading the new controller or results. The source and expected-data hashes are in [independent_expected_freeze.json](independent_expected_freeze.json).

The reviewer then read the controller and ran [independent_probe.py](independent_probe.py). All 70 offline assertions passed. These include 12 rounds with two separate SQLite connections competing for one remaining unit. Each round gave one permit. The probe also checks overlapping cumulative values, report replay, old progress, invalid scope and values, conflicting final reports, intent replay, pending holds, incorrect fields, incorrect payloads, and reuse of a saved-record alias. These are offline checks, not more production cases.

The checked controller source has SHA256 `46d454c624e1dfb347015a9f786b4f86d15d5b6dfa9c686b8e3e9a53f6406a82`. No controller correction was required by the pre-live review. The plan and controller were frozen at 18:23:45 UTC, before the first account write.

The source keeps the balance read, limit check, and intent allocation in one `BEGIN IMMEDIATE` transaction. A permit result is returned only after commit. The reviewer checked the official [SQLite transaction](https://www.sqlite.org/lang_transaction.html) and [isolation](https://www.sqlite.org/isolation.html) documentation. This use of a transaction does not create one atomic transaction with Google.

## Independent trace comparison

[check_independent.py](check_independent.py) imports no controller code. It derives booked A use from sets of accepted cumulative reports and derives B use from distinct allocated intent keys. It compares every saved before/after balance, result decision, final operation map, and final case state. Its final expected vectors were frozen before source access. The checker itself was written after source review; it is not represented as a second blind implementation.

The final comparison passed all **16 cases, 87 non-initial events, and 190 initial/before/after state records**. There are 103 log entries when the 16 initialization entries are included. These are checks of the same cases, not additional trials. The result and exact trace hashes are in [independent_live_checks.json](independent_live_checks.json).

The final records match the independent case vectors: 18 A records and eight B records, no case above its declared count limit, and no repeated intent granted a new permit. There are 33 requests and eight permits. Twelve requests were refused for capacity, four for quarantine, and two for a changed payload. Seven repeated keys received no permit. The 14 terminal cases have exact final A booking. The two invalid-report cases retain their reservations and do not establish final settlement.

The two saved-data analysis runs agree byte for byte on their row, request, and summary files. The analysis status is deliberately limited to accounting. A true `fields_verified` input is not independently established by the ledger.

## Private evidence and cleanup

The reviewer read the raw connector receipts, browser observations, private alias maps, command records, and cleanup evidence. The creation/trace/privacy audit passed 860 assertions in its saved run. It checks the 26 distinct provider IDs, complete known A/B sets, creation after the freeze, B dispatch after the durable permit, supported saved fields, case limits, raw evidence hashes, and absence of known private IDs and account addresses from the public files then present.

A separate 92-assertion check verifies the later named-zone evidence for all 13 Calendar events. Each browser URL identifies the exact event. Both start and end zone controls name Toronto. Some retained snapshots show only the modal zone dialog; the connector supplies the other checked event fields. The displayed current GMT offset in the zone label is not used to infer the November event offset or the IANA zone.

A separate 160-assertion cleanup/scope check passed. The exact Drive parent and all 13 child URLs have Folder Path evidence through Trash and the test parent. An empty active-marker search provides an additional bounded check. This is not an observed API `trashed=true` field. One initial child path had not finished loading; the later full path was checked without repeating a mutation. All 13 Calendar IDs return `cancelled` after their deletion calls. The bounded active query is empty and has no next-page token. The pre-cleanup record sets match all known IDs. No Trash purge occurred. These checks concern only the temporary test records.

One first Calendar A event included the account owner as an attendee despite an empty requested attendee list. The same exact ID was corrected before the P/T observations. No other attendee was present. This was one extra field update, not an extra record creation. The initial failed check and correction remain in the evidence.

## Negative field-proof result and repair

The four initial Calendar B proofs asserted full field verification, but their connector views lacked the saved IANA zone. Those four saved outputs and three later repeated completion outputs were unsupported for the full intended field set at their original times. This is **seven outputs on four records**, not seven different records or seven proven incorrect saved zones.

Later exact-ID editor observations verify the named Toronto zone on all 13 events. They support later complete proofs for the four B records. They cannot make the original incomplete proofs complete retroactively. The controller retains the historical first confirmation; later accepted proof replays do not add another allocation or another count.

The separate Calendar adapter now requires named-zone evidence and explicit presence of every required returned field. The reviewer identified a missing-key check: using `fields.get` alone could accept an absent field when its intended value was null. The corrected adapter adds presence checks and omission controls. The source revisions and timing are recorded. The actual saved extracts already contained those fields, so this correction does not change the measured record counts.

All 28 adapter replay checks passed: seven checks for each of the four B records. They cover missing zone evidence, unverified zone evidence, an incorrect zone label, an incorrect start time, missing recurrence, missing Meet information, and a complete matching proof. These are saved-data checks of a repair, not a new prospective account trial. The original field-proof failure remains a negative result.

## Limits and publication checks

All writers must use the same intact ledger, and each permit must be used at most once. One saved record must have the declared one-unit cost. Truthful source totals, a stopped A producer, a faithful alias-to-ID map, and correct saved-field observations remain assumptions. Evidence hashes bind retained files; they do not authenticate provider state. The ledger cannot detect a false but well-formed field assertion. A saved intent denotes historical completion, not a fresh guarantee about current fields. A process restart is not a crash or power-failure test. A pending hold or quarantine can refuse useful work indefinitely.

The report distinguishes the original simulation, the earlier production comparison, this new 16-case test, offline checks, and later adapter replay. It does not claim a new accounting mechanism or infer population rates from selected cases. It states AI roles and the absence of human and peer review. The new source uses are primary documentation and are bounded to the read sections.

Relevant NeurIPS checklist topics were used as a review aid: claim support, conditions, method, repeat instructions, negative results, limits, rights, and private data. No new license or third-party code is assigned or copied. The public material contains safe aliases and result extracts. Raw account IDs, addresses, private URLs, and process logs remain private. No harmful operational detail is introduced. The reviewer found no remaining material error in the stated report after the recorded corrections. Publication still requires the root agent to compare the checked files with the remote commit.
