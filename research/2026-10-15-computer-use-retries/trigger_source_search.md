# Source search for the two-tab extension

Search date: 2026-10-15. The search was done before the scored plan.

Queries:
- site:arxiv.org browser agent retry partial observation multiple tabs reliability benchmark
- site:support.google.com/drive search filter folders refresh browser tab

Read sources:
- Google Drive, Search for files: https://support.google.com/drive/answer/2375114?hl=en . Read the filter guidance and file types. Documents and folders are separate types. This source does not establish cross-tab filter persistence.
- Google Drive, Organize your files: https://support.google.com/drive/answer/2375091?hl=en . Read New/Folder/Create and browser-window guidance. Used for workflow context only.
- Google Drive API files resource: https://developers.google.com/workspace/drive/api/reference/rest/v3/files . Read id, name, parents, shared, trashed, createdTime, version. Names need not be unique within a folder. The separate record audit uses distinct IDs.
- RFC 9110 section 9.2.2: https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2 . Read automatic-retry and idempotence conditions. The extension does not observe request internals or claim HTTP violations.
- WAREX v1: https://arxiv.org/html/2510.03285v1 . Read abstract and introduction for the distinction between infrastructure fault injection and normal interface filtering. This preprint was already cited. No code or data reused.
- CUJBench v1, 2026-04-25: https://arxiv.org/html/2604.23455v1 . Read abstract and introduction only. It studies browser/backend diagnosis with deterministic snapshots. Not cited for quantitative results; no full-paper review claimed.
- NeurIPS Paper Checklist: https://neurips.cc/public/guides/PaperChecklist . Read claims, limitations, assumptions, and reproducibility guidance. Used as a review aid only.

Proposed addition: a selected authenticated workflow with separate writer and observer tabs, common reload checks, actual retry branch records, and a later distinct-record audit. The prior same-tab Drive experiment did not activate retries. This changes the workflow, not the underlying retry principle. A limited search does not establish first novelty. The new study is not a benchmark reproduction or a natural agent error-rate estimate.
