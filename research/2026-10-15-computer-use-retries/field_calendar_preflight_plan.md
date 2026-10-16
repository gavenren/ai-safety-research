# Excluded Calendar field preflight

Create at most one temporary event through the signed-in Calendar browser. Title: FC-PREFLIGHT-20261015-CALENDAR. Initial description: FC-PREFLIGHT-MARKER-A. Use All day, Oct 14 2026 for both visible dates, Free, Private, no guests, location, conference, reminders, or recurrence.

Reload saved native detail. Save the raw browser fields and read-only connector search and read_event replies. Record field types and absence of fields. Replace the full description on the same native event ID with FC-PREFLIGHT-MARKER-B once. Reload and repeat the reads. This checks whether full replacement leaves extra text and whether boundary line breaks persist.

Proposed comparison: remove only boundary CR and LF characters from a string; preserve case, spaces, tabs, markup, and all interior characters. Do not turn null into an empty string. Read All day and inclusive dates in the reloaded UI. Check the connector boundary representation separately without an assumed time zone.

Move the event to recoverable Trash through the browser. Verify no active record through a loaded covered search and a read-only bounded connector query. Preserve raw data, errors, and capture times. Do not start scored trials until the parent freezes the plan.
