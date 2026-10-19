# Proofs and count controls

All symbols refer to the frozen model in [analysis_plan.md](analysis_plan.md). They do not describe arbitrary website effects.

## 1. The surviving contribution

Let a be actual x and r be reference x at the same position in the command word. The reference omits the agent increment. Let d=a-r. Immediately after the agent action, d=1. An add1 or sub1 changes a and r by the same amount, so d does not change. A flip_y does not change either x. A set0 or set1 gives a=r, so d=0. Every later command preserves d=0.

Thus d=1 exactly when no set command has occurred. It is 0 otherwise. Both worlds always have the same y. Provenance control retains precisely this distinction. It subtracts 1 in the first case and makes no change in the second. Its final complete record therefore equals the reference for every finite word in this alphabet. The proof is not limited to lengths zero through five.

The proof depends on fixed commands, full operation-type history, unbounded arithmetic and one atomic undo. A later conditional branch or a parameter copied from the affected state would require a different reference execution. The proof does not supply a practical history log, concurrency control, permission check, or repeat-safe undo mechanism.

## 2. Subtract and revision guard

Subtract always changes a to a-1. It is correct when d=1. When d=0, it moves a correct pre-undo state away from its target. Every set-containing word therefore produces both a false completion claim and new damage under Subtract.

Revision guard completes only when no background command wrote x. The only allowed background command is then flip_y. Actual x is initial x+1 and reference x is initial x. Restoring initial x and preserving current y is correct. A set to the existing value still changes the revision, so it does not pass. In other cases the rule abstains and changes nothing. It therefore has no false completion claim, wrong change or new damage in the model. It can still leave the original effect unresolved.

## 3. Exact count identities

At length L, the number of histories is N_L=4*5^L. Four comes from the two choices for each initial field. There are 3^L words without a set: each position is add1, sub1 or flip_y. Thus no-set histories number 4*3^L, and set-containing histories number 4*(5^L-3^L).

Provenance control has N_L clean completions. Subtract has 4*3^L clean completions and 4*(5^L-3^L) false confirmations and new-damage cases.

Revision guard has four clean completions at every length: one all-flip word per initial record. It has 4*(3^L-1) unresolved cases and 4*(5^L-3^L) abstain-correct cases. These quantities sum to N_L.

Full restore changes y only when the background has an odd number of flip_y commands. There are four non-flip choices and one flip choice per position. The even-minus-odd word count is (4-1)^L=3^L; the even-plus-odd count is 5^L. Hence its collateral count is 4*(5^L-3^L)/2. No other rule changes y.

Value guard can complete cleanly only for a no-set word with equal numbers of add1 and sub1. The number of such words is the central coefficient of (z+1+z^-1)^L. It equals C_L=sum over j=0..floor(L/2) of L!/(j!*j!*(L-2j)!). Its clean count is 4*C_L. Every completed set-containing history was already correct and becomes wrong, so its false-confirmation and new-damage counts are equal.

For L=3, N_L=500; no-set histories=108; set-containing histories=392; Revision guard clean=4 and unresolved=104; Full restore collateral=196; C_3=7 and Value guard clean=28.

Across L=0..5, there are 15,624 histories and 93,744 rule outcomes. No-set histories total 1,456. Set-containing histories total 14,168. Revision guard completes 24 times. These identities are controls, not estimates of natural frequencies.

## 4. Equal observations can require different undo results

Consider initial (x,y)=(0,0). The agent changes x to 1. Compare one later command:

| History | Actual final record | x revision count | Reference target |
| --- | --- | ---: | --- |
| sub1 | (0,0) | 1 | (-1,0) |
| set0 | (0,0) | 1 | (0,0) |

Both histories have the same length, initial record, current record and complete x revision count. The agent's own post-action record is also the same. A rule whose only inputs are these observations must select the same deterministic result in both cases. The two required targets differ. The rule therefore cannot complete correctly in both. It can abstain, or obtain additional operation information.

This is an information limit for the declared observation set. It does not state that all recovery is impossible. Provenance control distinguishes the command types and is outside that observation set. No database product or agent model is tested by the pair.

The enumeration groups all histories by (L, initial x, initial y, current x, current y, x revision count). It records each target count and a minimum pair where targets differ. The first pair above is minimum under the frozen history order: shorter histories have no background command and no ambiguity. The independent audit checks all groups and pairs.

## 5. Model controls and scope

All six rules pass all four length-zero controls. Full restore can erase an independent y change even if the x undo is correct. Field restore preserves y but can still erase later x changes. Value equality is not evidence that the original increment still contributes to current x. Revision guard is conservative but does not infer a safe inverse from a changed revision.

The results compare concrete prescribed rules with unequal information. They do not measure an LLM's skill, latency, tool use, or production error rate. Provenance control is given stronger information by design. Its benefit cannot be attributed to model intelligence.
