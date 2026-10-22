#!/usr/bin/env python3
"""Separate reviewer oracle, from plan/config/schema, without reading main source/results.

This audits saved data. It does not rerun the study experiment.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

RULES = ('active_commit', 'modulo2_commit', 'modulo4_commit', 'unique_precheck',
         'unique_commit', 'highwater_commit', 'cancel_fence_commit')


def schedules(n):
    ordered = [label for i in range(1, n + 1) for label in (f'A{i}', f'R{i}')] + ['N']
    for c, o in itertools.combinations(range(2 * n + 3), 2):
        remaining = iter(ordered)
        yield tuple('C' if pos == c else 'O' if pos == o else next(remaining)
                    for pos in range(2 * n + 3))


def controller_at(events, position):
    previous = events[:position]
    cancels = sum(e.startswith('A') for e in previous)
    restarts = sum(e.startswith('R') for e in previous)
    return cancels == restarts, cancels


def oracle(n, events, rule):
    c, o, new, first = [events.index(x) for x in ('C', 'O', 'N', 'A1')]
    active, generation = controller_at(events, o)
    active_c, generation_c = controller_at(events, c)
    cached = c < first
    accepted = {
        'active_commit': active,
        'modulo2_commit': active and generation % 2 == 0,
        'modulo4_commit': active and generation % 4 == 0,
        'unique_precheck': cached,
        'unique_commit': o < first,
        'highwater_commit': o < new,
        'cancel_fence_commit': o < first,
    }[rule]
    def highwater_before(pos):
        if rule == 'highwater_commit':
            return n if new < pos else 0
        if rule == 'cancel_fence_commit':
            return sum(e.startswith('A') for e in events[:pos])
        return 0
    effect_positions = [(new, 'N')] + ([(o, 'O')] if accepted else [])
    effects = [label for _, label in sorted(effect_positions)]
    final_highwater = n if rule in ('highwater_commit', 'cancel_fence_commit') else 0
    trace = []
    for pos, event in enumerate(events):
        after_active, after_generation = controller_at(events, pos + 1)
        effect_prefix = [label for k, label in sorted(effect_positions) if k <= pos]
        trace.append({
            'event': event, 'active': after_active, 'generation': after_generation,
            'highwater': highwater_before(pos + 1),
            'accepted': accepted if event == 'O' else True if event == 'N' else None,
            'effects': effect_prefix,
        })
    return {
        'check': {'active': active_c, 'generation': generation_c,
                  'highwater': highwater_before(c), 'passes': cached},
        'old_state': {'active': active, 'generation': generation, 'highwater': highwater_before(o)},
        'old_accepted': accepted, 'new_accepted': True,
        'stale_attempt': first < o, 'stale_accepted': first < o and accepted,
        'stale_after_new': first < o and accepted and new < o,
        'stale_while_inactive': first < o and accepted and not active,
        'rejected_valid_old': o < first and not accepted,
        'effects': effects, 'trace': trace,
        'final': {'active': True, 'generation': n, 'highwater': final_highwater},
    }


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    expected_keys = {(n, schedule, rule) for n in range(1, 9)
                     for schedule in schedules(n) for rule in RULES}
    seen = set()
    issues = []
    totals = {rule: Counter() for rule in RULES}
    checked_fields = 0
    records = 0
    for line in (folder / 'raw_results.jsonl').read_text().splitlines():
        row = json.loads(line)
        records += 1
        key = (row['n'], tuple(row['schedule']), row['rule'])
        if key in seen:
            issues.append({'case_id': row['case_id'], 'issue': 'duplicate key'})
        seen.add(key)
        predicted = oracle(*key)
        for field, value in predicted.items():
            checked_fields += 1
            if row[field] != value:
                issues.append({'case_id': row['case_id'], 'field': field,
                               'expected': value, 'actual': row[field]})
        for field in ('old_accepted', 'new_accepted', 'stale_attempt', 'stale_accepted',
                      'stale_after_new', 'stale_while_inactive', 'rejected_valid_old'):
            totals[row['rule']][field] += row[field]
        totals[row['rule']]['cases'] += 1
    missing = expected_keys - seen
    extra = seen - expected_keys
    result = {
        'kind': 'independent saved-trace audit, not a third experiment run',
        'records': records, 'expected_unique_keys': len(expected_keys),
        'missing_keys': len(missing), 'extra_keys': len(extra),
        'checked_top_level_fields': checked_fields,
        'issues': issues, 'totals': totals,
        'raw_results_sha256': hashlib.sha256((folder / 'raw_results.jsonl').read_bytes()).hexdigest(),
        'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (folder / 'separate_audit_result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('totals', 'issues')}, sort_keys=True))
    print(f'Issues: {len(issues)}')
    if issues or missing or extra:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
