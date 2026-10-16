# Change and failure record

## Before scored execution

The design review found that stale service values or incomplete coverage could leave a MISMATCH verdict. The checker now returns UNKNOWN when a required evidence gate fails. A regression test checks that such evidence cannot authorize repair.

The final root review found that an empty UI or service identity string was a known mismatch. Empty identities now return UNKNOWN. A test covers first, UI, and service IDs. The first local freeze manifest was replaced before either runner received permission to start. The final manifest alone defines scored execution.

Two author commands used an incorrect working-directory prefix while writing code. They failed before edits and before browser execution. Corrected commands succeeded. All 24 checker tests passed. These are author tooling errors, not trial outcomes. Preflight UI failures are recorded in field_preflight.md and original evidence.

## After freeze

The frozen plan, assignment file, contract, and checker remain unchanged. The browser helpers and analysis parsers are separate, unfrozen adapters. Their changes below do not replace the original evidence.

### Live helper and evidence issues

- Early Calendar helper and Recurrence parser errors were fixed before their next scored verdict. No Create was repeated because of those errors. Original failed records and the earlier adapter remain.
- N01 did not expose its assigned checkbox error. One Create was admitted, but no native record was observed. The runner stopped unresolved. Its early logger retained the baseline phase and omitted elapsed time. NF-00033 records a correction from original timestamps: 28.887 seconds. The raw decision remains unchanged.
- One N01 image was routed to the old preflight directory. NFP-00163 was appended after freeze. The first 162 Notion preflight records still have SHA-256 d1eae48d3c8e32d8cea9584d2749b78f461219622d6080470a9ff6cf6803c43a, which is the frozen hash. The appended image is scored-run evidence, not preflight evidence.
- C01's final native-identity record FCCAL-00098 cites FCCAL-00096, whose URL still shows search. A later native snapshot, FCCAL-00101, records the same event URL before the final decision. The reference defect is retained.
- N02 has failed read/navigation attempts that opened an icon menu. The later visible row context menu, Copy link action, receipt, and clipboard value establish identity. The logged errors remain. This is a read-path change, not a new write.
- C03 and N03 have failed reads during loading. Fresh reads supplied later evidence. No mutation was repeated because of these failures.
- N04 decision NF-00475 omits field_check_record_id. Its packet and preceding NF-00474 support the outcome. The decision is not edited. Later decisions include the key.
- N04's first cleanup image is labeled zero but still shows an active row. After one Trash action, later page reads show Trash and the parent becomes empty. No second Trash action was sent. Image labels are not count evidence.
- C07's wrong end date produced two visible Calendar day rows. Both rendered data-eventid values identify the same event. The adapter was extended to keep visible rows separate from distinct record identities. Its broad token click and old plural-heading extraction errors remain. The frozen count contract concerns distinct operation identities. The row-ID source and connector query supply that count; the heading alone does not. C11 uses the same evidence method.

### Live checking and offline checking

Calendar calls the frozen Python checker during the live procedure. The Notion helper records agent-assigned field judgments and constant gate flags; it does not enforce the gates by itself. The main and independent analyses derive values and gate status from the cited native sources. The frozen instructions require recorded field statuses before correction, but do not require automatic enforcement by the helper. The paper states this implementation difference. It does not call the Notion helper an automatic controller.

### Analysis development corrections

The main analyzer was written after the live plan freeze. During development, it was corrected to preserve an absent first identity, recognize explicit cleanup source keys, distinguish a normal empty-table disabled select-all checkbox from loading, and include the required Calendar query scope. It also learned to count distinct event IDs when one multi-day event has two rows. The raw heading remains in the output.

The initial title-only baseline parser read Notion's Name header as a data title. A later draft substituted an empty string when N01 had no saved title. Both issues were corrected before release. N01's baseline is UNKNOWN under the frozen function. Tests now check both cases. The live decisions were not changed.

The independent parser initially required native Description innerHTML and innerText to agree. The frozen contract uses visible innerText, so that extra guard was removed. C05's visible newline is a supported wrong value. Raw innerHTML remains diagnostic evidence. The final review compares each field status, not just overall results.

Fifteen main parser tests use saved source records with controlled offline changes. They cover missing and stale fields, missing identity and DOM references, wrong query bounds, incomplete row-identity mapping, an extra blank row, missing title, and rejection of a live success label when the raw value is wrong. These are code checks, not additional live trials. Code formatting was changed with an abstract-syntax-tree equality check. No frozen file was formatted or changed.

### Public extraction review

The independent privacy comparison found that 33 intermediate Notion snapshots lost an outside-task loading marker when no task token was present after the banner. The extractor was corrected to retain that marker anywhere in the source. The original source hashes remain unchanged. The scored outcomes did not depend on those snapshots. The full public extraction and both analyses were repeated after this fix.

A second extraction check found that a schema type named `str` had entered the identity alias map. Global substitution damaged helper code in the public adapter archive. Identity discovery now accepts only an identity-shaped value in the designated keys. The raw helpers were unchanged. The public data and code archive were regenerated. The final review checks source transformations and adapter syntax. These two extraction defects changed no live action or result.
