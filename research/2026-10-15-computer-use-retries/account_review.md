# Independent review of the authenticated account experiment

Date: 2026-10-15. Status: **PASS for the stated, limited results, with the defects below retained.**

A separate Codex agent made this review. This agent did not design or run the trials and did not write the author analyzer. The review is not human or external peer review. It covers the new 30-trial account experiment, the new report claims, privacy edits, and preservation of earlier evidence. PDF layout and GitHub publication have separate checks.

## Evidence and independent calculation

The reviewer read the saved plan, all 30 assignments, both complete private action logs, both current result files, the original invalid B exports, and the explicit correction records. The reviewer then wrote `account_validate.py` without importing `account_analyze.py`. It counts exact folder rows inside Item List, excludes the focused-row echo, and treats a loading screen as unknown. It reads action times, full observations, decision times, and the later connector records.

Run:

```sh
python3 account_validate.py --fresh-copy
```

The result is saved in `account_validation.json`. All **1,831 checks pass**. This includes 12 parser checks, all 30 trial paths, plan hashes and timing, all 24 matched comparisons, author-output agreement, and two separate temporary-copy reproductions. Both reproductions give byte-identical trial tables, summary, and pair tables. A second full validator run also gave a byte-identical validation file. These checks do not erase observed plan deviations.

The independent result agrees with the author result:

- 30 trials have one matching row at the first decision and one distinct record in the later connector audit.
- All 30 confirmations are within 120 seconds. No retry occurs. No trial has a zero-record or duplicate-record outcome in this finite audit.
- All 12 All-view core controls pass. The six Receipt controls have both a matching row and an exact-name receipt.
- Decision times range from 6.333 to 15.028 seconds. They are wall times, not service latency.
- Both directional comparison criteria, H-A1 and H-A2, fail to show their required positive difference. The intended hidden-folder condition is absent at every first decision. This is not a successful causal test of retry safety under a hidden result.

The connector read occurred after all trial decisions and per-trial browser audits. The reviewer compared all 30 public record aliases, names, types, creation times, and sharing fields with the private connector replies. All match. The four blocks have 8, 8, 8, and 6 records. The read capacity was 100 per block. The finite read and matching browser lists support these test counts. They do not prove indefinite durability or a permanent end to execution.

## Defects and claim limits

Two pre-write absence checks are not verified. D02 and D06 show the Documents filter but no usable list or empty-result message before Create. Their baseline counts remain unknown. They remain in the outcome table. The report now states these plan deviations. No loading screen was counted as zero.

Only D02 explicitly shows All in the first-decision filter toolbar. The other 29 first-decision states do not show the toolbar. All 15 Documents assignments nevertheless show the matching folder. This supports a visible result at decision time. It does not establish the precise filter transition or its internal cause. Runner annotations that say All do not replace the observed toolbar evidence.

The initial A logger label and early B labels were stale. The reviewer checked the correction line ranges, time bounds, unique names in the UI, and explicit decision records. The raw text remains unchanged, apart from the declared privacy edits. The invalid exports remain clearly marked and are not scored inputs. The saved action summaries do not independently capture complete tool-call code or model-turn boundaries. The report states this limit.

D16 and D18 each have one browser-read error during the post-decision audit. The later ready reads show one matching row. There is no subsequent creation action. These errors do not become decision failures, and they are not omitted.

No trial reaches a zero-count retry condition. All six Receipt controls also have a visible row. Therefore, zero duplicates cannot establish the safety of an absence-based retry under uncertainty, and these controls cannot establish a benefit from a receipt alone. The report keeps the 30 account trials separate from the earlier 60 public-site trials and 18 local trials. It makes no population error-rate, speed-improvement, or new-protocol claim from these account results.

## Image review and privacy

The reviewer opened all 27 retained original per-trial images. Each agrees with its correct post-reload text audit. D11, D12, and D13 original per-trial images are missing. The existing file named D11 shows D14. It is not counted as a D11 image. See `account_image_review.json` for the file hashes and mapping.

The reviewer also opened the four public block images and the cleanup image. The block images show all 30 planned names in the correct blocks, with no duplicate row. They were captured later and do not replace missing original images. The cleanup image shows the exact test parent under Trash. It does not show permanent deletion. The public clips exclude account name, email, private folder IDs, and storage usage. The owner label `me` and a single avatar letter remain.

The reviewer compared 11 public text files with their private originals. All 449 non-string scalar values are unchanged. The 281 changed string values contain only the declared privacy replacements. No action, count, timestamp, correction, or test-name field changed. The reviewer also checked hashes and scanned the new text for private IDs, account details, and live credential patterns. The check found no remaining value in those categories. Private source files and full images are not part of the public package. See `account_private_evidence_review.json` and `account_redaction_manifest.json` for the dated check.

## Earlier evidence and report

The earlier package has 110 files. The 98 protected evidence and code files are byte-identical. Only report, bibliography, README, PDF, and declared review/build/release metadata can change. The comparison records its time and lists the permitted changes. Old review hashes refer to the corresponding older paper version.

The reviewer checked the revised abstract, contribution and related-work text, Section 8, the relevant limits, ethics text, and account evidence notes. The result table, defect counts, timing range, and interpretation agree with the evidence. Two method sentences were clarified to distinguish the required baseline check from its two failed verifications and to make filter removal conditional. Codex use and the lack of human review remain explicit.

The account result is suitable for publication as a limited transfer test with a negative comparison result. It is not proof that the retry rules are equal, safe on other websites, or effective under uncertain execution. No material evidence error remains in the stated account results. PDF layout, repository history, final package hashes, and remote publication must still be checked by the lead's release procedure.
