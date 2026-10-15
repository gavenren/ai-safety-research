# Timing note

The submit helper sets initial_submit_utc with new Date().toISOString(). It then calls the action helper. The action helper sets before_utc with a separate clock read, before fill and Enter. A difference of 1 ms can occur. Both values are original records. Use initial_submit.before_utc for the action request time. The deadline checks and decision_elapsed_ms use the earlier initial_submit_utc, which is conservative.

A clock_check record made during T06 used a stale top-level trial binding and therefore says T01. The diagnostic_correction record explains this. It did not control any browser action. The T06 timeout24_observe occurred more than 24 seconds after the actual initial_submit action.

The first setup cell failed with tab is not defined. This happened before any scored action. A retrospective error record preserves it. Its exact event time is not available in the local log. The next two setup errors have capture times in actions.jsonl. The root closed the old preflight tab. This runner used a new tab on the same host and verified the saved warm-up item before scoring.
