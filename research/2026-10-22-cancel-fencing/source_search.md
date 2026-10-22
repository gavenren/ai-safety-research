# Source search and scope

Search date: 2026-10-22, America/Toronto. Searches were completed before the plan and code. Primary sources were used for substantive claims. A limited search does not establish novelty.

## Queries

- `site:research.google.com archive chubby fencing sequencer lock delay 2006 pdf`
- `site:arxiv.org AI agent cancellation stale action fencing token 2026`
- `site:arxiv.org "cancellation" "agent" "2026" "fencing"`
- `site:docs.temporal.io "Cancellation" "Heartbeat" activity`
- `AI agent cancellation shutdown stale actions fencing stop means stop paper 2026`
- `site:docs.temporal.io "cancellation" "heartbeating"`

## Sources used

1. Mike Burrows. *The Chubby lock service for loosely-coupled distributed systems*. OSDI, 2006, pages 335–350. Original publisher PDF: https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf . Read abstract and Sections 2.3–2.4, with the sequencer API in 2.6. These sections establish prior generation and recipient checks. This study neither implements Chubby nor tests its guarantees. The Google archive PDF redirect failed; the original USENIX copy was accessible. No paper text or PDF is redistributed.
2. Martin Kleppmann. *How to do distributed locking*. Author article, 2016-02-08. https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html . Read sections from “What are you using that lock for?” through “Making the lock safe with fencing.” The delayed-check problem and recipient token check are prior ideas. This study does not test Redlock or adopt the article's performance claims. No copied text is included.
3. Genliang Zhu and Chu Wang. *Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution*. arXiv:2609.21284v1, 2026-09-18, preprint. https://arxiv.org/html/2609.21284v1 . Read abstract, Sections 1–1.2, 3.1–3.3, 4.4, and 6.2. Cancellation versus receiver fencing, old epochs, and the check at the effect boundary are close prior work. Our small model adds a complete restart-horizon/order corpus for seven fixed rules. It omits their delegation, multiple authority roots, certificates, and real worker process. We did not verify their code or proofs. The arXiv record specifies a non-exclusive arXiv license; no full text is redistributed.
4. NeurIPS. *Paper Checklist Guidelines*. https://neurips.cc/public/guides/PaperChecklist . Read claim, limitation, theory, reproduction, code/data, settings, significance, compute, and later ethics/asset/LLM-use guidance. Used only as a review aid, not an approval claim.

## Leads and access limits

Sajjad Khan, *Stop Means Stop*, arXiv:2607.14166v3, revised 2026-08-08. Original abstract and submission history were read at https://arxiv.org/abs/2607.14166 . It identifies fence-on-cancel as prior work. HTML v2 and v3 returned 404. Its full paper was not checked, so its framework results and proofs are not used as evidence here. The Temporal cancellation URL failed; search snippets and general task documentation are not used to establish a cancellation guarantee. Other search results were not used.

## Repository comparison

Read the repository protocol, index, October 16 field-snapshot report, October 17 repair-dependencies report, and October 22 undo-visibility report. October 16 already tests reused revisions during reads; October 17 tests stale decisions during repair. This note tests permanent retirement of one worker across restarts and receiver knowledge before a new worker writes. It does not claim that token reuse or check-use delay was first found here.
