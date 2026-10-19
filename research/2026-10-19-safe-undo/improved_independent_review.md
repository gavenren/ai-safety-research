# Independent review of the improved undo extension

Status: PASS for the stated scope. Date: October 19, 2026.

The frozen input manifest is `aa8a01119e48c503a7b2e396f8b677ba7ce4e0feb91e93b415fb94fd027d30ac`. All six frozen input hashes match. No assignment, rule, reference target or outcome definition changed after the freeze.

## Separate model and evidence checks

The reviewer inspected the controller during the design review. The reviewer then wrote a separate Python rule and outcome model without importing the controller or reading the primary analyzer. That model passed 30 local controls. The reviewer later read the primary analyzer to map result fields for exact comparison. The model did not change. This is a separate Codex agent check. No human review occurred.

The final checks passed:

- [Outcome audit](improved_independent_results.json): all 32 assignments are retained; 30 are valid and two are unknown.
- [Result comparison](improved_independent_comparison.json): 427 checks match the primary results, including each trial, denominators, site and rule counts, pairs and hypothesis measures.
- [Native source review](improved_source_review.json): 186 saved-field links, 60 final reload actions, 60 controller calls, 30 history seals and 30 undo dispatch checks.
- [Extraction review](improved_extraction_review.json): 15,847 field and hash checks cover 32 terminal rows and 6,409 source lines. Exact controller inputs, outputs, saved fields, literal fault instructions and cleanup extracts match their private sources.
- [Cleanup review](improved_cleanup_review.json): all 32 new saved trial records and the new Notion parent have removal evidence. Both final site summaries pass. Browser limits remain as stated below.

The source review checks the native record identity and field contract. It checks the deliberate later writes, their saved values and the seal time. The incomplete-history case retains both hidden set0,set1 writes. The prestate-mismatch case retains the add1 after the seal. The public controller input has no evaluator reference target. Two final reads are separate logged reloads. Wrong saved fields remain scored outcomes.

## Results and interpretation

| Rule | Assigned | Valid | Clean completion | False confirmation | Correct state with refusal | Unresolved | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 16 | 15 | 9 | 6 | 0 | 0 | 1 |
| Checked history | 16 | 15 | 7 | 0 | 2 | 6 | 1 |

Calendar05 and Calendar13 remain unknown. Cleanup does not change either outcome. Fourteen of 16 site/scenario pairs have valid results for both rules. All eight deliberately faulty actuator writes were observed as injected. They are controlled browser writes, not provider faults.

H1 has no counterexample in the 15 valid checked-rule cases. H2 passes in all seven valid positive controls. One of eight planned positive controls is unknown, so planned coverage is incomplete. H3 has four observed refusals before an undo write. H4 has four refusals after deliberately wrong saved fields. H5 has six baseline false confirmations in the incomplete-history and wrong-save cases. These results concern the selected cases only. They are not population rates.

The checked rule prevents some completion claims. It does not repair the wrong saved values in the faulty-write cases. Its two saved reads do not prove an atomic update or absence of a later concurrent edit. The command log is supplied by the test driver. It is not native provider history. A retained local counterexample shows that a dishonest completeness flag with hidden set0,set1 can still cause a false completion. The incomplete-history case also violates the baseline's earlier complete-log premise. This comparison tests the full checked rule; it does not isolate each added check.

## Cleanup, privacy and limits

Calendar01, Calendar05 and Calendar13 have later cleanup checks. The final terminal file changes only their cleanup fields and adds the original values and reasons. Earlier rows and failures remain. A ready Calendar search covers October 1 through October 31, which includes all test events. The new Calendar13 editor tab failed to close. Its saved record is in Trash. The earlier possible Calendar23 form from the prior extension was not rechecked. No claim is made that all browser state is clear. Recoverable Trash is not permanent deletion.

Public data use synthetic fields and record aliases. The bounded scan found no supplied private strings, native account identifiers, account email pattern, private account URL or local home path in the extracts. Raw private UI remains local. Public line hashes identify the retained sources but do not let an outside reader inspect those private account records.

The first source audit had two format errors: Calendar logs a successful reload as action_result, and a no-write decision has no actuator event. The audit now checks those formats. Original audit versions and failed receipts remain local. [The change record](improved_independent_changes.md) states these corrections. No rule, saved evidence or scored outcome changed for these audit corrections.
