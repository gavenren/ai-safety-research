# Technical paper analysis plan

Date: 2026-10-22. Saved before simulation implementation or execution. Literature searching and selection of a coverage-aware accounting argument preceded this plan; this is not a preregistered empirical study.

## Question
When can authenticated accelerator activity support a defensible interval for total compute, and how does missing evidence alter that interval?

## Scope and method
Develop a proposed receipt protocol and elementary conditional accounting propositions. Distinguish accepted measurements, enrolled device-time gaps, and devices outside the enrolled inventory. Specify a fixed operation-count convention and separate workload attribution from physical metering. Review primary research, IETF specifications, and vendor documentation; no claim of exhaustive literature coverage or demonstrated novelty.

## Synthetic demonstration fixed before execution
Use 100 devices and 100 one-unit epochs. Twenty devices have capacity 400 abstract operation units per epoch; eighty have capacity 100. Load percentage is 10 + ((17 * device + 13 * epoch) % 81), so each true amount is integer and at most its stipulated capacity. A recorded amount is true amount plus ((device + epoch) % 3) - 1. The assumed error bound is 2 units per observed device-epoch. No physical hardware measurements enter this example.

Compare complete reporting; 500 uniformly sampled missing records using seed 20261022; 500 highest-capacity missing records; 500 highest-activity missing records; and all 2,000 high-capacity device-epochs missing. Rank ties by device and epoch. Report observed totals, lower/upper bounds, time coverage, capacity coverage, interval width, and oracle truth. Then enumerate every missingness mask for a separate 12-record instance with the same load/meter rules and verify containment. This enumeration checks implementation arithmetic under stipulated assumptions, not hardware or cryptographic soundness.

## Additional checks
Show that a missing-interval capacity bound remains valid when reports are withheld adversarially. Construct a false-meter example to demonstrate loss of validity if the assumed error bound fails. Show an unknown external-inventory budget cannot produce a finite global upper bound. Check threshold decisions at an explicitly synthetic threshold. No p-values or real-world detection probabilities will be estimated.

## Outputs
technical.md, technical_simulation.py, technical_results.json, technical_sources.md, technical_references.bib. Any post-plan change will be recorded here.

## Changes after saving
None at initial save. After the first run, reviewer feedback requested direct validation of positive exceedance and equality boundaries. Four deterministic classification checks were added: [10,20] at thresholds 20, 10, 9, and 19. The five simulation scenarios and their reported values were unchanged. These checks are post-plan validation, not additional empirical results.
