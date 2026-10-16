# Prospective saved-field contract

Date: 2026-10-15. This contract applies only to the new field-check trials. It does not rescore earlier trials. Freeze this file with the checker and tests before scored execution.

## Inputs and observation sources

The checker receives field values and observation facts. The analyzer must derive each from cited saved sources. A runner's verdict or `fields_match` flag is not a value source. Preserve missing keys. Do not replace them with empty values.

`calendar_fields(token, ui, event, expected_date)` accepts native saved UI values and one detailed Calendar connector `structuredContent`. The default target date is 2026-10-14. Search rows do not contain all required fields and cannot replace a detailed read.

| Native UI key | Correct value | Source |
| --- | --- | --- |
| title | exact operation token | Reloaded native Title control |
| description | exact operation token | Read-only visible Description textbox text |
| all_day | Boolean true | Present native All day checkbox is checked |
| start_date | `2026-10-14` | Native Start date, converted from the explicit displayed calendar date |
| end_date | `2026-10-14` | Native inclusive End date, converted as above |
| availability | `Free` | Native Show as control |
| visibility | `Private` | Native Visibility control |
| recurrence | `Does not repeat` | Native Recurrence control |
| guests | empty list | Explicit empty Guests section |
| location | empty string | Explicit empty Add location control |
| conference | Boolean false | Native Add Google Meet control and no existing conference |
| reminders | empty list | Present empty Notifications list |

Calendar preflight shows that the accessibility snapshot omits Description text. A read-only DOM read of the visible native textbox supplies its text. Keep that read and its source state. It must follow a native reload and precede any new edit. Do not infer this value from the title or a runner declaration.

The detailed connector checks are: exact summary token, `status=confirmed`, `transparency=transparent`, `visibility=private`, explicit `attendees=[]`, explicit empty location and hangout_link, explicit empty recurrence and recurring_event_id, and `reminders.use_default=false` with `reminders.overrides=[]`. The observed null values count as empty only for location, hangout_link, recurrence, and recurring_event_id. Missing keys are UNKNOWN. Strings and lists must have the supported types. Integer zero is not Boolean false.

The connector description must be the token followed by zero or more CR or LF characters. Only trailing CR/LF characters are removed. Spaces, tabs, case, leading or interior line breaks, and extra tokens are significant. HTML or angle-bracket text is UNKNOWN under this narrow contract. Preflight returned the token plus two LF characters and no HTML. The native visible description must equal the token exactly.

The connector start must equal `2026-10-14T00:00:00`. Its exclusive end must equal `2026-10-15T00:00:00`. A valid different no-offset date-time is MISMATCH. A missing, invalid, offset, or otherwise unsupported date representation is UNKNOWN. These are the tool's observed strings. They are not raw Google API date keys or proof of a UTC instant. The native All day and inclusive date controls are required independently.

`notion_fields(token, ui)` requires `title=token`, `marker=token`, `verified=false`, and `body_empty=true`. The saved native title comes from the banner plus read-only native title textbox text. Marker comes from the Page properties row named Marker and its value button. The explicit Empty value button means an empty string. The present Verified checkbox supplies true when checked and false when not checked. An absent checkbox is unknown. The empty-page prompt supplies empty-body evidence. A nonmodal Writing Replay prompt is accepted only when it does not cover the title or properties and there is no pending editor. This does not claim that an arbitrary dialog is safe.

## Saved-record gate

`check_record` combines those field results with `first_id`, `ui_id`, `service_id`, `operation_ids`, and the following Boolean facts: `native_ready`, `native_fresh`, `service_ready`, `service_fresh`, `coverage_ready`, `coverage_fresh`, `scope_covered`, and `edit_pending`. Notion passes `needs_service=false`; Calendar uses the default true. Fresh means a completed read after the latest admitted mutation. The analyzer must check that order from the logs. Ready means that the relevant native controls or covered view are complete and readable.

The identity list is the complete set of operation records within the saved scope. It must contain exactly the first native ID. The UI ID must agree; the Calendar service ID must also agree. An unresolved native-ID mapping is UNKNOWN. A title is not an identity. Repeated occurrences of the same ID in an input list are an invalid list, not two proved records.

MATCH requires all required checks to match. Any definite wrong field or identity makes MISMATCH, even when another field is unknown. Keep every unknown in the per-field results. If any required native, service, or coverage read is stale, not ready, or outside the required scope, the overall saved-record result is UNKNOWN. A pending edit also gives UNKNOWN. Keep field subresults for diagnosis, but do not use stale or incomplete evidence to permit repair. Do not score a draft as a saved mismatch. A conflict that supplies one definite wrong supported value is MISMATCH. Unsupported representations remain UNKNOWN.

## Action gate and comparison

`next_action` receives the computed record status, Create and repair admissions, and supported Boolean facts. Reserve each mutation before its potentially effective call. After one Create admission, no input permits another Create. A MISMATCH can permit one same-ID repair only when the retained identity is known, no write is pending, and the assigned target is known wrong. An UNKNOWN permits a read, not a mutation. A second failed correction, excess mutation count, or deadline gives UNRESOLVED. A final MATCH can permit confirmation. Live agents apply these rules and retain action logs; the reference function is not an autonomous browser controller.

`baseline_title_count` is an offline paired check of the same initial saved evidence. It returns MATCH only for a fresh, ready, covered singleton with the exact title. It does not use non-title fields or execute a second policy. Its wrong matches are counterfactual classification errors, not live claims.

## Checks before freeze

The code tests cover correct and deliberately wrong fields, narrow description equality, missing values, unsupported types, field conflicts, date formats, exclusive end, optional fields, identities, counts, pending edits, readiness, and mutation budgets. The exhaustive local test checks 576 fact combinations after at least one Create admission. These checks do not establish a service-level exactly-once guarantee.
