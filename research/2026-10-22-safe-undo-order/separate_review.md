# Separate agent review

Date: 2026-10-22. Reviewer: a separate Codex agent assigned to the overlapping-gates study. This agent did not write the safe-undo-order study. This is AI review, not human review or external peer review.

## Result

Pass within the declared finite scope. No material method, result, proof, or source error was found. The main agent must still perform its final package and remote publication checks.

## Review method and evidence

The reviewer read the frozen plan and configuration, source-search record, main program, report, analytic derivation, README, validation note, deviations, and execution evidence. It then wrote [separate_audit.py](separate_audit.py). The audit does not import or run study.py. It audits the saved rows, with states represented as sets of field names and a bottom-up set of states that can reach the goal. The main program instead uses integer bits and forward graph traversal.

The [audit receipt](separate_audit.json) records successful checks of all 1,179 saved rule cases and all 4,042 states in those traces. It compares actions, candidate checks, status, path validity, goal completion, initial and final reachability, and avoidable-dead-end labels. It also checks all 6,963 field-name transformations against other saved rows. All rule, priority, smaller-control, and condition totals agree. The first recorded witness and its two paired cases agree. All primary report table cells agree with the audited summaries.

The frozen input hashes and implementation hash match. Both execution receipts use the same source hash and stay below the resource limits. The five deterministic reproduction hashes match the package. No third full study run occurred during review.

The reviewer read the main code before writing the separate audit. This was not a blind evaluation. Independent authorship and a different state representation reduce some implementation-error risks, but do not remove errors shared by the specification.

## Proof checks

The three-bit graph has three two-bit states, three one-bit states, and six possible edges between the groups. Counting state sets with no selected edge gives 8 + 6 + 3 + 1 = 18. Thus 46 of 64 conditions allow a complete safe path. Each fixed order needs exactly two particular intermediate states, so 16 of 64 conditions permit it.

For one priority, the first available upper state has 8, 4, or 2 stopping conditions, depending on its position. Three, one, or zero of these have an alternative complete path. This gives 14 partial stops, four avoidable stops, eight initial refusals, and 42 completions. Field relabeling preserves the count for each priority. The report's aggregate totals follow by multiplication by six.

The smaller-size argument is valid. With two bits, every valid first step leaves one bit, and clearing it reaches the required valid goal. With one bit, the first action reaches the goal. The three-bit witness is therefore the first possible dimension under the declared one-way action model. It is not a claim about minimal real-world workflows. The report states that limit.

## Original sources

The reviewer reopened the following originals on 2026-10-22:

- [Sagas PDF](https://sigmodrecord.org/?download_id=11106&smd_process_download=1), Introduction, published pages 249–250. Each subtransaction preserves consistency, and compensation has a semantic meaning. The report correctly avoids presenting the toy result as a defect in Sagas.
- [FF author's page](https://fai.cs.uni-saarland.de/hoffmann/ff.html), General Information and Basic Principles. It discusses goal order, dead ends, and complete-search fallback. The report clearly distinguishes its fixed controller from FF.
- [UndoBench v1](https://arxiv.org/html/2610.05622v1), abstract and Sections 2.1–2.4. The source separates state conditions and effect history. The report imports no source performance result and identifies the preprint.

The limited source claims are supported. No global novelty, new planning algorithm, production-site result, or measured AI-agent performance is claimed. Source material is paraphrased, attributed, and not redistributed.

## Final editorial action and limits

The author can replace the prospective review wording with this completed review and link the audit. No numerical, model, source-code, or result correction is required. Keep the no-human-review statement.

The finite-corpus and complete-knowledge assumptions are clear. Refusals, partial stops, target restoration, and valid completion are kept distinct. No secret, private account record, copied long passage, new license, or actionable production exploit was found. This content check is not a security or standards certification.
