# Source search for the authenticated-account extension

Date: 2026-10-15. This is a manual extension to the existing paper. The prior source records remain unchanged.

## Exact new searches

1. `site.support.google.com/drive filter file type folders duplicate names create folder`
2. `browser agent benchmark live websites webvoyager webarena authenticated tasks retry observation`

The first query used a malformed domain phrase, but returned official Google help and API pages. We read the original official pages below. We did not use forum claims as evidence. The second query returned benchmark papers and vendor score reports. The report uses the original WebVoyager and versioned WAREX sources already cited; vendor leaderboard claims were not used.

## Primary reads

- Google, Organize your files in Google Drive: https://support.google.com/drive/answer/2375091?hl=en . Read creation, duplicate-name organization, and removal sections. Undated help page, accessed 2026-10-15. It documents New / Folder / Create. It cautions that organizational changes can take time to appear. It does not document the precise automatic filter behavior measured here.
- Google, Search for files in Google Drive: https://support.google.com/drive/answer/2375114 . Read search/filter and advanced search sections. Undated help page, accessed 2026-10-15. Type filters narrow results, and Remove/Clear filters remove them. Folder and Document are separate types.
- Google, REST Resource: files: https://developers.google.com/workspace/drive/api/reference/rest/v3/files . Read File fields for id, name, parents, MIME type, shared, trashed, createdTime, and version. Page update shown: 2026-07-14. Name need not be unique within a folder. Distinct returned IDs are therefore used for duplicate scoring. The study does not implement or claim a server transaction protocol.
- Google, Delete files in Google Drive: https://support.google.com/drive/answer/2375102 . Read Trash and permanent-deletion distinction. Undated help page, accessed 2026-10-15. Moving to Trash permits recovery before permanent deletion. The planned cleanup does not empty Trash.
- He et al., WebVoyager, ACL 2024: https://aclanthology.org/2024.acl-long.371/ . Reopened the original paper page; the paper abstract and relevant method were read during the prior extension. This provides live-browser evaluation context. The new study is not a WebVoyager benchmark run.
- Kara et al., WAREX, arXiv:2510.03285v1, 28 September 2025: https://arxiv.org/html/2510.03285v1 . Reopened and read the introduction/framework sections. The cited version remains labeled a preprint. A search also returned a later TMLR version, but it was not read or used. WAREX introduces infrastructure faults; this study introduces no fault and tests ordinary type-filter behavior.
- NeurIPS Paper Checklist: https://neurips.cc/public/guides/PaperChecklist . Reopened relevant claims, limitations, reproduction, ethics, resources, and rights guidance. Used only as a review aid.

An attempted direct help URL resolved to Buy more Google storage. It was not relevant, is not cited, and did not cause a purchase. The correct filter and Trash pages were reached through the official organization page.

## Contribution and limits

The extension checks whether the public-demo result transfers to one authenticated, service-backed folder workflow. It adds independent connector enumeration of synthetic records and records automatic view changes and creation notifications. It does not propose a new retry protocol. It does not measure natural model behavior or a representative production error rate. The final plan was saved after a small feasibility check. A limited search cannot establish novelty or first priority.

No source paper or application code is redistributed. The report uses original prose and brief attribution. Google screenshots and rendered UI evidence show newly created synthetic test names. Public evidence removes private account identifiers and navigation details under a documented procedure.
