# Browser extension change and failure record

The plan and configuration were saved before app implementation and scored trials. The execution manifest was saved before warm-up and scored actions. The server had started before the execution manifest; no task had yet started. Its code bytes match the saved hash. No app code, condition, policy, or delay changed during execution.

The analyzer was written while trials ran, without reading their outcomes. A code review added guards for retry or claim after an observed deadline. This did not change the plan or app. A fresh reviewer checks the final data separately.

One warm-up W01 checked the page and persistence path. It is retained in the raw evidence and excluded from all 18 scored rows. All 18 scored trials started and stopped. All accepted actions resolved before the frozen audit. No trial was replaced. The server was stopped only after the evidence was frozen.

Agent logs report context recovery or compaction delays in A02, A04, B05, and B07. A02 and B05 ended unresolved. A04 made a late completion claim. All are retained. Repeated Statsig HTTP403 telemetry messages occurred. No local task request failure is recorded. This does not isolate the cause of each elapsed-time gap.

Four unsafe absence-policy claims were observed. These follow the intentionally weak policy and remain research outcomes, not data-check failures. No action resolved after stop; the planned post-stop duplicate observation was zero.

The original synthetic evidence remains unchanged. Old release, PDF, and final-review records are preserved with simulation_ prefixes. reproduction_check.json still refers to the original synthetic version and its report hash. Current report and PDF checks are separate. The exact title of the newly cited author webpage was corrected after a direct source check. No new license was assigned.
