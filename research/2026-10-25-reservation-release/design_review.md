# Design review before experiment

Date: 2026-10-25. Review by a separate Codex agent. No experiment was run for this review.

## Decision and contribution limit

Proceed only as a small regression artifact for established conditions. The recent budget-conservation preprint, https://arxiv.org/html/2610.00349v1, already covers timeout refunds, late effects, retained uncertain holds, fences, terminal evidence, and effect coverage. Its introduction and Sections 2.3–2.5 explicitly distinguish ledger accounting from external exposure. A generic timeout-refund example is not a new finding.

A useful narrower artifact can separate four times: provider acceptance, irreversible charge, receipt delivery, and fence installation. It can compare a point observation with a terminal no-effect certificate. Report both observed overspend and uncovered liability before overspend. The October 24 study tests admission inside one local database; it expressly excludes later external effects and settlement. The October 22 cancellation study tests authority of a stale worker; it does not score conserved money or charge coverage. State these differences without claiming global priority.

The following is a proposed exact design, not frozen instructions. The lead must select, revise, and freeze the final plan before implementation. Do not treat any counts below as experimental results.

## Common provider schedule

Initially A has a reservation of a units and a request in transit. A has not yet been accepted. B has no reservation and makes one later request. The total budget is C. Choose a and b from {1,2}, C from {1,2,3,4}, and retain only a <= C. This gives 14 demand/capacity settings.

Use six named events:

- A: the provider attempts to accept the request for A. If F has occurred, reject acceptance. Otherwise accept it.
- E: the provider resolves A. If accepted, the chosen branch charges a units or finishes with no charge. If acceptance was rejected, the result is no charge in either branch. No later effect remains possible after E.
- T: deliver the correct final outcome to the controller. It settles A exactly once. A charge becomes committed spend; no charge returns the reservation.
- O: read whether a charge exists now. This is a point observation. It neither blocks acceptance nor cancels accepted work.
- F: atomically close future acceptance of A and record a provider snapshot. It does not cancel already accepted work. The snapshot includes accepted, resolved, and charged status. A sound no-effect certificate exists at F only if A was not accepted, or A is already resolved with no charge.
- D: make the rule's one release decision and then attempt to admit and immediately charge B.

Retain all orders with A < E < T and O < D. There are 6!/(3!*2!) = 60 orders. Include both E branches. There are 14*60*2 = 1,680 input worlds. Five rules give 8,400 rule outcomes. Branch copies after a rejected acceptance are deliberate controls, not independent observations. Preserve that multiplicity and state it.

Every rule receives the same O, F, and T events at the same points. This is a comparison of evidence use. It is not a comparison of fence deployment costs. No rule changes the event order. B admission uses one atomic local balance check for every rule.

## Five possible release rules

All rules first honor a final outcome delivered by T. If T precedes D, the hold is already settled and no speculative refund is needed. Otherwise:

1. Timeout: release the complete A hold at D.
2. ZeroObservation: release at D only if O reported no charge. O is always before D but can be stale.
3. FenceOnly: release at D only if F has occurred.
4. ClosureCertificate: release at D only if F supplied the sound no-effect certificate defined above.
5. TerminalOnly: keep the hold until T.

Use exact names and conditions in the final plan. A pure current zero-charge result does not certify non-acceptance or prevent a later charge. A fence acknowledgement proves only exclusion of new acceptance. Already accepted work can still charge. The certificate has a stronger interface than FenceOnly, and that assumption must be explicit.

If D precedes T and an unsafe rule has already released A's hold, T still records the actual charge correctly. Do not discard that late receipt or invent a negative reservation. Use a hold of zero or a, a committed-A amount of zero or a, and an available balance C - holdA - committedA - committedB. This balance can become negative under an unsafe rule. A signed accounting identity is not a nonnegative-budget guarantee.

## Truth and measures

Keep provider truth separate from controller evidence. Define provider liability L_A after each event:

- If A charged, L_A = a permanently.
- If A is resolved without charge, L_A = 0 permanently.
- If A is accepted and unresolved, L_A = a.
- If A is not yet accepted and F has not occurred, L_A = a because the in-transit request can still be accepted.
- If A was not accepted and F has occurred, L_A = 0.

The preselected future outcome branch must not be used to reduce L_A while work remains unresolved. Otherwise the audit uses hindsight and understates uncertainty.

Recommended measures, at each step and by case:

- Actual charge above budget: actual_A_charge + committed_B > C.
- Exposure above budget: L_A + committed_B > C. This can occur before an actual charge breach.
- Uncovered A liability: max(0, L_A - holdA - committedA). Record first occurrence and maximum amount.
- Premature refund: D removes a positive hold while L_A > 0. This is a contract failure, not a claim that the test agent used natural language incorrectly.
- Negative local available balance after a late receipt.
- B acceptance and refusal.
- Safe-feasible B refusal: B is refused although L_A immediately before D plus b is at most C. This uses authoritative model truth, not the selected future branch. It measures conservative lost opportunity, not an unsafe policy error.
- Number of A acceptances blocked by the common fence and final A outcome.

Do not combine these overlapping counts into one failure total. Preserve a final-state score and the first bad prefix; all final receipts arrive in this model, so an earlier exposure violation can be hidden by a final no-charge result.

## Controls and independent checks

- T before D: all five rules must make the same B decision.
- F before A: later A acceptance is rejected. The closure certificate is valid and remains valid.
- A before F before E: the fence leaves accepted work able to charge.
- O before E with no observed charge: the point observation can be true and still insufficient for release.
- E no-charge before F: the certificate can close a previously accepted job.
- E no-charge after F but before D, with T after D: the saved certificate may remain unavailable even though safe-feasible B admission is now possible.
- C >= a+b: no actual or exposure breach, but an uncovered-A score can still expose a broken coverage contract.
- Every policy must retain correct arithmetic and exactly one settlement. Do not score a local balance check as permission to refund an unresolved hold.

Two implementations should be written separately from the frozen plan. Compare every input, observation, decision, state transition, and score. Check schedule enumeration using a different generator or positional formula. Two deterministic runs are enough if no defect is found. No sample confidence interval is appropriate for the finite designed corpus.

## Safety argument to check after implementation

For TerminalOnly, the hold covers A until a correct terminal receipt replaces it with actual spend or a zero outcome. For ClosureCertificate, an early release requires a proof that A cannot charge later; the fence and status snapshot share one authoritative event. Thus held or committed A covers L_A before B admission. The atomic local balance check then keeps L_A plus B at most C. This argument is conditional on correct price bounds, complete acceptance mediation, sound certificates, and correct settlement. It does not apply to untracked external writers or incomplete cancellation receipts.

## Further cautions

Call this a finite simulation. Real SQLite code is unnecessary unless it tests a separate implementation claim; the selected question concerns an external-effect protocol. Do not label local events as real provider behavior. There is no model-action selection or production account test. No new protocol, production risk rate, or novelty priority follows from this artifact.

The source paper was read for its introduction and Sections 2.3–2.5 during this review. The source agent is checking closer protocol and evaluation sections. Do not present this design review as a full audit of that paper.
