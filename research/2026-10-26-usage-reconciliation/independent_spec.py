#!/usr/bin/env python3
"""Independent prefix specification from the frozen plan, without main-code access.

The ledger is a function of a report prefix, not an iterative state update.
No main result or implementation is imported.
"""
import argparse
import itertools
import json
from pathlib import Path

RULES = ('AddEvery', 'DedupSum', 'LastValue', 'HighWaterEarly',
         'HighWaterHeld', 'TerminalOnly')
GROUPS = ('PT', 'PPT', 'PTT', 'PPTT')
METRICS = ('actual_excess', 'uncovered', 'inflated', 'deficit')
PLAN_SHA256 = '0058dfdedd935767a88381ffe8bc655fc2dbb536e25f0fa4f4d8a8748fcee097'


def schedules():
    for group in GROUPS:
        for delivery in sorted(set(itertools.permutations(group))):
            for gap in range(len(delivery) + 1):
                yield group, ''.join(delivery[:gap]) + 'D' + ''.join(delivery[gap:])


def worlds():
    index = 0
    for R in (1, 2):
        for x in range(R + 1):
            for z in range(x, R + 1):
                for C in range(R, R + 3):
                    for b in (1, 2):
                        for group, order in schedules():
                            yield dict(id=f'{index:04d}', R=R, x=x, z=z,
                                       C=C, b=b, group=group, order=order)
                            index += 1


def a_prefix(w, rule, prefix):
    """Compute A state directly from all reports in a prefix."""
    reports = [e for e in prefix if e != 'D']
    seen = sorted(set(reports))
    closed = 'T' in seen
    values = [w['x'] if e == 'P' else w['z'] for e in reports]
    if rule == 'AddEvery':
        q = sum(values)
    elif rule == 'DedupSum':
        q = (w['x'] if 'P' in seen else 0) + (w['z'] if closed else 0)
    elif rule == 'LastValue':
        q = values[-1] if values else 0
    elif rule in ('HighWaterEarly', 'HighWaterHeld'):
        q = max(values, default=0)
    elif rule == 'TerminalOnly':
        q = w['z'] if closed else 0
    else:
        raise ValueError(rule)
    if not reports:
        h = w['R']
    elif rule == 'HighWaterEarly':
        h = 0
    elif rule == 'TerminalOnly':
        h = 0 if closed else w['R']
    else:
        h = 0 if closed else max(0, w['R'] - q)
    return dict(q=q, h=h, f=closed, seen=seen)


def state(w, rule, prefix):
    a = a_prefix(w, rule, prefix)
    if 'D' in prefix:
        prior = prefix.split('D')[0]
        before = a_prefix(w, rule, prior)
        accepted = w['C'] - before['q'] - before['h'] >= w['b']
        k = w['b'] if accepted else 0
    else:
        accepted, k = None, 0
    return dict(**a, k=k, available=w['C'] - a['q'] - a['h'] - k,
                accepted=accepted)


def metric_values(w, s):
    target = w['z'] if s['f'] else w['R']
    return dict(actual_excess=max(0, w['z'] + s['k'] - w['C']),
                uncovered=max(0, w['z'] - s['q'] - s['h']),
                inflated=max(0, s['q'] + s['h'] - target),
                deficit=max(0, -s['available']))


def trace(w, rule):
    seq = w['order']
    states = [state(w, rule, seq[:n]) for n in range(len(seq) + 1)]
    events = []
    for i, e in enumerate(seq):
        events.append(dict(index=i, event=e,
                           value=(w['x'] if e == 'P' else w['z']) if e != 'D' else None,
                           terminal_report=e == 'T',
                           duplicate=(e in seq[:i]) if e != 'D' else False,
                           before=states[i], after=states[i + 1],
                           decision=states[i + 1]['accepted'] if e == 'D' else None))
    return dict(initial=states[0], events=events, final=states[-1],
                scores=score(w, states))


def score(w, states):
    seq = w['order']
    measured = [metric_values(w, s) for s in states]
    metrics = {}
    for key in METRICS:
        values = [m[key] for m in measured]
        first = next((j for j, v in enumerate(values) if v), None)
        metrics[key] = dict(case=first is not None, max=max(values),
                            first=None if first is None else dict(
                                index=first - 1,
                                event='INITIAL' if first == 0 else seq[first - 1]))
    d = seq.index('D')
    accepted = states[d + 1]['accepted']
    final = states[-1]
    error = final['q'] - w['z']
    return dict(metrics=metrics, accepted=accepted, refused=not accepted,
                unsafe_admission=accepted and w['z'] + w['b'] > w['C'],
                feasible_refusal=(not accepted) and w['z'] + w['b'] <= w['C'],
                receipt_sufficient_refusal=(not accepted) and states[d]['f']
                    and w['z'] + w['b'] <= w['C'],
                breach_before_terminal=any(m['actual_excess'] > 0 and not s['f']
                    for m, s in zip(measured, states)),
                final_error=error, final_overcount=error > 0,
                final_undercount=error < 0, final_exact=error == 0,
                final_hold=final['h'])


CONTROL_SPECS = (
    ('distinct_cumulative', 2, 2, 1, 2, 1, 'PTD', [3,3,2,2,2,2], [0,0,0,0,0,0]),
    ('delayed_progress', 2, 2, 1, 2, 1, 'TPD', [3,3,1,2,2,2], [0,0,1,0,0,0]),
    ('early_zero', 2, 2, 0, 2, 1, 'PDT', [2,2,2,2,2,2], [0,0,0,1,0,0]),
    ('equal_values_distinct_ids', 2, 3, 1, 1, 2, 'PTD', [2,2,1,1,1,1], [0,0,1,1,1,1]),
    ('duplicate_terminal', 2, 3, 0, 1, 2, 'PTTD', [2,1,1,1,1,1], [0,1,1,1,1,1]),
    ('duplicate_progress', 2, 3, 1, 2, 1, 'PPTD', [4,3,2,2,2,2], [0,0,1,1,1,1]),
    ('zero_final', 2, 2, 0, 0, 2, 'TPD', [0,0,0,0,0,0], [1,1,1,1,1,1]),
    ('pre_report_guard', 2, 2, 1, 1, 2, 'DPT', [2,2,1,1,1,1], [0,0,0,0,0,0]),
)


def controls():
    rows = []
    for name, R, C, x, z, b, order, qs, admissions in CONTROL_SPECS:
        w = dict(R=R, C=C, x=x, z=z, b=b, order=order)
        for i, rule in enumerate(RULES):
            result = trace(w, rule)
            assert result['final']['q'] == qs[i], (name, rule, 'q')
            assert result['final']['h'] == 0, (name, rule, 'hold')
            assert result['scores']['accepted'] == bool(admissions[i]), (name, rule, 'B')
            rows.append(dict(name=name, rule=rule, final=result['final'],
                             scores=result['scores']))
    return rows


def aggregate(rows):
    result = {}
    for rule in RULES:
        for group in ('ALL',) + GROUPS:
            selected = [x for x in rows if x['rule'] == rule
                        and (group == 'ALL' or x['group'] == group)]
            item = dict(rule=rule, group=group, worlds=len(selected))
            booleans = ('accepted', 'refused', 'unsafe_admission', 'feasible_refusal',
                        'receipt_sufficient_refusal', 'breach_before_terminal',
                        'final_overcount', 'final_undercount', 'final_exact')
            for key in booleans:
                item[key] = sum(x['scores'][key] for x in selected)
            for key in METRICS:
                item[key + '_cases'] = sum(x['scores']['metrics'][key]['case'] for x in selected)
                item[key + '_max'] = max(x['scores']['metrics'][key]['max'] for x in selected)
            item['final_hold_nonzero'] = sum(x['scores']['final_hold'] != 0 for x in selected)
            item['final_error_min'] = min(x['scores']['final_error'] for x in selected)
            item['final_error_max'] = max(x['scores']['final_error'] for x in selected)
            result[(rule, group)] = item
    return list(result.values())


def run():
    all_worlds = list(worlds())
    assert len(all_worlds) == 3240
    assert len({tuple(w.items()) for w in all_worlds}) == 3240
    rows = []
    event_count = 0
    for w in all_worlds:
        outcomes = {}
        for rule in RULES:
            t = trace(w, rule)
            outcomes[rule] = t
            rows.append(dict(id=w['id'], group=w['group'], rule=rule, scores=t['scores']))
            event_count += len(t['events'])
            assert all(s['q'] >= 0 and s['h'] >= 0 and s['k'] >= 0
                       for s in [t['initial']] + [e['after'] for e in t['events']])
            if rule in ('HighWaterHeld', 'TerminalOnly'):
                assert not t['scores']['metrics']['actual_excess']['case']
                assert not t['scores']['metrics']['uncovered']['case']
                assert t['scores']['final_exact'] and t['scores']['final_hold'] == 0
        a, b = outcomes['HighWaterHeld'], outcomes['TerminalOnly']
        assert a['scores']['accepted'] == b['scores']['accepted']
        assert all(e['after']['q'] + e['after']['h'] == f['after']['q'] + f['after']['h']
                   for e, f in zip(a['events'], b['events']))
        if w['group'] == 'PT':
            assert outcomes['AddEvery'] == outcomes['DedupSum']
        assert outcomes['DedupSum']['final']['q'] == w['x'] + w['z']
        assert all(e['after']['q'] == f['after']['q'] for e, f in zip(
            outcomes['HighWaterEarly']['events'], outcomes['HighWaterHeld']['events']))
    return dict(plan_sha256=PLAN_SHA256, worlds=len(all_worlds), outcomes=len(rows),
                events=event_count, controls=controls(), summary=aggregate(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('worlds', 'outcomes', 'events')}))


if __name__ == '__main__':
    main()
