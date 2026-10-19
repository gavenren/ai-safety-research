# Failed checks and corrections

1. The first unit-test run had one failure. All 13 malformed inputs were rejected, but the test expected a list size of 14. The list contains six explicit cases and seven missing-key cases. The expected count was corrected to 13. The model, frozen files and generated results did not change. The analysis command had run after that failed test; no result was approved for publication at that point. The corrected tests and a clean reproduction must pass before publication.
2. A read of a browser skill at an assumed local path failed because that file was absent. No browser action or publication occurred from that read. The available runtime documentation will be used for publication.

3. Browser setup returned the documented browser agent as a value. An initial call did not bind that value, so the next read said that agent was not defined. The returned value was bound and the browser list then worked. No publication action occurred before this correction.
4. The first report draft stated 464 observation groups. The six per-length counts sum to 364. The independent implementation also found 364. The report text was corrected; generated data and frozen inputs did not change.

5. The independent model includes six explicit zero-count aggregate rows and 60 additional subgroup comparison rows. The main display omits those rows. The comparison adapter checks the common scope and records the row-schema differences. No model logic was changed to obtain agreement.

There are no omitted failed study cases. Hypotheses are evaluated on the full frozen corpus. This file will record any later material correction.
