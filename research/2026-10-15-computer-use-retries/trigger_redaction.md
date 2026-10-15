# Evidence and privacy notes

The trial data come from a new private Google Drive test collection. The test names are synthetic. The user authorized this test and recoverable cleanup. No existing user record was used as a test.

## Text records

The public copies retain full task observations, exact test names, filters, status messages, action arguments, UTC times, errors, and decision records. Stable aliases replace private folder and record IDs. The process also removes the account name, email, handle, storage totals, local workspace path, and contact-hovercard URL. It parses JSON and writes it again. It does not alter a count, trial label, time, action, or correction. An unexpected Storage page in T29/T30 exposed unrelated file rows in private snapshots. Those complete snapshot fields are replaced with an explicit wrong-page Storage placeholder. Their record positions, timestamps, actions, and errors remain. A private check verifies that these snapshots contain no exact T29 success receipt. No zero count is inferred from a redacted writer view. The original local files remain unchanged. The redaction manifest lists private-source and public-copy hashes. Public readers cannot use these hashes to read the private originals.

The preflight JSONL used a fixed P01 identifier for part of the session. P02/P03 phase names and exact visible tokens identify the later cases. The old phase name after_24_reloaded refers to a 17.099-second check. The preflight note explains this error and the valid later P03 check. Scored logs use explicit trial identities. Any metadata correction is an additional record; the original record is retained.

The later connector audit uses unique aliases for distinct record IDs. This preserves the count of service records without releasing live private folder links. The audit is read-only and follows all trial decisions. A failed early preflight connector call is preserved separately. No connector data were supplied to the runners during scored decisions.

## Images

Trial images are direct browser screenshots of the planned content area. They are not generated or reconstructed. The clipped region excludes account controls, storage usage, and unrelated navigation. It keeps the test parent, block name, filter controls, and list or empty-view message. A small owner initial and the word me can remain. Google Drive retains the rights to its interface artwork. The images provide attributed evidence; no new license is assigned to that material.

A decision image is captured after the decision record. The page can change between those times. Therefore, the image supports the visible state at its capture time, not necessarily the earlier observation used for the decision. The raw observation and its UTC time are the primary decision evidence. T04, T24, and T27 first observer reads were zero, while their later images show a folder. T31 confirmed from one text row, but its later decision image shows two. T10 has a blank main area in its later image; it is unknown, not evidence of zero. This difference must not be removed or hidden.

An audit image is captured after the observer is put in All and reloaded. It cannot change the earlier decision. The two example images in the report are exact copies of T18's later decision-view and audit images. The browser returns JPEG bytes, although the original filenames end in .png. The archive preserves those original filenames and bytes. Use a viewer that detects the format from the bytes. The image manifest records names, detected format, and hashes. The independent image review checks required rows, filters, visible private information, and any image/observation difference.

## Limits

The logs are agent-written action records with copied browser observations. They are not a separate capture of every model instruction or tool-call payload. Instruction separation is not secure isolation. A finite browser or connector audit cannot prove permanent durability or closure of a pending action. The evidence supports this selected set only.

Cleanup moves the dedicated parent to Trash. It does not empty Trash or permanently delete data. The cleanup record and image provide the final observed state.
