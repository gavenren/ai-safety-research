# Plan: retry timing with finite request memory

Date: October 18, 2026 (America/Toronto). Save and hash this plan and config.json before code or enumeration. This is a local plan record, not external preregistration.

## Question and contribution

For one logical operation, can a retry cutoff based on send time prevent duplicate effects when the receiver forgets prior requests after a finite period? Does a success reply establish that no earlier message can create a later duplicate?

The artifact contribution is an exact synthetic regression corpus, paired counts, boundary cases, and small proofs for seven prescribed rules. RIFL and later work already establish the finite-retention problem. No new protocol, first discovery, provider defect, or real-agent performance claim is intended. The October 15 model used ideal permanent deduplication. October 16 and 17 concern field reads and repair decisions. This study adds an explicit request-memory lifetime and timed transport.

## Fixed model

Time is an integer tick, not a measured second. One client wants one append effect. The payload is fixed. There are three possible send slots, numbered 0, 1, 2, at times 0, s, 2s. A slot is used only if the policy permits it and no earlier success receipt has been observed. The first slot is always sent. This exception also applies to Delay margin when its bound is greater than the retention period.

Each slot is assigned one transport code before any policy runs. Code 0 is a permanent drop before arrival. For d from 0 through D, code 1+2d means arrival d ticks after send with a lost success reply; code 2+2d means that arrival with an immediately visible success reply. The client cannot see assigned future outcomes. A dropped request never arrives. No request is duplicated by transport. The only requests are those the controller sends. An unused slot's code remains part of the corpus assignment but has no effect.

Each arrived request is handled atomically: deadline check, lookup, optional append, and request-record storage are one event. There is no queue after admission, crash, partial effect, concurrent user, key collision, payload change, or account permission change. The request identity is stable in all rules except New key. A successful append creates a new effect number. A cache hit returns the stored effect number without another append. A success reply is truthful about that one effect. It does not report a global effect count. A visible first success stops all later sends, but already sent requests still arrive and are processed. The final audit drains every sent request. Rejected receiver deadlines do not produce a success receipt; the model does not expose other feedback to the client.

Finite request memory keeps an entry from its effect time c until, but not including, c+T. At an arrival at time t, an entry is expired if t-c >= T. A cache hit does not extend retention. After expiry a matching key is treated as new. The entry and effect are written atomically. This exact-expiry rule is a model assumption, not an assertion about any provider. In the permanent reference, entries never expire.

At each time, arrivals from earlier sends run first, in increasing slot number. They can stop the send scheduled at that time. Then the scheduled slot is considered. Its zero-delay arrival runs immediately after its send. Events have a sequential index, including within the same tick. Thus a later event can occur after a receipt at the same tick. After all three send slots, any remaining arrivals run in time and slot order.

## Rules

| Code | Rule |
| --- | --- |
| no_retry | Send slot 0 only. Finite memory. |
| new_key | Permit every slot until a success receipt. Give each used slot a distinct key. Finite memory. |
| stable_key | Permit every slot until a success receipt. Use one key. Finite memory. |
| send_cutoff | Use one key. Permit a retry only when send time t<T. Finite memory. |
| delay_margin | Use one key. Permit a retry only when t+B<T, where B is the declared bound from send to atomic receiver handling. Finite memory. Slot 0 is always permitted. |
| receiver_cutoff | Use send_cutoff. In addition, the receiver rejects all arrivals at t>=T, including a late first attempt. The absolute deadline T is fixed at the logical operation's time origin and never renewed. Finite memory. |
| permanent | Permit every slot until a success receipt. Use one key and permanent request memory. |

Receiver cutoff and Permanent require stronger server capabilities. Delay margin needs a correct delay bound and a common time scale; the client does not observe the first actual effect time. These are explicit assumptions, not claimed browser features.

## Main grid and stress grid

Main: T in {1,2,3,4,5}; D in {0,1,2,3}; s in {1,2,3}; B=D. Each setting has q=2D+3 transport codes per slot, hence q^3 assignments. All assignments run all seven rules on separate fresh server states. There are 60 settings, 18,360 assignments, and 128,520 rule assignments. Different unused suffixes retain multiplicity. Counts are finite corpus totals, not estimates of natural probabilities.

Stress: T=3, D=2, s=1, B=1. Actual delay exceeds the declared bound. Keep all 343 assignments and all seven rules. These 2,401 rule assignments remain separate from the main grid. This tests a broken premise, not failure of a theorem whose premise holds.

Primary displayed setting: main T=2,D=3,s=1, 729 assignments per rule. Also report paired availability costs in main T=4,D=2,s=1, with 343 assignments. No setting will be selected after results to replace these.

## Measures

Final effect count; number of sends, arrivals, cache hits, rejected arrivals, expired-key encounters; first receipt time and returned effect number; effect count at that receipt; final event time; and event traces.

- duplicate: final effect count >1.
- confirmed: at least one success receipt was visible.
- false_exact_claim: confirmed and final count !=1. This scores a hypothetical controller that promotes a success receipt to a terminal claim of exactly one effect. The service receipt itself is not false.
- wrong_at_receipt: first receipt exists and count at that event >1.
- late_duplicate: first receipt exists and a second-or-later append occurs at a later event index, including a later event at the same tick.
- future_only_false: false_exact_claim and count at the first receipt equals 1.
- missed: final count=0.
- unconfirmed_one: final count=1 with no visible success receipt.
- unconfirmed_duplicate: final count>1 with no visible success receipt.
- clean_confirmed: confirmed and final count=1.

Some labels overlap. The four-way partition missed, unconfirmed_one, unconfirmed_duplicate, and confirmed covers every assignment; split confirmed into clean and false for a five-way partition. Do not sum overlapping error labels.

For each setting, compare each rule with Permanent on the same assigned codes. Count cases where Permanent has an effect but the rule has none; where Permanent confirms but the rule does not; where the rule creates a duplicate but Permanent does not; and where each rule has clean confirmation and Permanent has none. These are matched synthetic outcomes, not randomized causal or runtime estimates.

## Hypotheses and decision rules

H1: Stable key has at least one main duplicate; Send cutoff also has at least one main duplicate. A key and a send-time cutoff alone are insufficient in this model.

H2: No retry, Delay margin, Receiver cutoff, and Permanent each have zero duplicate and false-exact-claim cases in every main setting.

H3: Send cutoff has at least one main future-only false claim: the receipt-time count is one, but the drained final count exceeds one.

H4: Delay margin and Receiver cutoff each have at least one main case with no effect when Permanent has an effect. Safety does not imply equal completion opportunity.

H5: Delay margin has at least one duplicate in the separate broken-bound stress grid. Receiver cutoff and Permanent have zero stress duplicates.

Retain pass or fail for every hypothesis. Retain all zero-error settings and all cost cases. No sampling, significance test, training, or confidence interval is appropriate for these exact finite counts.

## Controls and proofs

Check all-drop and immediate-visible-success controls. Check finite memory just before, exactly at, and after expiry. Check that a cache hit does not renew the record. Check reordered arrivals and requests delivered after a first success. Check deadline equality, the initial-send exception, and safe margin with B>=D. Check that output labels use drained effects, not the last client action. Verify conservation of the five-way partition.

Prove that No retry and Permanent cannot create two effects. For Delay margin, if any retry is allowed under B>=D, then D<T and all possible sent arrivals occur before T; this is earlier than the first effect time plus T. If no retry is allowed, one send is safe. For Receiver cutoff, all accepted arrivals are before T; the same argument applies. State the initial-only exception and server atomicity clearly.

For each setting, rule, and nonempty error label in {duplicate,false_exact_claim,future_only_false,late_duplicate}, retain a minimum witness ordered by sends, arrivals, final event time, then the complete three-code tuple. Preserve complete witness events.

## Reproduction, review, and rights

Use local Python standard-library programs and exact integers. Save config, plan hashes, environment, raw traces, summaries, paired results, witnesses, tests, and logs. Use deterministic JSON and gzip. Request an independent implementation from this plan without access to the main code. Run documented commands from a fresh folder and compare generated files. Review source claims and proofs separately. Use the NeurIPS checklist as a review aid. Record errors and any later amendment; do not silently change frozen inputs.

All records are synthetic. There will be no account writes, paid service, real browser trial, training, or redistribution of source papers or code. Codex authorship and actual agent/human review status will be explicit. No new license will be assigned. Publication needs source, privacy, content, code, and remote-file checks.
