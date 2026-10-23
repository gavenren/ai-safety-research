# Source search for the October 23 study

Search and access date: 2026-10-23. The source-review clock was checked at 13:57:49 UTC. These searches and reads took place before the root agent selected or froze the experiment plan. No experiment was run by this source reviewer. The log records a limited search, not a novelty proof.

## Repository review

The current public `README.md` and `RESEARCH_PROTOCOL.md` were read with the GitHub connector on 2026-10-23. The index had no October 23 study. It included the October 22 compute-verification paper and five production extensions. The source reviewer did not use the index as proof of an immutable commit. The root agent must check that state before publication.

Local reports read:

- `outputs/2026-10-22-receipt-binding/report.md` and `source_search.md`: the synthetic study and live extension compare operation scope and payload binding. The live exact-repeat cases have no deliberate later change to the resource.
- `outputs/2026-10-18-retry-retention/report.md`: the model varies retention, delay, and dropped replies. It has no other writer and uses one fixed effect.
- `outputs/2026-10-16-field-snapshot/report.md`: the model compares mixed field reads. A later write after the last observation is outside its scored decision interval.
- `outputs/2026-10-17-repair-dependencies/report.md`, through method and planned measures: the model already compares stale decisions and guarded repair under concurrent edits. Do not present another version check as a new repair method.

## Exact search queries

1. `site.aws.amazon.com/builders-library making retries safe with idempotent APIs late arriving requests deleted resource semantically equivalent response`
2. `site.docs.stripe.com/api idempotent requests first request result parameters saved result`
3. `site.rfc-editor.org RFC 9110 If-Match lost update representation selected resource`
4. `site.sosp15.mpi-sws.org RIFL implementing linearizability large-scale distributed systems completion record garbage collection`
5. `site.arxiv.org agent idempotency receipt current state retry verification completion stale`
6. `site.docs.stripe.com api-v2-overview idempotency updated response replay`
7. `"Implementing Linearizability at Large Scale and Low Latency" pdf Stanford rifl`
8. `site.arxiv.org "receipt" "current state" idempotency`

## Primary sources read

### S1. AWS: Making retries safe with idempotent APIs

Author: Malcolm Featonby. Date: undated page. Type: provider engineering article.

URL: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/

Read scope: request identity and atomic recording; semantic equivalence; late requests; changed parameters; conclusion. In the browser extraction, the main checked passages were lines 237–258, 313–379, and 423–477. The sample commands were read, not executed.

Supported use: AWS describes a repeated request after another actor terminates the resource. The response remains consistent with the earlier operation and can expose the later terminated state. It also stores original parameters to reject a conflicting repeated request. This is direct prior work for the historical-operation/current-state distinction. It is not evidence that every service returns a frozen body or a fresh state.

### S2. Stripe: Idempotent requests

Author: Stripe. Date: current undated reference. Type: provider API document.

URL: https://docs.stripe.com/api/idempotent_requests

Read scope: complete short substantive reference, excluding linked pages not listed here.

Supported use: API v1 saves the first status and body after execution starts and returns that result for a repeated key. It checks changed parameters. The page distinguishes API v2. Limit any frozen-response statement to API v1. No Stripe endpoint was tested.

### S3. Stripe: API v2 overview

Author: Stripe. Date: current undated reference. Type: provider API document.

URL: https://docs.stripe.com/api-v2-overview

Read scope: opening comparison table and the full Idempotency and Idempotency differences sections (extraction lines 129–152).

Supported use: API v2 skips a successful operation on replay and returns an updated response. It can retry failed work. The documented replay scope includes account or sandbox, API, key, and a 30-day interval. This is a counterexample to any claim that all idempotent responses are frozen snapshots.

### S4. Lee et al.: Implementing Linearizability at Large Scale and Low Latency

Authors: Collin Lee, Seo Jin Park, Ankita Kejriwal, Satoshi Matsushita, John Ousterhout. Date: October 2015. Venue: SOSP 2015. DOI: 10.1145/2815400.2815416. Type: conference paper, author-hosted PDF.

URL: https://web.stanford.edu/~ouster/cgi-bin/papers/rifl.pdf

Author project page checked: https://seojinpark.net/projects/rifl/

Read scope: abstract; Section 2 including Figure 2; Section 3; Section 4.1; Section 9. The extracted Section 4 and Section 8 surroundings were visible but are not used for empirical claims. No source code or benchmark was reproduced.

Supported use: Figure 2 already gives a repeated fixed write that overwrites an intervening write. RIFL stores a result record atomically with the effect and returns it without another execution. The paper states limits for client crashes. Our small model would not implement RIFL or improve its algorithm.

### S5. RFC 9110: HTTP Semantics

Editors: Roy T. Fielding, Mark Nottingham, Julian Reschke. Date: June 2022. Type: Internet Standard.

URL: https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1

Read scope: Section 13 opening, all of Section 13.1.1, and the matching Section 13.2 precondition-order excerpt. Relevant extraction lines: 2723–2760 and 2898–2903.

Supported use: If-Match checks the selected representation before the method. A failed condition must not execute that method, but a successful reply is permitted when the change appears already applied. Thus, a status code alone is not a complete record-history proof. The RFC does not establish a particular browser connector's atomic capability.

### S6. Google Calendar: Get specific versions of resources

Author: Google. Date: current undated page. Type: provider API guide.

URL: https://developers.google.com/workspace/calendar/api/guides/version-resources

Read scope: conditional modification and conditional retrieval prose; the displayed Java examples. Relevant extraction lines: 58–143.

Supported use: the guide describes If-Match for updates/deletes and a 412 response after a changed version. Inserts have a different ID-based condition. There are documented ETag exceptions for read-only calendarList fields. This is an interface example, not proof that our tools supply or exercised the condition.

### S7. Salas: Authority at Commit Time

Author: Jesus Salas. Version: arXiv:2609.31490v1, submitted 2026-09-25; the manuscript itself says August 2026. Type: preprint. Peer review or acceptance was not independently verified.

URL: https://arxiv.org/html/2609.31490v1

Read scope: abstract; Sections 2.4, 3.2–3.3, 4.1, 6.4–6.6, and 7.1. Relevant extraction passages include lines 138–218, 220–245, and 343–366. The complete paper, code, proofs, and experiments were not checked.

Supported use: this work resolves a lost response through a canonical verdict or receipt and treats current workflow closure separately. It also states that an external adapter must supply idempotency or reconciliation. These are close ideas. Our proposed study would supply a smaller explicit observation-equivalence corpus, not a new receipt protocol or a test of this preprint.

### S8. Liu, Yu, and Zhang: Revocation Is Not Complete at Receipt

Authors: Lifei Liu, Haoran Yu, Danping Zhang. Version: arXiv:2610.15991v1, dated 2026-10-11. Type: preprint. The manuscript has DAI 2026 conference text, but acceptance was not independently verified.

URL: https://arxiv.org/html/2610.15991v1

Read scope: abstract, contribution statement, and Sections 2.1–2.2. The experiments and code were not reproduced or fully reviewed.

Supported use: this work distinguishes receipt stages from a bounded effect outcome and gives an indistinguishability argument when later evidence is missing. That proof pattern is prior work. Its target is distributed revocation, unlike our proposed single-record operation history and current-state claims. Do not claim to invent the use of separate outcome evidence.

### S9. NeurIPS Paper Checklist

Author: NeurIPS. Date: current 2026 page. Type: research review guide.

URL: https://neurips.cc/public/guides/PaperChecklist

Read scope: opening guidance, claims and limitations, theory assumptions, reproduction, open code/data, experimental detail, and uncertainty guidance. The root review must apply the relevant ethical and rights checks too.

Use: review aid only. This is not conference approval, submission compliance, or certification.

## Leads not used as evidence

Search results also returned ClaimReceipt (arXiv:2609.01992), an IETF Internet-Draft on receipt-gated effectuation, an Agent Receipts Protocol page, and informal blog/forum discussions. Their full content was not read. They are search leads only. No claim relies on them.

## Rights and uncertainty

No paper, source code, figure, or API example is copied into the study. The notes paraphrase only the listed facts and preserve URLs. No new license is assigned to the owner's work. Web extraction can omit layout or equations; the proposed report must not rely on an uninspected equation or figure detail. The limited search supports a bounded artifact contribution. It cannot establish priority or comprehensive novelty.
