# Additional website evidence

Providers: ToolsQA, https://demoqa.com/webtables; SpryMedia, https://datatables.net/examples/core/api/add_row.html. Access date: 2026-10-15. No new license is assigned to the providers' interface material.

The public JSONL files contain the task region from actual browser DOM observations. Each line is one original action, observation, decision, audit, cleanup, or image record. Actions preserve chosen arguments, request start/end times, errors, and before/after task states. Record IDs and trial IDs are retained. The analyzer reads visible row cells and current search, rather than treating the runner's hand count as truth.

DemoQA extraction starts at the Web Tables heading and keeps the table, pagination, and form. It removes the copyright footer line. DataTables extraction starts at Add new row and ends after pagination, before the Javascript/HTML/CSS example tabs. It keeps the search field, all table rows, and the total-entry footer. That total remains visible but is excluded from the supplied rules. Unrelated navigation and published application-code examples are not part of the public state text.

Every state string has an original SHA256 hash. A hash identifies bytes; it cannot prove that an observation is true. Full original observations remain local for review. The evidence manifest has the original and extracted file hashes. An unavailable task region is marked unknown. It is not changed to an empty ready table. Image paths are reduced to their filenames. No action result, time, error, or task row is changed.

The screenshots are direct browser captures. The image manifest states their actual byte format and hash. Filenames ending in .jpg contain JPEG bytes. Each normal trial has decision, pre-reload audit, and post-reload cleanup images. Additional images remain clearly named and timed. A later image cannot replace an earlier decision state. Full private fallback images are excluded from the public archive; their hashes and exclusion remain in the manifest and action log. The corrected task image is a separate later observation.

The DemoQA test emails use example.com, a reserved example domain. The other named rows and addresses are public default sample data. DataTables rows are generated numeric labels. These are not personal records. Scored trials need no login or connected-account data. Reload removes the added rows after the audit and restores the observed default baseline.

The preflight files are separate from scored evidence. The first DataTables later read failed the timing gate. It is retained. No preflight case enters a scored denominator. The saved plan has local freeze hashes, not external preregistration.

Exact browser trajectories depend on hosted page versions, model decisions, and tool timing. A new run can differ. Offline reconstruction checks the archived trial counts without website or account access. Read cross_plan.md and README.md before a new run.
