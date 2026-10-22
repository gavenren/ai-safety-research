# Separate review of the receipt live extension

Date: 2026-10-22. Outcome: pass within the stated limits.

A separate Codex agent reviewed the raw local records, the public evidence, the scoring code, and the report. The reviewer did not make account calls or account changes. This is an AI review. No human review or peer review occurred.

## Method

The reviewer wrote `review_receipt_audit.py` without imports from the author's code. The reviewer had read that code before writing the audit. This was not a blind test or a plan saved before the trials. The audit compares the actual native record IDs with the private fixture list. It checks the recorded UI fields, dispatch, first saved-state read, local receipt decision, and final read. It checks the full exposed record fields and their allowed changes. It also checks the frozen helper hashes, time order, and the public evidence file hashes.

The audit passed 475 checks across all 12 cases. `review_receipt_audit.json` contains the check list. The public scoring procedure also reproduced `live_results.json` byte for byte in `review_reproduced_results.json`. The raw audit needs private account evidence. The public scoring procedure needs only the published alias evidence.

## Supported results

There are 12 cases and 16 distinct temporary records. There are 12 logged first browser saves and no logged second browser saves. The key-only rule returned success for four changed requests whose requested saved state did not match. The bound rule returned conflict for those four changed requests. Both rules returned success for the four exact requests. Each decision matches the corresponding saved-state evidence and rule.

All exposed first-read fields equal the corresponding final-read fields. The first save changed only the allowed fields: title and modification time in Drive, or description in Calendar. The four alternate target records retained their exposed baseline fields. These comparisons support the reported local decisions. They do not prove that Google made no hidden internal writes or that a provider has an exactly-once guarantee.

The corrected runtime helper hash is `4019197c40a9fa6117a835c88960bf058a9ea78bc84a8e3e3306d721ad25df66`. The helper freeze precedes the recorded before-save UI evidence in all 12 receipt cases. The audit found the required action evidence, saved-state gate, ordered local decision events, and later readback in each case. The local helper did not dispatch a second action.

## Failures and procedure limits

The first Drive exact case timed out during reload after Save. Its first-read file is a byte copy of the retained interruption read. These two files are one observation. No repeat Save is logged. The failed reload start time is not available, so compliance with the planned 30-second uncertain-state check cannot be established. The report retains the case and marks its timing check as unknown. All four false claims remain in the 11-case subset with a known timing check.

The six Calendar saves have no reopened post-save editor record. The reviewer requested an explicit procedure deviation, and the report and README now contain it. The persisted description and other exposed fields have connector readback. The all-day UI evidence is from before Save. A post-save all-day UI check is not available. The 11-case timing subset is not a subset that passed every planned procedure step.

The metadata baseline is from setup, about 27 to 33 minutes before the cases. It is not an immediate per-case baseline. Fresh UI observations support the before-save field checks. Absent connector fields remain unverified. The report identifies the missing Drive trash and version fields and the missing full Calendar conference, version, and calendar-container evidence.

The policies are local receipt rules. These trials do not test a Google idempotency API, receiver-side atomic fencing, multiple accounts, concurrent writers, receipt expiry, or process-crash recovery. Both sites belong to one user. The selected cases give counts, not an estimate of a production error rate.

## Sources and publication checks

The reviewer checked the relevant original AWS, Stripe, Google Drive, Google Calendar, and NeurIPS pages. AWS describes rejecting changed parameters with a reused client request ID. Stripe API v1 describes parameter checks for a reused key. These sources support the prior-work scope. They do not establish that these local rules are new. Google field definitions support the stated field checks and their limits. The NeurIPS checklist was a review aid, not an approval or submission claim.

The exact-value privacy scan found no tested private native IDs, parent IDs, resource URLs, or account email addresses in this public package. This is a bounded scan, not proof that every possible private string was excluded. The evidence and report were also inspected for unsupported novelty, copied source passages, and unsupported completion claims. No material issue remains in the reviewed study claims.

The shared cleanup summary reports removal from the stated active scopes. This reviewer read that summary but did not independently audit its raw cleanup evidence. Root must add the verified cleanup status and completed review status during final integration. A public GitHub commit was not checked in this review.

## Reproduction

From this folder, with the private evidence in the parent's `private` folder:

```sh
python3 review_receipt_audit.py
```

With public evidence only:

```sh
python3 live_receipt_analyze.py --evidence live_evidence.json --output review_reproduced_results.json
cmp live_results.json review_reproduced_results.json
```

Reviewed scoring code SHA-256: `76f6abef638cab52866aa2f866b498ea7947cdfb9d12e10f33b6dbdeaf073bb9`.

Reviewed public evidence SHA-256: `0a9f97f6d2d15c4a9d3a25dae91cc3f1aebbad79fc3177d71b276bbc0c42037f`.

Reviewed public result SHA-256: `d92255bee0768bb5245be1defe422ce61faff4c3f60fc58c947b9cbd005099aa`.
