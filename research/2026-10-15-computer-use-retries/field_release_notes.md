# Release check notes

The first release validator assumed that the independent review stored its unresolved findings as a count. The receipt uses a list. The validator now requires the list to be empty. Its next run required a PDF build-script hash that the builder does not emit. The release record now includes the hash of the unchanged script used for both verified builds. Neither correction changed trial evidence, analysis, report text, or PDF bytes. The final release validator must pass before upload.

The final font check is an extract of the separate visual review. It is not a second review. The review receipt binds the report, PDF, code, and evidence; the package manifest also covers the later release records. Remote publication requires a separate Git tree comparison.

The remote-blob check found one extra trailing newline in the saved root index source copy. The live connector read and the remote blob hash support removal of that one byte. The updated index now preserves the original trailing newlines and changes only the existing paper row. The earlier local copy remains private. The paper and trial files were unaffected.
