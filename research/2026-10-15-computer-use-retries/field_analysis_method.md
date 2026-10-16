# Analysis method for the saved-field study

This file describes the offline analysis. It is not a new plan or a live browser policy. The original plan, assignment file, equality rules, and checker were frozen before scored actions. The field analyzer was written after that freeze. It reads saved evidence only. It makes no model, browser, connector, or network call.

## Inputs

`field_assignments.csv` lists all 20 assigned cases. The two `field_*_runner_actions.jsonl` files contain task-region observations, visible DOM value reads, native identities, actions, admissions, live checker output, decisions, errors, and cleanup evidence. The two `field_*_runner_records.json` files are JSON objects keyed by original relative filename. They contain each trial packet and supporting files. Calendar search and detail replies remain inside that bundle with their original arguments and call times. The preflight logs and record bundles are separate from scored trials. The Notion preflight log has one later image record, as the change record explains.

The public extraction replaces private record identities with stable aliases. Equality and inequality remain available. Source references and exact synthetic field values are retained. The manifest gives hashes of both original files and public extracts. Original private source files remain local. A separate agent compares original and public evidence. A public alias is not a live service URL.

## Values and evidence gates

The analyzer parses Calendar's Title, All day, dates, Show as, Visibility, Recurrence, Guests, location, conference, and Notifications from the native snapshot. It obtains Description from the recorded visible DOM textbox read, with its source snapshot reference. It reads the detailed connector event, not only the search row. It passes explicit values and missing keys to the frozen `fieldcheck.py` functions.

For Notion, it parses the native title from the DOM read and requires the same title in the banner. Marker comes from the Marker property row's value button. Verified comes from its present checkbox. The raw DOM checkbox value must agree. The empty-page prompt supplies empty-body evidence. A missing property control is unknown. A pending property editor is not a saved-field witness.

The analyzer derives count from the complete search view or unfiltered table. Notion's empty table has a disabled select-all checkbox and no data-row checkbox. This does not mean loading. A progress indicator or incomplete required controls prevents a ready count. A Notion table row's Copy link evidence must include its selected-row context menu, copy action, copy receipt, and copied identity. Calendar's recorded native URL must agree with its later native and service identities. A linked source that still has the search URL is retained as a reference departure.

The first observed identity must agree with the trial packet. A missing first identity is not filled from a later result. All required native, service, and coverage reads must follow the last relevant action. A known field error permits repair only when evidence gates pass. UNKNOWN never becomes an empty string or a false checkbox. The raw and interpreted values remain in the details output.

## Outcomes

The three phases are initial saved fields, final fields before decision, and a separate audit after decision. The analyzer compares its result with each live checker result. It checks freeze and action order, Create and correction budgets, admission before action, initial mismatch before correction, final check before decision, audit after decision, the deadline, and zero active records after cleanup. Calendar cleanup also needs a complete bounded service query with zero events.

An exposed injection is an assigned wrong field that is actually observed wrong after saving. An assigned injection without a visible native record is not an exposed error. A detected wrong value must have an initial MISMATCH result. A successful correction needs one admitted correction, the same first native ID, final and audit MATCH, and one covered record. A false completion claim requires a later supported contradiction; an unknown audit remains a separate category. All assignments remain in the denominator.

The baseline applies only the frozen title-and-count function to the same initial saved observations. It does not run a second browser policy. Its false matches are classification errors on observed wrong-field records. The experiment does not estimate a deployed policy's causal effect.

## Outputs and reproduction

`field_trials.csv` contains one row per assignment. `field_groups.csv` contains service totals. `field_details.json` contains source references, parsed values, all checks, identity witnesses, cleanup, and original decisions. `field_analysis_checks.json` records consistency and order checks. `field_summary.json` records grouped results, frozen hashes, input hashes, and failed analysis checks. Standard output is saved in `field_analysis_log.txt`.

The optional `--trials` argument is only for development. It labels its output DEVELOPMENT_SUBSET. Release analysis must omit it and include every assignment. The separate `field_independent_replay.py` uses its own parser and comparison functions. It does not import the main analyzer or frozen checker. Reproduction must compare outputs in a separate folder. It does not repeat the live trial or remove the service, account, scope, and timing limits.

## Supporting adapter code

`field_adapters.zip` preserves the final helper code and retained earlier versions. `field_adapter_manifest.json` gives original and public hashes. Private paths and record identities are replaced with placeholders. These are supporting source records, not a ready unattended program. They need the documented browser environment, initialized controls, new test data, and a fresh plan before another live run. The Notion helper records judgments; the Calendar checkpoint adapter calls the frozen checker. Earlier failed adapter versions remain as evidence and must not be mistaken for the final implementation.

For the two multi-day Calendar cases, the analyzer uses the saved visible row-ID read only when it covers every displayed row and refers to the exact covered snapshot. It keeps the heading's visible row count. It then compares the distinct rendered ID set with the bounded connector result. Missing or inconsistent mapping gives UNKNOWN. It never obtains a distinct-record count by simply replacing two rows with one.
