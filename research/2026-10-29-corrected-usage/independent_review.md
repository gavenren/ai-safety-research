# Independent formula check

Date: 2026-10-29. A separate Codex agent did this check. It is an AI check. No human or external peer review occurred.

## Access order and independence

The reviewer first read only `plan.md` and `plan_freeze.json`. The inherited task context also contained the plan text and proposed topic. The reviewer wrote `independent_spec.py` from that contract and froze it at 13:37:17 UTC. Its SHA-256 is `d28129ade94834eb6fbc37569511c1a963049acb50317bd950ee9e48b5c42685`.

After the main source was frozen, the reviewer read it to map field names, record order, and named control labels. The reviewer then froze `compare_independent.py` at 13:40:15 UTC, before opening any main result. Its SHA-256 is `228b7a3c1b6d85b871e5530a778a99533cf2de1ae2a41454fb22db9aa6f56326`. Neither file imports the main runner. The frozen sources were not repaired after output access.

The separate specification uses distinct report prefixes, signed prefix sums, minimum prefix sums, report positions, and greatest source revisions. It does not copy the main mutable update loop. The adapter maps these expected values to the published record format. Shared plan assumptions remain a limit on independence.

## Commands and results

Run from this study folder:

```sh
python3 compare_independent.py --results results --out independent_comparison.json > independent_run.log
python3 compare_independent.py --results reproduced --out independent_reproduction_comparison.json > independent_reproduction_run.log
```

Both commands exited with code zero. Both complete comparisons passed. There was no failed comparison or repair. Each check compared:

- All 11,664 input records and their order.
- All 69,984 primary rule cases, 408,240 state records, 338,256 delivery steps and duplicate flags, and 419,904 decision branches.
- All closure fields, errors, negative-balance flags, local balances, and excess-charge measures.
- All 78 summary rows, seven matched tables, and 11 first adverse examples.
- All 48 named and boundary rule cases, with 240 states and 288 decision branches.
- Source hashes, zero model and external-call records, reported bounds, and the total size of the seven scientific result files.

The check also verified the two reflection identities and the ordering between the clipped totals at all 68,040 input prefix positions. A prefix position belongs to one history; it is not an independent trial. Exact repeats were removed before the formulas were evaluated.

GlobalClamp overcounts in 3,170 histories. ItemClamp overcounts in 4,014. MaxReplace overcounts in 6,480. ArrivalReplace has 3,370 undercounts and 3,370 overcounts. It gives 8,078 excess-charge branches and 8,078 feasible refusals. Net and RevisionReplace are exact in every primary history. Each rule has 11,664 histories and 69,984 decision branches.

ItemClamp has a greater final total than GlobalClamp in 1,164 matched histories and the same total in 10,500. It never has a lower total. Its largest additional amount is two units. It refuses 2,104 more decision branches. ArrivalReplace and Net have equal total admission counts, but their matched decisions differ. Equal totals do not establish correct individual decisions.

## Formula checks

Let S_k be the ordinary sum after the first k distinct reports, including S_0=0. Let m_k be the minimum of S_0 through S_k. Assume the clipped balance is q_k=S_k-m_k. The next delta d gives

`max(0,q_k+d) = max(0,S_(k+1)-m_k) = S_(k+1)-min(m_k,S_(k+1))`.

The zero initial state satisfies the identity. Induction therefore gives the GlobalClamp formula for every finite prefix. An exact repeat changes neither the distinct prefix nor the balance. At complete closure, the signed deltas sum to Z, so the final overcount is `-m_final` and cannot be negative.

The same argument applies to each item's own prefix. At every shared delivery position, the sum of the two item prefix sums is the shared prefix sum. Each item prefix sum is at least its own minimum. Therefore the minimum shared sum is at least the sum of the two item minima. Negating this inequality shows that ItemClamp's total lift is at least GlobalClamp's lift. Their unclipped net sum is equal. Thus ItemClamp cannot have a lower total at any prefix.

Net is exact after complete receipt because each item's two distinct deltas telescope: `u+(v-u)=v`. RevisionReplace is exact because the received greatest revision is the declared final revision 2 for each item. These arguments require the stated report identity, delta, revision, completeness, and external finality contracts. They do not establish those contracts for a real provider.

## Scope limits

This check did not run a production billing service or a browser experiment. It did not validate source citations, human review, or remote publication. It did not perform another main experiment run. The two saved result folders were checked against the same separate formulas. Corrected charges do not measure physical compute use, and a credit does not reverse past compute. No population failure rate follows from this selected finite corpus.
