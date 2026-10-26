# Prospective Calendar zone evidence test

Date: 2026-10-26. Owner-requested extension of the usage accounting paper.

Question: Does the corrected Calendar field adapter refuse missing or incorrect named-zone evidence on new production records?

Hypothesis: It returns a full-field proof only when the exact-record evidence shows the intended start and end zone. A UTC offset is the distance from UTC. It does not uniquely identify a named time zone.

Method: Use 12 new private, Free events in the owner's primary Calendar. Six conditions have two events each. The two runs use November 4 and 5, 2026, at 12:00–12:05. No guests, reminders, recurrence, or Meet link. Record exact IDs privately. Each event has a unique test title. Create each once through the connected action. Do not retry an uncertain create. Read its exact ID after creation. Record complete returned fields and any omitted zone labels.

Conditions: complete evidence; absent zone object; absent end-zone label; incorrect supplied New York labels for a Toronto event; actual saved New York zone when Toronto is intended; unverified zone evidence. Only the actual-saved-zone condition changes the production saved zone. Other omissions and corruption are explicit local changes to evidence, not website faults.

Before any editor zone read, call the frozen corrected adapter on the new connector read with no zone object. Do not claim completion. Then open each exact saved event in the real Calendar browser editor. Read the event title and start/end zone controls. Cancel the dialog and editor without saving. Save raw UI evidence privately and publish only safe extracts and hashes. The UI's displayed GMT offset may describe the current date. Compare the named zone, not that label's offset. An exact-record audit links the private ID and URL to the safe alias.

Call the adapter with the assigned evidence for each case. Then supply the unmodified exact-record evidence and call it again. Keep the two actual New York cases incorrect until cleanup; do not repair or create replacements. This last call measures evidence recovery for ten correct events and continuing refusal for two incorrect events. These are 36 adapter evaluations on 12 records, not 36 independent website trials.

Baseline: A local field-only rule compares all returned non-zone fields and confirmed status but ignores named-zone evidence. It is a counterfactual comparator, not a separate account writer. It is expected to accept the two wrong-zone records because New York and Toronto have the same offset on these dates.

Measures: decision, rejection reason, full-field proof count, unsupported proof count against the predeclared evidence contract, wrong-saved-zone acceptance, recovery count, created record count, duplicate create count, and cleanup status. The primary criterion is zero unsupported proofs in assigned conditions and zero acceptance for the actual wrong-zone records. Expected assigned outcomes: 2 accept and 10 reject. Expected unmodified-evidence outcomes: 10 accept and 2 reject. Connector-only evidence should be rejected in all 12 cases. Preserve any failure; do not change the frozen adapter silently.

Cleanup: Read each exact ID, delete only these new temporary events, then read cancelled status on each ID. Search the exact test marker within November 4–6 UTC. Check all pages. No active result is expected. Do not purge Trash or change other events.

Analysis: Fixed selected cases, one account, one connector and browser session. No random sample, confidence interval, significance claim, population error rate, or reliability guarantee. Repeated phases are dependent. Missing/corrupt evidence is controlled injection. The actual wrong-zone case is a production saved-field error created for the test. No server outage is induced. The adapter trusts the evidence producer and does not authenticate evidence, enforce freshness, or guarantee an atomic cross-tool snapshot.

Freeze this plan, case matrix, copied adapter and evaluator before the first write. Record every deviation. Repeat the saved-input analysis twice. Obtain an independent agent audit, check private-data removal and source use, update the existing report and index, and verify the remote file hashes before reporting publication. Codex generates this extension. No human or peer review is implied.
