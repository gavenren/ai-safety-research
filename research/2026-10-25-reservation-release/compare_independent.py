"""Compare saved main evidence with the frozen position-based specification.

This schema adapter was written after inspecting the evidence format. It does
not import or read the main interpreter. It imports independent_check only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

import independent_check as spec


def scalar_count(value):
    if isinstance(value, dict):
        return sum(scalar_count(v) for v in value.values())
    if isinstance(value, list):
        return sum(scalar_count(v) for v in value)
    return 1


def adapt_state(x, inp):
    receipt = x['fence_receipt']
    if receipt is not None:
        receipt = {'accepted': receipt['accepted'], 'resolved': receipt['resolved'],
                   'charged': receipt['charged'], 'certificate': receipt['closure_certificate']}
    d = x['decision']
    if d is not None:
        d = {'released': d['released'],
             'held_before': 0 if inp['schedule'].index('T') < inp['schedule'].index('D') else inp['a'],
             'premature': d['premature_refund'], 'b_accepted': d['b_accepted'],
             'safe_feasible': d['pre_d_liability'] + inp['b'] <= inp['capacity'],
             'safe_feasible_refusal': d['safe_feasible_b_refusal']}
    return {
        'state': {'actual_a': x['actual_a'], 'hold': x['hold_a'], 'booked_a': x['booked_a'],
                  'booked_b': x['booked_b'], 'accept_attempted': x['acceptance_attempted'],
                  'accepted': x['accepted'], 'resolved': x['resolved'], 'fenced': x['fenced'],
                  'settled': x['settled'], 'observation': x['observation'],
                  'fence_receipt': receipt, 'decision': d, 'settlement_count': x['settlement_count']},
        'audit': {'liability': x['liability'], 'available': x['available'],
                  'actual_excess': x['actual_excess'], 'exposure_excess': x['exposure_excess'],
                  'uncovered': x['uncovered_liability'], 'deficit': x['local_deficit']},
    }


def adapt_scores(s):
    result = {}
    for main, flag, maximum, first in (
        ('actual_excess', 'actual_breach', 'max_actual_excess', 'first_actual_breach'),
        ('exposure_excess', 'exposure_breach', 'max_exposure_excess', 'first_exposure_breach'),
        ('uncovered', 'uncovered_liability', 'max_uncovered_liability', 'first_uncovered_liability'),
        ('deficit', 'negative_available', 'max_local_deficit', 'first_negative_available'),
    ):
        result[main+'_case'] = bool(s[flag])
        result[main+'_max'] = s[maximum]
        result[main+'_first'] = s[first]
    result.update({
        'exposure_without_final_actual': bool(s['exposure_without_final_actual_breach']),
        'premature_refund': bool(s['premature_refund']),
        'b_accepted': bool(s['b_accepted']), 'b_refused': bool(s['b_refused']),
        'safe_feasible_refusal': bool(s['safe_feasible_b_refusal']),
        'released': bool(s['released']), 'a_blocked': bool(s['a_blocked']),
        'a_charged': bool(s['final_a_charge']), 'settlements': s['settlement_count'],
    })
    return result


def adapt(row):
    inp = row['input']
    return {'input': inp, 'rule': row['rule'],
            'initial': adapt_state(row['initial'], inp),
            'trace': [{'event': t['event'], 'before': adapt_state(t['before'], inp),
                       'after': adapt_state(t['after'], inp)} for t in row['trace']],
            'final': adapt_state(row['final'], inp), 'scores': adapt_scores(row['scores'])}


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(label + '\nActual: ' + repr(actual) + '\nExpected: ' + repr(expected))


def row_key(row):
    return spec.key_of(row), row['rule']


def load_json(path):
    return json.loads(path.read_text())


def read_traces(path):
    with gzip.open(path, 'rt') as stream:
        return [json.loads(line) for line in stream]


def compare(folder):
    expected_raw = list(spec.all_rows())
    pure_checks = spec.verify_properties(expected_raw)
    spec_controls = spec.named_controls()
    expected = {row_key(r): adapt(r) for r in expected_raw}
    actual = read_traces(folder/'traces.jsonl.gz')
    assert len(actual) == len(expected) == 8400
    seen = set()
    world_ids = {}
    counts = Counter()
    for row in actual:
        key = row_key(row)
        assert key not in seen, key
        seen.add(key)
        semantic = {k: v for k, v in row.items() if k != 'world_id'}
        assert_equal(semantic, expected[key], repr(key))
        counts['initial_final_state_scalar_values'] += scalar_count(row['initial']) + scalar_count(row['final'])
        counts['event_state_scalar_values'] += sum(scalar_count(t['before']) + scalar_count(t['after']) for t in row['trace'])
        counts['score_values'] += scalar_count(row['scores'])
        counts['events'] += len(row['trace'])
        wk = key[0]
        if wk in world_ids:
            assert row['world_id'] == world_ids[wk]
        else:
            world_ids[wk] = row['world_id']
    assert seen == set(expected)
    assert len(world_ids) == len(set(world_ids.values())) == 1680

    inputs = load_json(folder/'inputs.json')
    input_keys = [spec.world_key(i['a'], i['b'], i['capacity'], i['branch'], i['schedule']) for i in inputs]
    assert len(input_keys) == len(set(input_keys)) == 1680
    assert set(input_keys) == set(world_ids)
    assert all(set(i) == {'a','b','capacity','branch','schedule'} for i in inputs)
    for idx, key in enumerate(input_keys):
        assert world_ids[key] == f'w{idx:04d}'

    with (folder/'summary.csv').open(newline='') as stream:
        summaries = list(csv.DictReader(stream))
    assert len(summaries) == 15
    assert {(r['rule'], r['branch']) for r in summaries} == set((r,b) for r in spec.RULES for b in ('all',)+spec.BRANCHES)
    for row in summaries:
        selected = [v for (w,rule),v in expected.items() if rule == row['rule'] and (row['branch']=='all' or w[3] == row['branch'])]
        for k, value in row.items():
            if k in ('rule','branch'):
                continue
            if k == 'cases':
                want = len(selected)
            elif k.endswith('_max'):
                want = max(s['scores'][k] for s in selected)
            else:
                want = sum(s['scores'][k] for s in selected)
            assert int(value) == want, (row['rule'], row['branch'], k, value, want)
            counts['summary_numeric_values'] += 1

    pairs = load_json(folder/'paired.json')
    assert len(pairs) == 10
    assert {(r['left'],r['right']) for r in pairs} == set(combinations(spec.RULES, 2))
    for row in pairs:
        assert row['worlds'] == 1680
        decisions = 0
        deltas = {k: 0 for k in row['deltas_right_minus_left']}
        for wk in world_ids:
            left, right = expected[wk,row['left']], expected[wk,row['right']]
            decisions += left['scores']['b_accepted'] != right['scores']['b_accepted']
            for k in deltas:
                deltas[k] += int(right['scores'][k]) - int(left['scores'][k])
        assert row['b_decisions_differ'] == decisions
        assert_equal(row['deltas_right_minus_left'], deltas, 'paired deltas')
        counts['paired_score_deltas'] += len(deltas)

    controls = load_json(folder/'controls.json')
    assert len(controls) == 35 and len({r['name'] for r in controls}) == 7
    for row in controls:
        actual_control = row['trace']
        inp = actual_control['input']
        want = adapt(spec.evaluate(inp['a'],inp['b'],inp['capacity'],inp['branch'],inp['schedule'],actual_control['rule']))
        got = {k:v for k,v in actual_control.items() if k!='world_id'}
        assert_equal(got, want, 'control '+row['name']+'/'+row['rule'])
        assert row['rule'] == actual_control['rule'] and row['pass'] is True
        assert row['expected_b_accepted'] == want['scores']['b_accepted']
        assert row['expected_actual_breach'] == want['scores']['actual_excess_case']
    for name in {r['name'] for r in controls}:
        assert {r['rule'] for r in controls if r['name']==name} == set(spec.RULES)

    witnesses = load_json(folder/'witnesses.json')
    for label, witness in witnesses.items():
        rule, score = label.split('/')
        first = next(r for r in actual if r['rule'] == rule and r['scores'][score])
        assert_equal(witness, first, 'first witness '+label)
    checks = load_json(folder/'checks.json')
    expected_checks = {
        'ample_budget_cases': pure_checks['ample_capacity_cases'],
        'branch_prefix_pairs': pure_checks['pre_resolution_branch_pairs'],
        'complete_rule_cases': pure_checks['complete_rule_cases'],
        'fence_before_a': pure_checks['fence_before_acceptance_cases'],
        'terminal_before_d': pure_checks['terminal_first_worlds'],
    }
    assert_equal(checks, expected_checks, 'saved checks')
    return {'status':'pass','cases':len(actual),'worlds':len(world_ids),
            'summaries':len(summaries),'policy_pairs':len(pairs),
            'main_named_controls':len(controls),'independent_named_controls':len(spec_controls),
            'first_witnesses':len(witnesses),'comparisons':dict(counts),
            'pure_checks':pure_checks,'main_runner_imported':False,'main_runner_source_read':False,
            'meaning':'Saved synthetic traces, evidence, decisions, all state fields, scores, summaries, pairs, controls, and witnesses match the frozen independent position-based specification. This is not a provider or production-agent validation.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = compare(args.results)
    result['wall_seconds'] = time.monotonic()-started
    result['files'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(args.results.iterdir()) if p.is_file() and p.name!='environment.json'}
    result['independent_code_sha256'] = hashlib.sha256(Path(spec.__file__).read_bytes()).hexdigest()
    result['adapter_code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
