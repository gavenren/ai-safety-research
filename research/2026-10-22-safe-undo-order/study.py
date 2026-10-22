#!/usr/bin/env python3
"""Exact synthetic undo-order study. Python standard library only."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import resource
import signal
import sys
import time
import traceback


def encode(state, n):
    return format(state, f'0{n}b')


def conditions(n):
    internal = list(range(1, (1 << n) - 1))
    for condition in range(1 << len(internal)):
        yield condition, {0, (1 << n) - 1} | {
            state for bit, state in enumerate(internal) if condition & (1 << bit)
        }


def clear(state, field, n):
    return state & ~(1 << (n - 1 - field))


def remaining(state, field, n):
    return bool(state & (1 << (n - 1 - field)))


def run_rule(n, valid, priority, rule):
    state = (1 << n) - 1
    trace, actions, checks = [state], [], 0
    if rule == 'complete':
        selected = None
        for order in itertools.permutations(priority):
            probe = state
            safe = True
            for field in order:
                probe = clear(probe, field, n)
                checks += 1
                if probe not in valid:
                    safe = False
                    break
            if safe:
                selected = order
                break
        if selected is None:
            return trace, actions, checks, 'refused_before_action'
        for field in selected:
            state = clear(state, field, n)
            trace.append(state)
            actions.append(field)
    elif rule == 'fixed':
        for field in priority:
            state = clear(state, field, n)
            trace.append(state)
            actions.append(field)
    elif rule == 'greedy':
        while state:
            selected = None
            for field in priority:
                if remaining(state, field, n):
                    checks += 1
                    if clear(state, field, n) in valid:
                        selected = field
                        break
            if selected is None:
                status = 'partial_stop' if actions else 'refused_before_action'
                return trace, actions, checks, status
            state = clear(state, selected, n)
            trace.append(state)
            actions.append(selected)
    else:
        raise ValueError(rule)
    return trace, actions, checks, 'target_reached'


def graph_reachable(state, valid):
    """Separate set-based graph oracle. Does not use action orders or run_rule."""
    frontier = {state}
    visited = set()
    while frontier:
        node = frontier.pop()
        if node == 0:
            return True
        visited.add(node)
        bit = 1
        while bit <= node:
            if node & bit:
                child = node - bit
                if child in valid and child not in visited:
                    frontier.add(child)
            bit <<= 1
    return False


def row(case_id, group, n, condition, valid, priority, rule):
    trace, actions, checks, status = run_rule(n, valid, priority, rule)
    initial_exists = graph_reachable((1 << n) - 1, valid)
    final_exists = graph_reachable(trace[-1], valid)
    reached = trace[-1] == 0
    safe = all(state in valid for state in trace)
    return {
        'case_id': case_id, 'group': group, 'bits': n,
        'condition_id': condition, 'valid_states': [encode(x, n) for x in sorted(valid)],
        'priority': ''.join(chr(97 + x) for x in priority), 'rule': rule,
        'trace': [encode(x, n) for x in trace],
        'actions': ''.join(chr(97 + x) for x in actions),
        'candidate_checks': checks, 'status': status,
        'target_reached': reached, 'all_states_valid': safe,
        'valid_completion': reached and safe,
        'partial_stop': status == 'partial_stop',
        'refused_before_action': status == 'refused_before_action',
        'initial_safe_path': initial_exists, 'final_safe_path': final_exists,
        'avoidable_dead_end': bool(actions) and not reached and initial_exists and not final_exists,
    }


def rename_state(state, permutation, n):
    out = 0
    for old_field, new_field in enumerate(permutation):
        if remaining(state, old_field, n):
            out |= 1 << (n - 1 - new_field)
    return out


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    config = json.loads((base / 'config.json').read_text())
    freeze = json.loads((base / 'freeze.json').read_text())
    for name, digest in freeze['sha256'].items():
        assert hashlib.sha256((base / name).read_bytes()).hexdigest() == digest
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    start_wall, start_cpu = time.monotonic(), time.process_time()
    receipt = {
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version, 'platform': platform.platform(),
        'machine': platform.machine(), 'source_sha256': source_hash,
        'config_sha256': freeze['sha256']['config.json'],
        'command': ['python3', 'study.py', '--out', str(out)],
        'dependencies': 'Python standard library only', 'random_seed': None,
        'resource_limits': {'cpu_seconds': 60, 'wall_seconds': 120},
    }
    dump(out / 'execution_started.json', receipt)
    resource.setrlimit(resource.RLIMIT_CPU, (60, 61))
    signal.alarm(120)
    rows = []
    check_counts = Counter()
    try:
        # Cases contain all control dimensions; no random sampling.
        with (out / 'cases.jsonl').open('w') as stream:
            for n in config['control_bits'] + [config['primary_bits']]:
                group = 'primary' if n == config['primary_bits'] else 'smaller_control'
                for condition, valid in conditions(n):
                    for priority in itertools.permutations(range(n)):
                        for rule in config['rules']:
                            item = row(len(rows) + 1, group, n, condition, valid, priority, rule)
                            stream.write(json.dumps(item, sort_keys=True) + '\n')
                            stream.flush()
                            rows.append(item)
                            # Graph reachability and path checks are separate algorithms.
                            if rule == 'complete':
                                assert item['valid_completion'] == item['initial_safe_path']
                                assert item['all_states_valid']
                                assert item['initial_safe_path'] or item['refused_before_action']
                                check_counts['complete_graph_oracle'] += 1
                            if rule == 'greedy':
                                assert item['all_states_valid']
                                if not item['target_reached']:
                                    assert not item['final_safe_path']
                                if n <= 2:
                                    assert not item['avoidable_dead_end']
                                check_counts['greedy_validity_and_stop'] += 1
                            if rule == 'fixed':
                                assert item['target_reached']
                                check_counts['fixed_target'] += 1
                            # All-valid, endpoints-only, and one-chain controls.
                            if len(valid) == 1 << n:
                                assert item['valid_completion']
                                check_counts['all_valid'] += 1
                            if valid == {0, (1 << n) - 1} and n >= 2 and rule != 'fixed':
                                assert item['refused_before_action']
                                check_counts['endpoints_only'] += 1
                            chain = {(1 << n) - 1}
                            probe = (1 << n) - 1
                            for f in range(n):
                                probe = clear(probe, f, n)
                                chain.add(probe)
                            if valid == chain and rule in ('greedy', 'complete'):
                                assert item['valid_completion']
                                check_counts['single_chain'] += 1
                            # Field names have no effect when priority is relabeled too.
                            original = run_rule(n, valid, priority, rule)
                            for permutation in itertools.permutations(range(n)):
                                renamed_valid = {rename_state(x, permutation, n) for x in valid}
                                renamed_priority = tuple(permutation[x] for x in priority)
                                renamed = run_rule(n, renamed_valid, renamed_priority, rule)
                                expected = ([rename_state(x, permutation, n) for x in original[0]],
                                            [permutation[x] for x in original[1]], original[2], original[3])
                                assert renamed == expected
                                check_counts['field_renaming'] += 1
                            if time.monotonic() - start_wall > config['wall_seconds_limit']:
                                raise TimeoutError('wall limit exceeded')
        assert len(rows) == 1179
        primary = [x for x in rows if x['group'] == 'primary']
        assert len(primary) == 1152
        assert any(x['avoidable_dead_end'] for x in primary if x['rule'] == 'greedy')
        assert any(not x['all_states_valid'] for x in primary if x['rule'] == 'fixed')
        flags = ['target_reached', 'all_states_valid', 'valid_completion', 'partial_stop',
                 'refused_before_action', 'initial_safe_path', 'avoidable_dead_end']
        def aggregate(selected):
            return {'cases': len(selected), **{flag: sum(x[flag] for x in selected) for flag in flags}}
        summary = {
            'primary': {rule: aggregate([x for x in primary if x['rule'] == rule]) for rule in config['rules']},
            'by_priority': {p: {rule: aggregate([x for x in primary if x['rule'] == rule and x['priority'] == p])
                               for rule in config['rules']} for p in sorted({x['priority'] for x in primary})},
            'smaller_controls': {str(n): {rule: aggregate([x for x in rows if x['bits'] == n and x['rule'] == rule])
                                         for rule in config['rules']} for n in config['control_bits']},
            'conditions_with_safe_path': len({x['condition_id'] for x in primary if x['initial_safe_path']}),
            'conditions_with_any_greedy_dead_end': len({x['condition_id'] for x in primary if x['avoidable_dead_end']}),
            'unknown_cases': 0, 'total_rule_cases': len(rows),
        }
        condition_rows = []
        for cid in range(64):
            selected = [x for x in primary if x['condition_id'] == cid]
            condition_rows.append({'condition_id': cid, 'valid_states': selected[0]['valid_states'],
                                   'rules': {rule: aggregate([x for x in selected if x['rule'] == rule])
                                             for rule in config['rules']}})
        witness = next(x for x in primary if x['avoidable_dead_end'])
        paired = [x for x in primary if x['condition_id'] == witness['condition_id'] and x['priority'] == witness['priority']]
        dump(out / 'summary.json', summary)
        dump(out / 'conditions.json', condition_rows)
        dump(out / 'witness.json', {'selection': 'first avoidable dead end in frozen case order', 'paired_cases': paired})
        dump(out / 'checks.json', {'passed': dict(check_counts), 'failed': 0, 'hypotheses': {f'H{i}': True for i in range(1, 6)}})
        receipt.update({'exit_status': 0, 'valid_cases': len(rows), 'unknown_cases': 0, 'error': None})
        print(json.dumps(summary['primary'], sort_keys=True))
    except BaseException:
        receipt.update({'exit_status': 1, 'completed_records': len(rows), 'error': traceback.format_exc()})
        print(receipt['error'], file=sys.stderr)
        raise
    finally:
        signal.alarm(0)
        receipt.update({'finished_at_utc': datetime.now(timezone.utc).isoformat(),
                        'wall_seconds': time.monotonic() - start_wall,
                        'cpu_seconds': time.process_time() - start_cpu})
        dump(out / 'execution.json', receipt)


if __name__ == '__main__':
    main()
