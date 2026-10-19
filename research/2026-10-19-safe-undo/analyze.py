"""Exact fixed-command undo study. Python standard library only."""
import argparse
import csv
import gzip
import hashlib
import io
import itertools
import json
from collections import defaultdict
from pathlib import Path

ALPHABET = ['add1', 'sub1', 'set0', 'set1', 'flip_y']
RULES = ['full_restore', 'field_restore', 'subtract', 'value_guard', 'revision_guard', 'provenance']
METRICS = ['correct_final', 'complete', 'changed', 'false_confirmation', 'wrong_change',
           'collateral_change', 'new_damage', 'unresolved', 'abstain_correct', 'clean_completion']


def validate(c):
    expected = {'initial_x': [0, 1], 'initial_y': [0, 1], 'lengths': list(range(6)),
                'alphabet': ALPHABET, 'rules': RULES, 'primary_length': 3, 'agent_increment': 1}
    if type(c) is not dict or c.keys() != expected.keys():
        raise ValueError('Configuration keys differ from the frozen design')
    # Type-sensitive comparison prevents True from replacing 1.
    if json.dumps(c, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Configuration differs from the frozen design')
    return c


def step(state, command):
    x, y = state
    if command == 'add1': x += 1
    elif command == 'sub1': x -= 1
    elif command == 'set0': x = 0
    elif command == 'set1': x = 1
    elif command == 'flip_y': y = 1-y
    else: raise ValueError('Unknown command')
    return [x, y]


def run_case(x0, y0, word):
    initial = [x0, y0]
    actual = [[x0+1, y0]]
    reference = [initial.copy()]
    revisions, survives = [0], [True]
    for command in word:
        actual.append(step(actual[-1], command))
        reference.append(step(reference[-1], command))
        revisions.append(revisions[-1] + int(command != 'flip_y'))
        survives.append(survives[-1] and command not in ('set0', 'set1'))
        assert actual[-1][1] == reference[-1][1]
        assert actual[-1][0]-reference[-1][0] == int(survives[-1])
    before, target = actual[-1], reference[-1]
    outcomes = {}
    for rule in RULES:
        after, complete = before.copy(), True
        if rule == 'full_restore': after = initial.copy()
        elif rule == 'field_restore': after[0] = x0
        elif rule == 'subtract': after[0] -= 1
        elif rule == 'value_guard':
            complete = before[0] == x0+1
            if complete: after[0] = x0
        elif rule == 'revision_guard':
            complete = revisions[-1] == 0
            if complete: after[0] = x0
        elif rule == 'provenance' and survives[-1]: after[0] -= 1
        correct, changed = after == target, after != before
        o = {'after': after, 'correct_final': correct, 'complete': complete, 'changed': changed,
             'false_confirmation': complete and not correct,
             'wrong_change': changed and not correct,
             'collateral_change': after[1] != before[1],
             'new_damage': before == target and not correct,
             'unresolved': not complete and not correct,
             'abstain_correct': not complete and correct,
             'clean_completion': complete and correct}
        assert sum(o[k] for k in ['clean_completion', 'false_confirmation', 'unresolved', 'abstain_correct']) == 1
        if rule != 'full_restore': assert after[1] == before[1]
        outcomes[rule] = o
    return {'initial': initial, 'word': list(word), 'actual_states': actual,
            'reference_states': reference, 'revision_counts': revisions, 'survives': survives,
            'before': before, 'target': target, 'has_set': not survives[-1], 'outcomes': outcomes}


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def analyze(c, output):
    validate(c)
    output.mkdir(parents=True, exist_ok=True)
    aggregate, pairs, groups, witnesses = {}, {}, {}, {}
    trace_count = 0
    # Stable gzip header and no embedded filename give byte-repeatable traces.
    with (output/'traces.jsonl.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as gz:
            for length in c['lengths']:
                for x0, y0 in itertools.product(c['initial_x'], c['initial_y']):
                    for word in itertools.product(ALPHABET, repeat=length):
                        case = run_case(x0, y0, word)
                        case['case_id'] = trace_count
                        case['length'] = length
                        gz.write((encoded(case)+'\n').encode())
                        trace_count += 1
                        subset = 'has_set' if case['has_set'] else 'no_set'
                        for rule, o in case['outcomes'].items():
                            for label in ['all', subset]:
                                key = (length, label, rule)
                                a = aggregate.setdefault(key, {'length': length, 'subset': label, 'rule': rule,
                                                               'cases': 0, **dict.fromkeys(METRICS, 0)})
                                a['cases'] += 1
                                for metric in METRICS: a[metric] += int(o[metric])
                            for metric in ['false_confirmation', 'wrong_change', 'collateral_change',
                                           'new_damage', 'unresolved', 'abstain_correct']:
                                wkey = rule+':'+metric
                                if o[metric] and wkey not in witnesses:
                                    witnesses[wkey] = {'case_id': case['case_id'], 'initial': case['initial'],
                                                       'word': list(word), 'before': case['before'],
                                                       'target': case['target'], 'outcome': o}
                            if rule != 'provenance':
                                p = pairs.setdefault((length,rule), {'length':length,'rule':rule,
                                    'provenance_clean_rule_abstains':0,'abstains_before_correct':0,
                                    'abstains_before_wrong':0,'provenance_clean_rule_false':0})
                                assert case['outcomes']['provenance']['clean_completion']
                                if not o['complete']:
                                    p['provenance_clean_rule_abstains'] += 1
                                    p['abstains_before_correct' if case['before']==case['target'] else 'abstains_before_wrong'] += 1
                                p['provenance_clean_rule_false'] += int(o['false_confirmation'])
                        key = (length,x0,y0,*case['before'],case['revision_counts'][-1])
                        g = groups.setdefault(key, {'key':list(key),'cases':0,'targets':{},'first_by_target':{}})
                        target_key = encoded(case['target'])
                        g['cases'] += 1
                        g['targets'][target_key] = g['targets'].get(target_key,0)+1
                        g['first_by_target'].setdefault(target_key, {'case_id':case['case_id'],'word':list(word),
                                                                  'target':case['target']})
    aggregate_rows = [aggregate[k] for k in sorted(aggregate)]
    with (output/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['length','subset','rule','cases']+METRICS)
        w.writeheader(); w.writerows(aggregate_rows)
    pair_rows = [pairs[k] for k in sorted(pairs)]
    group_rows=[]
    for key in sorted(groups):
        g=groups[key]
        first=sorted(g.pop('first_by_target').values(),key=lambda z:z['case_id'])
        g['ambiguous']=len(first)>1
        g['minimum_pair']=first[:2] if g['ambiguous'] else []
        group_rows.append(g)
    write_json(output/'paired_results.json',pair_rows)
    write_json(output/'observation_groups.json',group_rows)
    write_json(output/'witnesses.json',witnesses)
    allrows=[r for r in aggregate_rows if r['subset']=='all']
    byrule={rule:{m:sum(r[m] for r in allrows if r['rule']==rule) for m in ['cases']+METRICS} for rule in RULES}
    h={
      'H1':all(byrule[r]['false_confirmation']>0 for r in ['full_restore','field_restore']) and byrule['full_restore']['collateral_change']>0,
      'H2':all(r['correct_final']==(0 if r['subset']=='has_set' else r['cases']) for r in aggregate_rows if r['rule']=='subtract' and r['subset']!='all'),
      'H3':byrule['value_guard']['false_confirmation']>0 and byrule['value_guard']['new_damage']>0,
      'H4':byrule['revision_guard']['false_confirmation']==byrule['revision_guard']['wrong_change']==0 and byrule['revision_guard']['complete']<trace_count,
      'H5':byrule['provenance']['clean_completion']==trace_count,
      'H6':any(g['ambiguous'] for g in group_rows)}
    amb=[g for g in group_rows if g['ambiguous']]
    first_ambiguity=min(amb,key=lambda g:tuple(v['case_id'] for v in g['minimum_pair'])) if amb else None
    counts_by_length=[]
    for length in c['lengths']:
        gs=[g for g in group_rows if g['key'][0]==length]
        counts_by_length.append({'length':length,'groups':len(gs),'ambiguous_groups':sum(g['ambiguous'] for g in gs),
                                'histories_in_ambiguous_groups':sum(g['cases'] for g in gs if g['ambiguous'])})
    summary={'histories':trace_count,'policy_outcomes':trace_count*len(RULES),
             'aggregate_rows':len(aggregate_rows),'paired_rows':len(pair_rows),'witnesses':len(witnesses),
             'hypotheses':h,'totals':byrule,'observation_counts':counts_by_length,'first_ambiguity':first_ambiguity}
    write_json(output/'summary.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,default=Path('.'));p.add_argument('--output-dir',type=Path,default=Path('.'))
    args=p.parse_args()
    manifest=json.loads((args.input_dir/'input_manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if hashlib.sha256((args.input_dir/name).read_bytes()).hexdigest()!=digest: raise ValueError('Frozen file changed: '+name)
    summary=analyze(json.loads((args.input_dir/'config.json').read_text()),args.output_dir)
    print(json.dumps({k:summary[k] for k in ['histories','policy_outcomes','aggregate_rows','paired_rows','witnesses','hypotheses']},sort_keys=True))
