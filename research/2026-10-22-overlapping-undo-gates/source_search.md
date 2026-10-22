# Source search and reading record

Search and access date: 2026-10-22, America/Toronto. Sources were searched and read before the plan was frozen. The search was limited. It does not establish novelty or priority. No source data, source code, or figures are copied into this package.

## Search terms

The web tool ran these exact queries:

1. `site.redis.io distributed locks random value unlock same value release lock`
2. `site.aws.amazon.com builders library making retries safe idempotent APIs late arriving requests`
3. `site.docs.python.org threading semaphore release count boundedsemaphore`

The queries returned original vendor documentation and the primary preprint listed below. Current Atomix v2 and the NeurIPS checklist were also opened directly. The repository protocol, index through October 22, and the October 22 visibility report were read locally from the main agent's verified files.

## Sources read and their use

1. Malcolm Featonby, *Making retries safe with idempotent APIs*, Amazon Builders' Library. [Original article](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). Read the sections on client request identifiers, atomic recording, late requests, and changed intent. The article describes retained request identity and late requests after resource removal. This is prior work for the lifecycle registry. The HTML did not expose a publication date. The linked original PDF bears a 2020 copyright notice. Access date is recorded instead of an inferred publication date. No AWS operation was run.

2. Redis, *Distributed Locks with Redis*. [Original documentation](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/). Read the single-instance implementation and safe release explanation. Release must match the value of the acquired lock. This supports ownership as an established idea. The present model is not Redis, Redlock, a lease, or a mutual-exclusion lock. No publication date was exposed.

3. Vivek Shahare, Milind Chabbi, and Nikhil Hegde, *Protecting Locks Against Unbalanced Unlock()*, arXiv:2304.11983v1, 2023-04-24. [Original preprint](https://arxiv.org/html/2304.11983v1). Read the abstract, introduction, Section 2, and Section 3.1 (Boolean test-and-set lock), with the beginning of Section 3.2 for context. Repeated or unowned release can break safety, and owner checks are known. The paper studies actual shared-memory locks; this note studies an abstract shared reader gate. No performance or frequency result is imported. The source labels its license CC BY-SA 4.0; no source text, code, table, or figure is redistributed.

4. Bardia Mohammadi, Nearchos Potamitis, Lars Klein, Akhil Arora, and Laurent Bindschaedler, *Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows*, arXiv:2602.14849v2, revised 2026-05-29. [Original preprint](https://arxiv.org/html/2602.14849v2). Read the introduction and Section 2.2, including operation lifecycle, ownership, and seal enforcement. Terminal states and runtime-managed concurrency are not new here. This note does not implement or evaluate Atomix, and does not use its reported results.

5. Python Software Foundation, *threading — Thread-based parallelism*. [Original documentation](https://docs.python.org/3.14/library/threading.html). Read the search-returned Semaphore and BoundedSemaphore descriptions. This was a design lead only. The study's count increments on close and decrements on release, with a clamp at zero. It is not a Python semaphore, and no statement about Python semaphore correctness is made. This lead is not a technical reference in the report.

6. NeurIPS, *Paper Checklist Guidelines*. [Original guide](https://neurips.cc/public/guides/PaperChecklist). Read claims, limitations, theory, reproduction, code/data, experimental details, uncertainty, compute, and broader impact guidance. Use only as a review aid.

## Relation to earlier repository studies

The October 22 visibility report uses one gate owner and interrupted field changes. This new note removes field predicates and failures, and tests two gate owners with duplicate request delivery. The October 18 retry-retention report varies memory expiry. This note retains all completed IDs and tests no expiry. Its contribution is the exact gate corpus, comparison, and retained counterexamples. Known ownership and request-deduplication mechanisms are not claimed as new.

## Excluded leads and access limits

Search results included discussion forums, third-party copies, semaphore overviews, and unrelated lock designs. They were not used as technical evidence. Only the read portions above support the report. No full systematic literature review or broad novelty claim is made. All listed original URLs returned readable content or the specified original documentation excerpt during this run.
