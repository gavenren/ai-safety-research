# Source check for the revised retry rule

Search and access date: 2026-10-15. These notes were saved before scored trials. The search is limited. It does not establish novelty or priority. No third-party paper, source code, or data are copied into the study.

## Search terms

- site.rfc-editor.org rfc 9110 9.2.2 automatically retry non-idempotent original request never applied
- site.developers.google.com calendar api events id prevent duplicates creation all-day end exclusive
- site.notion.com help duplicate delete restore content database unique ID page title
- browser agent recovery idempotent duplicate confirmation transaction identity retry research
- computer use agent false success persistent state RStackBench
- site.usenix.org RIFL exactly once semantics browser retry duplicate request

General searches also returned vendor posts and informal research pages. Those results were not used as technical authority. The sources below are standards, provider documentation, or the original research authors' paper.

## Sources read and exact use

1. Fielding, Nottingham, and Reschke. RFC 9110, HTTP Semantics. June 2022. https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2 . Read scope: Sections 9.2.1 and 9.2.2. Idempotence concerns the intended effect of repeated operations. A non-idempotent retry needs evidence that the original was not applied or an applicable idempotent contract. This supports the refusal to retry after zero matches alone. It does not establish a contract for a particular browser button.

2. Lee, Park, Kejriwal, Matsushita, and Ousterhout. Implementing Linearizability at Large Scale and Low Latency. SOSP 2015. DOI 10.1145/2815400.2815416. https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf . Read scope in this extension: abstract, introduction, and the Section 9 browser discussion on PDF pages 14-15. RIFL records completed request results and returns them on a retry. The browser discussion links uncertain outcomes to recognition of prior effects. This is prior systems work, not a guarantee supplied by our browser-only rule.

3. Google. Create events. Provider documentation, undated. https://developers.google.com/workspace/calendar/api/guides/create-events . Read scope: event metadata, identity, and all-day representation. The API can accept a client event ID, while the server supplies one when absent. All-day events use date fields. This study does not create through the API and does not test the client-specified-ID mechanism.

4. Google. Events resource. Provider documentation, undated. https://developers.google.com/workspace/calendar/api/v3/reference/events . Read scope: id, start, end, description, recurrence, attendee, and reminder fields. The event end is exclusive. The documented collision caveat prevents an unqualified claim that an arbitrary client ID is a complete server guarantee. For the proposed all-day task, the expected values are start.date 2026-10-14 and end.date 2026-10-15.

5. Notion. Unique ID. Provider documentation, undated. https://www.notion.com/help/unique-id . Read scope: adding the database ID property and its special URL. The ID property provides fixed task numbers, including for deleted pages. This is not the same thing as the native page UUID. The proposed trial uses native page links already visible in the UI, so no inference about native UUID semantics is taken from this property guide.

6. Bhagtani, Sridhar, Pouyan, Zhao, and Siow. ERPBench: A State-Grounded Evaluation Paradigm for Computer-Use Agents in Enterprise Software. arXiv:2609.17885v1, September 15, 2026. PREPRINT. Version 2 exists dated September 23, 2026; this check uses version 1 and does not claim to cover later changes. https://arxiv.org/abs/2609.17885 ; https://arxiv.org/html/2609.17885v1 . Read scope: abstract, Section 3 task design and grading, Section 4.3 failure analysis, and conclusion. The paper checks persistent task fields through a separate service interface and separates save actions from correct stored state. It studies a self-hosted ERP system with screenshot-only agents. Our extension uses two existing account services, accessibility-supported browser control, and selected recovery cases. Notion has browser evidence only; Calendar has a read-only service audit. Thus our evidence is not equivalent to ERPBench's database access.

## Proposed contribution

The contribution is a tested change to the paper's supplied recovery rule: preserve the first native record identity, account for incomplete effects, repair the same record, and check stored fields before a completion claim. The design compares that whole rule with the old exact-title Absence rule. Known systems principles and earlier state-based browser evaluations already cover its main ideas. Do not label it a new distributed-systems protocol, a new exactly-once guarantee, or the first test of persistent browser state.

The title and case distinction are original study choices. That fact does not establish broad method novelty. Claims must stay within the measured operations, service versions, dates, observation bounds, and actual audit access.
