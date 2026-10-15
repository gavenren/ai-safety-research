# Runner A notes

All 16 assigned trials finished. Each first decision had one exact-token row. Each pre-reload and ready post-reload audit had one exact-token row. No retry, scheduled wait, or rule-driven filter removal was used. All eight Documents assignments had an automatic change to All before the first decision. The four Receipt trials also had an exact-token creation receipt.

The D01 log closure captured setup. An append-only correction maps its records to D01. The raw records remain unchanged. D01 and D02 result annotations add observed view fields. D02 app behavior is not a policy error.

D18 had one failed post-reload observation after its recorded decision. The reload action itself logged ok. The first recovery state had disabled New; the next ready state showed one D18 row. No write was repeated.

Some early Documents baseline captures were loading states. All later full states remain available. D02 and D06 need careful baseline review; do not infer zero from a loading state. From D18 onward, explicit ready empty states were captured before opening New.

The tab is 591349075. It is marked for handoff so the lead can continue the audit and cleanup. No cleanup or publication was done by this runner.
