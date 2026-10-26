# Local controller commands

The controller does not access Google Drive, Google Calendar, a browser, or a network. An authorized operator must make the production writes and obtain fresh saved-record evidence. The controller saves a decision before that action. It then records the actual result and processes any remaining report.

Use Python 3.13.7 with the standard library. Run commands from the repository workspace. No random seed is used.

## Receipt file

Save one JSON file per shared A fixture. Use exactly these top-level keys:

- `site`: `drive` or `calendar`.
- `case`: `overlap`, `late`, `early`, or `duplicate`.
- `fixture`: a safe unique fixture alias, such as `calendar-overlap`.
- `counter_start`: a fixed safe counter alias, such as `CUA-USAGE-20261026-calendar-overlap`.
- `P` and `T`: report objects described below.

Each report has `id`, `captured_at`, `terminal`, `value`, `records`, and `evidence_sha256`. T also has `producer_stopped: true`. P must not have that extra field. Use separate report IDs. Use UTC ISO times. P must be captured before a separate T read, even when both counts are equal. Each evidence hash is the lowercase SHA-256 of a saved private observation file. Each list must contain at least one hash. A zero P still needs evidence of an empty exact scope.

`records` contains only safe aliases, not service IDs. Its distinct alias count must equal `value`. P's set must be a subset of T's set. Safe aliases can contain letters, digits, periods, underscores, colons, and hyphens. Keep account IDs, private URLs, and account addresses out of these files.

Illustrative structure only; the values and hashes below are not live evidence:

```json
{
  "site": "calendar",
  "case": "overlap",
  "fixture": "calendar-overlap",
  "counter_start": "CUA-USAGE-20261026-calendar-overlap",
  "P": {
    "id": "calendar-overlap-P",
    "captured_at": "2026-10-26T18:00:00Z",
    "terminal": false,
    "value": 1,
    "records": ["calendar-overlap-A1"],
    "evidence_sha256": ["0000000000000000000000000000000000000000000000000000000000000000"]
  },
  "T": {
    "id": "calendar-overlap-T",
    "captured_at": "2026-10-26T18:00:01Z",
    "terminal": true,
    "value": 1,
    "records": ["calendar-overlap-A1"],
    "evidence_sha256": ["1111111111111111111111111111111111111111111111111111111111111111"],
    "producer_stopped": true
  }
}
```

The controller constructs each report envelope from the fixed site, case, fixture, counter start, and the report object. It hashes canonical sorted JSON bytes. Repeated T delivery reuses the same envelope, ID, and hash.

## Save the decision

Use each of these exact rule names: `AddEvery`, `DedupSum`, `LastValue`, `HighWaterEarly`, `HighWaterHeld`, and `TerminalOnly`.

```sh
python3 outputs/2026-10-26-usage-reconciliation/live/controller.py prepare \
  --receipts work/2026-10-26-usage-live/calendar-overlap-receipts.json \
  --rule LastValue \
  --intended-name CUA-USAGE-20261026-calendar-overlap-LastValue-B1 \
  --state-dir work/2026-10-26-usage-live/decisions
```

The command creates `<site>-<case>-<rule>.json` exclusively. It refuses to replace an existing branch. Its output gives the absolute `state_path`, decision, available balance, and pending events. Save this result before any B action. Do not create B when `accepted` is false.

At D, `k` is the rule's local B booking. It is not proof of actual B use. `actual_b_count` remains null until readback. For the early case, the saved trace stops at D, the terminal flag is false, and `remaining_events` is `T`.

## Save the action evidence

After an admitted record is created, read its exact ID and required saved fields. Save a private evidence file and its public safe alias. Then save a JSON action evidence file with these fields:

```text
status: saved
observed_at: UTC observation time after prepare
actual_b_count: 1
b_alias: unique safe branch B alias
fields_verified: true
evidence_sha256: nonempty list of hashes of private readback evidence
```

For a refusal, do not create a record. After a complete test-scope check establishes that the branch marker is absent, save:

```text
status: absent
observed_at: UTC observation time after prepare
actual_b_count: 0
complete_scope_check: true
evidence_sha256: nonempty list of hashes of private absence evidence
```

Do not include `b_alias` for an absent record. `absent` can also describe a confirmed failed admitted write. That outcome does not pass the integration check. An uncertain write must use `status: unknown`, `actual_b_count: null`, observation time, and evidence hashes. Stop dependent writes and resolve its identity before any retry. An unknown outcome has no final score, and its pending T is not consumed. An optional `note` can record a short safe explanation; omit all private information.

## Finish the branch

```sh
python3 outputs/2026-10-26-usage-reconciliation/live/controller.py finish \
  --state work/2026-10-26-usage-live/decisions/calendar-overlap-LastValue.json \
  --evidence work/2026-10-26-usage-live/calendar-overlap-LastValue-action.json
```

The command checks that controller and plan hashes did not change after prepare. It verifies that evidence time follows prepare, records actual B use, and then consumes the tail. It writes the completed state atomically. Repeating finish with identical evidence only reads the existing result. Different evidence cannot silently replace a finished or unknown result.

Cleanup checks and the final A/B saved-state audit are separate requirements. A completed local branch file does not prove cleanup, publication, or an unrecorded external action.

## Repeat the local code checks

```sh
python3 outputs/2026-10-26-usage-reconciliation/live/check_controller.py
```

This check uses invented receipt data. It compares all four cases on both site labels against the unchanged original simulator. It also checks the early-case pause, distinct report IDs, and unknown-outcome behavior. `controller_checks.json` contains 48 check rows and 312 state comparisons. These are software checks, not production observations.

`expected_controls.json` records the independent manual expected counts from the pre-execution design review. `controller_freeze.json` records source and plan hashes before production execution. The pure functions `prepare_value`, `finish_value`, `transition`, and `report_envelope` support an independent saved-data replay.
