# Independent agent review

Date: 2026-10-26. Reviewer: a separate Codex agent, `calendar_zone_audit`.

## Scope and method

The reviewer saved expected decisions before the new account evidence. The reviewer did not create events or run the account actions. The review checked the frozen plan, copied adapter, case matrix, create and read replies, exact event editor captures, local evidence changes, decision outputs, and cleanup replies.

The review used a separate audit script. It checked expected decisions directly. It did not use the adapter under test to calculate the expected outcomes. Private IDs and full account captures were read locally. They are excluded from this public note.

## Evidence result

All 558 audit assertions passed. These assertions are evidence checks, not 558 website trials.

- The freeze preceded all 12 event creates. The copied adapter matched the repaired adapter without changes.
- The 12 new records had distinct exact IDs. Create replies, reads, titles, and editor links matched the same records.
- All non-zone fields matched their targets. Both New York controls retained the same returned start and end times as the Toronto targets.
- The real editor showed Toronto on 10 records and New York on two records. Both start and end labels were checked.
- The 12 connector-only evaluations preceded the editor zone reads. All 12 were rejected.
- In the assigned conditions, two complete controls were accepted. Ten missing, incorrect, or unverified evidence inputs were rejected.
- With complete exact-record evidence, 10 correct records were accepted. The two wrong saved zone names were still rejected.
- Eight records changed from rejection to acceptance after the complete evidence was supplied. The two positive controls were accepted in both phases.
- The 36 evaluations produced 12 accepted outputs on 10 distinct records and 24 rejections. The expected rejection reasons, proof fields, payload hashes, and evidence hashes matched.
- All 12 exact IDs returned `cancelled` after deletion. A later search returned no active events and no next page in the declared marker and date range.

The full public-safe check list is in [audit_results.json](audit_results.json).

## Limits and review status

This is a small selected test in one connected primary Calendar. The repeated evidence phases use the same 12 records. They do not estimate a production failure rate.

The absent or corrupted evidence inputs were controlled local changes. The two New York cases were actual saved zone-name mismatches. They did not have incorrect clock times. The adapter trusts the evidence producer. This review does not establish evidence authentication, freshness, protection from simultaneous edits, or an atomic snapshot across tools.

The private source captures are not included in the public package. Their published hashes permit later comparison with the retained captures but do not let a reader inspect those private captures from the hash alone.

## Final text and reproduction review

The new paper section and reproduction guide agree with the audited evidence. They distinguish 12 new records, 36 dependent evaluations, 12 accepted outputs, 10 accepted records, and eight changes from rejection to acceptance. They retain the seven earlier unsupported outputs. They distinguish actual wrong saved zone names from local evidence changes and correct numeric times.

The reviewer also ran the public analysis once. Both output files matched the saved summary and decision table byte for byte. This was an additional local replay, not another account trial. The public analysis contains no network call or account action. Public action and cleanup extracts match their retained private source files. The displayed create-status absence is preserved as null and is not replaced with an invented create reply.

The review found no material error in the new result claims. The public files were checked against all new private record IDs, event URLs, and the account email. None were present. Source bibliographic checks were assigned separately; this evidence review does not claim to have read every cited paper.

No human review or external peer review occurred. This note is not a certification.
