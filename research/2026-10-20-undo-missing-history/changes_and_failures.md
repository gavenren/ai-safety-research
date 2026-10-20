# Changes and failed checks

The plan, configuration, and source record were frozen before the first model run. No frozen input or hypothesis was changed.

The first main analysis finished with exit code 0. All six planned hypotheses and twelve local controls passed. The false-bound failures are retained research results, not excluded cases.

Before analysis, an attempt to read a guessed prior controller filename failed because that file did not exist. The prior report was read instead. This did not remove any study case.

During publication preparation, the first browser setup did not assign its returned handle. The browser call failed with `agent is not defined`. Assigning the returned handle restored access. No upload or account change occurred in that failed call.

The independent reviewer identified a scope ambiguity in the example description. The examples use the first tight-bound case, except for the false-bound example. The report now states this. A several-histories example occurs earlier when loose bounds are included. No numerical value changed.

The independent receipt initially used the label `summary_rows` for 200 joint groups. The main summaries use 170 separate-scope rows. Both counts were correct. The reviewer renamed the former field `independent_joint_summary_rows` and explained the difference. The revised independent check passed.

The main program gained explicit checks for the frozen initial values, bound-setting names, and absent seed. This prevents unintended configuration changes from appearing to be supported. The clean rerun after this change matched all nine result files.

The first README draft used proposed command options and a receipt filename that were not part of the final independent script. These were corrected before the documented clean rerun. No failed experiment was replaced.

The first clean reproduction passed. Both commands exited with code 0 and all nine deterministic result files matched exactly.
