# Independent audit changes

The first independent rule and reference implementation preceded review of the primary code and live results. Its 18 rule/control checks passed. Later changes handled recorded evidence formats and explicit cleanup limits. Original intermediate versions and failed receipts remain local.

- The observation adapter added Notion checkbox objects and public record aliases. The rule and reference logic did not change.
- The audit now rejects a recorded decision outside the allowed state domain and reports a decision that differs from the frozen rule. It still grades the actual saved state. Fifteen malformed record copies are rejected.
- The first source adapter expected Calendar decision data under decision, but the log uses output. It also expected only one Private text form. Both observed forms are now accepted. The original failed source receipt is retained.
- The first extraction adapter expected type for every event. Notion uses kind. The corrected adapter retains all raw lines and checks their hashes.
- One exploratory read used a JSONL parser on a formatted JSON receipt and failed. It changed no file.
- The comparison adapter added explicit planned and unscored counts when those fields were added to the primary output. No classification changed.
- The final source audit checks cleanup for unknown records as well as valid records. It requires a ready exact-marker Calendar search. Calendar 02 failed this check on its earlier view because the page still said Searching for. A later ready view supplies the final evidence.
- The cleanup audit checks the original versus final Calendar rows. It permits the documented identity recovery for trial 14 and the unresolved browser-form status for trial 23. All scored fields stay unchanged. The new no_saved_record_found label describes uncertainty about saved-record creation; it does not change an undo score.
- The Notion parent cleanup uses the final confirmed Trash view. An earlier image label was premature because its confirmation was not complete. Both records remain in the private evidence.
- The first complete public extraction omitted Calendar 05 recovery_note by selecting an unused reconstruction key. Review found the omission. The corrected extraction retains recovery_note, and all final receipts were rerun against it.
- The final extraction audit also checks public cleanup summaries and their source hashes. Private account-name literals were removed from the audit code; the check reads its terms from a private local file.

The main analysis was read only after the independent rule model and evidence checks were written. The primary name abstain_correct maps to the independent name correct_state_abstention. This is an output-name mapping only.
