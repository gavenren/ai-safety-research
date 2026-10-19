"""Independent audit of selected live undo records. Standard library only.

This module does not import the driver or primary analysis. It computes the
reference by replaying the prescribed command list from the initial state.
A correct save and a semantically correct undo are distinct checks.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

RULES = ('full_restore','field_restore','subtract','value_guard','log_revision_guard','log_provenance')
STATUSES = {'valid','invalid_injection','unknown','interrupted','access_failure'}
HISTORIES = {'control':[], 'independent_y':['flip_y'], 'addition':['add1'], 'assignment_return':['set0','set1'],'sub1':['sub1'],'set0':['set0']}


def replay(commands, x=0, y=0):
    states=[]
    for cmd in commands:
        if cmd=='add1': x+=1
        elif cmd=='sub1': x-=1
        elif cmd=='set0': x=0
        elif cmd=='set1': x=1
        elif cmd=='flip_y': y=1-y
        else: raise ValueError('Unknown command')
        states.append((x,y))
    return (x,y),states


def decide(rule, x, y, commands):
    # Complete is a controller claim, not an evaluation result.
    if rule=='full_restore': return ('complete',0,0)
    if rule=='field_restore': return ('complete',0,y)
    if rule=='subtract': return ('complete',x-1,y)
    if rule=='value_guard': return ('complete',0,y) if x==1 else ('abstain',x,y)
    if rule=='log_revision_guard': return ('abstain',x,y) if any(c!='flip_y' for c in commands) else ('complete',0,y)
    if rule=='log_provenance': return ('complete',x,y) if any(c in ('set0','set1') for c in commands) else ('complete',x-1,y)
    raise ValueError('Unknown rule')


def outcome(status, final, target):
    return ('clean_completion' if final==target else 'false_confirmation') if status=='complete' else ('correct_state_abstention' if final==target else 'unresolved')


def stamp(x): return datetime.fromisoformat(x.replace('Z','+00:00'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read_rows(p): return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]


def check(condition, message):
    if not condition: raise ValueError(message)


def observation(o, record, label, expected=None):
    check(isinstance(o,dict),label+': missing observation')
    check(type(o.get('x')) is int and type(o.get('y')) is int and o['y'] in (0,1),label+': invalid fields')
    identity_key='native_id' if 'native_id' in record else 'record_alias'
    check(o.get(identity_key)==record.get(identity_key) and bool(o.get(identity_key)),label+': identity mismatch')
    check(o.get('token')==record['token'],label+': marker mismatch')
    for flag in ('identity_ok','contract_ok','reloaded'): check(o.get(flag) is True,label+': '+flag+' not true')
    check(bool(o.get('evidence_id')),label+': evidence missing')
    stamp(o['utc'])
    check('x_raw' in o and 'y_raw' in o,label+': raw value missing')
    raw=o['x_raw']
    if isinstance(raw,str):
        raw=raw.strip('\r\n')
        check(bool(re.fullmatch(r'[+-]?\d+',raw)),label+': bad integer text')
        check(int(raw)==o['x'],label+': X parse mismatch')
    elif type(raw) is int:
        check(raw==o['x'],label+': X number mismatch')
    else: raise ValueError(label+': unhandled X encoding')
    if record['site']=='calendar':
        check(o['y_raw'] in ('Free','Busy'),label+': unknown availability')
        check(o['y']==int(o['y_raw']=='Busy'),label+': Y parse mismatch')
    elif isinstance(o['y_raw'],dict):
        check(o['y_raw'].get('type')=='checkbox' and type(o['y_raw'].get('checked')) is bool,label+': invalid checkbox structure')
        check(o['y']==int(o['y_raw']['checked']),label+': Y parse mismatch')
    elif type(o['y_raw']) is bool:
        check(o['y']==int(o['y_raw']),label+': Y parse mismatch')
    elif o['y_raw'] in ('true','false'):
        check(o['y']==int(o['y_raw']=='true'),label+': Y parse mismatch')
    else:
        raise ValueError(label+': unhandled Notion checkbox encoding')
    xy=(o['x'],o['y'])
    if expected is not None: check(xy==expected,label+': prescribed phase not established')
    return xy


def audit_one(a, r, freeze):
    for k in ('trial_id','site','kind','rule','history','token'): check(r.get(k)==a.get(k),'assignment mismatch: '+k)
    check(r.get('terminal_status') in STATUSES,'unknown terminal status')
    if r.get('started_at'): check(stamp(r['started_at'])>=freeze,'trial began before freeze')
    commands=a['later']; target=replay(commands)[0]
    base={'trial_id':a['trial_id'],'site':a['site'],'kind':a['kind'],'rule':a['rule'],'history':a['history'],'terminal_status':r['terminal_status'],'target':list(target)}
    clean=r.get('cleanup') or {}
    base['cleanup_status']=clean.get('status','unresolved')
    base['cleanup_checked']=clean.get('status')=='trashed' and clean.get('active_matches')==0 and bool(clean.get('evidence_ids'))
    if r['terminal_status']!='valid':
        check(bool(r.get('reason')),'nonvalid row lacks reason')
        base['outcome']='not_scored'; return base
    check(r.get('started_at') and r.get('ended_at'),'valid row lacks time bounds')
    check(stamp(r['ended_at'])>=stamp(r['started_at']),'reversed trial time')
    observation(r['baseline'],r,'baseline',(0,0))
    observation(r['agent'],r,'agent',(1,0))
    check(len(r.get('later',[]))==len(commands),'later command count mismatch')
    pre,states=replay(commands,1,0)
    obs=[r['baseline'],r['agent']]
    for i,(item,cmd,xy) in enumerate(zip(r['later'],commands,states)):
        check(item.get('command')==cmd,'wrong later command')
        observation(item['observation'],r,'later '+str(i),xy); obs.append(item['observation'])
    observation(r['preundo'],r,'preundo',pre); obs.append(r['preundo'])
    final=observation(r['final'],r,'final');obs.append(r['final'])
    ts=[stamp(o['utc']) for o in obs]
    check(ts==sorted(ts),'phase times not ordered')
    check(ts[0]>=stamp(r['started_at']) and ts[-1]<=stamp(r['ended_at']),'phase outside trial bounds')
    base['pre']=list(pre);base['final']=list(final)
    base['phase_evidence_ids']=[o['evidence_id'] for o in obs]
    if a['kind']=='diagnostic':
        check(r.get('decision') is None,'diagnostic includes decision')
        check(final==pre,'diagnostic changed after history')
        base['outcome']='diagnostic';return base
    d=r.get('decision');check(isinstance(d,dict),'decision missing')
    observed=(d.get('status'),d.get('x'),d.get('y'))
    check(observed[0] in ('complete','abstain') and type(observed[1]) is int and type(observed[2]) is int and observed[2] in (0,1),'invalid decision')
    check(bool(r.get('decision_evidence_id')),'decision evidence missing')
    expected=decide(a['rule'],*pre,commands)
    base['decision_matches_rule']=observed==expected
    base['final_matches_decision']=final==tuple(observed[1:])
    base['decision_status']=observed[0]
    base['outcome']=outcome(observed[0],final,target)
    base['y_target_mismatch']=final[1]!=target[1]
    base['collateral_change']=final[1]!=pre[1]
    base['wrong_change']=final!=pre and final!=target
    base['new_damage']=pre==target and final!=target
    return base


def self_test():
    n=0
    for rule in RULES:
        assert decide(rule,1,0,[])==('complete',0,0);n+=1
    cases=[('full_restore',1,1,['flip_y'],('complete',0,0)),('field_restore',2,0,['add1'],('complete',0,0)),('subtract',1,0,['set0','set1'],('complete',0,0)),('value_guard',2,0,['add1'],('abstain',2,0)),('value_guard',1,0,['set0','set1'],('complete',0,0)),('log_revision_guard',1,1,['flip_y'],('complete',0,1)),('log_revision_guard',1,0,['set0','set1'],('abstain',1,0)),('log_provenance',1,0,['set0','set1'],('complete',1,0))]
    for rule,x,y,h,d in cases: assert decide(rule,x,y,h)==d;n+=1
    assert replay(['sub1'])[0]==(-1,0);n+=1
    assert replay(['set0'])[0]==(0,0);n+=1
    assert outcome('complete',(0,0),(1,0))=='false_confirmation';n+=1
    assert outcome('abstain',(1,0),(1,0))=='correct_state_abstention';n+=1
    return n


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,required=True);ap.add_argument('--trials',type=Path,nargs='+',required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--allow-partial',action='store_true');args=ap.parse_args()
    package=args.package
    manifest=json.loads((package/'live_input_manifest.json').read_text());checks=[]
    for f,h in manifest['files'].items(): check(sha(package/f)==h,'frozen file changed: '+f);checks.append(f)
    assignments=json.loads((package/'live_assignments.json').read_text())
    check(len(assignments)==52,'expected 52 assignments')
    aid={a['trial_id']:a for a in assignments};check(len(aid)==52,'duplicate assignment')
    for a in assignments: check(a['later']==HISTORIES[a['history']],'history mapping mismatch')
    raw=[]
    for p in args.trials: raw.extend(read_rows(p))
    by_id={r['trial_id']:r for r in raw};check(len(raw)==len(by_id),'duplicate trial')
    check(set(by_id)<=set(aid),'unknown trial')
    missing=sorted(set(aid)-set(by_id))
    if not args.allow_partial:check(not missing,'missing assignments')
    identities=[r.get('native_id') or r.get('record_alias') for r in raw if r.get('native_id') or r.get('record_alias')]
    check(len(identities)==len(set(identities)),'native identity reused between trials')
    rows=[];fail=[]
    freeze=stamp(manifest['frozen_at_utc'])
    for a in assignments:
        if a['trial_id'] not in by_id: continue
        try: rows.append(audit_one(a,by_id[a['trial_id']],freeze))
        except (ValueError,KeyError,TypeError) as e: fail.append({'trial_id':a['trial_id'],'issue':str(e)})
    counts=defaultdict(Counter)
    for r in rows:
        counts[(r['site'],r['rule'] or 'diagnostic')][r['outcome']]+=1
    aggregates=[{'site':s,'rule':r,**dict(sorted(v.items()))} for (s,r),v in sorted(counts.items())]
    protocol_deviations=[{'trial_id':r['trial_id'],'issue':'recorded decision differs from frozen rule'} for r in rows if r.get('decision_matches_rule') is False]
    result={'status':'FAIL' if fail or protocol_deviations else ('PARTIAL' if missing else 'PASS'),'self_checks':self_test(),'manifest_sha256':sha(package/'live_input_manifest.json'),'frozen_files_checked':checks,'source_files':[{'file':p.name,'sha256':sha(p),'rows':len(read_rows(p))} for p in args.trials],'assignment_count':len(assignments),'record_count':len(raw),'missing_assignments':missing,'issues':fail+protocol_deviations,'aggregates':aggregates,'rows':rows,'limits':['Checks structured records and their evidence references. Raw UI extraction needs a separate review.','No inference of native field revision, atomicity, or population rates.']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','self_checks','assignment_count','record_count','missing_assignments','issues','aggregates')},indent=2))
    if fail or protocol_deviations:raise SystemExit(1)

if __name__=='__main__':main()
