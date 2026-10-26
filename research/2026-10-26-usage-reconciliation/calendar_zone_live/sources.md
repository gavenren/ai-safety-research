# Source check: new Calendar time-zone tests

Search and read date: 2026-10-26. This check used public primary sources. It did not use account data. It does not establish novelty.

## Search record

The web search used these exact terms:

- `site:developers.google.com calendar api events timeZone IANA offset`
- `site:support.google.com/calendar time zone event computer`
- `computer use agents task completion verification saved state benchmark arxiv`

The closest selected research sources were StateAct and OpenComputer. Search results also included OSWorld 2.0, SaaS-Bench, and other work. Those other papers were not read for this check and must not be cited as fully checked sources.

## Primary documentation read

1. Google, [Events resource](https://developers.google.com/workspace/calendar/api/v3/reference/events). Read the start/end schema, time-zone field definitions, status, visibility, transparency, and reminder entries. The start and end `timeZone` fields hold IANA names. A numeric offset in a time string is a different field. For a single event, the named zone is optional in the API. Thus, a study can require explicit zone evidence as its own contract; it must not claim Google requires a named zone on every single event. The status documentation supports checking `cancelled` after deletion. Page read on 2026-10-26.

2. Google, [Calendars and events](https://developers.google.com/workspace/calendar/api/concepts/events-calendars). Read the event identity and time-zone sections. The page states that several representations can specify the same instant, while an explicit `timeZone` attaches a named zone to the event. Single events can use different start and end zones. Query display zones can differ from event zones. This supports separate checks for the named start and end zones. It does not prove what the connected tool returns. The page shows an update date of 2026-09-03.

3. Google, [Use Google Calendar in different time zones](https://support.google.com/calendar/answer/37064?hl=en). Read the computer instructions for event zones, calendar zones, and display zones. The event editor has a Time zone control and can use separate start/end zones. A calendar grid label does not establish the zone of one exact event. Use the saved event editor for the observed record. Read on 2026-10-26; no publication date was shown in the read text.

## Closest related research read

4. Yan Yang and coauthors, [StateAct: Program State, before Pixels, for Long-Horizon Computer-Use Agents](https://arxiv.org/html/2607.22798v1). Preprint v1, 2026-07-24. Read the abstract, introduction, related verification discussion, and section 4.2. The finish check inspects the actual saved artifact independently of the acting agent's claims. Its stated purpose is structural validation. The proposed Calendar extension is narrower: it tests one existing field checker with new production events and deliberately incomplete or incorrect evidence. It is not a new form of independent verification. No performance number from this paper is needed for the extension. The full paper was opened, but only these sections were reviewed in detail.

5. Jinbiao Wei and coauthors, [OpenComputer: Verifiable Software Worlds for Computer-Use Agents](https://arxiv.org/html/2605.19769v1). Preprint v1, 2026-05-19. Read the abstract and section 3.2, including verifier tests and bounded repair. It uses app-specific state checks, positive and negative fixtures, and checks against live applications. Its repair process preserves the recorded task and state. The proposed extension applies a frozen checker to new temporary Calendar events after an earlier repair. It is a small prospective validation, not a new verifier architecture. The full paper was opened, but only these sections were reviewed in detail.

## Review aid

6. NeurIPS, [Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). Read claims, limitations, reproducibility, experiment details, uncertainty, resources, ethics, impact, licenses, assets, and AI-use items. Apply these items to the new section. Keep selected-case counts separate from production error rates. Record evidence omissions and corruptions as local test inputs. Record wrong saved zones separately. Do not claim external review or NeurIPS approval. An agent review is not human review. Read on 2026-10-26.

## Contribution and rights boundary

This extension can add new evidence about whether the corrected checker refuses incomplete or wrong zone evidence and accepts complete matching evidence. It cannot establish a general error rate, prove all time zones work, or establish a new algorithm. Missing connector output must be measured in this run; the Google API schema alone does not establish that omission.

Use short original summaries and source links. Do not copy diagrams, paper text, code, or datasets. Google developer pages state CC BY 4.0 for their documentation and Apache 2.0 for code samples. No source code sample is used here. OpenComputer's HTML lists CC BY 4.0. StateAct's HTML lists the arXiv perpetual non-exclusive license. No new license is assigned to the user's work. Do not publish private account identifiers, event links, owner addresses, or unrelated screen content.
