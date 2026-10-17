#!/usr/bin/env python3
"""Independent exhaustive implementation of the frozen October 17 plan.

This file does not import or call the main analysis program. The state is a
four-element list in A, X, Y, U order. The generator directly visits every
initial record and every assigned gap program. Outputs are exact corpus counts.
"""
from __future__ import annotations
import argparse
import copy
import csv
import gzip
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

POLICIES = ('replace', 'patch', 'refresh_cas', 'replan_cas',
            'dependency_guard', 'source_only_guard')
BAD = ('permission_violation', 'source_violation', 'semantic_invalid',
       'collateral', 'bad_union')
COUNT = ('rounds', 'attempts', 'rejections', 'harmless_rejections',
         'background_writes')
FIELD_POSITION = (0, 1, 3)
EXPECTED_CONFIG = {
    'attempt_budgets': [1, 2, 3], 'writes_per_gap': [0, 1, 2],
    'fields': ['A', 'X', 'Y', 'U'], 'background_fields': ['A', 'X', 'U'],
    'policies': list(POLICIES), 'initial_permission': 1,
    'initial_target': 'one_minus_X',
    'task': 'Y_equals_precommit_X_when_precommit_A_is_one',
    'revision': 'atomic_nonreused_integer',
    'unused_suffix': 'not_executed_but_assignment_counted',
    'random_sampling': False,
}


def validate_config(obj):
    # This reproduction is bound to the declared finite corpus. Do not silently
    # accept a different experiment or JSON booleans as integer budgets.
    if type(obj) is not dict or obj != EXPECTED_CONFIG:
        raise ValueError('Configuration is not the frozen experiment.')
    for name in ('attempt_budgets', 'writes_per_gap'):
        if any(type(v) is not int for v in obj[name]):
            raise ValueError('Grid entries must be integers.')
    if type(obj['initial_permission']) is not int:
        raise ValueError('Initial permission must be integer one.')
    if type(obj['random_sampling']) is not bool:
        raise ValueError('Random sampling flag must be boolean.')
    return obj


def read_config(path):
    return validate_config(json.loads(Path(path).read_text()))


def evaluate(initial, program, policy):
    """Run a policy until its own success, denial, or exhausted budget."""
    if policy not in POLICIES:
        raise ValueError('Unknown policy.')
    initial = tuple(initial)
    state = list(initial)
    revision = 0
    out = {k: 0 for k in COUNT}
    out.update({k: False for k in BAD})
    out['decision'] = 'exhausted'
    out['events'] = []
    read_permission = policy in ('replan_cas', 'dependency_guard', 'source_only_guard')
    for index, word in enumerate(program, 1):
        out['rounds'] = index
        snapshot, read_revision = tuple(state), revision
        out['events'].append({'kind': 'read', 'round': index,
                              'state': list(snapshot), 'revision': read_revision})
        if read_permission and snapshot[0] == 0:
            out['decision'] = 'read_denied'
            out['events'].append({'kind': 'read_denied', 'round': index,
                                  'state': state[:], 'revision': revision})
            break
        candidate = snapshot[1] if read_permission else initial[1]
        for symbol in word:
            state[FIELD_POSITION[symbol]] ^= 1
            revision += 1
            out['background_writes'] += 1
            out['events'].append({'kind': 'background', 'round': index,
                                  'field': symbol, 'state': state[:],
                                  'revision': revision})
        precommit = tuple(state)
        out['attempts'] += 1
        if policy in ('replace', 'patch'):
            passes = True
        elif policy in ('refresh_cas', 'replan_cas'):
            passes = revision == read_revision
        elif policy == 'dependency_guard':
            passes = (state[0], state[1]) == (snapshot[0], snapshot[1])
        else:
            passes = state[1] == snapshot[1]
        event = {'kind': 'commit', 'round': index, 'pre_state': list(precommit),
                 'pre_revision': revision, 'candidate': candidate,
                 'accepted': passes}
        if passes:
            out['permission_violation'] = precommit[0] == 0
            out['source_violation'] = candidate != precommit[1]
            out['semantic_invalid'] = out['permission_violation'] or out['source_violation']
            if policy == 'replace':
                state = list(initial)
            state[2] = candidate
            revision += 1
            out['collateral'] = any(state[j] != precommit[j] for j in (0, 1, 3))
            out['bad_union'] = out['semantic_invalid'] or out['collateral']
            out['decision'] = 'success'
        else:
            out['rejections'] += 1
            out['harmless_rejections'] += int(precommit[0] == 1 and candidate == precommit[1])
        event.update({'post_state': state[:], 'post_revision': revision})
        out['events'].append(event)
        if passes:
            break
    out['finalstate'] = state
    out['revision'] = revision
    return out


def rank_witness(row):
    return (row['background_writes'], row['rounds'], tuple(row['initial']),
            tuple(tuple(word) for word in row['program']))


def iter_assignments(K, b):
    alphabet = tuple(itertools.chain.from_iterable(
        itertools.product(range(3), repeat=n) for n in range(b + 1)))
    for x, u in itertools.product((0, 1), repeat=2):
        initial = (1, x, 1-x, u)
        for program in itertools.product(alphabet, repeat=K):
            yield initial, program


def pair_subset(program):
    unrelated = all(word and all(t == 2 for t in word) for word in program)
    even = lambda word: word.count(0) % 2 == 0 and word.count(1) % 2 == 0
    returned = (bool(program[0]) and any(t in (0, 1) for t in program[0])
                and even(program[0]) and all(word and even(word) for word in program[1:]))
    assert not (unrelated and returned)
    return unrelated, returned


def write_csv(path, rows):
    with Path(path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def enumerate_all(config, outdir):
    summaries, paired, witnesses = [], [], []
    full = {}
    for K in config['attempt_budgets']:
        for b in config['writes_per_gap']:
            counters = {p: Counter() for p in POLICIES}
            best = {}
            pair = Counter()
            total = 0
            for initial, program in iter_assignments(K, b):
                total += 1
                results = {}
                for policy in POLICIES:
                    row = {'K': K, 'b': b, 'initial': list(initial),
                           'program': [list(word) for word in program], 'policy': policy}
                    row.update(evaluate(initial, program, policy))
                    results[policy] = row
                    key = (K, b, initial, program, policy)
                    full[key] = row
                    c = counters[policy]
                    c['assignments'] += 1
                    c[row['decision']] += 1
                    for name in BAD + COUNT:
                        c[name] += int(row[name])
                    c['any_harmless_rejection'] += int(row['harmless_rejections'] > 0)
                    for outcome in BAD:
                        if row[outcome] and ((policy, outcome) not in best or
                                rank_witness(row) < rank_witness(best[policy, outcome])):
                            best[policy, outcome] = row
                replacement = results['replace']
                patch = results['patch']
                pair['replace_collateral_patch_none'] += int(replacement['collateral'] and not patch['collateral'])
                complete = results['dependency_guard']
                replan = results['replan_cas']
                if complete['decision'] == 'success' and replan['decision'] == 'exhausted':
                    pair['dependency_success_replan_exhausted'] += 1
                    unrelated, returned = pair_subset(program)
                    pair['unrelated_only'] += int(unrelated)
                    pair['returned_dependency'] += int(returned)
                    pair['other_paired'] += int(not unrelated and not returned)
            expected = 4 * sum(3**j for j in range(b + 1))**K
            assert total == expected
            for p in POLICIES:
                c = counters[p]
                assert c['success'] + c['read_denied'] + c['exhausted'] == expected
                assert c['bad_union'] <= c['success']
                assert c['semantic_invalid'] <= c['bad_union']
                assert c['harmless_rejections'] <= c['rejections'] <= c['attempts']
                if p in ('replan_cas', 'dependency_guard'):
                    assert c['bad_union'] == 0
                if p != 'replace':
                    assert c['collateral'] == 0
                if p == 'source_only_guard':
                    assert c['source_violation'] == 0
                if p == 'refresh_cas' and K == 1:
                    assert c['bad_union'] == 0
                if b == 0:
                    assert c['success'] == 4 and c['bad_union'] == 0
                summaries.append(dict(K=K, b=b, policy=p, **{n:c[n] for n in (
                    'assignments', 'success', 'read_denied', 'exhausted', *COUNT,
                    *BAD, 'any_harmless_rejection')}))
            paired.append(dict(K=K, b=b, assignments=total, **{n:pair[n] for n in (
                'replace_collateral_patch_none', 'dependency_success_replan_exhausted',
                'unrelated_only', 'returned_dependency', 'other_paired')}))
            for (p, outcome), row in sorted(best.items()):
                witnesses.append({'outcome': outcome, **row})
    outdir.mkdir(exist_ok=True, parents=True)
    write_csv(outdir / 'independent_results.csv', summaries)
    write_csv(outdir / 'independent_pairs.csv', paired)
    (outdir / 'independent_witnesses.json').write_text(json.dumps(witnesses, indent=2) + '\n')
    return full, summaries, paired, witnesses


def semantic_controls():
    ini = (1, 0, 1, 0)
    checks = 0
    # A newer token attached to the original candidate must fail after an X conflict.
    stale = evaluate(ini, ((1,), ()), 'refresh_cas')
    assert stale['decision'] == 'success' and stale['source_violation'] and stale['attempts'] == 2
    checks += 1
    # A fresh token does not repair the old permission decision either.
    denied = evaluate(ini, ((0,), ()), 'refresh_cas')
    assert denied['permission_violation'] and denied['finalstate'][0] == 0
    checks += 1
    # A permission denial ends before the second background word.
    stopped = evaluate(ini, ((0,), (0, 1)), 'replan_cas')
    assert stopped['decision'] == 'read_denied' and stopped['rounds'] == 2
    assert stopped['attempts'] == 1 and stopped['background_writes'] == 1
    checks += 1
    # Whole replacement restores outside fields; its apparently valid final state is insufficient.
    replaced = evaluate(ini, ((0, 1),), 'replace')
    assert replaced['finalstate'] == [1, 0, 0, 0] and replaced['collateral']
    assert replaced['permission_violation'] and replaced['source_violation']
    checks += 1
    # U-only interference and returned X each admit the dependency guard, but not strict CAS.
    for program in (((2,),), ((1, 1),)):
        assert evaluate(ini, program, 'dependency_guard')['decision'] == 'success'
        r = evaluate(ini, program, 'replan_cas')
        assert r['decision'] == 'exhausted' and r['harmless_rejections'] == 1
        checks += 1
    assert evaluate(ini, ((0,),), 'source_only_guard')['permission_violation']
    checks += 1
    # Source-only permission check at the beginning of the round is insufficient.
    assert evaluate(ini, ((1, 1),), 'dependency_guard')['revision'] == 3
    checks += 1
    # Unused suffixes do not run, but count as distinct assigned scenarios.
    first = evaluate(ini, ((), (0, 1), (2,)), 'dependency_guard')
    second = evaluate(ini, ((), (1,), ()), 'dependency_guard')
    assert first == second and first['rounds'] == 1 and first['background_writes'] == 0
    checks += 1
    # A return in a suffix after a U-only success is outside the returned-dependency subset.
    assert pair_subset(((2,), (1, 1))) == (False, False)
    assert pair_subset(((1, 1), (2,))) == (False, True)
    checks += 1
    return checks


def config_controls():
    invalid = []
    for name in EXPECTED_CONFIG:
        value = copy.deepcopy(EXPECTED_CONFIG)
        del value[name]
        invalid.append(value)
    for key, value in (
        ('attempt_budgets', [True, 2, 3]), ('attempt_budgets', [0, 1, 2]),
        ('attempt_budgets', [1, 2, 3, 3]), ('attempt_budgets', '1,2,3'),
        ('writes_per_gap', [False, 1, 2]), ('writes_per_gap', [0, 1, -2]),
        ('writes_per_gap', [0, 1.0, 2]), ('initial_permission', True),
        ('random_sampling', 0), ('random_sampling', True),
        ('background_fields', ['A', 'X', 'Y']), ('revision', 'wraps'),
    ):
        obj = copy.deepcopy(EXPECTED_CONFIG)
        obj[key] = value
        invalid.append(obj)
    invalid.extend([None, [], 'config', {**EXPECTED_CONFIG, 'extra': 1}])
    for obj in invalid:
        try:
            validate_config(obj)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Malformed input accepted: {obj}')
    assert validate_config(copy.deepcopy(EXPECTED_CONFIG)) == EXPECTED_CONFIG
    return len(invalid)


def symmetry_controls(full):
    checked = 0
    for key, row in full.items():
        K, b, initial, program, policy = key
        for indexes in ((1, 2), (3,)):
            alternate_initial = tuple(v ^ int(j in indexes) for j, v in enumerate(initial))
            other = full[K, b, alternate_initial, program, policy]
            for field in (*BAD, *COUNT, 'decision', 'revision'):
                assert row[field] == other[field]
            expected_final = [v ^ int(j in indexes) for j, v in enumerate(row['finalstate'])]
            assert expected_final == other['finalstate']
            checked += 1
    return checked


def trace_key(row):
    return (row['K'], row['b'], tuple(row['initial']),
            tuple(tuple(word) for word in row['program']), row['policy'])


def main_schema(row):
    """Map the independently computed record to the published trace schema.

    Only data schemas, not main source code, were inspected to write this
    adapter. The independent transition function above is not changed here.
    """
    out = {k: row[k] for k in ('K', 'b', 'initial', 'program', 'policy',
                              'decision', *COUNT)}
    out.update({k: int(row[k]) for k in BAD})
    out.update({k: int(row['decision'] == k) for k in ('success', 'read_denied', 'exhausted')})
    out['final_state'] = row['finalstate']
    out['final_revision'] = row['revision']
    out['before_effect'] = None
    out['collateral_fields'] = []
    events = []
    state = row['initial'][:]
    for event in row['events']:
        kind = event['kind']
        if kind == 'read':
            events.append(event)
            assert state == event['state']
        elif kind == 'read_denied':
            events.append({**event, 'kind': 'deny'})
        elif kind == 'background':
            events.append({'kind': kind, 'round': event['round'],
                           'field': event['field'], 'before': state[:],
                           'after': event['state'], 'revision': event['revision']})
            state = event['state'][:]
        else:
            assert kind == 'commit'
            pre = event['pre_state']
            assert state == pre
            events.append({'kind': 'guard', 'round': event['round'],
                           'state': pre, 'revision': event['pre_revision'],
                           'candidate': event['candidate'], 'passed': event['accepted'],
                           'valid_y_only_effect': pre[0] == 1 and event['candidate'] == pre[1]})
            if event['accepted']:
                events.append({'kind': 'commit', 'round': event['round'],
                               'before': pre, 'after': event['post_state'],
                               'revision': event['post_revision']})
                out['before_effect'] = pre
                out['collateral_fields'] = [name for j, name in ((0, 'A'), (1, 'X'), (3, 'U'))
                                            if pre[j] != event['post_state'][j]]
                state = event['post_state'][:]
    out['events'] = events
    return out


def compare_main(directory, full, summaries, paired, witnesses):
    checked_rows, checked_events, seen = 0, 0, set()
    with gzip.open(directory / 'traces.jsonl.gz', 'rt') as f:
        for line in f:
            row = json.loads(line)
            key = trace_key(row)
            assert key not in seen, ('duplicate trace', key)
            seen.add(key)
            expected = main_schema(full[key])
            assert row == expected, ('trace mismatch', key,
                                     {k:(expected.get(k), row.get(k)) for k in set(row)|set(expected)
                                      if row.get(k) != expected.get(k)})
            checked_rows += 1
            checked_events += len(row['events'])
    assert seen == set(full)
    expected_aggregates = {(r['K'], r['b'], r['policy']):r for r in summaries}
    seen_aggregates = set()
    scalar_count = 0
    with (directory / 'results.csv').open(newline='') as f:
        for raw in csv.DictReader(f):
            row = {k: v if k == 'policy' else int(v) for k,v in raw.items()}
            key = row['K'], row['b'], row['policy']
            assert key not in seen_aggregates
            seen_aggregates.add(key)
            for name, value in row.items():
                assert value == expected_aggregates[key][name], ('aggregate', key, name)
                if name not in ('K', 'b', 'policy'):
                    scalar_count += 1
    assert seen_aggregates == set(expected_aggregates)
    expected_pairs = {(r['K'],r['b']):r for r in paired}
    main_pairs = json.loads((directory / 'paired_results.json').read_text())
    assert len(main_pairs) == len(expected_pairs)
    seen_pairs = set()
    for row in main_pairs:
        key = row['K'], row['b']
        assert key not in seen_pairs
        seen_pairs.add(key)
        for name, value in row.items():
            other = 'dependency_success_replan_exhausted' if name == 'dependency_success_cas_exhausted' else name
            assert value == expected_pairs[key][other], ('paired', key, name)
    assert seen_pairs == set(expected_pairs)
    expected_witness = {(r['K'],r['b'],r['policy'],r['outcome']):r for r in witnesses}
    main_witness = json.loads((directory / 'witnesses.json').read_text())
    assert len(main_witness) == len(expected_witness)
    seen_witness = set()
    for value in main_witness:
        row = value['case']
        key = row['K'], row['b'], row['policy'], value['outcome']
        assert key not in seen_witness
        seen_witness.add(key)
        assert row == main_schema(expected_witness[key]), ('witness', key)
        assert value['minimum_consumed_writes'] == expected_witness[key]['background_writes']
    assert seen_witness == set(expected_witness)
    names = ('traces.jsonl.gz', 'results.csv', 'paired_results.json', 'witnesses.json',
             'analysis_plan.md', 'config.json', 'input_manifest.json')
    return {'status': 'PASS', 'policy_scenario_rows': checked_rows,
            'events': checked_events, 'aggregate_rows': len(seen_aggregates),
            'aggregate_scalar_values': scalar_count, 'paired_rows': len(seen_pairs),
            'minimal_witnesses': len(seen_witness),
            'witness_ties_and_full_traces': 'PASS',
            'sha256': {name: hashlib.sha256((directory/name).read_bytes()).hexdigest()
                       for name in names}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, default=Path('.'))
    parser.add_argument('--output-dir', type=Path, default=Path('.'))
    parser.add_argument('--compare-main', type=Path)
    args = parser.parse_args()
    config = read_config(args.input_dir / 'config.json')
    manifest = json.loads((args.input_dir / 'input_manifest.json').read_text())
    for name, expected in manifest['sha256'].items():
        assert hashlib.sha256((args.input_dir/name).read_bytes()).hexdigest() == expected
    controls = semantic_controls()
    invalid_rejected = config_controls()
    full, summary, paired, witnesses = enumerate_all(config, args.output_dir)
    transformed_rows = symmetry_controls(full)
    comparison = None
    if args.compare_main is not None:
        comparison = compare_main(args.compare_main, full, summary, paired, witnesses)
        (args.output_dir/'independent_comparison.json').write_text(json.dumps(comparison, indent=2)+'\n')
    receipt = {'status': 'independent_enumeration_complete',
               'policy_scenario_rows': len(full), 'aggregate_rows': len(summary),
               'paired_rows': len(paired), 'minimal_witnesses': len(witnesses),
               'handcrafted_controls': controls,
               'malformed_configurations_rejected': invalid_rejected,
               'symmetry_rows_checked': transformed_rows,
               'main_code_read_or_imported': False,
               'frozen_inputs_match': True}
    if comparison is not None:
        receipt['main_comparison'] = comparison['status']
    (args.output_dir/'independent_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
