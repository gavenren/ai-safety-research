# Separate agent review

Date: 2026-10-22. Reviewer: a separate Codex agent assigned to the overlapping-gates study. This agent did not write the receipt-binding study. This is AI review, not human review or external peer review.

## Result

Pass within the stated finite scope. No material result, method, source, or claim error was found. Publication still requires the main agent's final package and remote verification checks.

## Evidence checked

The reviewer read the frozen plan, configuration, source record, main code, complete report, reproduction instructions, references, resource deviation, checklist, and execution receipts. The reviewer read the original AWS article's request-identity and changed-intent discussion and the current Stripe API v1 idempotency reference. These sources support the limited prior-work claims. The report makes no claim that either provider uses a faulty baseline.

The reviewer wrote [separate_audit.py](separate_audit.py). It does not import or run study.py. It uses direct two-request equality cases and closed-form effect histories. It compares every saved receipt, action, effect list, oracle class, and score. The [audit receipt](separate_audit.json) records:

- 1,280 unique rule outcomes from 256 request pairs.
- 11,520 row comparisons and 25 named control rows.
- Exact agreement with all summary totals and the independent count argument.
- Matching frozen-input and code hashes, both execution output hashes, and repeat-file hashes.

The independent count argument gives 192 new identities, 16 exact retries, and 48 conflicts. The global-key rule adds 64 cross-account false replies and missing effects, giving 112 false replies. The account-key rule keeps the correct effect history in every pair, but falsely accepts all 48 conflicts. The table and example match these facts.

The resource-check limit is explicitly disclosed: the code checks 60 CPU seconds after computation instead of installing an interrupt. Both observed runs were below one CPU second. This is not a hard-timeout guarantee. No run was added during this review.

## Review limits and edits

The reviewer read the main code before writing the separate evaluator. This was not a blind evaluation. The evaluator is a different implementation by a separate AI agent in the same session. It does not establish real service behavior, performance, authorization correctness, or safety under crashes and races.

The reviewer changed only the prospective review sentence in report.md to record the completed review. No frozen input, study code, or result was changed. The report retains synthetic-scope limits and AI/no-human-review disclosure. No copied passage, private record, credential, new license, or unsupported novelty claim was found in the reviewed package.
