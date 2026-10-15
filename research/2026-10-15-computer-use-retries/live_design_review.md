# Design review for a real website test

Date: 2026-10-15. This is a proposed extension of the existing retry paper.
The lead later selected public test websites, then revised the selected tasks to TodoMVC.
The first section applies to the latest choice.
The earlier designs remain below as design history. They are not executed tests.
This review used the saved paper, README, browser plan, and browser review files.
No account was opened. No record was created. No trial was run. Nothing was published.

## Latest update: TodoMVC view-scope test

The lead proposed **60 trials = 2 hosted implementations x 2 list views x 5 rules x 3 repeats**.
The list views are All and Completed.
The five rules are No retry, Absence, Wait24, Closure, and Scope-aware.
The task is to create exactly one active task with a unique test token.
Scope-aware changes the list to All and checks the token before any retry.

This is a valid small test of **view scope**, if the selected sites pass setup checks.
A Completed view intentionally excludes active tasks.
It is not a stale read, an uncertain server commit, or an injected delay.
Two TodoMVC hosts provide two implementations of one workflow, not two independent application domains.
Keep this result separate from the local delayed-write experiment.

The TodoMVC specification defines creation by Enter, active and completed filters, and storage in localStorage.
It also states that the footer is hidden when no tasks exist.
This supports a fixed completed seed task when a filter must be selected before a trial.
Exclude the seed from all token counts.
The active-item counter is not a substitute for an exact token check.
Source: [TodoMVC application specification](https://github.com/tastejs/todomvc/blob/master/app-spec.md).

The specification is not proof that a live implementation complies.
The lead reported that the live React and Vue warm-up tasks disappeared after reload.
These are reports from the lead's UI checks; this reviewer did not operate the UI.
Keep both failed setup checks and the plan amendment.
Do not score those attempts as trials if their exclusion was fixed before scoring.

The source review supports one further candidate: [official KnockoutJS TodoMVC](https://todomvc.com/examples/knockoutjs/).
Its [served app source](https://todomvc.com/examples/knockoutjs/js/app.js) reads and writes `todos-knockoutjs` in localStorage.
Its write function has a 500 ms rate limit after changes stop.
Use at least a one-second quiet interval for the setup reload check.
That interval is a setup choice, not a general timing bound.
The source returns only completed tasks in the Completed view.
Source SHA-256: `fc01edc03a90a4e7569755bc3b8ab7b5015768980cdfebfaa4251f55c894a698`.

The [Playwright TodoMVC demo](https://demo.playwright.dev/todomvc/) source reads an array from localStorage and writes the full array on changes.
The lead reported successful reload persistence in its warm-up.
Microsoft's [test generator guide](https://playwright.dev/docs/codegen) uses this demo for UI test recording.
This is primary evidence that the demo is intended for this kind of small UI test.

The current TodoMVC repository states that its code uses the MIT license unless otherwise stated.
Retain notices if source is redistributed.
Do not apply the Playwright repository license to every third-party bundle in the demo.
Sources: [TodoMVC repository](https://github.com/tastejs/todomvc) and [TodoMVC license](https://raw.githubusercontent.com/tastejs/todomvc/master/license.md).

The runner must have the same visible controls under every rule.
The rules may specify different procedures for those controls.
If only Scope-aware may change the filter, describe this as a comparison of supplied procedures.
Do not claim that the result measures spontaneous model judgment with equal evidence use.
If another rule changes the filter, retain the trial and score adherence from the saved rule text.
Do not silently restore a filter to force a duplicate.

Closure still has no documented terminal-failure signal in these apps.
It therefore cannot retry an unseen task under its stated trigger.
No retry has the same retry behavior.
Wait24 cannot solve a view that excludes the task for any length of time.
These facts explain the expected mechanism; they are not observed outcomes until trials run.

Use one active write tab per origin.
Tabs on one origin share localStorage, and each app can retain an old task array.
A later write from an old tab can replace newer storage state.
A new tab is not an isolated trial.
Reload before each new trial and count exact unique tokens.
Never clear unrelated storage or remove unrelated tasks.
Finish each audit before another task on that origin can change storage.

For each trial, save four count states where possible:

1. Before submission: All contains zero matches for the new token.
2. After submission: save the selected view and its visible token count.
3. After the runner stops: switch to All and count exact token matches.
4. After reload: restore All if needed and count exact token matches again.

The post-stop filter change belongs to the observer, not the runner's task time.
Do not use the observer's result to repair a runner claim after the fact.
Record the result before reload even if the reload later fails.
This prevents a storage loss from hiding a duplicate that was already visible.
Report **duplicates before reload** and **duplicates after reload** as separate fields.
Report reload loss and failed audits separately.

Name the persistence outcome **task retained in this browser after reload**.
Do not claim remote storage, server durability, or protection against browser-storage loss.
A success toast, active-item counter, or filtered empty list does not by itself prove an exact task count.
The All-view audit must also check task state: the requested task must remain active.
Turning the task into a completed task to reveal it changes the goal.

Keep all 60 assigned rows, all failed setup checks, and all deviations.
Use counts by view, rule, implementation, and repeat block.
Balance rule order before scoring.
Three repeats per cell are a small sample; report raw counts and times.
Do not infer a field error rate or claim that 24 seconds is safe.
The useful claim is that a correct empty result from an incomplete view can be insufficient for a retry decision.

Source-review details:

- The served React bundle had no `localStorage` string. Hash: `6197ad9358985fb3f745aef3fca9abbe2fc7f0cd35cd4525cb8570107ae6b78a`.
- The served Playwright bundle had explicit storage reads and writes. Hash: `0e639b342c23262b71c7f41d353aa7d16a69ea0563ceeda1ab7f04beb870b07b`.
- The official home page linked KnockoutJS, React, Vue, JavaScript ES6, and TypeScript React at the checked paths.
- The Vue and JavaScript ES6 bundles also had no `localStorage` string. This source check alone was not treated as proof of loss.
- The older TypeScript React bundle used localStorage, but it was very similar to the Playwright demo. KnockoutJS offers more implementation variation.
- The web tool could not read the Knockout app source or README. A direct HTTPS source read succeeded without an account.
- No source code was executed, no storage was read, and no browser control was used by this reviewer.

## Update: the selected public-site design

The lead proposed **48 trials = 3 workflows x 4 rules x 4 repeats**.
The workflows are UI Testing Playground AJAX, UI Testing Playground Client Side Delay, and The Internet Add/Remove Elements.
This is three workflows on two public test websites.
Call the study an **external live test-site UI pilot**.
The sites are outside the local test server, but their tasks are constructed demonstrations.
Do not call these production account tasks or natural production faults.

The returned live HTML was checked on 2026-10-15.
Each action adds an element to the current page:

- AJAX requests `/ajaxdata`, then appends a result paragraph.
- Client Side Delay schedules a 15-second timer, then appends a result paragraph.
- Add/Remove Elements immediately appends a Delete button.

These are page effects. The checked actions do not create a stored server record.
Use **duplicate result elements**, **visible result count**, and **page effect after stop** as outcomes.
Do not use **duplicate durable records**, **stored write**, or **persistence failure** for this extension.
The Add/Remove source is available in [The Internet source file](https://raw.githubusercontent.com/saucelabs/the-internet/master/views/add_remove_elements.erb).
The live Playground source was read from [AJAX](http://uitestingplayground.com/ajax) and [Client Side Delay](http://uitestingplayground.com/clientdelay).

The 48-trial design can answer two useful questions:

1. Can each instructed rule be used with the evidence that these pages provide?
2. When a fresh empty view occurs after the first click, does an absence retry produce extra result elements?

The immediate task is a positive control for observation and count accuracy.
It does not expose the same delay as the other two tasks.
Report its results separately from the two delayed tasks.
Report the number of trials with an actual empty post-click observation.
Tool or model delay can cause the first observation to miss the 15-second window.
Retain such trials and mark them as unexposed.

Neither checked Playground handler provides an attempt-specific final failure signal.
The spinner becomes hidden when the first callback completes.
If two callbacks are pending, that hidden spinner does not prove that the second callback has finished.
Closure and No retry therefore have the same permitted retry behavior in these tasks.
Call this a result about rule availability, not a four-way test of distinct recovery mechanisms.
Wait24 remains a chosen wait period. Network delay and timer scheduling have no proved 24-second upper bound.

Keep a separate page for each running or stopped trial until its audit is complete.
Do not reload, navigate, close, delete elements, or reset a page before its final count check.
Those actions can erase results or cancel callbacks.
Freeze a follow-up horizon before execution; 60 seconds after the last click is a practical choice.
A trial that stops later needs a count check at stop as well.
Report counts at the saved times and report the horizon.
Do not claim that a finite check proves no future result can appear.

An independent observer can count the current page elements and inspect screenshots.
That is a separate check of page state, not an independent server audit.
If screenshots and read-only DOM counts are both used, state both observation methods.
Do not describe the study as pixel-only.
Save each action start and return time, each observation time, and each count.
Record browser background throttling and shared host limits if they apply.

The site owners describe these projects as suitable for automation practice.
This supports the proposed small test through normal page controls.
It does not permit high-load testing.
Run no more than one active AJAX trial at a time and keep the two-click cap.
The Playground project names Apache License 2.0.
Preserve source attribution and check notices before any source redistribution.
Sources: [Playground repository](https://github.com/inflectra/ui-test-automation-playground) and [The Internet repository](https://github.com/saucelabs/the-internet).

Read failures must stay in the source record.
The web tool could not open the Playground URLs.
Direct HTTPS reads failed with a certificate hostname mismatch for both host forms.
The advertised HTTP pages returned the source successfully, without credentials.
No certificate check was disabled.
Two guessed raw GitHub template paths returned 404; they were not used as evidence.
Record the actual browser URL and any browser failure during feasibility checks.

Do not pool these page-element outcomes with the old SQLite record outcomes.
A combined paper can present the three studies as separate evidence:
the synthetic model, the local real-agent record pilot, and the external test-site UI pilot.
The new test adds site and interface coverage. It does not prove production transaction safety.

## Main result

Use real service websites only when a small test area and a separate record check are available.
Fix the site list and trial count before the first scored trial.
Do not transfer the local 24-second delay bound to a real service.
Call it **Wait24**, a chosen wait period, unless a service gives a suitable documented bound.

The local test used an attempt-specific permanent-drop status.
A real website may have no equivalent status.
A timeout, blank list, closed dialog, offline message, or generic error does not prove that an earlier write cannot finish.
If no suitable status is available, the closure rule must stop without retry.
This is a measured limit of the rule on that service.
It is not evidence that a terminal-state rule recovered the task.

## Site choices

Three types of site must remain separate.

| Type | Suitable use | Main limit |
| --- | --- | --- |
| Production service with a private test area | Create small test records through the real UI. Check their saved IDs through a separate read method. | Needs current access and user scope. Normal delays may give no ambiguous result. |
| Public demonstration or training service | Test the UI where its owner permits this use. | A public URL does not make the service a production website. Shared resets and local browser storage can invalidate record counts. |
| Public production site with read-only tasks | Repeat search or navigation and record visible results. | This can test observations and task completion. It cannot test duplicate saved records. |

Possible production tasks are one private Google task, one event in a separate private calendar, or one page in a private Notion test area.
These are candidate tasks, not verified available accounts.
Use only test content with a unique trial marker.
For Calendar, use no guests, no conferencing, no shared calendar, and no reminder.
For Notion, use no mention, comment, sharing change, or workflow automation.
Check these settings before the trial plan is fixed.
Google Tasks and Calendar are two services from one vendor; do not call them independent vendors.

Google documents that its Tasks insert operation creates a task in a specified list.
The API response can support a separate record check, if access is available.
It does not establish the semantics of a browser error.
Source: [Google Tasks insert](https://developers.google.com/workspace/tasks/reference/rest/v1/tasks/insert).

The Calendar API has notification options, but its documentation warns that some email can still be sent.
Therefore, an empty guest list and a private test calendar are needed; a notification flag alone is not a sufficient control.
Source: [Google Calendar insert](https://developers.google.com/workspace/calendar/api/v3/reference/events/insert).

WebArena is a self-hosted environment.
Its repository says that its public demo sites are for browsing and that evaluation needs a separate installation.
Do not run write trials on those public demos.
Source: [WebArena repository](https://github.com/web-arena-x/webarena).

WorkArena uses the ServiceNow platform for evaluation.
It is a possible later test environment, but the present review did not verify an available test instance.
Source: [WorkArena repository](https://github.com/ServiceNow/WorkArena).

## Fixed small design

Preferred design: **36 assigned trials = 3 services x 4 rules x 3 repeat blocks**.
Use one well-defined create task per service.
Use an isolated test area, or a separate unique marker, for every trial.
If only two services qualify, fix **40 assigned trials = 2 services x 4 rules x 5 blocks** before execution.
Do not select the smaller design after seeing outcomes.
These counts are modest; they do not support a claim about all websites.

| Rule | Retry condition |
| --- | --- |
| Absence | Retry once after the first fresh task-specific result check shows no record. |
| Wait24 | Retry once after at least 24 seconds and a fresh task-specific result check still shows no record. |
| Closure | Retry once only when an attempt-specific signal proves that the first attempt cannot take effect. Otherwise stop unresolved at the deadline. |
| No retry | Submit once, check, and stop at success or the deadline. |

The shared limit is two submission actions, including the first action.
Record blocked or disabled retry controls as site behavior.
Do not open a second path, change a key, or bypass a site control to force a duplicate.
If Closure and No retry have the same possible actions on a service, report that fact.
Do not count their equal results as a test of terminal failure recovery.

Use a fixed rule order that is balanced across blocks.
Save the order and any random seed before execution.
Use a new agent context for each service-block if practical.
Do not treat trials in the same context, service, or host as independent samples.
Run one write trial at a time on a service.
Fix task instructions, observation access, deadline, and maximum retries across rules.

Suggested deadline: 120 seconds from the first submission action.
Record setup failures separately and retain them in the assigned-trial table.
Fix a total admission budget before execution.
If that budget ends, retain all unstarted trials.
Never add trials to obtain a failure, a significant result, or a preferred success count.

No artificial blank screen, hidden result overlay, or modified service response is part of this design.
Do not label natural trials as pending, failed, or stale from the intended task.
Classify only the exposures shown by saved evidence.
If no trial encounters uncertainty, report **no relevant exposure**.
More easy successful tasks do not replace a test of ambiguous execution.

## Record checks and outcomes

Keep runner access separate from observer access.
The runner uses the browser UI and gets one fresh observation after each action.
The observer can use an approved read-only connector to list records in the test area.
Do not give hidden record data to the runner before it stops.
Record the exact submission UI action. A dialog opening or a title edit may not be the commit action.

Before each trial, check that its marker has zero records.
Use the same semantic task marker for both attempts.
Save all matching record IDs, not only the first search result.
Do not add an idempotency key unless that is a separate stated control.
Do not change normal site deduplication behavior.

Check the saved records after the runner stops, again at 60 seconds after stop, and at 5 minutes after stop.
Use a fresh service read for each check.
Save full pagination and query filters.
A failed audit is **unverified**, not zero records.
Keep audit failure, task failure, and rule violation as separate fields.

Without a service closure contract, the last check is a finite follow-up horizon.
Call it **count at the last audit**, not a proven final count for all future time.
Report only **no later effect observed within 5 minutes** when all checks pass.
Do not infer server commit times from the time that the browser first showed a record.
Provider timestamps and local timestamps can use different clocks.
Where exact ordering is unknown, record a time interval or an unknown value.

Primary fields:

- Assigned, started, stopped, setup failure, and audit failure.
- Submission actions, supported retries, and rule violations.
- Record counts and record IDs at each audit.
- Observed duplicate: more than one matching record at any audit.
- Supported on-time claim: a claim before the deadline with one observed task record and one record at every later successful audit.
- Unsafe claim: a claim contradicted by a later successful audit.
- Unverified claim: required record evidence is missing.
- Time to claim and time to independently observed stored record, kept separate.
- Empty observation after submission, before retry, and before a later original effect when the latter can be identified.
- Known stale negative, known pending state, terminal failure signal, or unknown execution state.
- Later effects observed after stop, and the follow-up horizon.

Do not infer stale-negative exposure merely because a record appeared later.
That result could mean a pending write, delayed observation, delayed index, or a missed UI element.
Attempt identity or a suitable time-bounded independent record check is needed for a stronger label.

## Analysis and checks

Report every assigned trial, including interruption, login failure, service error, and unstarted trial.
Report outcomes by service, rule, and block.
Show the number of trials with each relevant exposure as well as the full denominator.
Keep the new results separate from the 18 local trials and the synthetic event grid.

Report counts, raw times, and ranges.
Timing comparisons among trials that both succeed are selected comparisons.
Show unsuccessful and late trials next to them.
Do not claim a speed gain from successful pairs alone.
Do not treat a zero-duplicate result as a safety proof.
Do not give a population error rate from three chosen services.
If uncertainty intervals are added, state the sampling and dependence assumptions explicitly.
Small clustered counts make precise estimates unsuitable.

An independent reviewer should reconstruct counts from the saved record IDs and audit responses.
The reviewer should also compare action logs, screenshots, timestamps, and the fixed trial list.
Keep all failed checks and plan changes.
A technical repair must not erase a scored trial or silently replace it.
Record changes after trials start as deviations.

Do not clean up test records until the final audit and evidence copy are complete.
Keep a record of the exact IDs removed during later cleanup.
Exclude account identifiers, unrelated records, and credentials from any public package.
Use only a narrow test-area export for publication.

## Required claim limits

The strongest supported claim is a small test of instructed retry rules on the named services and dates.
It is not a natural model error rate.
It is not proof that any fixed wait is safe on the internet.
It is not a test of terminal recovery on a service that supplies no terminal status.
It is not a field failure estimate from a random sample of websites.
It does not establish absence of effects after the last audit.

## Source check record

Primary searches on 2026-10-15:

- `WebArena reproducible realistic web environment evaluation self hosted websites original paper`
- `BrowserGym benchmark environment real world websites WorkArena paper official`
- `site.developers.notion.com create page API` (the first query had an invalid site filter)
- `site:developers.notion.com "Create a page"`

The WebArena paper abstract and the official WebArena and WorkArena repositories were read.
Google Tasks and Calendar API pages were read.
Opening `https://developers.notion.com/reference/post-page` failed in the web tool.
Notion remains a candidate that needs a live access and record-check test.
The search result for an official Notion Postman collection was not used to make a UI or safety claim.
No secondary benchmark result was used.
This review is by an AI agent. It is not human or external peer review.
