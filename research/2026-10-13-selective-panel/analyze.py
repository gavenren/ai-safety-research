"""Exact routing audit. Run with Python 3.13; no third-party packages."""
import csv
import hashlib
import json
import math
import platform
import sys
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = ('gemma-2-9b', 'Llama-3.1-8B', 'Mistral-7B', 'OLMo-2-7B', 'Qwen2.5-7B')
THRESHOLDS = (3, 4, 5)
REVIEW_ERRORS = (F(0), F(1, 20), F(1, 10), F(1, 5), F(3, 10), F(1, 2))


def ratio(n, d):
    return F(n, d) if d else None


def number(x):
    return '' if x is None else f'{float(x):.12f}'


def write_csv(name, rows):
    with (ROOT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def random_distribution(n, errors, accepted):
    denominator = math.comb(n, accepted)
    return [(x, F(math.comb(errors, x) * math.comb(n-errors, accepted-x), denominator))
            for x in range(max(0, accepted-(n-errors)), min(errors, accepted)+1)]


def quantile(distribution, target):
    cumulative = F(0)
    for x, p in distribution:
        cumulative += p
        if cumulative >= target:
            return x
    raise AssertionError('Incomplete distribution')


def count_row(items, threshold):
    n = len(items)
    errors = sum(i['wrong'] for i in items)
    accepted = [i for i in items if i['agreement'] >= threshold]
    a = len(accepted)
    ea = sum(i['wrong'] for i in accepted)
    d, ed = n-a, errors-ea
    return n, errors, a, ea, d, ed


def controls():
    cases = {}
    for name, items, threshold in [
        ('all_correct', [{'wrong': 0, 'agreement': 5}]*4, 5),
        ('all_wrong', [{'wrong': 1, 'agreement': 5}]*4, 5),
        ('no_accepted', [{'wrong': 0, 'agreement': 3}, {'wrong': 1, 'agreement': 3}], 5),
        ('correct_deferred', [{'wrong': 1, 'agreement': 5}, {'wrong': 0, 'agreement': 3}], 5),
        ('wrong_deferred', [{'wrong': 0, 'agreement': 5}, {'wrong': 1, 'agreement': 3}], 5),
        ('all_accepted', [{'wrong': 1, 'agreement': 5}, {'wrong': 0, 'agreement': 3}], 3),
    ]:
        n, e, a, ea, d, ed = count_row(items, threshold)
        cases[name] = dict(zip(('n','errors','accepted','accepted_errors','deferred','deferred_errors'),(n,e,a,ea,d,ed)))
        cases[name]['selective_error'] = number(ratio(ea,a))
        cases[name]['review_break_even_error'] = number(ratio(ed,d))
    cases['small_random_distribution'] = [[x, str(p)] for x,p in random_distribution(4,2,2)]
    assert cases['small_random_distribution'] == [[0,'1/6'],[1,'2/3'],[2,'1/6']]
    assert cases['no_accepted']['selective_error'] == ''
    assert cases['all_accepted']['review_break_even_error'] == ''
    return cases


def main():
    manifest = json.loads((ROOT/'input_manifest.json').read_text())
    for filename, key in [('data_labels.csv','data_sha256'),('analysis_plan.md','plan_sha256')]:
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest() == manifest[key]
    groups = defaultdict(dict)
    with (ROOT/'data_labels.csv').open(newline='') as f:
        source = list(csv.DictReader(f))
    for r in source:
        key = (r['dataset'], r['item_id'])
        assert r['model'] in MODELS and r['model'] not in groups[key]
        ref, vote = int(r['reference']), int(r['prediction'])
        assert ref in (0,1) and vote in (0,1)
        groups[key][r['model']] = (ref,vote)
    items=[]
    for (dataset,item_id), votes in sorted(groups.items()):
        assert set(votes) == set(MODELS)
        assert len({r[0] for r in votes.values()}) == 1
        ref = next(iter(votes.values()))[0]
        s = sum(v[1] for v in votes.values())
        agreement = max(s,5-s)
        item = {'dataset':dataset,'item_id':item_id,'reference':ref,'flag_votes':s,
                'majority':int(s>=3),'agreement':agreement,'wrong':int(int(s>=3)!=ref)}
        item.update({f'accept_t{t}':int(agreement>=t) for t in THRESHOLDS})
        items.append(item)
    assert len(source)==6990 and len(items)==1398
    write_csv('results_items.csv',items)
    sets = sorted({i['dataset'] for i in items})
    assert len(sets)==7
    rows=[]; probabilities=[]; scenarios=[]
    for dataset in sets:
        for reference in ('all','0','1'):
            subset=[i for i in items if i['dataset']==dataset and (reference=='all' or i['reference']==int(reference))]
            for t in THRESHOLDS:
                n,e,a,ea,d,ed=count_row(subset,t)
                distribution=random_distribution(n,e,a)
                assert sum(p for _,p in distribution)==1
                assert sum(x*p for x,p in distribution)==F(a*e,n)
                qlo,qhi=quantile(distribution,F(1,40)),quantile(distribution,F(39,40))
                risk,base=ratio(ea,a),F(e,n)
                row={'dataset':dataset,'reference':reference,'threshold':t,'n':n,'errors':e,
                     'accepted':a,'accepted_errors':ea,'deferred':d,'deferred_errors':ed,
                     'coverage':number(F(a,n)),'baseline_error':number(base),'selective_error':number(risk),
                     'selective_minus_baseline':number(None if risk is None else risk-base),
                     'residual_automated_error':number(F(ea,n)),
                     'review_break_even_error':number(ratio(ed,d)),
                     'error_capture':number(ratio(ed,e)),
                     'random_expected_accepted_errors':number(F(a*e,n)),
                     'random_q025_errors':qlo,'random_q975_errors':qhi,
                     'random_q025_selective_error':number(ratio(qlo,a)),
                     'random_q975_selective_error':number(ratio(qhi,a))}
                rows.append(row)
                for x,p in distribution:
                    probabilities.append({'dataset':dataset,'reference':reference,'threshold':t,
                                          'accepted_errors':x,'probability_numerator':p.numerator,
                                          'probability_denominator':p.denominator})
                for h in REVIEW_ERRORS:
                    actual=F(ea,n)+h*F(d,n)
                    random=F(a*e,n*n)+h*F(d,n)
                    change=actual-base
                    scenarios.append({'dataset':dataset,'reference':reference,'threshold':t,
                                      'review_error':number(h),'system_error':number(actual),
                                      'baseline_error':number(base),'change':number(change),
                                      'random_system_error':number(random),
                                      'routing_minus_random':number(actual-random),
                                      'outcome':'improve' if change<0 else 'worsen' if change>0 else 'tie'})
    write_csv('results_groups.csv',rows)
    write_csv('results_random_distribution.csv',probabilities)
    write_csv('results_review_scenarios.csv',scenarios)
    summary={'items':len(items),'votes':len(source),'group_rows':len(rows),'random_probability_rows':len(probabilities),
             'scenario_rows':len(scenarios),'thresholds':{}}
    for t in THRESHOLDS:
        prim=[r for r in rows if r['reference']=='all' and r['threshold']==t]
        valid=[r for r in prim if r['selective_error']!='']
        cmp=lambda r: F(r['accepted_errors'],r['accepted'])-F(r['errors'],r['n'])
        summary['thresholds'][str(t)]={
            'sets_improve':sum(cmp(r)<0 for r in valid),'sets_tie':sum(cmp(r)==0 for r in valid),
            'sets_worsen':sum(cmp(r)>0 for r in valid),'sets_no_accepted':len(prim)-len(valid),
            'mean_set_coverage':float(sum(F(r['accepted'],r['n']) for r in prim)/7),
            'mean_set_selective_error':float(sum(F(r['accepted_errors'],r['accepted']) for r in valid)/len(valid)),
            'class_rows_no_accepted':sum(r['accepted']==0 for r in rows if r['reference']!='all' and r['threshold']==t),
            'class_rows_selective_worse':sum(F(r['accepted_errors'],r['accepted'])>F(r['errors'],r['n']) for r in rows if r['reference']!='all' and r['threshold']==t and r['accepted'])}
    for name,obj in [('results_summary.json',summary),('results_controls.json',controls()),
                     ('environment.json',{'python':platform.python_version(),'implementation':platform.python_implementation(),
                                          'platform':platform.system(),'machine':platform.machine(),'packages':'standard library only','random_seed':None})]:
        (ROOT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
    print('PASS: input hashes, keys, labels, count checks, distributions, and controls.')


if __name__=='__main__':
    main()
