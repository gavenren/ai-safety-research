# Design review

Date: 2026-10-29. Reviewer: a separate Codex agent. No human review occurred.

## Decision and scope

No material contract, counting, or hypothesis error was found. The frozen plan is suitable for the stated finite comparison. This review read only `plan.md`. It did not read a main implementation or results and did not run an experiment. This is a design review, not a result check or publication receipt.

## Contract and comparison

The target is the authoritative corrected charge for completed work. A lower charge does not erase physical compute or another irreversible effect. The plan states this limit. The six rules receive the same reports, event IDs, and closure conditions. Each report includes both a signed change and a replacement value; the compared rules use different stated parts of that information. These encodings are a research contract, not a claim that one named provider supplies this exact combined record.

All rules filter exact repeated event IDs. Replayed old events therefore have no further effect. ArrivalReplace means the last distinct delivered report, not the last physical delivery. This detail must remain clear in the report and implementation.

No rule makes a job decision on an incomplete prefix. The external declaration of finality and the requirement to receive all four report IDs are separate conditions. A complete report set does not itself prove that no later correction exists. The plan correctly identifies this as an assumption. It imposes the same full-history gate on every rule, although RevisionReplace could use less history under a different contract. Thus the study does not compare minimum data requirements or partial-data utility.

The six budget branches use the known final charge to select their test budgets. This is a controlled boundary test. It is not a forecast of a live budget. The scorer can know final charge; a rule must not read any future report value. Net may have a negative partial sum. The plan retains it as partial accounting evidence and does not use it to admit new work.

## Counts

There are 3^4 = 81 numeric settings. Four distinct reports give 4! = 24 orders. Each five-report multiset has one repeated ID and gives 5!/2! = 60 orders. Thus there are 144 orders per numeric setting and 11,664 histories per rule. Six rules give 69,984 primary rule cases. Each rule has 11,664 times 6 = 69,984 independent decision branches. Across six rules, there are 419,904 branches. These branches are not sequential jobs or independent empirical samples.

The six named controls all occur in the primary corpus. They should be presented as repeated examples. The two boundary controls have different closure conditions and must remain outside the primary error totals. The control called “equal revisions” has equal values at two different revisions. The report should call it “equal values at both revisions” to avoid implying revision-ID reuse. This is a label clarification, not a change to inputs or rules.

## Conditional formulas

Let a duplicate delivery contribute zero. Let S_k be the sum of distinct delivered changes through step k, with S_0 = 0. Define m_k as the minimum of zero and all S_j for j at most k. The recurrence q_k = max(0, q_(k-1) + d_k) has the solution q_k = S_k - m_k. This follows by induction: substitute the prior solution and use min(m_(k-1), S_k) for the new minimum. At complete receipt, S_N = Z. Therefore GlobalClamp's final overcount is -m_N. It cannot undercount final charge under this contract.

For ItemClamp, apply the same result to each item's changes. Its final overcount is the sum of the two nonnegative lifts. At any global prefix, each item's partial sum is at least its own minimum over all prefixes. The minimum of the shared sum is therefore at least the sum of the item minima. The shared lift is at most the sum of the item lifts. Hence ItemClamp's final q is at least GlobalClamp's on every matched history. This proves the proposed ordering without an empirical frequency claim.

Net telescopes to vA + vB when each delta appears exactly once. RevisionReplace retains revision 2 for each item after complete receipt, so it has the same total. MaxReplace retains max(u,v) for each item and thus overcounts exactly when at least one u exceeds its v. ArrivalReplace can retain revision 1 if it arrives last. Depending on the direction of the correction, that can make the total too small or too large. Item-level errors can also offset, so the scorer must compare the summed q with Z rather than infer a total error from one item's direction.

## Required result checks

The main implementation still needs checks for duplicate immutability, seen-ID sets, all stored balances and revisions, closure flags, and every saved decision branch. The independent formulas must cover negative prefixes and first adverse examples as well as final totals. The report must retain rejected hypotheses if they occur. The design review does not establish source verification, actual resource use, reproducibility, absence of private data, or remote publication.
