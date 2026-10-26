#!/usr/bin/env python3
"""Exact delivery and ledger simulation. No network, model, or random input."""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import platform
import resource
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

RULES = ('AddEvery', 'DedupSum', 'LastValue', 'HighWaterEarly',
         'HighWaterHeld', 'TerminalOnly')
GROUPS = ('PT', 'PPT', 'PTT', 'PPTT')
METRICS = ('actual_excess', 'uncovered', 'inflated', 'deficit')
FLAGS = ('accepted', 'refused', 'unsafe_admission', 'feasible_refusal',
         'receipt_sufficient_refusal', 'breach_before_terminal',
         'final_overcount', 'final_undercount', 'final_exact')


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def schedules():
    for group in GROUPS:
        for perm in sorted(set(itertools.permutations(group))):
            for gap in range(len(perm) + 1):
                yield group, ''.join(perm[:gap]) + 'D' + ''.join(perm[gap:])


def worlds():
    idx = 0
    for R in (1, 2):
        for x in range(R + 1):
            for z in range(x, R + 1):
                for C in range(R, R + 3):
                    for b in (1, 2):
                        for group, order in schedules():
                            yield dict(id=f'{idx:04d}', R=R, x=x, z=z,
                                       C=C, b=b, group=group, order=order)
                            idx += 1


def snap(q, h, f, seen, k, C):
    return dict(q=q, h=h, f=f, seen=sorted(seen), k=k,
                available=C-q-h-k)


def amounts(s, w):
    target = w['z'] if s['f'] else w['R']
    return dict(actual_excess=max(0, w['z']+s['k']-w['C']),
                uncovered=max(0, w['z']-s['q']-s['h']),
                inflated=max(0, s['q']+s['h']-target),
                deficit=max(0, -s['available']))


def simulate(w, rule):
    q, h, f, seen, k = 0, w['R'], False, set(), 0
    initial = snap(q, h, f, seen, k, w['C'])
    events = []
    decision = None
    for index, event in enumerate(w['order']):
        before = snap(q, h, f, seen, k, w['C'])
        v = None if event == 'D' else w['x'] if event == 'P' else w['z']
        duplicate = event in seen if event != 'D' else False
        if event == 'D':
            accepted = before['available'] >= w['b']
            decision = dict(accepted=accepted, available=before['available'],
                            terminal_seen=f, feasible=w['z']+w['b'] <= w['C'])
            if accepted:
                k = w['b']
        else:
            f = f or event == 'T'
            if rule == 'AddEvery':
                q += v
                h = 0 if f else max(0, w['R']-q)
            elif rule == 'DedupSum':
                if not duplicate:
                    q += v
                h = 0 if f else max(0, w['R']-q)
            elif rule == 'LastValue':
                q = v
                h = 0 if f else max(0, w['R']-q)
            elif rule in ('HighWaterEarly', 'HighWaterHeld'):
                q = max(q, v)
                h = 0 if rule == 'HighWaterEarly' or f else w['R']-q
            elif rule == 'TerminalOnly':
                if event == 'T':
                    q, h = v, 0
            else:
                raise ValueError(rule)
            seen.add(event)
        after = snap(q, h, f, seen, k, w['C'])
        events.append(dict(index=index, event=event, value=v,
                           terminal_report=event == 'T', duplicate=duplicate,
                           before=before, after=after,
                           decision=decision.copy() if event == 'D' else None))
    assert decision is not None
    states = [(-1, 'INITIAL', initial)] + [(e['index'], e['event'], e['after']) for e in events]
    scores = {}
    for metric in METRICS:
        vals = [(i, ev, amounts(s, w)[metric]) for i, ev, s in states]
        bad = next(((i, ev) for i, ev, v in vals if v > 0), None)
        scores[metric+'_case'] = bad is not None
        scores[metric+'_max'] = max(v for _, _, v in vals)
        scores[metric+'_first'] = None if bad is None else dict(index=bad[0], event=bad[1])
    err = q-w['z']
    scores.update(accepted=decision['accepted'], refused=not decision['accepted'],
                  unsafe_admission=decision['accepted'] and not decision['feasible'],
                  feasible_refusal=not decision['accepted'] and decision['feasible'],
                  receipt_sufficient_refusal=not decision['accepted'] and decision['feasible'] and decision['terminal_seen'],
                  breach_before_terminal=any(not s['f'] and amounts(s, w)['actual_excess'] > 0 for _, _, s in states),
                  final_error=err, final_overcount=err > 0, final_undercount=err < 0,
                  final_exact=err == 0, final_hold=h)
    return dict(world_id=w['id'], rule=rule, initial=initial, events=events,
                final=events[-1]['after'], scores=scores)


def summary_add(row, record):
    row['cases'] += 1
    for key in FLAGS:
        row[key] += int(record['scores'][key])
    for metric in METRICS:
        row[metric+'_cases'] += int(record['scores'][metric+'_case'])
        row[metric+'_max'] = max(row[metric+'_max'], record['scores'][metric+'_max'])
    row['max_final_overcount'] = max(row['max_final_overcount'], record['scores']['final_error'])
    row['max_final_undercount'] = max(row['max_final_undercount'], -record['scores']['final_error'])


CONTROLS = (
    ('distinct_totals', 2, 1, 2, 2, 1, 'PTD'),
    ('late_progress', 2, 1, 2, 2, 1, 'TPD'),
    ('zero_progress', 2, 0, 2, 2, 1, 'PDT'),
    ('equal_distinct_values', 2, 1, 1, 3, 2, 'PTD'),
    ('duplicate_final', 2, 0, 1, 3, 2, 'PTTD'),
    ('duplicate_progress', 2, 1, 2, 3, 1, 'PPTD'),
    ('zero_final', 2, 0, 0, 2, 2, 'TPD'),
    ('before_reports', 2, 1, 1, 2, 2, 'DPT'),
)


def control_rows():
    rows = []
    for name, R, x, z, C, b, order in CONTROLS:
        w = dict(id=name, R=R, x=x, z=z, C=C, b=b, order=order,
                 group=''.join(sorted(order.replace('D', ''))))
        for rule in RULES:
            rows.append(dict(input=w, result=simulate(w, rule)))
    by_key = {(r['input']['id'], r['result']['rule']):r['result'] for r in rows}
    assert by_key['distinct_totals', 'DedupSum']['final']['q'] == 3
    assert by_key['late_progress', 'LastValue']['scores']['unsafe_admission']
    assert by_key['zero_progress', 'HighWaterEarly']['scores']['breach_before_terminal']
    assert by_key['equal_distinct_values', 'DedupSum']['scores']['receipt_sufficient_refusal']
    assert by_key['equal_distinct_values', 'TerminalOnly']['scores']['accepted']
    assert by_key['duplicate_final', 'AddEvery']['final']['q'] == 2
    assert by_key['duplicate_final', 'DedupSum']['final']['q'] == 1
    assert by_key['duplicate_progress', 'AddEvery']['final']['q'] == 4
    assert by_key['duplicate_progress', 'DedupSum']['final']['q'] == 3
    assert all(by_key['zero_final', r]['scores']['accepted'] for r in RULES)
    assert all(not by_key['before_reports', r]['scores']['accepted'] for r in RULES)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.monotonic(), time.process_time()
    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    args.out.mkdir(parents=True, exist_ok=True)
    assert not any(args.out.iterdir()), 'Output directory must be empty'
    inputs = list(worlds())
    assert len(inputs) == 3240 and len(list(schedules())) == 60
    assert len({tuple(w.items()) for w in inputs}) == 3240
    dump(args.out/'inputs.json', inputs)
    controls = control_rows()
    dump(args.out/'controls.json', controls)
    summaries = {(r,g):defaultdict(int) for r in RULES for g in ('ALL',)+GROUPS}
    pairs = {r:dict(both_accept=0, rule_only_accept=0, baseline_only_accept=0, both_refuse=0) for r in RULES}
    witnesses = {}
    counters = defaultdict(int)
    with (args.out/'traces.jsonl.gz').open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz:
            for w in inputs:
                records = {rule:simulate(w,rule) for rule in RULES}
                baseline = records['TerminalOnly']
                for rule, record in records.items():
                    states = [record['initial']] + [e['after'] for e in record['events']]
                    for pos, e in enumerate(record['events']):
                        assert e['before'] == states[pos]
                        assert not e['before']['f'] or e['after']['f']
                        assert min(e['after'][v] for v in ('q','h','k')) >= 0
                        assert e['after']['k'] in (0,w['b'])
                        assert e['value'] == (None if e['event']=='D' else w['x'] if e['event']=='P' else w['z'])
                        counters['transitions'] += 1
                    assert record['scores']['unsafe_admission'] == record['scores']['actual_excess_case']
                    assert sum(e['event']=='D' for e in record['events']) == 1
                    if rule in ('HighWaterHeld','TerminalOnly'):
                        assert not record['scores']['actual_excess_case'] and not record['scores']['uncovered_case']
                        assert record['final']['q'] == w['z'] and record['final']['h'] == 0
                        for s, bs in zip(states, [baseline['initial']]+[e['after'] for e in baseline['events']]):
                            assert s['q']+s['h'] == bs['q']+bs['h']
                            assert s['k'] == bs['k']
                        counters['complete_rule_cases'] += 1
                    if rule == 'DedupSum':
                        assert record['final']['q'] == w['x']+w['z']
                        if w['group']=='PT':
                            other=records['AddEvery']
                            assert record['events']==other['events'] and record['scores']==other['scores']
                            counters['no_duplicate_pairs'] += 1
                    if rule == 'HighWaterEarly':
                        assert [s['q'] for s in states] == [records['HighWaterHeld']['initial']['q']]+[e['after']['q'] for e in records['HighWaterHeld']['events']]
                        counters['high_water_pairs'] += 1
                    for group in ('ALL', w['group']):
                        summary_add(summaries[rule,group], record)
                    a, b = record['scores']['accepted'], baseline['scores']['accepted']
                    pairs[rule]['both_accept' if a and b else 'rule_only_accept' if a else 'baseline_only_accept' if b else 'both_refuse'] += 1
                    for key in ('actual_excess_case','uncovered_case','inflated_case','receipt_sufficient_refusal','breach_before_terminal','final_overcount','final_undercount'):
                        if record['scores'][key] and (rule,key) not in witnesses:
                            witnesses[rule,key] = dict(input=w,result=record)
                    gz.write((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
                    counters['rule_outcomes'] += 1
                if int(w['id']) % 100 == 0:
                    assert time.monotonic()-wall <= 300, 'Wall-time limit'
                    assert sum(p.stat().st_size for p in args.out.iterdir()) <= 200_000_000, 'Output-size limit'
    rows = [dict(rule=r,group=g,**summaries[r,g]) for r in RULES for g in ('ALL',)+GROUPS]
    fields = list(rows[0])
    with (args.out/'summary.csv').open('w', newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    dump(args.out/'paired.json', pairs)
    dump(args.out/'witnesses.json', [dict(rule=r,measure=m,**v) for (r,m),v in witnesses.items()])
    # Permutation invariance concerns A ledger state only; B admission depends on D.
    for R in (1,2):
        for x in range(R+1):
            for z in range(x,R+1):
                for rule in ('HighWaterHeld','TerminalOnly'):
                    finals=set()
                    for group, order in schedules():
                        w=dict(id='invariant',R=R,x=x,z=z,C=R,b=1,group=group,order=order)
                        s=simulate(w,rule)['final']; finals.add((s['q'],s['h'],s['f']))
                    assert finals == {(z,0,True)}
                    counters['final_permutation_groups'] += 1
    checks=dict(status='pass',worlds=len(inputs),control_rows=len(controls),**counters)
    dump(args.out/'checks.json', checks)
    size=sum(p.stat().st_size for p in args.out.iterdir())
    elapsed_cpu, elapsed_wall = time.process_time()-cpu, time.monotonic()-wall
    assert size<=200_000_000 and elapsed_wall<=300 and elapsed_cpu<=120
    env=dict(started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
             python=sys.version,platform=platform.platform(),machine=platform.machine(),
             cpu_seconds=elapsed_cpu,wall_seconds=elapsed_wall,bytes_before_environment=size,
             limits=dict(cpu_seconds=120,wall_seconds=300,bytes=200_000_000),seed=None,
             network_calls=0,model_calls=0,dependencies='Python standard library only',
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    dump(args.out/'environment.json', env)
    print(json.dumps(checks,sort_keys=True))
    print(json.dumps(env,sort_keys=True))


if __name__ == '__main__':
    main()
