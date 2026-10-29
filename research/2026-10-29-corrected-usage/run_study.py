"""Finite corrected-charge comparison. Python standard library only."""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import platform
import resource
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RULES = ['Net', 'GlobalClamp', 'ItemClamp', 'ArrivalReplace', 'MaxReplace', 'RevisionReplace']
IDS = ['A1', 'A2', 'B1', 'B2']
MULTISETS = [('none', IDS), ('repeat_A2', ['A1','A2','A2','B1','B2']),
             ('repeat_B2', ['A1','A2','B1','B2','B2'])]


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')


def reports(values):
    out = {}
    for i, item in enumerate('AB'):
        u, v = values[2*i:2*i+2]
        for rev, value, delta in [(1,u,u),(2,v,v-u)]:
            eid = item+str(rev)
            out[eid] = dict(id=eid, item=i, revision=rev, value=value, delta=delta)
    return out


def directions(values):
    def sign(a,b):
        return 'down' if b<a else 'up' if b>a else 'equal'
    return sign(values[0],values[1])+'_'+sign(values[2],values[3])


def generate_inputs():
    inputs=[]
    for values in itertools.product(range(3), repeat=4):
        for group, multiset in MULTISETS:
            for order in sorted(set(itertools.permutations(multiset))):
                inputs.append(dict(id=len(inputs), values=list(values), duplicate_group=group,
                                   correction_group=directions(values), order=list(order)))
    assert len(inputs)==11664
    return inputs


def evaluate(case, rule, finality=True):
    # The update loop consumes one received record at a time. Only the scorer uses Z.
    r=reports(case['values'])
    seen=set(); q=0
    items=[0,0] if rule not in ('Net','GlobalClamp') else []
    revisions=[0,0] if rule=='RevisionReplace' else []
    states=[]
    def snapshot(eid, duplicate):
        return dict(event=eid, duplicate=duplicate, seen=sorted(seen), q=q,
                    items=items.copy(), revisions=revisions.copy())
    states.append(snapshot(None,False))
    for eid in case['order']:
        e=r[eid]; duplicate=eid in seen
        if not duplicate:
            seen.add(eid); i=e['item']
            if rule=='Net': q+=e['delta']
            elif rule=='GlobalClamp': q=max(0,q+e['delta'])
            elif rule=='ItemClamp': items[i]=max(0,items[i]+e['delta'])
            elif rule=='ArrivalReplace': items[i]=e['value']
            elif rule=='MaxReplace': items[i]=max(items[i],e['value'])
            elif rule=='RevisionReplace':
                if e['revision']>revisions[i]:
                    revisions[i]=e['revision']; items[i]=e['value']
            else: raise ValueError(rule)
            if items: q=sum(items)
        states.append(snapshot(eid,duplicate))
    complete=seen==set(IDS)
    gate=complete and finality
    z=case['values'][1]+case['values'][3]
    branches=[]
    for slack,b in itertools.product(range(3),(1,2)):
        cap=z+slack
        admitted=gate and q+b<=cap
        charge=z+(b if admitted else 0)
        branches.append(dict(cap=cap, demand=b, admitted=admitted, final_charge=charge,
                             excess=max(0,charge-cap), feasible_refusal=not admitted and z+b<=cap,
                             local_balance=cap-q-(b if admitted else 0)))
    score=dict(error=q-z, under=q<z, exact=q==z, over=q>z,
               any_negative=any(s['q']<0 for s in states),
               min_q=min(s['q'] for s in states),
               excess_case=any(b['excess']>0 for b in branches),
               excess_branches=sum(b['excess']>0 for b in branches),
               max_excess=max(b['excess'] for b in branches),
               feasible_refusal_case=any(b['feasible_refusal'] for b in branches),
               feasible_refusal_branches=sum(b['feasible_refusal'] for b in branches),
               admitted=sum(b['admitted'] for b in branches))
    return dict(case_id=case['id'],rule=rule,states=states,closure=dict(external_finality=finality,
                all_reports=complete,passed=gate),true_charge=z,branches=branches,score=score)


def new_summary(rule, group):
    return dict(rule=rule,group=group,cases=0,branches=0,under=0,exact=0,over=0,
                any_negative=0,excess_case=0,excess_branches=0,feasible_refusal_case=0,
                feasible_refusal_branches=0,admitted=0,max_over=0,max_under=0,max_excess=0,min_q=0)


def add_summary(s,t):
    v=t['score']; s['cases']+=1; s['branches']+=len(t['branches'])
    for k in ['under','exact','over','any_negative','excess_case','excess_branches',
              'feasible_refusal_case','feasible_refusal_branches','admitted']:
        s[k]+=int(v[k])
    s['max_over']=max(s['max_over'],v['error'])
    s['max_under']=max(s['max_under'],-v['error'])
    s['max_excess']=max(s['max_excess'],v['max_excess'])
    s['min_q']=min(s['min_q'],v['min_q'])


def controls():
    fixtures=[('early_credit',[2,0,0,0],['A2','A1','B1','B2']),
              ('late_original_up',[0,2,0,0],['A2','A1','B1','B2']),
              ('offset_across_items',[2,0,2,2],['B1','A2','A1','B2']),
              ('equal_revisions',[1,1,1,1],['A2','B2','A1','B1']),
              ('zero_values',[0,0,0,0],['A1','A2','B1','B2']),
              ('exact_replay',[2,0,0,2],['A2','A2','B2','A1','B1'])]
    named=[]
    for name,values,order in fixtures:
        case=dict(id=name,values=values,order=order)
        named.append(dict(input=case,traces=[evaluate(case,r) for r in RULES]))
    boundary=[]
    for name,order,finality in [('missing_report',['A1','A2','B1'],True),
                                ('open_period',IDS,False)]:
        case=dict(id=name,values=[2,0,0,2],order=order)
        boundary.append(dict(input=case,traces=[evaluate(case,r,finality) for r in RULES]))
    return dict(named=named,boundary=boundary)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',required=True)
    args=parser.parse_args(); out=Path(args.out)
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    out.mkdir(parents=True,exist_ok=False)
    started=datetime.now(timezone.utc).isoformat(); wall=time.monotonic(); cpu=time.process_time()
    inputs=generate_inputs(); dump(out/'inputs.json',inputs)
    summaries={}; witnesses={}
    paired={r:dict(rule=r,reference='Net',cases=0,q_lower=0,q_equal=0,q_higher=0,
                  decision_differences=0,extra_admissions=0,fewer_admissions=0) for r in RULES}
    clamp_pair=dict(reference='GlobalClamp',rule='ItemClamp',cases=0,q_lower=0,q_equal=0,
                    q_higher=0,max_gap=0,decision_differences=0,extra_admissions=0,fewer_admissions=0)
    state_count=0; step_count=0; branch_count=0; hypothesis=dict(H1=True,H2=True,H3=True,H4=True)
    with (out/'traces.jsonl.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=6) as gz:
            for case in inputs:
                ts={r:evaluate(case,r) for r in RULES}
                for rule,t in ts.items():
                    gz.write((json.dumps(t,sort_keys=True,separators=(',',':'))+'\n').encode())
                    state_count+=len(t['states']);step_count+=len(case['order']);branch_count+=6
                    for group in ['all','duplicate:'+case['duplicate_group'],'correction:'+case['correction_group']]:
                        k=(rule,group)
                        if k not in summaries: summaries[k]=new_summary(rule,group)
                        add_summary(summaries[k],t)
                    for kind in ['under','over','any_negative','excess_case','feasible_refusal_case']:
                        k=rule+':'+kind
                        if t['score'][kind] and k not in witnesses:
                            witnesses[k]=dict(input=case,trace=t)
                    p=paired[rule];p['cases']+=1
                    gap=t['states'][-1]['q']-ts['Net']['states'][-1]['q']
                    p['q_lower' if gap<0 else 'q_higher' if gap>0 else 'q_equal']+=1
                    for b,n in zip(t['branches'],ts['Net']['branches']):
                        p['decision_differences']+=int(b['admitted']!=n['admitted'])
                        p['extra_admissions']+=int(b['admitted'] and not n['admitted'])
                        p['fewer_admissions']+=int(n['admitted'] and not b['admitted'])
                cp=clamp_pair;cp['cases']+=1
                gap=ts['ItemClamp']['states'][-1]['q']-ts['GlobalClamp']['states'][-1]['q']
                cp['q_lower' if gap<0 else 'q_higher' if gap>0 else 'q_equal']+=1
                cp['max_gap']=max(cp['max_gap'],gap)
                for b,g in zip(ts['ItemClamp']['branches'],ts['GlobalClamp']['branches']):
                    cp['decision_differences']+=int(b['admitted']!=g['admitted'])
                    cp['extra_admissions']+=int(b['admitted'] and not g['admitted'])
                    cp['fewer_admissions']+=int(g['admitted'] and not b['admitted'])
                hypothesis['H1'] &= all(ts[r]['score']['exact'] and not ts[r]['score']['excess_case']
                                       and not ts[r]['score']['feasible_refusal_case'] for r in ('Net','RevisionReplace'))
                hypothesis['H2'] &= gap>=0 and all(not ts[r]['score']['under'] for r in ('GlobalClamp','ItemClamp'))
                expected_max=sum(max(case['values'][i],case['values'][i+1]) for i in (0,2))
                hypothesis['H3'] &= ts['MaxReplace']['states'][-1]['q']==expected_max
                # A separate prefix identity, independent of clamped state, within the runner.
                rr=reports(case['values']); seen=set(); net=0; low=0; nets=[0,0]; lows=[0,0]
                for k,eid in enumerate(case['order'],1):
                    if eid not in seen:
                        seen.add(eid);e=rr[eid];net+=e['delta'];low=min(low,net)
                        nets[e['item']]+=e['delta'];lows[e['item']]=min(lows[e['item']],nets[e['item']])
                    hypothesis['H4'] &= ts['GlobalClamp']['states'][k]['q']==net-low
                    hypothesis['H4'] &= ts['ItemClamp']['states'][k]['q']==sum(nets)-sum(lows)
                if case['id']%500==0:
                    assert time.monotonic()-wall<300,'periodic wall bound'
                    assert sum(p.stat().st_size for p in out.iterdir())<200_000_000,'periodic output bound'
    rows=[summaries[k] for k in sorted(summaries)]
    with (out/'summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    dump(out/'paired.json',dict(against_net=list(paired.values()),item_vs_global=clamp_pair))
    dump(out/'witnesses.json',witnesses)
    ctl=controls();dump(out/'controls.json',ctl)
    assert all(not t['closure']['passed'] and not any(b['admitted'] for b in t['branches'])
               for c in ctl['boundary'] for t in c['traces'])
    assert all(hypothesis.values())
    assert (state_count,step_count,branch_count)==(408240,338256,419904)
    check=dict(passed=True,input_histories=len(inputs),rules=len(RULES),rule_cases=len(inputs)*len(RULES),
               state_records=state_count,delivery_steps=step_count,decision_branches=branch_count,
               summary_rows=len(rows),named_control_rule_cases=36,boundary_control_rule_cases=12,
               boundary_decisions=72,hypotheses_checked=hypothesis,witnesses=len(witnesses))
    dump(out/'checks.json',check)
    scientific=sorted(out.iterdir())
    size=sum(p.stat().st_size for p in scientific)
    elapsed=time.monotonic()-wall
    assert elapsed<300 and size<200_000_000
    env=dict(started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
             python=sys.version,platform=platform.platform(),machine=platform.machine(),
             cpu_seconds=time.process_time()-cpu,wall_seconds=elapsed,scientific_bytes=size,
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             seed=None,external_calls=0,model_calls=0,peak_memory_measured=False,
             bounds=dict(cpu_seconds=120,periodic_wall_seconds=300,periodic_output_bytes=200_000_000))
    dump(out/'environment.json',env)
    print(json.dumps(check,sort_keys=True));print(json.dumps(env,sort_keys=True))


if __name__=='__main__': main()
