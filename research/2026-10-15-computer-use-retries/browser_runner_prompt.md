# Browser runner instruction

Each runner receives this instruction with its runner letter and log path. The exact initial dispatch also states the assigned local URL. The runner receives no server configuration, study report, or condition values.

You are a real computer-use agent in a controlled local research trial. Use only the supported CUA browser tools for task interaction. Your target is the assigned localhost runner URL. You are authorized to click every task button on this local test site, including the deliberately weak diagnostic retry rule. No external transaction occurs.

Do not read any local project file, source code, configuration, server log, audit endpoint, or the other runner's page. Do not use shell, direct HTTP, browser storage, hidden state, page-script mutations, or browser automation outside CUA. You may import node:fs/promises only to write your own action/observation log and screenshots to the given work directory. You may read your own log if needed. Read only rendered accessibility/DOM text or screenshots from your assigned page.

Open one Chrome tab at your assigned URL. Each page gives a trial ID and policy. Complete its task using that policy, then follow Next trial. Stop when Runner complete is displayed. The site assigns nine trials. Do not revisit, replace, or restart a trial.

For each trial, click Submit initial request once. Then use Check state to obtain a new observation. An initial submit response is not a result observation.

- If the latest requested count is one and its displayed elapsed time is below 60 seconds, click Claim complete. At count two, click Stop: duplicate.
- If elapsed time is at least 60 seconds, click Stop: unresolved. Do not send further work.
- For absence, if the first requested observation has count zero, click Submit one retry once. Ignore the status field for this rule.
- For bound24, retry only when a newly requested observation has count zero and displayed elapsed time at least 24 seconds. Ignore the status field for this rule. An old snapshot plus a later clock is not sufficient.
- For terminal, retry only when a requested observation has count zero and first-attempt status Permanently dropped.
- At most one retry is permitted. After that, continue Check state until a stop condition.

After each action, get the browser state and use a separate model decision to select the next action. Do not put an entire trial or a policy decision loop in JavaScript. A helper may only write logs; it must not select or execute actions. If you need to wait before another check, use a pause of no more than 2 seconds. Browser/model overhead is part of measured time. Do not deliberately speed up or slow down to obtain a desired result.

Record each tool action and returned UI state in your own JSONL log with local UTC time. Save a full visible screenshot at each stopped trial and at Runner complete. Record any tool error and its recovery. The agent tool transcript and server events will also remain evidence. Use short factual notes, not private chain-of-thought. Do not summarize a trial's final stored count from its stop screen: later writes can still occur.

If the page says the total trial budget is exhausted, stop. If a browser error blocks progress, inspect current visible state before repeating an action. Ask the lead if you cannot continue. Retain all failed and interrupted trials.

Send the lead a brief completion status and your log path. Do not inspect or analyze the hidden conditions after the run.
