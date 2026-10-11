# Failed checks and repairs

1. A preliminary Python network metadata request failed because the local Python trust store could not verify the HTTPS certificate. No unverified connection was made. Public retrieval then used curl with certificate checks enabled.
2. An unquoted URL in a preliminary shell request was rejected by shell pattern expansion. Quoting the public URL fixed this request.
3. The first data fetch stopped on duplicate Aegis IDs. A full schema audit found two repeated, byte-equivalent structured records per model. The parser now collapses identical copies and rejects conflicting ones. Amendment 1 was saved before rate analysis.

4. A release-link check ran before review.md was saved. It reported that missing file. The file was then added; the final link check is recorded separately.
