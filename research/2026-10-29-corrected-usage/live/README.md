# Production website test

Date: 2026-10-29. This folder extends the [same paper](../report.md). It does not replace the original simulation.

The test used temporary empty Google Drive folders and private Free events in the owner's primary Google Calendar. Connector tools created 25 records. Browser actions saved 12 source corrections and 18 output names. Another 18 decisions made no output save. Test credits, source revision labels, report order, exact replay, and period closure were controlled study inputs. No actual billing system was tested.

## Repeat the saved-data analysis

Use Python 3.13.7 and its standard library. The unchanged parent `run_study.py` must remain one folder above this folder. Run from this folder:

```sh
python3 controller.py observations.json rerun_a.json
python3 controller.py observations.json rerun_b.json
cmp decisions.json rerun_a.json
cmp rerun_a.json rerun_b.json
python3 check_results.py
```

Every command must exit with code zero. The last command must report a passed check. `cmp` is a file comparison command. The saved `reproduction.json` records the original analysis and two re-executions. The repeated analysis uses saved data; it does not perform a second website experiment.

## Repeat the website procedure

Use an account whose owner authorizes temporary records. Read `plan.md` first. Use a new unique marker and preserve its mapping to each provider ID privately. Create one private Drive parent and twelve child folders. Create twelve private Free Calendar events with no other guests, reminders, recurrence, or meeting link. Six records per service are the source A/B pairs. The other six are output markers, one per rule. The original interval was 2026-11-04 12:00-12:05 at the requested America/Toronto zone. The evidence audit verifies the numeric interval and browser Free/Private fields; it does not certify a named saved zone.

Read each exact source ID after revision 1. Save revision 2 by changing its name in the production browser. Reopen the record, check its name, and read its exact ID again. Do not continue with a conflicting or unknown source. Keep the initial observation before the correction. Do not create a second record to represent revision 2.

For each case, supply the captured values in the declared local delivery order. Use a fresh local rule state. All four reports and the researcher's period closure are required. Read each output marker before its decision. An admission permits one browser rename to the declared case name. A refusal permits no Save action. Read all exact output IDs after the case. Save this evidence before the next case reuses the markers. The original browser helper used Drive's Rename form and Calendar's event editor. It checked the existing title before each Calendar save. The observed event link identifies the exact editor; no other event should be selected.

Website controls can change. Follow the current visible controls and save each actual action. Do not retry a write after an uncertain response. First read the exact record. Separate page navigation from a successful save. A name shown while a page loads can be stale. Wait for the expected record's own name before checking its path or fields.

After the tests, cancel only the exact new Calendar IDs and check their cancelled state and the bounded active marker query. Move only the new Drive parent to recoverable Trash. Reopen each exact child URL and check its own name plus the Trash and parent path. Do not empty Trash. A successful rerun can have different provider IDs and times. Do not expect identical website logs.

## Evidence and limits

`observations.json` contains all 24 source versions. `decisions.json` contains all 36 rule decisions and 192 prefix states. `actions.json` joins each decision to its before/after saved names. `browser_actions.json` records the 12 source saves, 18 output saves, and 18 no-save decisions. `browser_evidence.json` contains test-only extracts and private-source hashes. `cleanup.json` records the bounded cleanup evidence. `environment.json` gives tool and runtime limits. The three freeze files preserve the plan and accounting implementations.

`independent_checks.json` and `independent_review.md` cover the private source audit and formula comparison. `portable_checks.json` and `check_results.py` check the released data. `output_checks.json` and `output_review.md` cover the output and cleanup audit. `changes.md` retains failed checks and navigation issues. `source_notes.md` gives search terms, rights, dates, and read scopes.

Private exact IDs, account addresses, unfiltered page content, and screenshots remain local. The released extracts permit analysis and claim checks. They do not let a reader independently query the removed private test records. A source hash links an extract to retained raw evidence; the hash alone does not prove a provider action.

There are only six chosen service cases and 36 matched rule decisions. They are not independent population samples. The source records and output markers were shared across rule comparisons. No confidence interval or production error rate is claimed. The rules were applied by an instrumented Codex browser workflow, not by an independent unsupervised agent benchmark. No new licence is assigned. Codex generated this extension. No human or external peer review occurred.
