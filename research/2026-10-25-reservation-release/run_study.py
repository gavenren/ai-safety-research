"""Exact finite reservation-release audit. No network or provider calls."""
import argparse, copy, csv, gzip, hashlib, itertools, json, platform, resource, sys, time
from pathlib import Path
RULES = ('Timeout','ZeroObservation','FenceOnly','ClosureCertificate','TerminalOnly')
EVENTS = ('A','E','T','O','F','D')

def audit(s,c,a):
    if s['actual_a']: liability=a
    elif s['resolved']: liability=0
    elif s['accepted'] or not s['fenced']: liability=a
    else: liability=0
    available=c-s['hold']-s['booked_a']-s['booked_b']
    return {'liability':liability,'available':available,
            'actual_excess':max(0,s['actual_a']+s['booked_b']-c),
            'exposure_excess':max(0,liability+s['booked_b']-c),
            'uncovered':max(0,liability-s['hold']-s['booked_a']),
            'deficit':max(0,-available)}

def simulate(x,rule):
    a,b,c=x['a'],x['b'],x['capacity']
    s={'actual_a':0,'hold':a,'booked_a':0,'booked_b':0,'accept_attempted':False,
       'accepted':False,'resolved':False,'fenced':False,'settled':False,
       'observation':None,'fence_receipt':None,'decision':None,'settlement_count':0}
    initial={'state':copy.deepcopy(s),'audit':audit(s,c,a)};trace=[]
    for event in x['schedule']:
        before={'state':copy.deepcopy(s),'audit':audit(s,c,a)}
        if event=='A':
            s['accept_attempted']=True;s['accepted']=not s['fenced']
        elif event=='E':
            s['resolved']=True
            s['actual_a']=a if s['accepted'] and x['branch']=='charge' else 0
        elif event=='T':
            assert s['resolved'] and not s['settled']
            s['hold']=0;s['booked_a']=s['actual_a'];s['settled']=True;s['settlement_count']+=1
        elif event=='O':s['observation']=s['actual_a']
        elif event=='F':
            s['fenced']=True
            s['fence_receipt']={'accepted':s['accepted'],'resolved':s['resolved'],'charged':s['actual_a'],
              'certificate':not s['accepted'] or (s['resolved'] and s['actual_a']==0)}
        elif event=='D':
            truth=before['audit'];held=s['hold']
            release=(held>0 and (rule=='Timeout' or
                (rule=='ZeroObservation' and s['observation']==0) or
                (rule=='FenceOnly' and s['fence_receipt'] is not None) or
                (rule=='ClosureCertificate' and s['fence_receipt'] is not None and s['fence_receipt']['certificate'])))
            if release:s['hold']=0
            admit=audit(s,c,a)['available']>=b
            if admit:s['booked_b']=b
            s['decision']={'released':bool(release),'held_before':held,
              'premature':bool(release and truth['liability']>0),'b_accepted':admit,
              'safe_feasible':truth['liability']+b<=c,
              'safe_feasible_refusal':bool(not admit and truth['liability']+b<=c)}
        after={'state':copy.deepcopy(s),'audit':audit(s,c,a)}
        assert s['hold'] in (0,a) and s['booked_a'] in (0,a) and s['booked_b'] in (0,b)
        assert s['actual_a']>=before['state']['actual_a']
        assert after['audit']['available']+s['hold']+s['booked_a']+s['booked_b']==c
        trace.append({'event':event,'before':before,'after':after})
    assert s['settlement_count']==1 and s['settled'] and s['hold']==0 and s['booked_a']==s['actual_a']
    scores={}
    for field in ('actual_excess','exposure_excess','uncovered','deficit'):
        hits=[e for e in trace if e['after']['audit'][field]>0]
        scores[field+'_case']=bool(hits)
        scores[field+'_max']=max(e['after']['audit'][field] for e in trace)
        scores[field+'_first']=hits[0]['event'] if hits else None
    scores.update({'exposure_without_final_actual':bool(scores['exposure_excess_case'] and not trace[-1]['after']['audit']['actual_excess']),
       'premature_refund':s['decision']['premature'],'b_accepted':s['decision']['b_accepted'],
       'b_refused':not s['decision']['b_accepted'],'safe_feasible_refusal':s['decision']['safe_feasible_refusal'],
       'released':s['decision']['released'],'a_blocked':not s['accepted'],
       'a_charged':s['actual_a']>0,'settlements':s['settlement_count']})
    assert scores['actual_excess_case']==scores['deficit_case']
    return {'input':x,'rule':rule,'initial':initial,'trace':trace,'final':trace[-1]['after'],'scores':scores}

# Controls and expected decisions are declared before the first experiment.
# Every control has a=b=C=1. Tuple gives B acceptance in RULES order.
CONTROLS=(
 ('accepted_before_fence','A O F D E T','charge',(1,1,1,0,0),(1,1,1,0,0)),
 ('fence_before_accept','F A O D E T','charge',(1,1,1,1,0),(0,0,0,0,0)),
 ('terminal_before_decision','A E T O D F','charge',(0,0,0,0,0),(0,0,0,0,0)),
 ('zero_observation_late_charge','O D A E T F','charge',(1,1,0,0,0),(1,1,0,0,0)),
 ('zero_resolution_before_fence','A E F O D T','zero',(1,1,1,1,0),(0,0,0,0,0)),
 ('zero_resolution_after_fence','A F E O D T','zero',(1,1,1,0,0),(0,0,0,0,0)),
 ('exposure_hidden_by_zero','A O F D E T','zero',(1,1,1,0,0),(0,0,0,0,0)),
)

def control_check():
    out=[]
    for name,order,branch,admits,breaches in CONTROLS:
        for i,rule in enumerate(RULES):
            x={'a':1,'b':1,'capacity':1,'branch':branch,'schedule':order.split()};r=simulate(x,rule)
            assert r['scores']['b_accepted']==bool(admits[i]),(name,rule,'admit')
            assert r['scores']['actual_excess_case']==bool(breaches[i]),(name,rule,'breach')
            if name=='exposure_hidden_by_zero':assert r['scores']['exposure_without_final_actual']==bool(admits[i])
            out.append({'name':name,'rule':rule,'expected_b_accepted':bool(admits[i]),'expected_actual_breach':bool(breaches[i]),'trace':r,'pass':True})
    return out

def worlds():
    schedules=sorted(p for p in itertools.permutations(EVENTS) if p.index('A')<p.index('E')<p.index('T') and p.index('O')<p.index('D'))
    assert len(schedules)==60
    items=[]
    for a,b,c,branch in itertools.product((1,2),(1,2),(1,2,3,4),('charge','zero')):
        if a>c:continue
        for schedule in schedules:items.append({'a':a,'b':b,'capacity':c,'branch':branch,'schedule':list(schedule)})
    assert len(items)==1680
    return items

def dump(path,obj):path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def main(out):
    out.mkdir(parents=True,exist_ok=False)
    cpu,wall=time.process_time(),time.monotonic()
    resource.setrlimit(resource.RLIMIT_CPU,(120,125))
    try:
        control=control_check();dump(out/'controls.json',control)
        inputs=worlds();dump(out/'inputs.json',inputs)
        records=[];checks={'terminal_before_d':0,'fence_before_a':0,'complete_rule_cases':0,'ample_budget_cases':0,'branch_prefix_pairs':0}
        for j,x in enumerate(inputs):
            group=[]
            for rule in RULES:
                r=simulate(x,rule);r['world_id']=f'w{j:04d}';records.append(r);group.append(r)
                p=x['schedule']
                if p.index('F')<p.index('A'):assert r['scores']['a_blocked'];checks['fence_before_a']+=1
                if rule in ('ClosureCertificate','TerminalOnly'):
                    assert not r['scores']['actual_excess_case'] and not r['scores']['exposure_excess_case'] and not r['scores']['uncovered_case'];checks['complete_rule_cases']+=1
                if x['capacity']>=x['a']+x['b']:
                    assert not r['scores']['actual_excess_case'] and not r['scores']['exposure_excess_case'];checks['ample_budget_cases']+=1
            if x['schedule'].index('T')<x['schedule'].index('D'):
                assert len({r['scores']['b_accepted'] for r in group})==1;checks['terminal_before_d']+=1
            if j%100==0:
                assert time.monotonic()-wall<300
                assert sum(f.stat().st_size for f in out.iterdir() if f.is_file())<200_000_000
        keyed={(r['input']['a'],r['input']['b'],r['input']['capacity'],r['input']['branch'],tuple(r['input']['schedule']),r['rule']):r for r in records}
        for key,r in keyed.items():
            if key[3]!='charge':continue
            twin=key[:3]+('zero',)+key[4:];t=keyed[twin]
            k=r['input']['schedule'].index('E')
            assert r['trace'][:k]==t['trace'][:k];checks['branch_prefix_pairs']+=1
        with (out/'traces.jsonl.gz').open('wb') as f:
            with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as g:
                for r in records:g.write((json.dumps(r,sort_keys=True,separators=(',',':'))+'\n').encode())
        bools=[k for k,v in records[0]['scores'].items() if isinstance(v,bool)]
        maximums=[k for k in records[0]['scores'] if k.endswith('_max')]
        rows=[]
        for rule in RULES:
            for branch in ('all','charge','zero'):
                selected=[r for r in records if r['rule']==rule and (branch=='all' or r['input']['branch']==branch)]
                row={'rule':rule,'branch':branch,'cases':len(selected)}
                row.update({k:sum(r['scores'][k] for r in selected) for k in bools})
                row.update({k:max(r['scores'][k] for r in selected) for k in maximums});rows.append(row)
        with (out/'summary.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        comparisons=[]
        for left,right in itertools.combinations(RULES,2):
            arows=[r for r in records if r['rule']==left];brows=[r for r in records if r['rule']==right]
            comparisons.append({'left':left,'right':right,'worlds':len(arows),'deltas_right_minus_left':{k:sum(b['scores'][k]-a['scores'][k] for a,b in zip(arows,brows)) for k in bools},'b_decisions_differ':sum(a['scores']['b_accepted']!=b['scores']['b_accepted'] for a,b in zip(arows,brows))})
        dump(out/'paired.json',comparisons)
        witness={}
        for r in records:
            for metric in ('actual_excess_case','exposure_without_final_actual','safe_feasible_refusal','uncovered_case'):
                if r['scores'][metric]:witness.setdefault(r['rule']+'/'+metric,r)
        dump(out/'witnesses.json',witness);dump(out/'checks.json',checks)
        size=sum(f.stat().st_size for f in out.iterdir() if f.is_file());assert size<200_000_000 and time.monotonic()-wall<300
        env={'python':platform.python_version(),'platform':platform.platform(),'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-wall,'result_bytes_before_environment':size,'worlds':len(inputs),'outcomes':len(records),'model_api_calls':0,'seed':None,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        dump(out/'environment.json',env)
        print(json.dumps({'status':'pass','controls':len(control),'checks':checks,'summary_all':[r for r in rows if r['branch']=='all'],'environment':env},indent=2))
    except BaseException as e:
        dump(out/'failure.json',{'type':type(e).__name__,'message':str(e),'elapsed_seconds':time.monotonic()-wall});raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);main(p.parse_args().out)
