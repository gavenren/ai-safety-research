# Evidence map and limits

The private audit compares exact native IDs before it writes aliases. Public `A` and `B` are local to each case. All 16 fixtures have distinct native IDs. The source filename and SHA-256 are recorded for each relevant original file. No raw file is changed by the extraction.

| Raw file pattern | Role |
|---|---|
| `manifest.json` | Expected native identity, setup fields, and provider URL |
| `baselines.json` | One full connector setup batch for all fixtures |
| `intent-ui-SERVICE-ALIAS.json` | Actual before-Save UI values, native identity, and source reference |
| `intent-source-drive-ALIAS.json` | Actual row data-id, baseline name, active parent URL, and filled rename value |
| `ui-first-calendar-ALIAS-filled.json` | Calendar title and all-day, Free, Private flags before Save |
| `dispatch-first-SERVICE-ALIAS.json` | Recorded first browser dispatch and requested field |
| `ui-first-SERVICE-ALIAS-sent.json` | Postclick UI observation; not by itself saved-state proof |
| `intent-first-SERVICE-ALIAS.json` | Independent saved-field read before the local second decision |
| `intent-receipt-SERVICE-POLICY-PAIR.json` | Actual online local decision and complete original envelopes |
| `receipt-after-SERVICE-ALIAS.json` | Independent saved-field read after that decision |

Changed-target cases retain first and final reads for B as well as A. Their B records stay equal to the setup baseline. A's available fields stay unchanged from first read to final read. Calendar description comparison trims only trailing actual CR/LF. Drive compares full names under the fixed fixture prefix.

The raw preparation records have `after_read: null` and `second_browser_action_time: null`. They were saved before later audits. The extractor does not fill those fields or infer that a later audit is absent. It uses the separate `receipt-after-*` files. No second browser action occurred in these cases.

The Drive K EXACT first-read file is byte-identical to `receipt-interruption-read.json`. The copy identifies the case; it does not add a read. The action and saved field are known. The exact failed-reload start time is absent, so the 30-second uncertainty limit is unknown for that case. Its 252.474-second case interval is below eight minutes.

The browser checked each Calendar baseline description through actual DOM text before Save. The retained before-Save intent record contains the new description, not a separate copy of the old DOM text. The helper's BASE check, older connector baseline, and unchanged fixed UI fields support the action contract; this is not a claim that the old DOM text was independently serialized twice.

Public hashes of original envelopes cover their private native IDs and evidence. They are not hashes of alias-substituted envelopes. Raw comparison checks and the public analysis have separate roles. A hash proves consistency with a retained byte sequence; it does not prove that a provider committed a change.

Drive `trashed` and `version` were not exposed by the connector. Calendar full conference data, provider version/ETag, and a calendar-container attestation were not exposed. The before-Save browser view supplies active parent and all-day evidence where applicable. Full metadata at each case start was not collected: the setup batch was 27–33 minutes earlier. All available collateral fields were compared across retained reads.
