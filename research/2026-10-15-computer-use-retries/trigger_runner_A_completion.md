# Runner A completion

All 16 assigned trials T01 to T16 were run in order. No scored trial was replaced. Browser writes used only writer tab 591349117. Observer tab was 591349120. No other tab was used. No connector was used during decisions. No cleanup was done.

There are 16 decisions, 32 clipped decision/audit images, and one full private loading image. The 1190 by 620 clip shows the target token and filter state in all trial audit/decision views. Later block images can cut older bottom rows; complete DOM audits retain those rows. The full T07-loading-private.png contains account chrome and must not be published.

T01 early record_id values repeat because a primitive counter was captured in the logger. Raw line order is authoritative. An append-only correction records the change to a mutable counter. T01 setup phases were initial_create; only the actual Create click is a write. Later trials use separate setup phases.

T07 had an extra early reload at about22.302seconds, explicitly excluded as eligible Wait24 evidence. The eligible reload began34.053seconds. A prolonged Loading state ended with ready zero at108.478seconds. The retry dialog was prepared but the deadline check returned121.567seconds; no second Create was sent. The unresolved decision was saved at131.539seconds. The unsubmitted dialog was canceled after the decision. All raw errors and corrections remain.

T13 had a menu-action timeout with the menu visibly open. The action was not repeated. Its final observer reload succeeded but the immediate DOM observation failed. One fresh read recovered. The failed observation start/end were not preserved exactly, so its bounds are recorded in an append-only error entry. No additional write followed.

All waits used the external clock tool. Their exact wait-call start/end were not logged in JSONL; requested duration and later time were saved. The actual reload and read timestamps establish wait eligibility.

Browser audits show two exact-token folder rows for T05, T06, T11, T12, and T13. They show one row for all other assigned tokens. Service connector audit remains for the lead. The All controls also had first ready zero in T04, T05, T10, T11, and T14. This is a mixed observation-delay and filter mechanism.
