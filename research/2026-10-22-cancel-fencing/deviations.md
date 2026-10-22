# Recorded procedure limits

1. Drive C1 preparation was recorded at 16:28:58.248274 UTC. The revised runtime helper freeze was recorded at 16:29:21.322660 UTC. Both record the same helper bytes. The case plan and pure decision rule were frozen earlier. Do not claim that this helper freeze preceded C1 preparation.
2. Calendar C1, C3, and C4 have before-save editor evidence and saved connector readback, but no reopened post-save editor record. The initial plan called for reopen/reload plus connector read. Post-save all-day UI state is not independently verified in those cases. The target descriptions and unchanged exposed connector fields are verified. All cases are retained.
3. Calendar C2's connector read was recorded before its blocked UI read. Both follow its no-dispatch decision. Preserve the actual order.
4. Analysis and sanitizer code were written after collection. Their hashes were frozen before local scoring. The original case rules and plan were fixed before collection.

The prior runtime-helper review found an incomplete receipt evidence gate. It was corrected and separately reviewed. That issue concerns the receipt path, not the cancellation decision function. Its original review and correction remain in the package.

No provider error, failed browser save, rejected target identity, collateral mismatch, or uncertain target-field outcome was found in the eight saved cancellation cases. This statement is limited to the checked fields and recorded actions. No duplicate-effect counter or provider-wide cancellation claim is made.
