# Instructions for each live runner

Read the frozen plan and your saved assignments. Do not replace an assignment or silently repair the background history. Use a fresh temporary record for each assignment. Apply all six fixed rules, including unsafe baselines, only to these test records. Read live_rules.js into the Node environment and use its exported decide function. Save that function's actual output before any undo action.

Save your exact executed helper source and a complete chronological actions.jsonl locally. Each action needs an ID, trial token, phase, start/end time, UI arguments, tool error if any, and before/after observation IDs. Each saved field read needs a native identity, marker, raw X and Y representation, parsed x/y, and complete site-contract checks. Save private screenshots at least at final states and cleanup evidence. Do not omit failed actions or hide stale reads.

Write trials.jsonl with one record per assignment. Use this structure (add fields if useful):

    {"trial_id":"calendar-01","site":"calendar","kind":"core","rule":"...","history":"...","token":"TEMP-UNDO-...","native_id":"private","terminal_status":"valid|invalid_injection|unknown|interrupted|access_failure","reason":null,"baseline":{...},"agent":{...},"later":[{"command":"set0","observation":{...}}],"preundo":{...},"decision":{...},"decision_evidence_id":"...","final":{...},"cleanup":{...},"started_at":"...","ended_at":"..."}

Each observation object: {"x":0,"y":0,"x_raw":"0","y_raw":"Free","native_id":"private","token":"...","identity_ok":true,"contract_ok":true,"reloaded":true,"evidence_id":"UC-...","utc":"..."}. Use null for unavailable fields. Do not assert contract_ok unless each required contract field was read. Store those fields in the raw evidence and/or observation. For Notion the parent schema can be checked once and referenced; Name and identity must be checked for each record. For Calendar verify the all-day date, privacy and empty guest/reminder/other fields on each reopened record.

Only count the later commands that have verified saved states. If a prescribed phase fails, keep the row with an invalid or unknown status. A successful tool call does not substitute for saved evidence. For abstention and complete no-op, still reload and read the final record. Diagnostics have decision=null and no undo; their final field read follows the later command.

Cleanup object: {"status":"trashed|unresolved|not_created","evidence_ids":[...],"active_matches":0}. Preserve the native identity in the private log. Check that there are no active records with this run's marker after all trials. Save cleanup_summary.json with every created identity and the final search/table evidence. Keep errors even if a later saved read resolves them.

The code and plan are fixed. Save deviations separately, and tell root before a change to the study procedure. Freeze does not prevent safe inspection after an uncertain tool action. Do not issue a second ambiguous creation, toggle, add, subtract or delete.

Wait for root's explicit release with the manifest hash before scored work. Do not publish.
