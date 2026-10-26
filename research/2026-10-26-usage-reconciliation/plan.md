# Plan: cumulative usage reports and reservation accounting

Date: 2026-10-26, America/Toronto. This plan was frozen before implementation and analysis.

## Question and contribution

Can event-ID deduplication alone make cumulative usage reports safe for reservation accounting? How do six rules differ under delayed, repeated, and reordered progress and final reports?

A cumulative report gives total use since one fixed start, not an additional amount. A reservation holds budget capacity for a job. A terminal report proves the job has ended and gives its final cumulative use. Deduplication ignores a repeated event ID.

The contribution is a complete small comparison corpus, with separate safety and accounting measures. Summation, maximum merging, retained reservations, terminal evidence, and deduplication are established ideas. No new protocol or priority is claimed. October 25 assumes one correct final receipt; this study varies receipt delivery and bookkeeping after provider work is complete.

## Hypotheses and decision criteria

H1: DedupSum removes exact replay overcount but can still overcount different cumulative reports. It has a final overcount witness and a receipt-sufficient refusal caused by that overcount. Compare the same world with TerminalOnly to isolate this effect.
H2: LastValue can undercount after a delayed progress report, even though its terminal flag never reopens. At least one world exceeds the real budget after admitting B.
H3: HighWaterEarly can exceed the budget because a progress value does not prove final use. At least one world is unsafe before T is delivered.
H4: HighWaterHeld and TerminalOnly have no actual budget breach or uncovered actual A charge, settle to z, and make identical B decisions in all worlds. Under a fixed cap, progress booking alone creates no additional admission capacity when the residual reservation is retained.

Record exact counts. A missing predicted witness rejects that hypothesis; do not alter rules to obtain it. Publish supported negative results. No sample probabilities or operational error rates.

## Provider and controller model

There is one fixed job A and one budget C. A originally reserved R. Before the delivery history begins, the provider has emitted P with cumulative value x, then completed A and emitted T with final value z. It has already used z units. Both reports may be delayed. There is no further A use. Reports are true, authenticated, bound to A and one counter start, and immutable. P is nonterminal even if x=z. T is terminal. Their distinct IDs are P and T. A duplicate is byte-identical and has the same ID. Equal values do not mean equal IDs or status.

The actual A use z is audit truth; it is not supplied to a controller until T. The controller starts with booked A use q=0, hold h=R, terminal flag f=false, seen-ID set empty, booked B use k=0. Its available balance is C-q-h-k. Local event processing and the B admission check are atomic. There is no clock or provider execution timeline inside this delivery model.

B is one independent requested job with use b. At its single D event, admit B iff available>=b. If admitted, book and use b immediately; otherwise refuse it. B never retries. A use is irreversible and cumulative. This is an integer resource model, not real money or a service integration.

## Inputs and schedules

R is 1 or 2. Enumerate each integer pair 0<=x<=z<=R. There are 3+6=9 pairs with their R value. C is R, R+1, or R+2. b is 1 or 2. There are 54 numeric settings.

Delivery multisets are PT, PPT, PTT, and PPTT. Generate every distinct permutation. For each delivery order, insert D at every gap, including before all reports and after all reports. The four schedule groups contain 2*3=6, 3*4=12, 3*4=12, and 6*5=30 histories. Total 60 schedules. Thus 3,240 input worlds and 19,440 rule outcomes. Same-ID copies are not labeled as separate occurrences. Retain equal-value, zero-use, and repeated controls; their multiplicity is not a population distribution.

Use ascending R,x,z,C,b; multiset order PT,PPT,PTT,PPTT; lexical unique delivery permutations (P before T); ascending D gap. World ID is the zero-based index padded to four digits. Rule order below. Persist full inputs and deterministic trace order.

## Six rules

For every received report with value v, first set f = f OR (ID==T). Thus the terminal status is sticky for every rule. D does not change A state. Ignore rules do not undo a prior final outcome. Update as follows:

1. AddEvery: q=q+v on every delivery. Then h=0 if f, else max(0,R-q).
2. DedupSum: add v to q only if its ID is not in seen. Add its ID to seen. Then h=0 if f, else max(0,R-q).
3. LastValue: q=v on every delivery. Then h=0 if f, else max(0,R-q).
4. HighWaterEarly: q=max(q,v). Set h=0 after any report, including nonterminal P.
5. HighWaterHeld: q=max(q,v). Then h=0 if f, else R-q. Monotonic values and a correct cap make this nonnegative.
6. TerminalOnly: ignore P for q and h. On T, assign q=v and h=0, including duplicates. The terminal flag remains sticky.

For trace comparability, seen records all received IDs for every rule, even if unused by that rule. The membership test for DedupSum uses the pre-event set.

## Measures

Save initial state, each event's before and after state, value and terminal status, duplicate indicator, and D decision. Save available balance after each event.

At each state score actual excess max(0,z+k-C), uncovered actual A charge max(0,z-q-h), inflated total A accounting max(0,q+h-R) before the first delivered T and max(0,q+h-z) after it, and local deficit max(0,-available). Record case existence, maximum units, and first bad event for each. The initial state must be included, with index -1 and label INITIAL. A first-bad record uses event index and label. A breach before first T means a state with f=false, including INITIAL. Actual excess and coverage use true finished use z, not a claim about possible future use or controller knowledge.

At D record accepted/refused; unsafe admission iff accepted and z+b>C; feasible refusal iff refused and z+b<=C. Record receipt-sufficient refusal iff refused, T was delivered before D, and z+b<=C. This last measure isolates refusal despite complete final evidence. Also record whether an actual breach occurs before the first T delivery (or without any T yet), final q-z signed error, final overcount/undercount/exact, and final h.

Publish summaries for each rule and duplicate group, and paired admission differences against TerminalOnly. Measures overlap; do not sum them into a failure total. Counts are exact for the chosen finite corpus, so no sampling interval applies.

## Planned controls and invariant checks

Named controls (run all six rules):
- R=C=2,x=1,z=2,b=1, P,T,D: distinct cumulative totals must not be added.
- Same numbers, T,P,D: delayed progress must not reduce final booking; LastValue can admit unsafe B.
- R=C=2,x=0,z=2,b=1, P,D,T: progress zero must not release the reservation.
- R=2,C=3,x=1,z=1,b=2, P,T,D: safe feasible B with distinct equal-valued IDs.
- R=2,C=3,x=0,z=1,b=2, P,T,T,D: repeated terminal report must not double book.
- R=2,C=3,x=1,z=2,b=1, P,P,T,D: repeated progress plus cumulative terminal report.
- R=2,C=2,x=0,z=0,b=2, T,P,D: true zero final use with delayed zero progress.
- R=2,C=2,x=1,z=1,b=2, D,P,T: pre-report guard must keep the full cap.

Check complete input counts, unique world/rule keys, state continuity, nonnegative q,h,k, correct report values/status, sticky f, and once-only B. H4 is checked at every step, and final q=z,h=0 for its two rules. Compare HighWaterHeld and TerminalOnly total q+h and B decisions at every step. DedupSum and AddEvery agree in the no-duplicate group. DedupSum final q=x+z in every world. HighWaterEarly and HighWaterHeld have equal q at every step. Permuting delivery without D cannot change the two complete rules' final state. The eight controls give 48 rows; preserve exact outcomes rather than selecting only successes.

## Execution and review

Freeze plan SHA-256 before main implementation. Freeze main source before its first run. A separate agent must write and freeze an independent specification before reading main code or results. Compare all saved event states, decisions, scores and summaries, not only headline counts. The independent adapter may read the schema after its specification is frozen; disclose this order.

Run the main procedure twice into different result directories. Compare deterministic files byte for byte. Keep environment metadata outside byte equality. Use Python standard library, no random seed, no model API or external calls in the experiment. Limit each run to 120 CPU seconds, 300 wall seconds and 200 MB output; stop and preserve failures if exceeded. Record actual CPU/wall time, versions, platform, logs and output bytes. Use a finite simulator, not SQLite or a browser.

Freeze all rules before execution. Preserve deviations and failed checks. Source review and separate final review must pass before publication. Check NeurIPS guidance, claims, assumptions, reproduction, rights, copied text, private data, relative links, and AI/human review disclosure. No new license.

## Limits and interpretation

One nonterminal and one terminal value, one writer/start epoch, no resets or downward corrections, honest reports, complete delivery, no conflicts, no crashes or concurrent local transitions, known cap, one second job, and small integer scope. No provider API or deployment guarantee. The maximum rule is not valid for arbitrary gauges, sums of independent increments, counter resets, or billing corrections. All provider work has finished before observation; live-progress timing and unresolved-provider risk are outside this experiment. No language-model performance or natural-language completion claim is measured. Independent code can share a model mistake. Report Codex generation, separate AI reviews, and no human/peer review.
