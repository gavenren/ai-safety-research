# Supplement to original error records

This file copies text from the tool replies. Its file time is not the original error time. The action log supplies the source order and recorded time ranges.

- FCCAL-00004: `Cannot read properties of null (reading 'token')`.
- FCCAL-00016: `fcbase is not defined`.
- FCCAL-00315 follows FCCAL-00314 and retains this read failure:

```text
Error: Playwright selector deadline exceeded
locator.waitFor(visible) timed out for selector internal:role=textbox[name="Title"s]
Locator diagnostics: {"kind":"no_matches","action":"waitFor","locator":"internal:role=textbox[name=\"Title\"s]","matchCount":0,"matches":[],"visibleCount":0,"truncated":false}
```

FCCAL-00046 and FCCAL-00678 already retain the complete raw action error strings in actions.jsonl.
