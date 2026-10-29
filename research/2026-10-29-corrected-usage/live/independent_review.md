# Independent source and decision check

Date: 2026-10-29. Status: passed for the scope below.

The formula evaluator was saved and frozen before the reviewer read the new live implementation or its results. The inherited chat did contain an excerpt of the original study code. Thus, this was a separate implementation check, but it was not fully blind to the original method. The evaluator uses prefix sums, prefix minima, and record selection. Its frozen file did not change.

The review checked 24 saved versions of 12 source records. It compared the public names, source labels, times, and evidence hashes with the private exact-record connector reads. Both versions of each source used the same provider record. Version 1 was read before version 2. All 12 corrected names also appeared in the saved browser evidence. The review checked the unshared Drive parent relation. It checked private Calendar status, the saved numeric time interval, no other attendees, no recurrence, no reminders, and no meeting link. Browser evidence showed Free and Private. The raw Calendar response did not show a named time zone; this review does not claim that it verified one.

All 36 rule decisions matched the frozen formulas. All 192 prefix balances, duplicate flags, event labels, and received-ID sets matched. The comparison also covered final balances, errors, admissions, excess credits, and feasible refusals. In total, 1,674 assertions passed. See `independent_checks.json` for the counts and file hashes.

The first audit adapter run failed because the adapter expected an output name for a refusal. The actual data schema uses `null` for a refusal. The adapter was corrected. The frozen formulas and the experiment data did not change. This adapter correction was made after the data became available. It is separate from the frozen accounting evaluator.

At this review stage, output actions and cleanup were not checked. An admission in this file is a local decision, not proof of a saved website change. A later action audit must check that distinction before publication.

The selected cases use real saved Drive and Calendar fields. Test credits, ordered source labels, closure, and delayed or repeated delivery remain study data. They are not provider billing fields or provider guarantees. These results do not estimate the rate of failures in normal website use.

Codex performed this check. No human review or external peer review occurred.
