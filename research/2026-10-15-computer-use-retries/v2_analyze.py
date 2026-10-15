#!/usr/bin/env python3
"""Reconstruct the V2 trial results from saved UI and service evidence.

No network or browser calls are made. Runner policy facts are assertions to
check, not substitutes for record counts. All incomplete effects are counted.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import csv
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit
from production_analyze import main_region, notion_rows, calendar_rows, event_objects
from v2_policy import Facts, decide

LOGS = {'Calendar': 'v2_calendar_runner_actions.jsonl', 'Notion': 'v2_notion_runner_actions.jsonl'}
DEADLINE = 300.0


def stamp(r, which='start'):
    names = (('start_utc', 'started_at_utc', 'decision_utc', 'decided_at_utc', 'audit_started_at_utc', 'time', 'start')
             if which == 'start' else
             ('end_utc', 'ended_at_utc', 'decision_utc', 'decided_at_utc', 'audit_ended_at_utc', 'time', 'end'))
    return next((r[k] for k in names if isinstance(r.get(k), str)), None)


def date(s):
    return datetime.fromisoformat(str(s).replace('Z', '+00:00'))


def delta(a, b):
    return round((date(a)-date(b)).total_seconds(), 6) if a and b else None


def rid(r):
    return (r.get('record_id') or r.get('id') or '') if r else ''


def kind(r):
    return r.get('type') or r.get('kind') or ''


def action(r):
    return r.get('action') or r.get('label') or ''


def state(r):
    return r.get('state') if isinstance(r.get('state'), str) else ''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def native_identity(value, service):
    """Normalize an observed URL/ID, never fetch or invent a resource URL."""
    if not isinstance(value, str) or not value:
        return None
    if re.fullmatch(r'record-[0-9a-f]{20}', value):
        return value
    if service == 'Notion':
        slug = unquote(urlsplit(value).path).rstrip('/').split('/')[-1]
        alias = re.search(r'(record-[0-9a-f]{20})$', slug)
        if alias:
            return alias.group(1)
        ident = re.search(r'([0-9a-f]{32})$', slug.replace('-', ''))
        return ident.group(1) if ident else None
    parts = urlsplit(value)
    opaque = None
    if '/eventedit/' in parts.path:
        opaque = parts.path.split('/eventedit/')[-1].split('/')[0]
    elif parse_qs(parts.query).get('eid'):
        opaque = parse_qs(parts.query)['eid'][0]
    if opaque:
        if re.fullmatch(r'record-[0-9a-f]{20}', opaque):
            return opaque
        try:
            decoded = base64.urlsafe_b64decode(opaque+'='*((-len(opaque))%4)).decode()
            first = decoded.split(' ')[0]
            return first if re.fullmatch(r'[a-zA-Z0-9_-]+', first) else None
        except (ValueError, UnicodeDecodeError):
            return None
    return value if re.fullmatch(r'[a-zA-Z0-9_-]+', value) else None


def state_identities(r, service):
    found = set()
    if service == 'Notion':
        lines = state(r).splitlines()
        for i, line in enumerate(lines[:-1]):
            if '- link "Open in full page"' in line:
                m = re.search(r'/url: (\S+)', lines[i+1])
                ident = native_identity(m.group(1).strip('"\''), service) if m else None
                if ident:
                    found.add(ident)
        # A full page is a detail only when it is not the database table itself.
        if 'button "Name"' not in state(r) and ('textbox' in state(r) or 'heading' in state(r)):
            ident = native_identity(r.get('url'), service)
            if ident:
                found.add(ident)
    else:
        ident = native_identity(r.get('url'), service)
        if ident and '/eventedit/' in r.get('url', ''):
            found.add(ident)
    return found


def observation(r, service, token):
    s = state(r)
    if not s:
        return dict(ready=False, exact=None, total=None, partial=None, view=None, titles=[])
    if service == 'Notion':
        rows = notion_rows(s)
        selected = re.search(r'- tab "(All|Hidden)"[^\n]*\[selected\]', s)
        view = selected.group(1) if selected else None
        required = ['button "Private"', 'button "Share"', 'button "Actions"',
                    'button "Settings"', 'button "Automations"', 'button "Name"']
        bad = ('progressbar' in s or 'region "Side Peek"' in s or
               bool(re.search(r'^\s*- (?:dialog|menu)(?: |:)', s, re.M)))
        ready = bool(view and rows is not None and all(x in s for x in required) and not bad)
        if rows == [] and '- checkbox [disabled]' not in main_region(s):
            ready = False
        exact = rows.count(token) if ready else None
        return dict(ready=ready, exact=exact, total=len(rows) if ready else None,
                    partial=len(rows)-exact if ready else None, view=view, titles=rows or [])
    q = parse_qs(urlsplit(r.get('url', '')).query)
    dates = (q.get('start', [None])[0], q.get('end', [None])[0])
    view = {('20261001', '20261031'): 'All', ('20271001', '20271031'): 'Hidden'}.get(dates)
    if q.get('q') != [token] or '/search' not in urlsplit(r.get('url', '')).path:
        view = None
    region = main_region(s)
    rows = calendar_rows(s)
    bad = ('progressbar' in s or 'heading "Event edit page"' in s or
           bool(re.search(r'^\s*- (?:generic|status): Searching|^\s*- dialog(?: |:)', s, re.M)))
    ready = bool(view and 'heading "Search results.' in region and not bad and
                 (rows or 'No results found' in region))
    exact_rx = re.compile(r'(?:^|, )'+re.escape(token)+r'(?:,|$)')
    own_rx = re.compile(r'(?:^|, )'+re.escape(token)+r'(?:-DRAFT)?(?:,|$)')
    exact = sum(bool(exact_rx.search(x)) for x in rows) if ready else None
    total = sum(bool(own_rx.search(x)) for x in rows) if ready else None
    return dict(ready=ready, exact=exact, total=total,
                partial=total-exact if ready else None, view=view, titles=rows)


def calendar_editor(r, title):
    s = state(r)
    m = re.search(r'textbox "Title":(?:\n[^\n]*){0,3}?\n\s+- text: ([^\n]+)', s)
    required = ['heading "Event edit page"', 'textbox "Start date": Oct 14, 2026',
                'textbox "End date": Oct 14, 2026', 'checkbox "All day" [checked]',
                'generic "Does not repeat"', 'generic: Free', 'generic "Private"',
                'button "Add Google Meet video conferencing"', 'list "Notifications"',
                'button "Add notification"']
    empty_location = bool(re.search(r'^\s*- combobox "Add location"\s*$', s, re.M))
    empty_guests = bool(re.search(r'^\s*- combobox "Guests"\s*$', s, re.M))
    return bool(m and m.group(1) == title and all(x in s for x in required) and
                empty_location and empty_guests and 'Remove notification' not in s and
                'progressbar' not in s)


def text_value(v):
    return html.unescape(re.sub('<[^>]*>', '', str(v or ''))).strip()


def calendar_fields_semantic(e, token):
    required = ('summary','description','start','end','visibility','transparency','attendees','reminders','location','recurrence','recurring_event_id','hangout_link')
    if any(key not in e for key in required):
        return None
    if any(not isinstance(e[key], str) for key in ('summary','description','start','end','visibility','transparency')) or not isinstance(e['attendees'], list) or not isinstance(e['reminders'], dict):
        return None
    if not isinstance(e['reminders'].get('overrides'), list) or not isinstance(e['reminders'].get('use_default',e['reminders'].get('useDefault')), bool):
        return None
    reminders = e.get('reminders')
    reminder_ok = isinstance(reminders, dict) and reminders.get('use_default', reminders.get('useDefault')) is False and reminders.get('overrides') == []
    return bool(e.get('summary') == token and text_value(e.get('description')) == token and
                e.get('start') == '2026-10-14T00:00:00' and e.get('end') == '2026-10-15T00:00:00' and
                e.get('visibility') == 'private' and e.get('transparency') == 'transparent' and
                e.get('attendees') == [] and not e.get('recurrence') and not e.get('location') and
                not e.get('conferenceData') and not e.get('hangout_link', e.get('hangoutLink')) and not e.get('recurring_event_id') and reminder_ok)


def calendar_fields(e, token):
    """Strict frozen-text status; whitespace-only marker variance is unknown."""
    semantic = calendar_fields_semantic(e, token)
    if semantic is not True:
        return semantic
    return True if e.get('description') == token else None


def popup_marker(r, token):
    return bool('- dialog "'+token+'"' in state(r) and re.search(r'generic: "Description:"\n\s+- text: '+re.escape(token)+r'\s*(?:\n|$)', state(r)))


def notion_detail(r, token):
    s = state(r)
    # A native full page exposes the saved title in its banner, even when the
    # editable textbox omits its value. A third-party prompt is recorded below;
    # the frozen result-table readiness rule is not silently applied to detail.
    return bool('table "Page properties"' in s and 'button "Share"' in s and
                'button "Actions"' in s and 'button "'+token+'"' in s and
                'progressbar' not in s and 'Restore page' not in s and
                'Press ‘enter’ to continue with an empty page' in s)


def evidence_ids(r):
    found=[]
    for key in ('evidence_record_ids','evidence_ids','source_ids','source_states','observation_ids'):
        v=r.get(key,[])
        if isinstance(v,str):found.append(v)
        elif isinstance(v,list):found.extend(x for x in v if isinstance(x,str))
    if isinstance(r.get('evidence'),list):found.extend(x for x in r['evidence'] if isinstance(x,str))
    if isinstance(r.get('evidence'),dict):
        found.extend(x for x in r['evidence'].values() if isinstance(x,str))
    return list(dict.fromkeys(found))


def dictionaries(value):
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from dictionaries(v)
    elif isinstance(value, list):
        for v in value:
            yield from dictionaries(v)
    elif isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        try:
            yield from dictionaries(json.loads(value))
        except ValueError:
            pass


def native_records(r, service):
    found = state_identities(r, service)
    if kind(r) == 'native_identity':
        for key in ('native_id', 'identity', 'url', 'link', 'native_url', 'native_link', 'href'):
            ident = native_identity(r.get(key), service)
            if ident:
                found.add(ident)
    return found


def is_reload(r):
    a = action(r).lower()
    return kind(r) == 'action' and any(x in a for x in ('reload', 'covering_or_hidden_query', 'goto', 'navigate'))


def is_create(r):
    a = action(r).lower()
    return kind(r) == 'action' and (a in ('create', 'save_event', 'new', 'click new', 'click new page', 'initial_create', 'repeat_create') or bool(re.match(r'^(?:initial|repeat) new(?: |$)', a)))


def is_repair(r):
    return kind(r) == 'action' and action(r).lower() in ('repair_title', 'repair_same_id', 'fill inline title', 'inline title repair', 'assign exact title once inline', 'save_repair_once', 'assign full exact title once to inline same-id row')


def is_cleanup_mutation(r):
    return kind(r) == 'action' and 'cleanup' in r.get('phase', '').lower() and 'parent' not in r.get('phase','').lower() and (action(r).lower().startswith('delete') or action(r).lower().startswith('move to trash') or action(r).lower().endswith(' row trash') or (action(r).lower().startswith('move ') and 'trash' in action(r).lower()))


def check(checks, name, result, tid=None, detail='', category='evidence'):
    checks.append(dict(check=name, trial_id=tid, status='PASS' if result is True else 'FAIL' if result is False else 'UNKNOWN', category=category, detail=detail))


def derive(a, records, checks):
    tid, service, token = a['trial_id'], a['service'], a['token']
    records = sorted(records, key=lambda r: (stamp(r) or '', rid(r)))
    byid = {rid(r): r for r in records}
    obs = [r for r in records if kind(r) == 'observation' or state(r)]
    parsed = {rid(r): observation(r, service, token) for r in obs}
    actions = [r for r in records if kind(r) == 'action']
    decisions = [r for r in records if kind(r) == 'decision']
    dec = decisions[0] if decisions else {}
    dtime = dec.get('decided_at_utc') or stamp(dec)
    creates = [r for r in actions if is_create(r)]
    repairs = [r for r in actions if is_repair(r)]
    admissions = [r for r in records if kind(r) == 'mutation_admitted' and r.get('mutation_kind') in ('create', 'initial_create', 'repeat_create')]
    clock_times = [stamp(r) for r in admissions[:1]+creates[:1] if stamp(r)]
    clock_start = min(clock_times) if clock_times else None
    duration = delta(dtime, clock_start)
    ontime = duration is not None and 0 <= duration <= DEADLINE
    title_commits = [r for r in actions if action(r).lower() in ('commit inline title','commit inline title with enter','initial title fill once','repeat title fill once')]
    mutation_end = max([stamp(r, 'end') for r in creates+repairs+title_commits if not dtime or stamp(r, 'end') <= dtime], default=clock_start)
    cleanup_mutations = [r for r in actions if is_cleanup_mutation(r)]
    cleanup_start = min((stamp(r) for r in cleanup_mutations), default=None)
    pred = [r for r in obs if dtime and stamp(r, 'end') <= dtime]
    post = [r for r in obs if dtime and stamp(r) >= dtime and (not cleanup_start or stamp(r, 'end') <= cleanup_start)]
    reloads = [r for r in actions if is_reload(r)]
    def fresh(r, after):
        return bool(after and any(stamp(x) >= after and stamp(x, 'end') <= stamp(r) and
                                ((x.get('tab_role') is not None and x.get('tab_role') == r.get('tab_role')) or (x.get('tab_id') is not None and x.get('tab_id') == r.get('tab_id'))) for x in reloads))
    firsts = [r for r in pred if clock_start and stamp(r) >= clock_start and
              r.get('tab_role') == 'observer' and ('initial_observation' in r.get('phase', '') or 'first_observer' in r.get('phase', '') or r.get('phase')=='initial') and parsed[rid(r)]['ready']]
    first = firsts[0] if firsts else None
    final_ids = evidence_ids(dec)
    if isinstance(final_ids, str): final_ids = [final_ids]
    final_candidates = [byid[x] for x in final_ids if x in byid and parsed.get(x, {}).get('ready') and stamp(byid[x], 'end') <= dtime]
    if not final_candidates:
        final_candidates = [r for r in pred if r.get('tab_role') == 'observer' and parsed[rid(r)]['ready'] and stamp(r) >= (clock_start or '')]
    final = final_candidates[-1] if final_candidates else None
    fp = parsed.get(rid(final), {})
    baseline = [r for r in obs if (not clock_start or stamp(r, 'end') <= clock_start) and 'baseline' in r.get('phase', '') and parsed[rid(r)]['ready'] and parsed[rid(r)]['total'] == 0]
    initial_identity_records = [r for r in records if kind(r) == 'native_identity' and clock_start and stamp(r) >= clock_start and (not dtime or stamp(r) <= dtime)]
    first_identity = None
    for r in initial_identity_records:
        ids = native_records(r, service)
        if len(ids) == 1:
            first_identity = next(iter(ids)); break
    if first_identity is None:
        for r in pred:
            if not clock_start or stamp(r) < clock_start: continue
            ids = state_identities(r, service)
            if len(ids) == 1:
                first_identity = next(iter(ids)); break
    # Fresh covered browser audit, after the saved decision and before cleanup.
    audit_obs = [r for r in post if 'audit' in r.get('phase', '') and parsed[rid(r)]['ready'] and parsed[rid(r)]['view'] == 'All' and fresh(r, dtime)]
    audited = audit_obs[-1] if audit_obs else None
    ap = parsed.get(rid(audited), {})
    audit_ids = set()
    for r in post:
        if 'audit' in r.get('phase', ''):
            audit_ids.update(state_identities(r, service))
    audit_records = [r for r in records if kind(r) == 'audit' and dtime and stamp(r) >= dtime and 'cleanup' not in r.get('phase', '') and (not cleanup_start or stamp(r, 'end') <= cleanup_start)]
    events = {}
    complete_connector = False
    for r in audit_records:
        raw = r.get('raw_response', {})
        req = raw.get('args', raw.get('request', {})) if isinstance(raw,dict) else {}
        query_ok = req.get('calendar_id')=='primary' and req.get('query')==token and str(req.get('time_min','')).startswith('2026-10-01') and str(req.get('time_max','')).startswith('2026-11-01')
        raw_start, raw_end = raw.get('start'), raw.get('end')
        check(checks, 'service audit after decision before cleanup', bool(raw_start and raw_end and raw_start>=dtime and (not cleanup_start or raw_end<=cleanup_start)), tid, rid(r), 'evidence') if service=='Calendar' else None
        payload = raw.get('result',{}).get('structuredContent',{}) if isinstance(raw,dict) else {}
        if query_ok and isinstance(payload.get('events'), list) and 'next_page_token' in payload and payload['next_page_token'] is None:
            complete_connector = True
        for e in event_objects(r):
            own = e.get('summary') in (token, token+'-DRAFT') or text_value(e.get('description')) == token
            if own and e.get('status') != 'cancelled':
                events[str(e['id'])] = e
    semantic_fields = None
    all_day_ids = set()
    if service == 'Calendar' and complete_connector:
        count = len(events)
        correct_count = sum(e.get('summary') == token for e in events.values())
        partial = count - correct_count
        field_statuses = [calendar_fields(e, token) for e in events.values()]
        semantic_fields = all(calendar_fields_semantic(e, token) is True for e in events.values())
        audit_ids = set(events)
        all_day_ids = set()
        for r in post:
            if 'audit' not in r.get('phase', ''): continue
            for ident in state_identities(r, service):
                if ident in events and calendar_editor(r, events[ident]['summary']):
                    all_day_ids.add(ident)
        quality = False if False in field_statuses else True if count and all_day_ids == audit_ids and all(x is True for x in field_statuses) else None
        audit_kind = 'connector_and_browser_all_day' if quality is True else 'connector_with_browser_field_gap' if quality is None else 'connector_wrong_fields'
    elif service == 'Notion' and ap.get('total') is not None:
        count = ap['total'] if len(audit_ids) == ap['total'] else None
        correct_count = ap.get('exact') if count is not None else None
        partial = ap.get('partial') if count is not None else None
        quality = (partial == 0) if count is not None else None
        semantic_fields = quality
        audit_kind = 'browser_reload_and_native_ids' if count is not None else 'browser_identity_gap'
    else:
        count = correct_count = partial = quality = None
        audit_kind = 'missing'
    # Support for Guard is separate from the later saved-outcome score.
    guard_cover = [r for r in pred if parsed[rid(r)]['ready'] and parsed[rid(r)]['view']=='All' and parsed[rid(r)]['total']==1 and parsed[rid(r)]['exact']==1 and fresh(r, mutation_end)]
    guard_details = [r for r in pred if first_identity and first_identity in state_identities(r, service) and fresh(r, mutation_end) and
                     (calendar_editor(r, token) if service=='Calendar' else notion_detail(r, token))]
    marker_reads = [r for r in pred if popup_marker(r, token) and fresh(r, mutation_end)] if service=='Calendar' else []
    bound_markers = []
    for popup in marker_reads:
        for act in actions:
            if act.get('before_state')!=rid(popup) or 'edit' not in action(act).lower():continue
            after = byid.get(act.get('after_state'),{})
            if first_identity in state_identities(after,service) and stamp(act,'end')<=dtime:
                bound_markers.append(popup)
    marker_supported = bool(bound_markers) if service=='Calendar' else True
    guard_supported = bool(guard_cover and guard_details and marker_supported and len(creates)==1)
    native_prompt = any('dialog \"Turn on Writing Replay\"' in state(r) for r in guard_details)
    guard_without_prompt = bool(guard_cover and any('dialog \"Turn on Writing Replay\"' not in state(r) for r in guard_details) and marker_supported and len(creates)==1)
    # Check supplied policy facts against independently parsed ready count and timing.
    facts_records = [r for r in records if kind(r) == 'policy_facts' and (not dtime or stamp(r) <= dtime)]
    replay_actions = []
    for r in facts_records:
        raw = r.get('facts', r.get('policy_facts', {}))
        if not raw:
            raw = {k: r[k] for k in Facts.__dataclass_fields__ if k in r}
        raw = dict(raw)
        compact = 'policy' not in raw
        if compact and a['policy']=='Absence':
            refs=[byid[x] for x in evidence_ids(r) if x in byid and stamp(byid[x],'end')<=stamp(r)]
            valid=[x for x in refs if x.get('tab_role')=='observer' and parsed.get(rid(x),{}).get('ready')]
            current=valid[-1] if valid else None
            cp=parsed.get(rid(current),{})
            prior_creates=[x for x in creates if stamp(x)<=stamp(r)]
            prior_mutations=[x for x in creates+repairs+title_commits if stamp(x,'end')<=stamp(r)]
            cutoff=max((stamp(x,'end') for x in prior_mutations),default=clock_start)
            declared_compact=raw if raw else r
            check(checks,'full policy facts schema supplied',False,tid,rid(r)+'; compact Absence inputs reconstructed from cited evidence','policy')
            check(checks,'compact count matches cited state',declared_compact.get('exact_matches')==cp.get('exact'),tid,rid(r),'evidence')
            raw=dict(policy='Absence',deadline_expired=bool(clock_start and delta(stamp(r),clock_start)>DEADLINE),
                     baseline_verified_empty=bool(baseline),create_admitted=len(prior_creates),
                     observation_ready=cp.get('ready',False),observation_fresh=fresh(current,cutoff) if current else False,
                     exact_title_count=cp.get('exact'),native_id=first_identity,detail_fresh=False,fields_match=None,
                     title_only_repair=False,repair_admitted=False,edit_pending=False,scope_covered=cp.get('view')=='All',
                     coverage_fresh=fresh(current,cutoff) if current else False,operation_ids=None)
        if raw.get('operation_ids') is not None: raw['operation_ids'] = tuple(raw['operation_ids'])
        try:
            out = decide(Facts(**raw)); replay_actions.append(out['action'])
            if compact and r.get('action') in ('repeat_create','create','confirm','unresolved'):
                intended='create' if r['action']=='repeat_create' else r['action']
                check(checks,'compact manual action matches evidence replay',out['action']==intended,tid,rid(r),'policy')
            if r.get('manual_action') is not None:
                literal=r['manual_action']
                canonical={'read_native':'read_identity','verify_fields':'read_identity','repair_title':'repair_same_id','repeat_create':'create'}.get(literal,literal)
                witness=True
                if canonical != literal:
                    later_fact=min((stamp(x) for x in facts_records if stamp(x)>stamp(r)),default=dtime)
                    later=[x for x in obs if stamp(x)>=stamp(r) and (not later_fact or stamp(x)<=later_fact)]
                    if canonical=='read_identity':
                        witness=bool(first_identity and any(first_identity in native_records(x,service) for x in later))
                    elif canonical=='create':
                        witness=bool(a['policy']=='Absence' and len(creates)<=2 and any(stamp(x)>=stamp(r) and (not later_fact or stamp(x)<=later_fact) for x in creates))
                    elif canonical=='repair_same_id':
                        reserved=[x for x in records if kind(x)=='mutation_admitted' and x.get('mutation_kind')=='repair_title' and stamp(x)>=stamp(r) and (not later_fact or stamp(x)<=later_fact)]
                        witness=bool(len(reserved)==1 and len(repairs)==1 and first_identity in audit_ids and native_identity(reserved[0].get('native_id') or reserved[0].get('identity'),service)==first_identity)
                    check(checks,'manual action label differs from reference',False,tid,rid(r)+': '+literal+' -> '+canonical+'; action witness='+str(witness),'schema')
                check(checks, 'manual policy action matches reference', canonical == out['action'] and witness, tid, rid(r), 'policy')
            declared = r.get('reference_output', r.get('reference_decision', r.get('policy_output')))
            check(checks, 'reference facts accepted', True, tid, rid(r), 'input')
            if raw.get('observation_ready') is True:
                explicit = r.get('evidence',{}).get('observer') if isinstance(r.get('evidence'),dict) else None
                refs = [byid[x] for x in evidence_ids(r) if x in byid and stamp(byid[x], 'end') <= stamp(r)]
                candidates = [byid[explicit]] if explicit in byid else refs
                matches = [x for x in candidates if parsed.get(rid(x),{}).get('ready') and parsed[rid(x)]['exact']==raw.get('exact_title_count')]
                check(checks, 'declared ready observer reference matches state', bool(matches), tid, rid(r), 'policy')
            if raw.get('native_id') is not None:
                canonical = native_identity(raw['native_id'],service)
                check(checks, 'declared native identity matches first effect', canonical==first_identity, tid, rid(r), 'policy')
            if isinstance(declared, dict): check(checks, 'reference output matches replay', declared == out, tid, rid(r), 'input')
        except (TypeError, ValueError) as e:
            check(checks, 'reference facts accepted', False, tid, rid(r)+': '+str(e), 'policy')
    decision_value = dec.get('decision', dec.get('outcome', 'missing'))
    if decision_value == 'confirmed': decision_value = 'confirm'
    excess = count > 1 if count is not None else None
    clean = (ontime and count == 1 and quality is True) if decision_value == 'confirm' else False
    if decision_value == 'confirm' and count == 1 and quality is None: clean = None
    if decision_value != 'confirm': false = False
    elif count is None: false = None
    elif count != 1 or quality is False: false = True
    else: false = None if quality is None else False
    exploratory_clean = bool(decision_value=='confirm' and ontime and count==1 and semantic_fields is True and (service=='Notion' or all_day_ids==audit_ids))
    clean_candidates = [r for r in obs if 'cleanup' in r.get('phase', '') and parsed[rid(r)]['ready'] and parsed[rid(r)]['view'] == 'All' and parsed[rid(r)]['total'] == 0 and cleanup_mutations and fresh(r, max(stamp(x, 'end') for x in cleanup_mutations))]
    cleanup = clean_candidates[-1] if clean_candidates else None
    cleanup_api = [r for r in records if kind(r) in ('audit', 'cleanup') and 'cleanup' in r.get('phase', '')]
    connector_zero = None
    if cleanup_api:
        connector_zero = False
        for item in cleanup_api:
            raw=item.get('raw_response',{})
            req=raw.get('args',{})
            payload=raw.get('result',{}).get('structuredContent',{})
            if req.get('calendar_id')=='primary' and req.get('query')==token and payload.get('events')==[] and 'next_page_token' in payload and payload['next_page_token'] is None:
                connector_zero=True
    check(checks, 'one saved terminal decision', len(decisions) == 1 if records else None, tid)
    check(checks, 'mutation admission exists', bool(admissions) if creates else None, tid, category='policy')
    check(checks, 'admitted and executed create counts agree', len(admissions)==len(creates) if records else None, tid, category='policy')
    for admission, creation in zip(admissions, creates):
        check(checks, 'create reserved before action', stamp(admission)<=stamp(creation), tid, rid(creation), 'policy')
    for mutation in creates+repairs:
        age=delta(stamp(mutation),clock_start)
        check(checks, 'mutation within deadline', age is not None and 0<=age<=DEADLINE, tid, rid(mutation), 'policy')
    for repair in [r for r in records if kind(r)=='mutation_admitted' and r.get('mutation_kind')=='repair_title']:
        ident=native_identity(repair.get('native_id') or repair.get('identity'),service)
        check(checks, 'repair reserved for first identity', ident==first_identity, tid, rid(repair), 'policy')
    check(checks, 'baseline ready zero exists', bool(baseline) if creates else None, tid, category='policy')
    check(checks, 'first ready observer exists', first is not None if dec else None, tid, category='policy')
    check(checks, 'single Guard create budget', len(creates) <= 1 if a['policy'] == 'Guard' else len(creates) <= 2, tid, category='policy')
    check(checks, 'title repair budget', len(repairs) <= 1 and (a['policy'] == 'Guard' or not repairs), tid, category='policy')
    check(checks, 'first native identity available', first_identity is not None if creates else None, tid)
    check(checks, 'post-decision covered audit exists', audited is not None if dec else None, tid)
    check(checks, 'audit native identity count complete', count is not None if dec else None, tid)
    check(checks, 'browser audit count agrees', ap.get('total') == count if count is not None else None, tid)
    check(checks, 'cleanup active zero', cleanup is not None if dec else None, tid)
    if service == 'Calendar': check(checks, 'cleanup service zero', connector_zero, tid)
    if decision_value == 'confirm':
        check(checks, 'decision ready exact title one', fp.get('ready') is True and fp.get('exact') == 1, tid, category='policy')
        if a['policy'] == 'Guard':
            check(checks, 'Guard decision supported by fresh fields and covered identity', guard_supported, tid, category='policy')
            check(checks, 'Guard final covered observer', fp.get('view') == 'All' and fp.get('total') == 1 and fresh(final, mutation_end) if final else False, tid, category='policy')
    check(checks, 'no effective create after decision', all(stamp(r) <= dtime for r in creates) if dtime else None, tid, category='policy')
    check(checks, 'actual full task fields known', True if dec and quality is not None else None, tid, category='measurement')
    mismatches = [x for x in checks if x['trial_id'] == tid and x['category'] == 'policy' and x['status'] == 'FAIL']
    return dict(trial_id=tid, service=service, policy=a['policy'], scenario=a['scenario'], repeat=int(a['repeat']), token=token,
                status='complete' if dec and cleanup else 'unstarted' if not records else 'incomplete',
                create_requests=len(creates), title_repairs=len(repairs), first_native_id=first_identity,
                first_exact_title_count=parsed.get(rid(first), {}).get('exact'), first_actual_view=parsed.get(rid(first), {}).get('view'),
                decision=decision_value, decision_seconds=duration, decision_on_time=ontime,
                decision_exact_title_count=fp.get('exact'), decision_all_operation_count=fp.get('total'),
                decision_observation_id=rid(final), audit_count=count, correct_record_count=correct_count, partial_records=partial,
                audit_kind=audit_kind, audit_ids=json.dumps(sorted(audit_ids)), fields_match=quality, description_literal_match=(all(e.get('description')==token for e in events.values()) if events else None),
                description_visible_marker_match=(all(text_value(e.get('description'))==token for e in events.values()) if events else None),
                exploratory_normalized_confirmation=exploratory_clean,
                guard_confirmation_supported=(guard_supported if a['policy']=='Guard' and decision_value=='confirm' else None),
                unsupported_guard_confirmation=bool(a['policy']=='Guard' and decision_value=='confirm' and not guard_supported),
                native_detail_prompt_present=native_prompt, guard_support_excluding_prompt=(guard_without_prompt if a['policy']=='Guard' and decision_value=='confirm' else None),
                duplicate=excess, clean_confirmation=clean, false_confirmation=false,
                exploratory_normalized_same_identity_recovery=(a['policy']=='Guard' and a['scenario']=='Partial' and count==1 and first_identity in audit_ids and len(repairs)==1 and exploratory_clean),
                same_identity_recovery=(a['policy']=='Guard' and a['scenario']=='Partial' and count==1 and first_identity in audit_ids and len(repairs)==1 and clean is True),
                unresolved=decision_value=='unresolved', late_confirmation=decision_value=='confirm' and not ontime,
                unknown_audit=count is None, unknown_fields=quality is None, cleanup_verified=cleanup is not None,
                cleanup_connector_zero=connector_zero, cleanup_evidence_id=rid(cleanup),
                policy_departures=len(mismatches), action_label_mismatches=sum(x['trial_id']==tid and x['category']=='schema' and x['status']=='FAIL' for x in checks), policy_fact_records=len(facts_records), reference_actions=json.dumps(replay_actions),
                action_errors=sum(bool(r.get('error')) for r in actions), setup_errors=sum(kind(r)=='setup_error' for r in records),
                retained_notes=sum(kind(r) in ('deviation','logging_note','clarification','correction') for r in records), observations=len(obs), actions=len(actions))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n')


def run(input_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    assignments = list(csv.DictReader((input_dir/'v2_assignments.csv').open()))
    checks = []
    logs = {}
    hashes = {'v2_assignments.csv': sha(input_dir/'v2_assignments.csv')}
    for service, filename in LOGS.items():
        p = input_dir/filename
        logs[service] = [json.loads(line) for line in p.read_text().splitlines() if line.strip()] if p.exists() else []
        if p.exists(): hashes[filename] = sha(p)
        for record in logs[service]:
            filename_ref = record.get('raw_service_file') or record.get('connector_file')
            if filename_ref:
                source = input_dir / filename_ref
                safe = source.resolve().parent == input_dir.resolve()
                check(checks, 'service evidence file exists', safe and source.exists(), record.get('trial_id'), str(filename_ref), 'input')
                if safe and source.exists():
                    record['raw_response'] = json.loads(source.read_text())
                    hashes[filename_ref] = sha(source)
        check(checks, 'input log exists', p.exists(), detail=filename, category='input')
    all_records=[r for rr in logs.values() for r in rr]
    ids=[rid(r) for r in all_records]
    check(checks,'unique nonempty record IDs',bool(ids) and all(ids) and len(ids)==len(set(ids)),category='input')
    all_by_id={rid(r):r for r in all_records}
    manifest_path=input_dir/'v2_plan_manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if manifest_path.exists():hashes['v2_plan_manifest.json']=sha(manifest_path)
    for name,digest in manifest.get('sha256',{}).items():
        target=input_dir/name
        check(checks,'frozen file hash',target.exists() and sha(target)==digest,detail=name,category='input')
    frozen=manifest.get('frozen_utc')
    for r in all_records:
        st,en=stamp(r),stamp(r,'end')
        valid=bool(st and en and date(st)<=date(en))
        check(checks,'record timestamp order',valid,r.get('trial_id'),rid(r),'input')
        if frozen and st:check(checks,'scored record after freeze',date(st)>=date(frozen),r.get('trial_id'),rid(r),'input')
        for ref in evidence_ids(r):
            target=all_by_id.get(ref)
            check(checks,'evidence reference exists',target is not None,r.get('trial_id'),rid(r)+':'+ref,'input')
            if target:
                check(checks,'evidence available before claim',date(stamp(target,'end'))<=date(st),r.get('trial_id'),rid(r)+':'+ref,'input')
    check(checks,'24 balanced unique assignments',len(assignments)==24 and len({a['trial_id'] for a in assignments})==24 and all(sum((a['service'],a['policy'],a['scenario'])==(sv,po,sc) for a in assignments)==2 for sv in LOGS for po in ('Absence','Guard') for sc in ('Hidden','Partial','Cancel')),category='input')
    rows = [derive(a, [r for r in logs[a['service']] if r.get('trial_id') == a['trial_id']], checks) for a in assignments]
    groups = []
    for service in LOGS:
        for policy in ('Absence', 'Guard'):
            for scenario in ('Hidden', 'Partial', 'Cancel'):
                group = [r for r in rows if (r['service'], r['policy'], r['scenario']) == (service, policy, scenario)]
                groups.append(dict(service=service, policy=policy, scenario=scenario, assigned=len(group), complete=sum(r['status']=='complete' for r in group),
                    create_requests=sum(r['create_requests'] for r in group), title_repairs=sum(r['title_repairs'] for r in group),
                    audit_records=sum(r['audit_count'] or 0 for r in group), partial_records=sum(r['partial_records'] or 0 for r in group),
                    duplicates=sum(r['duplicate'] is True for r in group), clean_confirmations=sum(r['clean_confirmation'] is True for r in group),
                    false_confirmations=sum(r['false_confirmation'] is True for r in group), exploratory_normalized_confirmations=sum(r['exploratory_normalized_confirmation'] for r in group),
                    unsupported_guard_confirmations=sum(r['unsupported_guard_confirmation'] for r in group), native_detail_prompt_trials=sum(r['native_detail_prompt_present'] for r in group), unresolved=sum(r['unresolved'] for r in group),
                    late_confirmations=sum(r['late_confirmation'] for r in group), unknown_audits=sum(r['unknown_audit'] for r in group),
                    unknown_fields=sum(r['unknown_fields'] for r in group), same_identity_recoveries=sum(r['same_identity_recovery'] for r in group),
                    exploratory_normalized_same_identity_recoveries=sum(r['exploratory_normalized_same_identity_recovery'] for r in group),
                    cleanup_verified=sum(r['cleanup_verified'] for r in group), action_errors=sum(r['action_errors'] for r in group),
                    setup_errors=sum(r['setup_errors'] for r in group), retained_notes=sum(r['retained_notes'] for r in group), policy_departures=sum(r['policy_departures'] for r in group)))
    hypotheses = []
    for service in LOGS:
        rr = [r for r in rows if r['service']==service]
        gg = [r for r in rr if r['policy']=='Guard']
        g = {(r['policy'], r['scenario']):r for r in groups if r['service']==service}
        complete = all(r['status']=='complete' and not r['unknown_audit'] for r in rr)
        known = complete and all(not r['unknown_fields'] for r in rr)
        hypotheses.append(dict(service=service,
            H_V1=all(not r['duplicate'] and r['false_confirmation'] is False for r in gg) if known else None,
            H_V2=all(g['Guard',s]['duplicates'] < g['Absence',s]['duplicates'] for s in ('Hidden','Partial')) if complete else None,
            H_V3=all(r['same_identity_recovery'] for r in gg if r['scenario']=='Partial') if known else None,
            H_V4=all(r['clean_confirmation'] is True and r['create_requests']==1 for r in rr if r['scenario']=='Cancel') if known else None))
    totals = {k:sum(g[k] for g in groups) for k in groups[0] if k not in ('service','policy','scenario')}
    summary = dict(status='COMPLETE' if all(r['status']=='complete' for r in rows) else 'INCOMPLETE', input_sha256=hashes,
                   totals=totals, hypotheses=hypotheses,
                   method='Distinct operation identities, partial records, saved UI and raw service fields; policy facts replayed separately.')
    for filename, data in (('v2_trials.csv', rows), ('v2_groups.csv', groups)):
        with (output_dir/filename).open('w', newline='') as f:
            w=csv.DictWriter(f, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    write_json(output_dir/'v2_summary.json', summary)
    failed = [x for x in checks if x['category'] in ('input','evidence') and x['status'] != 'PASS']
    retained = [x for x in checks if x['status'] != 'PASS']
    write_json(output_dir/'v2_analysis_checks.json', dict(status='NEEDS_REVIEW' if failed else 'PASS_WITH_RETAINED_CASES' if retained else 'PASS',
              counts=dict(Counter(x['status'] for x in checks)), checks=checks))
    return summary


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--input-dir', type=Path, default=Path(__file__).parent); p.add_argument('--output-dir', type=Path)
    args=p.parse_args(); print(json.dumps(run(args.input_dir, args.output_dir or args.input_dir), indent=2, sort_keys=True))
