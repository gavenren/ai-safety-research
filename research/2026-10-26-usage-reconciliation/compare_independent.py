#!/usr/bin/env python3
"""Compare saved main results with the frozen independent prefix specification.

This adapter maps field names only. The specification was frozen first.
It does not import or execute the main implementation.
"""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import independent_spec as spec

WITNESS_MEASURES = ('actual_excess_case', 'uncovered_case', 'inflated_case',
                    'receipt_sufficient_refusal', 'breach_before_terminal',
                    'final_overcount', 'final_undercount')
CONTROL_IDS = ('distinct_totals', 'late_progress', 'zero_progress',
               'equal_distinct_values', 'duplicate_final', 'duplicate_progress',
               'zero_final', 'before_reports')


def mapped_state(s):
    return {k: v for k, v in s.items() if k != 'accepted'}


def mapped_trace(w, rule, t=None):
    if t is None:
        t = spec.trace(w, rule)
    scores = {k: v for k, v in t['scores'].items() if k != 'metrics'}
    for key, d in t['scores']['metrics'].items():
        for part in ('case', 'max', 'first'):
            scores[key + '_' + part] = d[part]
    events = []
    for event in t['events']:
        e = dict(event)
        e['before'] = mapped_state(e['before'])
        e['after'] = mapped_state(e['after'])
        if e['event'] == 'D':
            e['decision'] = dict(accepted=event['decision'],
                                  available=e['before']['available'],
                                  feasible=w['z'] + w['b'] <= w['C'],
                                  terminal_seen=e['before']['f'])
        events.append(e)
    return dict(world_id=w['id'], rule=rule, initial=mapped_state(t['initial']),
                final=mapped_state(t['final']), events=events, scores=scores)


def mapped_summary(rows):
    mapped = []
    for item in spec.aggregate(rows):
        row = {k: v for k, v in item.items() if k not in (
            'worlds', 'final_hold_nonzero', 'final_error_min', 'final_error_max')}
        row['cases'] = item['worlds']
        row['max_final_overcount'] = max(0, item['final_error_max'])
        row['max_final_undercount'] = max(0, -item['final_error_min'])
        mapped.append(row)
    return mapped


def compare(results):
    all_worlds = list(spec.worlds())
    saved_inputs = json.loads((results / 'inputs.json').read_text())
    assert saved_inputs == all_worlds, 'input worlds differ'
    scores_for_summary = []
    all_scores = {}
    first = {}
    state_records, events_count, decision_records = 0, 0, 0
    unique_keys = set()
    with gzip.open(results / 'traces.jsonl.gz', 'rt') as f:
        for w in all_worlds:
            for rule in spec.RULES:
                line = next(f, None)
                assert line is not None, 'missing trace'
                actual = json.loads(line)
                t = spec.trace(w, rule)
                expected = mapped_trace(w, rule, t)
                assert actual == expected, ('trace differs', w['id'], rule)
                key = (w['id'], rule)
                assert key not in unique_keys
                unique_keys.add(key)
                state_records += 2 + 2 * len(t['events'])
                events_count += len(t['events'])
                decision_records += 1
                scores_for_summary.append(dict(id=w['id'], group=w['group'],
                                                rule=rule, scores=t['scores']))
                all_scores[key] = t['scores']
                for measure in WITNESS_MEASURES:
                    if expected['scores'][measure]:
                        first.setdefault((rule, measure), dict(
                            input=w, rule=rule, measure=measure, result=expected))
        assert next(f, None) is None, 'extra trace'
    with (results / 'summary.csv').open() as f:
        saved_summary = [{k: (v if k in ('rule', 'group') else int(v))
                          for k, v in row.items()} for row in csv.DictReader(f)]
    summary_expected = mapped_summary(scores_for_summary)
    assert saved_summary == summary_expected, 'summary differs'
    paired = {}
    for rule in spec.RULES:
        counts = dict(baseline_only_accept=0, both_accept=0,
                      both_refuse=0, rule_only_accept=0)
        for w in all_worlds:
            a = all_scores[(w['id'], rule)]['accepted']
            b = all_scores[(w['id'], 'TerminalOnly')]['accepted']
            key = ('both_accept' if a else 'baseline_only_accept') if b else (
                'rule_only_accept' if a else 'both_refuse')
            counts[key] += 1
        paired[rule] = counts
    assert json.loads((results / 'paired.json').read_text()) == paired, 'paired differs'
    control_rows = json.loads((results / 'controls.json').read_text())
    assert len(control_rows) == 48
    independent_controls = spec.controls()
    for i, control in enumerate(spec.CONTROL_SPECS):
        _, R, C, x, z, b, order, _, _ = control
        group = 'P' * order.count('P') + 'T' * order.count('T')
        w = dict(id=CONTROL_IDS[i], R=R, C=C, x=x, z=z, b=b, group=group, order=order)
        for j, rule in enumerate(spec.RULES):
            expected = dict(input=w, result=mapped_trace(w, rule))
            assert control_rows[6*i+j] == expected, ('control differs', i, rule)
    saved_witnesses = json.loads((results / 'witnesses.json').read_text())
    witness_keys = [(w['rule'], w['measure']) for w in saved_witnesses]
    assert len(set(witness_keys)) == len(witness_keys)
    assert set(witness_keys) == set(first), 'witness coverage differs'
    for witness in saved_witnesses:
        assert witness == first[(witness['rule'], witness['measure'])], 'first witness differs'
    counts = dict(complete_rule_cases=2 * len(all_worlds), control_rows=48,
                  final_permutation_groups=2 * len({(w['R'], w['x'], w['z']) for w in all_worlds}),
                  high_water_pairs=len(all_worlds),
                  no_duplicate_pairs=sum(w['group'] == 'PT' for w in all_worlds),
                  rule_outcomes=len(unique_keys), status='pass', transitions=events_count,
                  worlds=len(all_worlds))
    assert json.loads((results / 'checks.json').read_text()) == counts, 'check counts differ'
    files = ('inputs.json', 'traces.jsonl.gz', 'summary.csv', 'paired.json',
             'controls.json', 'witnesses.json', 'checks.json')
    hashes = {name: hashlib.sha256((results / name).read_bytes()).hexdigest() for name in files}
    return dict(status='pass', plan_sha256=spec.PLAN_SHA256,
                specification_sha256=hashlib.sha256(Path(spec.__file__).read_bytes()).hexdigest(),
                adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                main_implementation_imported=False, main_implementation_executed=False,
                worlds=len(all_worlds), outcomes=len(unique_keys), events=events_count,
                state_records=state_records, decision_records=decision_records,
                score_records=len(unique_keys), summary_rows=len(saved_summary),
                summary_numeric_values=sum(len(r)-2 for r in saved_summary),
                paired_rows=len(paired), paired_values=4*len(paired),
                control_rows=len(control_rows), independent_control_rows=len(independent_controls),
                first_witnesses=len(saved_witnesses), evidence_sha256=hashes,
                compared_fields='All input fields; all initial/final and event before/after states; report metadata; decisions; all score fields and first-event records; summaries; paired counts; controls; first witnesses; check counts.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    receipt = compare(args.results)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ('status', 'worlds', 'outcomes', 'events', 'state_records')}))


if __name__ == '__main__':
    main()
