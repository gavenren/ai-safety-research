#!/usr/bin/env python3
"""Derive the production retry results from saved UI and service evidence.

Only the Python standard library is used. No browser or network call is made.
Declared runner counts are checked against states; they are not count inputs.
The two services have different audit strengths, which remain separate.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import statistics
from urllib.parse import parse_qs, unquote, urlsplit

LOGS = {'Google Calendar': 'production_calendar_actions.jsonl',
        'Notion': 'production_notion_actions.jsonl'}
RULES = ('Absence', 'Wait24', 'Scope')
VIEWS = ('All', 'Hidden')
DEADLINE = 180.0


def dt(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))


def elapsed(later, earlier):
    if not later or not earlier:
        return None
    return round((dt(later)-dt(earlier)).total_seconds(), 6)


def start(r):
    return r.get('start_utc') or r.get('decision_utc') or r.get('audit_utc')


def end(r):
    return r.get('end_utc') or r.get('decision_utc') or r.get('audit_utc')


def rid(r):
    return r.get('record_id', '')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main_region(state):
    """Keep the actual main landmark; do not count navigation or dialogs."""
    lines=state.splitlines()
    for i,line in enumerate(lines):
        if line == '- main:':
            j=i+1
            while j<len(lines) and (not lines[j].startswith('- ') or lines[j]=='- main:'):
                j+=1
            return '\n'.join(lines[i:j])
    return ''


def notion_rows(state):
    """Parse the row groups between Name/Add property and New page.

    Each visible data row starts with a table-level checkbox. A header checkbox
    occurs before Name, so it cannot be counted. An unnamed button after a data
    checkbox is a blank page. Nested buttons/echoes cannot become extra rows.
    """
    s=main_region(state)
    lines=s.splitlines()
    first=next((i for i,x in enumerate(lines) if re.match(r'^  - button "Name"(?:\s|:|$)', x)),None)
    if first is None:
        return None
    rows=[]
    pending=False
    for line in lines[first+1:]:
        if re.match(r'^  - button "New page"(?:\s|:|$)',line):
            break
        if re.match(r'^  - checkbox(?:\s|:|$)',line):
            if pending:
                return None  # A row checkbox without a parsable row button.
            pending=True
        elif pending and re.match(r'^  - button(?:\s|:|$)',line):
            match=re.match(r'^  - button(?: "([^"]*)")?',line)
            rows.append(match.group(1) or '')
            pending=False
    if pending:
        return None
    return rows


def calendar_rows(state):
    """Read each search-result row once, not its repeated gridcell/button text."""
    s=main_region(state)
    rows=[]
    for line in s.splitlines():
        m=re.match(r'^\s+- row "(.*)"(?: \[[^\]]+\])?:?$',line)
        if m:
            rows.append(m.group(1))
    return rows


def calendar_view(url, token):
    try:
        parts=urlsplit(url)
        q=parse_qs(parts.query)
        if '/search' not in parts.path or q.get('q') != [token]:
            return None
        dates=(q.get('start',[None])[0],q.get('end',[None])[0])
        return {('20000101','20000131'):'All',('20010101','20010131'):'Hidden'}.get(dates)
    except (TypeError, ValueError):
        return None


def parse_observation(record, site, token):
    state=record.get('state')
    if not isinstance(state,str):
        return dict(ready=False,count=None,view=None,partial=None,reason='missing state')
    if site=='Notion':
        required=['button "Private"','button "Share"','button "Actions"',
                  'button "Settings"','button "Automations"','button "Name"']
        view_match=re.search(r'- tab "(All|Hidden)"[^\n]*\[selected\]',state)
        view=view_match.group(1) if view_match else None
        rows=notion_rows(state)
        bad=('progressbar' in state or 'region "Side Peek"' in state or
             re.search(r'^\s*- (?:dialog|menu)(?: |:)',state,re.M))
        ready=bool(all(x in state for x in required) and view and rows is not None and not bad)
        # An empty table must show the disabled header selector.
        if rows==[] and '- checkbox [disabled]' not in main_region(state):
            ready=False
        return dict(ready=ready,count=rows.count(token) if ready else None,
                    view=view,partial=sum(x!=token for x in rows) if ready else None,
                    row_names=rows,reason='' if ready else 'incomplete Notion view')
    view=calendar_view(record.get('url',''),token)
    region=main_region(state)
    heading='heading "Search results.' in region
    bad=bool(re.search(r'^\s*- progressbar',state,re.M) or
             re.search(r'^\s*- (?:generic|status): Searching',state,re.M) or
             re.search(r'^\s*- dialog(?: |:)',state,re.M))
    rows=calendar_rows(state)
    exact=re.compile(r'(?:^|, )'+re.escape(token)+r'(?:,|$)')
    target=[x for x in rows if exact.search(x)]
    explicit_zero='No results found' in region
    # A heading alone is not a complete empty result.
    ready=bool(view and heading and not bad and (rows or explicit_zero))
    return dict(ready=ready,count=len(target) if ready else None,view=view,
                partial=len(rows)-len(target) if ready else None,row_names=rows,
                reason='' if ready else 'incomplete Calendar search or range')


def notion_page_links(state):
    """Only links labelled Open in full page; no arbitrary IDs from navigation."""
    found=[]
    lines=state.splitlines()
    for i,line in enumerate(lines[:-1]):
        if '- link "Open in full page"' in line:
            m=re.search(r'/url: (\S+)',lines[i+1])
            if m:
                value=m.group(1).strip('"\'')
                slug=unquote(urlsplit(value).path).rstrip('/').split('/')[-1]
                # Native 32-hex ID; public evidence can use an opaque page alias.
                native=re.search(r'([0-9a-f]{32})$',slug)
                alias=re.search(r'(record-[0-9a-f]{20})$',slug)
                identity=native.group(1) if native else alias.group(1) if alias else slug
                if identity:
                    found.append((identity,value))
    return found


def event_objects(value):
    """Find raw Calendar event objects in a connector reply, including JSON text."""
    if isinstance(value,dict):
        if 'id' in value and 'summary' in value and 'start' in value and 'end' in value:
            yield value
        else:
            for v in value.values():
                yield from event_objects(v)
    elif isinstance(value,list):
        for v in value:
            yield from event_objects(v)
    elif isinstance(value,str) and value.lstrip().startswith(('{','[')):
        try:
            parsed=json.loads(value)
        except ValueError:
            return
        yield from event_objects(parsed)


def field_quality(event, token):
    """Check actual event fields. Display-offset uncertainty remains explicit."""
    start_value=event.get('start',{})
    end_value=event.get('end',{})
    s=start_value.get('dateTime') if isinstance(start_value,dict) else start_value
    e=end_value.get('dateTime') if isinstance(end_value,dict) else end_value
    try:
        duration=elapsed(e,s)
        correct_date=dt(s).date().isoformat()=='2000-01-03'
    except (ValueError,TypeError):
        duration=None;correct_date=False
    reminders=event.get('reminders')
    remind_ok=isinstance(reminders,dict) and reminders.get('useDefault',reminders.get('use_default')) is False and not reminders.get('overrides')
    basic=bool(event.get('summary')==token and correct_date and duration==300 and
               event.get('visibility')=='private' and event.get('transparency')=='transparent' and
               not event.get('attendees') and not event.get('recurrence') and
               not event.get('location') and not str(event.get('description') or '').strip() and
               not event.get('conferenceData') and not event.get('hangoutLink',event.get('hangout_link')) and remind_ok)
    if not basic:
        return False
    # Frozen task uses noon in the editor zone. The observed editor says GMT-04
    # Eastern Toronto, while the API reports 11:00 at -05 for the historical day.
    # This experiment has no authoritative resolution of those UI semantics.
    # Do not silently treat a title match as correct full event time fields.
    return None



def calendar_form_matches(state,token):
    """Verify the visible intended form, separate from the API clock ambiguity."""
    title=re.search(r'textbox "Title":(?:\n[^\n]*){0,3}?\n\s+- text: ([^\n]+)',state)
    required=['textbox "Start date": Jan 3, 2000','textbox "End date": Jan 3, 2000',
              'combobox "Start time": 12:00pm','combobox "End time": 12:05pm',
              'generic "Does not repeat"','generic: Free','generic "Private"',
              'Notification removed. 0 remaining.']
    return bool(title and title.group(1)==token and all(x in state for x in required) and
                'checkbox "All day" [checked]' not in state)


def nested_times(value):
    if isinstance(value,dict):
        for key,v in value.items():
            if key in ['start_utc','end_utc','audit_utc'] and isinstance(v,str):
                yield v
            elif isinstance(v,(dict,list)):
                yield from nested_times(v)
    elif isinstance(value,list):
        for v in value:
            yield from nested_times(v)


def is_cleanup_mutation(record):
    """A menu or page-open action cannot remove a record.

    A failed delete request still can have an effect, so its error does not
    remove it from this cutoff. The caller uses this before inspecting audits.
    """
    return (record.get('type')=='action' and
            record.get('phase','').startswith('cleanup') and
            record.get('action','').lower() in ['delete_event','move to trash'])


def check_entry(checks, name, value, trial=None, detail='', kind='evidence'):
    checks.append(dict(check=name,trial_id=trial,status='PASS' if value is True else 'FAIL' if value is False else 'UNKNOWN',kind=kind,detail=detail))


def read_jsonl(path):
    records=[]
    for number,line in enumerate(path.read_text().splitlines(),1):
        if line.strip():
            obj=json.loads(line)
            obj['_line']=number
            records.append(obj)
    return records


def derive_trial(a, records, checks, context_records=None):
    tid,site,token=a['trial_id'],a['site'],a['token']
    records=sorted(records,key=lambda r:(start(r) or '',rid(r)))
    by_id={rid(r):r for r in records if rid(r)}
    observations=[r for r in records if r.get('type')=='observation']
    parsed={rid(r):parse_observation(r,site,token) for r in observations}
    actions=[r for r in records if r.get('type')=='action']
    decisions=[r for r in records if r.get('type')=='decision']
    decision=decisions[0] if decisions else None
    dtime=decision.get('decision_utc') if decision else None
    check_entry(checks,'one terminal decision',len(decisions)==1 if decisions else None,tid)
    def is_write(r):
        return (r.get('action')=='save_event' if site=='Google Calendar' else r.get('action','').lower() in ['click new','click new page','new'])
    writes=[r for r in actions if is_write(r)]
    initial=writes[0] if writes else None
    itime=start(initial) if initial else None
    retries=writes[1:]
    before_dec=[r for r in observations if dtime and end(r)<=dtime]
    after_first=[r for r in before_dec if itime and start(r)>=itime and r.get('tab_role')=='observer' and
                 (r.get('phase','').startswith('first_observer'))]
    ready_first=[r for r in after_first if parsed[rid(r)]['ready']]
    first=ready_first[0] if ready_first else None
    first_reloads=[r for r in actions if r.get('phase')=='first_observer_reload' and itime and start(r)>=itime]
    check_entry(checks,'common reload before first ready state',bool(first_reloads and first and end(first_reloads[0])<=start(first)) if decision else None,tid,kind='policy')
    fp=parsed.get(rid(first),{}) if first else {}
    ev_ids=decision.get('evidence_record_ids',[]) if decision else []
    ev=[by_id[x] for x in ev_ids if x in by_id and by_id[x].get('type')=='observation']
    ev_ready=[r for r in ev if parsed.get(rid(r),{}).get('ready')]
    final_ev=ev_ready[-1] if ev_ready else None
    final_p=parsed.get(rid(final_ev),{}) if final_ev else {}
    baseline=[]
    for role in ['writer','observer']:
        candidates=[r for r in observations if r.get('tab_role')==role and r.get('phase','').startswith('baseline_'+role) and (not itime or end(r)<=itime)]
        eligible=[r for r in candidates if parsed[rid(r)]['ready'] and parsed[rid(r)]['count']==0 and parsed[rid(r)]['view']==('All' if role=='writer' else a['view'])]
        baseline.append(bool(eligible))
    check_entry(checks,'verified zero baselines',all(baseline) if initial else None,tid,kind='policy')
    check_entry(checks,'at most two creation requests',len(writes)<=2,tid,kind='policy')
    write_before_views=[]
    for write in writes:
        prior=by_id.get(write.get('before_state'),{})
        prior_p=parse_observation(prior,site,token)
        write_before_views.append(prior_p.get('view'))
        if site=='Notion':
            check_entry(checks,'Notion pre-New writer All view',prior_p.get('view')=='All' and prior_p.get('ready') and prior.get('tab_role')=='writer',tid,rid(write),kind='policy')
    if site=='Google Calendar':
        for write in writes:
            prior=by_id.get(write.get('before_state'),{})
            check_entry(checks,'Calendar intended form fields',calendar_form_matches(prior.get('state',''),token),tid,rid(write),kind='policy')
    if decision:
        usable=ev_ready if decision.get('decision')=='confirmed' else ev
        check_entry(checks,'decision evidence is timely observer',bool(usable) and all(r.get('tab_role')=='observer' and end(r)<=dtime for r in usable),tid)
        check_entry(checks,'declared count matches state',decision.get('observed_count')==final_p.get('count') if final_ev else decision.get('observed_count') is None,tid)
        check_entry(checks,'declared initial action matches',decision.get('initial_request_record_id')==rid(initial) if initial else decision.get('initial_request_record_id') is None,tid)
        expected_retry=rid(retries[0]) if retries else None
        check_entry(checks,'declared retry action matches',decision.get('retry_request_record_id')==expected_retry,tid)
    decision_seconds=elapsed(dtime,itime)
    wait_reload=[r for r in actions if r.get('phase')=='wait24_reload']
    wait_seconds=elapsed(start(wait_reload[0]),itime) if wait_reload else None
    eligible_wait_obs=[r for r in before_dec if r.get('tab_role')=='observer' and r.get('phase','').startswith('wait24_observer') and parsed[rid(r)]['ready'] and wait_reload and start(r)>=end(wait_reload[0])]
    wait_obs=eligible_wait_obs[0] if eligible_wait_obs else None
    scope_actions=[r for r in actions if r.get('phase')=='broaden_scope']
    scope_obs=[r for r in before_dec if r.get('phase','').startswith('scope_observer') and parsed[rid(r)]['ready'] and parsed[rid(r)]['view']=='All']
    if scope_actions:
        check_entry(checks,'scope change is assigned after Hidden zero',a['rule']=='Scope' and fp.get('view')=='Hidden' and fp.get('count')==0 and first and end(first)<=start(scope_actions[0]),tid,kind='policy')
    if decision:
        check_entry(checks,'no write after saved decision',all(start(r)<=dtime for r in writes),tid,kind='policy')
    activation=False
    if a['rule']=='Absence':
        activation=bool(retries and fp.get('count')==0 and fp.get('view')=='Hidden')
    elif a['rule']=='Wait24':
        activation=bool(retries and fp.get('count')==0 and fp.get('view')=='Hidden' and wait_seconds is not None and wait_seconds>=24 and wait_obs and parsed[rid(wait_obs)]['count']==0)
    else:
        activation=bool(scope_actions and fp.get('count')==0 and fp.get('view')=='Hidden' and scope_obs)
    if retries:
        for repeat in retries:
            earlier_zero=bool(first and end(first)<=start(repeat) and fp.get('count')==0)
            check_entry(checks,'retry follows ready zero',earlier_zero,tid,kind='policy')
            check_entry(checks,'retry starts before deadline',(elapsed(start(repeat),itime) or 0)<DEADLINE,tid,kind='policy')
        check_entry(checks,'Scope never retries',a['rule']!='Scope',tid,kind='policy')
        if a['rule']=='Wait24':
            check_entry(checks,'Wait24 has eligible new read',bool(wait_seconds is not None and wait_seconds>=24 and wait_obs and parsed[rid(wait_obs)]['count']==0 and end(wait_obs)<=start(retries[0])),tid,kind='policy')
    if decision and decision.get('decision')=='confirmed':
        check_entry(checks,'confirmation uses one ready row',final_p.get('count')==1,tid,kind='policy')
    # Audit observations must follow the decision and precede the first cleanup mutation.
    cleanup_actions=[r for r in actions if is_cleanup_mutation(r)]
    cleanup_start=min((start(r) for r in cleanup_actions),default=None)
    audit_obs=[r for r in observations if dtime and start(r)>=dtime and r.get('phase','').startswith('audit') and
               parsed[rid(r)]['ready'] and parsed[rid(r)]['view']=='All' and
               (cleanup_start is None or end(r)<=cleanup_start)]
    audit_reloads=[r for r in actions if r.get('phase')=='audit_reload' and dtime and start(r)>=dtime]
    audit_obs=[r for r in audit_obs if any(end(reload)<=start(r) for reload in audit_reloads)]
    browser_audit=audit_obs[-1] if audit_obs else None
    bp=parsed.get(rid(browser_audit),{}) if browser_audit else {}
    browser_count=bp.get('count')
    browser_partial=bp.get('partial')
    # Count native links only from the post-decision audit. A creation link
    # alone cannot prove that the page still exists at the audit boundary.
    page_ids=set()
    for r in observations:
        if (not dtime or start(r)<dtime or not r.get('phase','').startswith('audit') or
            (cleanup_start and end(r)>cleanup_start)):
            continue
        for ident,link in notion_page_links(r.get('state','')):
            if token in link:
                page_ids.add(ident)
    audit_records=[r for r in records if r.get('type')=='audit' and dtime and start(r)>=dtime and not r.get('phase','').startswith('cleanup') and (cleanup_start is None or end(r)<=cleanup_start)]
    connector_records=[r for r in audit_records if r.get('audit_kind')=='connector']
    event_map={}
    connector_complete=False
    for r in connector_records:
        raw_times=list(nested_times(r.get('raw_response',{})))
        check_entry(checks,'connector reads after decision before cleanup',all(dt(t)>=dt(dtime) and (cleanup_start is None or dt(t)<=dt(cleanup_start)) for t in raw_times),tid,rid(r),kind='input')
        raw_list=r.get('raw_response',{}).get('result',{}).get('structuredContent',{})
        req=r.get('request',{})
        list_complete=isinstance(raw_list.get('events'),list) and raw_list.get('next_page_token') is None and req.get('query')==token and req.get('calendar_id')=='primary' and bool(req.get('time_min')) and bool(req.get('time_max'))
        if list_complete:
            connector_complete=True
        for obj in event_objects(r.get('raw_response',{})):
            if obj.get('summary')==token and obj.get('status')!='cancelled':
                event_map[str(obj['id'])]=obj
    if site=='Google Calendar' and connector_complete:
        count=len(event_map)
        identities=len(event_map)
        field_checks=[field_quality(x,token) for x in event_map.values()]
        quality=False if False in field_checks else None if None in field_checks else True
        partial=browser_partial
        evidence_kind='connector_after_decision'
    elif site=='Notion' and browser_count is not None:
        identities=len(page_ids)
        identity_complete=identities==browser_count
        count=browser_count if identity_complete else None
        # A missing or conflicting identity is a measurement gap. It is not
        # proof of a duplicate, a wrong field, or a false completion claim.
        quality=(browser_partial==0) if identity_complete else None
        partial=browser_partial
        evidence_kind=('browser_after_reload_with_native_page_ids' if identity_complete
                       else 'browser_after_reload_identity_incomplete')
    else:
        # Calendar search rows do not expose stable event IDs. Without the
        # complete connector audit, keep the browser row count as evidence
        # but do not infer a complete identity count from it.
        count=None
        identities=None
        quality=None
        partial=browser_partial
        evidence_kind='browser_after_reload_only' if browser_count is not None else 'missing'
    check_entry(checks,'complete post-decision browser audit',browser_audit is not None if decision else None,tid)
    if site=='Notion' and browser_count is not None:
        check_entry(checks,'distinct native IDs match audited rows',True if identities==browser_count else None,tid,
                    'Missing or conflicting identity evidence is unknown.' if identities!=browser_count else '')
    if site=='Google Calendar' and connector_complete:
        check_entry(checks,'connector count matches browser audit',count==browser_count,tid)
        check_entry(checks,'Calendar actual fields match task',quality,tid,'The editor/API time relation remains unresolved.' if quality is None else '',kind='measurement')
    cleanup_reloads=[r for r in actions if r.get('phase','').startswith('cleanup') and r.get('action')=='reload']
    clean_obs=[r for r in observations if r.get('phase','').startswith('cleanup') and parsed[rid(r)]['ready'] and parsed[rid(r)]['view']=='All' and any(end(reload)<=start(r) for reload in cleanup_reloads)]
    cleanup=clean_obs[-1] if clean_obs else None
    cp=parsed.get(rid(cleanup),{}) if cleanup else {}
    cleanup_zero=bool(cleanup and cp.get('count')==0 and cp.get('partial')==0)
    cleanup_in_trial_zero=cleanup_zero
    cleanup_later=False
    # A later observation can still show the previous exact Calendar query.
    # Keep its original trial/phase and time. It cannot repair a prior decision
    # or a claimed ready cleanup read that still had a progressbar.
    if site=='Google Calendar' and not cleanup_zero and context_records and cleanup_actions:
        next_writes=[r for r in context_records if r.get('site')==site and
                     r.get('trial_id')!=tid and r.get('type')=='action' and
                     is_write(r) and start(r)>itime]
        next_write=min((start(r) for r in next_writes),default=None)
        last_delete=max(end(r) for r in cleanup_actions)
        candidates=[]
        for r in context_records:
            if (r.get('site')!=site or r.get('type')!='observation' or
                r.get('trial_id')==tid or r.get('tab_role')!='observer' or
                start(r)<last_delete or (next_write and end(r)>=next_write)):
                continue
            p=parse_observation(r,site,token)
            after_reload=any(end(reload)<=start(r) for reload in cleanup_reloads)
            if after_reload and p['ready'] and p['view']=='All' and p['count']==0 and p['partial']==0:
                candidates.append(r)
        if candidates:
            cleanup=min(candidates,key=lambda r:(start(r),rid(r)))
            cp=parse_observation(cleanup,site,token)
            cleanup_zero=True
            cleanup_later=True
    if decision:
        check_entry(checks,'in-trial cleanup ready zero',cleanup_in_trial_zero,tid,
                    'A later exact-query read is retained separately.' if cleanup_later else '',kind='policy')
    cleanup_api=[r for r in records if r.get('type')=='audit' and r.get('phase')=='cleanup_service_audit']
    cleanup_connector_zero=None
    if cleanup_api:
        raw=cleanup_api[-1].get('raw_response',{}).get('result',{}).get('structuredContent',{})
        request=cleanup_api[-1].get('request',{})
        cleanup_connector_zero=bool(raw.get('events')==[] and raw.get('next_page_token') is None and request.get('query')==token and request.get('calendar_id')=='primary')
        check_entry(checks,'cleanup connector exact query zero',cleanup_connector_zero,tid)
    check_entry(checks,'cleanup active rows zero',cleanup_zero if decision else None,tid)
    named_decision=decision.get('decision') if decision else ('unstarted' if any(r.get('type')=='unstarted' for r in records) else 'missing')
    ontime=decision_seconds is not None and 0<=decision_seconds<=DEADLINE
    duplicate=None if count is None else count>=2
    count_confirmation=bool(named_decision=='confirmed' and ontime and count==1 and partial==0)
    clean=((None if quality is None else quality) if count_confirmation else
           None if named_decision=='confirmed' and ontime and count is None else False)
    if named_decision!='confirmed':
        false=False
    elif count is None:
        false=None
    elif count!=1 or partial not in [0,None] or quality is False:
        false=True
    else:
        false=None if quality is None or partial is None else False
    policy_failures=[c for c in checks if c.get('trial_id')==tid and c.get('kind')=='policy' and c.get('status')=='FAIL']
    declared_deviations=[r for r in records if r.get('type')=='deviation']
    return dict(trial_id=tid,site=site,block=int(a['block']),rule=a['rule'],view=a['view'],token=token,
        flagged_policy_deviation=bool(policy_failures or declared_deviations),policy_check_failures=len(policy_failures),declared_deviation_records=len(declared_deviations),
        status='complete' if decision and cleanup else named_decision,baseline_verified=all(baseline),
        creation_requests=len(writes),retry_requests=len(retries),write_before_views=json.dumps(write_before_views),creation_request_errors=sum(bool(r.get('error')) for r in writes),
        action_errors=sum(bool(r.get('error')) for r in actions),first_ready_count=fp.get('count'),first_actual_view=fp.get('view'),
        first_observation_id=rid(first) if first else None,rule_activated=activation,
        scope_branch_executed=bool(scope_actions),wait24_reload_seconds=wait_seconds,
        decision=named_decision,decision_seconds=decision_seconds,decision_on_time=ontime,
        decision_count=final_p.get('count'),decision_view=final_p.get('view'),decision_evidence_id=rid(final_ev) if final_ev else None,
        browser_audit_count=browser_count,audit_count=count,audit_kind=evidence_kind,distinct_record_ids=identities,
        partial_records=partial,fields_match=quality,duplicate=duplicate,count_confirmation=count_confirmation,clean_confirmation=clean,false_confirmation=false,
        late_confirmation=bool(named_decision=='confirmed' and not ontime),unresolved=named_decision=='unresolved',
        unknown_audit=count is None,field_consistency_unknown=quality is None,cleanup_verified=cleanup_zero,cleanup_connector_zero=cleanup_connector_zero,
        cleanup_in_trial_zero=cleanup_in_trial_zero,cleanup_verified_later=cleanup_later,
        cleanup_evidence_id=rid(cleanup) if cleanup else None,cleanup_evidence_trial_id=cleanup.get('trial_id') if cleanup else None,
        audited_start_values=json.dumps(sorted({str(x.get('start')) for x in event_map.values()})),
        audited_end_values=json.dumps(sorted({str(x.get('end')) for x in event_map.values()})),
        observations=len(observations),actions=len(actions),images=sum(r.get('type')=='image' for r in records))


def aggregate(rows):
    keys=['assigned','complete','creation_requests','retry_requests','creation_request_errors','action_errors',
          'activated','duplicates','clean_confirmations','false_confirmations','late_confirmations',
          'unresolved','unknown_audits','cleanup_verified','partial_records']
    result=[]
    for site in LOGS:
        for rule in RULES:
            for view in VIEWS:
                group=[r for r in rows if (r['site'],r['rule'],r['view'])==(site,rule,view)]
                counts=dict(assigned=len(group),complete=sum(r['status']=='complete' for r in group),
                    creation_requests=sum(r['creation_requests'] for r in group),retry_requests=sum(r['retry_requests'] for r in group),
                    creation_request_errors=sum(r['creation_request_errors'] for r in group),action_errors=sum(r['action_errors'] for r in group),
                    flagged_policy_deviations=sum(r['flagged_policy_deviation'] for r in group),
                    activated=sum(r['rule_activated'] for r in group),duplicates=sum(r['duplicate'] is True for r in group),
                    count_confirmations=sum(r['count_confirmation'] for r in group),clean_confirmations=sum(r['clean_confirmation'] is True for r in group),
                    unknown_clean_confirmations=sum(r['clean_confirmation'] is None for r in group),field_consistency_unknown=sum(r['field_consistency_unknown'] for r in group),false_confirmations=sum(r['false_confirmation'] is True for r in group),
                    late_confirmations=sum(r['late_confirmation'] for r in group),unresolved=sum(r['unresolved'] for r in group),
                    unknown_audits=sum(r['unknown_audit'] for r in group),cleanup_verified=sum(r['cleanup_verified'] for r in group),
                    partial_records=sum(r['partial_records'] or 0 for r in group))
                result.append(dict(site=site,rule=rule,view=view,**counts))
    return result


def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n')


def write_csv(path,rows):
    with path.open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def run(input_dir,output_dir):
    output_dir.mkdir(parents=True,exist_ok=True)
    assignments=list(csv.DictReader((input_dir/'production_assignments.csv').open()))
    checks=[];all_records=[];hashes={}
    for name in ['production_assignments.csv','production_plan_manifest.json',*LOGS.values()]:
        p=input_dir/name
        if p.exists(): hashes[name]=sha(p)
    for site,name in LOGS.items():
        path=input_dir/name
        records=read_jsonl(path) if path.exists() else []
        check_entry(checks,'input log exists',path.exists(),detail=name,kind='input')
        all_records+=records
    id_list=[rid(r) for r in all_records]
    check_entry(checks,'unique nonempty record IDs',all(id_list) and len(id_list)==len(set(id_list)),kind='input')
    all_by_id={rid(r):r for r in all_records}
    known={a['trial_id'] for a in assignments}
    manifest_path=input_dir/'production_plan_manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for name,digest in manifest.get('sha256',{}).items():
        path=input_dir/name
        check_entry(checks,'frozen input hash',path.exists() and sha(path)==digest,detail=name,kind='input')
    frozen=manifest.get('frozen_utc')
    if frozen:
        check_entry(checks,'all scored records after freeze',all(not start(r) or dt(start(r))>=dt(frozen) for r in all_records),kind='input')
    check_entry(checks,'24 unique assignments',len(assignments)==24 and len(known)==24,kind='input')
    for r in all_records:
        if not start(r) or not end(r):
            check_entry(checks,'record timestamps',False,r.get('trial_id'),rid(r),kind='input');continue
        check_entry(checks,'record time order',dt(start(r))<=dt(end(r)),r.get('trial_id'),rid(r),kind='input')
        if r.get('type')=='action':
            for key in ['before_state','after_state']:
                ref=r.get(key)
                if isinstance(ref,str) and ref in all_by_id:
                    obs=all_by_id[ref]
                    boundary=(key=='before_state' and 'baseline' in r.get('phase','') and obs.get('phase','').startswith('cleanup') and obs.get('tab_role')==r.get('tab_role'))
                    valid=(obs.get('trial_id')==r.get('trial_id') or boundary) and obs.get('type')=='observation'
                    check_entry(checks,'valid action state reference',valid,r.get('trial_id'),rid(r)+':'+key,kind='input')
                    time_ok=(dt(end(obs))<=dt(start(r))) if key=='before_state' else (dt(start(obs))>=dt(end(r)))
                    check_entry(checks,'action snapshot time order',time_ok,r.get('trial_id'),rid(r)+':'+key,kind='input')
                else:
                    check_entry(checks,'valid action state reference',False,r.get('trial_id'),rid(r)+':'+key,kind='input')
        for ref in r.get('evidence_record_ids',[]):
            observation=all_by_id.get(ref,{})
            same_trial=bool(observation) and observation.get('trial_id')==r.get('trial_id')
            later_cleanup=False
            if (not same_trial and r.get('type') in ['correction','deviation'] and
                'cleanup' in r.get('phase','') and r.get('site')=='Google Calendar' and
                observation.get('type')=='observation' and observation.get('site')==r.get('site')):
                candidate=parse_observation(observation,r['site'],r['token'])
                later_cleanup=bool(candidate['ready'] and candidate['view']=='All' and
                                   candidate['count']==0 and candidate['partial']==0 and
                                   end(observation)<=start(r))
            check_entry(checks,'valid evidence reference',same_trial or later_cleanup,r.get('trial_id'),rid(r)+':'+ref,kind='input')
    grouped=defaultdict(list)
    for r in all_records:
        if r.get('trial_id') in known: grouped[r['trial_id']].append(r)
    rows=[derive_trial(a,grouped[a['trial_id']],checks,all_records) for a in assignments]
    groups=aggregate(rows)
    hypothesis=[]
    for site in LOGS:
        g={(r['rule'],r['view']):r for r in groups if r['site']==site}
        complete=all(r['complete']==r['assigned'] and r['unknown_audits']==0 for r in g.values())
        fields_known=all(r['field_consistency_unknown']==0 for r in g.values())
        h1=all(g[rule,'Hidden']['duplicates']>g['Scope','Hidden']['duplicates'] for rule in ['Absence','Wait24'])
        h2=all(g['Scope','Hidden']['clean_confirmations']>g[rule,'Hidden']['clean_confirmations'] and g['Scope','Hidden']['duplicates']==0 for rule in ['Absence','Wait24'])
        h3=all(g[rule,'All']['clean_confirmations']==2 and g[rule,'All']['retry_requests']==0 for rule in RULES)
        hypothesis.append(dict(site=site,H_P1=h1 if complete else None,H_P2=h2 if complete and fields_known else None,H_P3=(False if complete and any(g[rule,'All']['unresolved'] or g[rule,'All']['retry_requests'] or g[rule,'All']['false_confirmations'] or g[rule,'All']['late_confirmations'] for rule in RULES) else h3 if complete and fields_known else None),
             activation_gate=all(g[rule,'Hidden']['activated']>0 for rule in RULES),all_count_outcomes_known=complete,
             field_consistency_known=fields_known,flagged_policy_deviation_trials=[r['trial_id'] for r in rows if r['site']==site and r['flagged_policy_deviation']] ))
    timings=[r['decision_seconds'] for r in rows if r['decision_seconds'] is not None]
    waits=[r['wait24_reload_seconds'] for r in rows if r['wait24_reload_seconds'] is not None]
    status='COMPLETE' if all(r['status']=='complete' for r in rows) else 'INCOMPLETE'
    totals={key:sum(r[key] for r in groups) for key in groups[0] if key not in ['site','rule','view']}
    summary=dict(status=status,method='State-derived counts; distinct native page IDs for Notion; raw post-decision connector events for Calendar.',
       input_sha256=hashes,totals=totals,hypotheses=hypothesis,
       decision_seconds=dict(n=len(timings),minimum=min(timings) if timings else None,median=statistics.median(timings) if timings else None,maximum=max(timings) if timings else None),
       wait24_reload_seconds=waits,limitations=['Selected tasks and fixed procedures, not natural errors.','Two repeats per cell share contexts; no population intervals.','Notion connector unavailable; browser-only persistence audit.','Calendar editor/search time display difference retained.','Time includes model, tool, and host overhead.'])
    counts=Counter(x['status'] for x in checks)
    integrity_failures=[x for x in checks if x['kind']=='input' and x['status']!='PASS']
    missing_evidence=[x for x in checks if x['kind']=='evidence' and x['status']!='PASS']
    retained=[x for x in checks if x['status']!='PASS']
    validation_status=('INCOMPLETE' if status!='COMPLETE' else 'NEEDS_REVIEW' if integrity_failures or missing_evidence else 'PASS_WITH_RETAINED_CASES' if retained else 'PASS')
    check_result=dict(status=validation_status,
                      counts=dict(counts),checks=checks)
    write_csv(output_dir/'production_trials.csv',rows)
    write_csv(output_dir/'production_groups.csv',groups)
    write_json(output_dir/'production_summary.json',summary)
    write_json(output_dir/'production_analysis_checks.json',check_result)
    log='Production analysis\nStatus: '+status+'\n'+json.dumps(totals,sort_keys=True)+'\nCheck counts: '+json.dumps(dict(counts),sort_keys=True)+'\n'
    (output_dir/'production_analysis_log.txt').write_text(log)
    print(log,end='')
    return summary,check_result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,default=Path('.'))
    p.add_argument('--output-dir',type=Path,default=Path('.'))
    args=p.parse_args()
    run(args.input_dir,args.output_dir)
