#!/usr/bin/env python3
"""Exact finite experiment. Python standard library only. See frozen plan.md."""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import platform
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
OUTCOMES = ('correct_completion', 'false_completion', 'refusal_correct', 'refusal_incorrect')
DELTAS = {'x_add1': (1, 0), 'x_sub1': (-1, 0), 'y_add1': (0, 1), 'y_sub1': (0, -1)}
FIELDS = ['case_id', 'setting', 'rule', 'initial_x', 'initial_y', 'target_x', 'target_y',
          'final_x', 'final_y', 'done_x', 'done_y', 'stopped', 'claim', 'correct', 'outcome',
          'applications_x', 'applications_y', 'changes_x', 'changes_y', 'repeated', 'omitted']


def dump(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def cases(config):
    case_id = 0
    for setting in config['settings']:
        words = [list(w) for length in range(setting['max_word_length'] + 1)
                 for w in itertools.product(config['alphabet'], repeat=length)]
        for initial in itertools.product(config['initial_values'], repeat=2):
            for cuts in itertools.product(config['cuts'], repeat=setting['crashes']):
                for word_ids in itertools.product(range(len(words)), repeat=setting['crashes']):
                    external = [words[i] for i in word_ids]
                    target = list(initial)
                    for word in external:
                        for command in word:
                            delta = DELTAS[command]
                            target = [target[i] + delta[i] for i in range(2)]
                    case_id += 1
                    yield dict(case_id=case_id, setting=setting['name'], initial=list(initial),
                               cuts=list(cuts), external=external, target=target,
                               no_external=not any(external))


def run(case, rule):
    value = [v + 1 for v in case['initial']]
    done = [False, False]
    applications = [0, 0]
    changes = [0, 0]
    stopped = False
    trace = []

    def record(event, **details):
        trace.append(dict(event=event, value=value[:], done=[int(x) for x in done],
                          applications=applications[:], changes=changes[:],
                          stopped=int(stopped), **details))

    def apply(field):
        old = value[field]
        value[field] = case['initial'][field] if rule.endswith('_set') else old - 1
        applications[field] += 1
        changes[field] += int(old != value[field])

    record('start')
    for attempt, cut in enumerate(case['cuts'] + [4]):
        pending = [False, False]
        interrupted = attempt < len(case['cuts'])
        record('attempt_start', attempt=attempt, cut=cut, interrupted=int(interrupted))
        for slot in range(1, cut + 1):
            field, phase = divmod(slot - 1, 2)
            action = 'padding'
            if stopped:
                action = 'stopped'
            elif rule == 'restart_inverse':
                if phase == 0:
                    apply(field)
                    action = 'inverse'
            elif rule.startswith('atomic_'):
                if phase == 0 and not done[field]:
                    apply(field)
                    done[field] = True
                    action = 'atomic_effect_and_done'
                elif phase == 0:
                    action = 'already_done'
            elif phase == 0:
                if not done[field]:
                    pending[field] = True
                    if rule == 'before_inverse':
                        done[field] = True
                        action = 'early_done'
                    else:
                        apply(field)
                        action = 'effect_without_done'
                else:
                    action = 'already_done'
            elif pending[field]:
                if rule == 'before_inverse':
                    apply(field)
                    action = 'effect_after_done'
                else:
                    done[field] = True
                    action = 'late_done'
            record('slot', attempt=attempt, slot=slot, action=action,
                   pending=[int(x) for x in pending])
        if interrupted:
            if rule == 'stop_on_uncertainty':
                stopped = True
            record('crash', attempt=attempt, cut=cut)
            for command in case['external'][attempt]:
                delta = DELTAS[command]
                value = [value[i] + delta[i] for i in range(2)]
                record('external', attempt=attempt, command=command)
    claim = rule == 'restart_inverse' or all(done)
    correct = value == case['target']
    outcome = OUTCOMES[(0 if claim else 2) + (0 if correct else 1)]
    row = dict(case_id=case['case_id'], setting=case['setting'], rule=rule,
               initial_x=case['initial'][0], initial_y=case['initial'][1],
               target_x=case['target'][0], target_y=case['target'][1],
               final_x=value[0], final_y=value[1], done_x=int(done[0]), done_y=int(done[1]),
               stopped=int(stopped), claim=int(claim), correct=int(correct), outcome=outcome,
               applications_x=applications[0], applications_y=applications[1],
               changes_x=changes[0], changes_y=changes[1],
               repeated=int(any(n > 1 for n in applications)), omitted=int(any(n < 1 for n in applications)))
    record('audit', claim=int(claim), correct=int(correct), outcome=outcome, target=case['target'])
    return row, trace


def controls():
    checks = []

    def check(rule, cut, words, expected):
        case = dict(case_id=0, setting='control', initial=[0, 0], cuts=[cut],
                    external=[words], target=[sum(DELTAS[w][i] for w in words) for i in range(2)])
        row, _ = run(case, rule)
        actual = {k: row[k] for k in expected}
        assert actual == expected, (rule, cut, words, actual, expected)
        checks.append(dict(rule=rule, cut=cut, external=words, expected=expected, passed=True))

    check('restart_inverse', 1, [], dict(final_x=-1, final_y=0, applications_x=2, applications_y=1, outcome='false_completion'))
    check('before_inverse', 1, [], dict(final_x=1, final_y=0, applications_x=0, applications_y=1, outcome='false_completion'))
    check('after_inverse', 1, [], dict(final_x=-1, final_y=0, applications_x=2, applications_y=1, outcome='false_completion'))
    check('after_set', 1, [], dict(final_x=0, final_y=0, applications_x=2, changes_x=1, outcome='correct_completion'))
    check('stop_on_uncertainty', 1, [], dict(final_x=0, final_y=1, done_x=0, done_y=0, outcome='refusal_incorrect'))
    check('stop_on_uncertainty', 3, [], dict(final_x=0, final_y=0, done_x=1, done_y=0, outcome='refusal_correct'))
    check('atomic_inverse', 1, ['x_add1'], dict(final_x=1, final_y=0, applications_x=1, applications_y=1, outcome='correct_completion'))
    check('after_set', 1, ['x_add1'], dict(final_x=0, final_y=0, applications_x=2, outcome='false_completion'))
    check('atomic_set', 0, ['x_add1'], dict(final_x=0, final_y=0, applications_x=1, applications_y=1, outcome='false_completion'))
    check('atomic_set', 4, ['x_add1'], dict(final_x=1, final_y=0, outcome='correct_completion'))
    check('stop_on_uncertainty', 4, ['x_add1'], dict(final_x=1, final_y=0, stopped=1, outcome='correct_completion'))
    check('after_set', 0, ['x_add1', 'x_sub1'], dict(final_x=0, final_y=0, outcome='correct_completion'))
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    config = json.loads((HERE / 'config.json').read_text())
    freeze = json.loads((HERE / 'freeze.json').read_text())
    for name, expected in freeze['files'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    check_results = controls()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    summaries, pairs, witnesses, case_counts = {}, {}, {}, {}
    inverse_identity_checks = 0
    with (out / 'cases.jsonl').open('w', encoding='utf-8', newline='\n') as case_file, \
         (out / 'outcomes.csv').open('w', encoding='utf-8', newline='') as result_file, \
         (out / 'traces.jsonl.gz').open('wb') as compressed:
        writer = csv.DictWriter(result_file, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        with gzip.GzipFile(filename='', mode='wb', fileobj=compressed, mtime=0) as trace_file:
            for case in cases(config):
                case_file.write(dump(case) + '\n')
                case_counts[case['setting']] = case_counts.get(case['setting'], 0) + 1
                rows = {}
                for rule in config['rules']:
                    row, trace = run(case, rule)
                    rows[rule] = row
                    writer.writerow(row)
                    trace_file.write((dump(dict(case_id=case['case_id'], rule=rule, events=trace)) + '\n').encode())
                    if not rule.endswith('_set'):
                        for i, field in enumerate(('x', 'y')):
                            assert row['final_' + field] - case['target'][i] == 1 - row['applications_' + field]
                            inverse_identity_checks += 1
                    for subset in ['all'] + (['no_external'] if case['no_external'] else []):
                        key = (case['setting'], subset, rule)
                        if key not in summaries:
                            summaries[key] = dict(setting=key[0], subset=key[1], rule=rule, n=0,
                                **{o: 0 for o in OUTCOMES}, repeated=0, omitted=0, applications=0, value_changes=0)
                        summary = summaries[key]
                        summary['n'] += 1
                        summary[row['outcome']] += 1
                        for k in ('repeated', 'omitted'):
                            summary[k] += row[k]
                        summary['applications'] += row['applications_x'] + row['applications_y']
                        summary['value_changes'] += row['changes_x'] + row['changes_y']
                    witness_key = rule + ':' + row['outcome']
                    if witness_key not in witnesses:
                        witnesses[witness_key] = dict(case=case, result=row, events=trace)
                for rule, row in rows.items():
                    key = (case['setting'], rule, row['outcome'], rows['atomic_inverse']['outcome'])
                    pairs[key] = pairs.get(key, 0) + 1
                assert time.process_time() - start_cpu < config['cpu_limit_seconds'], 'CPU limit exceeded'
    assert case_counts == config['expected_cases'], case_counts
    summary_rows = list(summaries.values())
    with (out / 'summary.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(summary_rows)
    write_json(out / 'summary.json', summary_rows)
    write_json(out / 'pairs.json', [dict(setting=k[0], rule=k[1], outcome=k[2], atomic_outcome=k[3], n=n) for k, n in pairs.items()])
    write_json(out / 'witnesses.json', witnesses)
    primary = {r['rule']: r for r in summary_rows if r['setting'] == 'two_crashes' and r['subset'] == 'all'}
    no_external = [r for r in summary_rows if r['subset'] == 'no_external']
    hypotheses = {
        'H1': all(primary[r]['false_completion'] > 0 and primary[r]['repeated'] > 0 for r in ['restart_inverse', 'after_inverse']),
        'H2': primary['before_inverse']['false_completion'] > 0 and primary['before_inverse']['omitted'] > 0,
        'H3': primary['after_set']['false_completion'] > 0 and all(r['false_completion'] == 0 for r in no_external if r['rule'] == 'after_set'),
        'H4': primary['atomic_set']['false_completion'] > 0 and primary['atomic_set']['applications'] == 2 * primary['atomic_set']['n'] and primary['atomic_set']['repeated'] == primary['atomic_set']['omitted'] == 0,
        'H5': all(r['correct_completion'] == r['n'] and r['repeated'] == r['omitted'] == 0 for r in summary_rows if r['rule'] == 'atomic_inverse'),
        'H6': all(r['false_completion'] == 0 for r in summary_rows if r['rule'] == 'stop_on_uncertainty') and primary['stop_on_uncertainty']['correct_completion'] < primary['atomic_inverse']['correct_completion'] and primary['stop_on_uncertainty']['refusal_correct'] > 0,
    }
    write_json(out / 'checks.json', dict(frozen_inputs_match=True, case_counts=case_counts,
        outcomes=sum(case_counts.values()) * len(config['rules']), controls=check_results,
        inverse_identity_checks=inverse_identity_checks, hypotheses=hypotheses))
    metadata = dict(python=sys.version, platform=platform.platform(), machine=platform.machine(),
        cpu_seconds=time.process_time() - start_cpu, wall_seconds=time.perf_counter() - start_wall,
        max_rss_platform_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        max_rss_units='bytes on macOS; kibibytes on Linux', dependencies='Python standard library',
        random_seed=None, paid_compute=False, model_calls_in_experiment=0,
        command='python3 study.py --out ' + str(out))
    write_json(out / 'execution.json', metadata)
    print(json.dumps(dict(cases=case_counts, outcomes=sum(case_counts.values()) * len(config['rules']),
                         controls=len(check_results), hypotheses=hypotheses, cpu_seconds=metadata['cpu_seconds'])))


if __name__ == '__main__':
    main()
