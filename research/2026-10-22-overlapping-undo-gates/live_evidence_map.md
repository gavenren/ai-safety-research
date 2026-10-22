# Live gate evidence map

This table maps observed boundaries to existing private records. It does not create or replace raw evidence. Each referenced file has a SHA256 in `live_evidence.json`. An audit read and a guarded read have different roles.

| Case | Step | Authoritative read files | First verified DOM time | Seconds from initial reload | Earlier AX/DOM difference |
| --- | ---: | --- | --- | ---: | --- |
| G1-boolean | 1 | `gate-read-G1-boolean-1-recheck.json` (audit) | 2026-10-22T16:08:59.878Z | 13.519 | no |
| G1-boolean | 2 | `gate-read-G1-boolean-2-recheck.json` (audit) | 2026-10-22T16:09:40.793Z | 13.534 | no |
| G1-boolean | 3 | `gate-read-G1-boolean-3-guarded.json` (guarded_read), `gate-read-G1-boolean-3-recheck.json` (audit) | 2026-10-22T16:10:24.795Z | 13.063 | no |
| G1-boolean | 4 | `gate-read-G1-boolean-4-guarded.json` (guarded_read) | 2026-10-22T16:10:40.023Z | None | no |
| G1-boolean | 5 | `gate-read-G1-boolean-5-guarded.json` (guarded_read) | 2026-10-22T16:10:59.506Z | 11.422 | no |
| G1-nonnegative_count | 1 | `gate-read-G1-nonnegative_count-1-audit.json` (audit) | 2026-10-22T16:12:42.806Z | 23.6 | no |
| G1-nonnegative_count | 2 | `gate-read-G1-nonnegative_count-2-audit.json` (audit) | 2026-10-22T16:12:53.301Z | 0.922 | no |
| G1-nonnegative_count | 3 | `gate-read-G1-nonnegative_count-3-audit.json` (audit) | 2026-10-22T16:13:24.112Z | 22.905 | no |
| G1-nonnegative_count | 4 | `gate-read-G1-nonnegative_count-4-audit.json` (audit), `gate-read-G1-nonnegative_count-4-guarded.json` (guarded_read) | 2026-10-22T16:13:24.516Z | None | no |
| G1-nonnegative_count | 5 | `gate-read-G1-nonnegative_count-5-audit.json` (audit), `gate-read-G1-nonnegative_count-5-guarded.json` (guarded_read) | 2026-10-22T16:14:25.885Z | 52.773 | no |
| G1-active_ids | 1 | `gate-read-G1-active_ids-1-audit.json` (audit) | 2026-10-22T16:14:52.026Z | 4.666 | no |
| G1-active_ids | 2 | `gate-read-G1-active_ids-2-audit.json` (audit) | 2026-10-22T16:15:16.200Z | 16.9 | no |
| G1-active_ids | 3 | `gate-read-G1-active_ids-3-audit.json` (audit) | 2026-10-22T16:15:28.671Z | 5.066 | no |
| G1-active_ids | 4 | `gate-read-G1-active_ids-4-audit.json` (audit) | 2026-10-22T16:15:29.233Z | None | no |
| G1-active_ids | 5 | `gate-read-G1-active_ids-5-audit.json` (audit), `gate-read-G1-active_ids-5-guarded.json` (guarded_read) | 2026-10-22T16:15:41.321Z | 4.569 | yes |
| G1-lifecycle_registry | 1 | `gate-read-G1-lifecycle_registry-1-audit.json` (audit) | 2026-10-22T16:16:31.100Z | 4.851 | yes |
| G1-lifecycle_registry | 2 | `gate-read-G1-lifecycle_registry-2-audit.json` (audit) | 2026-10-22T16:16:45.878Z | 7.478 | no |
| G1-lifecycle_registry | 3 | `gate-read-G1-lifecycle_registry-3-audit.json` (audit) | 2026-10-22T16:17:13.139Z | 17.988 | no |
| G1-lifecycle_registry | 4 | `gate-read-G1-lifecycle_registry-4-audit.json` (audit) | 2026-10-22T16:17:13.518Z | None | no |
| G1-lifecycle_registry | 5 | `gate-read-G1-lifecycle_registry-5-audit.json` (audit), `gate-read-G1-lifecycle_registry-5-guarded.json` (guarded_read) | 2026-10-22T16:17:25.472Z | 4.601 | no |
| G2-boolean | 1 | `gate-read-G2-boolean-1-audit.json` (audit) | 2026-10-22T16:17:45.686Z | 5.227 | no |
| G2-boolean | 2 | `gate-read-G2-boolean-2-audit.json` (audit), `gate-read-G2-boolean-2-guarded.json` (guarded_read) | 2026-10-22T16:18:08.072Z | 14.587 | no |
| G2-boolean | 3 | `gate-read-G2-boolean-3-audit.json` (audit) | 2026-10-22T16:18:08.765Z | None | no |
| G2-boolean | 4 | `gate-read-G2-boolean-4-audit.json` (audit) | 2026-10-22T16:18:24.645Z | 7.676 | no |
| G2-boolean | 5 | `gate-read-G2-boolean-5-audit.json` (audit), `gate-read-G2-boolean-5-guarded.json` (guarded_read) | 2026-10-22T16:18:38.804Z | 6.568 | no |
| G2-nonnegative_count | 1 | `gate-read-G2-nonnegative_count-1-audit.json` (audit) | 2026-10-22T16:19:02.432Z | 7.789 | no |
| G2-nonnegative_count | 2 | `gate-read-G2-nonnegative_count-2-audit.json` (audit), `gate-read-G2-nonnegative_count-2-guarded.json` (guarded_read) | 2026-10-22T16:19:14.671Z | 4.637 | no |
| G2-nonnegative_count | 3 | `gate-read-G2-nonnegative_count-3-audit.json` (audit) | 2026-10-22T16:19:15.343Z | None | no |
| G2-nonnegative_count | 4 | `gate-read-G2-nonnegative_count-4-audit.json` (audit) | 2026-10-22T16:19:29.151Z | 6.417 | no |
| G2-nonnegative_count | 5 | `gate-read-G2-nonnegative_count-5-audit.json` (audit) | 2026-10-22T16:19:46.167Z | 8.676 | no |
| G2-active_ids | 1 | `gate-read-G2-active_ids-1-audit.json` (audit) | 2026-10-22T16:20:13.538Z | 8.311 | no |
| G2-active_ids | 2 | `gate-read-G2-active_ids-2-audit.json` (audit), `gate-read-G2-active_ids-2-guarded.json` (guarded_read) | 2026-10-22T16:20:28.390Z | 6.903 | no |
| G2-active_ids | 3 | `gate-read-G2-active_ids-3-audit.json` (audit) | 2026-10-22T16:20:29.050Z | None | no |
| G2-active_ids | 4 | `gate-read-G2-active_ids-4-audit.json` (audit) | 2026-10-22T16:20:41.545Z | 5.111 | no |
| G2-active_ids | 5 | `gate-read-G2-active_ids-5-audit.json` (audit) | 2026-10-22T16:20:56.314Z | 7.57 | no |
| G2-lifecycle_registry | 1 | `gate-read-G2-lifecycle_registry-1-audit.json` (audit) | 2026-10-22T16:21:26.720Z | 14.268 | no |
| G2-lifecycle_registry | 2 | `gate-read-G2-lifecycle_registry-2-audit.json` (audit), `gate-read-G2-lifecycle_registry-2-guarded.json` (guarded_read) | 2026-10-22T16:21:39.287Z | 6.851 | no |
| G2-lifecycle_registry | 3 | `gate-read-G2-lifecycle_registry-3-audit.json` (audit), `gate-read-G2-lifecycle_registry-3-guarded.json` (guarded_read) | 2026-10-22T16:21:40.186Z | None | no |
| G2-lifecycle_registry | 4 | `gate-read-G2-lifecycle_registry-4-audit.json` (audit) | 2026-10-22T16:21:54.902Z | 6.499 | no |
| G2-lifecycle_registry | 5 | `gate-read-G2-lifecycle_registry-5-audit.json` (audit), `gate-read-G2-lifecycle_registry-5-guarded.json` (guarded_read) | 2026-10-22T16:22:08.611Z | 6.233 | no |

The first G1 Boolean baseline has setup identity and a fresh DOM baseline. It has no fresh full connector start check. Each later connector boundary serves as the prior case end and the next case start. The final boundary ends case eight. Connector values for trashed and version were unavailable.

| Connector source | Ends case | Starts case | Result |
| --- | --- | --- | --- |
| `gate-connector-G1-boolean-end-G1-count-start.json` | G1-boolean | G1-nonnegative_count | verified |
| `gate-connector-boundary-2.json` | G1-nonnegative_count | G1-active_ids | verified |
| `gate-connector-boundary-3.json` | G1-active_ids | G1-lifecycle_registry | verified |
| `gate-connector-boundary-4.json` | G1-lifecycle_registry | G2-boolean | verified |
| `gate-connector-boundary-5.json` | G2-boolean | G2-nonnegative_count | verified |
| `gate-connector-boundary-6.json` | G2-nonnegative_count | G2-active_ids | verified |
| `gate-connector-boundary-7.json` | G2-active_ids | G2-lifecycle_registry | verified |
| `gate-connector-boundary-8.json` | G2-lifecycle_registry | None | verified |
