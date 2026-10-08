# Research protocol

## Purpose

Produce small, useful AI safety studies with clear evidence and methods that others can repeat. Seek an original contribution. Do not promise a new finding each day.

Use ASD-STE100 Simplified Technical English. Define necessary research terms.

## 1. Select a question

Read previous reports and unfinished work. Search current primary research sources. Record the search date, terms, source links, and closest related studies.

State the research question and the exact proposed contribution. Explain the difference from earlier work. A limited search does not prove novelty. Do not present a summary or a renamed method as new research.

Select a study that fits the available resources. Suitable work can include an experiment, a simulation, or a formal analysis. State the limits of each method.

## 2. Record the plan

Save the hypothesis, method, baseline, measures, and decision criteria before analysis. Record later changes. Identify exploratory analyses.

Use only data and tools with suitable access rights. Do not start paid services without a separate spending limit from the repository owner.

## 3. Do the work

Save code or full derivations, inputs or retrieval steps, dependency versions, model versions, settings, random seeds, logs, and raw results.

Use suitable controls and comparison baselines. Check for data leakage and sampling errors where relevant. Report uncertainty with its method and assumptions.

Preserve negative results and failed tests. Do not invent data, references, experiments, measurements, or results. Do not treat a simulation as evidence of real model behaviour.

## 4. Write the report

Include these parts:

- Title, date, and abstract.
- Research question and safety relevance.
- Related work and the proposed contribution.
- Method and results.
- Discussion and limitations.
- Ethical issues and possible misuse.
- References and instructions to repeat the work.
- AI use and human review status.

Separate evidence, assumptions, interpretations, hypotheses, and unfinished work. Check each reference against its original source. Identify preprints.

State that Codex generated the study and report when this is true. Describe each AI tool and its role. State when no human review occurred. Do not claim peer review, endorsement, certification, or university affiliation without evidence.

Respect source licenses and attribution. Do not apply a new license to the owner's work without an owner decision.

## 5. Check before publication

Use the relevant parts of the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist) as a review aid. This does not establish conference approval or submission compliance.

Run the documented procedure. Check that its outputs support the report. For formal work, check each proof and its assumptions. Request a separate agent review when available. Resolve material errors.

Check source links, novelty claims, copied text, private information, secrets, and license conflicts. Do not publish actionable details that enable serious harm.

Publish only after the required checks pass. A valid negative result can be published. If a check fails, keep the draft and evidence locally. Record the problem and continue the study later.

## 6. Publish and verify

Use a folder such as `research/YYYY-MM-DD-topic/`. Include `report.md`, `references.bib`, a README with reproduction steps, and the applicable code, data, and results.

Update the report index in the repository README. Use a clear commit message. Preserve previous work. Do not force-push or bypass branch protections.

After publication, fetch the remote commit. Confirm that the report and its supporting files are present. Record the run date, question, checks, publication status, and verified link.

## Status labels

- **Draft:** Work is incomplete or a required check failed.
- **Published research note:** Required checks passed and the remote files were verified.
- **Human reviewed:** A named human completed the stated review.
- **Peer reviewed:** An external review process is documented.

Agent review alone is not human review or external peer review.

