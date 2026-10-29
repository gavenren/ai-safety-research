# Plan: signed corrections and nonnegative balances

Date: 2026-10-29, America/Toronto. Save this plan before implementation and execution.

## Question and contribution

Can forcing every partial balance to be nonnegative corrupt the final accounting of delayed signed corrections? How does clipping per item differ from clipping the shared total?

The October 26 study assumed monotone cumulative totals. The October 27 study added counter restarts but excluded corrections. This study uses corrected charges for completed work. The final charge can be lower or higher than the initial report. It does not measure physical compute, and a credit does not undo past resource use. The contribution is a declared finite comparison corpus, matched decisions, full traces, and separate formulas for known accounting rules. No new protocol or global novelty is claimed.

Primary source search before selection found Google Cloud's append-only correction documentation and Stripe's duplicate and unordered event delivery documentation. These support the motivation, not the exact combined test protocol. Neither service is tested. Source scopes and further related-work checks will be saved separately.

## Fixed contract and inputs

Two completed charge items A and B have independent nonnegative integer charges. Each emits revision 1 with initial value u and revision 2 with authoritative corrected value v. All four values uA,vA,uB,vB are in {0,1,2}, giving 81 settings. A report includes its unique event ID, stable item ID, revision, replacement value, and signed delta. For revision 1 the delta is u; for revision 2 it is v-u. These are two equivalent encodings supplied to all rules. Old reports are not false transport records; they retain their earlier values. No new work occurs during delivery. The true final charge is Z=vA+vB.

IDs A1,A2,B1,B2 are unique and bind all fields. Exact repeated deliveries preserve all fields. Use three multisets: A1,A2,B1,B2; A1,A2,A2,B1,B2; A1,A2,B1,B2,B2. Enumerate all distinct permutations, sorted lexically. These give 24,60,60 orders, or 144 in total. Cross with the 81 settings for 11,664 histories per rule. Do not label identical copies separately.

All six rules ignore an already seen event ID before updating any amount. Initialize zero balances, no seen IDs, and revision zero for both items. Rules can use only reports already delivered. No field can reveal a future final value to a rule. A separate scorer has the full input.

## Six rules

- Net: add each distinct signed delta to one shared total. Temporary negative totals are retained.
- GlobalClamp: after each distinct delta, set the shared total to max(0, old total + delta).
- ItemClamp: apply that clipping separately to the reported item's balance, then sum both balances.
- ArrivalReplace: replace the reported item's balance with the value of the last distinct delivered report, then sum.
- MaxReplace: retain the greatest delivered replacement value for each item, then sum.
- RevisionReplace: replace an item's balance only when its source revision is greater than the stored revision, then sum. Source revisions are trusted and do not wrap or collide.

Keep the seen IDs and every rule-relevant balance and revision after each event, plus the initial state and duplicate decision. Net and GlobalClamp need only q; the other rules retain two item balances. Only RevisionReplace retains revisions. Every state records q and the sorted seen IDs. Exact copies do not change these fields.

## Closure and decisions

No decision is made while reports are arriving. After all delivery, a trusted external closure declaration states that revision 2 is final for both registered items and no further correction can arrive for this accounting period. Require all four unique reports as a common completeness condition. The report set alone does not prove external finality. All primary histories meet both conditions.

After closure, evaluate six independent hypothetical job decisions for each history and rule: C in {Z,Z+1,Z+2}, b in {1,2}. Admit iff the closure conditions hold and q+b<=C. An admitted new job incurs exactly b units of charge. It has no correction. Actual final charge is Z+b if admitted, otherwise Z. These are independent branches, not six sequential jobs. There are 69,984 branches per rule and 419,904 across six rules.

## Hypotheses and measures

H1: Net and RevisionReplace are exact after complete closure for all primary histories. They have no excess-charge admission or feasible refusal.

H2: GlobalClamp and ItemClamp can overcount even after exact duplicate filtering and complete receipt. They cannot undercount final charges. ItemClamp's final q is at least GlobalClamp's on each matched history.

H3: MaxReplace overcounts when an initial value exceeds its corrected value. ArrivalReplace can undercount or overcount when old reports arrive late.

H4: Clipping changes order independence. Let S_k be the sum of distinct delivered deltas through step k, S_0=0. GlobalClamp has q_k=S_k-min(0,min_{j<=k}S_j). Thus final error is the magnitude of the lowest negative prefix. ItemClamp has the sum of those lifts on each item's own prefix. Prove these identities and compare every prefix against a separate implementation.

Record final q-Z, under/exact/over counts, largest positive and negative error, any negative intermediate q, and first adverse examples in enumeration order. Record each branch's admitted flag, final charge, excess max(0,final charge-C), feasible refusal (refused and Z+b<=C), and local balance C-q-b if admitted, C-q otherwise. A negative local balance is not the same as excess actual charge. Report case and branch denominators. Group by duplicate type and by correction directions for both items; groups overlap. Compare every rule with Net and compare ItemClamp with GlobalClamp, including q gaps and matched decision changes.

## Controls and checks

Six named controls repeat selected primary histories: early credit (2,0,0,0; A2,A1,B1,B2), late original after upward correction (0,2,0,0; A2,A1,B1,B2), offset across items (2,0,2,2; B1,A2,A1,B2), equal revisions (1,1,1,1; A2,B2,A1,B1), zero values (0,0,0,0; A1,A2,B1,B2), exact replay (2,0,0,2; A2,A2,B2,A1,B1). Input tuples are uA,vA,uB,vB. These are not extra independent samples.

Two separate boundary controls use (2,0,0,2). Missing-report control delivers A1,A2,B1 and has an external finality declaration but fails the common completeness gate. Open-period control delivers all four reports but has no external finality declaration. Every rule refuses all six branches in each control. These controls do not test partial-data utility or the ability of a real service to provide finality. Do not pool them into primary error counts.

Freeze an independent formula specification before it reads main implementation or results. Prefer prefix sums, source revision selection, and final report positions to copying the main loops. Freeze a schema adapter before reading outputs. Compare every state, duplicate flag, error, branch, summary, matched comparison, and control. Run the main experiment twice and compare deterministic scientific files byte for byte. Keep failures and amendments.

## Resources and reporting

Use local Python standard library and invented values. No seed, external account, paid compute, model API, installation, or network inside the experiment. Set a 120 CPU-second operating-system limit and periodic checks at 300 wall seconds and 200 MB output per run. Record actual times and versions. Save deterministic compressed JSON-lines traces, all generated inputs, summaries, paired outcomes, and controls. Peak memory is not measured unless a specific reliable method is added before execution.

This is a finite simulation, not a live billing, agent, financial, or production website test. No population confidence interval or significance claim follows. Assumptions include unique truthful IDs, correct signed deltas, trusted revisions, complete closure, fixed prices for the new job, and exact integers. No crashes, conflicting reports, new item, missing primary report, or future correction after closure is included. State Codex roles and actual human review status, use checked primary sources with attribution, assign no new license, complete separate reviews and relevant NeurIPS checklist checks, and verify every published file.
