#!/usr/bin/env python3
"""Exact receipt/state regression model. Python standard library only."""
import argparse
import csv
import hashlib
import itertools
import json
import platform
import time
from pathlib import Path

RULES = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
COMMANDS = ['set0', 'set1', 'flip_y']


def words():
    return [list(w) for n in range(3) for w in itertools.product(COMMANDS, repeat=n)]


def simulate(target, a, b, rule, history_id):
    state = {'x': 1-target, 'y': 0, 'v': 0}
    trace = []
    def event(kind, detail=None):
        trace.append({'point': len(trace), 'kind': kind, 'detail': detail,
                      'state': dict(state)})
    event('initial')
    state['x'] = target
    state['v'] += 1
    receipt = {'account': 'synthetic-account', 'key': 'original',
               'target': 'synthetic-record', 'payload': {'set_x': target},
               'effect_number': 1, 'post_revision': state['v']}
    receipt_hash = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    event('first_effect_and_receipt', receipt)
    def external(word, gap):
        for cmd in word:
            if cmd == 'flip_y':
                state['y'] ^= 1
            else:
                state['x'] = int(cmd[-1])
            state['v'] += 1
            event('external_' + gap, cmd)
    external(a, 'A')
    observed = dict(state) if rule != 'R0' else None
    read_point = len(trace) if observed is not None else None
    if observed is not None:
        event('atomic_read')
    external(b, 'B')
    baseline = dict(state)
    mismatch = observed is not None and observed['x'] != target
    action = 'none'
    dispatched = accepted = hits = refusals = 0
    if mismatch and rule in ['R3', 'R4', 'R5']:
        dispatched = 1
        if rule == 'R3':
            action = 'original_receipt_replay'
            hits = 1
            event(action, receipt)
        elif rule == 'R5' and state['v'] != observed['v']:
            action = 'condition_refused'
            refusals = 1
            event(action, {'expected_revision': observed['v'], 'new_key': 'repair'})
        else:
            action = 'new_key_effect'
            accepted = 1
            state['x'] = target
            state['v'] += 1
            event(action, {'key': 'repair', 'set_x': target,
                          'expected_revision': observed['v'] if rule == 'R5' else None})
    current_claim = True
    if rule == 'R1':
        current_claim = observed['x'] == target
    elif rule == 'R2' or refusals:
        current_claim = None
    dated_claim = observed['x'] == target if rule == 'R2' else None
    event('reply', {'original_applied': True, 'current_match': current_claim,
                    'read_match': dated_claim, 'read_point': read_point if rule == 'R2' else None})
    # Independent scoring within this implementation reads trace states, not an
    # operation's success flag. A second program checks every row separately.
    actual_current = trace[-1]['state']['x'] == target
    first_applied = any(e['kind'] == 'first_effect_and_receipt' for e in trace)
    actual_at_read = trace[read_point]['state']['x'] == target if read_point is not None else None
    scores = {
        'false_history': int(not first_applied),
        'dated_claims': int(dated_claim is not None),
        'false_dated': int(dated_claim is not None and dated_claim != actual_at_read),
        'reply_claims': int(current_claim is not None),
        'reply_positive_claims': int(current_claim is True),
        'reply_negative_claims': int(current_claim is False),
        'false_positive': int(current_claim is True and not actual_current),
        'false_negative': int(current_claim is False and actual_current),
        'unknown': int(current_claim is None),
        'extra_effects': accepted,
        'overwrites': int(accepted and baseline['x'] != state['x']),
        'unrelated_damage': int(baseline['y'] != state['y']),
        'reads': int(observed is not None),
        'dispatches': dispatched,
        'receipt_hits': hits,
        'accepted_new_writes': accepted,
        'condition_refusals': refusals,
    }
    assert hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest() == receipt_hash
    return {'history_id': history_id, 'target': target, 'A': a, 'B': b, 'rule': rule,
            'receipt': receipt, 'read': observed, 'baseline': baseline,
            'final': dict(state), 'action': action,
            'claims': {'original_applied': True, 'current_match': current_claim,
                       'read_match': dated_claim, 'read_point': read_point if rule == 'R2' else None},
            'scores': scores, 'trace': trace}


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(destination):
    start = time.perf_counter()
    cpu_start = time.process_time()
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    cases = []
    for target in [0, 1]:
        for ai, a in enumerate(words()):
            for bi, b in enumerate(words()):
                hid = f't{target}-a{ai:02d}-b{bi:02d}'
                cases.append({'history_id': hid, 'target': target, 'A': a, 'B': b})
                for rule in RULES:
                    rows.append(simulate(target, a, b, rule, hid))
    assert len(cases) == 338 and len(rows) == 2028 < 10000
    for name, data in [('cases.jsonl', cases), ('results.jsonl', rows)]:
        with (destination/name).open('w') as f:
            for row in data:
                f.write(json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n')
    keys = list(rows[0]['scores'])
    totals = []
    for rule in RULES:
        selected = [r for r in rows if r['rule'] == rule]
        totals.append({'rule': rule, 'histories': len(selected),
                       **{k: sum(r['scores'][k] for r in selected) for k in keys}})
    write_csv(destination/'summary.csv', totals)
    pairs = []
    for l, r in itertools.combinations(totals, 2):
        pairs.append({'left': l['rule'], 'right': r['rule'],
                      **{k+'_right_minus_left': r[k]-l[k] for k in keys}})
    write_csv(destination/'paired_differences.csv', pairs)
    # Preserve all cases in the files above. This small subset supports hand checks.
    examples = [r for r in rows if r['target'] == 1 and
                (r['A'], r['B']) in [([], []), (['set0'], []), (['set1'], []),
                (['flip_y'], []), (['set0','set1'], []), ([], ['set0']),
                (['set0'], ['set1']), (['set0'], ['flip_y'])]]
    (destination/'examples.json').write_text(json.dumps(examples, indent=2)+'\n')
    # Controls pre-specified in plan.md.
    checks = {}
    checks['historical_and_dated_claims_correct'] = all(r['scores']['false_history'] == r['scores']['false_dated'] == 0 for r in rows)
    checks['no_y_damage'] = all(r['scores']['unrelated_damage'] == 0 for r in rows)
    checks['same_key_no_extra_effect'] = all(r['scores']['extra_effects'] == 0 for r in rows if r['rule'] == 'R3')
    checks['unconditional_new_key_accepts_dispatch'] = all(r['scores']['dispatches'] == r['scores']['accepted_new_writes'] for r in rows if r['rule'] == 'R4')
    checks['cas_accepts_dispatched_iff_B_empty'] = all(r['scores']['accepted_new_writes'] == int(not r['B']) for r in rows if r['rule'] == 'R5' and r['scores']['dispatches'])
    checks['no_background_control'] = all(not any(r['scores'][k] for k in ['false_positive','false_negative','extra_effects']) for r in rows if not r['A'] and not r['B'])
    lookup = {(r['target'], tuple(r['A']), tuple(r['B']), r['rule']): r for r in rows}
    def complement(word):
        return tuple({'set0':'set1','set1':'set0','flip_y':'flip_y'}[x] for x in word)
    checks['target_symmetry'] = all(r['scores'] == lookup[(1-r['target'], complement(r['A']), complement(r['B']), r['rule'])]['scores'] for r in rows)
    assert all(checks.values()), checks
    (destination/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    elapsed = time.perf_counter()-start
    cpu_elapsed = time.process_time()-cpu_start
    assert cpu_elapsed < 60, '60 CPU second execution gate exceeded'
    environment = {'python': platform.python_version(), 'implementation': platform.python_implementation(),
                   'platform': platform.platform(), 'elapsed_wall_seconds': elapsed,
                   'elapsed_cpu_seconds': cpu_elapsed,
                   'dependencies': 'Python standard library', 'random_seed': None,
                   'randomness': 'none', 'cases': len(cases), 'outcomes': len(rows)}
    (destination/'environment.json').write_text(json.dumps(environment, indent=2)+'\n')
    print(json.dumps({'checks': checks, 'environment': environment, 'totals': totals}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('results'))
    run(parser.parse_args().out)
