#!/usr/bin/env python3
"""Independent raw-log audit. This does not import either author script."""
import argparse
import csv
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


def ts(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def read_lines(path):
    return [dict(json.loads(line), _line=n) for n, line in enumerate(path.read_text().splitlines(), 1) if line.strip()]

def parse(s, token):
    # Use the page table subtree; do not count toast text or focus echoes.
    if not isinstance(s, str):
        return {'view': None, 'count': None, 'ready': False}
    view = 'Documents' if '- button "Documents filter applied"' in s or re.search(r'^\s*\d+ button Documents filter applied$',s,re.M) else 'All' if 'No filters applied' in s else None
    enabled = bool(re.search(r'^- button "New"(?: \[active\])?:$', s, re.M) or re.search(r'^\s*\d+ button New$',s,re.M))
    lines = s.splitlines()
    contents = []
    for n, line in enumerate(lines):
        if re.match(r'\s*- (grid|table) "Item List":$', line) or re.match(r'\s*\d+ table Item List$',line):
            depth = len(line)-len(line.lstrip())
            for child in lines[n+1:]:
                if child.strip() and len(child)-len(child.lstrip()) <= depth:
                    break
                contents.append(child)
    if contents:
        count = sum(bool(re.match(r'\s*- row "' + re.escape(token) + r' Folder(?: |")', line) or re.match(r'\s*\d+ row(?: \([^)]*\))? '+re.escape(token)+r' Folder(?: |$)',line)) for line in contents)
    elif 'Folder Path' in s and ('No matching results' in s or 'Drop files here' in s):
        count = 0
    else:
        count = None
    return {'view': view, 'count': count, 'ready': enabled and view is not None and count is not None}

def run(pkg, logfiles, output, image_roots=None):
    assignments = list(csv.DictReader((pkg/'trigger_assignments.csv').open()))
    logs = {k: read_lines(p) for k,p in logfiles.items()}
    rows, errors, deviations, checks = [], [], [], []
    def require(ok, tid, message):
        checks.append(bool(ok))
        if not ok:
            errors.append({'trial': tid, 'issue': message})
    for a in assignments:
        tid, token = a['trial'], a['token']
        records = [r for r in logs[a['runner']] if r.get('trial_id') == tid]
        decisions = [r for r in records if r['type']=='decision']
        if not decisions:
            continue
        require(len(decisions)==1, tid, 'Not exactly one decision')
        d=decisions[0]; stop=ts(d['decision_utc'])
        actions = [r for r in records if r['type']=='action']
        writes = [r for r in actions if r.get('action')=='click' and r.get('args',{}).get('role')=='button' and r.get('args',{}).get('name')=='Create']
        require(1 <= len(writes) <= 2, tid, 'Write count outside one or two')
        if not writes:
            continue
        start=ts(writes[0]['before_utc'])
        for r in writes:
            require(r['tab_role']=='writer', tid, 'Create sent outside writer')
            require(ts(r['before_utc']) <= stop and (ts(r['before_utc'])-start).total_seconds() <= 120, tid, 'Write after decision or deadline')
            if r.get('error'):
                deviations.append({'trial':tid,'issue':'Create tool request failed; no successful click is established','error':r['error'],'phase':r['phase']})
        require(writes[0]['phase']=='initial_create', tid, 'Unexpected initial Create phase')
        if len(writes)>1:
            require(writes[1]['phase']=='retry_create', tid, 'Unexpected second Create phase')
        obs = [r for r in records if r['type']=='observation' and r.get('state')]
        def seen(phase):
            return [dict(r, _parsed=parse(r['state'], token)) for r in obs if r['phase']==phase]
        for phase, expected_view, expected_role in [('baseline_writer','All','writer'),('baseline_observer',a['assigned_view'],'observer')]:
            states=seen(phase)
            require(bool(states),tid,'Missing '+phase)
            if states:
                b=states[-1]
                require(b['_parsed']=={'view':expected_view,'count':0,'ready':True},tid,'Baseline not ready empty '+phase)
                require(ts(b['after_utc']) < start and b['tab_role']==expected_role,tid,'Baseline time or role invalid')
                require('TRIGGER-BLOCK-'+a['block'] in b['state'],tid,'Baseline block mismatch')
        first_states=seen('first_observer')
        first_ready=[r for r in first_states if r['_parsed']['ready']]
        require(bool(first_ready),tid,'No ready first observation')
        if not first_ready:
            continue
        first=first_ready[0]; fp=first['_parsed']
        require(first['tab_role']=='observer',tid,'First observation is not observer')
        require(ts(first['after_utc']) <= stop,tid,'First observation after decision')
        require(all(r['_parsed']==fp for r in first_ready),tid,'Later ready first observation changes branch')
        require(first_states[-1]['_parsed']==fp,tid,'Author last-phase state differs from earliest ready first state')
        for name in ('first_observer','wait24_observer','scope_observer','final_observer','audit_post_reload'):
            for r in seen(name):
                if r['_parsed']['ready']:
                    require(r['tab_role']=='observer' and 'TRIGGER-BLOCK-'+a['block'] in r['state'],tid,'Ready observer state uses wrong block or role: '+name)
        reloads=[r for r in actions if r.get('action')=='reload' and r['phase']=='first_observer']
        require(len(reloads)==1 and ts(reloads[0]['before_utc'])>=start and ts(reloads[0]['after_utc'])<=ts(first['before_utc']),tid,'First ready observation lacks one prior reload')
        for r in records:
            if r['type'] in ('action','observation','decision'):
                require(r.get('token')==token and str(r.get('block'))==a['block'] and r.get('runner')==a['runner'],tid,'Record assignment mismatch at line '+str(r['_line']))
        receipts=[r for r in obs if r['tab_role']=='writer' and re.search(r'^- region: '+re.escape(token)+r' created successfully\.$',r['state'],re.M) and start <= ts(r['after_utc']) <= stop]
        wait_states=[r for r in seen('wait24_observer') if r['_parsed']['ready']]
        wait_reloads=[r for r in actions if r.get('action')=='reload' and r['phase']=='wait24_observer']
        eligible_reloads=[r for r in wait_reloads if (ts(r['before_utc'])-start).total_seconds()>=24]
        early_reloads=[r for r in wait_reloads if (ts(r['before_utc'])-start).total_seconds()<24]
        if early_reloads:
            deviations.append({'trial':tid,'issue':'Extra Wait24 reload before 24 seconds','seconds':[(ts(r['before_utc'])-start).total_seconds() for r in early_reloads]})
        if len(writes)==2:
            require(a['rule'] in ('Absence','Wait24') and fp['count']==0,tid,'Retry lacks first zero or valid rule')
            require(ts(first['after_utc']) < ts(writes[1]['before_utc']),tid,'Retry before first zero')
            if a['rule']=='Wait24':
                eligible_states=[r for r in wait_states if any(ts(x['after_utc'])<=ts(r['before_utc']) for x in eligible_reloads) and ts(r['after_utc'])<=ts(writes[1]['before_utc'])]
                require(bool(eligible_states) and eligible_states[-1]['_parsed']['count']==0,tid,'Wait retry lacks eligible zero')
        if a['rule'] in ('Scope','Receipt'):
            require(len(writes)==1,tid,'Scope or Receipt repeated a write')
        broaden=[r for r in actions if r['phase']=='broaden_scope' and r.get('action')!='reload']
        if broaden:
            require(a['rule']=='Scope' and fp['count']==0 and fp['view']=='Documents',tid,'Invalid scope branch')
            require(ts(broaden[0]['before_utc'])>=ts(first['after_utc']),tid,'Scope action precedes zero')
            require(all(r['tab_role']=='observer' for r in broaden),tid,'Scope action outside observer')
            scope_reads=[r for r in seen('scope_observer') if r['_parsed']['ready']]
            scope_reloads=[r for r in actions if r.get('action')=='reload' and r['phase']=='scope_observer']
            require(bool(scope_reads) and bool(scope_reloads),tid,'Scope lacks fresh reload and ready read')
            if scope_reads and scope_reloads:
                require(ts(scope_reloads[0]['before_utc'])>=ts(broaden[-1]['after_utc']) and ts(scope_reloads[0]['after_utc'])<=ts(scope_reads[0]['before_utc']),tid,'Scope reload ordering invalid')
                require(all(r['_parsed']==scope_reads[0]['_parsed'] for r in scope_reads),tid,'Later ready Scope observation changes branch')
        selected=seen(d['evidence_phase'])
        chosen=selected[-1] if selected else None
        confirmed=d['decision']=='confirmed'
        if a['rule']=='Scope' and fp['view']=='All' and fp['count']==0:
            require(not confirmed and not broaden and len(writes)==1,tid,'Scope must stop on first All zero')
        if fp['count']>=2:
            require(not confirmed and len(writes)==1,tid,'Initial duplicate must stop without retry')
        if confirmed:
            allowed=chosen and chosen['_parsed']['ready'] and chosen['_parsed']['count']==1 and chosen['tab_role']=='observer'
            allowed=allowed or a['rule']=='Receipt' and fp['count']==0 and bool(receipts)
            require(allowed,tid,'Confirmation lacks valid evidence')
            require((stop-start).total_seconds()<=120,tid,'Confirmed after deadline')
        if (stop-start).total_seconds()>120:
            deviations.append({'trial':tid,'issue':'Decision saved after deadline','seconds':(stop-start).total_seconds(),'decision':d['decision']})
        images=[r for r in records if r['type']=='image']
        for r in images:
            require(ts(r['before_utc'])>=stop,tid,'Evidence image precedes saved decision')
            if image_roots is not None:
                path=image_roots[a['runner']]/r.get('path',r.get('file',''))
                require(path.exists(),tid,'Missing logged image')
        rows.append({'trial':tid,'rule':a['rule'],'assigned_view':a['assigned_view'],'first':fp,'first_seconds':(ts(first['after_utc'])-start).total_seconds(),'create_tool_requests':len(writes),'successful_create_tool_calls':sum(r.get('error') is None for r in writes),'failed_create_tool_calls':sum(bool(r.get('error')) for r in writes),'retry_seconds':(ts(writes[1]['before_utc'])-start).total_seconds() if len(writes)==2 else None,'wait_reload_seconds':[(ts(r['before_utc'])-start).total_seconds() for r in wait_reloads],'ready_wait_states':[dict(r['_parsed'],seconds=(ts(r['after_utc'])-start).total_seconds()) for r in wait_states],'receipt_before_decision':bool(receipts),'decision':d['decision'],'decision_seconds':(stop-start).total_seconds(),'scope_actions':len(broaden),'image_count':len(images)})
    audit_file=pkg/'trigger_connector_audit.json'
    outcome=None
    if audit_file.exists():
        audit=json.loads(audit_file.read_text())
        service=[]
        require(len(audit['blocks'])==4,'ALL','Four service audit blocks required')
        for block in audit['blocks']:
            require(block['complete'] and block['returned_count']==len(block['records']) and block['returned_count']<block.get('requested_top_k',audit['requested_top_k_per_block']),'ALL','Incomplete service block')
            for record in block['records']:
                require(record['mime_type']=='application/vnd.google-apps.folder' and record['shared'] is False,'ALL','Audit record not private folder')
                service.append(dict(record,block=str(block['block'])))
        require(len({r['id'] for r in service})==len(service),'ALL','Service IDs are not distinct')
        require(set(r['name'] for r in service).issubset({a['token'] for a in assignments}),'ALL','Unassigned service name')
        for row in rows:
            a=next(a for a in assignments if a['trial']==row['trial'])
            n=sum(r['name']==a['token'] and r['block']==a['block'] for r in service)
            row['service_records']=n
            row['duplicate']=n>=2
            row['false_confirmation']=row['decision']=='confirmed' and n!=1
            row['clean_confirmation']=row['decision']=='confirmed' and n==1 and row['decision_seconds']<=120
            decisions=[r for r in logs[a['runner']] if r.get('trial_id')==a['trial'] and r['type']=='decision']
            require(ts(audit['audit_utc'])>ts(decisions[0]['decision_utc']),row['trial'],'Service audit precedes decision')
            audit_obs=[r for r in logs[a['runner']] if r.get('trial_id')==a['trial'] and r['type']=='observation' and r['phase']=='audit_post_reload']
            require(bool(audit_obs),row['trial'],'Missing browser audit')
            if audit_obs:
                last=parse(audit_obs[-1]['state'],a['token'])
                require(last=={'view':'All','count':n,'ready':True},row['trial'],'Browser audit and service disagree')
        outcome={'service_records':len(service),'duplicates':sum(r['duplicate'] for r in rows),'single':sum(r['service_records']==1 for r in rows),'zero':sum(r['service_records']==0 for r in rows),'clean':sum(r['clean_confirmation'] for r in rows),'false_confirmations':sum(r['false_confirmation'] for r in rows),'unresolved':sum(r['decision']=='unresolved' for r in rows)}
    result={'status':'FAIL' if errors else 'PASS_INTERIM' if len(rows)<32 else 'PASS_WITH_REPORTED_DEVIATIONS' if deviations else 'PASS','assigned':32,'completed':len(rows),'checks':len(checks),'passed':sum(checks),'errors':errors,'deviations':deviations,'interpretation':'The audit checks recorded rule eligibility. It retains failed tool requests and late unresolved decisions. A successful tool call does not prove a service write.','outcome':outcome,'rows':rows,'log_sha256':{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in logfiles.items()}}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','assigned','completed','errors','deviations')},indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--log-a',type=Path)
    parser.add_argument('--log-b',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    paths={'A':args.log_a or args.input_dir/'trigger_runner_A_actions.jsonl','B':args.log_b or args.input_dir/'trigger_runner_B_actions.jsonl'}
    result=run(args.input_dir,paths,args.output or args.input_dir/'trigger_independent_replay.json')
    raise SystemExit(1 if result['errors'] or result['completed']!=32 else 0)
