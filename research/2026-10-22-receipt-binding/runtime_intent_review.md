# Separate runtime-helper review

Date: 2026-10-22. Reviewer: a separate Codex agent. No human review occurred.

Current status: PASS after the correction described at the end of this file. The initial review below is retained. The reviewer made no account calls and ran no real-case prepare command.

Initial status: NEEDS ONE CORRECTION before receipt cases use this helper as their evidence gate. Cancellation preparation, receipt binding, and cooperative file protection passed review.

Reviewed runtime SHA-256: `4eec25d134dacf73e2504cf0dbabb71a48f311c71d74ff87cae6ff6d378a0858`.

## Material issue: the first-read gate is incomplete

`check_first_read()` checks UTC format, rejects a future timestamp, and checks fields. It does not establish that the read followed the first browser save. It also does not require the parent's UI evidence for active Drive state or Calendar all-day state. `receipt_prepare()` passes this field-check result as `evidence_complete` to the receipt rule. It can therefore return success with required first-operation evidence absent.

The reviewer used only synthetic fixtures from `check_runtime_intent.py`. For each provider, the reviewer supplied the exact expected PAYLOAD-A fields with read time `2000-01-01T00:00:00+00:00`. No browser-action record or UI evidence was supplied. Both calls returned true with no errors. No account record was read or changed in this test.

The README correctly assigns these checks to the parent, but the helper does not consume their result. Before receipt preparation, require recorded evidence that the first browser save occurred, the independent read followed it, and the required UI checks passed. A mandatory parent gate can carry these references and times. Missing, stale, or contradictory evidence must give UNKNOWN. Do not substitute the helper's preparation time for the browser-action time.

Add negative synthetic checks for a read before the first save, a missing first-save record, and a failed or missing required UI check. Freeze the corrected helper before its dependent live cases. The pure receipt rule does not need to change.

## Checks that passed

The reviewer ran `python3 check_runtime_intent.py`. All 150 synthetic checks passed. All file writes in that program were in a temporary directory. These are helper checks, not production trials.

C1 checks generation 0 before local cancellation and reuses the result. C2 checks it again after restart and blocks it. C3 records its final check before cancellation and retains the admitted old command. C4 admits generation 1. The helper leaves actual browser action times and saved outcomes unset. Its timestamps are local helper event times, not invented website times. The sequence numbers give the recorded event order. These checks do not establish an atomic provider fence.

Receipt envelopes bind service, account alias, operation ID, native target, action, and suffix payload. Changed-target cases change the native target while preserving PAYLOAD-A. Drive renders the requested suffix under the selected target's fixed alias prefix. Changed-payload cases change PAYLOAD-A to PAYLOAD-B. The weak key-only result and bound conflict result agree with the frozen rule. No receipt outcome admits a second browser mutation.

The code verifies the frozen pure-rule hash. New case files use an exclusive lock and reject an existing complete or partial record. The helper writes a same-directory temporary file, flushes it, and replaces the current file atomically. This protects complete-file visibility and cooperating writers. It is not a demonstrated crash-durability protocol: the parent directory is not fsynced, and an abandoned lock requires inspection. No crash-durability claim should be added.

Malformed saved fields and unknown identities are rejected. Calendar description comparison removes only trailing CR and LF. Drive metadata does not pretend to expose omitted trashed or version fields. These strengths do not remove the first-operation evidence gap above.

## Review boundary

The reviewer read the implementation before the synthetic checks. This was not a blinded review. No source or account state was changed. The review does not verify real first saves, later readbacks, cleanup, or publication. After the gate correction, rerun the synthetic checks and review the new freeze hash before use.

## Correction review

Corrected runtime SHA-256: `4019197c40a9fa6117a835c88960bf058a9ea78bc84a8e3e3306d721ad25df66`. The current freeze at 16:29:21 UTC matches this file and all other listed files. The original runtime file is retained as `runtime_intent_v1_not_for_use.py`; its hash matches the initial reviewed version above.

The corrected helper requires the recorded before-save UI fields, native identity, provider URL identity, a matching dispatch label, a postclick UI record, and an existing raw UI source reference. It checks the order UI observation <= dispatch <= postclick observation <= independent read <= preparation, with UTC times and an eight-minute limit. Calendar requires a Boolean all-day value, Free, Private, and exact PAYLOAD-A. Drive requires the active parent and exact rename input. Receipt preparation now requires both the saved-field gate and the action-evidence gate.

The reviewer inspected the correction and reran `python3 check_runtime_intent.py`. All 192 synthetic checks passed. These include the old-read case, wrong UI target, missing raw UI source, and a numeric value supplied instead of the required all-day Boolean. The original gap is resolved for this declared recorded-evidence interface.

The helper checks recorded observations and references. It cannot authenticate an observer or prove the contents of arbitrary source files without a separate evidence review. Actual browser action logs and saved records still need review before a live result is published. No real prepare command, account call, or account change occurred during this correction review. No human review occurred.
