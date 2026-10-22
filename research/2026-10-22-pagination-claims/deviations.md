# Changes, failures, and limits

No frozen input, code, case, or outcome was changed after the first execution. Both planned full runs completed. No assertion failed, case was excluded, or unknown outcome was dropped. The raw result files match on repeat. The count explanation in the report was written after execution and is labelled as such where applicable.

Resource implementation limit: The frozen plan calls for a stop if an execution exceeds 60 CPU seconds. The implementation checks this threshold after the main calculation. It does not install an interrupting CPU limit. Both completed runs used less than one CPU second. No limit was reached. Do not treat this check as protection against a future hung process. Use an external timeout for a larger extension. This limit does not change the recorded inputs or results.

The separate audit evaluates saved evidence. It is not a third run of the experiment. Report edits after review will be recorded in the review file. No model API call occurs inside a trial.
