# Execution notes

The frozen plan, case file, copied corrected adapter, and evaluator did not change. All 12 planned records and all 36 evaluations completed. No account create or delete was retried. No browser Save action was used.

Before account writes, an old browser connection was unavailable. A fresh inventory showed the same signed-in Chrome profile on its current connection. The task used that connection. No credentials or account permissions changed.

The first local safe-data export failed with `KeyError: 'status'`. The create action returns an ID and URL but does not return a status field. The export now preserves that absence as null and reports confirmed status from the later exact read. Two analysis attempts then failed because the export had not created `cleanup.json`. After the exporter was fixed, two complete analyses passed and matched. These were local packaging failures after account cleanup. They did not cause another account write or a change to any trial result.

The evidence producer set `verified:true` after the exact record and both displayed zone controls were checked. This flag means the capture was checked. It does not mean the zone matched Toronto. Both New York captures also have this flag. The adapter then compared their labels and refused them.

The two positive controls were accepted in both evidence phases. Eight other correct records changed from refusal to acceptance when complete evidence was supplied. Thus, 12 accepted outputs refer to ten records. The two wrong-zone records remained wrong until deletion. They were not repaired for the test.
