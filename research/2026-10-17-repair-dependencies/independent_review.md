# Independent review

Date: October 17, 2026. Result: PASS for the stated finite-model audit.

This review was performed by a separate Codex agent. No human review or peer review occurred. The reviewer independently implemented the frozen plan before reading main results. The reviewer did not read, import, or call `analyze.py`. Main output data and their schemas were inspected only after the independent enumeration was complete.

## Checks performed

- Frozen plan and configuration hashes match `input_manifest.json`.
- All 59,184 main policy-scenario rows match the independent computation. The comparison checks all scalar fields, decisions, final states, revisions, complete input programs, and all 379,596 consumed events.
- All 54 aggregate rows and 756 scalar aggregate values match. All nine paired comparison rows match.
- All 88 minimum-write witnesses match. This includes the complete trace and the tie rule: consumed writes, rounds, initial tuple, and full integer word program.
- Ten handcrafted controls pass. They cover stale source, stale permission, denial before a gap, replacement collateral, unrelated interference, source return, omitted permission, revision changes on return, unused suffixes, and the H5 first-word condition.
- The independent validator rejects 27 malformed configurations. Two state symmetries pass across 118,368 transformed rows: complement X and Y together, or complement U.
- A separate fresh-directory run of the independent command exits zero. All five generated independent data files are byte-identical. See `independent_reproduction.json`.
- The main test log records nine successful test methods. The root reproduction receipt records successful execution of all three README commands in a separate empty directory and byte equality of ten generated data files. This reviewer read those records; the independent calculation does not depend on the main implementation.

## Report and proof review

The abstract, result table, error-set intersections, paired subset counts, corpus sizes, and worked examples match the independent data. The current-value permission contract is explicit. The semantic oracle uses the pre-effect state. Whole-record collateral is counted separately from semantic validity. The report states that success means a write occurred and does not mean the write was valid.

The two safety arguments follow from the assumptions. Replan CAS permits a successful attempt only after a gap with no writes. The complete dependency guard directly requires the needed A and X values at the effect. The formulas for Refresh CAS and the H5 subsets are correct. The proof does not require a natural probability distribution. No source or permission-history guarantee is implied.

The report preserves unused-suffix multiplicity and each policy's own stopping point. It makes no causal latency claim or real-world error-rate claim. It states that the tested rules are prescribed abstract policies, and that there was no live website or model test. It identifies prior concurrency principles and limits its contribution to the case corpus and exact checks. Primary-source reading and metadata checks are recorded by the separate source reviewer; they are outside this numerical review.

One wording issue was found: the draft called the symmetry controls “field relabelings.” The report now says “bit complements,” which matches the executed checks. No numerical or model-scope correction was needed. No material issue remains in this review scope.

The README commands match the available command interfaces and checked reproduction. The independent comparison reads main files as data and does not import main code. To repeat the independent check, use:

```sh
python3 independent_audit.py --input-dir . --output-dir . --compare-main .
```

## Limits

Both implementations derive from the same small plan. Agreement does not exclude a shared conceptual omission. The finite audit cannot establish production behavior, provider support for atomic guards, or a general rate of failure. This review is an automated check and is not institutional approval, certification, or peer review.

## Reviewed file hashes

These SHA-256 values identify the reviewed versions. A later change requires a new relevant check.

| File | SHA-256 |
| --- | --- |
| `report.md` | `cc5669e94616a510fbc4743bd5406da4f9d5b7d4695f3cac7c5838894757dad1` |
| `README.md` | `612d85626728aa0a572e237501eb1a99f17d3d01f6860a1ed6d02dedf96908e4` |
| `derivations.md` | `96ad16a5a6f06fac4c27c9947be4936daff30f5e43e06f65206b49252721a1e1` |
| `analysis_plan.md` | `7e8a7cf42623c7c04deea810eb8005991223af5e4bcabe97005c65bc00d23544` |
| `config.json` | `62796531c052e3d16826d8c8a05ccb31c4bfa98812c3c7b4e2e05b9cd1f356ae` |
| `input_manifest.json` | `07e5afff3bb047a88ec04bd0e1286ae0b628898bf811f972612debb41c4a2b24` |
| `independent_audit.py` | `64e02919a8e43b77682241b29d6d8ad3131972b2b972993740d843b7278e0c08` |
| `independent_comparison.json` | `5c6ab38c6991c39a79fe7e73b9cdae5ef0494d85f8eaecaabbe533ac8a128181` |
| `independent_reproduction.json` | `b37d2987a030e3629af698cdc490a591487598ec46102ec5f937a8c5346e5df0` |
