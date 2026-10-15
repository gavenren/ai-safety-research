#!/usr/bin/env python3
"""Independent offline replay from public UI states and connector response data.

This file does not import the main analyzer or use its result files. It derives
counts from complete UI states. Native visible links or saved connector responses
establish record identity. It uses the frozen assignments and 180-second rule.
"""
import csv, hashlib, json, re, random
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

P=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def time(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def delta(a,b): return round((time(a)-time(b)).total_seconds(),3)
def state_read(r, site, token):
    s=r.get('state',''); u=r.get('url','')
    if not isinstance(s,str): return None
    if site=='Notion':
        m=re.search(r'^    - tab "(All|Hidden)"(?: \[active\])? \[selected\]',s,re.M)
        view=m.group(1) if m else None
        required=['button "Private"','button "Share"','button "Actions"','button "Settings"','button "Automations"','button "Name"','- main:']
        if not view or not all(t in s for t in required) or 'progressbar' in s or 'region "Side Peek"' in s or re.search(r'^- (?:menu|dialog):',s,re.M): return None
        main=s.split('- main:',1)[1].split('\n- region',1)[0]
        n=len(re.findall(r'^  - button "'+re.escape(token)+r'"(?::| \[active\]:)',main,re.M))
        checkboxes=len(re.findall(r'^  - checkbox(?:\s|$)',main,re.M))
        rowtotal=max(0,checkboxes-1)
        if n>rowtotal or (n==0 and rowtotal==0 and 'checkbox [disabled]' not in main): return None
        return {'count':n,'view':view,'other_rows':rowtotal-n,'record_id':r['record_id']}
    q=parse_qs(urlparse(u).query)
    if q.get('q')!=[token]: return None
    dates=(q.get('start'),q.get('end'))
    view='All' if dates==(['20000101'],['20000131']) else 'Hidden' if dates==(['20010101'],['20010131']) else None
    if not view or 'heading "Search results.' not in s or 'progressbar' in s or 'Searching' in s: return None
    rows=re.findall(r'^      - row "(.*)":',s,re.M)
    n=sum(token in t for t in rows)
    if not rows and 'No results found' not in s: return None
    return {'count':n,'view':view,'other_rows':len(rows)-n,'record_id':r['record_id']}

def first_ready(records,site,token,prefix,after=None,before=None,view=None):
    for r in sorted(records,key=lambda r:r.get('end_utc','')):
        if r.get('type')!='observation' or r.get('tab_role')!='observer' or not r.get('phase','').startswith(prefix): continue
        if after and time(r['start_utc'])<time(after):continue
        if before and time(r['end_utc'])>time(before):continue
        x=state_read(r,site,token)
        if x and (view is None or x['view']==view): return r,x
    return None,None

def utc_values(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ('start_utc','end_utc') and isinstance(v,str):yield v
            else:yield from utc_values(v)
    elif isinstance(x,list):
        for v in x:yield from utc_values(v)

def raw_events(r):
    return r.get('raw_response',{}).get('result',{}).get('structuredContent',{})

def run():
    assignments=list(csv.DictReader((P/'production_assignments.csv').open()))
    sources=['production_calendar_actions.jsonl','production_notion_actions.jsonl']
    allrows=[]
    for f in sources: allrows.extend(json.loads(l) for l in (P/f).read_text().splitlines())
    rows=[]
    for a in assignments:
        tid,site,token=a['trial_id'],a['site'],a['token']; rs=[r for r in allrows if r.get('trial_id')==tid]; byid={r['record_id']:r for r in rs}
        acts=sorted([r for r in rs if r.get('type')=='action'],key=lambda r:r['start_utc'])
        creates=[r for r in acts if r.get('action')==('click New' if site=='Notion' else 'save_event')]
        ds=[r for r in rs if r.get('type')=='decision']
        out={'trial_id':tid,'site':site,'rule':a['rule'],'assigned_view':a['view'],'started':bool(creates),'decision_records':len(ds),'writes':len(creates)}
        if not creates or not ds: out['status']='incomplete';rows.append(out);continue
        d=ds[0];t0=creates[0]['start_utc'];dt=d['decision_utc']
        r0,first=first_ready(rs,site,token,'first_observer',after=t0,before=dt)
        decision_evidence=[(byid[x],state_read(byid[x],site,token)) for x in d.get('evidence_record_ids',[]) if x in byid]
        accepted=[(r,x) for r,x in decision_evidence if x and time(r['end_utc'])<=time(dt)]
        final=accepted[-1][1] if accepted else None
        reloads=[r for r in acts if r.get('phase')=='first_observer_reload']
        errors=[]
        if len(ds)!=1: errors.append('decision_count')
        if len(creates)>2:errors.append('more_than_one_retry')
        if not first or not final:errors.append('missing_ready_decision_input')
        if not reloads or (r0 and time(reloads[0]['end_utc'])>time(r0['start_utc'])):errors.append('missing_common_reload')
        wait_gate=None; branch=None
        if first:
            if first['count']>0:
                branch='one' if first['count']==1 else 'multiple'
                expected='confirmed' if first['count']==1 else 'unresolved'
                if len(creates)!=1 or d['decision']!=expected:errors.append('positive_first_rule')
            else:
                branch='zero'
                if a['rule']=='Scope':
                    if len(creates)!=1:errors.append('scope_retried_write')
                    if first['view']=='All':
                        if d['decision']!='unresolved':errors.append('scope_all_zero')
                    else:
                        scope=[r for r in acts if r.get('phase')=='scope_reload']
                        if not scope or not final or final['view']!='All':errors.append('scope_missing_cover')
                        if final and d['decision']!=('confirmed' if final['count']==1 else 'unresolved'):errors.append('scope_final_count')
                else:
                    branch_source=r0
                    if a['rule']=='Wait24':
                        gates=[r for r in acts if r.get('phase')=='wait24_reload']
                        wait_gate=delta(gates[0]['start_utc'],t0) if gates else None
                        rw,xw=first_ready(rs,site,token,'wait24_observer',after=gates[0]['end_utc'] if gates else t0,before=dt)
                        if not gates or wait_gate<24 or not xw:errors.append('wait24_gate')
                        branch_source=rw
                        if xw and xw['count']>0 and len(creates)>1:errors.append('wait24_retried_positive')
                    if len(creates)==2:
                        if branch_source and time(creates[1]['start_utc'])<time(branch_source['end_utc']):errors.append('retry_before_zero')
                        if delta(creates[1]['start_utc'],t0)>180:errors.append('late_retry')
                        reloadfinal=[r for r in acts if r.get('phase')=='final_observer_reload']
                        if not reloadfinal:errors.append('missing_final_reload')
                    if final and d['decision']!=('confirmed' if final['count']==1 else 'unresolved'):errors.append('retry_final_count')
        if final and (d.get('observed_count')!=final['count'] or d.get('actual_view')!=final['view']):errors.append('declared_decision_mismatch')
        cleanup_actions=[r for r in acts if r.get('phase','').startswith('cleanup') and (r.get('action')=='Move to Trash' or 'delete_event' in r.get('action',''))]
        cleanup_start=min((r['start_utc'] for r in cleanup_actions),default=None)
        audit_r,audit=first_ready(rs,site,token,'audit_observer',after=dt,before=cleanup_start,view='All')
        ids=set();identity_evidence=[];field_status=True;service_data=None
        if site=='Notion':
            for r in rs:
                if r.get('type')!='observation' or not r.get('phase','').startswith('audit') or time(r['start_utc'])<time(dt) or (cleanup_start and time(r['end_utc'])>time(cleanup_start)):continue
                s=r.get('state','')
                # Only the visible Open in full page link of this exact title.
                for m in re.finditer(r'link "Open in full page":\n\s+- /url: /p/'+re.escape(token)+r'-(record-[a-f0-9]{20})\?',s):
                    ids.add(m.group(1));identity_evidence.append(r['record_id'])
        else:
            service=[r for r in rs if r.get('type')=='audit' and r.get('phase')=='service_audit']
            if service:
                service_data=raw_events(service[0]);ev=service_data.get('events',[])
                req=service[0].get('request',{})
                if req.get('calendar_id')!='primary' or req.get('query')!=token or req.get('time_min')!='2000-01-01T00:00:00-05:00' or req.get('time_max')!='2000-02-01T00:00:00-05:00' or req.get('max_results')!=20:errors.append('audit_request_bounds')
                times=list(utc_values(service[0].get('raw_response',{})))
                if not times or any(time(t)<time(dt) or (cleanup_start and time(t)>time(cleanup_start)) for t in times):errors.append('service_audit_outside_interval')
                if service_data.get('next_page_token') is not None:errors.append('incomplete_service_audit')
                ids={e['id'] for e in ev if e.get('summary')==token and e.get('id')};identity_evidence=[service[0]['record_id']]
                details=[x.get('result',{}).get('structuredContent',{}) for x in service[0].get('raw_response',{}).get('read_events',[])]
                # Requested UI noon and saved service 11:00 do not establish time-field correctness.
                field_status=None
                if not details:errors.append('no_service_field_reads')
                for e in details:
                    if e.get('summary')!=token or e.get('recurrence') or e.get('attendees') or e.get('hangout_link') or e.get('transparency')!='transparent' or e.get('visibility')!='private' or e.get('location') or (e.get('description') or '').strip() or e.get('reminders')!={'use_default':False,'overrides':[]}:
                        field_status=False
        identity_agrees=bool(audit is not None and len(ids)==audit['count'])
        audit_count=audit['count'] if identity_agrees else None
        duplicate=(audit_count>=2) if audit_count is not None else None
        elapsed=delta(dt,t0);on_time=elapsed<=180
        count_confirm=(d['decision']=='confirmed' and on_time and audit_count==1) if audit_count is not None else None
        partials=audit['other_rows'] if audit else None
        clean=False if d['decision']!='confirmed' or not on_time or (audit_count is not None and audit_count!=1) or (partials is not None and partials>0) or field_status is False else True if audit_count==1 and partials==0 and field_status is True else None
        cleanup_reads=[]
        for r in rs:
            if r.get('type')=='observation' and r.get('phase','').startswith('cleanup') and cleanup_start and time(r['start_utc'])>=time(cleanup_start):
                x=state_read(r,site,token)
                if x and x['view']=='All':cleanup_reads.append((r,x))
        clean_r,clean_x=cleanup_reads[-1] if cleanup_reads else (None,None)
        cleanup_in_phase=bool(clean_x and clean_x['count']==0 and clean_x['other_rows']==0)
        cleanup=cleanup_in_phase;cleanup_later=None;cleanup_api_zero=None
        if site!='Notion':
            later_starts=[r['start_utc'] for r in allrows if r.get('site')==site and r.get('type')=='action' and r.get('action')=='save_event' and r.get('trial_id')!=tid and time(r['start_utc'])>time(dt)]
            next_write=min(later_starts) if later_starts else None
            if not cleanup and cleanup_start:
                for r in allrows:
                    if r.get('site')!=site or r.get('type')!='observation' or r.get('tab_role')!='observer' or r.get('phase')!='baseline_observer_before':continue
                    if time(r['start_utc'])<=time(cleanup_start) or (next_write and time(r['end_utc'])>=time(next_write)):continue
                    x=state_read(r,site,token)
                    if x and x['view']=='All' and x['count']==0 and x['other_rows']==0:
                        cleanup=True;cleanup_later=r['record_id'];break
        if site!='Notion':
            ca=[r for r in rs if r.get('type')=='audit' and r.get('phase')=='cleanup_service_audit']
            cleanup_api_zero=bool(ca and raw_events(ca[-1]).get('events')==[] and raw_events(ca[-1]).get('next_page_token') is None)
            cleanup=cleanup and cleanup_api_zero
        departures=[]
        for c in creates:
            b=byid.get(c.get('before_state'),{});af=byid.get(c.get('after_state'),{})
            bv=state_read(b,site,token)
            if site=='Notion':
                m=re.search(r'^    - tab "(All|Hidden)"(?: \[active\])? \[selected\]',af.get('state',''),re.M)
                if not bv or bv['view']!='All':departures.append(c['record_id']+': ready All writer not established immediately before create')
                if m and m.group(1)!='All':departures.append(c['record_id']+': Hidden selected in first state after create')
        false_confirm=False if d['decision']!='confirmed' else None if audit_count is None else True if audit_count!=1 or (partials is not None and partials>0) or field_status is False else None if field_status is None or partials is None else False
        out.update(status='complete',initial_request=creates[0]['record_id'],retry_request=creates[1]['record_id'] if len(creates)>1 else None,first=first,final=final,decision=d['decision'],decision_seconds=elapsed,on_time=on_time,branch=branch,wait24_reload_seconds=wait_gate,audit_ui=audit,audit_ids=sorted(ids),identity_evidence=identity_evidence,identity_agrees=identity_agrees,audit_count=audit_count,duplicate=duplicate,count_confirmation=count_confirm,task_fields_correct=field_status,clean_confirmation=clean,false_confirmation=false_confirm,partial_rows=partials,cleanup=cleanup,cleanup_in_named_phase=cleanup_in_phase,cleanup_later_cross_trial_evidence=cleanup_later,cleanup_connector_zero=cleanup_api_zero,cleanup_evidence=clean_r['record_id'] if clean_r else None,policy_errors=errors,writer_view_departures=departures)
        rows.append(out)
    result={'method':'Independent parse of public saved states and native IDs. No main analyzer import or result input. Unknown identity agreement or task fields remain null.','inputs':{f:sha(P/f) for f in sources+['production_assignments.csv','production_plan.md','production_plan_manifest.json','production_runner_instructions.md']},'assignments':len(rows),'complete':sum(r['status']=='complete' for r in rows),'trials':rows}
    freeze=json.loads((P/'production_plan_manifest.json').read_text())
    seed=random.Random(2026101507); expected=[]
    for site in ('Google Calendar','Notion'):
        for block in (1,2):
            cells=[('Absence','All'),('Absence','Hidden'),('Wait24','All'),('Wait24','Hidden'),('Scope','All'),('Scope','Hidden')]
            seed.shuffle(cells);expected.extend((site,rule,view) for rule,view in cells)
    unique_ids=[r['record_id'] for r in allrows]
    check_order={}
    for site in ('Google Calendar','Notion'):
        started=[r for r in rows if r['site']==site and r.get('initial_request')]
        actual=sorted(started,key=lambda x:time(next(r['start_utc'] for r in allrows if r['record_id']==x['initial_request'])))
        check_order[site]=[x['trial_id'] for x in actual]==[x['trial_id'] for x in started]
    result['integrity_checks']={'assignment_order_from_seed':expected==[(a['site'],a['rule'],a['view']) for a in assignments], 'record_ids_unique':len(unique_ids)==len(set(unique_ids)), 'one_decision_per_complete_trial':all(r['decision_records']==1 for r in rows if r['status']=='complete'), 'started_order_matches_assignment':check_order, 'all_complete':result['complete']==24, 'all_complete_policy_inputs_match':all(not r.get('policy_errors') for r in rows if r['status']=='complete')}
    result['integrity_checks']['frozen_hashes_match']=all(sha(P/n)==h for n,h in freeze['sha256'].items())
    result['integrity_checks']['writes_after_freeze']=all(time(r['start_utc'])>time(freeze['frozen_utc']) for r in allrows if r.get('type')=='action' and r.get('action') in ('save_event','click New'))
    result['input_sha256']=dict(result['inputs'])
    result['issues']=[]
    for key in ('assignment_order_from_seed','record_ids_unique','one_decision_per_complete_trial','all_complete','frozen_hashes_match','writes_after_freeze'):
        if not result['integrity_checks'][key]:result['issues'].append(key)
    if not all(check_order.values()):result['issues'].append('creation_order')
    if any(r.get('identity_agrees') is False for r in rows):result['issues'].append('identity_agreement_missing')
    result['status']='PASS_WITH_LIMITATIONS' if not result['issues'] else 'NEEDS_REVIEW'
    result['status_meaning']='The replay inputs and identity evidence pass these checks. Retained procedure failures and unknown field correctness are study results, not passed experimental criteria.'
    result['groups']=[]
    for site in ('Google Calendar','Notion'):
        for rule in ('Absence','Wait24','Scope'):
            for view in ('All','Hidden'):
                g=[r for r in rows if r['site']==site and r['rule']==rule and r['assigned_view']==view and r['status']=='complete']
                result['groups'].append({'site':site,'rule':rule,'view':view,'completed':len(g),'duplicates':sum(r['duplicate'] is True for r in g),'duplicate_unknown':sum(r['duplicate'] is None for r in g),'count_confirmations':sum(r['count_confirmation'] is True for r in g),'clean_confirmations':sum(r['clean_confirmation'] is True for r in g),'clean_unknown':sum(r['clean_confirmation'] is None for r in g),'false_confirmations':sum(r['false_confirmation'] is True for r in g),'false_unknown':sum(r['false_confirmation'] is None for r in g),'retries':sum(r['writes']==2 for r in g),'cleanup':sum(r['cleanup'] for r in g)})
    result['hypotheses']=[]
    for site in ('Google Calendar','Notion'):
        g={(x['rule'],x['view']):x for x in result['groups'] if x['site']==site}
        complete=all(x['completed']==2 and x['duplicate_unknown']==0 for x in g.values())
        h1=all(g[(r,'Hidden')]['duplicates']>g[('Scope','Hidden')]['duplicates'] for r in ('Absence','Wait24')) if complete else None
        hidden_known=all(g[(r,'Hidden')]['clean_unknown']==0 for r in ('Absence','Wait24','Scope'))
        h2=all(g[('Scope','Hidden')]['clean_confirmations']>g[(r,'Hidden')]['clean_confirmations'] and g[('Scope','Hidden')]['duplicates']==0 for r in ('Absence','Wait24')) if complete and hidden_known else None
        controls=[r for r in rows if r['site']==site and r['assigned_view']=='All' and r['status']=='complete']
        h3=False if any(r['clean_confirmation'] is False or r['writes']!=1 for r in controls) else True if len(controls)==6 and all(r['clean_confirmation'] is True for r in controls) else None
        result['hypotheses'].append({'site':site,'H_P1':h1,'H_P2':h2,'H_P3':h3})
    (P/'production_independent_replay.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'complete':result['complete'],'assignments':len(rows),'errors':{r['trial_id']:r.get('policy_errors') for r in rows if r.get('policy_errors')},'identity_disagreements':[r['trial_id'] for r in rows if r.get('identity_agrees') is False],'writer_departures':{r['trial_id']:r.get('writer_view_departures') for r in rows if r.get('writer_view_departures')}},indent=2))
if __name__=='__main__':run()
