# Formal checks for the finite retry model

Date: 2026-10-15

These arguments apply to the model in `analysis_plan.md`. They are special cases of established retry and distributed systems reasoning. They are not new general impossibility results. The model has one writer, one logical item, no rollback, truthful historical reads, and at most one retry. A drop is permanent and specific to an attempt. A client timeout is not a drop.

## 1. A fresh negative read does not prove that an action has ended

At tick 0, submit an append action. At tick 1, read the current state with zero lag. Consider two worlds:

| World | First attempt at tick 1 | Resolution at tick 8 |
| --- | --- | --- |
| P | Pending, zero items | Commit one item |
| D | Pending, zero items | Drop with no item |

The read gives the same count and attempt state in both worlds. The count is current in both worlds. It contains no information that separates the two later outcomes.

If a retry is submitted at tick 1 and commits at tick 2, world P has one item at tick 2 and two at tick 8. A controller can claim completion at tick 2 before the second item exists. World D has one final item from the same retry.

Thus an absence-based retry can cause a duplicate even with zero read lag. The failure does not require a stale image or an incorrect query. A later truthful terminal state can separate these worlds. Waiting is therefore an available remedy in this bounded model.

## 2. A tight local relation for the two worlds

Restrict the decision at the shared tick-1 history to an immediate one-retry rule. It submits a retry with probability r, where 0 <= r <= 1. The retry, if sent, is certain to commit at tick 2. This local comparison permits no later fallback retry for world D.

Let A be the event that the rule sends the immediate retry. The identical history implies the same P(A) = r in both worlds.

- In world P, a duplicate occurs if and only if A occurs. Thus P(duplicate | P) = r.
- In world D, recovery by this immediate rule occurs if and only if A occurs. Thus P(recovery | D) = r.
- Failure to recover world D by this rule has probability 1 - r.

It follows that

P(duplicate | P) = P(recovery | D),

and

P(duplicate | P) + P(no recovery by this rule | D) = 1.

The relation is tight: a random choice that submits the retry with probability r attains it. These are probabilities from a defined random decision in two synthetic worlds. They are not incident probabilities for real services.

This relation does not apply to every adaptive policy. A rule can wait until tick 8, read the terminal state, and retry only in world D. Such a rule can recover world D without a duplicate in world P. The statement therefore does not claim that the full bounded task is impossible.

## 3. A terminal-drop gate is sufficient for at-most-one effects

Suppose a policy retries only after it observes that the original attempt is permanently dropped. There are two cases.

1. The original attempt commits. Its truthful state can never be `drop`. The gate sends no retry. The task has one final effect.
2. The original attempt drops. It has no effect and cannot add one later. At most one retry is sent. That retry contributes zero or one effect.

In both cases, the final effect count is at most one. A delayed read cannot invalidate this proof. Once a truthful permanent drop state exists, it stays true. Read delay can postpone recovery or confirmation. It cannot turn this state into a future commit.

The proof depends on truthful, permanent, attempt-specific status. It does not apply to an error message that can appear after a successful write, to an ambiguous timeout, or to a status for a different attempt. It proves at-most-one effects, not guaranteed completion. Both attempts can drop. The deadline can also pass before confirmation.

## 4. A bound on execution plus read lag is sufficient

Let U be a valid upper bound on the original resolution delay. Let L_max be a valid upper bound on read lag. Read at time t >= U + L_max. If the actual lag is L <= L_max, the historical time is

as_of = max(0, t - L) >= U.

The original attempt has resolved by U. If the original committed, its effect exists at every historical time at least U because there is no rollback. A truthful negative read at this time therefore excludes an original commit. The original must have dropped. A single retry cannot produce a second original effect.

For the main grid, U = 8 and L_max = 4. A negative query at or after tick 12 is safe under these assumptions. Effects that resolve exactly at the query boundary must be applied before the query. The saved event order satisfies this condition.

If either bound is wrong, the inequality can fail. A negative read can then precede the first effect. This explains why the stress suites can break the time-based gate. The terminal-drop proof does not need these numerical timing bounds. It still needs the status contract.

## 5. Direct event-time validation

The main analyzer advances through integer ticks. The separate validator does not use that transition loop. It computes the retry and stop times directly.

If the original attempt commits at d1 and read lag is L, its first possible visible time is v1 = d1 + L. If it drops, set v1 to infinity. Let S be the chosen finite query schedule.

- `absence_retry` uses the first t in S if t < v1.
- `timeout8` uses the first t in S with t >= 8 if t < v1.
- `bound12` uses the first t in S with t >= 12 if t < v1.
- `terminal_retry` retries only for a dropped original, at the first t in S with t >= d1 + L.
- `no_retry` has no retry time.

If the retry is submitted at a2 and commits, its visible time is v2 = a2 + d2 + L. The first query at or after the earliest finite visible time is the first positive observation. The observed count at that query determines whether the controller claims one item or stops with a detected duplicate.

The validator counts all admitted committed attempts for the final state, including attempts that resolve after a controller stop. Under ideal deduplication it takes the smaller of this count and one. It then reconstructs an ordered event list from the derived times and compares it with every saved event trace.

All outcome comparisons use exact integers and labels. Summary means are also checked from exact integer sums. There is no simulation noise and no fitted statistical model.

## 6. Ideal server deduplication is a separate sufficient condition

The positive control assumes that all committed attempts refer to the same durable logical key and that the server stores at most one item for that key. By that definition, any number of successful attempts in this model has at most one stored item. This result tests the scoring and client comparisons. It is not evidence that a real server implements durable deduplication correctly.

The client can still fail to obtain an effect when both attempts drop. It can also fail to confirm an effect before the deadline. Safety and completion therefore remain separate measures under deduplication.
