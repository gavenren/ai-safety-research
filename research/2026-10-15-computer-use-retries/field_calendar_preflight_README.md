# Calendar field-check preflight

Date: 2026-10-15, America/Toronto. All action times use UTC.

This excluded preflight used one temporary event. The event had the title FC-PREFLIGHT-20261015-CALENDAR. It was an all-day event on October 14. It was Free and Private. It had no guests, location, conference link, notification, or repeat rule. The event is now in recoverable Trash. The native search and the read-only connector found zero active events after cleanup.

## Field read result

The saved native editor snapshot has a Description textbox but omits its text. A read-only DOM read of that visible textbox gives its innerText, textContent, and innerHTML. Each was exactly FC-PREFLIGHT-MARKER-A before replacement and exactly FC-PREFLIGHT-MARKER-B after replacement. FCP-0052 and FCP-0065 retain these values. The native event edit URL was the same before and after. The complete connector replies contain the marker followed by two LF characters. No old marker remained after replacement.

The root draft uses only trailing CR/LF removal for the scored comparison. It does not remove spaces, change case, remove an interior newline, or accept a substring. This is narrower than the initial excluded preflight plan. No scored trial was run from the preflight plan.

The native UI explicitly shows All day checked. Its start and inclusive end fields both show Oct 14, 2026. The connector start is 2026-10-14T00:00:00. Its end is 2026-10-15T00:00:00. These strings have no offset. The connector gives no all-day flag or time-zone field. The study must preserve these two evidence forms. It must not infer UTC instants or raw API date objects.

The connector exposes search_events, search, read_event, and batch_read_event. It does not expose search_events_all_fields. The metadata has a generic CallToolResult return type. summary.json lists the actual observed output types.

## UI procedure

1. Use the Search UI. Set the token in Keywords contained in event. Set the From date to October 1, 2026 and To date to October 31, 2026. Save the ready result and URL.
2. Use Create then Event. Set the title. Select All day. Set start and end to October 14, 2026. Set the plain Description marker. Remove notifications. Set Show as to Free and Visibility to Private. Leave the guest, location, conference, and repeat controls empty or off. Save once.
3. Reload the covering search. Open the exact event row and select Edit event. Save the native URL as identity evidence. Reload the editor. Save the complete snapshot.
4. Read the Description textbox with the read-only locator evaluation in browser_helpers.js. The read uses innerText, textContent, and innerHTML. It reads a visible control; it does not read hidden app state.
5. To replace Description, fill the full expected plain value on that same editor. Save once. Return to the same observed native URL and reload. Read all saved fields and the visible Description value again.
6. Use a separate bounded connector search and read_event. Keep the complete raw replies.
7. Close the unchanged editor. Return to the observed covering search. Open only the exact owned test row. Use Delete event. This sends the event to recoverable Trash. Reload and require a ready zero result. Repeat the bounded connector search and require events=[] and next_page_token=null.

## Evidence

Initial saved fields: FCP-0051. Initial Description DOM: FCP-0052. Replacement saved fields: FCP-0064. Replacement Description DOM: FCP-0065. Saved replacement covering result: FCP-0071. Replacement popup marker: FCP-0074. Cleanup action: FCP-0076. Cleanup ready zero: FCP-0079. Connector cleanup: cleanup-search.json.

One Create menu action failed before dispatch. FCP-0014 retains the error. A new read, FCP-0015, showed no menu or editor. Only the menu open was repeated. No Save was repeated after an error.

## Public extraction rule

Keep all raw logs, URLs, IDs, names, and images private. A public extract can include the test token, field values, time ranges, source record IDs, field verdicts, error type, action counts, and original file hashes. Replace account names, email addresses, native event IDs, event URLs, and unrelated calendar text. Inspect each original image before public use. Do not publish an image with unrelated account contents. Do not claim that a hash proves the truth of its source.

The next scored run must use the root frozen plan and assignments. This preflight gives no scored success count.
