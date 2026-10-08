# Analysis plan

Recorded on October 8, 2026, before data analysis.

## Question

How have the count and severity of recorded AI incidents changed over time?

## Scope

Use the official AI Incident Database snapshot dated October 5, 2026. Start with the earliest valid incident date. This is not the inception of AI as a field. Count distinct incidents, not media reports. Use the latest complete calendar year, 2025, for full-year comparisons. Show 2026 separately as a partial year. Where possible, compare equal date ranges for 2025 and 2026.

## Method

Inspect the schema before selecting severity fields. Report missing dates, duplicate identifiers, classifications coverage, and any exclusions. Group incidents by recorded occurrence year. Show all years. Compare recent five-year periods only when the fields have comparable meanings. Do not use significance tests to imply a random population sample.

For severity, use existing documented harm or severity fields. Do not infer severity from article counts, model type, or year. If no valid common score exists, report harm indicators and missingness instead. Do not label harm types as an ordinal severity scale. Where a binary severity-related indicator is available, show observed classified shares and bounds that include unknown records.

## Criteria

Support a count trend only for recorded incidents in the database. A trend in actual global incidence or risk per AI use requires a reporting model and an exposure denominator. These may be unavailable.

Support a severity trend only if definitions and coverage permit comparable measurements. Otherwise, report that the direction cannot be established. Treat this as a valid study result.

## Output and checks

Save the input URL and file hash, code, derived data, figures, references, and reproduction steps. Inspect dates and classification joins. Recompute main values with a separate method or reviewer. Publish only after the repository research checks pass. Record changes to this plan below.

## Changes after schema inspection

Schema inspection found an ordinal Severity field in CSETv0. Only published annotations will be used. CSETv1 AI Harm Level describes harm occurrence and is not an equivalent severity scale. The two fields will not be merged.

Add a sensitivity check against the January 5, 2026 snapshot. This decision followed a difference between current counts and the Stanford AI Index summary. Compare the same incident-year counts across snapshots. Decompose net changes into added IDs, removed IDs, and date changes. This check is exploratory and was specified before the January snapshot was analysed.
