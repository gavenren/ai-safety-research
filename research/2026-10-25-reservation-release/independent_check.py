"""Independent position-based specification for the frozen reservation plan.

Written from plan.md without main-code or main-result access. Only Python's
standard library is used. The model uses event positions rather than mutating
one state through an event dispatcher.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import platform
import sys
import time

RULES = ('Timeout', 'ZeroObservation', 'FenceOnly', 'ClosureCertificate', 'TerminalOnly')
BRANCHES = ('charge', 'zero')


def schedules():
    """Choose positions for A,E,T, then O,D; F occupies the last position."""
    rows = []
    for aet in combinations(range(6), 3):
        available = sorted(set(range(6)) - set(aet))
        for od in combinations(available, 2):
            row = ['F'] * 6
            for p, event in zip(aet, 'AET'):
                row[p] = event
            for p, event in zip(od, 'OD'):
                row[p] = event
            rows.append(''.join(row))
    return sorted(rows)


def world_key(a, b, capacity, branch, order):
    return (a, b, capacity, branch, ''.join(order))


def evaluate(a, b, capacity, branch, order, rule):
    order = ''.join(order)
    assert len(order) == 6 and set(order) == set('AETOF D'.replace(' ', ''))
    p = {event: order.index(event) + 1 for event in order}
    assert p['A'] < p['E'] < p['T'] and p['O'] < p['D']
    assert a in (1, 2) and b in (1, 2) and a <= capacity <= 4
    assert rule in RULES and branch in BRANCHES
    accepted_final = p['A'] < p['F']
    final_charge = a if accepted_final and branch == 'charge' else 0

    def charge_at(k):
        return final_charge if p['E'] <= k else 0

    def liability_at(k):
        if p['E'] <= k:
            return final_charge
        if p['A'] <= k and accepted_final:
            return a
        if p['F'] <= k:
            return 0
        return a

    f_time = p['F']
    f_accepted = p['A'] < f_time
    f_resolved = p['E'] < f_time
    f_charge = charge_at(f_time - 1)
    fence_receipt = {
        'accepted': f_accepted,
        'resolved': f_resolved,
        'charged': f_charge,
        'closure_certificate': (not f_accepted) or (f_resolved and f_charge == 0),
    }
    observation = charge_at(p['O'] - 1)
    d_time = p['D']
    settled_at_d = p['T'] < d_time
    pre_hold = 0 if settled_at_d else a
    pre_booked = final_charge if settled_at_d else 0
    pre_liability = liability_at(d_time - 1)
    evidence_conditions = {
        'Timeout': True,
        'ZeroObservation': observation == 0,
        'FenceOnly': p['F'] < d_time,
        'ClosureCertificate': p['F'] < d_time and fence_receipt['closure_certificate'],
        'TerminalOnly': False,
    }
    released = bool(pre_hold and evidence_conditions[rule])
    hold_at_admission = 0 if released else pre_hold
    admission_balance = capacity - hold_at_admission - pre_booked
    b_accepted = admission_balance >= b
    decision = {
        'released': released,
        'released_units': pre_hold if released else 0,
        'premature_refund': released and pre_liability > 0,
        'b_accepted': b_accepted,
        'safe_feasible_b_refusal': (not b_accepted) and pre_liability + b <= capacity,
        'pre_d_liability': pre_liability,
        'pre_d_available': capacity - pre_hold - pre_booked,
        'admission_available': admission_balance,
    }

    def state_at(k):
        d_seen = p['D'] <= k
        settled = p['T'] <= k
        hold = 0 if settled or (d_seen and released) else a
        booked_a = final_charge if settled else 0
        booked_b = b if d_seen and b_accepted else 0
        actual = charge_at(k)
        liability = liability_at(k)
        available = capacity - hold - booked_a - booked_b
        return {
            'acceptance_attempted': p['A'] <= k,
            'accepted': p['A'] <= k and accepted_final,
            'acceptance_blocked': p['A'] <= k and not accepted_final,
            'resolved': p['E'] <= k,
            'actual_a': actual,
            'hold_a': hold,
            'booked_a': booked_a,
            'booked_b': booked_b,
            'fenced': p['F'] <= k,
            'observation': observation if p['O'] <= k else None,
            'fence_receipt': fence_receipt if p['F'] <= k else None,
            'settled': settled,
            'settlement_count': int(settled),
            'decision': decision if d_seen else None,
            'liability': liability,
            'available': available,
            'actual_excess': max(0, actual + booked_b - capacity),
            'exposure_excess': max(0, liability + booked_b - capacity),
            'uncovered_liability': max(0, liability - hold - booked_a),
            'local_deficit': max(0, -available),
        }

    initial = state_at(0)
    trace = [{'event': e, 'before': state_at(k), 'after': state_at(k + 1)}
             for k, e in enumerate(order)]
    final = trace[-1]['after']
    scores = {}
    for field, flag, maximum, first in (
        ('actual_excess', 'actual_breach', 'max_actual_excess', 'first_actual_breach'),
        ('exposure_excess', 'exposure_breach', 'max_exposure_excess', 'first_exposure_breach'),
        ('uncovered_liability', 'uncovered_liability', 'max_uncovered_liability', 'first_uncovered_liability'),
        ('local_deficit', 'negative_available', 'max_local_deficit', 'first_negative_available'),
    ):
        values = [x['after'][field] for x in trace]
        scores[flag] = int(any(values))
        scores[maximum] = max(values)
        scores[first] = next((x['event'] for x in trace if x['after'][field] > 0), None)
    scores.update({
        'exposure_without_final_actual_breach': int(scores['exposure_breach'] and not final['actual_excess']),
        'premature_refund': int(decision['premature_refund']),
        'released': int(released),
        'b_accepted': int(b_accepted),
        'b_refused': int(not b_accepted),
        'safe_feasible_b_refusal': int(decision['safe_feasible_b_refusal']),
        'a_accepted': int(accepted_final),
        'a_blocked': int(not accepted_final),
        'final_a_charge': final_charge,
        'final_actual_excess': final['actual_excess'],
        'settlement_count': final['settlement_count'],
    })
    return {
        'input': {'a': a, 'b': b, 'capacity': capacity, 'branch': branch, 'schedule': list(order)},
        'rule': rule,
        'initial': initial,
        'trace': trace,
        'final': final,
        'scores': scores,
    }


# Expected control outcomes were written before this evaluator's first run.
# Tuple columns: B accepts, actual breach, exposure breach, uncovered liability,
# premature refund, safe-feasible B refusal, final A charge.
CONTROL_EXPECTED = {
    'accepted_before_fence_late_charge': (
        'OAFDET', 'charge', [(1,1,1,1,1,0,1)]*3 + [(0,0,0,0,0,0,1)]*2),
    'fence_before_acceptance': (
        'OFDAET', 'charge', [(1,0,0,0,0,0,0)]*4 + [(0,0,0,0,0,1,0)]),
    'early_terminal_receipt': (
        'AETOFD', 'charge', [(0,0,0,0,0,0,1)]*5),
    'zero_observation_then_charge': (
        'OAEFDT', 'charge', [(1,1,1,1,1,0,1)]*3 + [(0,0,0,0,0,0,1)]*2),
    'zero_resolution_before_fence': (
        'AEOFDT', 'zero', [(1,0,0,0,0,0,0)]*4 + [(0,0,0,0,0,1,0)]),
    'zero_resolution_after_fence': (
        'AFEODT', 'zero', [(1,0,0,0,0,0,0)]*3 + [(0,0,0,0,0,1,0)]*2),
    'exposure_without_actual_breach': (
        'OAFDET', 'zero', [(1,0,1,1,1,0,0)]*3 + [(0,0,0,0,0,0,0)]*2),
}
CONTROL_COLUMNS = ('b_accepted', 'actual_breach', 'exposure_breach',
                   'uncovered_liability', 'premature_refund',
                   'safe_feasible_b_refusal', 'final_a_charge')


def named_controls():
    outputs = []
    for name, (order, branch, expected) in CONTROL_EXPECTED.items():
        for rule, want in zip(RULES, expected):
            row = evaluate(1, 1, 1, branch, order, rule)
            actual = tuple(row['scores'][k] for k in CONTROL_COLUMNS)
            assert actual == want, (name, rule, actual, want)
            outputs.append({'name': name, 'rule': rule, 'order': order,
                            'branch': branch, 'expected': dict(zip(CONTROL_COLUMNS, want)),
                            'actual': dict(zip(CONTROL_COLUMNS, actual)), 'pass': True})
    return outputs


def key_of(row):
    x = row['input']
    return world_key(x['a'], x['b'], x['capacity'], x['branch'], x['schedule'])


def all_rows():
    orders = schedules()
    assert len(orders) == len(set(orders)) == 60
    for a, b, capacity, branch, order in product((1, 2), (1, 2), range(1, 5), BRANCHES, orders):
        if a > capacity:
            continue
        for rule in RULES:
            yield evaluate(a, b, capacity, branch, order, rule)


def verify_properties(rows):
    checks = Counter()
    by_world = {}
    for row in rows:
        inp, score, rule = row['input'], row['scores'], row['rule']
        a, b, cap = inp['a'], inp['b'], inp['capacity']
        states = [row['initial']] + [s['after'] for s in row['trace']]
        assert score['settlement_count'] == 1
        assert row['final']['booked_a'] == row['final']['actual_a']
        assert score['actual_breach'] == int(row['final']['local_deficit'] > 0)
        assert row['final']['actual_excess'] == row['final']['local_deficit']
        old_a = old_b = 0
        for s in states:
            assert s['actual_a'] in (0, a) and s['booked_a'] in (0, a)
            assert s['hold_a'] in (0, a) and s['booked_b'] in (0, b)
            assert s['actual_a'] >= old_a and s['booked_b'] >= old_b
            old_a, old_b = s['actual_a'], s['booked_b']
            assert s['available'] + s['hold_a'] + s['booked_a'] + s['booked_b'] == cap
            checks['state_bookkeeping_checks'] += 1
        if rule in ('ClosureCertificate', 'TerminalOnly'):
            assert not any(score[k] for k in ('actual_breach', 'exposure_breach', 'uncovered_liability', 'negative_available', 'premature_refund'))
            checks['complete_rule_cases'] += 1
        if cap >= a + b:
            assert not score['actual_breach'] and not score['exposure_breach']
            checks['ample_capacity_cases'] += 1
        if inp['schedule'].index('F') < inp['schedule'].index('A'):
            assert score['a_blocked'] == 1 and score['final_a_charge'] == 0
            checks['fence_before_acceptance_cases'] += 1
        by_world.setdefault(key_of(row), {})[rule] = row
    assert len(rows) == 8400 and len(by_world) == 1680
    checks['cases'] = len(rows)
    checks['worlds'] = len(by_world)
    for world, group in by_world.items():
        assert set(group) == set(RULES)
        order = world[-1]
        if order.index('T') < order.index('D'):
            decisions = [g['final']['decision'] for g in group.values()]
            assert decisions == [decisions[0]] * 5
            checks['terminal_first_worlds'] += 1
        closure, terminal = group['ClosureCertificate'], group['TerminalOnly']
        assert closure['scores']['b_accepted'] >= terminal['scores']['b_accepted']
        checks['closure_extra_acceptances'] += closure['scores']['b_accepted'] - terminal['scores']['b_accepted']
        if world[3] == 'charge':
            other = by_world[world[:3] + ('zero', world[-1])]
            cutoff = order.index('E')
            for rule, row in group.items():
                assert row['initial'] == other[rule]['initial']
                assert row['trace'][:cutoff] == other[rule]['trace'][:cutoff]
                checks['pre_resolution_branch_pairs'] += 1
    for rule in RULES[:3]:
        assert any(r['scores']['premature_refund'] and r['rule'] == rule for r in rows)
        assert any(r['scores']['actual_breach'] and r['rule'] == rule for r in rows)
    assert any(r['scores']['exposure_without_final_actual_breach'] for r in rows)
    assert checks['closure_extra_acceptances'] > 0
    return dict(checks)


def summary(rows):
    out = {}
    for rule in RULES:
        for branch in ('all',) + BRANCHES:
            selected = [r for r in rows if r['rule'] == rule and (branch == 'all' or r['input']['branch'] == branch)]
            keys = [k for k, v in selected[0]['scores'].items() if isinstance(v, int)]
            out[rule + '/' + branch] = {'cases': len(selected),
                **{k: sum(r['scores'][k] for r in selected) for k in keys}}
    return out


def dump_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    controls = named_controls()
    rows = list(all_rows())
    checks = verify_properties(rows)
    with (args.output / 'independent_expected.jsonl.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, filename='') as gz:
            for row in rows:
                gz.write((json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n').encode())
    dump_json(args.output / 'independent_summary.json', summary(rows))
    dump_json(args.output / 'independent_controls.json', controls)
    result = {'status': 'pass', 'checks': checks, 'named_control_rows': len(controls),
              'main_code_read': False, 'main_results_read': False,
              'python': platform.python_version(), 'elapsed_seconds': time.monotonic()-start,
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    dump_json(args.output / 'independent_result.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
