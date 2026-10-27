"""Compare all saved data with the frozen independent prefix specification."""
import argparse,csv,gzip,hashlib,json
from pathlib import Path
from collections import Counter,defaultdict
import independent_spec as spec

def state(rule,point_values,prefix):
    s=spec.prefix_state(rule,point_values,prefix)
    return {'seen':list(s['seen']),'arrival':list(s['arrival']),'q':s['q'],
            'last':s['last_arrival'] if rule=='ArrivalDrop' else None,
            'by_epoch':s['epoch_last'] if rule=='EpochLast' else s['epoch_max'] if rule=='EpochMax' else {},
            'all_final_reports_seen':all(x in prefix for x in ('T0','T1'))}

def expected_trace(h,rule):
    v=h['values'];points=spec.values(**v);order=h['order']
    states=[state(rule,points,order[:i]) for i in range(len(order)+1)]
    closed=states[-1]['all_final_reports_seen'];raw=spec.all_branches(states[-1]['q'],v['z0']+v['z1'],closed)
    decisions=[{'capacity':d['C'],'demand':d['b'],'closed':closed,**{k:x for k,x in d.items() if k not in ('C','b')}} for d in raw]
    return {'history_id':h['id'],'rule':rule,'initial':states[0],
            'steps':[{'report_id':r,'duplicate':r in order[:i],'after':states[i+1]} for i,r in enumerate(order)],
            'final_error':states[-1]['q']-(v['z0']+v['z1']),'decisions':decisions}

def expected_inputs():
    rows=[]
    for n,x in enumerate(spec.enumerate_inputs()):
        rows.append({'id':f'h{n:05d}','values':{k:x[k] for k in ('p0','z0','p1','z1')},
                     'group':x['group'].replace('repeat','replay'),
                     'reset_visibility':'decrease' if x['p1']<x['z0'] else 'no_decrease',
                     'order':list(x['order'])})
    return rows

def summarize(rule,group,scores):
    errors=[x[0] for x in scores];branches=[d for _,ds in scores for d in ds]
    return {'rule':rule,'group':group,'histories':len(scores),'exact':sum(e==0 for e in errors),
            'undercount':sum(e<0 for e in errors),'overcount':sum(e>0 for e in errors),
            'max_under_units':max([0]+[-e for e in errors]),'max_over_units':max([0]+errors),
            'admission_branches':len(branches),'admitted':sum(d['admitted'] for d in branches),
            'excess_branches':sum(d['excess']>0 for d in branches),'max_excess_units':max(d['excess'] for d in branches),
            'feasible_refusals':sum(d['feasible_refusal'] for d in branches),
            'local_deficit_branches':sum(d['local_balance']<0 for d in branches)}

CONTROL_INPUTS=(
 ('visible_reset',(1,2,0,1),('P0','T0','P1','T1')),
 ('hidden_reset',(1,1,2,2),('P0','T0','P1','T1')),
 ('late_old_progress',(0,2,1,2),('T0','P1','T1','P0')),
 ('equal_values',(1,1,1,1),('P0','T0','P1','T1')),
 ('zero_use',(0,0,0,0),('P0','T0','P1','T1')),
 ('exact_replay',(1,2,1,2),('T0','P1','T0','P0','T1')),
 ('missing_final',(1,2,1,2),('P0','T0','P1')),
)

def compare(root):
    study=Path(__file__).resolve().parent
    freeze=json.loads((study/'independent_freeze.json').read_text())
    assert hashlib.sha256((study/'independent_spec.py').read_bytes()).hexdigest()==freeze['source_sha256']
    plan_freeze=json.loads((study/'plan_freeze.json').read_text())
    assert hashlib.sha256((study/'plan.md').read_bytes()).hexdigest()==plan_freeze['plan_sha256']
    inputs=json.loads((root/'inputs.json').read_text());histories=expected_inputs()
    assert inputs['rules']==list(spec.RULES) and inputs['histories']==histories
    assert len(histories)==5184
    stats=Counter();group_names=('ALL','base','replay_T0','replay_T1','decrease','no_decrease')
    buckets={(r,g):[] for r in spec.RULES for g in group_names};pairs={r:Counter() for r in spec.RULES};witnesses={}
    with gzip.open(root/'traces.jsonl.gz','rt') as stream:
        for h in histories:
            z=h['values']['z0']+h['values']['z1']
            for rule in spec.RULES:
                actual=json.loads(next(stream));expected=expected_trace(h,rule)
                assert actual==expected,('trace mismatch',h['id'],rule)
                stats['rule_histories']+=1;stats['steps']+=len(expected['steps']);stats['state_records']+=len(expected['steps'])+1
                stats['admission_branches']+=len(expected['decisions']);stats['duplicate_deliveries']+=sum(e['duplicate'] for e in expected['steps'])
                for group in ('ALL',h['group'],h['reset_visibility']):buckets[rule,group].append((expected['final_error'],expected['decisions']))
                for d in expected['decisions']:
                    # Direct feasible-demand calculation, independent of EpochMax simulation.
                    baseline=d['capacity']-z>=d['demand']
                    key={ (True,True):'both_admit',(False,False):'both_refuse',
                          (True,False):'only_rule_admits',(False,True):'only_epochmax_admits'}[d['admitted'],baseline]
                    pairs[rule][key]+=1
                conditions={'undercount':expected['final_error']<0,'overcount':expected['final_error']>0,
                            'excess':any(d['excess'] for d in expected['decisions']),
                            'feasible_refusal':any(d['feasible_refusal'] for d in expected['decisions'])}
                for label,occurs in conditions.items():
                    key=rule+':'+label
                    if occurs and key not in witnesses:witnesses[key]={'history':h,'trace':expected}
        assert next(stream,None) is None,'extra trace'
    expected_summaries=[summarize(r,g,buckets[r,g]) for r in spec.RULES for g in group_names]
    with (root/'summary.csv').open(newline='') as f:
        actual_summaries=[{k:v if k in ('rule','group') else int(v) for k,v in row.items()} for row in csv.DictReader(f)]
    assert actual_summaries==expected_summaries,'summary mismatch'
    assert json.loads((root/'paired.json').read_text())=={r:dict(x) for r,x in pairs.items()},'paired mismatch'
    assert json.loads((root/'witnesses.json').read_text())==witnesses,'first witness mismatch'
    controls=[]
    for name,vals,order in CONTROL_INPUTS:
        h={'id':name,'values':dict(zip(('p0','z0','p1','z1'),vals)),'order':list(order),'primary':name!='missing_final'}
        controls.append({'history':h,'results':[expected_trace(h,r) for r in spec.RULES]})
    assert json.loads((root/'controls.json').read_text())==controls,'control mismatch'
    checks=json.loads((root/'checks.json').read_text())
    assert checks['counts']==dict(stats)
    assert checks=={'passed':True,'counts':dict(stats),'input_histories':5184,'summary_rows':30,
                    'control_rule_rows':35,'witnesses':len(witnesses),'source_order_formula_checked':True,
                    'epochmax_exact_checked':True,'duplicate_no_change_checked':True,'missing_final_gate_checked':True}
    # Check closed-form endpoints separately from delivery-prefix evaluation.
    assert all(expected_trace(h,'GlobalMax')['final_error']==-min(h['values']['z0'],h['values']['z1']) for h in histories)
    assert all(expected_trace(h,'SourceOrderDrop')['final_error']==(0 if h['values']['p1']<h['values']['z0'] else -h['values']['z0']) for h in histories)
    assert all(expected_trace(h,'EpochMax')['final_error']==0 for h in histories)
    return {'passed':True,'input_histories':5184,**dict(stats),'summary_rows':30,'paired_rules':5,
            'control_rule_rows':35,'witnesses':len(witnesses),'full_state_and_decision_comparison':True,
            'source_and_global_closed_forms':True,'independent_source_sha256':freeze['source_sha256'],
            'all_summary':[{k:v for k,v in s.items() if k!='group'} for s in expected_summaries if s['group']=='ALL']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--results',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=compare(args.results);args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='all_summary'},sort_keys=True))
