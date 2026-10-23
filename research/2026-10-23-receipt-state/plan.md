# Plan: receipt history, observed state, and later edits

Date: 2026-10-23 (America/Toronto). This plan is saved before implementation or enumeration. Its SHA-256 hash and time are saved in `plan_freeze.json`. This is a finite model study, with no live account test.

## Question and contribution

When a correctly bound receipt remains valid after later edits, which rules make false state claims or add an unauthorized effect? Supply one complete regression corpus with separate history, observation, reply, and effect scores. A regression corpus is a fixed set of cases used to detect known errors after code changes. The mechanisms are established in AWS, RIFL, and HTTP guidance. This is not a new retry algorithm. The source search is saved separately.

## Hypotheses

H1. A permanent correct receipt always proves the first effect in this model, but can fail as evidence of the target at reply time.
H2. An atomic read proves state at that read. Later writes can invalidate a claim about state at the reply.
H3. A same-key replay adds no effect. A new-key repeat can add an unauthorized effect even with a fresh revision check.
H4. A read with a stated observation point, plus a historical receipt, can make correct separate claims without another effect. It does not guarantee the later target.

## Exact model and contract

One account, target, original key, and fixed payload. The record has target bit `x`, unrelated bit `y`, and non-reused integer revision `v`. Initial state is `(1-target, 0, 0)`. The first operation sets `x=target`, increments `v`, and atomically stores a permanent receipt bound to account, key, target, and payload. All histories start with this successful operation and its receipt available. No loss, expiry, identity mismatch, deletion, cache, partial read, or provider defect is modeled.

Only that original operation is authorized. No later repair authority is given. A new key identifies a new operation. Every accepted new-key effect is extra under this contract, including an assignment of the same value. Exact same-key requests replay the original receipt without another write. The receipt lookup precedes effect evaluation. A changed payload under the same key would conflict, but is outside this corpus.

Enumerate targets 0 and 1. Enumerate each of two external gaps over alphabet `set0`, `set1`, `flip_y`, at lengths 0, 1, and 2. Every external command increments `v`, even a same-value write. Gap A is after the first effect and before the observation. Gap B is after that observation and before an optional replay/new write and the reply. Every assigned A and B word runs for every rule. Reads are atomic. No external write occurs between the optional final operation and the reply. There are 2*(1+3+9)^2=338 histories per rule. The second target is a symmetry control, not an independent sample.

## Six fixed rules

All rules report the first operation as applied, from its bound receipt. Their state statements are separate from the provider response. Only R0 skips the read after A. Others observe `(x,y,v)` after A.

| ID | Name | Action after B | State statement at reply |
|---|---|---|---|
| R0 | ReceiptNow | None | Assert target holds now from old receipt. |
| R1 | ReadNow | None | Assert target holds now iff it held at the read. |
| R2 | ReadDated | None | State equality or mismatch only at the read revision; no reply-state claim. |
| R3 | ReplayNow | If read mismatched, send exact original key and payload. | Assert target holds now from original/replayed success. |
| R4 | NewKeyNow | If read mismatched, assign target under a new key. | Assert target holds now. |
| R5 | FreshCASNow | If read mismatched, assign target under a new key only if current revision equals read revision. | Assert target holds now after acceptance or a matching read; if condition fails, state unknown. |

CAS means compare and set: check and write are one indivisible step. The expected revision is the read revision, not the original pre-effect or receipt revision. Its exact non-reused counter is stronger than a general provider ETag. The conditional operation still needs authorization; a passed condition does not supply it.

## Measures, controls, and decisions

Preserve every history, state transition, receipt, observation, action, claim, and score. Measure false historical claims; false read-point claims; reply claims, false positive reply claims (said match, actually mismatch), false negative reply claims (said mismatch, actually match), unknown reply state; extra effects; target-value overwrites; unrelated-field damage; reads; dispatches; receipt hits; accepted new writes; condition refusals. A target-value overwrite means an extra write changes the target value present after all external commands. Overwrite is a subset of extra effect, not an additional case total. An external same-value assignment still increments the revision but is not target-value damage.

Score against full state histories and the single-operation authority contract. Preserve pairwise count differences. Report exact counts and conditional denominators. No p-values or sampling confidence intervals: this is a complete finite corpus, not a random sample or a website failure estimate. Do not call an unknown state a false claim. Do not label a truthful provider receipt as a false response.

Expected controls: all historical receipts stay correct and unchanged; R2 has no false read statement or extra effect; R3 has no extra effect; R4 accepts every dispatched new key; R5 accepts a dispatched new key iff B is empty; no rule damages y; target-label complement preserves counts; no-background histories have no false claims or extra effects. Check one changed target, same-value write, unrelated write, and change-and-return by hand. Independently implement an evaluator from this plan without importing main policy code. Compare all per-case scores. Make paired examples where an identical receipt or read leads to different reply truth.

## Execution and stop gate

Use Python standard library only. No stochastic models, API calls, credentials, live mutations, or paid compute. No seed is needed. Cap the model at this grid, 10,000 outcomes, and 60 local CPU seconds per run. Save runtime and versions. Stop and record a plan change if the model, score, or rule must change. An implementation bug fix does not change the model; record it. Publish only after reproduction, independent comparison, source/claim review, privacy/rights checks, and remote verification. A negative result is valid.

## Scope

This extends the October 22 receipt-binding study by fixing identity and payload and adding later writers. It differs from October 16 mixed reads (reads here are atomic), October 17 repair dependencies (no dependency inference), and October 18 receipt retention (memory here is permanent). The design does not establish real service guarantees, real agent skill, lasting completion, or permission to overwrite later work.
