# Independent review of the additional website experiment

Date: 2026-10-15. Status: **PASS WITH LIMITATIONS**. No unresolved material error was found in the new experiment or its reported results. This review is by a separate Codex agent. It is not human review, external peer review, or approval by a conference. The reviewer did not perform the website trials, write their plan, or write the main analyzer. The review covers the new 48-trial extension. Prior studies keep their earlier review records.

## Independent reconstruction

The reviewer first read the frozen plan, assignments, runner instructions, and design review. The reviewer then wrote cross_independent_replay.py without reading or importing cross_analyze.py. It derives table rows from visible cell lines. It reads active search, complete headers, enabled Add, disabled Next, and form status from the saved observations. It computes time from raw request and observation timestamps. It does not use runner summaries as outcome evidence.

All four frozen file hashes match. An independent use of random.Random(20261016) recreates all 48 assignments in order. All initial scored requests occur after the saved freeze time. All 48 trials are complete. All 1,448 trial checks pass. The checks cover baseline rows, actual search, new ready observations, six DemoQA form values, one-retry limits, Wait24 eligibility, the 120-second deadline, scope changes, decision evidence, full audit rows, no reload before audit, and cleanup.

The results are 32 on-time correct confirmations and 16 unresolved decisions. Each unresolved case has two new rows at its pre-reload audit. There are 64 new rows in total, 48 initial requests, and 16 retry requests. No confirmation is false or late. All 48 cleanup observations show the default baseline and empty search. No scored action log contains a tool error.

On each site, all four Hidden Absence cases and all four Hidden Wait24 cases retry and create extra effects. All four Hidden Scope cases clear search and confirm one row without retry. All 12 All controls on each site confirm one row without retry. Thus the three stated hypotheses and all activation gates hold on each site's fixed assignments. These results do not estimate a population rate.

The eight Wait24 later reads start 27.277 to 29.488 seconds after the initial request. The median decision time is 6.1165 seconds, reported as 6.117 seconds. The range is 2.267 to 40.443 seconds. These measurements include model, tool, and shared-host delays.

Only after deriving these outcomes did the reviewer read the main analyzer and its outputs. Every trial's first count, actual first view, retry count, decision, decision time, Wait24 interval, audit count, and classification matches. A separate execution of the documented main command produced byte-identical cross_trials.csv, cross_groups.csv, cross_summary.json, cross_analysis_checks.json, and cross_analysis_log.txt. Its 15 parser checks passed. Run `python3 cross_independent_replay.py` from this folder to repeat the independent reconstruction. This command uses only the Python standard library and the saved files.

## Original and public evidence

The reviewer compared all 880 scored/setup records and 23 excluded preflight records with the full local originals. The independent comparison checked 948 state strings, exact non-state metadata, original state hashes, and the task-region extraction. It preserved every search field, row cell, footer count, action argument, time, error, decision, and correction. Both runner completion summaries also match their local originals byte for byte. No non-example.com email, private local path, credential pattern, or application-source block was found in the new public evidence. This is a bounded check, not a guarantee that a pattern scan can find every possible secret. See cross_private_review.json.

The failed 19.606-second DataTables feasibility read remains separate from the scored trials. Its second preflight passed at 36.318 seconds. Setup tab-ownership failures and the early DemoQA helper error remain documented. They do not become scored failures or replacement trials. The raw records have 316 action records and 272 observation records. A fixed form-fill action can contain six fields. These counts are not model-call counts.

## Images and retained defect

The reviewer viewed all 54 distinct image byte patterns. SHA256 groups cover all 145 public images. Each archive member matches its original file, manifest byte count, JPEG signature, and timed image record. There are 144 planned decision/audit/cleanup captures and one additional D03 audit capture. The one full private fallback is absent from the public archive.

DemoQA images show the task title, search, displayed rows, and pagination. DataTables images show Add, search, rows, footer totals, and pagination, with one retained exception: D03-audit.jpg cuts off the status and pagination. The later D03-audit-expanded.jpg shows the complete three-row audit and controls. It is separately timed, before cleanup, and does not change the earlier unresolved decision. No private account controls or non-test personal records were visible. The DataTables task crops do not show a URL bar; the report and evidence notes provide the provider and source URL. See cross_image_review.json for exact hashes and limits.

## Claims, sources, and rights

The reviewer read the completed abstract, Section 10, related-work addition, shared limitations and ethics text, reproduction instructions, bibliography additions, source search, and change record. All new numerical claims agree with the raw-evidence reconstruction. The paper separates DemoQA duplicate records from DataTables extra generated rows. It states that the rule ignores visible DataTables footer totals, that a new read is not a reload, that Receipt is unavailable, and that the audit is browser evidence rather than an independent service audit.

The reviewer opened the official [DataTables example](https://datatables.net/examples/core/api/add_row.html) and [row.add() reference](https://datatables.net/ref/core/api/row.add%28%29). Their descriptions support one added row per click and search-dependent visibility. The reviewer read the [WAREX abstract and introduction](https://arxiv.org/html/2510.03285v1) and [RFC 9110 section 9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2). Their use in the new comparison is limited and supported. [DemoQA](https://demoqa.com/webtables) returned no web-extract text. Its task claims were checked against the actual original browser observations and images. This review does not claim a fresh full reading of every reference from the prior studies.

The new prose does not claim a first discovery, new retry protocol, general model gain, statistical significance, natural failure rate, or server durability. No copied source passage was found in the new prose. Necessary provider UI evidence has attribution. Published logs exclude page-code examples. No new source license is assigned. Synthetic example.com records are identified as test data. The Codex role and absence of human or external peer review remain explicit.

The reviewer used the [NeurIPS checklist](https://neurips.cc/public/guides/PaperChecklist) as a review aid for claims, limitations, methods, reproduction, code/data, uncertainty, compute, ethics, and rights. The selected repeated tasks do not justify population confidence intervals. The report states that limit. Model sampling settings and inference hardware are not available. The review is not a claim of NeurIPS compliance or approval.

## Review boundary

The two sites were selected after successful feasibility checks. Both use table tasks. One runner per site means that site and runner effects cannot be separated. Shared contexts and a shared host limit independence. The rules deliberately exclude some visible information. The archived logs do not contain complete model-turn boundaries or tool-call code; the paper correctly calls this an instruction boundary rather than secure isolation. These limits remain material to interpretation.

The review does not certify exact future live reproduction, a security boundary, service-side persistence, or GitHub publication. PDF layout and remote publication checks are separate. cross_review_receipt.json fixes the exact report and supporting input hashes used for this decision.
