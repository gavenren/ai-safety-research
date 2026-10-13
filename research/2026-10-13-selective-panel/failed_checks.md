# Failed checks and repairs

Date: 2026-10-13.

The first analysis run stopped at the model-key check. The code expected `Gemma-2-9B`, but the unchanged input uses `gemma-2-9b`. The exact input alias was added to the code. No row or label was changed. No routing result was produced by the failed run. The full analysis was then repeated.

This repair did not change the question, selection rule, data, or saved plan. Further failures, if any, are recorded below before publication.

The first figure placed its legend low because the text used data coordinates. Visual review found the layout issue. The legend now uses axes coordinates. The figure was regenerated and checked. No numerical result changed.
