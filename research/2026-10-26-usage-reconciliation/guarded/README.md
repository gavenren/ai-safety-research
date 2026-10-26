# CheckedLedger production extension

This folder contains a local admission controller for the second production extension. The controller does not call a website. The operator calls the service only after a saved `dispatch: true` result. One permit must cause at most one create attempt. No automatic retry is allowed.

Read [plan.md](plan.md) for the fixed eight-case matrix. The source uses the Python standard library and SQLite. `independent_*` files come from a separate reviewer. These checks are not extra production trials.

## Operator procedure

Run each command in a fresh Python process. Preserve command arguments, start/end UTC times, stdout, stderr, and exit code privately. A nonzero exit, timeout, missing reply, or database-busy error gives no permission to write. Export after each case and after any unusual result. Preserve the private database; do not reset a ledger or reuse an old permit.

From this directory, start a ledger:

```sh
python3 controller.py init --db /tmp/usage-drive-overlap.sqlite --site drive --case overlap
```

For `unknown`, add `--capacity 1 --reservation 1`. Use a separate DB for each case/site. The scope is `site=drive`, `fixture=drive-overlap`, `counter_start=drive-overlap-A` in this example. Calendar uses `calendar` in these fields. These are safe aliases, not account IDs.

Capture each report into a JSON file. The report below is a format example, not actual evidence. Replace the time, record aliases, and evidence hashes with the observed values. P and T must come from separate reads. P0 is captured before any A record is created. The report value must equal the number of distinct known A aliases. Keep the private alias-to-ID map for audit.

```json
{"site":"drive","fixture":"drive-overlap","counter_start":"drive-overlap-A","id":"drive-overlap-P","captured_at":"2026-10-26T18:00:00.000000Z","value":1,"records":["drive-overlap-A1"],"terminal":false,"producer_stopped":false,"evidence_sha256":["REPLACE_WITH_RETAINED_RAW_SHA256"]}
```

T uses a distinct event ID, `terminal:true`, and `producer_stopped:true`. That stop is the local operator's recorded end of A creation. Use the T total and complete known A aliases. An old P is delivered unchanged after T in `late`. Exact replays reuse the full same JSON content.

```sh
python3 controller.py report --db /tmp/usage-drive-overlap.sqlite --input /tmp/report.json
```

The payload file must contain the exact intended public fields. For Drive it can contain `name`, `mimeType`, and a safe parent alias. For Calendar include summary, start, end, timezone, privacy, free/busy status, reminders, and the declared absence of guests/conference/recurrence. Do not put account addresses, private IDs, or private URLs into the public payload. Bind the private target map separately. Save one canonical payload and use it unchanged for a retry.

```sh
python3 controller.py request --db /tmp/usage-drive-overlap.sqlite --key B1 --payload /tmp/payload.json
```

Only `decision=permit` with `dispatch=true` authorizes one create. The command commits a pending unit before printing this result. Save it before the external create. Keep the returned `payload_sha256`. Requests with `pending`, `already_saved`, `payload_conflict`, `limit_refused`, or `quarantined` never create a new record. `already_saved` means historical exact-readback confirmation, not a fresh claim about later current state.

After one create, read its exact ID and all intended fields. Store the raw readback privately. Build a safe proof with the actual alias and hashes:

```json
{"status":"saved","observed_at":"2026-10-26T18:01:00.000000Z","record_alias":"drive-overlap-B1","fields_verified":true,"payload_sha256":"REPLACE_WITH_PERMIT_PAYLOAD_SHA256","evidence_sha256":["REPLACE_WITH_RETAINED_RAW_SHA256"]}
```

```sh
python3 controller.py observe --db /tmp/usage-drive-overlap.sqlite --key B1 --input /tmp/proof.json
```

Never set `fields_verified:true` without checking the exact saved record against the intended payload and private target map. The controller validates the proof's structure and binding; it cannot authenticate Google or infer truth from a hash. A failed proof keeps the pending hold.

For `unknown`, create once but withhold the saved proof from the controller. Send an unknown envelope with `status`, `observed_at`, and `evidence_sha256`. Repeat the same key, ask for another key, then reopen in another process. Send a copy of the real proof with `fields_verified:false`; it must not claim success. Then send the valid proof. Replay the exact proof and the saved key: both must book no extra unit and grant no extra permit. The raw service reply was observed by the researcher; this is a controlled missing-evidence path, not a Google outage.

For `compete`, use two subprocesses, one payload/key each, against the same DB. Start both without waiting for the first process to finish. Retain both start/end records. Exactly one may receive a permit. Dispatch only that winner. SQLite serializes the allocation transactions; this does not test simultaneous website writes.

For `invalid`, deliver valid P1 first. Then deliver: a copied report with another fixture; a changed same-ID report with value 0 and empty records; a new-ID report with boolean `value:true`. All must be rejected. The first bad report quarantines the case. For `contradiction`, deliver valid T1 then a new-ID T0 with an empty record set. The contradiction must not release additional capacity.

Export a public safe trace:

```sh
python3 controller.py export --db /tmp/usage-drive-overlap.sqlite --out /tmp/drive-overlap.json
```

## Limits

The ledger has no shared transaction with Google. It guarantees one local permit per key under its stated conditions, not exactly-once remote execution. An unused permit can cause a lasting hold. There is no automatic refund or recovery after uncertain dispatch. All writers must use the same intact ledger. Trusted field checks, stable alias-to-ID maps, truthful final reports, a fixed unit, and correct local stop evidence remain requirements. A later invalid report cannot undo a past action. No claim about Google billing, quota controls, natural error rates, or general agent reliability follows.
