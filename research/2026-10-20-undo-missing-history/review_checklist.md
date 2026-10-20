# Publication review

Date: 2026-10-20. Review aid: [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), accessed today. Relevant claims, limits, theory, reproducibility, settings, uncertainty, compute, ethics, rights, and AI-use items were read. This is not a conference submission or a claim of approval.

| Item | Result and evidence |
| --- | --- |
| Claim support | Counts come from the saved enumeration. All report tables were checked against results. No model or website error rate is claimed. |
| Prior work | The closest method is explicitly credited to lossy-event monitoring. Compensation and possible-world agreement are established. Source search and read scopes are saved. Inaccessible leads support no claims. |
| Prospective plan | Plan, configuration, and source record hashes were saved before model execution. Hashes still match. Later corrections are in changes_and_failures.md. |
| Theory | True-history inclusion and target-set inclusion prove the stated model conditions. The claims require an honest bound and exact execution. Separate agent review checked these assumptions. |
| Reproduction | The documented clean rerun matched all nine deterministic result files. Both commands exited with code 0. |
| Independent check | Separate code matched every case, candidate count, target set, decision, and main summary row. It did not read or import the main analyzer. A separate release agent also reviewed both codes and report claims. |
| Statistical uncertainty | Exact finite enumeration uses no sampling, fitted parameters, seed, confidence interval, or significance test. Deployment uncertainty remains unknown. |
| Controls and failures | Zero-loss equivalence, empty candidate sets, wrong inputs, hidden assignments, and false loss bounds were checked. False-bound errors remain in the report. Refusal and completion are separate outcomes. |
| Compute | Local CPU, Python version, elapsed times, machine model, and installed memory are recorded. Peak process memory was not measured. No training or paid compute. |
| Ethics and privacy | Synthetic fields only. No account records, secrets, human subjects, or personal data. Risks of unverified bounds and unsafe deployment are stated. |
| Rights | No third-party code, dataset, model weights, or full source text is redistributed. Citations and read scopes are preserved. No new license is assigned. |
| AI and review status | Codex generated the study, code, and report. Separate Codex review is stated. No human or external peer review occurred. |
| Publication | Authorized target: gavenren/ai-safety-research, main. Remote commit and file verification are required after upload. Local checks alone do not prove publication. |

The final release inventory binds the reviewed files. Task state stores the later remote verification receipt.
