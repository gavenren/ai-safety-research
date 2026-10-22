# Reproduce the production-page policy scores

This extension contains two real provider page chains and local policy replay. It does not contain an autonomous browser-agent benchmark.

The account setup and page reads were performed once on 2026-10-22. Four temporary fixtures were created through connectors for each provider. No external attendee was added. Full requests and responses remain private because they contain account IDs and page tokens. The public trace uses stable fixture aliases and SHA-256 token links. The parent run owns cleanup and publication.

Use Python 3.13.7 or a compatible Python 3 release on a Unix system. The code uses only the standard library and sets a 30 CPU second process limit. It does not use the network, models, account credentials, or random numbers.

```sh
python3 live_analysis.py --trace live_trace.json --output reproduced_results.json --execution reproduced_execution.json
cmp live_results.json reproduced_results.json
```

The result JSON must match byte for byte. Execution times and timestamps will differ. The saved repeat used the same pages and is not another service trial.

Files:

- `live_trace.json`: eight pages and two empty controls, with aliases and token-hash links.
- `query_freeze.json`: pre-collection timestamp and private-query/configuration hash.
- `analysis_freeze.json`: implementation and trace hashes before scoring. Code was written after page collection; rules were fixed earlier.
- `live_analysis.py`: fixed local policy scoring.
- `live_results.json`: all 48 local rule outcomes and six inventory-control outcomes.
- `live_execution.json`, `live_execution_repeat.json`, and `live_reproduction.json`: versions, time, and exact-match checks.
- `analysis.log` and `analysis_repeat.log`: saved scoring outputs.
- `build_trace.py` and `trace_build.log`: private-to-public trace checks. The script needs private evidence that is not distributed. It cannot independently fetch the original records.
- `report_extension.md`: the production extension included in the existing paper. The separate review passed. Cleanup evidence is in `live_cleanup.md`.

The private trace builder checked that each later request used the previous response token unchanged, that fixed query fields did not change, and that every returned ID belonged to the frozen manifest. The public scoring code checks linked token hashes, final-token state, exact alias inventory, duplicate returns, and rule counts.

To repeat the account test, create new fixtures and freeze new IDs and query arguments before collection. Use real provider pagination. Do not substitute slices of a single response. Keep fixtures fixed until the chain is finished. Page order can change. Report any failed call or missing fixture. Never alter a trace to make it match the published order.

The eight target filters are paired cases on two traces. Nonfinal empty pages, nonfinal short pages, and native incomplete-search flags were not observed. Wider coverage remains unknown.
