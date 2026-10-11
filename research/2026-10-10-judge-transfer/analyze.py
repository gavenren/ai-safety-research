"""Audit cross-test-set transfer of binary prevalence correction."""
import csv
import hashlib
import json
import platform
import time
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
MODELS = ['Llama-3.1-8B', 'Mistral-7B', 'OLMo-2-7B', 'Qwen2.5-7B', 'gemma-2-9b']
SETS = ['beavertails', 'xstest', 'ethics', 'wildguard', 'aegis', 'toxicchat', 'toxigen']
SHARES = [.01, .05, .10, .25, .50]
B = 2000
SEED = 20261010

def write_csv(name, rows):
    with (ROOT/name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def summarize(rows):
    eligible = [r for r in rows if r['eligible']]
    return {'cells': len(rows), 'eligible': len(eligible),
            'improved': sum(r['absolute_error_change'] < -1e-12 for r in eligible),
            'worse': sum(r['absolute_error_change'] > 1e-12 for r in eligible),
            'tied': sum(abs(r['absolute_error_change']) <= 1e-12 for r in eligible),
            'clipped_improved': sum(r['clipped_absolute_error_change'] < -1e-12 for r in eligible),
            'clipped_worse': sum(r['clipped_absolute_error_change'] > 1e-12 for r in eligible),
            'clipped_tied': sum(abs(r['clipped_absolute_error_change']) <= 1e-12 for r in eligible),
            'out_of_range': sum(not 0 <= r['corrected'] <= 1 for r in eligible),
            'raw_mae': float(np.mean([abs(r['raw_bias']) for r in eligible])),
            'corrected_mae': float(np.mean([abs(r['corrected_bias']) for r in eligible])),
            'clipped_mae': float(np.mean([abs(r['clipped_bias']) for r in eligible])),
            'fixed_half_mae': float(np.mean([abs(.5-r['assumed_share']) for r in eligible])),
            'intervals_suppressed': sum(r['bootstrap_nonpositive_J_fraction'] > 0 for r in eligible)}

def main():
    start = time.perf_counter()
    raw = list(csv.DictReader((ROOT/'data_labels.csv').open()))
    keyed = {(r['dataset'], r['item_id'], r['model']): (int(r['reference']), int(r['prediction'])) for r in raw}
    assert len(keyed) == len(raw)
    arrays = {}; counts = np.zeros((len(SETS),len(MODELS),4),dtype=int)
    class_n = np.zeros((len(SETS),2),dtype=int)
    rng = np.random.default_rng(SEED)
    draws = np.zeros((B,len(SETS),len(MODELS),2)) # columns: f, s
    for di,d in enumerate(SETS):
        ids = sorted({r['item_id'] for r in raw if r['dataset'] == d})
        labels = np.array([keyed[(d,i,MODELS[0])][0] for i in ids])
        pred = np.array([[keyed[(d,i,m)][1] for m in MODELS] for i in ids])
        for i,y in zip(ids,labels):
            assert all(keyed[(d,i,m)][0] == y for m in MODELS)
        arrays[d] = (labels,pred)
        for y in [0,1]:
            subset = pred[labels == y]
            class_n[di,y] = len(subset)
            assert len(subset) > 0
            indices = rng.integers(0,len(subset),size=(B,len(subset)))
            draws[:,di,:,y] = subset[indices].mean(axis=1)
        for mi,m in enumerate(MODELS):
            z = pred[:,mi]
            counts[di,mi] = [sum((labels==0)&(z==0)),sum((labels==0)&(z==1)),sum((labels==1)&(z==0)),sum((labels==1)&(z==1))]
    confusion=[]; draw_rows=[]; results=[]; checks=[]
    for di,d in enumerate(SETS):
        other=[i for i in range(len(SETS)) if i != di]
        target_keys={(d,i) for dd,i,mm in keyed if dd==d}
        source_keys={(dd,i) for dd,i,mm in keyed if dd!=d}
        assert not target_keys & source_keys
        for mi,m in enumerate(MODELS):
            tn,fp,fn,tp = map(int, counts[di,mi]); ctn,cfp,cfn,ctp = map(int,counts[other,mi].sum(axis=0))
            f=fp/(tn+fp); s=tp/(fn+tp); fc=cfp/(ctn+cfp); sc=ctp/(cfn+ctp); jc=sc-fc
            confusion.append(dict(model=m,target=d,n=tn+fp+fn+tp,tn=tn,fp=fp,fn=fn,tp=tp,source_tn=ctn,source_fp=cfp,source_fn=cfn,source_tp=ctp,target_fpr=f,target_sensitivity=s,source_fpr=fc,source_sensitivity=sc,source_J=jc))
            bd=draws[:,di,mi,:]
            bc=(draws[:,other,mi,:]*class_n[other][None,:,:]).sum(axis=1)/class_n[other].sum(axis=0)
            bj=bc[:,1]-bc[:,0]
            invalid=float(np.mean(bj<=0))
            for bi in range(B):
                draw_rows.append(dict(draw=bi,model=m,target=d,target_fpr=bd[bi,0],target_sensitivity=bd[bi,1],source_fpr=bc[bi,0],source_sensitivity=bc[bi,1]))
            for p in SHARES:
                q=p*s+(1-p)*f
                row=dict(model=m,target=d,assumed_share=p,eligible=bool(jc>0),raw=q,source_J=jc,corrected='',clipped='',raw_bias=q-p,corrected_bias='',clipped_bias='',absolute_error_change='',clipped_absolute_error_change='',fixed_half_bias=.5-p,bootstrap_nonpositive_J_fraction=invalid,bias_low='',bias_high='',change_low='',change_high='')
                if jc>0:
                    corr=(q-fc)/jc; clipped=float(np.clip(corr,0,1)); bias=corr-p
                    identity=(p*(s-sc)+(1-p)*(f-fc))/jc
                    assert abs(bias-identity)<1e-12
                    row.update(corrected=corr,clipped=clipped,corrected_bias=bias,clipped_bias=clipped-p,absolute_error_change=abs(bias)-abs(q-p),clipped_absolute_error_change=abs(clipped-p)-abs(q-p))
                    q_no_shift=p*sc+(1-p)*fc
                    assert abs((q_no_shift-fc)/jc-p)<1e-12
                    bq=p*bd[:,1]+(1-p)*bd[:,0]
                    if invalid==0:
                        bb=(bq-bc[:,0])/bj-p
                        change=abs(bb)-abs(bq-p)
                        lo,hi=np.percentile(bb,[2.5,97.5]); clo,chi=np.percentile(change,[2.5,97.5])
                        row.update(bias_low=lo,bias_high=hi,change_low=clo,change_high=chi)
                if abs(s-f)>1e-12:
                    assert abs((q-f)/(s-f)-p)<1e-12
                else:
                    checks.append(dict(model=m,target=d,assumed_share=p,control='target oracle singular'))
                results.append(row)
    write_csv('results_confusion.csv',confusion)
    write_csv('results_grid.csv',results)
    write_csv('results_bootstrap_rates.csv',draw_rows)
    summary={'overall':summarize(results),'by_model':{m:summarize([r for r in results if r['model']==m]) for m in MODELS},
             'by_share':{str(p):summarize([r for r in results if r['assumed_share']==p]) for p in SHARES},
             'items_by_set':{d:dict(negative=int(class_n[i,0]),positive=int(class_n[i,1])) for i,d in enumerate(SETS)},
             'data_rows':len(raw),'unique_items':int(class_n.sum()),'bootstrap_draws':B,'seed':SEED,
             'source_J_min':min(r['source_J'] for r in confusion),'source_J_max':max(r['source_J'] for r in confusion),
             'oracle_singular_cases':checks}
    (ROOT/'results_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    print('All compound-key split, bias identity, no-shift, and applicable target-oracle controls passed.')
    print('Python:',platform.python_version(),'NumPy:',np.__version__,'System:',platform.system(),platform.machine())
    print('Data SHA256:',hashlib.sha256((ROOT/'data_labels.csv').read_bytes()).hexdigest())
    print('Plan SHA256:',hashlib.sha256((ROOT/'analysis_plan.md').read_bytes()).hexdigest())
    print('Elapsed analysis seconds:',round(time.perf_counter()-start,3))

if __name__ == '__main__': main()
