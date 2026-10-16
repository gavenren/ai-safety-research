# Derivations for the fixed field-read model

Date: October 16, 2026.
Status: mathematical derivations from the frozen [analysis plan](analysis_plan.md). These are not measured results. The main calculation and separate validation must check the stated identities and witnesses. No website, account, model, or agent was tested for this file.

## 1. Terms and relation to known methods

A **state** is the complete vector of current field values. A field value of 1 means that it equals its required value. A **target** is the all-one vector. An **atomic event** has one effect between two model states, with no visible intermediate state inside that event. A **history** is one initial state and one ordered word of writes in each allowed gap. A **snapshot** returns values that were valid together at one time.

The distinction between sequential observations and a snapshot is established. Sequence-number methods and double collects are prior work, not a new contribution here. See [Afek et al., Section 3](https://groups.csail.mit.edu/tds/papers/Shavit/JACM93.pdf). The database term fractured read concerns transaction visibility; it is related, but this model has no multi-field transaction. See [Bailis et al., Section 3](https://www.bailis.org/papers/ramp-sigmod2014.pdf). We use **mixed read** for field observations from different model states.

## 2. Finite history set

Let:

- `d` be the number of required fields, either 2 or 3.
- `r` be the number of complete scans, either 1, 2, or 3.
- `m = r*d` be the number of field reads.
- `b` be the maximum writes in a gap, either 0, 1, or 2.
- `t = (1,...,1)` be the target.
- `p(j) = j mod d` be the field read at zero-based read index `j`.

There are `m+1` gaps. Gap 0 is after the initial revision read and before the first field read. Gap `m` is after the last field read and before the final revision read. The other gaps separate successive field reads. The final revision read and the decision have no write between them.

A gap word is an ordered tuple of field indices. Its length is from 0 through `b`. The empty word is allowed. Each index means “flip that field once.” Two occurrences of one index are two writes, even if they restore the earlier value.

For a gap, the number of allowed words is:

`q(d,b) = sum(k=0,...,b) d^k`.

Each gap chooses one word independently in this enumeration. There are `2^d` initial states. Therefore the exact number of histories is:

`N(d,r,b) = 2^d * q(d,b)^(m+1)`.

This is a count, not a probability model. The model does not state that all histories are equally likely on a website. When `r` or `b` changes, the finite history set changes.

## 3. Exact recurrence

At a fixed stage, use the state:

`z = (s, G, A, W, U)`.

Here:

- `s` is the current field vector.
- `G` is true exactly when all field reads so far equaled 1.
- `A` is true exactly when the target has existed at any model state so far.
- `W` is the exact total number of writes so far.
- `U` is the exact number of writes to field `d-1` so far.

The observation index belongs to the stage, not to `z`. Keep `W` exact, not only modulo four. The exact number is needed for the non-reused guard and minimum-write witnesses. Keep `U` exact to model a non-reused but incomplete revision.

Let `D_j(z)` count histories after `j` field reads and before gap `j`. Initially, for each initial vector `s`:

`D_0(s, true, s=t, 0, 0) = 1`.

All other counts are zero.

For each state with nonzero count and each permitted gap word `w`, apply the word in order. For each letter `i`:

1. Replace `s_i` by `1-s_i`.
2. Increase `W` by one.
3. Increase `U` by one if `i=d-1`.
4. Replace `A` by `A OR (s=t)` using the state after that write.

The flip and both applicable revision changes occur in the same atomic event. Do not test `A` only at the end of a gap. A target that exists between two writes still counts as a target that existed.

For `j<m`, perform field read `p(j)` after the word. Set:

`G_new = G AND (s[p(j)]=1)`.

Add `D_j(z)` to `D_(j+1)(s, G_new, A, W, U)`. Different words that reach the same state contribute separately to its count. For `j=m`, apply the last word and add the count to the terminal distribution without another field read.

## 4. Why merging is exact

Two history prefixes at the same stage with the same `z` have the same possible continuation words. Each continuation gives the same future record state, field-read result, revision conditions, and target-history flag. Every scored outcome depends only on the terminal `z`.

Thus the prefixes can be merged by adding their integer counts. This is a finite-state counting argument. It does not merge distinct histories into one vote. It preserves their multiplicity.

For witness selection, keep counts and representatives separate. Since `W` is exact, the representative for a fixed state has a fixed write count. Keep the lexically smallest prefix for that state, with order defined by the initial bit tuple and then the tuple of gap words. At the end, select the smallest `W` in the outcome set and break ties by the prescribed lexical order. Prefix merging is safe for this representative rule because the same continuation can be appended to either prefix.

## 5. Invariants and control identities

Before gap `j`, there have been `j` gap choices. Therefore:

`sum_z D_j(z) = 2^d * q(d,b)^j`.

After the last gap:

`sum_z D_terminal(z) = N(d,r,b)`.

Further checks are:

- `0 <= U <= W <= b*(m+1)`.
- `G` can change from true to false, but never back to true.
- `A` can change from false to true, but never back to false.
- If `A` is false at the end, the final state is not the target.
- A coordinate relabeling preserves counts when the read order and the partial-counter field are relabeled with it. Relabeling only the data while leaving those rules fixed is a different comparison.

For each fixed sequence of gap words, final state is the initial vector XOR the cumulative flip vector. XOR means bitwise addition modulo two. This map is a bijection on initial vectors: each possible final vector has exactly one initial preimage. Exactly one initial state for that gap sequence ends at the target. Consequently:

`number of histories with final state t = q(d,b)^(m+1)`.

This gives a control count independent of the main recurrence.

When `b=0`, every gap is empty. Only the target initial state can satisfy every field read. Each policy accepts that one history and has no false acceptance. No policy rejects a correct final state. These are analytic control predictions.

## 6. Terminal predicates and outcome counts

At terminal state `z`, define six acceptance predicates:

| Policy | Acceptance predicate |
|---|---|
| Values | `G` |
| Full revision | `G AND W=0` |
| Modulo 2 revision | `G AND W mod 2=0` |
| Modulo 4 revision | `G AND W mod 4=0` |
| Partial revision | `G AND U=0` |
| Atomic final snapshot | `s=t` |

The initial full, modulo, and partial revisions are zero. The final revisions are `W`, `W mod 2`, `W mod 4`, and `U`. These predicates therefore match the equal-before-and-after tests in the plan.

For a policy predicate `P(z)`, sum terminal counts over these sets:

- Accepted: `P(z)`.
- No-common-target: `P(z) AND NOT A`.
- Wrong-at-decision: `P(z) AND s!=t`.
- Rejected-correct-final: `NOT P(z) AND s=t`.

Every no-common-target acceptance is also wrong at decision, because the final state lies in the scored interval. The converse need not hold. The target can exist earlier and then cease to hold.

Accepted-correct-final, accepted-wrong-final, rejected-correct-final, and rejected-wrong-final are disjoint and partition all `N` histories. This supplies a further count check. Rejection is not a false completion claim.

## 7. Conditional full-revision guarantee

Under the frozen model, every atomic write adds one to a revision that never repeats. The final revision equals the initial revision only if `W=0`. The record is then constant over the entire scored interval. All fields are read at least once. If `G` is true, the constant record is the target. The final state is also the target because no write occurs between the final revision read and the decision.

Therefore full revision has no no-common-target or wrong-at-decision acceptance in this model. This is a conditional application of established revision reasoning, not a new concurrency theorem.

There is exactly one accepted history per grid setting: start at the target and use an empty word in every gap. A nonempty word contains at least one write, even when it restores the data. Thus:

`full-revision accepted = 1`.

Using the final-state control count from Section 5:

`full-revision rejected-correct-final = q(d,b)^(m+1) - 1`.

For `b=0` this is zero. For `b>0` it is positive. These are analytic predictions for the fixed finite set. They are not production frequencies. The rejected histories can have a correct final state even though the rule did not obtain the required unchanged-revision evidence.

The premises are material. All revision and field reads must be fresh reads of the same authoritative record. Each field flip and revision increment must be atomic together. Every required field must be covered. The revision must not wrap, reset, or repeat. A reused record identity needs a separate generation identity. A delayed counter update after a series of visible field writes does not satisfy the model.

For a multi-field write that exposes intermediate values, an odd/even write-in-progress protocol is one established approach, with writer and ordering conditions. The present model does not implement that protocol. See the [Linux sequence-counter documentation](https://docs.kernel.org/locking/seqlock.html).

## 8. Atomic final-snapshot control

The ideal atomic final snapshot accepts exactly when `s=t` at the common decision point. It therefore has zero wrong-at-decision acceptance by definition. It also has zero no-common-target acceptance because the final target state is a state within the scored interval. It rejects no correct final state.

Its accepted count is `q(d,b)^(m+1)`, from the bijection in Section 5. It uses a stronger interface than individual field reads. These control properties do not establish that a screenshot, DOM read, connector result, or provider response is an atomic final snapshot.

Saved-deliverable checks are already used in computer-use research. [StateAct, Section 4.2](https://arxiv.org/html/2607.22798v1) is one example. This model studies the consistency of supplied observations; it does not measure that paper's agents or finish gate.

## 9. Two-field minimum for a never-existing target

Consider `d=2` and `r>=1`, with read order `x,y,x,y,...`. There are `2r` field reads. Suppose every read equals 1, but `(1,1)` never exists anywhere in the scored interval.

Whenever `x` is read as 1, the state must be `(1,0)`. Whenever `y` is read as 1, the state must be `(0,1)`. Adjacent read states therefore differ in both bits. Each allowed write flips one bit, so at least two writes are required between each adjacent pair. There are `2r-1` such pairs, in disjoint time intervals. Hence:

`W >= 2*(2r-1)`.

The bound can be attained when `b=2`. Start in `(1,0)` with an empty initial gap. Between the first `x` read and the next `y` read, use:

`(1,0) -> (0,0) -> (0,1)`.

Between a `y` read and the next `x` read, use:

`(0,1) -> (0,0) -> (1,0)`.

Repeat these transitions between adjacent reads. Use an empty final gap. Every field read is 1. No state is `(1,1)`. Each intervening gap has exactly two writes, so the total is `2*(2r-1)`. This establishes both the lower bound and a matching history under the frozen model.

With `b<2`, no such two-field history can cross even the first adjacent `x,y` pair. The no-common-target set is therefore empty for Values, and for its stricter revision subsets, at these budgets. This statement concerns the never-existing target. It does not exclude a wrong final state after a target existed earlier.

For `r=1,2,3`, the proposed minimum values from this formula are 2, 6, and 10. These are mathematical predictions; the enumeration must still verify its saved witnesses against them. The matching construction uses an even write count, so it also supplies a modulo-2 candidate. It does not by itself establish the minimum for a modulo-4 outcome set.

## 10. Partial-revision distinction: two fields and three fields

The partial counter counts every write to the last field and never repeats. Equal initial and final partial revisions imply that the last field never changed. If Values accepts, the read of that field is 1. Thus it is 1 throughout the interval.

With **two fields**, the only other field is the first field. An accepted read of this field as 1 then occurs while the last field is also 1. The target exists at that read. Therefore the two-field partial guard cannot have a no-common-target acceptance under this model, regardless of the number of scans. It can still be wrong at decision: start at `(1,1)`, make all field reads, then flip the first field in the final gap. Values and the partial revision still pass, but final state is `(0,1)`. This path needs a positive gap budget.

With **three fields**, two fields remain outside the partial counter. Keep the last field at 1. Start at `(1,0,1)`. Read the first field as 1, then use two writes:

`(1,0,1) -> (0,0,1) -> (0,1,1)`.

Read the second field as 1. The third field is 1 in every state. Before the next pass needs the first field, reverse the two writes through `(0,0,1)`. The reverse transition can occur in a gap after the second read or after the third read. Repeat for later scans. After the last second-field read, no return is needed.

For `b=2`, this path gives all target-valued reads and `U=0`, while `(1,1,1)` never exists. Thus the fixed partial counter has a structural difference between two and three fields. The claim is about these field and counter definitions. It does not mean that incomplete revisions are safe for two-field tasks: the wrong-at-decision example already shows otherwise.

## 11. Snapshot, current state, and persistence

The two outcomes answer different questions. No-common-target asks whether the assembled target existed at any common time in the read interval. Wrong-at-decision asks whether it holds at the specified final event. The main model includes that event in the interval and permits no later write before the decision.

A live system can write after the last check. For example, a correct target can pass even a valid snapshot and full-revision check, then change before the assistant reports completion. The proof above does not cover that gap if it is added. A later mutation also does not show that the earlier snapshot was false. It shows the limit of the time claim. No finite observation here proves indefinite persistence.

Recent reads are not automatically authoritative. HTTP freshness concerns cache age and permitted reuse; it does not mean that the origin could not have changed. See [RFC 9111, Section 4.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-4.2). Validator equality also needs a defined resource and representation. A content-based validator can repeat when content returns; it need not be a never-reused history counter. See [RFC 9110, Section 8.8.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.8.1).

There is a concrete field-coverage warning in the Calendar documentation. Reminder changes do not change the event's `updated` field. The earlier account study checks reminders. Thus this timestamp is not a complete revision for that field contract. See the [Events reference](https://developers.google.com/workspace/calendar/api/v3/reference/events). Google also documents conditional requests using ETags, but the present study does not test their cache or concurrency behavior. See the [version-resource guide](https://developers.google.com/workspace/calendar/api/guides/version-resources).

## 12. Limits and review status

The derivations depend on the frozen model. It has exact reads, a fixed identity, one bit per field, atomic flips, known read order, and bounded write words. It excludes faulty sensors, wrong normalization, permissions, missing fields, delayed replicas, failed writes, and user interpretation. The checks concern one target record, not all side effects of a task.

The contribution is an explicit finite comparison and auditable witnesses. The underlying snapshot and revision principles are established. No new general algorithm, provider defect, natural failure rate, safety certification, or human review is claimed. Codex wrote these derivations. A separate calculation and agent review are required before publication.
