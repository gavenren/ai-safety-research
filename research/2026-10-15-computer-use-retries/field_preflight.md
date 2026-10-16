# Excluded setup tests

Both setup tests occurred before the scored plan freeze. They are not scored trials. They used separate temporary records and recoverable cleanup.

## Calendar

One all-day event on October 14, 2026 used a plain marker. A reloaded native editor showed All day checked and October 14 as both displayed dates. The description did not appear in the accessibility text. A read-only query of the visible Description textbox returned its exact marker in innerText, textContent, and innerHTML. The detailed connector returned that marker followed by two LF characters. The connector returned start 2026-10-14T00:00:00 and end 2026-10-15T00:00:00, without an all-day flag or timezone field.

One full-value description replacement retained the same native identity. A new saved editor read and connector read showed the replacement. Evidence includes FCP-0051/0052 and FCP-0064/0065. Recoverable cleanup ended with ready browser zero at FCP-0079 and an empty bounded connector search without another page. One menu-open error before dispatch is retained; the later fresh state supported a menu retry. Effective saves were not repeated.

These observations justify the prospective two-channel date contract and narrow trailing-CR/LF description rule. They do not establish how every rich-text description or date type behaves.

## Notion

A new private database has a Text property, Marker, and a Checkbox property, Verified. One preflight page showed correct fields at NFP-00066, saved wrong Marker and checked Verified at NFP-00104, and corrected fields on the same identity at NFP-00127. Marker values appear as the property value button; Empty is an explicit empty value. Verified appears as a checkbox, with its checked state. The page body has the empty-page prompt. The native title can also be read from the visible title textbox.

An immediate reload after Enter returned the old Marker value, although the prior editor showed WRONG. The image labeled saved-marker-mismatch actually shows a match. Both the failure and misleading label are retained. Scored reads therefore require a closed property editor, native title/header, complete properties, and a fresh reload. A setChecked(false) call reported an error, but the next state and reload showed unchecked. No second toggle was sent. A later Escape failed after a cleanup menu had already closed. That was not another mutation.

The preflight page is in recoverable Trash at NFP-00153. The parent has no active records at NFP-00161 and remains available for the scored cases. A nonmodal Writing Replay prompt remains visible. It is accepted only when the title and required properties remain visible and no field editor is pending. No extension setting changed. This rule is set before scored work.

Original snapshots, service replies, images, and hashes remain in the raw preflight folders. The public extraction must retain these failures and remove unrelated account information.
