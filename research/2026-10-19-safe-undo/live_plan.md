# Production website extension: plan

Date: 2026-10-19, America/Toronto. This is an extension of the same October 19 paper. Save the input manifest before scored trials. Unscored interface checks precede this plan. The original exhaustive simulation stays separate.

## Question and contribution

When a browser executes the six fixed undo rules on saved records, do the rules preserve specified later edits? This small case series adds browser action evidence from two production accounts. It does not establish novelty priority, a provider defect, or general agent performance. See live_source_notes.md for the limited primary-source search.

## Hypotheses and comparison

The full restore, field restore, subtract and value guard rules will each give at least one incorrect completion in the selected cases. The log-assisted revision guard will avoid incorrect completions but leave some cases unresolved. The log-assisted provenance control will produce the reference target in all valid selected cases. These are prospective predictions, not observations.

Compare each rule on a fresh record for each history and site. The control has no later command. The four histories are fixed test cases, not a random population sample. Do not calculate population confidence intervals or significance tests. Report exact counts with denominators and incomplete assignments.

## Sites and data contract

Use the existing connected Google Calendar and Notion accounts. All mutations use the supported browser interface. Connectors may read evidence but must not perform mutations. Use no paid service or new model API call.

Calendar: use a unique synthetic title, a past one-day all-day event on October 14, 2026, Private, without guests, reminders, location, conference or recurrence. X is Description, parsed as an exact signed decimal integer. Permit only boundary CR/LF removal; keep the raw string. Y is availability, Free=0 and Busy=1. Read Description explicitly because a DOM snapshot can omit its content. Verify the contract after each reopened saved edit page. Do not change account settings.

Notion: use a new private temporary database. Name is the synthetic marker, X has Number type, and Y has Checkbox type. Keep the page body empty. Close editors, wait two seconds after each saved mutation, reload the same page, wait two seconds, then read fields. An editor-ready header alone does not prove fresh values. Empty is not zero. Verify types and the selected record identity. These fixed waits follow the unscored preflight. A mismatch stays in the action log; the bounded corrective-save rule below applies.

Only temporary records for this run may change. No messages, invitations, access changes, credentials, payments or permanent deletion. Stop a trial if an unrelated record or outside edit is encountered.

## Assignments

Initial state is (X,Y)=(0,0). The agent action sets X=1. Read the saved record after each phase. Four later histories are crossed with six rules at each site: 48 planned rule trials. Use a fresh record for each assignment. The fixed order is shuffled separately per site by Python random.Random(2026101901). Save the generated list; it is the authoritative order. Add two diagnostic histories per site after core trials, for four diagnostics without undo.

| History | Later commands | Pre-undo fields | Reference target |
| --- | --- | --- | --- |
| control | none | (1,0) | (0,0) |
| independent_y | flip_y | (1,1) | (0,1) |
| addition | add1 | (2,0) | (1,0) |
| assignment_return | set0, then set1 | (1,0) | (1,0) |

Save and reopen each intermediate assignment in assignment_return. An attempted unchanged-value save is not evidence of a new field write. The arithmetic command is implemented as read, compute, and set a literal. This sequential implementation does not establish a remote arithmetic primitive.

Diagnostics use sub1 and set0 after the agent action. Both leave saved fields (0,0). Without the agent action, their targets are (-1,0) and (0,0). Compare selected fields only. Do not claim equal native revision metadata. No undo rule is executed for diagnostics.

## Rules

live_rules.js receives only the current fields and the verified test command log. It must not receive the reference target.

1. Full restore: set both fields to zero; status complete.
2. Field restore: set X to zero and preserve Y; status complete.
3. Subtract: set X to current X minus one and preserve Y; status complete.
4. Value guard: if X=1, restore X=0; otherwise abstain.
5. Log-assisted revision guard: restore X=0 only when the verified later log has no X write; otherwise abstain.
6. Log-assisted provenance control: if the later log contains a set command, keep current X; otherwise subtract one. Status complete.

The last two rules receive experiment-log information. Native Calendar event versions and Notion page timestamps are not X revision counters. The rules do not infer intent from the website. The pre-undo read and later write are separate operations. No outside writer is injected during that interval. Atomicity and race safety are not tested.

## Evidence and action limits

Record creation once per assignment. If creation is uncertain, inspect saved records before any further create. Never blindly retry add, subtract, toggle or delete. Each intended phase permits at most one corrective literal field save after a failed save and a fresh saved-state inspection. If the phase still lacks evidence, mark the assignment invalid or unknown and stop it. No replacement assignment is permitted. Keep errors and unsuccessful attempts.

Stop each trial after 12 minutes of active trial work or after two uncertain saves. The runner may pause between trials. An incomplete assignment stays in the denominator. A wrong saved undo result is a result, not an exclusion.

Require baseline, agent state, every later state, pre-undo state, rule decision before dispatch, and final saved state. Record native identity, marker, timestamps, exact visible fields, complete action arguments, tool results and errors. Close editors and reload before each saved read. Verify identity and the site contract. A typed input or success message alone does not establish the saved outcome.

The reference target is the result of the prescribed later commands on (0,0), with the agent action omitted. The evaluator, not the rule executor, computes it. Complete plus target match is clean completion. Complete plus mismatch is false confirmation. Abstain plus mismatch is unresolved. Abstain plus target match is correct-state abstention. Also count Y changes away from its target. Unknown observations are never inferred as success.

## Cleanup, privacy and release

After final evidence, move each known temporary record to recoverable Trash. Confirm absence from the active record search or table. Trash the new empty Notion parent only after all test child records are accounted for. Never empty Trash. Report any unresolved cleanup item separately.

Preserve private raw logs, exact helper source, screenshots and native IDs locally. Public evidence uses aliases and synthetic fields only. Preserve a private alias map. Publish action summaries and parsed field evidence with local source IDs; exclude account names, emails, private URLs and unrelated UI. An independent agent must inspect raw-to-public extraction and outcome counts. Record the limits of public replay when full private UI evidence cannot be shared.

Before publication, run the analysis and independent audit, check report values and references, inspect for private information and unsupported claims, and review relevant NeurIPS checklist items. State actual AI use and human review status. Update the same paper and index, then verify remote file hashes. Do not publish unsupported results.
