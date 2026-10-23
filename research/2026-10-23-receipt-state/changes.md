# Changes and execution notes

The question, corpus, six rules, and measures remained as frozen in `plan.md`. No exploratory trial was added.

1. The first main run passed all seven controls. Its actual output remains in `initial_run.log`.
2. CPU-time measurement was added after that run. The first instrumentation recorded wall time only. The run was repeated with the same model. This changed environment and timing records only. The final actual output is `run.log`.
3. The independent evaluator was written without reading or importing the main implementation. An output-name adapter was added after its first run. Its early hash in `independent_freeze.json` therefore differs from the final code hash. No independent policy rule changed. The comparison and repeat records are included.
4. The source reviewer removed the unused Google Calendar bibliography entry. Its read scope remains in the source search log.
5. The final reviewer requested the phrase “130 conditional write requests” for R5. The report now uses that phrase to distinguish attempted requests from 10 accepted effects. No result changed.

No experiment, comparison, or material publication check failed. A source reviewer initially used the wrong freeze filename and then read the correct one. The publication browser setup initially used an undefined local handle; setup was corrected before any upload. Neither event changed study evidence.

The model uses no language-model API call or live website action. The surrounding Codex session performs design, coding, writing, and review. The exact backend model build is not exposed by the available session interface and is not claimed. Python and platform versions are in `results/environment.json`.
