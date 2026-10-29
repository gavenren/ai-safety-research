# Prospective review of the production website extension

Date: 2026-10-29. This review was written before account tests and results.
Reviewer: a separate Codex agent. No human review occurred.

## Scope

Test the six unchanged rules from `outputs/2026-10-29-corrected-usage/plan.md`.
Use Google Drive and the primary Google Calendar in the connected account.
Use actual saved source fields and actual browser saves for admitted output actions.
The test credit is an invented accounting unit. It is not a provider charge, quota,
API limit, storage measure, time measure, or refund of physical work.

The website supplies saved record fields. The study supplies the revision labels,
signed deltas, selected delivery order, duplicate delivery, and closed accounting
period. Do not attribute those parts of the test to either website.

## Fixed cases

The value tuple is `(uA, vA, uB, vB)`. Here `u` is the initial value and `v` is
the corrected value. Source records A and B are separate objects. The two saved
states of each object supply reports 1 and 2. The demand is one test credit.

| Case | Values | Delivered report order | Cap | Expected final balances in rule order below |
| --- | --- | --- | --- | --- |
| Early credit | (2,0,0,0) | A2,A1,B1,B2 | 1 | 0,2,2,2,2,0 |
| Late old value after increase | (0,2,0,0) | A2,A1,B1,B2 | 2 | 2,2,2,0,2,2 |
| Unchanged values with exact replay | (1,1,1,1) | A2,A2,B2,A1,B1 | 3 | 2,2,2,2,2,2 |

Rule order: Net, GlobalClamp, ItemClamp, ArrivalReplace, MaxReplace,
RevisionReplace.

In the first case, only Net and RevisionReplace should admit. The other four
rules should refuse a feasible action. In the second case, only ArrivalReplace
should admit. Its admission should exceed the study cap by one credit. In the
third case, all six rules should admit. The exact repeated A2 report must leave
each rule's state unchanged. These are predictions, not observed results.

The design gives six source histories and 36 rule decisions across two services.
There are 24 unique saved source snapshots. The declared delivery lists contain
26 report deliveries across the six histories, or 156 rule update steps across
all six rules. These counts exclude setup, reads, output saves, and cleanup.

## Account records and actual browser actions

Use six source records and six output records per service. Add one private Drive
parent folder. This gives 25 initial records. Setup can use connectors. Each
source record must have its initial state read and saved before the browser writes
its revision 2 state. The revision label must change even when the value does not.
This gives 12 planned browser source corrections.

Use one output record per rule and service. Reuse it across the three cases in
fixed order. An admitted action changes its name or title through the browser to
a unique case-and-rule marker. A refused action makes no Save call. These rules
predict 18 output saves: nine per service. This is 18 saved renames, not 18 new
records. Do not count fixture creation or cleanup as a rule-controlled admission.

Before each case, save the exact current output field for every rule. After each
decision, read the same object again. For an admission, require the new marker,
the same object identity, and a fresh saved-state read. For refusal, require zero
Save calls and an unchanged field. A field alone cannot prove that no write was
attempted. Preserve the action log as well as the before and after values.

Keep each intermediate saved snapshot. The third case will overwrite the earlier
output names. Final names alone cannot support claims about the earlier cases.

Each case has its own ledger. The retained name from an earlier case is a baseline
field, not a credit in the next case. Reused objects and shared source observations
mean the 36 decisions are matched tests. They are not 36 independent samples.

## Conditions for valid evidence

1. Bind every report to the observed source object and saved state. Use a unique
   study event ID. An exact duplicate preserves the event ID and every field.
2. Save both initial and corrected reads before local delivery. The initial
   snapshot is an old saved value, not a new read of a record after correction.
3. Label the revision counter as a study counter. Do not imply a provider-native
   monotone sequence or a conditional-write guarantee.
4. Apply duplicate filtering before each amount update, as in the original rules.
   Do not turn an exact duplicate into a new report or a second admission request.
5. Close the controlled study period only after all four source states were
   observed. The researcher declares this closure. The website does not prove
   that no future edit or billing correction can occur.
6. Keep rule inputs separate from the scorer's final true value. Compute the final
   value from the observed revision 2 states. Do not give that value to a rule
   before its declared reports arrive.
7. If a save has an uncertain result, stop writes for that object. Check its saved
   state before any retry. Record the failure and any extra action. Do not hide
   an extra save inside the planned count.
8. Treat a failed read or parse as unknown. Do not replace it with the planned
   value. A write receipt alone is not a saved-field check.

## Privacy and cleanup

Keep exact account IDs, event URLs, and raw account evidence in local private
files. Publish only stable test aliases and relevant test fields. Calendar events
must be private and free, with no guests, reminders, meeting links, or recurrence.
Keep Drive test records private. Do not use or edit pre-existing user records.

Track all 25 created objects. Delete temporary Calendar events and verify their
cancelled state where available. Move Drive records to Trash and verify the
actual state supported by the available surface. Do not call a trashed record
permanently deleted. Do not purge Trash. Use exact-object checks plus a bounded
active marker search. An empty search alone is insufficient cleanup evidence.

## Reporting limits and review decision

The design can show whether these unchanged rules produce the expected decisions
when their inputs come from real saved website fields, and whether the controller
carries out the resulting browser writes. It does not test natural event disorder,
provider billing, real financial limits, concurrent writers, arbitrary stale reads,
or unbounded retries. No population error rate or statistical significance follows.

The three cases do not distinguish GlobalClamp from ItemClamp. Their difference
remains supported by the original simulation, not by this live extension. Do not
claim that the live extension confirms the full per-item comparison.

Proceed with the stated design. Before publication, compare all state and decision
rows with a separate implementation. Check actual saved output states and cleanup.
Keep failures and deviations in the report. Use the phrase "controlled tests on
production websites" and explain the local delivery step near the result claims.
