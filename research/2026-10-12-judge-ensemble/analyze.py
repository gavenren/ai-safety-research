"""Secondary class-specific majority-vote audit. No model inference."""
from pathlib import Path
import csv, hashlib, itertools, json, platform, time
import numpy as np

BASE = Path(__file__).resolve().parent
SEED = 20261012
DRAWS = 2000

def product_majority(rates):
    """Poisson-binomial tail; each input rate can differ."""
    dist = np.array([1.0])
    for r in rates:
        dist = np.convolve(dist, [1.0-r, r])
    return float(dist[len(rates)//2+1:].sum())

def save_csv(name, records):
    with (BASE/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(records[0])); w.writeheader(); w.writerows(records)

def main():
    start=time.perf_counter()
    rows=list(csv.DictReader((BASE/'data_labels.csv').open()))
    models=sorted({r['model'] for r in rows})
    assert len(models)==5
    grouped={}
    seen=set()
    for r in rows:
        key=(r['dataset'],r['item_id']); full=(*key,r['model'])
        assert full not in seen; seen.add(full)
        ref,pred=int(r['reference']),int(r['prediction'])
        assert ref in (0,1) and pred in (0,1)
        g=grouped.setdefault(key,{'ref':ref,'votes':{}})
        assert g['ref']==ref
        g['votes'][r['model']]=pred
    assert len(grouped)==1398 and len(rows)==6990
    for g in grouped.values(): assert sorted(g['votes'])==models
    datasets=sorted({k[0] for k in grouped})
    assert len(datasets)==7
    bits=np.array(list(itertools.product([0,1],repeat=5)),dtype=int)
    controls=[]
    for name,rates,actual in [('all_correct',[0.0]*5,0.0),('all_wrong',[1.0]*5,1.0),('identical_voters_02',[0.2]*5,0.2)]:
        controls.append(dict(name=name,rates=rates,observed_error=actual,independent_error=product_majority(rates)))
    rates=np.array([0.1,0.2,0.3,0.4,0.6])
    weights=np.prod(np.where(bits==1,rates,1-rates),axis=1)
    controls.append(dict(name='synthetic_product',rates=rates.tolist(),observed_error=float(weights[bits.sum(axis=1)>=3].sum()),independent_error=product_majority(rates)))
    for name,r in [('single_0',0.0),('single_02',0.2),('single_05',0.5),('single_1',1.0)]:
        controls.append(dict(name=name,rates=[r],observed_error=r,independent_error=product_majority([r])))
    (BASE/'results_controls.json').write_text(json.dumps({'controls':controls},indent=2)+'\n')
    rng=np.random.default_rng(SEED)
    cells=[]; patterns=[]; boots=[]; intervals=[]; primary=[]
    panels=list(itertools.combinations(range(5),3))+[tuple(range(5))]
    for dataset in datasets:
      for ref in (0,1):
        error=np.array([[g['votes'][m]!=ref for m in models] for k,g in sorted(grouped.items()) if k[0]==dataset and g['ref']==ref],dtype=int)
        n=len(error); codes=error @ (2**np.arange(4,-1,-1))
        hist=np.bincount(codes,minlength=32)
        for b,c in zip(bits,hist):
            patterns.append(dict(dataset=dataset,reference=ref,pattern=''.join(map(str,b)),count=int(c)))
        for panel in panels:
            sub=error[:,panel]; counts=sub.sum(axis=0); errors=int((sub.sum(axis=1)>len(panel)//2).sum())
            rates=counts/n; actual=errors/n; expected=product_majority(rates)
            cell=dict(dataset=dataset,reference=ref,panel='|'.join(models[j] for j in panel),panel_size=len(panel),n=n,errors=errors,observed_error=actual,independent_error=expected,gap=actual-expected,mean_member_error=float(rates.mean()),best_member_error=float(rates.min()),member_error_counts=json.dumps(counts.tolist(),separators=(',',':')))
            cells.append(cell)
            if len(panel)==5: primary.append(cell)
        sample_counts=rng.multinomial(n,hist/n,size=DRAWS)
        gaps=[]
        for draw,bc in enumerate(sample_counts):
            rates=(bc @ bits)/n
            actual=float(bc[bits.sum(axis=1)>=3].sum()/n)
            expected=product_majority(rates); gap=actual-expected; gaps.append(gap)
            boots.append(dict(dataset=dataset,reference=ref,draw=draw,n=n,pattern_counts=json.dumps(bc.tolist(),separators=(',',':')),observed_error=actual,independent_error=expected,gap=gap))
        lo,hi=np.percentile(gaps,[2.5,97.5],method='linear')
        intervals.append(dict(dataset=dataset,reference=ref,gap=primary[-1]['gap'],lower=float(lo),upper=float(hi)))
    save_csv('results_cells.csv',cells); save_csv('results_patterns.csv',patterns)
    save_csv('results_bootstrap.csv',boots); save_csv('results_intervals.csv',intervals)
    def stats(items):
        gaps=np.array([r['gap'] for r in items])
        return dict(cells=len(items),positive_gap=int((gaps>1e-12).sum()),negative_gap=int((gaps< -1e-12).sum()),zero_gap=int((abs(gaps)<=1e-12).sum()),abs_gap_at_least_5pp=int((abs(gaps)>=.05-1e-12).sum()),mean_observed=float(np.mean([r['observed_error'] for r in items])),mean_independent=float(np.mean([r['independent_error'] for r in items])),mean_gap=float(gaps.mean()),min_gap=float(gaps.min()),max_gap=float(gaps.max()))
    summary=dict(seed=SEED,bootstrap_draws_per_primary_cell=DRAWS,models=models,items=len(grouped),decisions=len(rows),primary=stats(primary),triples=stats([r for r in cells if r['panel_size']==3]),primary_by_reference={str(ref):stats([r for r in primary if r['reference']==ref]) for ref in (0,1)},full_panel_cells=primary)
    (BASE/'results_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    env=dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),seed=SEED,data_sha256=hashlib.sha256((BASE/'data_labels.csv').read_bytes()).hexdigest(),model_inference='None. Fixed saved model outputs only.')
    (BASE/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
    print(json.dumps({'data_rows':len(rows),'items':len(grouped),'point_cells':len(cells),'pattern_rows':len(patterns),'bootstrap_rows':len(boots),'interval_rows':len(intervals),'primary':summary['primary'],'elapsed_seconds':time.perf_counter()-start,'environment':env},indent=2))

if __name__=='__main__': main()
