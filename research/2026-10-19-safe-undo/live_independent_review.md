# Independent review of the live extension

Date: October 19, 2026. Review status: the stated saved-state results and bounded cleanup findings pass. Calendar trial 23 has an unresolved browser form. This review does not claim that all browser state is clean.

## Independence and scope

A separate Codex agent wrote the reference replay and six rule checks from the frozen plan before reading the main implementation or results. The first 18 rule/control checks ran before the first valid trial was inspected. The reviewer later read the main analysis to compare its output fields. The independent program does not import the rule driver or primary analysis.

The reference omits the agent action and replays the prescribed later commands from (0,0). The program checks the recorded rule output and grades the actual final saved fields. It does not force a saved result to equal the intended rule output. Unknown records remain unscored. No native field counter, atomic update, or trusted provider operation history is inferred.

## Results checked

All 52 assigned terminal rows are present. Of 48 core assignments, 43 have valid results and five are unknown. All four diagnostic assignments have valid results. The independent and primary programs agree on all 52 rows and 494 count or state checks. The comparison includes planned, valid and unscored counts by site and rule.

The 43 valid core results contain 26 clean completions, 11 false confirmations, four unresolved abstentions, and two abstentions with the correct saved state. All 43 observed final field vectors equal the rule decisions. The wrong completions therefore remain wrong even though the selected fields were saved as intended. These are selected cases, not a population estimate.

The independent program passed 18 rule/control checks and rejected 15 malformed copies of one retained trial. It also passed controls that preserve an unexpected final state and leave an unknown record unscored. The original trial was not changed. See [live_independent_self_checks.json](live_independent_self_checks.json), [live_independent_results.json](live_independent_results.json), and [live_comparison.json](live_comparison.json).

## Source and extraction checks

The source audit checked 234 saved-phase links and 52 terminal cleanup links. It compared raw values, record identity, marker, time, field contract, and source observations. Calendar Description is checked through the recorded visible-field text read because the accessibility snapshot omits that content. Notion X and Y can also be checked in the native source snapshot. The source review accepts both documented Private text forms in Calendar.

The extraction audit checked all 7,680 original raw-line hashes: 2,387 Calendar rows and 5,293 Notion rows. It checked 234 saved phases and 3,313 structured fields. It checked the original and final terminal file hashes and compared the public cleanup summaries with their source fields. The audit found no matches for 51 known private record identifiers or two private account-name terms in the trial, evidence and cleanup exports. It also checked for email addresses and private account URLs. This bounded check does not claim a universal privacy proof.

The early Calendar UC identifiers overlap across preflight and scored work. Source review uses trial context. The public data also retains original one-based line numbers and hashes. Calendar trial 05 was reconstructed from complete preserved phase, decision and cleanup records after a tool timeout. Its recovery_note is retained. No action or trial was repeated to supply the missing terminal row.

See [live_source_review.json](live_source_review.json) and [live_extraction_review.json](live_extraction_review.json). The full private native snapshots and images remain local. Public replay can check the extracted results, but it cannot independently reconstruct private account history. The private-source audit scripts require those local records.

## Cleanup findings and remaining limit

The cleanup audit checked 49 known saved trial Delete or Move to Trash actions against the exact temporary marker. It checked seven ready Calendar searches with exact markers and the October 1–31 date range. These include the five unknown assignments, the complete run prefix and the preflight marker. The final views show no active saved record for those markers. Both preflight records and the Notion parent were also removed through recoverable deletion.

Five later Calendar cleanup findings are retained separately from the original rows. The only extra identity recovery is Calendar 14, whose known native identity is supported by UCN-00150. Calendar 23 adds a browser-draft status. No baseline, agent state, later state, final state, decision, or scored status changed.

Calendar 02 originally showed a no-events heading while it still said Searching for the marker. That view was not accepted as final proof. A fresh ready search supplies the final finding. Calendar 14 first had a stale zero claim; UCN-00145 withdrew it, and later ready views support active absence. The original failed claims remain in the log.

The Notion parent was created in Private, as shown in NU-00014. The first parent deletion had not completed its confirmation. NU-06064 records this problem. The image label parent-trash-receipt is not proof of deletion. The final native parent view NU-06089 and the inspected parent-trash-verified image show the Trash banner and Restore page control. NU-06092 records closure of the runner tab.

Calendar 23 is different from a proved non-creation. Its creation-save call was uncertain. The final exact-marker search found no saved event. Two attempts to close the old form timed out. A possible unsaved form remains. Its status is no_saved_record_found, and its undo result stays unknown. The audit does not infer that this form was closed or that no save was ever sent. No Trash was emptied. Calendar's full Trash inventory was not inspected.

See [live_cleanup_review.json](live_cleanup_review.json) and [live_cleanup.json](live_cleanup.json). The saved-record cleanup checks pass within these limits. They do not establish complete browser cleanup.

## Review changes and disclosure

The [audit change record](live_independent_changes.md) states adapter corrections and failed checks. None changes a rule, reference target or scored outcome. The review supports the report's limited sequential-case claims. It does not establish race safety, autonomous rule discovery, a native Undo service, a production error rate, or broad novelty.

Codex generated this independent audit and review. Agent review is not human review or external peer review. Remote publication verification is a separate task.
