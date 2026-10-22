# Source checks added by the main agent

Access date: 2026-10-22. This file adds source checks to the frozen source review. It does not change the experiment plan.

## Search and reading

The main agent used these public search strings before the experiment:

- `site.cs.cornell.edu sagas Garcia Molina Salem isolation compensation 1987 pdf`
- `site.vldb.org invariant confluence coordination avoidance database systems 2014 compensation escrow`
- `AI agent transactions isolation intermediate states compensation 2026 paper`

The main agent checked Atomix v2 Sections 2.4–2.5 and relevant Section 3.3 text. It checked the Microsoft Saga article's context, solution, and problems sections. It read the UndoBench abstract and the Bailis paper's abstract and introduction. The separate source review records the wider reading. A search result was a lead, not proof of a claim. No external experimental result is used as a result of this study.

## SQLite documentation

1. SQLite, *Isolation In SQLite*. https://sqlite.org/isolation.html . Page update shown: 2022-04-18. The complete page was read. Separate private-cache connections see committed transactions. SQLite permits one writer at a time. WAL supplies snapshot isolation for readers. BEGIN IMMEDIATE starts a write transaction before a read-to-write upgrade is needed. The study uses these documented rules; it does not claim an engine isolation failure.
2. SQLite, *Write-Ahead Logging*. https://www.sqlite.org/wal.html . Read: Overview and How WAL Works through checkpointing. The study uses WAL on one host and saves checkpointed database files. It does not test power loss, concurrent checkpoint behavior, performance, or all known SQLite defects. No source publication date is claimed.
3. SQLite, *Copyright*. https://sqlite.org/copyright.html . Read: Public Domain section. SQLite code and documentation are in the public domain. This package uses the installed library and does not copy its code or documentation. This source status does not assign a license to the user's new work.

## Review guide

NeurIPS, *NeurIPS Paper Checklist*. https://neurips.cc/public/guides/PaperChecklist . The current page was available. Relevant sections were read: claims, limitations, theory, reproducibility, code and data, experiment details, statistical uncertainty, resources, ethics, broader impacts, safeguards, licenses, released assets, human subjects, and LLM use. It is a review aid only. Its use does not imply conference approval, peer review, or submission compliance.

## Rights and scope

The package contains original experiment code and synthetic test records. Source papers, figures, datasets, and code are not republished. References are paraphrases with attribution. No new reuse license is assigned. The search is limited and cannot establish priority. The report uses established isolation ideas and claims a small reproducible regression experiment.
