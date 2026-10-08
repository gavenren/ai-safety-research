# Research checks

Review date: October 8, 2026.

## Independent agent checks

A source agent checked the archive source, license, historical reference dates, prior work, and classification limits.

A severity agent inspected both original CSET files. It confirmed the published-only filter, 76 known legacy scores, the 2020 endpoint, and the absence of 2024–2026 classifications. It found that death and injury fields do not support a simple total of confirmed AI harm. Those fields are not used in the results.

A methods agent independently recomputed the main values from the original CSVs. It confirmed the annual totals, 47.557% growth from 2024 to 2025, the 4.978 multiple from 2020 to 2025, and the matched-window comparison. It also confirmed snapshot additions, date edits, and all missing-data bounds. It compared the selected public data extracts with the original fields and found exact agreement.

The methods agent reviewed report.md. It required a clear statement that CSETv0 includes harm that nearly occurred. That statement and its source were added. It also requested simpler wording about years when counts fell. That change was made.

## Execution and data checks

- Both original archives match the SHA-256 hashes in source_manifest.json.
- All four extracted source CSVs match their recorded hashes.
- All 1,713 current and 1,313 earlier IDs are distinct.
- All incident dates parse and precede their own snapshot cutoff.
- Every published CSET annotation used in the study joins to a current incident ID.
- Annual totals sum to the current record count.
- The legacy severity distribution sums to 92 published rows.
- The snapshot-change identity holds for every year.
- The standard reproduction command regenerated all tables and figures.
- All three final figures were visually inspected. Labels, axes, notes, and data marks were checked. An initial overlap in the snapshot figure was corrected.

## Publication checks

The report gives database dates, selection limits, incomplete-year limits, severity coverage, AI use, and the actual review status. No claim of a first discovery or a new statistical method is made. Source attribution and CC BY-SA terms are retained for the data adaptations.

The public extracts contain factual IDs, dates, publication flags, and selected classification values. They do not contain article text, descriptions, private contact data, or authentication data. The publication set contains only the report and its support files. Local caches and the full source archives are excluded.

## Limits of this review

These checks do not validate every source article or establish the true global incidence of AI harm. The source labels were not re-annotated. No human reviewed this report during this run. Agent review is not external peer review. The NeurIPS checklist was used as a general aid, not a claim of conference compliance or approval.
