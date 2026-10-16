# Source review: field checks across changing records

Date: October 16, 2026 (America/Toronto). Access date for all external sources: October 16, 2026.
Status: completed source review and design advice before calculation. No experiment was run for this review. No account record was changed. The final selected design is in analysis_plan.md; earlier suggestions remain here as context.

## Scope and search record

The search used the following terms:

1. `Afek Attiya Dolev Gafni Merritt Shavit atomic snapshots shared memory 1993 double collect sequence number pdf`
2. `fractured reads read atomic isolation RAMP transactions paper Bailis 2014`
3. `computer use agents benchmark final state verification task success artifact state StateAct 2026`
4. `site.developers.google.com calendar events updated changing reminders does not change updated property etag`
5. `site.rfc-editor.org RFC 9111 stale responses validation freshness`

I read the original source sections listed below. Search snippets were used to find sources, not as the final evidence. I did not read every paper in full. The first attempt to open the Afek journal PDF timed out. A second attempt succeeded. I did not inspect every cited paper or prove that this question is new.

## Primary sources and read limits

### S1. Atomic snapshots

Yehuda Afek, Hagit Attiya, Danny Dolev, Eli Gafni, Michael Merritt, and Nir Shavit. *Atomic Snapshots of Shared Memory*. Journal of the ACM 40(4), 873–890, September 1993. DOI: 10.1145/153724.153741.

Original journal PDF: https://groups.csail.mit.edu/tds/papers/Shavit/JACM93.pdf
Bibliographic check: https://projects.csail.mit.edu/jacm/References/afekadgms1993%3A873.html

Read scope: Section 3, Observation 1, Figure 3, Lemma 3.1, and the adjacent explanation on printed pages 878–882. I also read the start of Section 4 to check that bounded registers need further machinery. The full bounded and multi-writer proofs were not checked.

Supported facts: Two complete collects can establish a snapshot when each change leaves a unique mark. The simple construction stores a value and an increasing sequence number in one atomic write. Lemma 3.1 uses unchanged sequence numbers to rule out a write between the two reads of each register. Repeated value-only reads are not this construction. Repeated collects alone need not finish under continuing writes; the full algorithm adds other steps for its wait-free result.

Use: cite the established basis. Do not call a repeated-read test or a version guard a new snapshot algorithm. Cite the journal paper, not the May 1990 report, because the journal PDF is the version read here.

### S2. Fractured reads and visibility

Peter Bailis, Alan Fekete, Ali Ghodsi, Joseph M. Hellerstein, and Ion Stoica. *Scalable Atomic Visibility with RAMP Transactions*. SIGMOD 2014. DOI: 10.1145/2588555.2588562.

Author PDF: https://www.bailis.org/papers/ramp-sigmod2014.pdf

Read scope: abstract; Section 2 introduction; Sections 3.1–3.3; opening explanation in Section 4. The algorithm proofs, performance methods, and full appendix were not checked.

Supported facts: Read Atomic isolation prevents a reader from seeing only part of another transaction's writes. The paper calls this a fractured-read problem. This visibility property does not prevent concurrent writes. The paper separates it from serial access and from linearizability. It uses version metadata to find missing writes.

Use: this is related database work. A browser field observation is not itself a database transaction. For a simulated single record with atomic whole-record changes, use the plain term **mixed read** and define it. Do not claim that the simulation implements or measures RAMP.

### S3. Sequence counters

The Linux kernel documentation contributors. *Sequence counters and sequential locks*. Living implementation documentation. No publication date is stated in the read section.

Official source: https://docs.kernel.org/locking/seqlock.html

Read scope: Introduction; Sequence counters; Sequential locks; the first read-loop and write-loop examples. Latch details and the entire API list were not checked.

Supported facts: A reader copies data between two sequence reads. Acceptance needs the same even count at both ends. Writers make the count odd before a write and even after it. Writer serialization and ordering are necessary parts of this mechanism. A reader can retry when writes continue. These rules do not transfer automatically to a web service that exposes an update timestamp.

Use: supports an explicit write-in-progress condition if the model exposes partial writes. Under an atomic whole-record commit model, a simpler never-reused record revision can suffice. State which model is used. Do not present the simplified model as a Linux implementation.

### S4. Computer-use saved-state checks

Yan Yang, Xiangru Jian, Ziyang Luo, Zirui Zhao, Yutong Dai, Ziji Shi, Hanshu Yan, Jun Hao Liew, Silvio Savarese, and Junnan Li. *StateAct: Program State, before Pixels, for Long-Horizon Computer-Use Agents*. arXiv:2607.22798v1, July 24, 2026. **Preprint.**

Original HTML: https://arxiv.org/html/2607.22798v1
Metadata: https://arxiv.org/abs/2607.22798

Read scope: introduction; related-work paragraph on self-verification; Section 4.2; Section 6.1 discussion and Table 5. Other experiments and appendices were not read in full.

Supported facts: StateAct checks the persisted deliverable with a separate finish gate. The gate does not see the acting agent's narrative. It checks the requested artifact rather than an agent-created side file. The paper reports a limit: structural verification can miss wrong values and shared errors in interpretation.

Use: final saved-state checks are already established. The proposed study can examine the timing assumptions of a field checker. It should not claim to invent independent verification or establish a new computer-use benchmark score.

### S5. Calendar field coverage of update metadata

Google. *Events*. Calendar API v3 reference. Page last updated July 7, 2026 UTC.

Official source: https://developers.google.com/workspace/calendar/api/v3/reference/events

Read scope: resource representation; the descriptions for reminders, updated, sequence, and etag; the page update and rights notice.

Supported facts: The `updated` field covers the main event data. A reminder change does not change this value. `sequence` is the iCalendar sequence number and is writable. These descriptions do not make either field a never-reused revision for every field in the earlier study's contract.

Use: `updated` cannot support a claim that all checked fields were unchanged, because the earlier contract includes reminders. Do not infer that a user-visible date, a writable sequence field, or the tool's response time is a complete revision. The source does not establish the connector's cache or consistency behavior.

### S6. Calendar conditional requests

Google. *Get specific versions of resources*. Calendar API guide. Page last updated September 11, 2026 UTC.

Official source: https://developers.google.com/workspace/calendar/api/guides/version-resources

Read scope: introduction; Conditional modification; Conditional retrieval; the stated exception for `calendarList` entries. Java examples were inspected only to check which headers are used.

Supported facts: The guide describes `etag` for conditional changes and retrieval. `If-Match` can reject an intervening change with HTTP 412. `If-None-Match` can return HTTP 304 when a representation has not changed. Conditional insert is not supported in the same way. The guide also states an exception for some read-only `calendarList` fields.

Use: this motivates interface support for verified revisions. Do not generalize the calendarList exception to event fields. Do not claim that the current browser or connector exposes an authoritative monotonic revision without a separate check.

### S7. HTTP cache freshness

Roy T. Fielding, Mark Nottingham, and Julian Reschke. *HTTP Caching*. RFC 9111, June 2022. DOI: 10.17487/RFC9111.

Original standard: https://www.rfc-editor.org/rfc/rfc9111.html

Read scope: Sections 4, 4.2, 4.2.4, and 4.3 opening paragraphs.

Supported facts: An HTTP response can be reused while it is fresh under its cache rules. That term describes age relative to a lifetime; it is not a proof that the origin cannot have changed. Some stale responses can be served under specified permissions. Cache freshness does not force a user agent to refresh its display.

Use: distinguish a recent tool call from an authoritative current-state read. The proposed model must state its read semantics directly. This standard does not show that any tested provider violated its own rules.

### S8. HTTP validators

Roy T. Fielding, Mark Nottingham, and Julian Reschke. *HTTP Semantics*. RFC 9110, June 2022. DOI: 10.17487/RFC9110.

Original standard: https://www.rfc-editor.org/rfc/rfc9110.html

Read scope: Section 8.8.1 and the adjacent entity-tag discussion. The full standard was not read.

Supported facts: Strong validators distinguish representation data. They can use revision identifiers or a collision-resistant content hash. Weak validators need not change for each data change. Validator equality is scoped to the identified resource and representation.

Use: a content-derived token can repeat when the content returns. Therefore, token equality must not be silently interpreted as proof that no intervening change occurred. A record revision that never repeats is a stronger assumption than a generic entity tag. This last conclusion is a model-design inference, not a measured Calendar result.

## Search leads not used as research evidence

The search also found the Microsoft Research article *The Art of Building Verifiers for Computer Use Agents* (April 21, 2026), OSWorld 2.0, and other recent agent benchmark papers. I read selected paragraphs of the Microsoft article but did not read its linked paper. Do not cite its reported accuracy as checked evidence for this study. No result from these search leads is needed for the proposed question.

## Distinction from the October 15 work

I read Sections 12–13 and the related limits in the local published package `outputs/2026-10-15-computer-use-field-checks/report.md`.

That study tested exact saved-value comparisons, supported record identity, covered counts, and one same-record correction. It deliberately saved wrong fields in Calendar and Notion. It retained unknown fields and a finite post-decision audit. It did not deliberately schedule a second writer to change the record between field reads. It did not establish that all observations came from one revision. Do not change its scores from a new synthetic model.

A separate study can test this precise question: **When a checker reads the right record more than once, can correct individual field observations still support an incorrect combined claim?** This changes the object of study from value equality to temporal consistency. Temporal consistency means that the values are valid together at one time.

## Suggested bounded study, not a final plan

These are design suggestions. The parent agent must choose and freeze the final conditions before execution.

- Use a small synthetic record with two or three fields. Each field is either correct or incorrect against a fixed target. Give the record a fixed identity. Exclude duplicates so they cannot explain the result.
- Enumerate declared schedules of atomic whole-record writes and individual field reads. Preserve every schedule, each read, the ground-truth record states, and each classifier result. Do not label counts from this finite set as production failure rates.
- Compare a one-pass field check, two value-only passes, and a record-revision guard. Include an atomic full-record read as an interface control. State the extra evidence available to each rule.
- Use at least two definitions of a false claim. A **mixed-read false claim** accepts a target that never existed during the observation interval. A **claim-time false claim** accepts a target that is absent at the later claim event. Do not merge these metrics.
- Include stable-correct and stable-wrong controls, one change, returns to an earlier value, stale version reads, a version that omits a field, reused versions, and a write after the last check. Keep broken-assumption cases separate from the main theorem model.
- Report acceptance, rejection or UNKNOWN, and required reads. Do not call rejection a failure when the safe answer is uncertainty. Do not claim that a bounded retry rule is wait-free or guarantees progress under continuing writes.

A hand-constructed witness can alternate atomic states `(1,0)` and `(0,1)`. The first field can be read as `1` in the first state. The second can be read as `1` after a change. A value-only reader then assembles `(1,1)` although that target never existed. The writer can return to the earlier state before a new pass. A repeated assembled result does not establish that it was simultaneous. This is a logical illustration, not an executed measurement.

## Conditions needed for a revision argument

For a single record with atomic whole-record commits, a before-and-after revision guard can have a simple conditional proof. It needs all of these assumptions:

1. Each version and field read is linearizable: its result is the actual state at some point between the call and the response.
2. All reads address the same record and the same authoritative state, with explicit identity and field scope.
3. The operations are ordered: the first version read completes before field reads start; all field reads complete before the final version read starts.
4. Every relevant commit changes the revision. No value is reused or wrapped during the protected interval. The revision covers every checked field.
5. The revision changes atomically with the whole record. No intermediate field state is exposed under the old revision.
6. A claim is limited to the guarded observation interval. A later read or lock is needed for a stronger time claim.

If the two revisions agree under these conditions, there was no commit between them. The field values therefore belong to one constant record state in that interval. This is a direct application of established revision reasoning. It is not a general theorem for arbitrary browser views.

If writes are exposed field by field, a counter changed only at commit is insufficient. A reader can run during the unfinished write and observe the old counter at both ends. An odd/even write-in-progress protocol, serialized writers, and appropriate memory/read ordering would be a different model. Do not mix that model into the atomic-commit claim.

Equal values from two caches do not imply fresh state. A full record can also be stale: it is internally coherent but may fail the claim-time criterion. An opaque ETag need not reveal order. A coarse timestamp can miss changes. A counter can wrap, reset after restart, or belong to another object with a reused identity. These are distinct assumptions to test or exclude.

## Proposed contribution statement

A suitable statement is: “We provide a reproducible finite analysis of selected field-check schedules. The analysis separates individual value correctness, one-time joint correctness, and correctness at the completion claim. It gives explicit failure examples and tests a conditional revision guard.”

Do not claim first discovery, universal novelty, a new concurrency protocol, improved model ability, a live provider defect, or a production safety guarantee. The search is limited. The study can be useful even if its strongest result is a counterexample to a proposed completion rule.

## Rights and disclosure

This file contains original notes and paraphrases. It does not reproduce third-party papers or source code. Link to originals; retain their rights. Google page prose is marked CC BY 4.0 and its code samples have separate terms; no code sample is needed here. Do not assign a new license to the user's report. Codex performed this source review. No human or peer review is claimed.

## Addendum: selected finite model from the parent agent

The parent agent then selected a more specific model: two or three required binary fields; one, two, or three scans; zero, one, or two atomic single-field flips between reads; and one common final decision point. The controls include an exact revision, a revision modulo two or four, a revision that covers only the last field, and an atomic final snapshot. This note does not execute that plan.

This model can use a record revision without an odd/even write-in-progress state **if each atomic field flip and its revision increment occur together**. A field flip is then the complete write event in the model. No partially visible field write exists. This differs from a multi-field transaction whose revision changes only after all its writes. Do not generalize from the model to that transaction design. If a version increment is a later, separate event, the proof premise fails.

For a repeated two-field scan in the order `x,y`, a useful candidate witness starts at `(1,0)`. After reading `x=1`, it flips `x` to zero and then `y` to one. The intermediate state is `(0,0)`, so the target `(1,1)` is still absent. It reads `y=1`. It can reverse this process before reading `x` in the next scan. With `r` scans, the sequence has `2r` target-valued reads. There are `2r-1` adjacent read pairs. At each pair, the next field must change from zero to one, while the preceding field must first change from one to zero to exclude `(1,1)`. Thus at least two flips are needed for each pair. The lower bound is `2(2r-1)` flips. The construction meets the bound. This is a proposed hand derivation under the stated initial-state and read-order premises. The executable analysis and separate review must still check it.

The lower bound concerns only target-valued reads with no target state anywhere in the interval. It is not a lower bound for every false final-state claim. A final mutation can invalidate a previously correct target with fewer changes. A modulo counter can return to an earlier number; equality of such numbers is not the exact-revision assumption. The last-field-only counter can miss a change in another required field. These controls should be named for the deliberately broken assumption, not presented as provider measurements.
