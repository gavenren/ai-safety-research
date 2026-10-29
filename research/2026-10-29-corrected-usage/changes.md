# Changes and deviations

Date: 2026-10-29.

The plan, independent formulas, main implementation, and schema adapter were frozen in that order. The independent agent read the main source only after both implementation freezes. It read results only after freezing its adapter. No frozen source or planned rule changed after execution.

Both main runs and both independent comparisons passed without repair. The seven scientific output files were byte-identical. There was no failed experiment to discard. Separate source-discovery failures are retained in source_search.md.

The design review requested clearer wording for the control whose machine label is `equal_revisions`: it has equal values at two distinct revisions. The report uses that wording. The review also requested an explicit note that C is chosen relative to true final charge for controlled boundary tests. These are text clarifications, not changed inputs.

The matched admission result and the difference between item and shared clipping are planned comparisons. They are not new experiments selected after the result. The report notes that duplicate multiset groups weight first-occurrence orders differently; their frequency differences are not isolated replay effects.

The second complete scientific output set and Python cache files are omitted from publication. All inputs, main output, environment records, exact byte comparisons, and independent check records remain. Publication success requires a separate remote commit and file check.
