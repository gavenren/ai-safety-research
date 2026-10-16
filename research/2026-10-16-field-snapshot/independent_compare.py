#!/usr/bin/env python3
"""Compare separately derived files and replay the main witnesses.

This reads data files only. It does not import the main calculation.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
from independent_audit import accepted, replay


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path):
    return json.loads(path.read_text())


def canonical_independent_event_trace(trace):
    result = []
    revision = partial = 0
    for item in trace:
        event = item['event']
        if event == 'write':
            revision = item['revision']
            partial = item['partial_revision']
        row = {'operation': 'field_read' if event == 'read' else event,
               'state': ''.join(map(str, item['bits'])),
               'revision': revision, 'partial_revision': partial}
        for key in ('field', 'gap', 'value'):
            if key in item:
                row[key] = item[key]
        if 'read' in item:
            row['index'] = item['read']
        result.append(row)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    p = args.input_dir
    frozen = load_json(p / 'input_manifest.json')
    for file, value in frozen['sha256'].items():
        assert digest(p / file) == value, ('frozen', file)
    independ = load_json(p / 'independent_terminal_distribution.json')
    independent_terminal = {}
    for setting in independ:
        for row in setting['states']:
            key = (setting['d'], setting['r'], setting['b'],
                   ''.join(map(str, row['bits'])), row['total_writes'],
                   row['last_field_writes'], row['ever_target'], row['all_reads_target'])
            assert key not in independent_terminal
            independent_terminal[key] = row['histories']
    main_terminal = {}
    with gzip.open(p / 'terminal_counts.jsonl.gz', 'rt') as f:
        for line in f:
            row = json.loads(line)
            key = tuple(row[name] for name in ('fields', 'passes', 'writes_per_gap', 'current',
                                               'total_writes', 'last_field_writes', 'ever_target',
                                               'all_reads_target'))
            assert key not in main_terminal
            main_terminal[key] = row['histories']
    assert main_terminal == independent_terminal, 'Full terminal distributions differ'
    independent_results = {(x['d'], x['r'], x['b'], x['policy']): x
                           for x in load_json(p / 'independent_policy_results.json')}
    with (p / 'results.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    mapping = {'total_histories': 'total_histories', 'accepted': 'accepted',
               'no_common_target': 'no_common_target', 'wrong_at_decision': 'wrong_at_decision',
               'rejected_correct_final': 'rejected_correct_final',
               'min_no_common_target_writes': 'minimum_writes_no_common_target',
               'min_wrong_at_decision_writes': 'minimum_writes_wrong_at_decision'}
    seen = set()
    for row in rows:
        key = tuple(int(row[name]) for name in ('fields', 'passes', 'writes_per_gap')) + (row['policy'],)
        assert key not in seen
        seen.add(key)
        peer = independent_results[key]
        for a, b in mapping.items():
            value = None if row[a] == '' else int(row[a])
            assert value == peer[b], (key, a, value, peer[b])
    assert seen == set(independent_results)
    independent_stages = {}
    for setting in load_json(p / 'independent_stage_totals.json'):
        for row in setting['stages']:
            key = (setting['d'], setting['r'], setting['b'], row['gap_done'] + 1)
            independent_stages[key] = (row['histories'], row['state_count'])
    main_stages = {}
    for row in load_json(p / 'stage_totals.json'):
        key = tuple(row[name] for name in ('fields', 'passes', 'writes_per_gap', 'gaps_done'))
        assert key not in main_stages
        main_stages[key] = (row['histories'], row['merged_states'])
    assert main_stages == independent_stages
    independent_witnesses = {(x['d'], x['r'], x['b'], x['policy'], x['outcome']): x
                             for x in load_json(p / 'independent_witnesses.json')}
    main_witnesses = load_json(p / 'witnesses.json')
    seen = set()
    for row in main_witnesses:
        key = tuple(row[name] for name in ('fields', 'passes', 'writes_per_gap', 'policy', 'outcome'))
        assert key not in seen
        seen.add(key)
        peer = independent_witnesses[key]
        initial = tuple(map(int, row['initial']))
        gaps = tuple(tuple(x) for x in row['gap_words'])
        assert list(initial) == peer['initial']
        assert row['gap_words'] == peer['gaps']
        assert row['minimum_writes'] == peer['writes']
        assert all(len(w) <= row['writes_per_gap'] for w in gaps)
        state, trace = replay(row['fields'], row['passes'], initial, gaps)
        assert accepted(state, row['policy'])
        assert state[3] == row['minimum_writes']
        assert not state[1] if row['outcome'] == 'no_common_target' else not all(state[0])
        assert canonical_independent_event_trace(trace) == row['events'], key
    assert seen == set(independent_witnesses)
    files = ('input_manifest.json', 'config.json', 'analysis_plan.md',
             'results.csv', 'terminal_counts.jsonl.gz', 'stage_totals.json', 'witnesses.json',
             'independent_audit.py', 'independent_compare.py',
             'independent_policy_results.json', 'independent_terminal_distribution.json',
             'independent_stage_totals.json', 'independent_witnesses.json', 'independent_self_checks.json')
    receipt = {'status': 'PASS', 'settings': 18, 'policy_rows_compared': len(rows),
               'scalar_policy_values_compared': len(rows) * len(mapping),
               'terminal_rows_compared': len(main_terminal),
               'stage_rows_compared': len(main_stages),
               'witness_paths_minima_ties_and_all_event_states_compared': len(main_witnesses),
               'frozen_files_unchanged': True,
               'main_code_imported': False,
               'sha256': {name: digest(p / name) for name in files},
               'limits': ['Synthetic finite model only.',
                          'The independent programs ran after the input freeze.',
                          'The independent calculation was complete before main data comparison.',
                          'Both implementations use the declared state recurrence.',
                          'The small-case brute force uses no state merging.',
                          'A separate Codex agent review is not human or peer review.']}
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('sha256', 'limits')}))


if __name__ == '__main__':
    main()
