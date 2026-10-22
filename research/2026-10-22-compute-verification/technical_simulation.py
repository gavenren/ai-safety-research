#!/usr/bin/env python3
"""Synthetic interval accounting only; no hardware or cryptographic implementation.

Python 3.9+; standard library only. Run: python3 technical_simulation.py
All totals use exact integers. Output is deterministic for this Python RNG seed.
"""
import json
import random
from pathlib import Path

SEED = 20261022
ERROR = 2
THRESHOLD = 900000


def records(devices=100, epochs=100):
    out = []
    for d in range(devices):
        cap = 400 if d < 20 else 100
        for t in range(epochs):
            truth = cap * (10 + ((17*d + 13*t) % 81)) // 100
            measured = truth + ((d+t) % 3) - 1
            out.append({'device': d, 'epoch': t, 'capacity': cap,
                        'truth': truth, 'measured': measured})
    return out


def classify(lower, upper, threshold):
    return ('within' if upper <= threshold else
            'exceeds' if lower > threshold else 'unresolved')


def account(rows, missing):
    cap = sum(r['capacity'] for r in rows)
    known = [r for i, r in enumerate(rows) if i not in missing]
    gap = sum(r['capacity'] for i, r in enumerate(rows) if i in missing)
    lower = sum(max(0, r['measured'] - ERROR) for r in known)
    upper = sum(min(r['capacity'], r['measured'] + ERROR) for r in known) + gap
    truth = sum(r['truth'] for r in rows)
    assert all(0 <= r['truth'] <= r['capacity'] for r in rows)
    assert all(abs(r['measured'] - r['truth']) <= ERROR for r in known)
    assert lower <= truth <= upper
    return {'records': len(rows), 'missing': len(missing),
            'time_coverage_pct': 100 * len(known) / len(rows),
            'capacity_coverage_pct': 100 * (cap-gap) / cap,
            'observed': sum(r['measured'] for r in known),
            'truth': truth, 'lower': lower, 'upper': upper,
            'width': upper-lower, 'gap_capacity': gap,
            'threshold': THRESHOLD,
            'decision': classify(lower, upper, THRESHOLD)}


def main():
    rows = records()
    ix = list(range(len(rows)))
    rng = random.Random(SEED)
    by_capacity = sorted(ix, key=lambda i: (-rows[i]['capacity'], rows[i]['device'], rows[i]['epoch']))
    by_activity = sorted(ix, key=lambda i: (-rows[i]['truth'], rows[i]['device'], rows[i]['epoch']))
    masks = [('complete', set()),
             ('random_5pct', set(rng.sample(ix, 500))),
             ('high_capacity_5pct', set(by_capacity[:500])),
             ('high_activity_5pct', set(by_activity[:500])),
             ('all_high_capacity_20pct', set(by_capacity[:2000]))]
    results = {name: account(rows, mask) for name, mask in masks}
    small = records(devices=3, epochs=4)
    for bits in range(1 << len(small)):
        account(small, {i for i in range(len(small)) if (bits >> i) & 1})
    # Intentionally violate the meter error assumption. Without a valid bound,
    # the arithmetic's claimed interval excludes the true operation count.
    false_meter = {'capacity': 100, 'truth': 80, 'measured': 20,
                   'assumed_error': ERROR, 'claimed_lower': 18,
                   'claimed_upper': 22, 'truth_contained': False}
    assert not (false_meter['claimed_lower'] <= false_meter['truth'] <= false_meter['claimed_upper'])
    threshold_cases = [(10, 20, 20, 'within'), (10, 20, 10, 'unresolved'),
                       (10, 20, 9, 'exceeds'), (10, 20, 19, 'unresolved')]
    for lower, upper, threshold, expected in threshold_cases:
        assert classify(lower, upper, threshold) == expected
    output = {'kind': 'synthetic accounting demonstration, not a hardware benchmark',
              'seed': SEED, 'error_bound': ERROR,
              'capacity_units': 'abstract operation units per one-unit epoch',
              'total_capacity': sum(r['capacity'] for r in rows),
              'scenarios': results,
              'exhaustive_masks_checked': 1 << len(small),
              'exhaustive_failures': 0,
              'threshold_boundary_checks': [{'lower': lo, 'upper': hi, 'threshold': h, 'expected': expected, 'actual': classify(lo, hi, h)} for lo, hi, h, expected in threshold_cases],
              'false_meter_counterexample': false_meter,
              'external_inventory_rule': 'If external compute has no defensible finite budget, global upper bound is unbounded.'}
    path = Path(__file__).with_name('technical_results.json')
    path.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
