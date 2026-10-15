# Account evidence, privacy, and defects

Source: Google Drive browser UI and the connected Google Drive list-folder tool, October 15, 2026. All task names are new test tokens. No source application code is included. Google retains rights in its UI. No new license is assigned.

## Text and connector evidence

The original JSONL action logs and private connector replies remain local. Public copies replace account name, email, account handle, storage-use totals, local absolute paths, and private folder identifiers. Stable aliases preserve each block and each distinct record. One unrelated contact-hovercard URL and its query fields are removed. This change does not alter a test row, action, observation, time, receipt, or decision. Parsed JSON is serialized again. account_redaction_manifest.json records private and public hashes and byte sizes. Private inputs cannot be reconstructed from the public package. Their hashes support later comparison by the owner, not public verification of the hidden fields.

account_connector_audit.json contains exact test names, stable distinct-ID aliases, MIME type, creation time, and audit time. The connector was called only after all scored decisions and browser audits. Each request had capacity 100; the returned blocks have 8, 8, 8, and 6 records. No pagination token was returned. The later full browser lists show the same 30 names. This is a bounded service read, not indefinite storage assurance.

account_runner_B_results_original_logging_error.json and account_runner_B_results-before-correction.json are invalid historical exports. Do not use them as scored inputs. The current results, original raw logs, and explicit correction ranges are all retained. The analyzer uses the raw observations and correction record, then checks the current results. D01 also has an append-only correction in A's raw log. Neither correction changes the observed UI text.

## Image evidence

The original full screenshots contain account navigation and usage details and are kept private. Three originals, D11, D12, and D13, were overwritten by a logger error. The files named D11 depict D14. They are not evidence for D11. No missing image was reconstructed.

The public files account_block_1_audit.jpg through account_block_4_audit.jpg are later full-block audits made by the lead after the connector audit and after all trial decisions. They show 8, 8, 8, and 6 test rows. account_later_block_audits.json gives their accompanying observations and times. They do not replace the missing trial images. They do not establish an earlier filter state or decision time.

The browser screenshot API captured the rectangle x=260, y=70, width=1190, height=550 from a 1512 by 827 viewport. This removes the account header and side navigation. It retains the block name, filters, and every test row. No pixel inside that rectangle was changed. The five image files, including account_cleanup.jpg, use the tool's original JPEG bytes.

## Errors and limits

D02 and D06 did not save a usable pre-write list or empty-result message. Their absence baselines are unknown. D16 and D18 each had a failed read during the later audit, followed by a successful ready-state read. No retry write occurred. All deviations and errors remain in the trial evidence. The interpretation must not turn missing evidence into a successful check.

The cleanup action moved only the temporary test parent to Trash. The public cleanup state and image show the named folder under Trash. The immediate post-action My Drive page contained unrelated rows; only its exact success receipt is published in account_cleanup.json. The full page is local private evidence. Trash was not emptied.
