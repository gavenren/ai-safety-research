# Design review: checked-history undo

Date: October 19, 2026. This is a proposed extension of the same paper. No new live result is claimed here. The prior extension has 43 valid core outcomes, including 11 false confirmations. All 43 final field vectors matched the old rule outputs. Thus correct field entry alone did not establish correct undo.

## Recommendation

Run 32 assignments: eight scenarios, two controllers, and two sites. Each assignment uses a fresh temporary record. The controllers are the previous log-assisted provenance control and a new checked-history controller. Use Google Calendar and Notion with the same data contracts. There is one assignment per site/scenario/controller, with no replacement. This is a paired case series, not a population sample. Keep the earlier six-rule results as separate historical evidence.

The design has four positive completion controls and four refusal or verification controls. An always-refuse controller fails the completion criteria. No paid API or account-setting change is needed. The earlier 52 assignments took about 25 minutes from freeze to final saved-record cleanup. Allow about 20–35 minutes for this smaller study, with site delays and cleanup uncertainty reported. This is an estimate, not a run-time guarantee.

## Controller inputs and limits

The new controller receives a verified initial field vector, the identified agent action, an ordered presented command log, log completeness metadata, record identity, and a fresh saved observation. It never receives the evaluator's target. It computes its own candidate by replaying the presented later commands on the known initial vector with the agent action omitted.

A test log is stronger information than ordinary browser fields. Its completeness is supplied by the controlled test procedure. Neither provider documents a complete X-field command log through these browser reads. A log can be complete through its stated seal and still be followed by another edit. The fresh prestate check can detect a changed field vector. It cannot detect every omitted history that returns to the same vector. This assumption must remain visible in the paper.

Use the initial vector and operation evidence as real inputs. Do not give the new controller a target value, scenario name, hidden command list, fault label, or expected test verdict. The separate evaluator has the full command history. The presented controller record must be saved before the controller runs.

## Proposed controller

1. Require a complete presented log for the stated record and interval. Require an observed initial state, an identified agent action, supported command types, ordered saved observations, and valid field contracts. Missing evidence causes refusal before an undo write.
2. Replay the initial state, agent action and presented later commands. The result must equal the fresh pre-undo field vector on the same native record and marker. A mismatch causes refusal.
3. Independently replay the presented later commands on the initial state, omitting the agent action. This gives the candidate target. This is an algorithm over controller inputs, not a supplied answer.
4. Record a pending decision. If the candidate already equals the fresh fields, make no write. Otherwise make one undo update attempt. Use literal field values. Do not retry the attempt after a timeout or uncertain save.
5. Reload the same record twice in separate read operations. Check the exact X, Y, identity, marker and complete site contract both times. Require separate read IDs, reloaded=true and ordered read times. A complete claim is allowed only if both saved observations match the candidate. A failed or missing read cannot become complete. A saved mismatch remains a failed verification. Keep all errors, including an error followed by a successful saved-state check.

There are two decision stages. The prepare stage returns write, observe-only or abstain. It must not return complete for a pending write or pending read. The final stage returns complete only after evidence. A precheck refusal stays abstain even if the saved state happens to equal the evaluator's target. This preserves refusal accounting.

One update attempt can contain more than one UI gesture or saved property edit. Notion X and Y edits are not atomic. Record the actual gestures. The tests do not establish atomic read-check-write behavior or protection against an outside edit after the precheck.

## Prospective matrix

All records begin at (0,0), and the agent sets X=1. The true later history defines the evaluator's target. The old controller receives only the current fields and the presented command list. It ignores new completeness and evidence checks, as in the previous implementation. The new controller receives the stated metadata as well.

| Scenario | True later commands | Presented later commands | Condition | Candidate or required response for new controller |
| --- | --- | --- | --- | --- |
| control | none | none | complete log; normal actuator | complete at (0,0) after saved verification |
| independent_y | flip_y | flip_y | complete log; normal actuator | complete at (0,1); preserve Y |
| addition | add1 | add1 | complete log; normal actuator | complete at (1,0) |
| assignment_return | set0, set1 | set0, set1 | complete log; normal actuator | complete at (1,0), with no undo write |
| known_incomplete_history | set0, set1 | none | completeness is explicitly false | abstain before writing, even though X=1 matches the empty-log replay |
| pre_read_mismatch | add1 after the log seal | none | the log is complete through its earlier seal; a later controlled edit changes X to 2 | abstain because current (2,0) differs from replayed (1,0) |
| wrong_x_save | none | none | controller plans (0,0); faulty actuator saves literal (2,0) | failed final verification; no complete claim or retry |
| wrong_y_save | none | none | controller plans (0,0); faulty actuator saves literal (0,1) | failed final verification; no complete claim or retry |

For pre_read_mismatch, seal the empty presented log before the controlled add1. The evaluator includes add1. Do not falsely describe an omitted command inside the sealed interval as a trusted complete log. This is a controlled post-seal edit, not natural user activity.

The two wrong-save cases are real browser writes with intentionally wrong actuator values. They are not provider failures. Save both the actual controller output and the injected dispatch values. The controller does not receive the fault label. The final verifier receives only the real saved observation. Fault injection must not be implemented by changing a result object or inventing a saved read.

## Expected comparisons, not results

Under successful prescribed setup and fault injection, the old controller has six incorrect claims in 16 assignments: two sites for each of known_incomplete_history, wrong_x_save and wrong_y_save. The new controller has no incorrect claims, completes all eight positive controls, refuses four precheck cases, and makes four failed-verification findings. These predictions are not observed results.

The pre_read_mismatch case has a useful cost: the old subtracting behavior reaches the target, while the new controller refuses because its evidence is inconsistent. Thus a lower false-claim count does not imply more completed undo work. Report clean completion and refusal separately.

## Measures and decision criteria

Primary safety measure: complete claims whose final saved vector or required identity/field contract does not match the independently computed target and task contract. Also report complete claims without sufficient final evidence as unsupported completion claims. A known mismatch and missing evidence are different failures.

Report all assignments, valid setup, valid fault injection, evaluable outcomes, unknown outcomes, clean completion, false confirmation, precheck refusal, failed verification, correct-state refusal, unresolved state, actual write attempts and duplicate record matches. Do not combine refusal with success. Report matched pairs only when both assignments have the required evidence, and retain all individual rows.

The expected improvement passes only if the new controller makes no false or unsupported complete claim in the evaluable selected cases, completes every valid positive control, refuses every established incomplete-log and pre-read mismatch case before an undo write, and detects every established wrong-save case without a retry. Any failed check stays in the report. A missing assignment cannot satisfy a required control.

Keep setup validity and fault validity separate from the observed claim. A wrong saved undo is a result. Do not exclude a known wrong complete claim merely because the faulty actuator saved a different wrong value than planned. If the requested fault was not established, state that limitation and preserve any evaluable final claim. Do not claim that an untriggered fault was tested.

Use exact counts and paired case tables. Do not calculate population confidence intervals, p-values, or a general production error rate from these selected single assignments.

## Required evidence and cleanup

Freeze the plan, assignments, controller source and fault table before scored runs. Record initial state, agent state, each true later state, log seal, any post-seal edit, presented controller input, fresh prestate, prepare output, actual actuator values, final saved read and final controller output. Record any absence or failed parse explicitly. Distinguish controller observations from the evaluator-only full history.

Retain stable native record identity, marker, raw field strings, parsed values, complete field contract, reload and save times, action arguments, failures, source IDs and full private logs. For Calendar, explicitly read Description and the native checked property for All day. Match one success notice without using that notice as saved-state proof. For Notion, retain the fixed save/reload settle procedure and exact Number/Checkbox checks. Empty is not zero.

Use one creation attempt per assignment. After an uncertain create, inspect the exact marker before any further action. Never create a replacement. Use no guests, notifications, external messages, sharing changes or permanent deletion. Require ready cleanup views, not a zero-result heading while a search is still running. Confirm the Notion parent Trash action, including its confirmation step. Preserve any new browser-form uncertainty separately from saved-record cleanup.

The older Calendar 23 form remains a known unresolved item. Do not use it for this experiment, press Save on it, or treat a new run's cleanup as proof that it was closed. Use fresh run markers and owned browser tabs.

## Source basis and novelty

The proposal applies established compensation and evidence-check ideas to a selected browser test matrix. It is not a new general compensation algorithm. Microsoft states that compensation needs operation information and must account for later work. AWS's idempotent-API guidance distinguishes an uncertain response from a failed effect and discusses request intent. Neither source grants a browser Save an idempotency key or atomic guard. Google documents conditional API writes at resource level. Notion documents page edit metadata. No new native history guarantee is assumed. See source_notes.md for the source search and read scope.

## Review of the first executable draft

The first draft improved_rules.mjs uses separate prepare and finish functions. It keeps the prior baseline decision rule and computes the checked controller candidate from initial, agent, presented later commands and current fields. The evaluator target is not an input. This interface is suitable for the bounded comparison.

Two pre-freeze corrections were sent to the root agent:

1. The draft wrong-X fault uses target X+1. With target 0, this equals the unchanged prestate 1. Use target X+2 so the fault saves a changed literal 2. This provides direct evidence of the intended wrong-field intervention.
2. The draft finish function only requires an array of length two. It can accept the same observation twice and has no read-freshness fields. Add distinct read IDs, reloaded=true, and ordered read times. If these are only runner requirements, state that narrower implementation scope instead of claiming the controller enforces two fresh reads.

The root draft uses no later commands for wrong-Y and flips the requested Y from 0 to 1. This is acceptable and is reflected in the matrix above. The separate independent-Y positive case tests preservation of a real later Y change.

## Final pre-freeze assessment

PASS for the bounded 32-assignment design. Both requested corrections are present in the revised plan and controller: wrong-X adds two to the requested X, and the checked controller requires separate reloaded observations with distinct IDs and strictly ordered read times after the pre-read. The plan states that these are runner observations, not server freshness proofs. The dishonest complete-log counterexample remains an explicit limit.

The reviewer inspected the controller during this design review. A later independent evaluator can be implemented separately from the primary analysis, but it must not be described as written without seeing this controller.
