# Live order evidence map

Native IDs and private URLs are omitted. SHA256 references in `live_evidence.json` identify the original private files. Each row is an actual saved DOM observation, not a predicted state.

| Case | Step | State | DOM read time | Raw read file |
| --- | ---: | --- | --- | --- |
| ORDER-W-F | 0 | 111 | 2026-10-22T16:25:03.877Z | `order-read-ORDER-W-F-0.json` |
| ORDER-W-F | 1 | 101 | 2026-10-22T16:25:21.730Z | `order-read-ORDER-W-F-1.json` |
| ORDER-W-F | 2 | 001 | 2026-10-22T16:25:37.884Z | `order-read-ORDER-W-F-2.json` |
| ORDER-W-F | 3 | 000 | 2026-10-22T16:25:54.795Z | `order-read-ORDER-W-F-3.json` |
| ORDER-W-G | 0 | 111 | 2026-10-22T16:25:57.148Z | `order-read-ORDER-W-G-0.json` |
| ORDER-W-G | 1 | 101 | 2026-10-22T16:26:32.224Z | `order-read-ORDER-W-G-1.json` |
| ORDER-W-C | 0 | 111 | 2026-10-22T16:26:34.585Z | `order-read-ORDER-W-C-0.json` |
| ORDER-W-C | 1 | 011 | 2026-10-22T16:27:03.508Z | `order-read-ORDER-W-C-1.json` |
| ORDER-W-C | 2 | 010 | 2026-10-22T16:27:15.158Z | `order-read-ORDER-W-C-2.json` |
| ORDER-W-C | 3 | 000 | 2026-10-22T16:27:23.463Z | `order-read-ORDER-W-C-3.json` |
| ORDER-V-F | 0 | 111 | 2026-10-22T16:27:25.991Z | `order-read-ORDER-V-F-0.json` |
| ORDER-V-F | 1 | 101 | 2026-10-22T16:27:58.884Z | `order-read-ORDER-V-F-1.json` |
| ORDER-V-F | 2 | 001 | 2026-10-22T16:28:01.704Z | `order-read-ORDER-V-F-2.json` |
| ORDER-V-F | 3 | 000 | 2026-10-22T16:28:12.185Z | `order-read-ORDER-V-F-3.json` |
| ORDER-V-G | 0 | 111 | 2026-10-22T16:28:14.068Z | `order-read-ORDER-V-G-0.json` |
| ORDER-V-G | 1 | 101 | 2026-10-22T16:28:16.860Z | `order-read-ORDER-V-G-1.json` |
| ORDER-V-G | 2 | 001 | 2026-10-22T16:28:25.406Z | `order-read-ORDER-V-G-2.json` |
| ORDER-V-G | 3 | 000 | 2026-10-22T16:28:28.290Z | `order-read-ORDER-V-G-3.json` |
| ORDER-V-C | 0 | 111 | 2026-10-22T16:28:30.556Z | `order-read-ORDER-V-C-0.json` |
| ORDER-V-C | 1 | 101 | 2026-10-22T16:28:41.406Z | `order-read-ORDER-V-C-1.json` |
| ORDER-V-C | 2 | 001 | 2026-10-22T16:28:44.254Z | `order-read-ORDER-V-C-2.json` |
| ORDER-V-C | 3 | 000 | 2026-10-22T16:28:47.047Z | `order-read-ORDER-V-C-3.json` |

| Case | Full baseline time | Final connector time | Final connector before later DOM read |
| --- | --- | --- | --- |
| ORDER-W-F | 2026-10-22T16:22:59.301Z | 2026-10-22T16:26:19.139Z | False |
| ORDER-W-G | 2026-10-22T16:22:59.301Z | 2026-10-22T16:26:19.651Z | True |
| ORDER-W-C | 2026-10-22T16:22:59.301Z | 2026-10-22T16:27:46.418Z | False |
| ORDER-V-F | 2026-10-22T16:22:59.301Z | 2026-10-22T16:28:57.079Z | False |
| ORDER-V-G | 2026-10-22T16:22:59.301Z | 2026-10-22T16:28:57.522Z | False |
| ORDER-V-C | 2026-10-22T16:22:59.301Z | 2026-10-22T16:28:57.940Z | False |

The full baseline was a single batch. All final connector reads followed the final write. W-G had its one successful post-write DOM read after the connector read; no additional write occurred. Only the initial W-F pre-baseline placeholder is known to have been overwritten. The later baseline and all scored post-Save reads remain saved.
