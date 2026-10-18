# Proofs and exact controls

Date: October 18, 2026. These derivations use the frozen [plan](analysis_plan.md). They were written by a separate Codex agent without reading or importing the main program and without running the enumeration. They are analytic checks, not additional measured experiments. The established systems principles are credited in the [source record](source_search.md).

## Notation and model boundary

`T` is the finite retention period. `D` is the actual maximum delay from send to atomic receiver handling. `B` is the delay bound used by Delay margin. `s` is the send spacing. Slots 0, 1, and 2 have send times 0, `s`, and `2s`. A tick is a synthetic integer unit.

The first actual effect can come from any delivered slot. Call its time `c`. A later matching key has a cache hit only while its age is less than `T`. At age exactly `T`, the entry is expired. A hit does not change `c`. An effect and its request record are one atomic event. The proofs do not cover a separate queue between acceptance and effect.

A success reply identifies one completed effect. It does not state that the final effect count is one. `false_exact_claim` scores the hypothetical extra inference that one success reply means exactly one final effect. It does not label the service reply as false.

## No retry

Only slot 0 is sent. Transport does not copy requests. One arrival can append at most one effect. Thus No retry has final count at most one. Every visible success implies exactly one effect. Duplicate and false-exact-claim counts are zero for all model parameters.

## Permanent request memory

All arrivals use one key. The first delivered request appends an effect and atomically stores its result. Every later arrival finds that record and returns the same result. The record never expires. Thus Permanent has at most one effect. A visible success proves one effect, and no remaining arrival can append another. This proof assumes the permanent receiver state; a client label alone does not provide it.

## Delay margin under a correct bound

Assume `B >= D` and the frozen time model.

If no retry is permitted, only the first request can arrive, so the No retry argument applies. The initial-send exception is important: the first request is sent even when `D >= T`.

Otherwise, a permitted retry has a positive send time `t` and satisfies `t+B<T`. Therefore `D<=B<T`. The initial request arrives, if delivered, by time `D<T`. Each permitted retry arrives by `t+D<=t+B<T`. Hence every actual arrival occurs before absolute time `T`.

The first effect time satisfies `c>=0`, so `c+T>=T`. Every later arrival therefore precedes `c+T` and finds the original key record. It cannot append a second effect. This proves zero duplicates and zero false exact claims under the bound. It does not prove equal completion opportunity or progress without a receipt.

The bound must cover delivery to the atomic receiver event. A bound on local send time or on one part of a network path is insufficient. Clock error and separate receiver queues are outside this proof.

## Receiver cutoff

The receiver rejects every arrival at or after absolute time `T`. It does this before either cache lookup or append. Therefore every accepted arrival occurs before `T`.

If there is an accepted arrival, the first effect time `c` is nonnegative. All later accepted arrivals precede `T<=c+T`, so the stable-key record remains valid. No second effect can occur. If there is no accepted arrival, the final count is zero. Thus this rule has zero duplicates and false exact claims for all `D` and `B` in the model.

The deadline is fixed at the original logical operation's time origin. It is not reset for a retry. Admission and effect are atomic here. In a real system, rejecting new admissions does not itself cancel work already accepted into a separate queue.

## Corpus size

There is one drop code. Each delay from 0 through `D` has two codes: lost or visible success. Thus

`q = 1 + 2*(D+1) = 2D+3`.

Each setting has `q^3` complete assigned code tuples. The main grid has five values of `T`, three values of `s`, and four values of `D`. Its assignment count is

`5*3*(3^3+5^3+7^3+9^3) = 15*(27+125+343+729) = 18,360`.

Seven policies give `7*18,360 = 128,520` main rows. The stress setting has `7^3=343` assignments and `7*343=2,401` rows. Main and stress must remain separate. A different unused suffix is still a different assignment, even if its events do not occur.

## Closed-form control counts

These identities apply to each setting, including the stress setting.

### No retry counts

Only the first code matters. Each first code occurs with `q^2` suffixes.

- Missed: `q^2`, from the first drop code.
- Unconfirmed one: `(D+1)*q^2`, from lost replies on a delivered first request.
- Clean confirmed: `(D+1)*q^2`, from visible replies on a delivered first request.
- All duplicate and false-claim labels: zero.

The total is `(1+2*(D+1))*q^2=q^3`.

Across the main grid, these predict 2,460 misses, 7,950 unconfirmed-one cases, and 7,950 clean confirmations. For stress, they predict 49, 147, and 147 respectively. These are algebraic expectations, not values copied from an execution.

### Permanent counts

With no delivered request there is no visible success, so all three slots are sent. There is exactly one no-effect assignment: all three codes are drop.

The codes with no visible success are drop and the `D+1` lost-reply codes. There are `D+2` such codes. A tuple has no visible success if and only if all three codes come from this set. If any visible code is unused, an earlier visible success must already have stopped sends, so the tuple is still confirmed.

Therefore:

- Missed: `1`.
- Unconfirmed one: `(D+2)^3-1`.
- Clean confirmed: `q^3-(D+2)^3`.
- All duplicate and false-claim labels: zero.

Across the main grid, these predict 60 misses, 3,300 unconfirmed-one cases, and 15,000 clean confirmations. For stress, they predict 1, 63, and 279 respectively.

## Matched schedule controls

For a fixed assignment, New key, Stable key, and Permanent have the same sends, arrival times, and first visible-success time. Each uses the same rule for all send slots. Every arrival succeeds, whether by append or cache hit. Visibility is assigned by the same transport code. By induction over events, their client stop decision is the same. The returned effect number and final effect count can differ.

Thus a difference between these three rules in first-receipt time or number of sends is an implementation error in this model. Their effect-count differences are not measured gains in confirmation speed.

Send cutoff and Receiver cutoff also send the same slots. They have the same history for arrivals before `T`. Their response histories can first differ at or after `T`, when neither may send a retry. Receiver rejection can reduce confirmed completion, but cannot cause an extra send after the cutoff.

## Error-label identities

A truthful success reply implies that at least one effect exists at that event. Effects are never removed. Thus a confirmed case cannot have zero final effects.

Let `F` be false exact claims, `W` wrong-at-receipt cases, and `U` future-only false cases. Then `F` is the disjoint union of `W` and `U`. The first-receipt count is either already above one or exactly one; in the latter case, a later effect creates the failure.

Every future-only false case is a late-duplicate case. Every late-duplicate case is a false exact claim. A wrong-at-receipt case can also have a late duplicate, for example when another append follows an already duplicated state. These labels must not be added as disjoint groups.

The five disjoint outcomes are missed, unconfirmed one, unconfirmed duplicate, clean confirmed, and false exact claim. Their counts sum to `q^3` per rule and setting.

## Hand-worked boundary examples

These examples follow from the transition rules. The enumeration must retain them. They are not claimed minimum witnesses; the program applies the frozen minimum order separately. Code 0 is drop; code `1+2d` is delay `d` with lost reply; code `2+2d` is delay `d` with visible reply.

### Stable key fails at exact expiry

Use main `T=1,D=0,s=1`, tuple `(1,2,0)`. The first request appends at time 0, with its reply lost. The retry arrives at time 1. The age is exactly `T`, so a second effect is appended. Its visible reply reports that second effect. Final count is two.

### Send cutoff permits a duplicate after a receipt

Use primary main `T=2,D=3,s=1`, tuple `(8,2,0)`. Slot 0 is sent at 0 and arrives at 3. Slot 1 is sent at 1, which passes `1<T`. It arrives immediately, creates the first effect at time 1, and gives a visible reply. No further slot is sent. At time 3, the old slot-0 request arrives. The first record is now exactly two ticks old and has expired. A second effect occurs after the first receipt. The receipt-time count was one; the drained count is two.

This example does not require a false reply. It requires the controller to infer an exact final count from a reply about one effect.

### Broken margin bound

Use stress `T=3,D=2,s=1,B=1`, tuple `(1,6,0)`. The first request creates an effect at time 0 with a lost reply. A retry at time 1 passes `1+B=2<T`. Its actual delay is 2, so it arrives at time 3. The old record has expired, and a second effect occurs. The actual delay violated the bound used by the client. This does not contradict the proof under `B>=D`.

### Safe rules can miss an available effect

Use main `T=4,D=2,s=1`.

For tuple `(0,0,2)`, the first two slots drop. Permanent sends slot 2 at time 2 and receives an immediate visible success. Delay margin skips slot 2 because `2+D=4` is not less than `T`; it produces no effect.

For tuple `(0,0,6)`, the first two slots again drop. Permanent's last request arrives at time 4 and succeeds. Receiver cutoff rejects that arrival at the exact deadline; it produces no effect. The stronger receiver rule has a different acceptance contract.

## Interpretation limit

The proofs are conditional on the declared model. The finite enumeration checks program behavior within that model. Neither establishes a provider's actual contract, a language model's ability to follow a policy, or a general end-to-end protocol. Equal assignment weights are not real event probabilities. No confidence interval or population failure rate follows from these counts.
