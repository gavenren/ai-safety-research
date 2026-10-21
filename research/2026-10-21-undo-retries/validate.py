#!/usr/bin/env python3
"""Check the saved evidence, report tables, and a clean reproduction."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
KINDS = ['correct_completion', 'false_completion', 'refusal_correct', 'refusal_incorrect']
DETERMINISTIC = ['cases.jsonl', 'outcomes.csv', 'traces.jsonl.gz', 'summary.csv',
                 'summary.json', 'pairs.json', 'witnesses.json', 'checks.json']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    root = args.results
    freeze = json.loads((HERE / 'freeze.json').read_text())
    for file, sha in freeze['files'].items():
        assert hashlib.sha256((HERE / file).read_bytes()).hexdigest() == sha
    cases = [json.loads(line) for line in (root / 'cases.jsonl').read_text().splitlines()]
    config = json.loads((HERE / 'config.json').read_text())
    assert len(cases) == 2924
    assert [c['case_id'] for c in cases] == list(range(1, len(cases) + 1))
    assert len({json.dumps({k:v for k,v in c.items() if k != 'case_id'}, sort_keys=True) for c in cases}) == len(cases)
    observed_settings = {s: sum(c['setting'] == s for c in cases) for s in config['expected_cases']}
    assert observed_settings == config['expected_cases']
    for c in cases:
        reference = c['initial'][:]
        for word in c['external']:
            for command in word:
                reference[0 if command.startswith('x') else 1] += 1 if command.endswith('add1') else -1
        assert reference == c['target']
        assert c['no_external'] == (sum(map(len, c['external'])) == 0)
    rows = list(csv.DictReader((root / 'outcomes.csv').open()))
    assert len(rows) == len(cases) * len(config['rules'])
    summary, pair_counts, first_witness = {}, {}, {}
    trace_events = 0
    with gzip.open(root / 'traces.jsonl.gz', 'rt') as f:
        for index, (row, line) in enumerate(zip(rows, f, strict=True)):
            c = cases[index // len(config['rules'])]
            rule = config['rules'][index % len(config['rules'])]
            assert int(row['case_id']) == c['case_id'] and row['rule'] == rule
            assert row['setting'] == c['setting']
            for i, field in enumerate(('x', 'y')):
                assert int(row['initial_' + field]) == c['initial'][i]
                assert int(row['target_' + field]) == c['target'][i]
            trace = json.loads(line)
            assert trace['case_id'] == c['case_id'] and trace['rule'] == rule
            events = trace['events']
            trace_events += len(events)
            assert events[0]['event'] == 'start' and events[-1]['event'] == 'audit'
            audit = events[-1]
            for i, field in enumerate(('x', 'y')):
                assert audit['value'][i] == int(row['final_' + field])
                assert audit['done'][i] == int(row['done_' + field])
                assert audit['applications'][i] == int(row['applications_' + field])
                assert audit['changes'][i] == int(row['changes_' + field])
            assert [e['cut'] for e in events if e['event'] == 'crash'] == c['cuts']
            assert [e['command'] for e in events if e['event'] == 'external'] == sum(c['external'], [])
            assert sum(e['event'] == 'attempt_start' for e in events) == len(c['cuts']) + 1
            applied = [0, 0]
            changed = [0, 0]
            for previous, event in zip(events, events[1:]):
                if event['event'] == 'slot' and event['action'] in ('inverse', 'atomic_effect_and_done', 'effect_without_done', 'effect_after_done'):
                    field = (event['slot'] - 1) // 2
                    applied[field] += 1
                    changed[field] += int(previous['value'][field] != event['value'][field])
                assert event['applications'] == applied and event['changes'] == changed
            assert int(row['repeated']) == int(max(applied) > 1)
            assert int(row['omitted']) == int(min(applied) < 1)
            correct = audit['value'] == c['target']
            claim = bool(int(row['claim']))
            assert audit['claim'] == int(claim) and int(row['correct']) == int(correct)
            kind = KINDS[(0 if claim else 2) + (0 if correct else 1)]
            assert row['outcome'] == audit['outcome'] == kind
            for subset in ['all'] + (['no_external'] if c['no_external'] else []):
                key = (c['setting'], subset, rule)
                s = summary.setdefault(key, dict(setting=key[0], subset=key[1], rule=rule,
                    n=0, **{k:0 for k in KINDS}, repeated=0, omitted=0, applications=0, value_changes=0))
                s['n'] += 1
                s[kind] += 1
                s['repeated'] += int(row['repeated'])
                s['omitted'] += int(row['omitted'])
                s['applications'] += sum(applied)
                s['value_changes'] += sum(changed)
            atomic = rows[(index // 7) * 7 + config['rules'].index('atomic_inverse')]
            pair_key = (c['setting'], rule, kind, atomic['outcome'])
            pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
            first_witness.setdefault(rule + ':' + kind, (c, row, events))
    saved_summary = json.loads((root / 'summary.json').read_text())
    assert list(summary.values()) == saved_summary
    for saved, s in zip(csv.DictReader((root / 'summary.csv').open()), saved_summary, strict=True):
        assert saved == {k:str(v) for k,v in s.items()}
    saved_pairs = json.loads((root / 'pairs.json').read_text())
    assert {(p['setting'], p['rule'], p['outcome'], p['atomic_outcome']):p['n'] for p in saved_pairs} == pair_counts
    witnesses = json.loads((root / 'witnesses.json').read_text())
    assert witnesses.keys() == first_witness.keys()
    for key, (c, row, events) in first_witness.items():
        w = witnesses[key]
        assert w['case'] == c and w['events'] == events
        assert {k:str(v) for k,v in w['result'].items()} == row
    report = (HERE / 'report.md').read_text()
    tables, current = [], []
    for line in report.splitlines() + ['']:
        if line.startswith('|'):
            current.append([x.strip() for x in line.strip('|').split('|')])
        elif current:
            assert len({len(row) for row in current}) == 1, current
            tables.append(current)
            current = []
    assert len(tables) == 5
    table_checks = 0
    for t_index, columns in [(2, KINDS), (3, ['repeated', 'omitted', 'applications', 'value_changes'])]:
        for rule, table_row in zip(config['rules'], tables[t_index][2:], strict=True):
            s = summary[('two_crashes', 'all', rule)]
            assert table_row == [rule] + [f'{s[k]:,}' for k in columns]
            table_checks += len(columns)
    for rule, table_row in zip(config['rules'], tables[4][2:], strict=True):
        wanted = [rule, f"{summary[('two_crashes', 'no_external', rule)]['false_completion']:,}",
                  f"{summary[('one_crash', 'all', rule)]['false_completion']:,}"]
        assert table_row == wanted
        table_checks += 2
    assert tables[1][2:] == [['No fault', '0', '0', '4'], ['One crash', '1', '2', '420'], ['Two crashes, primary', '2', '1', '2,500']]
    compared = []
    if args.reference:
        for name in DETERMINISTIC:
            assert (root / name).read_bytes() == (args.reference / name).read_bytes(), name
            compared.append(name)
    print(json.dumps(dict(status='pass', frozen_files=len(freeze['files']), cases=len(cases),
        outcomes=len(rows), trace_events=trace_events, summary_rows=len(summary), paired_rows=len(pair_counts),
        witnesses=len(witnesses), report_tables=len(tables), result_table_cells=table_checks,
        deterministic_files_equal=compared), indent=2))


if __name__ == '__main__':
    main()
