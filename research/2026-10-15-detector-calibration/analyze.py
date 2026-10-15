"""Exact probability audit. Run from this folder with Python 3.14.7."""
from decimal import Decimal as D, getcontext, ROUND_CEILING
from pathlib import Path
from math import comb
import csv, hashlib, json, platform
ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/'config.json').read_text())
getcontext().prec=C['decimal_precision']
ZERO=D(0); ONE=D(1)

def verify_inputs():
    manifest=json.loads((ROOT/'input_manifest.json').read_text())
    for name,expected in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name

def pmf(m,s):
    if s==0:return [ONE]+[ZERO]*m
    if s==1:return [ZERO]*m+[ONE]
    return [D(comb(m,k))*s**k*(1-s)**(m-k) for k in range(m+1)]

def tail(m,k,s):
    return sum(pmf(m,s)[k:],ZERO)

def lower(m,k):
    if k==0:return ZERO,ZERO
    lo,hi=ZERO,ONE
    for _ in range(C['root_bisections']):
        mid=(lo+hi)/2
        if tail(m,k,mid)<=D(C['calibration_error']):lo=mid
        else:hi=mid
    assert tail(m,k,lo)<=D(C['calibration_error'])
    assert tail(m,k,hi)>=D(C['calibration_error'])
    return lo,hi

def length(p0,a,b):
    if a==0:return None
    q=1-p0*a
    if q==0:return 1
    n=max(1,int((b.ln()/q.ln()).to_integral_value(rounding=ROUND_CEILING)))
    while q**n>b:n+=1
    while n>1 and q**(n-1)<=b:n-=1
    assert q**n<=b and (n==1 or q**(n-1)>b)
    return n

def fmt(x):
    if x is None:return ''
    if isinstance(x,D):return format(x,'.30f')
    return x

def write_csv(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
        for r in rows:w.writerow({k:fmt(v) for k,v in r.items()})

def run():
    verify_inputs()
    roots={};boundrows=[]
    for m in C['calibration_sizes']:
        for k in range(m+1):
            lo,hi=lower(m,k); roots[m,k]=lo
            boundrows.append({'m':m,'k':k,'lower_lo':str(lo),'lower_hi':str(hi),'tail_at_lo':str(tail(m,k,lo)) if k else '', 'tail_at_hi':str(tail(m,k,hi)) if k else ''})
    write_csv('results_bounds.csv',boundrows)
    policies={};policyrows=[]
    for ps in C['targets']:
        p0=D(ps); n0=length(p0,ONE,D(C['alpha']))
        for m in C['calibration_sizes']:
            for rule in ['point_estimate','lower_bound']:
                for capmult in C['cap_multipliers']:
                    cap=None if capmult is None else capmult*n0
                    for k in range(m+1):
                        a=D(k)/m if rule=='point_estimate' else roots[m,k]
                        b=D(C['alpha'] if rule=='point_estimate' else C['target_error'])
                        n=length(p0,a,b)
                        launch=n is not None and (cap is None or n<=cap)
                        reason='launched' if launch else ('zero_sensitivity' if n is None else 'over_cap')
                        policies[ps,m,rule,capmult,k]=(n,launch)
                        policyrows.append({'p0':ps,'m':m,'rule':rule,'cap_multiplier':capmult or 'none','cap':cap,'k':k,'s_used':str(a),'target_error':str(b),'required_n':n,'launched':int(launch),'reason':reason})
    write_csv('results_policy.csv',policyrows)
    rows=[]
    for ps in C['targets']:
        p0=D(ps); n0=length(p0,ONE,D(C['alpha']))
        for m in C['calibration_sizes']:
            for ss in C['sensitivities']:
                s=D(ss); weights=pmf(m,s); assert abs(sum(weights)-1)<D('1e-65')
                for ratio in C['failure_rate_multipliers']:
                    p=p0*D(ratio);q=p*s
                    for rule in C['rules']:
                        for capmult in C['cap_multipliers']:
                            cap=None if capmult is None else capmult*n0
                            accept=ZERO;launchprob=ZERO;expected=ZERO;maximum=0
                            if rule in ['point_estimate','lower_bound']:
                                branches=[policies[ps,m,rule,capmult,k] for k in range(m+1)]
                            else:
                                n=length(p0,ONE if rule=='perfect_assumed' else s,D(C['alpha']))
                                ok=n is not None and (cap is None or n<=cap)
                                branches=[(n,ok)]*(m+1)
                            for w,(n,ok) in zip(weights,branches):
                                if ok:
                                    accept+=w*(1-q)**n
                                    launchprob+=w;expected+=w*n
                                    if w>0:maximum=max(maximum,n)
                            if rule in ['perfect_assumed','known_sensitivity']:
                                accept=(1-q)**n if ok else ZERO
                                launchprob=ONE if ok else ZERO
                                expected=D(n) if ok else ZERO
                                maximum=n if ok else 0
                            conditional=None if launchprob==0 else expected/launchprob
                            rows.append({'p0':ps,'m':m,'s':ss,'p_multiplier':ratio,'p':p,'f':'0','rule':rule,'cap_multiplier':capmult or 'none','cap':cap,'acceptance_probability':accept,'launch_probability':launchprob,'no_declaration_probability':1-accept,'expected_target_count':expected,'conditional_target_count':conditional,'max_target_count':maximum})
    assert len(rows)==1296
    write_csv('results_grid.csv',rows)
    boundary=[r for r in rows if r['p_multiplier']=='1']
    counts=[]
    for rule in C['rules']:
        for capmult in ['none',20]:
            cell=[r for r in boundary if r['rule']==rule and r['cap_multiplier']==capmult]
            worst=max(cell,key=lambda r:r['acceptance_probability'])
            counts.append({'rule':rule,'cap_multiplier':capmult,'cases':len(cell),'above_005':sum(r['acceptance_probability']>D('.05') for r in cell),'equal_005':sum(r['acceptance_probability']==D('.05') for r in cell),'maximum_ties_at_saved_precision':[{k:r[k] for k in ['p0','m','s']} for r in cell if fmt(r['acceptance_probability'])==fmt(worst['acceptance_probability'])],'maximum_probability':str(worst['acceptance_probability']),'maximum_at':{k:worst[k] for k in ['p0','m','s']}})
    example=[{k:fmt(v) for k,v in r.items()} for r in rows if r['p0']==C['planned_example']['target'] and r['m']==C['planned_example']['calibration_size'] and r['s']==C['planned_example']['sensitivity']]
    summary={'grid_rows':len(rows),'bounds_rows':len(boundrows),'policy_rows':len(policyrows),'boundary_counts':counts,'planned_example':example,'unconditional_corrected_bound':str(D(C['calibration_error'])+(1-D(C['calibration_error']))*D(C['target_error'])),'input_manifest_sha256':hashlib.sha256((ROOT/'input_manifest.json').read_bytes()).hexdigest()}
    (ROOT/'results_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'environment.json').write_text(json.dumps({'python':platform.python_version(),'implementation':platform.python_implementation(),'platform':platform.system(),'dependencies':'standard library only','decimal_precision':C['decimal_precision'],'root_bisections':C['root_bisections'],'random_sampling':False,'new_model_experiment':False},indent=2)+'\n')
    print(json.dumps({'status':'PASS','grid_rows':len(rows),'bounds_rows':len(boundrows),'policy_rows':len(policyrows),'boundary_counts':counts},indent=2))
if __name__=='__main__':run()
