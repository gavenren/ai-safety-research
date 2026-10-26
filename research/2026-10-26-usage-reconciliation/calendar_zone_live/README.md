# New Calendar time-zone evidence trials

Date: 2026-10-26. This folder extends [the same paper](../report.md#prospective-calendar-time-zone-evidence-test). It tests the existing corrected adapter on new temporary production events.

Twelve events support 36 dependent local evaluations. All 12 connector-only inputs were refused. The assigned inputs gave two accepted proofs and ten refusals. Complete unmodified evidence gave ten accepted proofs and two refusals. Eight refusals changed to acceptance. Two correct controls already passed. Two actual New York zone names remained wrong for the intended Toronto target and remained refused. All 12 events were then deleted and read as cancelled.

## Repeat the public analysis

Use Python 3.13.7 or a compatible Python 3 version. Only the standard library is needed. Run from the study folder:

```sh
python3 calendar_zone_live/analyze.py --out zone_reproduced
```

Compare `zone_reproduced/summary.json` and `zone_reproduced/decisions.csv` with this folder's saved files. The two original complete runs matched byte for byte. See [reproduction.json](reproduction.json). The command makes no network call and does not create events. It checks the four frozen source hashes, repeats all saved adapter calls, compares each result, checks the declared outcomes, checks time order, and checks the public cleanup extracts.

The first local export and two dependent analysis attempts failed before complete analysis. See [deviations.md](deviations.md). The corrected exporter used a later exact read for event status. Neither the frozen checker nor any trial input changed.

## Repeat account trials

Use a new unique test marker and new events in an authorized account. Follow [plan.md](plan.md) and [cases.json](cases.json). The create parameters and action times are in [actions.json](actions.json). Use the connected create action once per event. Save the returned exact ID and URL privately. Read each exact ID with the full event read action. Copy only explicitly returned fields into the observation. Do not infer a named zone from an offset.

Before reading the editor zones, evaluate the connector-only input. Then open each returned URL in the authenticated Calendar browser. Wait for Edit event, confirm the exact title, open the editor, wait for Time zone, and confirm the title again. Open Time zone and read both zone controls. Save a private capture. Cancel the zone dialog and cancel event changes. Do not save the editor. Use the actual named labels in the unmodified evidence; only the assigned local injections change evidence.

Run `evaluate.py` with a JSON object containing `case`, `observation`, `zone`, and `phase`, and use `--input FILE --out FILE`. Valid phases in the saved procedure are `connector_only`, `assigned`, and `complete`. The actual local extraction and call helpers are [capture_inputs.py](capture_inputs.py) and [run_assigned.py](run_assigned.py). They expect the private raw files in the workspace paths shown in their source. They are operator records, not a public replay dependency. The standard public replay uses only this folder.

Read each exact ID before deletion. Delete only the new test IDs. Read cancelled status for each. Search the marker within the declared dates and follow any next-page token. Keep unexpected results unresolved. Do not purge recoverable data. New provider behavior can differ from this run.

## Evidence and limits

`observations.json` contains safe returned-field extracts. `zone_observations.json` contains safe exact-event editor extracts. The three `*_results.json` files preserve the actual evaluated inputs, local injections, outputs, and evaluation times. `cleanup.json` gives exact-ID audit results and scoped search counts. Private raw captures contain account identifiers and unrelated UI content. They remain local. Published hashes bind the extracts to retained files but do not prove authenticity by themselves or let a reader inspect private source content.

The adapter and evaluator were frozen before new writes. [Independent expectations](independent_expectations.json) were recorded separately before the evidence. A separate Codex agent checked the private-to-public links and all selected outcomes. See [independent_review.md](independent_review.md) and [audit_results.json](audit_results.json). The exact model and connector build versions were not exposed; available versions are in [environment.json](environment.json).

This test isolates named-zone evidence in one account, English labels, and two zone names. It does not estimate a production error rate or test evidence authentication, malicious input, concurrent edits, or atomic snapshots. Missing/corrupt supplied evidence is a local test condition. Two wrong saved zones are actual production records. They have correct numeric times and offsets. This is prospective validation of an existing repair, not a new algorithm.

Codex generated the study, ran the tools, wrote the code, and drafted the report. Separate agents reviewed sources and evidence. No human or external peer review occurred. No paid service, new permission, or new license was used. Sources are paraphrased and linked in [sources.md](sources.md).
