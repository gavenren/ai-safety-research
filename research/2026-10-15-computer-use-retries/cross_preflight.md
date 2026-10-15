# Excluded feasibility cases

Date: 2026-10-15. These cases selected the workflow before scored trials. None enters the scored counts.

DemoQA kept CROSS-NOMATCH active after Submit. Its later ready table at 30.611 seconds had no matching row. A second identical form submission was accepted. Clearing search showed two exact CROSS-PREFLIGHT rows. Reload restored the three default rows and empty search.

DataTables P01 kept the added row hidden, but its later read was at 19.606 seconds. It failed the 24-second timing gate. Clearing search showed two total rows, one beyond baseline, and reload restored the single baseline row. P02 repeated the setup. Its later hidden read was at 36.318 seconds. A second Add produced a footer total of three while no row matched search. Clearing search showed three distinct row vectors, two beyond baseline. Reload restored the one-row baseline and empty search.

Both sites had no established exact-request success receipt. The three list-based rules are tested; Receipt is unavailable. DataTables shows total-entry counts even when rows are filtered. The supplied rules ignore this additional visible evidence.

These observations support a page-local test. No service-side audit or persistence guarantee is available. A reload resets the examples and must occur only after the primary audit. The preflight durations include other work and do not measure service latency. Raw action times and observations remain in the preflight JSONL files.
