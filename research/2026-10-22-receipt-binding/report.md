# A receipt must identify both the operation and its intended change

Date: 2026-10-22, America/Toronto. Extra study requested by the repository owner.

## Abstract

A repeated request can reuse an old operation ID with different data. A receipt can then confirm the wrong change, even when no extra effect occurs. We tested five receipt rules on all 256 ordered pairs from a 16-request alphabet. A key shared across accounts gave 112 false success replies. An account-scoped key without a payload check gave 48 false success replies, with zero incorrect effect histories. A rule that checked account, operation ID, and the stored payload matched the contract in all 256 pairs. These are exact counts in a synthetic model. They are not provider or AI-agent failure rates.

## Research question and safety relevance

How do receipt scope and immutable payload checks affect false success replies and repeated effects when a request ID is reused?

A **receipt** is a saved record of a completed effect. An **operation ID**, or key, identifies one intended operation. The **payload** is the target and numeric change. **Idempotency** means that retrying the same logical operation does not add another effect. A **scope** states where an ID has meaning. Here, each account has its own ID scope.

An AI agent can retry a command after a missing response. It can also change a target while retaining an ID. A success reply must support the current intent. Absence of duplicate effects alone does not prove that the reply is correct.

## Related work and contribution

The AWS Builders Library describes caller-scoped request IDs and checks for changed parameters. Stripe's API v1 reference describes replay of a saved result and rejection of changed parameters. These mechanisms are established. This study does not introduce a new idempotency algorithm. [Featonby, AWS](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) [Stripe](https://docs.stripe.com/api/idempotent_requests)

The repository's October 18 retry-retention study used fixed payloads. This note excludes retention and varies identity scope and payload. Its contribution is a complete, paired regression set with separate measures for false replies and effect errors. A limited [source search](source_search.md) does not prove novelty. No fault in AWS or Stripe is alleged or tested.

## Method

The [plan](plan.md), [configuration](config.json), and source log were frozen before implementation. The code hash was saved before the first execution. See [freeze.json](freeze.json) and [implementation_freeze.json](implementation_freeze.json).

Each request is `(account, key, target, delta)`. There are two accounts, two keys, two targets, and two deltas, −1 and +1. This gives 16 requests and 16² = 256 ordered pairs. Each rule receives every pair. There are 1,280 rule cases. The first request always commits. The second request has one of three contract outcomes:

- A new `(account, key)` applies one new effect.
- An existing identity with the same payload replays the first receipt.
- An existing identity with a changed payload returns a conflict and adds no effect.

This is the selected contract, not a claim about every provider. Receipts contain the full request and an effect sequence number. All operations are sequential and atomic. Receipts never expire. A conflict is a refusal, not a success.

The first four rules use different store keys. They replay an existing receipt when that key matches. Otherwise they apply a new effect. The fifth rule stores receipts by `(account, key)` and checks the original target and delta before replay.

The oracle classifies identity and payload equality directly. It does not use the receipt store. It compares the expected second action, full receipt, and ordered effect history. A false success is a conflict reported as success, or a success receipt for another intent. Missing and extra effects are counted separately. Ordered effects remain visible even when opposite deltas cancel in the final numeric state.

Named controls cover exact retries, equal keys in different accounts, changed targets, changed deltas, and new IDs with equal payloads. They are members of the full corpus, not extra independent cases. The hypothesis required the bound-receipt rule to match every case and each baseline to have an error. No random sampling, training, data split, or seed was used. A confidence interval would not describe uncertainty about this fully enumerated set.

## Results

All 1,280 rule cases completed. There were no unscored cases or failed assertions.

| Receipt rule | Pairs | False success replies | Missing effects | Extra effects | Wrong effect histories | Exact contract matches |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Key only, shared across accounts | 256 | 112 | 64 | 0 | 64 | 144 |
| Account and key | 256 | 48 | 0 | 0 | 0 | 208 |
| Account, target, and key | 256 | 48 | 0 | 32 | 32 | 208 |
| Full request as store key | 256 | 48 | 0 | 48 | 48 | 208 |
| Account and key, with stored payload check | 256 | 0 | 0 | 0 | 0 | 256 |

There are 192 new-identity pairs, 16 exact retries, and 48 payload conflicts. The checked rule applies, replays, and rejects those groups, respectively. It does not convert a conflict into a completed operation. [summary.json](summary.json)

For a concrete false reply, first apply `(A,0,x,+1)`, then request `(A,0,x,−1)`. The account-and-key rule returns the first receipt. Its effect history is correct under the contract because the changed payload must not execute. Its success reply is wrong. The full-request rule instead applies −1 as a new effect. The final numeric state returns to zero, but the forbidden second effect remains in the history. [controls.json](controls.json)

The following count check was derived after execution. For each first request, 12 second requests have another identity, one is identical, and three change its payload. Multiplication by 16 gives 192, 16, and 48. The global-key rule also confuses four requests in the other account for each first request, which gives 64 missing effects. Those 64 false replies plus the 48 conflicts give 112. This derivation agrees with the raw cases.

Both planned executions used unchanged Python 3.13.7 code on macOS 26.7.2 arm64. The first used 0.039504 CPU seconds; the repeat used 0.037740. All four deterministic result files matched byte for byte. The repeat is not a second sample. [reproduction.json](reproduction.json) records hashes. The execution receipts record exact commands, versions, and times.

## Discussion

The account-and-key rule has no incorrect effect history in this corpus, yet it gives 48 false success replies. Thus an audit that checks only duplicate effects can miss incorrect completion claims. Adding payload fields to the store key also has a limit: it can turn conflicting changes into distinct effects. Under this contract, the payload is a condition to validate, not an extension that creates a new identity.

The checked rule succeeds because it implements the declared sequential contract. The result is a regression test and a counterexample set. It does not prove a new general safety property.

## Limitations

The corpus has only two requests per case. Atomic writes, permanent receipts, correct account identity, and exact equality checks are assumptions. Crashes, races, expiry, hash collisions, authorization, transport faults, and uncertain effects are absent. No live service, browser agent, connected account, or language model was tested. Counts depend on this artificial alphabet and are not real-world probabilities. A different API contract can correctly allow a different result.

## Ethical and misuse considerations

The study uses new synthetic values and local code. It has no private records or external effects. No service was purchased. The main misuse risk is to call these counts provider faults or a general safety guarantee. Sources are linked and paraphrased. No external code, figures, or dataset are redistributed. No new license is assigned to the owner's work.

## AI use and review status

Codex generated the study, code, analysis, and report. Web search checked primary sources; local Python executed fixed rules. No model was called inside a trial. The exact runtime model build was not exposed and is not an experimental variable. A separate Codex agent checked all 1,280 saved outcomes with its own evaluator, checked the report and original sources, and found no material error. The [review record](separate_review.md) states the review limits. No human review or external peer review occurred. The NeurIPS checklist is a review aid, not approval or certification.

## References and reproduction

See [references.bib](references.bib) and [source_search.md](source_search.md) for checked sources and read scope. Follow [README.md](README.md) to repeat the run. [cases.jsonl](cases.jsonl) contains every request pair, rule output, oracle result, and score. [checks.json](checks.json) records the built-in checks.
