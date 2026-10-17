# Derivations for the repair-rule audit

Date: October 17, 2026. These arguments use the frozen plan. The source-review agent wrote them without importing the main program. They are direct arguments about the stated model. They are not machine-checked proofs or new concurrency algorithms.

## 1. Model and counting unit

Write a record as (A, X, Y, U; V). A, X, Y, and U are bits. V is an integer revision. The task permits an effect only if A = 1 immediately before the effect. The effect must set Y to that same pre-effect X and must preserve A, X, and U.

There are four initial records: A = 1, X in {0,1}, Y = 1 - X, and U in {0,1}. A background write flips A, X, or U and increments V in one atomic step. Each gap contains a word of at most b writes. With three possible letters, the number of gap words is

    q(b) = sum from j = 0 to b of 3^j.

Thus q(0) = 1, q(1) = 4, and q(2) = 13. A program assigns K gap words. Each setting contains 4 q(b)^K assignments. Counts retain unused suffixes as the plan requires. Two assignments can therefore have the same executed prefix. The counts are exact properties of this corpus, not estimates of a natural probability.

All reads, background writes, and guarded effects are atomic. A successful guard and its effect are one event. No other write can occur between them. These are essential assumptions.

## 2. Safety of a complete replan with CAS

Consider any successful `replan_cas` attempt. At its read, A = 1; otherwise the rule would stop. Let the read source be x and revision be v. The rule computes candidate Y = x.

Success requires the revision at the effect to equal v. Every background write increments V, and V never returns to an old value. No earlier successful agent write exists because success ends the policy. Therefore no background write occurred between this read and effect. At the effect, A is still 1 and X is still x. The candidate satisfies the task contract. The rule writes only Y, so it also preserves A, X, and U.

The argument applies to any successful attempt, including one after a rejection. Denial or exhausted retries does not issue an effect. Therefore this rule has no invalid accepted effect and no collateral overwrite under the model. The claim depends on complete revision coverage and a new candidate computed at every read. A fresh revision attached to an old candidate does not meet this proof.

## 3. Safety of the complete dependency-value guard

Consider any successful `dependency_guard` attempt. At its read, A = 1, and the candidate equals the read X, written x. Its atomic guard requires both current A = read A and current X = read X. Success therefore establishes current A = 1 and current X = x at the effect. The candidate is x, so the effect is valid. Only Y changes; the other fields remain intact.

This proof permits intervening writes. They can change U or change A or X and later return them to the read values. The model checks the current-value contract at the effect. It does not require an unchanged history. No claim follows for a contract in which any earlier permission withdrawal permanently invalidates the action.

An X-only guard lacks this proof. After a read with A = 1, a single A flip leaves X unchanged but makes A = 0. The X-only guard accepts and violates the permission condition. That is a missing dependency in the specified rule, not an error in the model's complete guard.

## 4. Refreshed-token success count and invalid retry

In `refresh_cas`, each round reads V but retains the original permission and candidate X. A round succeeds exactly when its gap word is empty. A nonempty word increases V and fails CAS, even if its bit changes later cancel. This policy does not stop on a later permission denial.

Among q^K assigned word programs, exactly (q - 1)^K contain no empty word. All other programs have a first empty word, where the policy succeeds. Including the four initial records gives

    refresh_cas successes = 4 [q^K - (q - 1)^K].

For K = 1, success requires an empty first gap. Its candidate and permission are then current, so no accepted effect is invalid. For K greater than 1 with b at least 1, use a first gap X and an empty second gap. The first attempt rejects. The second attempt reads the new revision but retains the old candidate. It passes CAS and writes the wrong source value. Replacing X with A gives a permission violation. Each example uses only one background write; zero writes cannot produce either violation.

For K = 2 and b = 2, q = 13. The success count is 4 (13^2 - 12^2) = 100. A first empty word gives 4 * 13 = 52 valid assignments, because all second words remain unused. A nonempty first word followed by an empty second word gives 4 * 12 = 48 other successes.

Of the 12 nonempty first words, the eight words

    A, X, AX, XA, AU, UA, XU, UX

leave A or X different from the initial value. Each has four possible initial records. Thus the invalid accepted-effect count in this setting is 4 * 8 = 32. The other four first words, U, AA, XX, and UU, preserve the current task inputs and produce valid effects. This is a union count: words AX and XA violate both the permission and source-value conditions and are counted once.

## 5. A correct final equation can hide an overwrite

Take initial (A, X, Y, U) = (1, 0, 1, 0). Let the first background word be U. Immediately before the effect the record is (1, 0, 1, 1).

The `replace` rule installs the old record with Y changed: (1, 0, 0, 0). It now satisfies Y = X, but it erased the background change to U. The same-input `patch` rule gives (1, 0, 0, 1) and preserves that change. This separates a collateral overwrite from a source-value or permission violation.

There is also a stronger warning about post-effect checks. Use the first word A instead. The pre-effect record is (0, 0, 1, 0), where permission is absent. `replace` installs (1, 0, 0, 0). A check only after the effect sees A = 1 and Y = X, because the replacement restored the old permission. The effect nevertheless violated the pre-effect permission condition and overwrote A. Therefore the audit must use the pre-effect state and a field-preservation check.

## 6. Two disjoint H5 subsets

H5 compares the same assigned input under `dependency_guard` and `replan_cas`. It counts cases where the complete dependency guard succeeds and the replan CAS rule exhausts all K attempts. The following subsets have direct counts. They are subsets of all paired outcomes, not a claim to count the entire paired set.

### Unrelated-only subset

Every assigned word is nonempty and contains only U. For b = 0 this is impossible. For b = 1 each word must be U, giving four assignments. For b = 2 each word can be U or UU, giving

    unrelated-only count = 4 * 2^K.

At the first effect A and X still equal the read values, so the dependency guard succeeds. Every replan CAS gap advances V, so that policy rejects K times. Its repeated reads always see A = 1. It therefore exhausts its budget rather than stopping on permission.

### Returned-dependency subset

The first word contains A or X and has even A and X parity. At b = 2 it must be AA or XX: two choices. Each later word is nonempty and also has even A and X parity. It can be U, UU, AA, or XX: four choices per later gap. Including four initial records gives

    returned-dependency count = 4 * 2 * 4^(K - 1), for b = 2.

For b less than 2 the count is zero. After the first word, the relevant fields equal their initial values, so the dependency guard succeeds. In the replan CAS execution, each word is nonempty and advances V, but preserves A and X at the next read. CAS therefore rejects in every round and exhausts K attempts. The subsets are disjoint because this subset's first word changes A or X, while every word in the unrelated-only subset contains U only.

## 7. Scope of the arguments

These arguments concern a deterministic function, Y = X, and an explicit permission bit. They do not measure an agent's ability to identify dependencies or to infer a user's intent. They do not establish general safety for browser actions, ETags, incomplete record versions, multiple records, or non-atomic checks followed by later effects. A is a modeled task permission, not a Google account permission.

Current-value validity differs from version history. A strict version rule can reject an action after values change and return. A complete value guard can accept that action under this task contract. Neither observation proves that one contract is correct for every application.

The audit does not implement or evaluate PlanFence, CoAgent, or the verified anomaly system. Those sources already establish related principles. PlanFence v2 explicitly retains the inputs behind a plan and requests a replacement plan; its contract ends before the later external effect. Here the complete atomic effect guard is an assumed capability. The contribution is the fixed case set and its exact regression checks, with these limits made explicit.
