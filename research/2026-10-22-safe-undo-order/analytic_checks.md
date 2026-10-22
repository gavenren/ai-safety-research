# Analytic checks

These are post-run explanatory derivations. They did not select the corpus or change the frozen hypotheses. They check the observed counts by a different argument.

## Number of conditions with a safe path

In the three-bit model, a full path visits one state with two ones and one state with one one. Call these the upper and lower states. There are three in each group. Each upper state has two permitted lower successors. The six possible upper-to-lower edges form a cycle.

A path exists exactly when a selected upper state and a selected lower state share an edge. Count conditions with no such edge, by the number of selected upper states:

| Selected upper states | Upper choices | Permitted lower subsets | Conditions without a path |
| --- | ---: | ---: | ---: |
| 0 | 1 | 8 | 8 |
| 1 | 3 | 2 | 6 |
| 2 | 3 | 1 | 3 |
| 3 | 1 | 1 | 1 |

The total is 18. Thus 64 - 18 = 46 conditions have a safe path. Each occurs under six priorities, so complete search has 276 valid completions and 108 refusals.

## Fixed order

For any priority, the fixed path uses two specific intermediate states. Both must be selected. The other four states are free choices. There are 2^4 = 16 valid paths among the 64 conditions. Therefore 48 fixed paths cross an invalid state per priority. Six priorities give 96 valid completions and 288 paths with a violation. Every fixed path still reaches 000.

## Greedy rule

Fix one priority, for example abc. Let U1, U2, U3 be its candidate first states in that order. If all three are absent, there are eight choices of lower states. These eight conditions cause refusal before mutation.

If Ui is the first selected upper state, the greedy rule can fail only when both its lower neighbors are absent. The one lower state that is not a neighbor remains optional.

| First selected upper state | Partial stops | Avoidable dead ends |
| --- | ---: | ---: |
| U1 | 8 | 3 |
| U2, with U1 absent | 4 | 1 |
| U3, with U1 and U2 absent | 2 | 0 |

For U1, its two lower neighbors are absent. The optional third lower state and U2,U3 give eight conditions. A different safe path exists when that lower state is present and at least one of U2,U3 is present: three conditions. For U2, U1 is absent. The optional lower state and U3 give four conditions; exactly one has both present and is avoidable. For U3, no other upper state is present, so neither partial stop is avoidable.

Thus one priority gives 8 refusals, 14 partial stops, 4 avoidable dead ends, and 64 - 8 - 14 = 42 valid completions. Six priorities give the observed 48, 84, 24, and 252 counts. Relabeling the fields maps each priority to every other priority, so these totals do not depend on the chosen names.

## Why three bits are the first case in this model

For one bit, the single allowed step reaches the valid goal. For two bits, any valid first step leaves one bit set. Clearing it reaches the valid goal. If no valid first step exists, no safe path exists. Thus greedy cannot create an avoidable dead end for one or two bits.

For three bits, valid states {000,010,011,101,111} give a witness. Priority bac clears b first and reaches 101. Its two remaining possible successors, 001 and 100, are invalid. But the initial state has the safe path 111 → 011 → 010 → 000, with actions acb. The model's prohibition on setting a cleared bit back to one is essential to the dead-end claim.
