# Source and claim review

Status: PASS for the files identified below. Review date: October 18, 2026.

A separate Codex agent checked source claims and proofs. This is not human review, peer review, or conference approval. This review does not replace the separate numerical comparison or the remote publication check.

## Scope

Read the final report, README, frozen plan and configuration, source record, bibliography, proofs, and failure record. Checked the six supporting references against the primary source material read on October 18. Exact read ranges are in source_search.md. No source paper code or empirical result was reproduced. The reviewer did not read or import the main calculation program and did not run the enumeration.

## Checks

- The report credits RIFL for the known finite-retention failure. Its citation now matches the limited read of Section 4.3.
- The AWS account is limited to caller identity, atomic effect records, intent, and varying retention requirements. No universal AWS timeout is claimed.
- Stripe v1 is correctly separated from v2. At least 24 hours does not mean an exact deletion time. V2 failed or partly failed work is described within its separate replay contract. Neither provider was tested.
- CapLease and Cordon are identified as preprints. Their assumptions and recovery mechanisms are not presented as failures measured here. Conference acceptance is not claimed.
- The six bibliography entries match the checked titles, authors, versions, dates, URLs, and read scopes. Unknown web publication dates are not invented.
- Additional leads remain in the search record. The expired IETF draft is not called an RFC. Unchecked software results are not used as evidence.
- The contribution is limited to the exact synthetic corpus, comparisons, controls, traces, and proofs. There is no unsupported first-discovery or new-protocol claim.
- Delay-margin and receiver-cutoff proofs state their required capabilities. The initial-send exception and atomic admission/effect boundary are explicit.
- The hand-worked examples are consistent with the model. The algebraic corpus and control identities were derived without the main program. Full numerical reproduction is a separate review.
- The receipt is correctly distinguished from a hypothetical exact-final-count claim. Main and stress are separate. Counts are not provider or model failure rates.
- AI generation and the lack of human or peer review are stated. No account test, source-code reuse, paid compute, or institutional endorsement is claimed.
- The source summaries are short attributed paraphrases. No full source paper or copied source code is included in these reviewed documents. No new license is assigned.
- The frozen plan and configuration hashes still match input_manifest.json.

## Corrections made before this pass

The root agent narrowed the RIFL citation range, changed Stripe v2 wording from unfinished work to failed or partly failed work, and clarified that the abstract refers to two separate safe rules. The source reviewer changed the search record opening to state that the search began before plan selection, with later checks disclosed. These edits do not change frozen inputs or numerical results. No unresolved material source or claim issue remains in these file versions.

## File binding

Any later change to these documents needs a review of the change. Hashes use SHA-256.

| File | SHA-256 |
| --- | --- |
| report.md | `d29a0a893b918012ec39293ce52e79a06642c639ba81b71aedc8d574004522a4` |
| README.md | `31ef7f1fe540dcd823e9d45158b20e7a63b10c40e19cd014669e9041878a42a7` |
| source_search.md | `37e25d69aee1c9ba52aed64e7bd90b10bc5456f4f4b45ba865c81fb05287dcdc` |
| references.bib | `ab9389b1f9a268071c381e6449193cf4b2b945306d8584b24f83fbba4ef22be2` |
| derivations.md | `038fef3484d781069a4dbfd7c20943fa0d347fdc92a579b95f1fe67639eaece1` |
| analysis_plan.md | `221e7665b46898382f325fce76779c8e2a91c12051227685bb5a7d3b8e76cf7e` |
| config.json | `d8160d49b9d68e919903d504df51b8c2d5673658cf5fd734176f23b43200d577` |
| input_manifest.json | `d3635b9d019b3a32dbe0391ef0f3939e300a07c554e2342e1dd47bf6944bb345` |
