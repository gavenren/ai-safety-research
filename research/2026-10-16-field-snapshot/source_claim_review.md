# Source and claim review

Date: October 16, 2026.
Reviewer: a separate Codex agent. This is not human or peer review.
Scope: report source claims, references, derivations, model limits, and novelty language. The independent calculation review has responsibility for the complete numerical replay.

## Files checked

| File | SHA-256 |
| --- | --- |
| report.md | `6781f3b41d347f61433f44444b059e2cda4caaacfffd20203fe4309af0572c35` |
| references.bib | `cb81138d088c28f191a056059e4dad96381495c7a620a8a76b74ac902d9c1104` |
| derivations.md | `ccd8c077d14297ffdc29077f39f5b27e941e04d261aef32cd68e0ffd8d556a3d` |
| analysis_plan.md | `4624ae4b04f9d3d26682e5b08d88ad1f0ee47d6bdc79e4b7b46c4f374ca3279d` |
| source_search.md | `060f01e58cdee980f083eaf6031d1f892226b770156e4a20ae3bc5993a9dfd62` |

The hashes identify the reviewed bytes. A later report edit requires a new check.

## Outcome

PASS. No material source or mathematical-claim error remains in the reviewed report. Two wording issues were reported and corrected before this record: the H3 summary now matches the frozen plan, and content-validator reuse is marked as an inference rather than a measured Calendar behavior.

## Source claim checks

- The snapshot paragraph is supported by Afek et al., Section 3. The report does not attribute its simplified guard to the complete wait-free algorithm. It states that the original construction has more machinery.
- The RAMP paragraph is limited to database visibility. It does not claim that the bit model implements RAMP or a multi-field transaction.
- The Linux paragraph keeps the writer-protocol and read-order conditions. The report's atomic bit flip and simultaneous revision update are explicit model assumptions.
- The StateAct paragraph concerns saved-output verification only. Version 1 is labeled as a preprint. No unreviewed benchmark accuracy is imported into the report.
- The Calendar reminder statement matches the official Events descriptions for `reminders` and `updated`. The earlier task contract includes reminders. The inference that this timestamp alone is incomplete for that contract is supported. It is not called a provider defect.
- The ETag paragraph does not claim that Google uses a content hash or permits stale reads. The content-token example is a general inference from a permitted HTTP validator design. Equal content tokens do not establish a never-reused history counter.
- The cache statement is supported by RFC 9111 Section 4.2. It concerns cache reuse rules, not an observed service fault.

The exact source sections read are recorded in source_search.md. Full-paper review is not claimed. Sources first read during the source review were reopened where needed to check metadata. No paper text or code was copied into this study.

## Bibliographic checks

All eight entries in references.bib have unique keys and balanced braces. Authors, titles, source identity, and listed publication or page-update dates match the checked sources:

| Key | Check |
| --- | --- |
| afek1993snapshots | Six authors, JACM 40(4), pages 873–890, 1993, DOI 10.1145/153724.153741. September is supported by the MIT JACM bibliography. The journal PDF, not the 1990 report, was read. |
| bailis2014ramp | Five named authors and the 2014 SIGMOD title agree with the original PDF. The PDF gives DOI 10.1145/2588555.2588562 and June 22–27, 2014. |
| linuxSequenceCounters | Official documentation title and institutional contributor attribution are appropriate. No invented publication date is supplied. |
| yang2026stateact | Ten authors match the version 1 arXiv page in order. The page gives July 24, 2026 and identifier 2607.22798v1. |
| googleCalendarEvents | Provider and title match. The checked page gives July 7, 2026 UTC as its update date. |
| googleCalendarVersions | Provider and title match. The checked page gives September 11, 2026 UTC as its update date. |
| rfc9111 | Roy T. Fielding, Mark Nottingham, and Julian Reschke match the named RFC editors. Title, RFC number, and June 2022 date match. |
| rfc9110 | The same three named editors, title, RFC number, and June 2022 date match. |

The RFC records name the responsible editors in the author field, as common RFC citations do. The Linux attribution is collective. Neither entry invents a person. Access dates are October 16, 2026.

## Logical claim checks

The derivations use the same gap count, read order, target, and write semantics as the frozen plan. The state contains all fields needed to determine future outcomes. Intermediate write states are included in target existence. The count recurrence preserves multiplicity. The final-vector XOR map supports the atomic-final control count. Full revision accepts only a target initial state and empty gap words. Its rejection count follows from that control identity.

The two-field bound uses disjoint adjacent-read intervals. Each interval must connect `(1,0)` and `(0,1)` through two flips while excluding `(1,1)`. The construction through `(0,0)` meets the bound for a gap budget of two. This proof is not applied to the distinct wrong-at-decision outcome.

The partial-counter argument correctly differs by dimension. With two fields, the fixed covered field is one throughout an accepted history, so a correct read of the other field creates a common target. With three fields, two uncovered fields can alternate. Neither argument claims safety against a later unobserved write.

The report gives the full-revision assumptions in its method and discussion. It does not treat a fresh tool call, a field timestamp, or a content validator as automatic proof of those assumptions. It distinguishes a correct snapshot from lasting persistence.

## Novelty and terminology

The contribution is a fixed synthetic comparison and complete witnesses. The report does not claim a new snapshot protocol, first discovery, natural failure rate, provider defect, or improvement in a language model. It separates two false outcomes and rejects population significance claims. The terms target, revision, snapshot, mixed read, and witness are defined. The use of “agent” in the model description does not describe a live trial; the synthetic scope is explicit.

## Limits of this review

This review does not prove that the cited services supply an atomic whole-record read or an authoritative non-reused revision. It does not independently rerun the complete calculation, validate a PDF, or prove remote publication. Those checks must have their own records. The bibliography supports the sources actually used; it is not an exhaustive literature review.
