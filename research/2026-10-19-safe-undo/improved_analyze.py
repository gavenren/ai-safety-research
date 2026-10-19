"""Grade extracted saved records. Do not infer a final value from a rule decision."""
import argparse, collections, hashlib, json
from pathlib import Path

def replay(start, commands):
    x,y=start['x'],start['y']
    for c in commands:
        if c=='add1': x+=1
        elif c=='sub1': x-=1
        elif c=='set0': x=0
        elif c=='set1': x=1
        elif c=='flip_y': y=1-y
        else: raise ValueError('Unknown command')
    return {'x':x,'y':y}

def vector(o):
    assert type(o['x']) is int and type(o['y']) is int and o['y'] in (0,1),'Invalid field value'
    return {'x':o['x'],'y':o['y']}

def grade(row, assignment):
    assert row['trial_id']==assignment['trial_id']
    assert row['assignment']==assignment,'Assignment drift'
    out={k:assignment[k] for k in ['trial_id','site','scenario','rule']}
    out.update(outcome='unknown',claim=None,target=replay({'x':0,'y':0},assignment['full_later']),reason=row.get('reason'),write_attempted=None)
    if row['status']!='valid': return out
    initial=vector(row['baseline']); agent=vector(row['agent'])
    assert initial=={'x':0,'y':0} and agent=={'x':1,'y':0},'Setup mismatch'
    phases=row['later_phases']; assert len(phases)==len(assignment['full_later'])
    current=agent
    for phase,command in zip(phases,assignment['full_later']):
        assert phase['command']==command
        current=replay(current,[command]); assert vector(phase['observation'])==current,'History not saved'
    assert vector(row['preundo'])==current,'Unexpected prestate'
    all_reads=[row['baseline'],row['agent']]+[p['observation'] for p in phases]+[row['preundo']]+row['final_reads']
    identity=row['baseline']['identity']
    assert all(r['identity']==identity and r['contract'] is True and r['reloaded'] is True for r in all_reads),'Invalid observation contract'
    assert all(r['source']['sha256'] and r['source']['line']>0 for r in all_reads),'Missing evidence link'
    inp=row['prepare_input']; assert vector(inp['initial'])==initial and vector(inp['agent'])==agent
    assert inp['later']==assignment['presented_later'] and inp['historyComplete']==assignment['history_complete']
    assert inp['expectedIdentity']==identity and inp['current']=={k:row['preundo'][k] for k in ['x','y','identity','contract','readId','readAt','reloaded']},'Rule input differs from read'
    assert len(row['final_reads'])==2,'Two final reads required for scoring'
    final=[vector(o) for o in row['final_reads']]
    claim=row['finish']['status'];out.update(claim=claim,final=final,write_attempted=row['actuator']['attempted'],reason=row['finish']['reason'])
    if claim=='unknown':return out
    assert claim in ('complete','abstain')
    correct=all(v==out['target'] for v in final)
    out['outcome']=('clean_completion' if correct else 'false_confirmation') if claim=='complete' else ('abstain_correct' if correct else 'unresolved')
    out['both_final_match_target']=correct
    out['y_mismatch']=any(v['y']!=out['target']['y'] for v in final)
    out['prewrite_refusal']=row['decision']['status']=='abstain' and not row['actuator']['attempted']
    out['deliberate_fault']=assignment['fault'] is not None
    out['fault_literal_observed']=None if not assignment['fault'] else all(v==row['actuator']['literal'] for v in final)
    return out

def aggregate(rows):
    counts=collections.Counter(r['outcome'] for r in rows)
    return {'planned':len(rows),'valid':len(rows)-counts['unknown'],**{k:counts[k] for k in ['clean_completion','false_confirmation','unresolved','abstain_correct','unknown']},'write_attempts':sum(r.get('write_attempted') is True for r in rows),'prewrite_refusals':sum(r.get('prewrite_refusal',False) for r in rows),'y_mismatches':sum(r.get('y_mismatch',False) for r in rows)}

def analyze(package):
    manifest=json.loads((package/'improved_input_manifest.json').read_text())
    for name,expected in manifest['files'].items():assert hashlib.sha256((package/name).read_bytes()).hexdigest()==expected,'Frozen input changed: '+name
    assigned=json.loads((package/'improved_assignments.json').read_text())['assignments']
    data=[json.loads(s) for s in (package/'improved_trials.jsonl').read_text().splitlines()]
    assert len(data)==len(assigned)==32
    by_id={r['trial_id']:r for r in data};assert len(by_id)==len(data)
    assert set(by_id)=={a['trial_id'] for a in assigned}
    rows=[grade(by_id[a['trial_id']],a) for a in assigned]
    by_rule={rule:aggregate([r for r in rows if r['rule']==rule]) for rule in ['baseline_log_provenance','checked_history']}
    by_site={site:{rule:aggregate([r for r in rows if r['site']==site and r['rule']==rule]) for rule in by_rule} for site in ['calendar','notion']}
    pairs=[]
    for site in by_site:
        for scenario in sorted({r['scenario'] for r in rows}):
            pair={r['rule']:r for r in rows if r['site']==site and r['scenario']==scenario}
            b,n=pair['baseline_log_provenance'],pair['checked_history']
            pairs.append({'site':site,'scenario':scenario,'baseline':b['outcome'],'improved':n['outcome'],'valid_pair':b['outcome']!='unknown' and n['outcome']!='unknown'})
    checked=[r for r in rows if r['rule']=='checked_history'];positive=[r for r in checked if r['scenario'] in ['control','independent_y','addition','assignment_return']]
    expected_refusals=[r for r in checked if r['scenario'] in ['incomplete_history','prestate_mismatch']]
    fault=[r for r in checked if r['deliberate_fault']] if all('deliberate_fault' in r for r in checked) else [r for r in checked if r['scenario'].startswith('wrong_')]
    hypotheses={'H1':{'false_confirmations':by_rule['checked_history']['false_confirmation'],'valid':by_rule['checked_history']['valid'],'unknown':by_rule['checked_history']['unknown']},'H2':{'planned_positive':len(positive),'clean_positive':sum(r['outcome']=='clean_completion' for r in positive),'unknown':sum(r['outcome']=='unknown' for r in positive)},'H3':{'planned':len(expected_refusals),'observed_prewrite_refusals':sum(r.get('prewrite_refusal',False) for r in expected_refusals)},'H4':{'planned':len(fault),'observed_refusals':sum(r['claim']=='abstain' for r in fault),'unknown':sum(r['outcome']=='unknown' for r in fault)},'H5':{'baseline_incomplete_or_wrong_save_false':sum(r['rule']=='baseline_log_provenance' and r['scenario'] in ['incomplete_history','wrong_x_save','wrong_y_save'] and r['outcome']=='false_confirmation' for r in rows)}}
    return {'status':'PASS','scope':'Selected controlled production cases; counts are not population rates.','total':aggregate(rows),'by_rule':by_rule,'by_site':by_site,'pairs':pairs,'hypotheses':hypotheses,'rows':rows}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--package',default='.');parser.add_argument('--output',default='improved_results.json');args=parser.parse_args()
    result=analyze(Path(args.package));Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'total':result['total'],'by_rule':result['by_rule']},indent=2))
