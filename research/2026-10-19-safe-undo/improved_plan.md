# Improved undo rules: prospective production test plan

Date: October 19, 2026. This extends the same paper. Save the input manifest before scored account changes. Preserve earlier simulation and production results. This is a local plan, not an external registration.

## Question and contribution

Can a controller that checks command history, the current record and the saved result reduce incorrect completion claims while still completing supported undo cases? Compare the prior log-assisted provenance rule with the checked-history rule in improved_rules.mjs. This is a small implementation and regression study. It combines established compensation and verification ideas. No new algorithm or global novelty is claimed.

## Hypotheses and decisions

H1: The checked-history rule has zero incorrect completion claims in all valid assigned cases. A single observed incorrect claim rejects H1. H2: It completes every valid clean case in the first four scenarios, so refusal alone cannot satisfy the study. H3: It refuses known incomplete history and stale sealed history before an undo write. H4: It refuses completion after either deliberately incorrect saved field. H5: The baseline gives at least one incorrect completion claim in the incomplete-history and wrong-save scenarios. Report failures and unknown results; do not replace them. Compare paired scenario/site outcomes only when both assignments have valid evidence. Report all assigned denominators.

## Rules and inputs

Initial fields are (X,Y)=(0,0). The recorded agent action adds one to X and has a saved observation (1,0). A command log is the ordered list of later commands whose saved phases were checked. The test driver supplies this log. It is not a native website history. A seal marks the last command included in the presented log. historyComplete means that the log is known complete through that seal; it does not prove no later edit.

The baseline keeps the old rule: if the presented log contains set0 or set1, preserve current X; otherwise subtract one. Preserve current Y. Its status is complete from this decision. Later reads allow independent scoring but do not alter that fixed status. This is a controller claim, not a claim that a free-running model chose to say success.

The checked-history rule validates record identity, field contract, the original action, and the log completeness flag. It replays the presented log from the saved agent state and compares it with a fresh pre-undo read. It refuses on a mismatch. It derives the undo target by replaying the same commands from the saved initial state. It makes at most one undo update attempt if needed. This attempt can contain the necessary separate literal field gestures, because Notion saves properties separately. It does not retry the attempt. It reports complete only after two separate reopened saved reads match identity, contract and both target fields. The controller requires reloaded=true, distinct read IDs, valid ordered read times, and both final times after the pre-read. These are recorded runner observations, not independent server freshness proofs. Missing or invalid final reads give unknown; a valid field mismatch gives abstain. It never receives the evaluator target or full withheld history. The complete-log assumption is stronger information than field equality. A dishonest completeness flag with a hidden return-to-same-value history can defeat this rule; state this limit and check it locally.

These are sequential browser changes. Two agreeing reads do not prove an atomic snapshot, a provider revision guard, complete native history or protection against all concurrent changes. No outside actor or race is injected between the pre-read and undo save.

## Assignments and fault controls

Eight scenarios crossed with two rules and two sites give 32 assignments, 16 per site. Each assignment uses a fresh temporary record. The order is shuffled separately by Python random.Random(2026101902); the saved list is authoritative. There is one assignment per site/scenario/rule. These selected cases are not a random sample. Use exact counts, not population confidence intervals or p-values.

| Scenario | Full later commands | Presented commands | Complete through seal | Intervention |
| --- | --- | --- | --- | --- |
| control | none | none | true | none |
| independent_y | flip_y | flip_y | true | none |
| addition | add1 | add1 | true | none |
| assignment_return | set0,set1 | set0,set1 | true | none |
| incomplete_history | set0,set1 | none | false | Withhold both commands from controller input; retain full evaluator evidence. |
| prestate_mismatch | add1 | none | true at earlier seal | Seal empty log, then perform a separate controlled add1 before fresh pre-read. |
| wrong_x_save | none | none | true | At the undo actuator, save requested X+2 and requested Y instead of the requested fields. |
| wrong_y_save | none | none | true | At the undo actuator, save requested X and flipped requested Y instead of the requested fields. |

The last two are deliberate actuator faults through the actual website UI. They are not alleged provider save defects. Record the correct decision, the intended target and actual injected literal before dispatch. Verify that the injected fields are saved before the controller finalizes. Do not correct an incorrect undo result. Cleanup occurs only after final evidence and the outcome. The evaluator independently replays full later commands without the agent action. Faulty undo writes are not part of that target.

## Website contract and action limits

Use existing connected Google Calendar and Notion accounts. All account mutations use the supported browser UI. No API mutation, new credential, access change, message, invitation, permanent deletion, purchase or paid model API call.

Calendar: unique synthetic title, private one-day all-day past event on October 14, 2026, no guests, reminders, location, conference or recurrence. X is Description as exact signed decimal integer with only boundary CR/LF removed. Read visible Description text explicitly. Y is Free=0/Busy=1. Check native All day checked value and all saved contract fields. Start creation only from a ready ordinary Calendar view; a search view with disabled Create is not ready. Success notices are not evidence of saved values. Use fresh ready exact-marker searches for cleanup. Do not touch or save the old uncertain Calendar trial23 form from the earlier study.

Notion: new private temporary database with Name title, X Number and Y Checkbox. Empty body, no sharing. After a field change, close the editor, wait two seconds, reload the same page, wait two seconds, then read. Empty is not zero. Verify property types, native identity, marker and non-Trash state. Two final reads require two separate reloads.

Create once per assignment. If uncertain, inspect before another create; do not blindly repeat. Before undo, each planned phase permits at most one corrective literal save after a fresh saved-state read. Save all failures. No correction or repeat write is permitted after undo or an injected undo fault. A wrong saved undo result is an outcome, not an exclusion. Stop the assignment at 12 minutes or two uncertain saves. Use phase checkpoints and action-attempt logs before dispatch. Unknown assignments stay in the planned count, with no replacements.

## Required evidence and measures

Record baseline, agent state, every actual later command and saved state, the seal, presented history, completeness flag, fresh pre-read, exact prepare input/output, actuator instruction, both final saved reads, exact finish input/output and cleanup. Keep stable native identity, synthetic marker, timestamps, complete action arguments, UI results/errors, screenshots and raw field strings privately. Terminal rows must record valid or unknown and a reason. A valid result requires all setup evidence and two final saved reads with stable identity and contract. Do not discard a final field mismatch.

A clean completion reports complete and both final reads equal the independently computed target. A false confirmation reports complete when either valid final read differs. An abstain-correct case refuses and both reads equal target. An unresolved case refuses while either valid read differs. Unknown is not a success, failure or refusal. Also report write attempts, deliberate-fault acceptance, preservation of Y, pre-write refusals and paired differences. The report must distinguish prevention of a claim from repair of an incorrect record.

## Cleanup, privacy and review

Move each known temporary record to recoverable Trash after evidence is saved. Confirm absence from the active exact-marker view. Remove the private Notion parent after every child is accounted for; verify its Trash banner. Never empty Trash. Report saved-record and browser-form cleanup separately.

Preserve complete private evidence locally. Public files contain synthetic fields and aliases, not account names, emails, native private IDs, unrelated content or screenshots. Publish extraction code, original line hashes and scoped independent source review. Public replay cannot reconstruct withheld private UI. Preserve old package files and their historical receipts. Add prefixed improved files; update the same report, README, bibliography and index only as needed. Run the documented analysis, independent evaluator, clean replay, privacy checks and relevant NeurIPS checklist review before publication. State actual Codex roles and no human review. Fetch remote commit and match file hashes after publication.
