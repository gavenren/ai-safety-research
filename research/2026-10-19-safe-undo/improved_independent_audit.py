"""Independent evidence and outcome checks for the improved live study.

No browser access. Does not import the JavaScript controller or main analyzer.
Raw browser source and public extraction require additional separate checks.
"""
import argparse
from collections import Counter,defaultdict
import hashlib,json,re
from pathlib import Path
from improved_independent_model import fields,vector,moment,replay,prepare,finish,grade


def require(c,m):
    if not c:raise ValueError(m)
def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def oid(o):return o.get('evidence_id') or o.get('readId') or (o.get('source') or {}).get('id')
def otime(o):return o.get('utc') or o.get('readAt')
def identity(o):return o.get('native_id') or o.get('identity') or o.get('record_alias')
def projected(o):return {'x':o['x'],'y':o['y'],'identity':identity(o),'contract':o.get('contract_ok',o.get('contract')),'reloaded':o.get('reloaded'),'readId':oid(o),'readAt':otime(o)}


def check_observation(o,t,label,expected=None):
    require(isinstance(o,dict) and fields(o),label+': missing or bad fields')
    ident=identity(t) or t['prepare_input']['expectedIdentity']
    require(identity(o)==ident and bool(ident),label+': record identity changed')
    require(o.get('contract_ok',o.get('contract')) is True and o.get('reloaded') is True,label+': contract or reload missing')
    if 'identity_ok' in o:require(o['identity_ok'] is True,label+': identity check false')
    marker=o.get('marker',o.get('token'))
    if marker is not None:require(marker==t['assignment']['marker'],label+': marker changed')
    require(bool(oid(o)),label+': read ID missing');moment(otime(o))
    if 'native_id' in t or 'x_raw' in o:
        require('x_raw' in o and 'y_raw' in o,label+': raw fields missing')
        raw=o['x_raw']
        require(isinstance(raw,str) and re.fullmatch(r'[+-]?\d+',raw.strip('\r\n')) is not None,label+': integer text invalid')
        require(int(raw.strip('\r\n'))==o['x'],label+': integer parse mismatch')
        y=o['y_raw']
        if t['assignment']['site']=='calendar':require(y in ('Free','Busy') and int(y=='Busy')==o['y'],label+': availability parse mismatch')
        elif isinstance(y,dict):require(y.get('type')=='checkbox' and type(y.get('checked')) is bool and int(y['checked'])==o['y'],label+': checkbox parse mismatch')
        elif type(y) is bool:require(int(y)==o['y'],label+': checkbox parse mismatch')
        else:require(y in ('true','false') and int(y=='true')==o['y'],label+': checkbox parse mismatch')
    if expected is not None:require(vector(o)==vector(expected),label+': prescribed setup state absent')
    return projected(o)


def audit_trial(a,t,freeze):
    require(t['trial_id']==a['trial_id'] and t['assignment']==a,'assignment changed')
    require(t['status'] in ('valid','unknown'),'unplanned terminal status')
    require(moment(t['started_at'])>=freeze and moment(t['ended_at'])>=moment(t['started_at']),'invalid trial interval')
    target,_=replay({'x':0,'y':0},a['full_later'])
    row={k:a[k] for k in ('trial_id','site','scenario','rule')};row.update(status=t['status'],target=target,cleanup_status=t.get('cleanup',{}).get('status','unresolved'))
    if t['status']=='unknown':
        require(bool(t.get('reason')),'unknown trial lacks reason')
        row['outcome']='unknown';row['write_attempted']=bool((t.get('actuator') or {}).get('attempted',(t.get('actuator') or {}).get('write_attempted',False)));return row
    base=check_observation(t['baseline'],t,'baseline',{'x':0,'y':0});agent=check_observation(t['agent'],t,'agent',{'x':1,'y':0})
    phases=t['later_phases'];require([p['command'] for p in phases]==a['full_later'],'true later commands changed')
    pre,states=replay({'x':1,'y':0},a['full_later'])
    obs=[t['baseline'],t['agent']]
    for i,(phase,expected) in enumerate(zip(phases,states)):
        check_observation(phase['observation'],t,'later '+str(i),expected);obs.append(phase['observation'])
    current=check_observation(t['preundo'],t,'preundo',pre);obs.append(t['preundo'])
    seal=t['seal'];require(seal['presented_later']==a['presented_later'] and seal['history_complete'] is a['history_complete'],'presented log seal differs')
    require(seal.get('before_later',seal.get('seal_before_later')) is a['seal_before_later'],'log seal position differs')
    seal_time=moment(seal['utc']);require(moment(agent['readAt'])<=seal_time<=moment(current['readAt']),'seal outside setup interval')
    if a['seal_before_later']:require(phases and seal_time<moment(otime(phases[0]['observation'])),'post-seal edit was not after seal')
    else:require(seal_time>=moment(otime(obs[-2])),'log sealed before included history')
    data=t['prepare_input'];expected_input={'initial':{'x':0,'y':0},'agent':{'x':1,'y':0},'current':current,'later':a['presented_later'],'historyComplete':a['history_complete'],'expectedIdentity':current['identity']}
    require(data==expected_input,'prepare input does not match presented evidence')
    expected_decision=prepare(a['rule'],data);issues=[]
    if t['decision']!=expected_decision:issues.append('recorded prepare output differs from frozen rule')
    require(bool(t.get('prepare_evidence_id') or t.get('prepare_evidence') or t.get('prepare_source')),'prepare evidence missing')
    require(len(t['final_reads'])==2,'two final reads missing')
    projected_reads=[]
    for i,o in enumerate(t['final_reads']):projected_reads.append(check_observation(o,t,'final '+str(i)));obs.append(o)
    require(t['finish_input']==projected_reads,'finish input does not match saved reads')
    times=[moment(otime(o)) for o in obs];require(times==sorted(times) and len({oid(o) for o in obs})==len(obs),'read order or IDs invalid')
    require(times[0]>=moment(t['started_at']) and times[-1]<=moment(t['ended_at']),'read outside trial interval')
    require(times[-2]>moment(current['readAt']) and times[-1]>times[-2],'final reads not after pre-read')
    expected_finish=finish(a['rule'],expected_decision,projected_reads)
    if t['finish']!=expected_finish:issues.append('recorded finish differs from frozen rule')
    require(bool(t.get('finish_evidence_id') or t.get('finish_evidence') or t.get('finish_source')),'finish evidence missing')
    require(t['finish']['status'] in ('complete','abstain','unknown'),'final status unknown to evaluator')
    actuator=t.get('actuator') or {};requested=actuator.get('requested');literal=actuator.get('literal',actuator.get('actual_literal'));attempted=actuator.get('attempted',actuator.get('write_attempted',False))
    require(type(attempted) is bool,'write flag not Boolean')
    wanted=expected_decision['write']
    if requested!=wanted:issues.append('actuator request differs from decision')
    if attempted!=(wanted is not None):issues.append('write attempt differs from rule')
    if 'write_attempts' in t:require(type(t['write_attempts']) is int and t['write_attempts']==int(attempted),'undo attempt count exceeds plan')
    expected_literal=None if wanted is None else dict(wanted)
    if expected_literal is not None and a['fault']=='x_plus_two':expected_literal['x']+=2
    if expected_literal is not None and a['fault']=='flip_y':expected_literal['y']=1-expected_literal['y']
    if literal!=expected_literal or actuator.get('fault')!=a['fault']:issues.append('actuator fault instruction differs from plan')
    if attempted:require(bool(actuator.get('evidence_id') or actuator.get('source')),'actuator dispatch evidence missing')
    saved_actuator=actuator.get('saved')
    if saved_actuator is not None:check_observation(saved_actuator,t,'actuator saved');require(moment(current['readAt'])<moment(otime(saved_actuator))<=times[-2],'actuator read outside interval')
    finals=[{'x':o['x'],'y':o['y']} for o in t['final_reads']]
    outcome=grade(t['finish']['status'],finals,target)
    row.update(outcome=outcome,pre=pre,decision_status=t['decision']['status'],finish_status=t['finish']['status'],finish_reason=t['finish']['reason'],decision_target=t['decision']['target'],final_reads=finals,write_attempted=attempted,prewrite_refusal=t['decision']['status']=='abstain',fault=a['fault'],fault_saved=all(f==expected_literal for f in finals) if a['fault'] else None,final_matches_dispatch=all(f==expected_literal for f in finals) if attempted else None,y_target_mismatch=any(f['y']!=target['y'] for f in finals),protocol_issues=issues,read_ids=[oid(o) for o in obs])
    return row


def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--trials',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-partial',action='store_true');args=p.parse_args()
    manifest=json.loads((args.package/'improved_input_manifest.json').read_text())
    for f,h in manifest['files'].items():require(sha(args.package/f)==h,'frozen file changed: '+f)
    assignments=json.loads((args.package/'improved_assignments.json').read_text())['assignments'];require(len(assignments)==32,'assignment count differs')
    raw=[]
    for path in args.trials:raw.extend(read(path))
    rows_by_id={r['trial_id']:r for r in raw};assigned={a['trial_id']:a for a in assignments}
    require(len(rows_by_id)==len(raw) and set(rows_by_id)<=set(assigned),'duplicate or unplanned trial')
    ids=[identity(t) or (t.get('prepare_input') or {}).get('expectedIdentity') for t in raw];known=[x for x in ids if x];require(len(set(known))==len(known),'record reused across trials')
    missing=sorted(set(assigned)-set(rows_by_id));require(args.allow_partial or not missing,'missing assignments')
    result_rows=[];issues=[]
    for a in assignments:
        if a['trial_id'] not in rows_by_id:continue
        try:
            row=audit_trial(a,rows_by_id[a['trial_id']],moment(manifest['frozen_at_utc']));result_rows.append(row)
            issues.extend({'trial_id':a['trial_id'],'issue':x} for x in row.get('protocol_issues',[]))
        except (ValueError,KeyError,TypeError) as e:issues.append({'trial_id':a['trial_id'],'issue':str(e)})
    counts=Counter();by_rule=defaultdict(Counter);by_site=defaultdict(Counter)
    for r in result_rows:
        for c in (counts,by_rule[r['rule']],by_site[r['site']]):
            c['assigned']+=1;c[r['status']]+=1
            if r['status']=='valid':c[r['outcome']]+=1;c['write_attempted']+=int(r['write_attempted']);c['prewrite_refusal']+=int(r['prewrite_refusal'])
            if r.get('fault') and r['status']=='valid':c['fault_assigned_valid']+=1;c['fault_saved']+=int(r['fault_saved'])
    pairs=[]
    for site in ('calendar','notion'):
        for scenario in sorted({a['scenario'] for a in assignments}):
            r={r['rule']:r for r in result_rows if r['site']==site and r['scenario']==scenario}
            complete=len(r)==2 and all(x['status']=='valid' for x in r.values())
            pairs.append({'site':site,'scenario':scenario,'paired_valid':complete,'outcomes':{k:v['outcome'] for k,v in r.items()}})
    result={'status':'FAIL' if issues else ('PARTIAL' if missing else 'PASS'),'manifest_sha256':sha(args.package/'improved_input_manifest.json'),'assignment_count':32,'record_count':len(raw),'missing':missing,'issues':issues,'counts':dict(counts),'rules':{k:dict(v) for k,v in by_rule.items()},'sites':{k:dict(v) for k,v in by_site.items()},'pairs':pairs,'rows':result_rows,'source_files':[{'name':p.name,'sha256':sha(p)} for p in args.trials],'limits':['Controller inspected during design review; main analysis not read during this independent implementation.','Saved observations require separate native-source and extraction checks.','True log completeness and atomic browser behavior are not established by matching values.']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k] for k in ['status','record_count','missing','issues','counts','rules']},indent=2))
    if issues:raise SystemExit(1)

if __name__=='__main__':main()
