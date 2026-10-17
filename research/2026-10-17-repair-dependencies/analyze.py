"""Exact regression corpus for the frozen four-field repair model."""
import argparse,csv,gzip,hashlib,itertools,json
from pathlib import Path
POLICIES=['replace','patch','refresh_cas','replan_cas','dependency_guard','source_only_guard']
OUTCOMES=['permission_violation','source_violation','semantic_invalid','collateral','bad_union']
NUMERIC=['success','read_denied','exhausted','rounds','attempts','rejections','harmless_rejections','background_writes']+OUTCOMES
EXPECTED={'attempt_budgets':[1,2,3],'writes_per_gap':[0,1,2],'fields':['A','X','Y','U'],'background_fields':['A','X','U'],'policies':POLICIES,'initial_permission':1,'initial_target':'one_minus_X','task':'Y_equals_precommit_X_when_precommit_A_is_one','revision':'atomic_nonreused_integer','unused_suffix':'not_executed_but_assignment_counted','random_sampling':False}
BG=[0,1,3]
def validate(c):
    def same(a,b):
        if type(a) is not type(b):return False
        if isinstance(b,dict):return a.keys()==b.keys() and all(same(a[k],v) for k,v in b.items())
        if isinstance(b,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
        return a==b
    if not same(c,EXPECTED):raise ValueError('Configuration differs from the frozen model')
    return c

def run(policy,initial,program):
    if policy not in POLICIES:raise ValueError('Unknown policy')
    s=list(initial);v=0;events=[];original=list(initial)
    r={k:0 for k in NUMERIC};r.update(decision=None,before_effect=None,collateral_fields=[])
    for index,word in enumerate(program):
        rn=index+1;r['rounds']=rn;read=s.copy();rv=v
        events.append({'kind':'read','round':rn,'state':read,'revision':rv})
        if policy in ['replan_cas','dependency_guard','source_only_guard'] and not read[0]:
            r['decision']='read_denied';r['read_denied']=1
            events.append({'kind':'deny','round':rn,'state':s.copy(),'revision':v});break
        candidate=original[1] if policy in ['replace','patch','refresh_cas'] else read[1]
        for field in word:
            before=s.copy();s[BG[field]]^=1;v+=1;r['background_writes']+=1
            events.append({'kind':'background','round':rn,'field':field,'before':before,'after':s.copy(),'revision':v})
        r['attempts']+=1
        if policy in ['replace','patch']:guard=True
        elif policy in ['refresh_cas','replan_cas']:guard=v==rv
        elif policy=='dependency_guard':guard=s[0]==read[0] and s[1]==read[1]
        else:guard=s[1]==read[1]
        safe=s[0]==1 and candidate==s[1]
        events.append({'kind':'guard','round':rn,'candidate':candidate,'passed':guard,'valid_y_only_effect':safe,'state':s.copy(),'revision':v})
        if not guard:
            r['rejections']+=1;r['harmless_rejections']+=int(safe)
            if rn==len(program):r['decision']='exhausted';r['exhausted']=1
            continue
        before=s.copy();r['before_effect']=before
        if policy=='replace':s=original.copy()
        s[2]=candidate;v+=1
        r['permission_violation']=int(before[0]==0);r['source_violation']=int(candidate!=before[1]);r['semantic_invalid']=int(not safe)
        r['collateral_fields']=[EXPECTED['fields'][i] for i in [0,1,3] if s[i]!=before[i]]
        r['collateral']=int(bool(r['collateral_fields']));r['bad_union']=int(bool(r['semantic_invalid'] or r['collateral']))
        r['success']=1;r['decision']='success'
        events.append({'kind':'commit','round':rn,'before':before,'after':s.copy(),'revision':v});break
    assert r['decision'] is not None
    r.update(final_state=s,final_revision=v,events=events)
    assert r['success']+r['read_denied']+r['exhausted']==1
    assert r['attempts']==r['rejections']+r['success']
    assert v==r['background_writes']+r['success']
    assert r['bad_union']<=r['success'] and r['harmless_rejections']<=r['rejections']
    assert r['semantic_invalid']==int(bool(r['permission_violation'] or r['source_violation']))
    if policy in ['replan_cas','dependency_guard']:assert r['bad_union']==0
    if policy!='replace':assert r['collateral']==0
    return r

def words(b):return sorted(w for n in range(b+1) for w in itertools.product(range(3),repeat=n))
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,default=Path('.'));ap.add_argument('--output-dir',type=Path,default=Path('.'));a=ap.parse_args()
    cfg=validate(json.loads((a.input_dir/'config.json').read_text()));manifest=json.loads((a.input_dir/'input_manifest.json').read_text())
    for n,h in manifest['sha256'].items():assert hashlib.sha256((a.input_dir/n).read_bytes()).hexdigest()==h,n
    out=a.output_dir;out.mkdir(parents=True,exist_ok=True);aggregates=[];witnesses=[];pairs=[];count=0;scenario_count=0
    with (out/'traces.jsonl.gz').open('wb') as raw:
      with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
       for K,b in itertools.product(cfg['attempt_budgets'],cfg['writes_per_gap']):
        allowed=words(b);expected=4*len(allowed)**K;best={};seen=0
        totals={p:{'K':K,'b':b,'policy':p,'assignments':expected,**{n:0 for n in NUMERIC}} for p in POLICIES}
        paired={'K':K,'b':b,'assignments':expected,'dependency_success_cas_exhausted':0,'unrelated_only':0,'returned_dependency':0,'replace_collateral_patch_none':0}
        for x,u in itertools.product([0,1],repeat=2):
         initial=(1,x,1-x,u)
         for program in itertools.product(allowed,repeat=K):
          seen+=1;scenario_count+=1;cases={}
          for policy in POLICIES:
           result=run(policy,initial,program);case={'K':K,'b':b,'initial':initial,'program':program,'policy':policy,**result};cases[policy]=result
           z.write((json.dumps(case,sort_keys=True,separators=(',',':'))+'\n').encode());count+=1
           for n in NUMERIC:totals[policy][n]+=result[n]
           key=(result['background_writes'],result['rounds'],initial,program)
           for outcome in OUTCOMES:
            if result[outcome] and ((policy,outcome) not in best or key<best[policy,outcome][0]):best[policy,outcome]=(key,case)
          if cases['dependency_guard']['success'] and cases['replan_cas']['exhausted']:
           paired['dependency_success_cas_exhausted']+=1
           if all(w and all(f==2 for f in w) for w in program):paired['unrelated_only']+=1
           if any(f in [0,1] for f in program[0]) and all(w and w.count(0)%2==0 and w.count(1)%2==0 for w in program):paired['returned_dependency']+=1
          paired['replace_collateral_patch_none']+=int(cases['replace']['collateral'] and not cases['patch']['collateral'])
        assert seen==expected
        for t in totals.values():
            assert t['success']+t['read_denied']+t['exhausted']==expected
            if b==0:assert t['success']==expected and t['bad_union']==t['rejections']==0
        assert paired['unrelated_only']+paired['returned_dependency']<=paired['dependency_success_cas_exhausted']
        aggregates.extend(totals.values());pairs.append(paired)
        for (policy,outcome),(key,case) in sorted(best.items()):witnesses.append({'outcome':outcome,'minimum_consumed_writes':key[0],'case':case})
    with (out/'results.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(aggregates[0]));wr.writeheader();wr.writerows(aggregates)
    dump(out/'paired_results.json',pairs);dump(out/'witnesses.json',witnesses)
    h={'H1':all(t['semantic_invalid']==0 for t in aggregates if t['policy']=='refresh_cas' and t['K']==1) and any(t['semantic_invalid']>0 for t in aggregates if t['policy']=='refresh_cas' and t['K']>1),'H2':all(t['bad_union']==0 for t in aggregates if t['policy'] in ['replan_cas','dependency_guard']),'H3':any(t['permission_violation'] for t in aggregates if t['policy']=='source_only_guard'),'H4':any(t['replace_collateral_patch_none'] for t in pairs) and any(t['semantic_invalid'] for t in aggregates if t['policy']=='patch'),'H5':any(t['unrelated_only'] for t in pairs) and any(t['returned_dependency'] for t in pairs)}
    summary={'status':'COMPLETE','settings':9,'policy_rows':len(aggregates),'scenario_assignments':scenario_count,'policy_assignments':count,'witnesses':len(witnesses),'hypotheses':h,'scope':'Exact fixed synthetic corpus; not real website rates or live agent trials','input_sha256':{n:hashlib.sha256((a.input_dir/n).read_bytes()).hexdigest() for n in ['analysis_plan.md','config.json','input_manifest.json']}}
    dump(out/'summary.json',summary);print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
