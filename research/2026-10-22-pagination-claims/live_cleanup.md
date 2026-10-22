# Cleanup evidence, 2026-10-22

The pre-cleanup identity sets matched the 21 created Drive folders and 23 created Calendar events. No other record was selected.

The browser moved the Drive parent to Trash. Its 20 descendants remained in that folder. A later exact-ID DOM read showed the parent in the Trash view. The active marker query then returned zero folders with no continuation token. The Trash-filtered connector query returned zero despite the parent being visible in Trash. It is not used as a Trash inventory. Descendants were not each opened in Trash.

The Calendar connector deleted all 23 temporary events through the normal event-delete action. Each exact-ID read then returned status cancelled. A marker query in the primary calendar, bounded to October 1–3 in Toronto, returned zero active events and no continuation token.

These checks establish removal from the stated active test scopes. They do not establish permanent erasure or an account-wide inventory. No permanent-delete or empty-Trash action was used. Restoration was not tested. The private record IDs and UI text are retained locally. The public JSON contains counts, limits, and source hashes.
