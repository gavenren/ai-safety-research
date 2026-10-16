# Independent design review

Date: October 16, 2026 (America/Toronto).
Status: Design review before the calculation.

The six policies can be compared on one fixed history and decision point. Counts describe only the finite history set. A ratio from one read budget must not be compared with a ratio from another budget as a causal effect. A rejection is not a false safety claim.

The state required for exact merging is the current field vector, whether the target has ever occurred, whether all field reads have matched the target, total write count, and write count for the last field. Total write count must remain exact, rather than only modulo four, to support minimum-write witnesses. The observation index is fixed by the dynamic-programming stage. The start revision is zero. Histories with identical states at the same stage have the same possible future outcomes.

Two details need explicit text in the frozen plan: a flip and all relevant revision updates occur in one atomic event; no write occurs between the final revision read and the decision. Without those premises, revision equality does not prove the stated final-state result.

For two fields with no all-one state, a target-valued read of x requires state (1,0); a target-valued read of y requires state (0,1). Each adjacent pair in x,y,x,y,... needs at least two bit flips, because one flip cannot join these vectors, and a path through (1,1) is excluded. There are 2r-1 disjoint intervals between the 2r reads. Thus at least 2(2r-1) flips are needed. A path through (0,0) in each interval meets the bound when b=2. This proof does not apply to a merely wrong final state.

The partial counter can reject writes to the last field while missing changes to other fields. Its no-common-target set may be empty for two fields, because one other field cannot alternate around a fixed last field equal to one. Three fields allow the first two fields to alternate while the last field stays at one. Empty settings must remain in the result tables.

The contribution is a numerical and logical audit of declared finite cases. Revision guards and atomic snapshots are established methods. The study must not claim a new snapshot algorithm, a provider fault, a browser trial, or a production failure rate.

Codex wrote this review. It is a separate agent review, not human or peer review. No analysis was run for this file.
