# Runner B evidence

All 16 assignments T17-T32 were attempted in order. The runner used two Chrome tabs and the saved trial plan. No connector was used during decisions. No data was removed. The lead must audit and clean up the test parent.

`actions.jsonl` holds the raw states, actions, times, decisions, images, and appended notes. `results.json` holds the 16 original decisions. `runner_summary.json` holds the final browser counts and evidence defects. Connector counts are pending.

## Defects and limits

T29 did not create a folder. New folder did not open its dialog. Fill and Create requests failed with no matching element. The rule then saw zero and no success receipt. It stopped unresolved. No repair write or replacement trial was made. Its t0 is the failed Create request time, not a successful click.

Offline review found an unexpected Storage view in T29 and T30 records. The cause is unknown. Records 361, 362, 363, 367, 376, 379, 380, and 382 contain private unrelated storage content in state or before_state. Redact the entire unrelated list and storage figures before publication. Preserve the event as STORAGE_VIEW. T30 resumed only after the exact assigned block path, empty exact-token baseline, and All filter were verified. No further navigation event occurred.

T24, T27, and T31 images taken after the decision show a later observer update. T24 and T27 earlier observer text had zero, while their images show one. T31 earlier final observer text had one, while its image shows two. Do not change the decisions from these images. T31 is a false confirmation if the connector audit finds two records.

The first T17 dialog actions have phase initial_create. Only the click with args.role button and args.name Create is the submit request. A raw appended note defines this correction.

All 32 images use the planned 1190 by 620 crop. They show the current trial state and filter. A bottom row for an older test can be partly cut when the block has ten records. The current trial rows remain in view. Full text holds all test rows. No full private screenshot was needed.
