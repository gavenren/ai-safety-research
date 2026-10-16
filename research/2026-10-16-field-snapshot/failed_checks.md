# Failed checks and changes

The first author command used a repository-relative output path while already in the study folder. It failed before creating the analysis program. The next command could not run the missing program. The path was corrected, then the complete calculation ran. No partial result was selected or reported.

Before freeze, the design reviewer required two clarifications: each field flip and revision update occur in one atomic event; the final revision read and decision have no intervening write. Both were added before calculation. The tie rule was also made explicit in field order. No frozen input changed after freeze.

All retained result rows include negative settings. The model does not force every weak guard to fail in every setting. In particular, a last-field revision cannot produce a no-common-target error with only two fields in this model. Its wrong-at-decision errors remain separate.

During report review, the hypothesis summary was corrected to the original H3 wording: at least one modulo setting and one partial setting must have a counterexample. The summary program checks the stronger conjunction for both modulo variants and the partial variant. That check passes and implies the planned H3. No count, input, or decision criterion changed. The validator discussion was also labeled explicitly as an inference from RFC 9110, not a measured Calendar result.
