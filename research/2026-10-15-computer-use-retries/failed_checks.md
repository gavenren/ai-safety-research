# Changes and failed checks

Before implementation or analysis, a design review found that a positive-count guard could claim completion after observing two items. The plan was amended to stop with a detected duplicate when the count is two. An observed count of one is the only completion claim. The original plan hash and amendment time are in input_manifest.json. No input case or hypothesis changed. No numerical analysis had run.

The PDF reviewer found that a figure legend overlapped a value label after the figure was changed to a vertical layout. The plot added top space, then the figure was regenerated. No data or result changed.

The first PDF text check gave a false failure for one paragraph that crossed a page break. Extracted text contained the running header between the paragraph's two parts. The check now removes only the known running header and footer before it compares the text. All 192 source text checks then passed. No report text changed. The final eight pages were rendered and inspected. A second build produced the same PDF hash.
