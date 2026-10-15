# Review checklist for the browser extension

The NeurIPS Paper Checklist was used as a review aid. This is not a claim of conference approval, submission compliance, or certification. The original synthetic review is preserved in simulation_review.md.

| Review item | Evidence and limit |
| --- | --- |
| Claims and contribution | The report separates a finite event model from an 18-trial real-agent browser pilot. It does not claim a new retry principle, first priority, a general speed gain, or field failure rates. |
| Method and assumptions | Saved browser plan, configuration, application hash, assigned policies, order, limits, and actual timer data are retained. Structured truthful status is a constructed application capability. |
| Reproduction | Original numerical outputs keep their prior hashes. The browser analyzer reads frozen SQLite and JSON evidence. A new model trajectory need not repeat byte for byte. |
| Uncertainty and selection | All 18 assigned trials remain. Two unresolved stops, one late claim, four duplicates, and zero post-stop effects are reported. Two repetitions per cell do not justify population confidence intervals. All six timing pairs are shown. |
| Data access and leakage | Runner prompts withhold condition values and forbid hidden-state access. Logs contain task actions and visible states, not tool code or model-turn boundaries. Instruction-based separation is not secure isolation. |
| Resources and versions | The server, browser-reported version, Python versions, and available agent identity are recorded. Exact model snapshot and service latency parts are unavailable. Existing Codex inference was used; no separate paid API or new paid compute service was started. |
| Ethics and rights | Only a local constructed task creates records. No external transaction is an experiment outcome. No private task record or copied source asset is included. No new license is assigned. |
| Provenance and review | Codex generated the work and performed the browser trials. Agent review is stated. No human or external peer review is claimed. |
| Presentation and checks | Current PDF layout and text checks are in pdf_check.json. Independent evidence checks are in browser_review.md and browser_reproduction_check.json. Release checks and remote verification are separate. |
