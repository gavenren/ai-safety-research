# Instructions for a repeated live-site run

Read live_plan.md and live_assignments.csv. Use a new token prefix, so a later run cannot match existing study tasks. Keep the same assignment order. Use one model context and one active write tab per site. Do not reuse a tab owned by a different browser session; open a new tab and verify its visible state. This startup issue occurred in the saved run and was resolved before scoring.

Use the supported browser interface for every action and observation. Do not use a scripted browser controller, hidden app state, localStorage reads, app source, or network inspection. Do not modify the site or inject faults. A helper can record an action and snapshot, but it must not implement a loop that selects policy actions. The model must inspect each state before it chooses the next allowed action.

Read the visible page and ground locators in it. Add a unique excluded warm-up task if filter controls are absent. Check that it survives reload before the first scored trial. Preserve unrelated items and browser data. Do not clear storage or delete tasks.

For each assigned row:

1. Reload, verify ready filter controls, select the assigned view, and verify zero exact matches for the token. Save the observation.
2. Record UTC immediately before the initial action. Fill the task input with the token and press Enter. Save the returned UI state. The timing interval includes these tool calls.
3. Apply only the assigned rule in live_plan.md. Record the visible exact token count, the selected view, input text that remains, and any errors. Wait24 must obtain a fresh observation at or after 24 seconds before it sends a retry. Never send more than one retry.
4. Record the decision and its UTC time before the audit changes the view. Do not repair the decision after the audit. Keep late and unresolved outcomes.
5. Select All for the audit. Count exact token labels and check that each matching task is active. Reload and repeat that check. Save both counts, both observations, and a screenshot after reload.
6. Save a result row. Then start the next assigned row. Stop admitting trials after the fixed budget. Keep every unstarted assignment in the result table.

The original run used model contexts in the existing Codex service and its supported Chrome interface. The immutable model build was unavailable. This file is a clear restatement of the runner instructions. It is not an exact transcript of every orchestration message. Raw tool observations and action records are in the two live_runner_*_actions.jsonl files. The instructions constrain the agent's behavior; the results are not spontaneous error rates.
