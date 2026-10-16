#!/usr/bin/env python3
"""Independent finite-history audit. Uses only the Python standard library.

This program does not import or call the main analysis. A separate agent wrote it
from the frozen plan. It keeps a complete count distribution and one lexical
path for each state. Paths are needed only for exact minimum-write witnesses.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path

POLICIES = ('values', 'full_revision', 'modulo_2', 'modulo_4',
            'partial_revision', 'atomic_final')
EXPECTED = {
    'fields': [2, 3], 'passes': [1, 2, 3], 'writes_per_gap': [0, 1, 2],
    'policies': list(POLICIES), 'partial_revision_field': 'last',
    'read_order': 'ascending', 'target': 'all_ones',
    'writes': 'atomic_single_bit_flip', 'initial_revision': 0,
    'seed': None, 'random_sampling': False,
}


def validate_config(cfg):
    """Reject a changed or incomplete frozen model, including bool-as-int."""
    if type(cfg) is not dict or set(cfg) != set(EXPECTED):
        raise ValueError('The input must have every declared key and no extra key.')
    for key, expected in EXPECTED.items():
        got = cfg[key]
        if type(got) is not type(expected) or got != expected:
            raise ValueError('Unsupported model value: ' + key)
        if isinstance(expected, list):
            if any(type(a) is not type(b) for a, b in zip(got, expected)):
                raise ValueError('Wrong model member type: ' + key)
    return cfg


def words(d, b):
    return sorted(t for n in range(b + 1) for t in product(range(d), repeat=n))


def evolve(bits, word):
    now = list(bits)
    saw = all(now)
    for field in word:
        now[field] ^= 1
        saw |= all(now)
    return tuple(now), bool(saw)


def accepted(state, policy):
    bits, ever, good, writes, last = state
    if policy == 'atomic_final':
        return all(bits)
    if not good:
        return False
    return {'values': True, 'full_revision': writes == 0,
            'modulo_2': writes % 2 == 0, 'modulo_4': writes % 4 == 0,
            'partial_revision': last == 0}[policy]


def distribution_rows(counts):
    return [{'bits': list(s[0]), 'ever_target': s[1],
             'all_reads_target': s[2], 'total_writes': s[3],
             'last_field_writes': s[4], 'histories': n}
            for s, n in sorted(counts.items())]


def replay(d, r, initial, gaps):
    bits = tuple(initial)
    ever = all(bits)
    good = True
    writes = last = 0
    trace = [{'event': 'initial_revision', 'revision': 0, 'bits': list(bits)}]
    if len(gaps) != d * r + 1:
        raise ValueError('Wrong gap count')
    for gap_index, word in enumerate(gaps):
        for field in word:
            if type(field) is not int or field not in range(d):
                raise ValueError('Wrong field')
            now = list(bits)
            now[field] ^= 1
            bits = tuple(now)
            writes += 1
            last += field == d - 1
            ever |= all(bits)
            trace.append({'event': 'write', 'gap': gap_index, 'field': field,
                          'revision': writes, 'partial_revision': last,
                          'bits': list(bits)})
        if gap_index < d * r:
            field = gap_index % d
            value = bits[field]
            good &= value == 1
            trace.append({'event': 'read', 'read': gap_index, 'field': field,
                          'value': value, 'bits': list(bits)})
    trace.append({'event': 'final_revision_and_decision', 'revision': writes,
                  'partial_revision': last, 'bits': list(bits)})
    return (bits, bool(ever), bool(good), writes, last), trace


def audit_setting(d, r, b):
    allowed = words(d, b)
    counts = {}
    best = {}
    for initial in product((0, 1), repeat=d):
        state = (initial, all(initial), True, 0, 0)
        counts[state] = 1
        best[state] = (initial, ())
    stages = []
    transitions = {(bits, word): evolve(bits, word)
                   for bits in product((0, 1), repeat=d) for word in allowed}
    for gap in range(d * r + 1):
        next_counts = defaultdict(int)
        next_best = {}
        for state, count in counts.items():
            bits, ever, good, writes, last = state
            initial, old_words = best[state]
            for word in allowed:
                new_bits, saw = transitions[bits, word]
                new_good = good and (gap == d*r or new_bits[gap % d] == 1)
                new_state = (new_bits, ever or saw, new_good,
                             writes + len(word), last + word.count(d - 1))
                next_counts[new_state] += count
                path = (initial, old_words + (word,))
                if new_state not in next_best or path < next_best[new_state]:
                    next_best[new_state] = path
        counts, best = dict(next_counts), next_best
        expected = 2**d * len(allowed)**(gap + 1)
        assert sum(counts.values()) == expected
        stages.append({'gap_done': gap, 'read_done': gap if gap < d*r else None,
                       'state_count': len(counts), 'histories': expected})
    results = []
    witnesses = []
    total = sum(counts.values())
    for policy in POLICIES:
        sets = {
            'accepted': [s for s in counts if accepted(s, policy)],
            'no_common_target': [s for s in counts if accepted(s, policy) and not s[1]],
            'wrong_at_decision': [s for s in counts if accepted(s, policy) and not all(s[0])],
            'rejected_correct_final': [s for s in counts if not accepted(s, policy) and all(s[0])],
        }
        row = {'d': d, 'r': r, 'b': b, 'policy': policy, 'total_histories': total}
        row.update({name: sum(counts[s] for s in selected) for name, selected in sets.items()})
        row['accept_fraction'] = str(Fraction(row['accepted'], total))
        row['no_common_given_accepted'] = (str(Fraction(row['no_common_target'], row['accepted']))
                                         if row['accepted'] else None)
        row['wrong_given_accepted'] = (str(Fraction(row['wrong_at_decision'], row['accepted']))
                                     if row['accepted'] else None)
        for outcome in ('no_common_target', 'wrong_at_decision'):
            selected = sets[outcome]
            row['minimum_writes_' + outcome] = None
            if not selected:
                continue
            chosen = min(selected, key=lambda s: (s[3], best[s]))
            initial, gaps = best[chosen]
            check, trace = replay(d, r, initial, gaps)
            assert check == chosen
            assert accepted(check, policy)
            assert (not check[1]) if outcome == 'no_common_target' else (not all(check[0]))
            row['minimum_writes_' + outcome] = check[3]
            witnesses.append({'d': d, 'r': r, 'b': b, 'policy': policy,
                              'outcome': outcome, 'writes': check[3],
                              'initial': list(initial), 'gaps': [list(w) for w in gaps],
                              'trace': trace})
        assert row['no_common_target'] <= row['wrong_at_decision'] <= row['accepted']
        if policy in ('full_revision', 'atomic_final'):
            assert row['no_common_target'] == row['wrong_at_decision'] == 0
        if policy == 'full_revision':
            assert row['accepted'] == 1
        if policy == 'atomic_final':
            assert row['accepted'] == total // 2**d
            assert row['rejected_correct_final'] == 0
        if d == 2 and b == 2 and policy == 'values':
            assert row['minimum_writes_no_common_target'] == 2 * (2*r - 1)
        if d == 2 and policy == 'partial_revision':
            assert row['no_common_target'] == 0
        results.append(row)
    return counts, best, stages, results, witnesses


def brute_setting(d, r, b):
    """Direct product of complete histories; no state merging."""
    hist = defaultdict(int)
    best = {}
    for initial in product((0, 1), repeat=d):
        for gaps in product(words(d, b), repeat=d*r + 1):
            state, _ = replay(d, r, initial, gaps)
            hist[state] += 1
            path = (initial, gaps)
            if state not in best or path < best[state]:
                best[state] = path
    return dict(hist), best


def malformed_checks(config):
    malformed = [None, [], {}, dict(config, unexpected=True)]
    for key in config:
        item = dict(config)
        del item[key]
        malformed.append(item)
    for key, value in [('fields', [True, 3]), ('passes', [1, 2, 2]),
                       ('writes_per_gap', [0, 1, 3]), ('initial_revision', False),
                       ('initial_revision', 1), ('random_sampling', 0),
                       ('random_sampling', True), ('seed', 3), ('target', 'all_zero'),
                       ('writes', 'whole_record'), ('read_order', 'descending'),
                       ('partial_revision_field', 0), ('policies', list(POLICIES[:-1]))]:
        malformed.append(dict(config, **{key: value}))
    failures = []
    for number, bad in enumerate(malformed):
        try:
            validate_config(bad)
        except (ValueError, TypeError):
            continue
        failures.append(number)
    assert not failures, failures
    return len(malformed)


def symmetry_checks(d, r, b):
    """Re-label fields and target values on each small complete history.

    The partial counter moves with its covered field. The read order moves
    with the labels. A fixed ascending order is not invariant if labels alone
    move, so that different experiment is not asserted here.
    """
    checks = 0
    for initial in product((0, 1), repeat=d):
        for gaps in product(words(d, b), repeat=d*r + 1):
            reference, _ = replay(d, r, initial, gaps)
            for perm in permutations(range(d)):
                for mask in (tuple(0 for _ in range(d)), tuple(1 for _ in range(d))):
                    now = [0] * d
                    target = [0] * d
                    for old in range(d):
                        now[perm[old]] = initial[old] ^ mask[old]
                        target[perm[old]] = 1 ^ mask[old]
                    ever = now == target
                    good = True
                    writes = covered = 0
                    for gap, word in enumerate(gaps):
                        for old_field in word:
                            field = perm[old_field]
                            now[field] ^= 1
                            writes += 1
                            covered += field == perm[d - 1]
                            ever |= now == target
                        if gap < d*r:
                            field = perm[gap % d]
                            good &= now[field] == target[field]
                    restored = tuple(now[perm[old]] ^ mask[old] for old in range(d))
                    actual = (restored, ever, good, writes, covered)
                    assert actual == reference, (d, r, b, initial, gaps, perm, mask)
                    checks += 1
    return checks


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    cfg = validate_config(json.loads(args.config.read_text()))
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    malformed = malformed_checks(cfg)
    rows, witnesses, terminals, stage_records, brute_checks = [], [], [], [], []
    symmetry_total = 0
    for d, r, b in product(cfg['fields'], cfg['passes'], cfg['writes_per_gap']):
        counts, best, stages, policy_rows, paths = audit_setting(d, r, b)
        rows += policy_rows
        witnesses += paths
        terminals.append({'d': d, 'r': r, 'b': b, 'states': distribution_rows(counts)})
        stage_records.append({'d': d, 'r': r, 'b': b, 'stages': stages})
        required = b == 0 or (d == 2 and r == 1) or (d == 2 and r == 2 and b == 1) or (d == 3 and r == 1 and b == 1)
        if required:
            brute, brute_paths = brute_setting(d, r, b)
            assert brute == counts, (d, r, b, 'distribution')
            assert brute_paths == best, (d, r, b, 'paths')
            symmetry_count = symmetry_checks(d, r, b)
            symmetry_total += symmetry_count
            brute_checks.append({'d': d, 'r': r, 'b': b, 'histories': sum(brute.values()),
                                 'full_distribution_equal': True, 'all_lexical_paths_equal': True,
                                 'permutation_and_target_relabel_checks': symmetry_count})
    assert len(rows) == 108
    dump(out / 'independent_policy_results.json', rows)
    dump(out / 'independent_terminal_distribution.json', terminals)
    dump(out / 'independent_witnesses.json', witnesses)
    dump(out / 'independent_stage_totals.json', stage_records)
    dump(out / 'independent_self_checks.json', {
        'status': 'PASS', 'settings': 18, 'policy_rows': len(rows),
        'witnesses_replayed': len(witnesses), 'malformed_inputs_rejected': malformed,
        'permutation_and_target_relabel_checks': symmetry_total,
        'brute_force_settings': brute_checks,
        'checks': ['stage_conservation', 'full_revision_zero_false', 'full_revision_accepts_one',
                   'atomic_final_uniform_count', 'atomic_final_zero_false',
                   'no_common_implies_wrong', 'two_field_minimum_writes',
                   'two_field_partial_no_common_zero'],
        'scope': 'Independent synthetic computation. No website or account was used.'})
    print(json.dumps({'status': 'PASS', 'policy_rows': len(rows), 'witnesses': len(witnesses),
                      'malformed_inputs_rejected': malformed, 'brute_force_settings': len(brute_checks)}))


if __name__ == '__main__':
    main()
