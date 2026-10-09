"""Exact, synthetic model comparison. Python standard library only."""
import csv
import hashlib
import json
import math
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent
N = 300
REPEATS = (1, 2, 5, 10, 30, 100, 300)
RATES = (0.001, 0.01, 0.05)
RHOS = (0.0, 0.01, 0.1, 0.5)
MODELS = ('beta', 'zero_atom', 'one_atom')
ALPHA = 0.05

def log_p0(p, rho, m, model):
    assert 0 <= p <= 1 and 0 <= rho <= 1
    assert m in REPEATS and N % m == 0 and model in MODELS
    if p == 0: return 0.0
    if p == 1: return -math.inf
    if rho == 0: return N * math.log1p(-p)
    if rho == 1: return (N // m) * math.log1p(-p)
    if model == 'beta':
        c = 1/rho - 1
        a = p*c
        log_s = math.fsum(math.log1p(-a/(c+j)) for j in range(m))
    elif model == 'zero_atom':
        h = p + rho*(1-p)
        # Positive terms avoid cancellation when p is close to one.
        left = math.log(rho) + math.log1p(-p)
        right = math.log(p) + m*(math.log1p(-rho)+math.log1p(-p))
        top, bottom = max(left,right), min(left,right)
        log_s = top + math.log1p(math.exp(bottom-top)) - math.log(h)
    else:
        low = p*(1-rho)
        log_s = math.log1p(-p) + (m-1)*math.log1p(-low)
    return (N // m) * log_s

def p0(p, rho, m, model):
    return math.exp(log_p0(p,rho,m,model))

def boundary(rho, m, model):
    lo, hi = 0.0, 1.0
    for _ in range(70):
        mid = (lo+hi)/2
        if log_p0(mid,rho,m,model) > math.log(ALPHA): lo=mid
        else: hi=mid
    return (lo+hi)/2

def save_csv(name, rows):
    with (ROOT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def main():
    rows=[]
    for p in RATES:
        for rho in RHOS:
            for m in REPEATS:
                effective_n=N/(1+(m-1)*rho)
                for model in MODELS:
                    prob=p0(p,rho,m,model)
                    assert 0<=prob<=1
                    rows.append(dict(p=p,rho=rho,repeats=m,groups=N//m,model=model,
                        zero_failure_probability=prob,independent_probability=(1-p)**N,
                        variance_effective_n=effective_n,
                        effective_n_plugin_probability=math.exp(effective_n*math.log1p(-p))))
    save_csv('results_grid.csv',rows)
    boundaries=[]
    for rho in RHOS:
        for m in REPEATS:
            for model in MODELS:
                u=boundary(rho,m,model)
                assert abs(p0(u,rho,m,model)-ALPHA)<1e-12
                boundaries.append(dict(rho=rho,repeats=m,groups=N//m,model=model,
                    p_boundary=u,probability_at_boundary=p0(u,rho,m,model),
                    probability_at_target=p0(0.01,rho,m,model),
                    target_false_clearance_above_5pct=p0(0.01,rho,m,model)>ALPHA))
    save_csv('results_boundaries.csv',boundaries)
    checks={}
    checks['probabilities_valid']=len(rows)
    checks['boundary_residuals_below_1e_12']=len(boundaries)
    for p in RATES:
        for rho in RHOS:
            var=rho*p*(1-p)
            for model in MODELS:
                assert abs(p0(p,rho,1,model)-(1-p)**N)<1e-12
                assert abs(p0(p,rho,2,model)-((1-p)**2+var)**(N//2))<1e-12
            if rho:
                h=p+rho*(1-p); w=p/h
                low=p*(1-rho); w1=(p-low)/(1-low)
                for mean, second in ((w*h,w*h*h),((1-w1)*low+w1,(1-w1)*low*low+w1)):
                    assert abs(mean-p)<1e-14
                    assert abs(second-p*p-var)<1e-14
                c=1/rho-1; a=p*c; b=(1-p)*c
                assert abs(a/(a+b)-p)<1e-14
                assert abs(a*b/((a+b)**2*(a+b+1))-var)<1e-14
        for m in REPEATS:
            for model in MODELS:
                assert abs(p0(p,0,m,model)-(1-p)**N)<1e-12
                assert abs(p0(p,1,m,model)-(1-p)**(N//m))<1e-12
    checks['moment_and_boundary_controls']='passed'
    for rho in RHOS[1:]:
        for m in REPEATS:
            assert 0 <= p0(math.nextafter(1.0,0.0),rho,m,'zero_atom') <= 1
    checks['near_one_zero_atom_controls']=21
    for rho in RHOS:
        for m in REPEATS:
            for model in MODELS:
                values=[p0(i/1000,rho,m,model) for i in range(1001)]
                assert all(a>=b for a,b in zip(values,values[1:]))
    checks['monotonicity_grid_checks']=len(RHOS)*len(REPEATS)*len(MODELS)*1000
    headline=[r for r in rows if r['p']==0.01 and r['rho']==0.1]
    summary=dict(type='Exact mathematical model study; no observed AI outputs',
        budget=N,grid_rows=len(rows),boundary_rows=len(boundaries),
        baseline_p01=(1-.01)**N,independent_95pct_zero_failure_boundary=1-ALPHA**(1/N),
        plan_sha256=hashlib.sha256((ROOT/'analysis_plan.md').read_bytes()).hexdigest(),
        python=platform.python_version(),checks=checks,headline=headline)
    (ROOT/'results_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='headline'},indent=2))
    print('p=.01, rho=.1: groups,repeats,model,P0,boundary')
    for r in headline:
        print(f"{r['groups']},{r['repeats']},{r['model']},{r['zero_failure_probability']:.9f},{boundary(.1,r['repeats'],r['model']):.9f}")

if __name__=='__main__': main()
