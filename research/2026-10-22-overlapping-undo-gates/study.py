#!/usr/bin/env python3
"""Complete finite gate study. Only the Python standard library is used."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import resource
import signal
import sys
import time

RULES = ('boolean', 'nonnegative_count', 'active_ids', 'lifecycle_registry')


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def dump(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_parts(label):
    return label[0], label[2], int(label[3])


def constraints(operations, flags):
    pred = {}
    for i, op in enumerate(operations):
        c, r = op + '_C0', op + '_R0'
        pred[c] = set()
        pred[r] = {c}
        if flags[2*i]:
            pred[op + '_C1'] = {c}
        if flags[2*i+1]:
            pred[op + '_R1'] = {r}
    return pred


def extensions(pred):
    def visit(prefix, used):
        if len(prefix) == len(pred):
            yield tuple(prefix)
            return
        for e in sorted(pred):
            if e not in used and pred[e] <= used:
                yield from visit(prefix + [e], used | {e})
    yield from visit([], set())


def permutation_enumerator(pred):
    """A separate algorithm for completeness; no recursive generator reuse."""
    for order in itertools.permutations(sorted(pred)):
        position = {e: i for i, e in enumerate(order)}
        if all(position[p] < position[e] for e, ps in pred.items() for p in ps):
            yield order


def expected_count(operations, flags):
    lengths, local = [], 1
    for i, _ in enumerate(operations):
        c, r = flags[2*i:2*i+2]
        lengths.append(2 + c + r)
        local *= 1 + c*(1+r)
    shuffles = math.factorial(sum(lengths))
    for n in lengths:
        shuffles //= math.factorial(n)
    return local * shuffles


def initial(rule):
    if rule == 'boolean':
        return False
    if rule == 'nonnegative_count':
        return 0
    return {} if rule == 'lifecycle_registry' else set()


def apply_rule(rule, state, operation, action):
    """No first/duplicate marker is supplied to a rule."""
    if rule == 'boolean':
        return action == 'C'
    if rule == 'nonnegative_count':
        return state + 1 if action == 'C' else max(0, state-1)
    if rule == 'active_ids':
        result = set(state)
        if action == 'C':
            result.add(operation)
        else:
            result.discard(operation)
        return result
    result = dict(state)
    if action == 'C' and operation not in result:
        result[operation] = 'active'
    elif action == 'R' and result.get(operation) == 'active':
        result[operation] = 'completed'
    return result


def state_view(rule, state):
    if rule == 'active_ids':
        return sorted(state)
    return dict(sorted(state.items())) if rule == 'lifecycle_registry' else state


def closed(rule, state):
    return ('active' in state.values()) if rule == 'lifecycle_registry' else bool(state)


def evaluate(history):
    states = {r: initial(r) for r in RULES}
    active = set()
    steps = []
    for i, event in enumerate(history):
        op, action, duplicate = event_parts(event)
        if not duplicate:
            if action == 'C':
                active.add(op)
            else:
                active.remove(op)
        output = {}
        for rule in RULES:
            states[rule] = apply_rule(rule, states[rule], op, action)
            blocked = closed(rule, states[rule])
            output[rule] = {'state': state_view(rule, states[rule]), 'closed': blocked,
                            'unsafe_open': bool(active) and not blocked,
                            'unnecessary_closed': not active and blocked}
        steps.append({'event_index': i, 'event': event, 'active_work': sorted(active),
                      'oracle_closed': bool(active), 'rules': output})
    score = {}
    for rule in RULES:
        unsafe = sum(s['rules'][rule]['unsafe_open'] for s in steps)
        blocked = sum(s['rules'][rule]['unnecessary_closed'] for s in steps)
        score[rule] = {'unsafe_points': unsafe, 'unnecessary_closed_points': blocked,
                       'unsafe_history': bool(unsafe), 'overblocked_history': bool(blocked),
                       'final_closed': closed(rule, states[rule])}
    return {'events': list(history), 'overlap': any(len(s['active_work']) > 1 for s in steps),
            'steps': steps, 'score': score}


def declarative_check(row):
    """Recompute from prefixes, positions, and closed-form rules."""
    history = row['events']
    ops = sorted({event_parts(e)[0] for e in history})
    positions = {event: i for i, event in enumerate(history)}
    comparisons = 0
    for i, saved in enumerate(row['steps']):
        prefix = history[:i+1]
        active = [op for op in ops if positions[op+'_C0'] <= i < positions[op+'_R0']]
        assert active == saved['active_work']
        walk = [0]
        for e in prefix:
            walk.append(walk[-1] + (1 if e[2] == 'C' else -1))
        by_op = {op: [e[2] for e in prefix if e[0] == op] for op in ops}
        expected_states = {
            'boolean': prefix[-1][2] == 'C',
            'nonnegative_count': walk[-1] - min(walk),
            'active_ids': [op for op, actions in by_op.items() if actions and actions[-1] == 'C'],
            'lifecycle_registry': {op: ('completed' if 'R' in actions else 'active')
                                   for op, actions in by_op.items() if actions}
        }
        for rule, state in expected_states.items():
            s = saved['rules'][rule]
            block = ('active' in state.values()) if rule == 'lifecycle_registry' else bool(state)
            assert s['state'] == state
            assert s['closed'] == block
            assert s['unsafe_open'] == (bool(active) and not block)
            assert s['unnecessary_closed'] == (not active and block)
            comparisons += 4
        comparisons += 1
    for rule in RULES:
        selected = [s['rules'][rule] for s in row['steps']]
        expect = {'unsafe_points': sum(s['unsafe_open'] for s in selected),
                  'unnecessary_closed_points': sum(s['unnecessary_closed'] for s in selected),
                  'unsafe_history': any(s['unsafe_open'] for s in selected),
                  'overblocked_history': any(s['unnecessary_closed'] for s in selected),
                  'final_closed': selected[-1]['closed'] if selected else False}
        assert expect == row['score'][rule]
        comparisons += 5
    return comparisons


def hand_checks():
    definitions = [
        ('empty', (), {r: (False, False) for r in RULES}),
        ('single_clean', ('A_C0','A_R0'), {r: (False, False) for r in RULES}),
        ('overlap_clean', ('A_C0','B_C0','A_R0','B_R0'),
         {r: (r == 'boolean', False) for r in RULES}),
        ('late_close', ('A_C0','A_R0','A_C1'),
         {r: (False, r != 'lifecycle_registry') for r in RULES}),
        ('extra_release', ('A_C0','B_C0','A_R0','A_R1','B_R0'),
         {r: (r in ('boolean','nonnegative_count'), False) for r in RULES}),
    ]
    rows = []
    for name, events, expected in definitions:
        row = evaluate(events)
        for rule, (unsafe, final) in expected.items():
            assert row['score'][rule]['unsafe_history'] == unsafe
            assert row['score'][rule]['final_closed'] == final
        row['name'] = name
        rows.append(row)
    return rows


def total(rows):
    out = {'histories': len(rows), 'points': sum(len(r['events']) for r in rows), 'rules': {}}
    for rule in RULES:
        out['rules'][rule] = dict(Counter({k: sum(r['score'][rule][k] for r in rows)
                                          for k in ('unsafe_points','unnecessary_closed_points',
                                                    'unsafe_history','overblocked_history','final_closed')}))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True, help='A new output directory')
    args = parser.parse_args()
    home = Path(__file__).resolve().parent
    config = json.loads((home/'config.json').read_text())
    freeze = json.loads((home/'freeze.json').read_text())
    for name, expected in freeze['sha256'].items():
        assert sha(home/name) == expected, 'Frozen input changed: '+name
    if args.out.exists():
        raise SystemExit('Output directory must not exist. Preserve previous runs.')
    args.out.mkdir(parents=True)
    out = args.out
    wall0, cpu0 = time.monotonic(), time.process_time()
    execution = {'started_utc': datetime.now(timezone.utc).isoformat(), 'status': 'running',
                 'command': ['python3','study.py','--out',str(args.out)],
                 'python': platform.python_version(), 'platform': platform.system(),
                 'release': platform.release(), 'machine': platform.machine(),
                 'source_sha256': sha(Path(__file__)), 'frozen_inputs': freeze['sha256'],
                 'random_seed': None, 'model_calls_in_trials': 0, 'paid_compute': False}
    dump(out/'execution.json', execution)
    log = []
    def timeout(signum, frame):
        raise RuntimeError('Wall limit reached')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(config['max_wall_seconds'])
    try:
        assert tuple(config['rules']) == RULES
        controls = hand_checks()
        dump(out/'hand_controls.json', controls)
        log.append('PASS five hand histories; 40 expected unsafe/final values')
        rows, counts, comparisons = [], [], 0
        raw = out/'raw_results.jsonl'
        with raw.open('w') as fp:
            for group, operations in [('single_operation',config['operations_control']),
                                      ('two_operations',config['operations_primary'])]:
                for flags in itertools.product(config['duplicate_choices'], repeat=2*len(operations)):
                    pred = constraints(operations, flags)
                    schedules = list(extensions(pred))
                    alternate = list(permutation_enumerator(pred))
                    expected = expected_count(operations, flags)
                    assert len(schedules) == expected
                    assert len(set(schedules)) == expected
                    assert schedules == alternate
                    counts.append({'group':group,'flags':list(flags),'count':len(schedules),
                                   'formula_count':expected,'permutation_count':len(alternate)})
                    for history in schedules:
                        row = evaluate(history)
                        row.update({'history_id':len(rows)+1,'group':group,
                                    'duplicate_flags':list(flags),'duplicate_count':sum(flags)})
                        comparisons += declarative_check(row)
                        if len(operations) == 2:
                            swapped = tuple(('B' if e[0]=='A' else 'A') + e[1:] for e in history)
                            assert evaluate(swapped)['score'] == row['score']
                        rows.append(row)
                        fp.write(encode(row)+'\n')
                        if time.process_time()-cpu0 >= config['max_cpu_seconds']:
                            raise RuntimeError('CPU limit reached')
                    log.append('PASS '+group+' flags='+''.join(map(str,flags))+' histories='+str(expected))
        primary = [r for r in rows if r['group']=='two_operations']
        single = [r for r in rows if r['group']=='single_operation']
        clean = [r for r in primary if r['duplicate_count']==0]
        duplicate = [r for r in primary if r['duplicate_count']>0]
        hypotheses = {
            'H1': total(clean)['rules']['boolean']['unsafe_history'] > 0 and all(
                total(clean)['rules'][r]['unsafe_history']==0 for r in RULES[1:]),
            'H2': total(duplicate)['rules']['nonnegative_count']['unsafe_history'] > 0 and
                  total(duplicate)['rules']['nonnegative_count']['final_closed'] > 0,
            'H3': total(rows)['rules']['active_ids']['unsafe_history']==0 and
                  total(rows)['rules']['active_ids']['final_closed'] > 0,
            'H4': all(total(rows)['rules']['lifecycle_registry'][k]==0 for k in
                      ('unsafe_points','unnecessary_closed_points'))}
        summary = {'primary':total(primary),'one_operation_controls':total(single),
                   'by_duplicate_count':{str(n):total([r for r in primary if r['duplicate_count']==n])
                                         for n in range(5)},
                   'by_work_overlap':{str(b).lower():total([r for r in primary if r['overlap']==b])
                                      for b in (False,True)},
                   'hypotheses': hypotheses, 'unknown_histories':0,
                   'total_histories':len(rows),'rule_history_outcomes':len(rows)*len(RULES)}
        dump(out/'summary.json',summary)
        witnesses = {}
        for rule in RULES:
            for issue in ('unsafe_history','final_closed'):
                found = [r for r in primary if r['score'][rule][issue]]
                if found:
                    witnesses[rule+'_'+issue] = min(found, key=lambda r:(len(r['events']),r['events']))
        dump(out/'witnesses.json', witnesses)
        checks = {'all_passed':True,'pattern_counts':counts,'declarative_comparisons':comparisons,
                  'unique_histories':len({tuple(r['events']) for r in rows}),
                  'saved_histories':len(rows),'symmetric_two_operation_histories':len(primary),
                  'hand_histories':len(controls),'hand_expected_values':40,
                  'duplicate_metadata_not_given_to_rules':True}
        assert checks['unique_histories'] == len(rows)
        assert all(hypotheses.values())
        dump(out/'checks.json',checks)
        log.append('PASS hypotheses H1-H4; no unknown or excluded histories')
        execution['status'] = 'complete'
        execution['output_sha256'] = {p.name:sha(p) for p in sorted(out.iterdir())
                                       if p.name not in ('execution.json','run.log')}
    except BaseException as exc:
        execution['status'] = 'failed'
        execution['error'] = type(exc).__name__ + ': ' + str(exc)
        log.append('FAIL '+execution['error'])
        raise
    finally:
        signal.alarm(0)
        execution.update({'finished_utc':datetime.now(timezone.utc).isoformat(),
                          'cpu_seconds':time.process_time()-cpu0,
                          'wall_seconds':time.monotonic()-wall0,
                          'peak_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        dump(out/'execution.json',execution)
        (out/'run.log').write_text('\n'.join(log)+'\n')
    print(encode({'status':execution['status'],'histories':summary['total_histories'],
                  'cpu_seconds':execution['cpu_seconds'],'wall_seconds':execution['wall_seconds']}))


if __name__ == '__main__':
    main()
