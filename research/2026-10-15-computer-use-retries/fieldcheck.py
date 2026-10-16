#!/usr/bin/env python3
"""Prospective field checks, not a browser driver. Use extracted saved values.

The analyzer must derive readiness, freshness, identity, coverage and values from
source records. A runner's success label is not an observation. Prior scores
are not changed by this file. No function here executes any write.
"""
from datetime import date, datetime, timedelta
import re
MATCH, MISMATCH, UNKNOWN = 'MATCH', 'MISMATCH', 'UNKNOWN'
MISSING = object()


def combine(statuses):
    values = tuple(statuses)
    if not values or any(x not in (MATCH, MISMATCH, UNKNOWN) for x in values):
        return UNKNOWN
    return MISMATCH if MISMATCH in values else UNKNOWN if UNKNOWN in values else MATCH


def result(value, expected, status, reason):
    return dict(observed=None if value is MISSING else value, present=value is not MISSING,
                expected=expected, status=status, reason=reason)


def exact(value, expected):
    if value is MISSING or type(value) is not type(expected):
        return result(value, expected, UNKNOWN, 'missing_or_unsupported_type')
    return result(value, expected, MATCH if value == expected else MISMATCH, 'exact_value')


def description(value, token, *, connector=False):
    if type(value) is not str:
        return result(value, token, UNKNOWN, 'missing_or_unsupported_type')
    if '<' in value or '>' in value:
        return result(value, token, UNKNOWN, 'unsupported_html_or_angle_text')
    compared = value.rstrip('\r\n') if connector else value
    return result(value, token, MATCH if compared == token else MISMATCH,
                  'trailing_cr_lf_only' if connector else 'exact_visible_text')


def date_value(value, expected, *, connector=False):
    if type(value) is not str:
        return result(value, expected, UNKNOWN, 'missing_or_unsupported_type')
    pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' if connector else r'\d{4}-\d{2}-\d{2}'
    try:
        if not re.fullmatch(pattern, value):
            raise ValueError()
        (datetime if connector else date).fromisoformat(value)
    except ValueError:
        return result(value, expected, UNKNOWN, 'unsupported_date_representation')
    return exact(value, expected)


def empty_optional(value, types):
    if value is MISSING or (value is not None and type(value) not in types):
        return result(value, None, UNKNOWN, 'missing_or_unsupported_type')
    return result(value, None, MATCH if value in (None, '', [], {}) else MISMATCH,
                  'explicit_empty')


def reminders(value):
    target = dict(use_default=False, overrides=[])
    if type(value) is not dict:
        return result(value, target, UNKNOWN, 'missing_or_unsupported_type')
    checks = [exact(value.get(k, MISSING), v)['status'] for k, v in target.items()]
    return result(value, target, combine(checks), 'explicit_disabled_reminders')


def summary(checks):
    return dict(status=combine(x['status'] for x in checks.values()), checks=checks)


def calendar_fields(token, ui, event, expected_date='2026-10-14'):
    """UI: title, description, all_day, start_date, end_date, availability,
    visibility, recurrence, guests, location, conference, reminders.
    UI dates are ISO dates parsed from the native displayed dates. UI description
    is native textbox visible text read after reload. Empty UI lists require
    explicit empty sections, not an absent key. Event is detailed connector
    structuredContent, not a search row. No-offset strings do not prove UTC or
    All day. Identity is checked separately by check_record.
    """
    if type(token) is not str or not token or '<' in token or '>' in token:
        raise ValueError('Invalid plain token')
    day = date.fromisoformat(expected_date)
    if day.isoformat() != expected_date or type(ui) is not dict or type(event) is not dict:
        raise ValueError('Invalid date or observation dictionary')
    end = (day + timedelta(days=1)).isoformat()
    c = {}
    for key, want in [('title',token), ('all_day',True), ('availability','Free'),
                      ('visibility','Private'), ('recurrence','Does not repeat'),
                      ('guests',[]), ('location',''), ('conference',False), ('reminders',[])]:
        c['ui.'+key] = exact(ui.get(key,MISSING),want)
    c['ui.description'] = description(ui.get('description',MISSING),token)
    for key in ('start_date','end_date'):
        c['ui.'+key] = date_value(ui.get(key,MISSING),expected_date)
    for key, want in [('summary',token), ('status','confirmed'), ('attendees',[]),
                      ('transparency','transparent'), ('visibility','private')]:
        c['connector.'+key] = exact(event.get(key,MISSING),want)
    c['connector.description'] = description(event.get('description',MISSING),token,connector=True)
    for key, want in [('start',expected_date), ('end',end)]:
        c['connector.'+key] = date_value(event.get(key,MISSING),want+'T00:00:00',connector=True)
    for key, types in [('location',(str,)), ('hangout_link',(str,)),
                       ('recurrence',(list,)), ('recurring_event_id',(str,))]:
        c['connector.'+key] = empty_optional(event.get(key,MISSING),types)
    c['connector.reminders'] = reminders(event.get('reminders',MISSING))
    return summary(c)


def notion_fields(token, ui):
    """Values: title, marker, verified bool, body_empty bool.
    Extract title from saved native textbox/banner; Marker from its value button
    (Empty is explicit empty); Verified from its checkbox; body_empty from the
    empty-page prompt. Missing controls do not mean empty or unchecked.
    """
    if type(token) is not str or not token or type(ui) is not dict:
        raise ValueError('Invalid Notion observation')
    return summary({'ui.'+k:exact(ui.get(k,MISSING),v) for k,v in
                    [('title',token),('marker',token),('verified',False),('body_empty',True)]})


def check_record(field_result, *, first_id, ui_id, service_id=MISSING,
                 operation_ids=MISSING, native_ready=False, native_fresh=False,
                 service_ready=False, service_fresh=False, coverage_ready=False,
                 coverage_fresh=False, scope_covered=False, edit_pending=True,
                 needs_service=True):
    """Facts must have source witnesses; booleans are not coerced.
    A known wrong field/identity wins over another unknown field only when all
    required evidence gates pass. Stale or incomplete evidence cannot authorize
    a repair. All checks must pass for MATCH.
    """
    if type(field_result) is not dict or type(field_result.get('checks')) is not dict:
        raise ValueError('Invalid field result')
    c = dict(field_result['checks'])
    local = locals()
    requirements = ['native_ready','native_fresh','coverage_ready','coverage_fresh','scope_covered']
    if needs_service is not False:
        requirements += ['service_ready','service_fresh']
    for key in requirements:
        v = local[key]
        c['evidence.'+key] = result(v,True,MATCH if v is True else UNKNOWN,'observation_requirement')
    c['evidence.no_pending_edit'] = result(edit_pending,False,
                          MATCH if edit_pending is False else UNKNOWN,'pending_write')
    valid_id = type(first_id) is str and bool(first_id)
    c['identity.first'] = result(first_id,'nonempty native identity',
                                MATCH if valid_id else UNKNOWN,'first_identity')
    for key,value in [('ui',ui_id)]+([('service',service_id)] if needs_service is not False else []):
        c['identity.'+key] = exact(value,first_id) if valid_id and type(value) is str and value else result(value,first_id,UNKNOWN,'identity_missing_or_unresolved')
    if type(operation_ids) is not list or any(type(x) is not str or not x for x in operation_ids):
        count = result(operation_ids,[first_id],UNKNOWN,'invalid_or_missing_identity_list')
    elif len(operation_ids)!=len(set(operation_ids)):
        count = result(operation_ids,[first_id],UNKNOWN,'duplicate_identity_list_entries')
    elif not valid_id:
        count = result(operation_ids,[first_id],UNKNOWN,'first_identity_unknown')
    else:
        count = result(operation_ids,[first_id],MATCH if operation_ids==[first_id] else MISMATCH,'covered_identity_set')
    c['identity.coverage'] = count
    r = summary(c)
    if any(local[key] is not True for key in requirements) or edit_pending is not False:
        r['status'] = UNKNOWN
    return r


def baseline_title_count(title, token, operation_ids, *, ready=False, fresh=False, scope_covered=False):
    """Offline paired decision, not an executed browser policy."""
    if ready is not True or fresh is not True or scope_covered is not True:
        return UNKNOWN
    if type(title) is not str or type(operation_ids) is not list:
        return UNKNOWN
    if any(type(x) is not str or not x for x in operation_ids) or len(operation_ids)!=len(set(operation_ids)):
        return UNKNOWN
    return MATCH if title==token and len(operation_ids)==1 else MISMATCH


def next_action(status, *, creates, repairs, same_identity=False,
                target_mismatch=False, pending=False, deadline=False, baseline_empty=False):
    """Reserve mutation counts before each potentially effective call."""
    if status not in (MATCH,MISMATCH,UNKNOWN):
        raise ValueError('Invalid status')
    if type(creates) is not int or creates<0 or type(repairs) is not int or repairs<0:
        raise ValueError('Invalid mutation count')
    for x in (same_identity,target_mismatch,pending,deadline,baseline_empty):
        if type(x) is not bool:
            raise ValueError('Invalid boolean fact')
    if deadline or creates>1 or repairs>1:
        return 'UNRESOLVED'
    if creates==0:
        return 'CREATE' if baseline_empty and repairs==0 and not pending else 'READ'
    if pending or not same_identity:
        return 'READ'
    if status==MATCH:
        return 'CONFIRM'
    if status==MISMATCH:
        return 'REPAIR_SAME_ID' if repairs==0 and target_mismatch else 'UNRESOLVED'
    return 'READ'
