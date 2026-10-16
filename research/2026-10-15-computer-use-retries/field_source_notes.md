# Source check for saved-field validation

Search and access date: 2026-10-15, America/Toronto. The search took place before scored trials. This is a limited search. It does not establish novelty or priority. The linked documents are primary sources. No third-party document, code, or data is republished here.

## Search terms

1. `site:developers.google.com/workspace/calendar/api/v3/reference/events description HTML end exclusive transparency transparent`
2. `computer use agents persistent state verification saved fields ERPBench 2026`
3. `site:support.google.com/calendar description formatting event Free Busy all day`
4. `site.notion.com/help database properties text checkbox` (lead search; the design reviewer opened the exact source below).

Search results also included support-community posts and another work named ERPBench. Those results were not used as technical authority. The exact papers used below have distinct titles and identifiers.

## Sources and read scope

### Google event fields

Google. *Events*. Provider reference, accessed 2026-10-15. [Source](https://developers.google.com/workspace/calendar/api/v3/reference/events).

Read scope: resource representation; `id`; `description`; `start` and `end`; recurrence; attendees; reminders; transparency; visibility; and status. Descriptions can contain HTML. All-day events have date fields. The end is exclusive. The `transparent` value means that the event does not block time; `opaque` means that it does. Event IDs and iCalendar UIDs are different. These are API definitions. They do not establish which fields the connected tool returns. The study must record that tool's actual schema and the native saved UI. The text-marker normalization below is a local prospective rule, not a Google guarantee.

### ERPBench

Bhagtani, K.; Sridhar, K.; Pouyan, M. B.; Zhao, Y.; and Siow, E. (2026). *ERPBench: A State-Grounded Evaluation Paradigm for Computer-Use Agents in Enterprise Software*. arXiv:2609.17885v1, 2026-09-15. Preprint. [Version used](https://arxiv.org/html/2609.17885v1). [Version record](https://arxiv.org/abs/2609.17885).

Read scope in this extension: abstract, introduction, related work, task design, and grading description. The work checks saved fields in a self-hosted ERP system and distinguishes a save action from correct persistent values. It gives task-specific expected values to its grader. Our selected account tests use normal browser controls and a read-only Calendar connector. They do not have direct database access. The version record has a later version 2; this note does not claim to review that version.

### StateAct

Yang, Y.; Jian, X.; Luo, Z.; Zhao, Z.; Dai, Y.; Shi, Z.; Yan, H.; Liew, J. H.; Savarese, S.; and Li, J. (2026). *StateAct: Program State, before Pixels, for Long-Horizon Computer-Use Agents*. arXiv:2607.22798v1, 2026-07-24. Preprint. [Source](https://arxiv.org/html/2607.22798v1).

Read scope: abstract, introduction, Section 4.2, Section 6.1, its finish-gate table, and conclusion. StateAct uses a separate final check that reads real artifacts without the acting agent's narrative. Its analysis distinguishes structural checks from correct field values. A check can still accept the wrong value. Our small study uses known target fields and injected errors. It does not reproduce StateAct, compare model scores, or prove a general verifier improvement.

### Retry identity

Lee, C.; Park, S. J.; Kejriwal, A.; Matsushita, S.; and Ousterhout, J. (2015). *Implementing Linearizability at Large Scale and Low Latency*. SOSP 2015. DOI: 10.1145/2815400.2815416. [Author-hosted paper](https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf).

Read scope in this extension: abstract, introduction, and Section 2. This work explains why uncertain responses can cause a repeated effect, and why systems need to recognize a prior request. A local one-Create limit is not the server mechanism in that paper. Our tests neither establish exactly-once service semantics nor test concurrent writers.

### Notion properties

Notion. *Database properties*. Provider guide, accessed 2026-10-15. [Source](https://www.notion.com/help/database-properties).

Read scope: property types and editing property values. Text properties contain text that can be formatted. Checkbox properties represent a true or false condition. These definitions support the selected Marker and Verified property types. They do not guarantee a native page URL, commit timing, or save persistence. The study checks the actual saved native page.

### Review aid

NeurIPS. *Paper Checklist Guidelines*. Accessed 2026-10-15. [Source](https://neurips.cc/public/guides/PaperChecklist).

Read scope: claims, limits, assumptions, reproduction, code and data, experiment details, statistics, compute, ethics, and assets. Use the relevant questions as a review aid. Do not claim conference approval or submission compliance. This selected, small case series does not supply population error rates. Report per-condition counts, retained failures, incomplete fields, and the evidence access limits. Save the plan and comparison rule before scored work. Keep copied private account material out of public data.

## Proposed contribution and limits

The proposed contribution is a prospective equality rule plus a traceable test of deliberately wrong saved fields in two existing account services. The new checker separates MATCH, MISMATCH, and UNKNOWN. It checks the first record identity, the saved required fields, and the covered record count. It permits one repair on that same record, then requires new reads. It does not create another record.

These ideas use established state verification and retry principles. The exact cases and evidence can be a useful addition to this paper. They are not a new distributed-systems guarantee or a claim to be the first field-checking method. A local classifier, given recorded observations, is not an autonomous browser driver.

The title-and-count baseline is an offline paired decision on the same saved observations. It does not execute a second browser policy. It estimates what that limited check would label in these cases. It does not estimate the causal effect of a deployed policy. Earlier Calendar strict UNKNOWN results must remain unchanged.
