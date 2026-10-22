# Plan: repeated gate requests during two undo operations

Date: 2026-10-22, America/Toronto. Save and hash this file before implementation and execution.

## Question and contribution

When two undo operations share a reader gate, can repeated close or release requests make the gate incorrect? Compare a Boolean flag, a nonnegative count, an active-ID set, and an active/completed ID registry. The contribution is a complete small regression corpus and an explicit safety/availability comparison. Ownership checks, idempotent requests, and terminal operation states are known ideas. This is not a new locking algorithm.

The October 22 visibility study has one source writer and one gate owner. This study tests multiple gate owners and repeated gate requests. It does not repeat the October 18 retention test: IDs never expire or get reused here.

## Model and assumptions

This is an in-memory, synthetic state-machine experiment. There is no website, database, AI-agent benchmark, or concurrent thread execution. Each request and each check is atomic in the model. All readers obey the gate.

There are two operation IDs, A and B. Each operation has a first close request C0 and a first release request R0. The first close marks work as active. The first release marks work complete. Work does not start before C0. R0 occurs after its work is complete, and the model combines completion and first release into one boundary. Each request can have zero or one duplicate, called C1 or R1. A duplicate does not change whether the work itself is complete. IDs are unique. No new operation uses a completed ID.

C0 precedes R0 and C1. R0 precedes R1. There is no order constraint between C1 and R0 or R1. Thus a late duplicate close can arrive after completion. Each included request is delivered exactly once. There is no drop, expiry, crash, clock, malicious sender, or data-field change. Delayed first release and missing first close are excluded.

## Rules

- Boolean: C sets closed=true; R sets closed=false.
- Nonnegative count: C adds one; R sets count=max(0,count-1). Closed means count>0. This is a deliberately simple count rule, not a tested library semaphore.
- Active-ID set: C adds its ID; R removes its ID if present. Closed means the set is nonempty.
- Lifecycle registry: C changes absent to active, but has no effect on active or completed. R changes active to completed; later releases have no effect. Closed means at least one entry is active. No completed entry is removed.

All state starts empty or open. All rules receive the same request history and know the same operation ID. Only the model oracle knows which deliveries are duplicates; the rules receive only the operation ID and C/R type.

## Oracle and measures

After every delivered event, the oracle blocks readers exactly when at least one operation has had C0 but not R0. Check each rule against this oracle.

- Unsafe-open point: a gate permits a reader while work is active.
- Unnecessary-closed point: a gate blocks a reader while no work is active.
- Unsafe history: at least one unsafe-open point.
- Overblocked history: at least one unnecessary-closed point.
- Final closed history: the gate remains closed after every included request is delivered and both operations are complete.

Record every event, the active work IDs, every rule's state and gate decision, and every point score. Also report history totals and point totals. Report subgroups by duplicate count and by whether the two operations were ever active together. These counts are corpus properties, not time fractions or natural failure rates.

## Corpus and order

For two operations, enumerate all 16 binary duplicate-presence vectors in the order C_A, R_A, C_B, R_B. For each vector, enumerate every linear extension of the declared precedence constraints, in sorted event-label order. This includes both overlapping and serial work. Every history is scored once per rule. One-operation controls use the same procedure with A only and all four duplicate-presence vectors. Enumerate controls first, then two-operation cases. Give consecutive history IDs starting at 1. Do not sample. No random seed is needed.

Derive each expected schedule count separately: an operation with no close duplicate has one local event order. A close duplicate alone gives two local orders. Both duplicates give three local orders. Interleave the two local orders in binomial(n_A+n_B,n_A) ways. Compare the enumerator count for every vector with this formula. Also compare the recursive enumeration to an independent permutation-and-filter enumerator. The second evaluator must derive oracle state from first-event positions rather than share the main evolving oracle.

## Hypotheses and decision criteria

- H1: With two operations and no duplicates, the Boolean flag has at least one unsafe history; the other rules have none.
- H2: With duplicate requests, the count rule has at least one unsafe history and at least one final closed history.
- H3: The active-ID set has no unsafe history, but at least one late duplicate close leaves a final closed gate.
- H4: The lifecycle registry matches the oracle at every point in the complete corpus.

A hypothesis is supported only if its exact criterion holds. Report adverse results rather than discard them. Do not change rules or inputs after results to make a criterion pass.

## Controls and checks

Check the empty history and the simple one-operation C0,R0 history. Check a no-duplicate overlap witness C_A0,C_B0,R_A0,R_B0. Check a late-close witness C_A0,R_A0,C_A1. Check repeated release C_A0,C_B0,R_A0,R_A1,R_B0. Check that duplicate metadata never reaches rule updates. Check symmetry under swapping A and B. Recompute all saved scores from event positions and declarative rule formulas. Reproduce the full run once in a fresh folder with unchanged code and compare all deterministic output files.

## Resource and failure limits

Use only the Python standard library and local CPU. Limit each full run to less than 60 CPU seconds and 120 wall seconds, with at most two full runs. Preserve the frozen inputs, source hash before execution, complete JSONL rows, summaries, controls, logs, command, software versions, clocks, and file hashes. Stop on an unexpected error, unknown result, missing row, failed control, resource limit, or count mismatch. Preserve failure evidence. No paid service or model API is used.

## Interpretation and review

The gate hides unfinished work; it does not provide mutual exclusion among undo operations. This model assumes the work can overlap. It does not establish correctness of those operations or any provider implementation. A zero violation count is limited to the declared model. Exact enumeration needs no confidence interval or significance test. Report safety and reader availability separately. A separate agent will review the finished package before publication. Record AI roles and no human review. Use the NeurIPS checklist as a review aid, not certification.
