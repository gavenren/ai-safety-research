# Independent proofs and checks

Date: October 18, 2026.

This file concerns the frozen synthetic model. It does not claim a property of a real website, service, or browser agent. A tick is a model time unit. An effect is one append. A receipt is the visible success reply for one request.

## Independence and event convention

The independent program was written from `analysis_plan.md`, `config.json`, and `input_manifest.json`. The reviewer did not read or import the main program, its tests, or its results before the independent program and its results were complete. The independent program uses an integer time loop and a list of future arrivals. It does not use the main program's event-heap design.

Before enumeration, the lead agent confirmed this event convention: each scheduled slot creates a send or skip event. This includes a slot stopped by an earlier receipt. A receipt is part of the arrival event that returns it. The last event time includes skip events. This convention resolves the meaning of event time and witness order. It does not change which requests arrive or which effects occur. The frozen plan and inputs were not changed.

The independent program's SHA-256 hash at its first complete run was `f5015fd4b9ebf7b8d6c2e70a6317f1ec46ee700361798210e3c956580aae8537`. Later code changes, if any, only add comparison or checks and are recorded in `independent_review.md`.

## Four safe rules in the main model

These proofs require the model's atomic receiver operation. A single arrival checks the deadline, checks the request table, and applies an effect without an intervening arrival. Each sent request arrives at most once. There are no crashes or partial effects.

### No retry

The client sends one request. That request either drops or arrives once. One arrival can create at most one effect. The record's retention time cannot change this result.

### Permanent

Every request has the same identity. The first accepted arrival, if any, stores an effect number. The entry never expires. Every later arrival finds that entry and creates no effect. Thus the final effect count is at most one.

### Delay margin with a correct bound

Let `D` be the largest actual delay, `B` the declared bound, and `T` the retention period. Assume `B >= D`.

If the client sends no retry, the No retry proof applies. The first-send exception can cause one late effect, but cannot cause two effects.

Otherwise at least one retry is sent at time `t > 0`, with `t + B < T`. It follows that `D <= B < T`. Thus the first request, if it arrives, arrives no later than `D`, before `T`. Every permitted retry arrives at a time no greater than `t + D <= t + B < T`. This argument applies to each sent retry.

Let `c >= 0` be the first effect time. Its request entry expires at `c + T >= T`. All arrivals occur before `T`, so no later arrival can reach expiry. They use the same identity and find the first entry. There can be at most one effect.

The proof does not require the client to know `c`. It does require the fixed operation time origin, a correct bound to atomic receiver handling, one time scale, and no queue after admission. If `B < D`, the proof does not apply.

### Receiver cutoff

The receiver rejects each arrival at time `t >= T`, including a late first request. Each accepted arrival therefore occurs before `T`. If the first effect is at `c >= 0`, its entry expires at `c + T >= T`. Every accepted later arrival occurs before that expiry and uses the same identity. It creates no new effect. A rejected arrival creates no effect. Thus the final effect count is at most one.

This rule needs an atomic server deadline that is fixed at the operation's time origin. A client send cutoff alone is a weaker condition.

## Why the receipt labels differ

A truthful success receipt proves that its request returned an existing effect number. It does not prove that every other sent request has finished. The audit therefore uses the final effect count after all sent requests have arrived or dropped.

If a receipt exists, at least one effect exists. A false exact claim therefore means a final count above one. There are two disjoint cases: the count was already above one at the first receipt, or it was one at that receipt and increased later. These are `wrong_at_receipt` and `future_only_false`.

Every `future_only_false` case is a `late_duplicate` case. Some late duplicate cases can already be wrong at receipt time. For example, a second effect can be confirmed and a third effect can occur later. These labels must not be added as if they were disjoint.

## Count controls

Let `q = 2D + 3`, the number of transport codes for each slot. There are `q^3` assignments for each setting and rule. Unused codes remain part of the assignment.

For No retry, exactly `q^2` assignments miss the effect, because the first code must be zero. Exactly `(D + 1)q^2` assignments have clean confirmation, because the first code must be one of the `D + 1` even arrival codes. The other `(D + 1)q^2` assignments have one unconfirmed effect.

For Permanent, only the all-drop assignment has no effect. If any code would give a visible reply, either its slot is sent and the reply arrives, or an earlier receipt already stopped that slot. Therefore Permanent confirms in exactly `q^3 - (D + 2)^3` assignments. The `D + 2` codes that do not give a visible reply are the drop code and the `D + 1` odd arrival codes. All Permanent confirmations are clean.

## Manual boundary controls

The program checks all-drop and immediate-visible-success cases for all seven rules. Other checks cover arrival just before, exactly at, and after expiry; a hit that does not renew retention; a late first request after a later request's receipt; receiver deadline equality; the unconditional first send; and an old arrival that stops a send at the same tick.

Two controls deliver three requests at the same tick. One confirms only at the last arrival. The other confirms at the first arrival and then creates later effects at the same tick. These cases distinguish clock time from event order.

The broken-bound control uses `T=3`, `D=2`, `s=1`, `B=1`, and codes `(1,6,0)`. The first effect occurs at time zero with a lost reply. A permitted retry sent at time one arrives at time three, exactly when the first entry expires. It creates a second effect and gives a visible reply. This is a broken premise of the safe-bound proof.

An added safety control checks all 343 assignments at `T=4`, `D=2`, `s=1` for each of `B=2,3,4`. These 1,029 control runs are separate from the planned main and stress corpus. They are not added to the reported corpus counts. The program also rejects 34 malformed configuration objects.
