# Source search before selection

Date: 2026-10-22, America/Toronto. Search method: public web search, then direct primary-source reads. Search and reading preceded the frozen plan and execution. Search results were leads, not evidence. This limited search cannot establish novelty or priority.

## Repository scope

Read the cached repository protocol and current research index. Read the October 22 undo-visibility report and its source and design reviews. The new note uses the unused three-bit valid-state proposal in that source review. The visibility experiment did not execute that proposal. The new question concerns undo order and inability to finish after a locally valid write. It does not repeat that study's two-reader ordering check.

## Queries

1. `site.arxiv.org agent undo invariant planning compensation recovery safe ordering`
2. `site.cs.cmu.edu planning greedy search dead ends state space safety invariants`
3. `site.sigmodrecord.org sagas compensation consistency`
4. `"The FF Planning System" "dead ends" Hoffmann Nebel 2001`
5. `site.arxiv.org "UndoBench" "2610.05622"`
6. `site.arxiv.org "compensation" "safe" "planning" agent 2026`

## Primary sources checked

### Sagas

Hector Garcia-Molina and Kenneth Salem, 1987. ACM SIGMOD Record 16(3), 249–259. Publisher record: https://sigmodrecord.org/1987/12/09/sagas/ . Full text: https://sigmodrecord.org/?download_id=11106&smd_process_download=1 . Read Section 1, published pages 249–251. The paper requires each subtransaction to preserve consistency. Compensation removes an earlier action's effect in a semantic sense, not necessarily by assigning an old value. It permits other transactions to observe partial work. These points are prior work. This note does not refute correctly designed Sagas. Source copyright applies; no source file is copied.

### FF author's system page

Joerg Hoffmann, FF Homepage: https://fai.cs.uni-saarland.de/hoffmann/ff.html . No current page publication date is given. Accessed 2026-10-22. Read General Information, Basic Principles, and Relevant Papers. The author describes goal-order problems, dead ends, and fallback from local search to complete search. This establishes that the general local-versus-complete planning distinction is old. The page links the 2001 Hoffmann and Nebel JAIR paper; that full paper was not read for this note and is not cited as if it was. Our greedy controller is not FF, enforced hill climbing, or greedy best-first graph search. It makes real modeled writes and does not backtrack. No FF code is used or distributed.

### UndoBench

Dolly Sah, Tanmay Sah, Harshul Jain, Tanya Sah. UndoBench: Separating Task Competence from Recovery Capability in Tool-Using AI Agents. arXiv:2610.05622v1, 2026-10-04. Preprint. https://arxiv.org/html/2610.05622v1 . Read abstract and Sections 2.1–2.4. The benchmark separates final environment conditions from effect history and defines recovery at several execution boundaries. This note does not introduce that distinction. It supplies a small fixed-controller planning corpus, not a language-model benchmark. No numerical source result or program is reused.

### NeurIPS Paper Checklist

https://neurips.cc/public/guides/PaperChecklist . Accessed 2026-10-22. Read claims, limitations, theory, reproducibility, code/data access, experimental details, uncertainty, and compute guidance. Used as a review aid only. It does not certify this note or establish submission compliance.

## Search limits

Searches also returned broad planning notes, secondary summaries, and unrelated robotics work. Those were not used as technical evidence. No source access failure blocked the four cited primary sources. Source web pages can change. The cited read scope is narrower than full-paper verification where stated. No claim depends on an unread source result.

## Selected contribution

The proposed artifact is a complete classification of 64 state conditions and all six priorities in a three-bit monotone undo model, with smaller-state controls and a graph oracle. It will test whether a locally permitted write can remove every safe route to the goal. The underlying mechanism is established planning. Exact corpus counts and recorded witnesses will be the contribution if the checks pass.
