"""Analyze saved live evidence. Standard library only; no account access."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

def apply(state, command):
    x,y=state
    if command=='add1': x+=1
    elif command=='sub1': x-=1
    elif command=='set0': x=0
    elif command=='set1': x=1
    elif command=='flip_y': y=1-y
    else: raise ValueError('Unknown command')
    return [x,y]

def state(observation):
    assert isinstance(observation,dict), 'Missing observation'
    x,y=observation['x'],observation['y']
    assert type(x) is int and type(y) is int and y in (0,1), 'Invalid fields'
    for key in ('identity_ok','contract_ok','reloaded'):
        assert observation[key] is True, 'Observation gate: '+key
    assert observation['evidence_id'] and observation['utc'] and observation['record_alias']
    return [x,y]

def grade(status, final, target):
    assert status in ('complete','abstain')
    return ('clean_completion' if final==target else 'false_confirmation') if status=='complete' else ('abstain_correct' if final==target else 'unresolved')

def analyze(assignments, trials):
    ids=[a['trial_id'] for a in assignments]
    assert len(ids)==len(set(ids)), 'Duplicate assignments'
    byid={t['trial_id']:t for t in trials}
    assert len(byid)==len(trials), 'Duplicate trial rows'
    assert set(byid)==set(ids), 'Missing or unplanned trial'
    aliases=[t['record_alias'] for t in trials if t.get('record_alias')]
    assert len(aliases)==len(set(aliases)), 'Record reused'
    counts=Counter(); sites=defaultdict(Counter); rules=defaultdict(Counter); outcomes=[]; diagnostics=[]
    for a in assignments:
        t=byid[a['trial_id']]
        for k in ('site','kind','rule','history','token'):
            assert t[k]==a[k], 'Assignment mismatch: '+k
        status=t['terminal_status'];counts['assigned']+=1;sites[a['site']]['assigned']+=1
        counts[a['kind']+'_assigned']+=1;sites[a['site']][a['kind']+'_assigned']+=1
        if a['kind']=='core':rules[a['rule']]['assigned']+=1
        assert status in ('valid','invalid_injection','unknown','interrupted','access_failure')
        counts[status]+=1;sites[a['site']][status]+=1
        cleanup=t['cleanup']
        assert cleanup['status'] in ('trashed','unresolved','not_created','no_saved_record_found')
        counts['cleanup_'+cleanup['status']]+=1
        if cleanup['status'] in ('trashed','no_saved_record_found'):
            assert cleanup['active_matches']==0 and cleanup['evidence_ids']
        if status!='valid':
            assert t.get('reason'), 'Missing exclusion reason'
            counts[a['kind']+'_unscored']+=1;sites[a['site']][a['kind']+'_unscored']+=1
            if a['kind']=='core':rules[a['rule']]['unscored']+=1
            outcomes.append({'trial_id':a['trial_id'],'site':a['site'],'rule':a['rule'],'history':a['history'],'kind':a['kind'],'terminal_status':status,'outcome':None})
            continue
        assert state(t['baseline'])==[0,0]
        assert state(t['agent'])==[1,0]
        expected=[1,0];reference=[0,0]
        assert [v['command'] for v in t['later']]==a['later'], 'Incomplete history'
        obs=[t['baseline'],t['agent']]
        for command,item in zip(a['later'],t['later']):
            expected=apply(expected,command);reference=apply(reference,command)
            assert state(item['observation'])==expected, 'Injection mismatch'
            obs.append(item['observation'])
        assert state(t['preundo'])==expected, 'Pre-undo mismatch'
        final=state(t['final']);obs.extend((t['preundo'],t['final']))
        assert all(o['record_alias']==t['record_alias'] and o['token']==t['token'] for o in obs), 'Wrong identity'
        row={'trial_id':a['trial_id'],'site':a['site'],'kind':a['kind'],'rule':a['rule'],'history':a['history'],'terminal_status':status,'preundo':expected,'target':reference,'final':final}
        if a['kind']=='diagnostic':
            assert t['decision'] is None and final==expected
            counts['diagnostics_valid']+=1;sites[a['site']]['diagnostics_valid']+=1
            diagnostics.append(row);row['outcome']=None
        else:
            decision=t['decision'];assert t['decision_evidence_id']
            assert type(decision['x']) is int and type(decision['y']) is int
            outcome=grade(decision['status'],final,reference)
            dispatch_match=final==[decision['x'],decision['y']]
            row.update(outcome=outcome,decision=decision,decision_saved=dispatch_match,collateral_y=final[1]!=reference[1])
            counts['core_valid']+=1;counts[outcome]+=1;sites[a['site']]['core_valid']+=1;sites[a['site']][outcome]+=1
            rules[a['rule']]['valid']+=1;rules[a['rule']][outcome]+=1
            counts['decision_saved']+=int(dispatch_match);counts['collateral_y']+=int(row['collateral_y'])
        outcomes.append(row)
    return {'counts':dict(counts),'sites':{k:dict(v) for k,v in sites.items()},'rules':{k:dict(v) for k,v in rules.items()},'outcomes':outcomes,'diagnostics':diagnostics,'inference':'Selected sequential cases in two accounts; no population estimate.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-dir',default='.');parser.add_argument('--output-dir',default='.')
    args=parser.parse_args();base=Path(args.input_dir);out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((base/'live_input_manifest.json').read_text())
    for file,sha in manifest['files'].items():
        assert hashlib.sha256((base/file).read_bytes()).hexdigest()==sha, 'Frozen input changed: '+file
    assignments=json.loads((base/'live_assignments.json').read_text())
    trials=[json.loads(s) for s in (base/'live_trials.jsonl').read_text().splitlines() if s]
    result=analyze(assignments,trials)
    (out/'live_results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result['counts'],sort_keys=True))

if __name__=='__main__':main()
