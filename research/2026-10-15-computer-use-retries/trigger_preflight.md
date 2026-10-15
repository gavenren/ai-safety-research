# Excluded feasibility checks

Date: 2026-10-15. These three folders are not scored trials.

P01 used a writer tab in All and a second observer tab in Documents. The observer showed an explicit Documents filter and No matching results before the write. After the writer created RETRY-PREFLIGHT-P01, its later state contained an exact-name creation receipt and one folder row. The observer still showed Documents and No matching results. A reload kept the Documents filter. The later recorded read was at 17.099 seconds from the first Create request. It still showed no matching results. Removing the filter showed one P01 row.

P02 used the same two tabs with the observer in All. The writer created RETRY-PREFLIGHT-P02. The first reload state was incomplete (New disabled). A later ready state showed one P02 row and one P01 row, with No filters applied. This supports using a reload followed by a usable-state check for scored observations.

A separate connector read with capacity 100 returned exactly two records, one per token. The four scored block folders were created later. No duplicate was made in feasibility.

The preflight logger used a fixed id P01 for the whole session. P02 phases explicitly start with P02 and contain its token. The scored logger must pass trial identity explicitly. The first two tab loads and some menu actions were not logged in the preflight JSONL. Preflight is a workflow check, not a timed comparison.

The workflow was selected because it kept a written folder outside the observer filter. This is purposeful case selection. It cannot estimate the frequency of this condition in normal use.

P03 corrected the timing gap. A first ready Documents view after reload was empty at 9.389 seconds. A writer read had the exact P03 success receipt at 9.575 seconds. The later reload at 41.834 seconds was loading and was not treated as zero. A ready Documents view at 72.973 seconds still had No matching results. Removing the filter and reloading produced a ready All view with one P03 row at 88.967 seconds. These times include other task work. They are not estimates of service delay. A P03 filtered image is retained.

Correction: the lead first described the P01 check as after 24 seconds in a progress message. Its saved elapsed time is 17.099 seconds. This was corrected before any scored trial. The old phase name after_24_reloaded is retained as raw evidence; it is not a valid timing label. P03 supplies the required delayed feasibility observation.
