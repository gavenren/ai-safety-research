# Independent review of the production record extension

Date: 2026-10-26. Reviewer: a separate Codex agent. No human review occurred.

## Decision

Pass for the stated, limited claim: the six local rules produced the recorded decisions, and the permitted writes produced the recorded temporary records. The private evidence supports the saved-field and cleanup statements. This review does not establish general production safety, Google billing correctness, or a natural failure rate. Remote publication still needs a separate check.

## Separation and method

The reviewer read the written plan and original report. The reviewer then wrote a prefix-based specification without reading the live controller or results. The source and expected calculations were frozen at 17:54:49 UTC. The controller freeze was later, at 17:55:42 UTC. The reviewer read the controller and production evidence only after that independent freeze.

The independent specification derives each state from the full received-report prefix. It does not import the controller or copy its state-transition loop. The exact source hash is in [independent_expected_freeze.json](independent_expected_freeze.json). Its expected rows are planned calculations, not website observations.

[check_independent.py](check_independent.py) compares the public branch records with that specification. [independent_live_checks.json](independent_live_checks.json) records the result. All 48 decisions, 156 transitions, and 312 saved before/after states match. The initial and final states and all reported result measures also match. These comparisons are checks of the same 48 branches, not extra trials.

## Private evidence audit

The reviewer also read the retained connector replies, action records, browser text, and record-ID maps. A separate read-only audit checked the following:

- All eight fixtures have distinct P and T identities, ordered capture times, and the declared record counts. The four zero-count P captures precede their later A creations.
- All 12 A creations follow the plan/controller freeze and precede T. Shared A records retain the checked fields before branch use and before cleanup.
- Every permitted B has one distinct saved ID. Calendar create requests start after the saved D decision. Drive server creation times occur after D and before the saved readback. The Drive browser dispatch start was not logged separately.
- All 22 permitted B records have exact-ID saved-field evidence. The 26 refused branch markers are absent from the observed test scopes and have no B record in the action ledger.
- The early-release branches consume T in the finish phase after action readback. Repeated T copies use the same report hash and ID.
- The complete known pre-cleanup record sets contain 17 Drive children and 17 Calendar events. They contain six A records and 11 B records per service. The Drive parent is a separate setup record.
- All 17 Calendar IDs return cancelled after cleanup. The bounded active-marker query is empty and has no next-page token.
- Each of the 17 Drive child URLs has retained browser evidence of the path through Trash and the test parent. The parent also has a Trash path. The active test-marker query is empty.

The private audit has 2,810 assertions and no unresolved failure. The public extracts were compared with their retained source hashes, and each published branch equals its private branch record. A scan found no known private record ID, account address, or private record URL in the live package. A hash binds an extract to a retained file; it does not independently prove provider state to an outside reader.

## Results and claim checks

The two sites give matching rule outcomes. The observed B count is 22. Four branches have scoped excess: two LastValue branches and two HighWaterEarly branches. There are 10 final overcounts, two final undercounts, and six feasible refusals after T. These measures overlap and are not one combined failure count.

The report and index state eight shared fixtures and 48 paired decisions. They distinguish 11 Drive browser B creations from 17 Calendar connector creations and six Drive connector A creations. The declared capacity, report envelopes, delivery order, and producer stop are local test controls. The report does not claim that Google issued or enforced them.

The original simulation remains a separate result. The extension gives execution evidence for selected counterexamples; it does not introduce a new accounting mechanism. AI roles and the absence of human or peer review are stated.

## Limits and recovered checks

The reviewer audited saved evidence and did not repeat production writes. All evidence is from one owner account per service and a selected, shared-fixture design. It does not support an independent sample size of 48.

Drive metadata omitted the requested `trashed` field. Cleanup is supported by exact-ID browser paths and active-scope absence, not an API `trashed=true` observation. An initial late-A1 browser capture had no complete path; the retained later full capture supplies that evidence. The audit required the Folder Path region, so a sidebar Trash label alone could not pass.

The Drive connector omitted the provider completeness flag and page-token field. The observed parent scope matches every known created ID. This does not prove absence outside the declared test scope. Drive creation-order checks use server creation times and local decision times, and thus assume the recorded clocks can be compared. The report states these limits.

The relevant NeurIPS checklist topics are covered: bounded claims, assumptions, method, repeatable calculations, limits, rights, private data, and actual review status. The checklist is a review aid, not conference approval or certification.

## Repeat the public calculation check

From the `live` directory, run:

```sh
python3 independent_expected.py --out /tmp/usage-expected.json
cmp independent_expected.json /tmp/usage-expected.json
python3 check_independent.py --out /tmp/usage-independent-checks.json
cmp independent_live_checks.json /tmp/usage-independent-checks.json
```

These commands use the Python standard library and make no network call. They do not repeat the account actions. The private raw-evidence audit requires the retained account evidence and is not an access path for public readers.
