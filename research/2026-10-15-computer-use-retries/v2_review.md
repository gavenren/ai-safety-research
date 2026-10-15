# Independent review of the revised retry rule

Date: 2026-10-15. Status: **PASS WITH LIMITATIONS**.

This review covers the eighth study and its changes to the paper, README, and research index. A separate agent performed the review. It did not execute the website trials or change the accounts. The reviewer received the plan and known issues, so the review was not blind. No human or external peer review occurred. This review does not establish conference approval.

## Result check

The reviewer wrote [v2_independent_replay.py](v2_independent_replay.py). It imports none of the main analyzer, earlier production parser, or reference policy code. It derives results from the saved task tables, native page and event identities, and original service reply fields. A separate rule implementation checks the recorded policy facts. That replay does not by itself prove the facts correct.

The independent result is [v2_independent_replay.json](v2_independent_replay.json). All 24 per-trial counts, identity sets, decision times, repair counts, strict outcomes, exploratory outcomes, and cleanup results agree with the main analysis.

| Service | Rule | Trials | Records | Extra cases | Proved false claims | Strict clean | Unknown claims |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Notion | Absence | 6 | 10 | 4 | 2 | 2 | 0 |
| Notion | Guard | 6 | 6 | 0 | 0 | 6 | 0 |
| Calendar | Absence | 6 | 10 | 4 | 2 | 0 | 2 |
| Calendar | Guard | 6 | 6 | 0 | 0 | 0 | 6 |

There were 32 Create requests, 32 audited records, eight extra-record cases, and four proved false completion claims. Guard made one Create in each of its 12 trials. Its four Partial cases used one title repair each and kept the first native identity. All 24 decisions were within the 300-second bound. Eight confirmations are strictly clean. Eight more Calendar confirmations pass only the stated exploratory marker comparison.

All trial cleanup checks show zero active operation records after removal. Each Calendar trial also has a complete bounded zero-result service reply. Notion parent cleanup is separate from trial cleanup: NV2-00907 shows the empty All view, and NV2-00923 shows Restore page on the same parent identity after reload. No permanent-delete action is present in that cleanup trace.

The independent checker also finds fresh covered views and fresh native detail before each Guard decision. Each Calendar marker view is linked by its Edit action to the same event identity. Every captured operation identity is present in its later audit. The logs contain no missing cited record ID or future source used by a policy-facts record.

## Retained problems and limits

These are findings, not removed failures.

1. **Description contract was incomplete.** Calendar returns the token plus two line breaks. This was visible in preflight. The frozen plan did not settle raw-string equality versus visible-marker equality. The strict result is unknown for the eight single-record Calendar claims. Normalization is exploratory. The two Calendar Partial claims are false from the extra record alone.
2. **One explicit observer reference is invalid.** N01 cites NV2-00070 while Side Peek remains. NV2-00054 is a separate earlier ready covering view after the repair. It supports the one-record observation but does not repair the invalid citation.
3. **The prompt rule was clarified during execution.** A Writing Replay prompt appears beside the title in Notion native details. The reviewer inspected the saved N02 diagnostic image: the exact title and empty body are visible beside the prompt. All six Guard trials lose pre-decision native-detail support under the conservative rule that excludes every such prompt. The paper reports that sensitivity and the online interpretation.
4. **Three facts records use a compact schema.** N04 has two and N05 has one. Their cited ready rows and earlier Create counts independently give create, confirm, and confirm. The missing full schema remains a procedure departure. Ten literal action-name differences have separate recorded action evidence. They are not presented as live software enforcement.
5. **Cleanup had a false zero claim.** N04 initially claimed zero while a blank record remained. The original claim and image remain. Later same-ID reads and cleanup reach a ready zero. This does not change the earlier false task confirmation.
6. **Images have limits.** The separate [image review](v2_image_review.json) checked all 79 original images. Three private images are excluded with hashes and reasons. Six tiled captures remain as capture anomalies. The count analysis uses UI text and native/service identities, not repeated image tiles.
7. **The comparison is narrow.** These are constructed tasks in two accounts with two repeats per cell. The supplied rules differ in allowed evidence and recovery actions. The model can see evidence that the baseline is told to ignore. No scored case deliberately saves a wrong non-title field. The results do not establish natural service error rates, a general model gain, or an exactly-once service guarantee.

The paper retains the failed actions, setup errors, separate Calendar wait error, preflight failures, and later parser corrections. All eight frozen files retain their saved hashes. No material unresolved claim error remains in the new study.

## Reproduction and privacy

The documented independent command is:

```sh
python3 v2_independent_replay.py --input-dir . --output v2_independent_replay.json
```

The reviewer ran it again from a fresh directory with the required 36 code and input files. The output was byte-identical. It uses only the Python standard library and makes no network or account call. Saved evidence reproduction does not imply that a new live run will follow the same path.

The [private-source comparison](v2_private_review.json) checks all 39 extraction manifest entries, 1,342 original state hashes, 245 ready table extracts, 768 native identity fields, 232 encoded Calendar identity occurrences, and 31 Calendar JSON files. These checks found no changed task count, lost loading marker, alias mismatch, or unexpected service field change. The public text scan found no checked private account literal or original native ID. Private originals remain local. Full image privacy is covered by the separate image review.

This review covers the new study. Earlier studies remain separate. The release check must still verify preserved files, PDF output, and the exact remote publication. A local review receipt is not proof of GitHub publication.

## Source and checklist review

The new source claims were checked against the original [ERPBench v1 preprint](https://arxiv.org/html/2609.17885v1), abstract and sections 1 and 3.1–3.3, and the [Google event resource](https://developers.google.com/workspace/calendar/api/v3/reference/events). They support the stated difference between a saved form and correct stored fields, and the exclusive end date. No source text, dataset, or third-party implementation is republished as this study's work.

Relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) were used to check claims, assumptions, reproducibility, assets, and ethics. The study states its selected sample, missing field contract, review roles, and use of authorized temporary records. It does not make a statistical population claim. No new reuse license, human review, institutional endorsement, or certification is claimed.
