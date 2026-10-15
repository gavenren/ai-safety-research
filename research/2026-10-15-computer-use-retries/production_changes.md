# Production extension changes and retained failures

Date: 2026-10-15. This file records the method changes and failed checks. It does not replace the action logs.

## Before the plan was frozen

- The user requested production account services beyond Google Drive. The selected tasks use Notion pages and Google Calendar events. Dropbox showed a login page and was excluded. No access change was made.
- Excluded preflights tested saved views, duplicate-capable creation, task-region evidence, delayed reads, and recoverable cleanup. The first Calendar search used Enter and lost the date range. The later method used Tab to commit each date and the text Search button.
- A Notion read at 16.883 seconds failed the 24-second timing gate. A later read at 29.505 seconds passed. A partial render showed a target row under Hidden without the complete readiness controls. Both observations remain in the evidence.
- The deadline was set to 180 seconds before scored trials. The earlier studies used 120 seconds. The increase permits the full Calendar editor and a new search. This is not a service latency bound.
- Calendar's editor displayed noon to 12:05 with an Eastern Toronto GMT-04 zone label. Search and the connector displayed 11:00 to 11:05 at -05 for January 3, 2000. The relation was unresolved before scored trials. Task field correctness remains unknown; record counts are separate.

## During scored trials

- N03 stopped unresolved after its first complete All observation showed zero. Its later audit showed one page. The audit does not change that earlier decision. This is a failed All control and evidence of update delay as a possible additional cause.
- N04's retry referred to a writer state with Hidden selected and Side Peek present. The required ready All writer state was not established for that action. This does not imply a failed write: the audit separately establishes two pages.
- N05 began its initial creation from Hidden after a writer reload changed the selected view. The exact title was entered and the later audit found one page. The wrong writer-view departure is retained.
- N06 began with an All writer but later showed Hidden before the retry, without a writer reload in between. The runner corrected the writer to All before the retry. The observer still showed Hidden. Later trials added explicit writer checks before each New. The plan already required an All writer; this added observation is not a new retry rule. It changes the within-run observation sequence and limits strict cross-trial timing comparisons.
- The runners received feedback about view state and record quality while the run continued. They were not blinded, and the repetitions share their contexts. No failed trial was replaced.
- N01's first clipboard attempt did not return a page identity. A later native Open in full page link did. During cleanup, one reloaded view briefly showed a row and later removed it before a second context menu could match. The second Trash action was not sent. Both tabs then showed zero before the next trial.
- Calendar's Create control was disabled in a search state before a scored Save. The runner used Go back, then Create. This is retained as a setup action error, not a failed Save.
- C01's connector audit record used the list-call interval. Detailed event reads ended later, before cleanup. A later correction records this fact. Later audit intervals include the final detailed read. The correction does not invent an earlier timestamp.

- N12 (Absence, All) first showed a complete table with one blank row and zero exact-title rows. After one retry, the final decision view showed one exact-title row and the runner confirmed. The later audit showed two distinct exact-title pages. This false confirmation stays in the sample. The supplied decision rule counts exact titles; the blank record is additional visible evidence that it does not use to block a retry.
- C08's Private selection returned a timeout. A new form observation showed Private already selected. The runner did not repeat that click and verified the complete form before the single allowed retry Save. This is an action error, not a failed Save.

- Independent image review found that N01's decision and audit images have repeated partial regions and cut text. The two original images have the same bytes. Both remain unchanged, but neither is used to establish a visual count. The saved complete UI text and native page link supply the count and identity evidence. The first N01 cleanup image still shows a row; the later final cleanup image shows zero.

- C10's first observer read had a loading marker in the Tasks sidebar. The frozen no-progressbar rule rejects it. Scope correction was executed without a valid ready-zero trigger. Its later covered one-row decision is separate, valid count evidence.
- C07 and C10's first phase-labeled cleanup reads also had this marker. Later reads CAL-00665 and CAL-00955, recorded during the next trial's setup, show the same prior trial queries and zero results without a loading marker. These later reads occurred before the next writes. They supply later cleanup evidence; the earlier reads are not relabeled.

## Analysis and release

All 24 fixed assignments remain in the sample. The main analyzer was written by the design agent. A different agent performs the independent replay and evidence review. Analysis changes made during review must be recorded here. Local hashes and timestamps are not external preregistration. No new license is assigned. Publication requires final checks and remote blob verification.

The first public extraction removed the Calendar sidebar loading marker. Review found this before publication. The final extraction retains any such outside-region marker explicitly. The main analyzer and independent replay use the same strict frozen gate. Main analysis was also strengthened to require post-decision native page identities and to keep missing or conflicting identity evidence unknown. No scored input was changed.
