"""Compare saved output with the earlier frozen independent specification.

The main source was read only to map output names and control labels. This
adapter was frozen before opening any main result file. It never imports the
main runner.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

import independent_spec as spec


def encode_state(s, event):
    return dict(event=event, duplicate=s['duplicate'], seen=s['seen'], q=s['q'],
                items=[s['balances'][i] for i in spec.ITEMS] if s['balances'] else [],
                revisions=[s['revisions'][i] for i in spec.ITEMS] if s['revisions'] else [])


def expected_trace(case, rule, finality=True):
    e = spec.expected_case(rule, case['values'], case['order'], finality)
    states = [encode_state(s, None if k == 0 else case['order'][k-1])
              for k, s in enumerate(e['states'])]
    branches = [dict(cap=b['cap'], demand=b['request'], admitted=b['accepted'],
                     final_charge=b['charge'], excess=b['excess'],
                     feasible_refusal=b['feasible_refusal'], local_balance=b['local_balance'])
                for b in e['decisions']]
    score = dict(error=e['error'], under=e['under'], exact=e['exact'], over=e['over'],
                 any_negative=e['negative_intermediate'], min_q=min(s['q'] for s in states),
                 excess_case=any(b['excess'] for b in branches),
                 excess_branches=sum(b['excess'] > 0 for b in branches),
                 max_excess=max(b['excess'] for b in branches),
                 feasible_refusal_case=any(b['feasible_refusal'] for b in branches),
                 feasible_refusal_branches=sum(b['feasible_refusal'] for b in branches),
                 admitted=sum(b['admitted'] for b in branches))
    return dict(case_id=case['id'], rule=rule, states=states,
                closure=dict(external_finality=finality, all_reports=e['complete'], passed=e['closed']),
                true_charge=e['truth'], branches=branches, score=score)


SUM_KEYS = ('under', 'exact', 'over', 'any_negative', 'excess_case', 'excess_branches',
            'feasible_refusal_case', 'feasible_refusal_branches', 'admitted')


def record_summary(stats, key, trace):
    if key not in stats:
        stats[key] = dict(rule=key[0], group=key[1], cases=0, branches=0,
                          **{k: 0 for k in SUM_KEYS}, max_over=0, max_under=0,
                          max_excess=0, min_q=0)
    row = stats[key]
    score = trace['score']
    row['cases'] += 1
    row['branches'] += len(trace['branches'])
    for name in SUM_KEYS:
        row[name] += int(score[name])
    row['max_over'] = max(row['max_over'], max(0, score['error']))
    row['max_under'] = max(row['max_under'], max(0, -score['error']))
    row['max_excess'] = max(row['max_excess'], score['max_excess'])
    row['min_q'] = min(row['min_q'], score['min_q'])


def new_pair(rule, reference, include_gap=False):
    p = dict(rule=rule, reference=reference, cases=0, q_lower=0, q_equal=0, q_higher=0,
             decision_differences=0, extra_admissions=0, fewer_admissions=0)
    if include_gap:
        p['max_gap'] = 0
    return p


def record_pair(p, t, ref):
    gap = t['states'][-1]['q'] - ref['states'][-1]['q']
    p['cases'] += 1
    p['q_lower'] += gap < 0
    p['q_equal'] += gap == 0
    p['q_higher'] += gap > 0
    if 'max_gap' in p:
        p['max_gap'] = max(p['max_gap'], gap)
    a = {i for i, b in enumerate(t['branches']) if b['admitted']}
    b = {i for i, b in enumerate(ref['branches']) if b['admitted']}
    p['decision_differences'] += len(a.symmetric_difference(b))
    p['extra_admissions'] += len(a - b)
    p['fewer_admissions'] += len(b - a)


def same(actual, expected, where):
    if actual != expected:
        raise AssertionError(f'Mismatch at {where}')


def read_json(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    results = Path(args.results)
    freezes = [('plan.md', 'plan_freeze.json', 'plan_sha256'),
               ('run_study.py', 'implementation_freeze.json', 'main_sha256'),
               ('independent_spec.py', 'independent_freeze.json', 'source_sha256'),
               ('compare_independent.py', 'independent_adapter_freeze.json', 'source_sha256')]
    for source, freeze, key in freezes:
        same(hashlib.sha256((root/source).read_bytes()).hexdigest(),
             read_json(root/freeze)[key], f'frozen {source}')
    inputs = [dict(id=i, values=list(values), duplicate_group=group,
                   correction_group='_'.join(spec.directions(values)), order=list(order))
              for i, (values, group, order) in enumerate(spec.cases())]
    same(read_json(results/'inputs.json'), inputs, 'all input records and order')
    stats = {}
    witnesses = {}
    pairs = {r: new_pair(r, 'Net') for r in spec.RULES}
    clamp_pair = new_pair('ItemClamp', 'GlobalClamp', True)
    states_count = steps_count = branches_count = duplicate_count = 0
    reflection_prefixes = 0
    case_count = 0
    with gzip.open(results/'traces.jsonl.gz', 'rt') as stream:
        for case in inputs:
            ts = {r: expected_trace(case, r) for r in spec.RULES}
            for k in range(len(case['order']) + 1):
                d = spec.reflection_details(case['values'], case['order'][:k])
                same(ts['Net']['states'][k]['q'], d['net'], 'net prefix')
                same(ts['GlobalClamp']['states'][k]['q'], d['net'] + d['global_lift'], 'global reflection')
                same(ts['ItemClamp']['states'][k]['q'], d['net'] + sum(d['item_lifts'].values()), 'item reflection')
                assert sum(d['item_lifts'].values()) >= d['global_lift']
                reflection_prefixes += 1
            for rule, t in ts.items():
                line = next(stream, None)
                assert line is not None, 'Missing trace'
                same(json.loads(line), t, f"case {case['id']} rule {rule}: complete trace")
                case_count += 1
                states_count += len(t['states'])
                steps_count += len(case['order'])
                branches_count += len(t['branches'])
                duplicate_count += sum(s['duplicate'] for s in t['states'])
                groups = ('all', 'duplicate:' + case['duplicate_group'],
                          'correction:' + case['correction_group'])
                for group in groups:
                    record_summary(stats, (rule, group), t)
                for kind in ('under', 'over', 'any_negative', 'excess_case', 'feasible_refusal_case'):
                    key = rule + ':' + kind
                    if t['score'][kind] and key not in witnesses:
                        witnesses[key] = dict(input=case, trace=t)
                record_pair(pairs[rule], t, ts['Net'])
            record_pair(clamp_pair, ts['ItemClamp'], ts['GlobalClamp'])
            for rule in ('Net', 'RevisionReplace'):
                assert ts[rule]['score']['exact']
                assert not ts[rule]['score']['excess_case']
                assert not ts[rule]['score']['feasible_refusal_case']
            for rule in ('GlobalClamp', 'ItemClamp'):
                assert not ts[rule]['score']['under']
            same(ts['MaxReplace']['states'][-1]['q'],
                 sum(max(case['values'][i:i+2]) for i in (0, 2)), 'max replacement expression')
        assert next(stream, None) is None, 'Extra trace'
    with (results/'summary.csv').open(newline='') as f:
        actual_summaries = [{k: (v if k in ('rule', 'group') else int(v)) for k, v in row.items()}
                            for row in csv.DictReader(f)]
    expected_summaries = [stats[k] for k in sorted(stats)]
    same(actual_summaries, expected_summaries, 'every summary field')
    same(read_json(results/'paired.json'),
         dict(against_net=list(pairs.values()), item_vs_global=clamp_pair), 'every paired table field')
    same(read_json(results/'witnesses.json'), witnesses, 'all first adverse examples')
    expected_controls = dict(named=[], boundary=[])
    control_states = control_branches = 0
    for i, (name, values, order, finality) in enumerate(spec.controls()):
        if name == 'late_original_upward':
            name = 'late_original_up'
        case = dict(id=name, values=list(values), order=list(order))
        ts = [expected_trace(case, r, finality) for r in spec.RULES]
        expected_controls['named' if i < 6 else 'boundary'].append(dict(input=case, traces=ts))
        control_states += sum(len(t['states']) for t in ts)
        control_branches += sum(len(t['branches']) for t in ts)
        if i >= 6:
            assert all(not t['closure']['passed'] and not any(b['admitted'] for b in t['branches']) for t in ts)
    same(read_json(results/'controls.json'), expected_controls, 'all named and boundary control fields')
    checks = dict(passed=True, input_histories=len(inputs), rules=len(spec.RULES), rule_cases=case_count,
                  state_records=states_count, delivery_steps=steps_count, decision_branches=branches_count,
                  summary_rows=len(expected_summaries), named_control_rule_cases=36,
                  boundary_control_rule_cases=12, boundary_decisions=72,
                  hypotheses_checked=dict(H1=True, H2=True, H3=True, H4=True), witnesses=len(witnesses))
    same(read_json(results/'checks.json'), checks, 'run check record')
    for rule in ('GlobalClamp', 'ItemClamp', 'MaxReplace'):
        assert stats[(rule, 'all')]['over'] > 0
    assert stats[('ArrivalReplace', 'all')]['under'] > 0
    assert stats[('ArrivalReplace', 'all')]['over'] > 0
    env = read_json(results/'environment.json')
    assert env['external_calls'] == env['model_calls'] == 0
    assert env['seed'] is None and env['peak_memory_measured'] is False
    assert 0 <= env['cpu_seconds'] < 120 and 0 <= env['wall_seconds'] < 300
    same(env['source_sha256'], read_json(root/'implementation_freeze.json')['main_sha256'], 'environment source hash')
    scientific = ('inputs.json', 'traces.jsonl.gz', 'summary.csv', 'paired.json',
                  'witnesses.json', 'controls.json', 'checks.json')
    same(env['scientific_bytes'], sum((results/p).stat().st_size for p in scientific), 'scientific byte total')
    record = dict(passed=True, specification_sha256=read_json(root/'independent_freeze.json')['source_sha256'],
                  adapter_sha256=read_json(root/'independent_adapter_freeze.json')['source_sha256'],
                  primary_input_histories=len(inputs), primary_rule_cases=case_count,
                  primary_state_records=states_count, primary_delivery_steps=steps_count,
                  primary_decision_branches=branches_count, ignored_duplicate_deliveries=duplicate_count,
                  distinct_input_prefixes_with_reflection_checks=reflection_prefixes,
                  summary_rows=len(expected_summaries), paired_tables=len(pairs)+1,
                  first_adverse_examples=len(witnesses), control_rule_cases=48,
                  control_states=control_states, control_branches=control_branches,
                  environment_consistency='source hash, limits, calls, and durable byte total checked',
                  scope='All saved primary traces, input metadata, controls, summaries, pairs, and witnesses compared. No main import.',
                  all_rule_summaries=[stats[(r, 'all')] for r in spec.RULES],
                  item_vs_global=clamp_pair)
    Path(args.out).write_text(json.dumps(record, sort_keys=True, indent=2) + '\n')
    print(json.dumps(record, sort_keys=True))


if __name__ == '__main__':
    main()
