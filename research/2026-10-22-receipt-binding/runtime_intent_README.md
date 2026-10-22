# Runtime intent helper

This local helper writes decision records before the parent sends a browser action. It does not call a browser or a service. A prepared record does not prove that an action was sent or saved. Its event timestamps are actual local helper times. Browser-action timestamps and saved-state results remain unset for the parent to supply from evidence.

From the workspace root:

```sh
python3 work/2026-10-22-five-live/runtime_intent.py cancel-prepare drive C1
python3 work/2026-10-22-five-live/runtime_intent.py cancel-prepare calendar C2
python3 work/2026-10-22-five-live/runtime_intent.py receipt-prepare drive K EXACT
python3 work/2026-10-22-five-live/runtime_intent.py receipt-prepare calendar B TARGET
```

Use services `drive` and `calendar`. Cancellation cases are `C1`, `C2`, `C3`, and `C4`. Receipt policies are `K` for key-only and `B` for bound. Receipt pairs are `EXACT`, `PAYLOAD`, and `TARGET`.

Cancellation output goes to `private/intent-cancel-SERVICE-CASE.json`. The helper uses the matching `CANCEL-CASE` manifest target. C1 and C3 record an OLD dispatch decision. C2 records no dispatch. C4 records a NEW dispatch decision. These are decisions, not observed browser saves. C3 explicitly records its final check before cancellation and restart. The client check is not an atomic fence at the provider.

Before a receipt command, the parent must save the first browser mutation and its independent read. The read file is:

`private/intent-first-SERVICE-RECEIPT-POLICY-PAIR-A.json`

The file must contain `{ "time": "UTC read completion timestamp", "result": rawToolResponse }`. Its time is the read time, not the first browser-action time. The raw response must have `structuredContent` from the full saved-resource read.

Three more recorded observations are required. Missing evidence makes the decision UNKNOWN:

- `private/intent-ui-SERVICE-ALIAS.json`: `{time, service, alias, url, observed_id, values, source_file}`. ALIAS includes `RECEIPT-POLICY-PAIR-A`. `source_file` is the basename of an existing separate raw UI or DOM record in `private/`. Do not use a passed flag in place of observed field values.
- `private/dispatch-first-SERVICE-ALIAS.json`: at least `{time, label}`, where label is exactly `first-SERVICE-ALIAS`. This is the actual dispatch record.
- `private/ui-first-SERVICE-ALIAS-sent.json`: `{time, role, url, state}` from the postclick observation. State and role must be nonempty strings.

For Drive, UI values must contain the actual selected-row native ID as `observed_id`, the actual `active_parent_id`, and the exact `rename_input_value`. The observed URL must identify that parent folder. For Calendar, `observed_id` must match the native ID decoded from the current event URL. UI values must contain `description: "PAYLOAD-A"`, `all_day: true`, `availability: "Free"`, and `visibility: "Private"`. The Boolean must come from the actual checkbox state.

The helper requires UTC times in this order: before-save UI, dispatch, postclick UI, independent-read completion, prepare. The span from before-save UI to prepare must be at most eight minutes. Hashes of the evidence references are stored. These are checks on recorded observations, not authentication of the observer. No time is substituted for a missing browser action.

The helper verifies the exact A target ID and PAYLOAD-A saved field. It also checks Drive folder type, parent, and not-shared state, or Calendar fixed saved fields against the baseline. Missing or different required fields cause an UNKNOWN receipt decision. Calendar saved-description comparison removes only trailing CR and LF. It does not trim spaces, parse HTML, or ignore case. Drive's omitted trashed/version fields are not claimed as checked. The UI gate and the saved-read gate must both pass.

Receipt output goes to `private/intent-receipt-SERVICE-POLICY-PAIR.json`. The immutable fields bind service, account alias, operation ID, native target, action, and suffix payload. For a changed Drive target, the rendered name keeps target B's alias prefix and requests PAYLOAD-A. The alias prefix identifies the fixture for the operator; the native target ID is the binding field. Thus a changed-target pair does not also change the canonical suffix payload.

The helper records the actual result from frozen `receipt_decision` before any second action. Every receipt outcome has `dispatch: false`. The helper never admits a second mutation. The parent must supply a later read of the intended target and, for changed-target cases, both A and B. A local success result is not itself a match with current saved state.

The helper checks the frozen `live_intent.py` hash before each case. It writes with a same-directory temporary file and atomic replacement. A case lock prevents two writers. An existing or partial case record is preserved and makes a repeated prepare command fail. Inspect the record; do not remove it to obtain a preferred result.

`check_runtime_intent.py` uses only synthetic fixtures in a temporary directory. The revised helper passed 192 conditions, including event order, all case decisions, changed target binding, exact payload checks, malformed evidence, stale evidence, missing UI source, wrong UI identity, and refusal to overwrite. These checks are not production experiments. The helper and check code were added before the parent's cancellation and receipt commands; the pure decision rules remain unchanged.

The first helper passed 150 initial checks but a separate review found that it did not enforce the first-action and read order. That version was never used for a production case. It is retained as `runtime_intent_v1_not_for_use.py`, with its original hash and check record. Do not use it. The revised gate is the required implementation. Atomic replacement makes file updates visible as a whole; no crash-durability claim is made.
