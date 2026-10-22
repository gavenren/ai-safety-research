#!/usr/bin/env python3
"""Independent audit of saved gate histories. Does not execute study.py."""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

RULES = ('boolean', 'nonnegative_count', 'active_ids', 'lifecycle_registry')


def expected_keys():
    keys = set()
    for ops in [('A',), ('A', 'B')]:
        group = 'single_operation' if len(ops) == 1 else 'two_operations'
        for flags in itertools.product([0, 1], repeat=2 * len(ops)):
            events = []
            required = []
            for i, op in enumerate(ops):
                events += [f'{op}_C0', f'{op}_R0']
                required.append((f'{op}_C0', f'{op}_R0'))
                if flags[2 * i]:
                    events.append(f'{op}_C1')
                    required.append((f'{op}_C0', f'{op}_C1'))
                if flags[2 * i + 1]:
                    events.append(f'{op}_R1')
                    required.append((f'{op}_R0', f'{op}_R1'))
            for history in itertools.permutations(events):
                positions = {event: j for j, event in enumerate(history)}
                if all(positions[a] < positions[b] for a, b in required):
                    keys.add((group, flags, history))
    return keys


def oracle(events):
    ops = sorted({e[0] for e in events})
    positions = {event: i for i, event in enumerate(events)}
    steps = []
    overlap = False
    for i, event in enumerate(events):
        prefix = events[:i + 1]
        active = [op for op in ops if positions[f'{op}_C0'] <= i < positions[f'{op}_R0']]
        overlap |= len(active) == 2
        wanted = bool(active)
        # Reflected prefix sum is the count's closed-form recurrence solution.
        sums = [0]
        for e in prefix:
            sums.append(sums[-1] + (1 if e[2] == 'C' else -1))
        count = sums[-1] - min(sums)
        present = [op for op in ops if any(e[0] == op for e in prefix)
                   and next(e for e in reversed(prefix) if e[0] == op)[2] == 'C']
        registry = {op: ('completed' if positions[f'{op}_R0'] <= i else 'active')
                    for op in ops if positions[f'{op}_C0'] <= i}
        states = {'boolean': event[2] == 'C', 'nonnegative_count': count,
                  'active_ids': present, 'lifecycle_registry': registry}
        closed = {'boolean': states['boolean'], 'nonnegative_count': count > 0,
                  'active_ids': bool(present), 'lifecycle_registry': bool(active)}
        steps.append({'event_index': i, 'event': event, 'active_work': active,
                      'oracle_closed': wanted,
                      'rules': {rule: {'state': states[rule], 'closed': closed[rule],
                                      'unsafe_open': wanted and not closed[rule],
                                      'unnecessary_closed': not wanted and closed[rule]}
                                for rule in RULES}})
    scores = {}
    for rule in RULES:
        unsafe = sum(s['rules'][rule]['unsafe_open'] for s in steps)
        extra = sum(s['rules'][rule]['unnecessary_closed'] for s in steps)
        scores[rule] = {'unsafe_points': unsafe, 'unnecessary_closed_points': extra,
                        'unsafe_history': unsafe > 0, 'overblocked_history': extra > 0,
                        'final_closed': steps[-1]['rules'][rule]['closed']}
    return overlap, steps, scores


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    expected = expected_keys()
    seen = set()
    issues = []
    totals = {'single_operation': {r: Counter() for r in RULES},
              'two_operations': {r: Counter() for r in RULES}}
    rows = 0
    points = 0
    for line in (folder / 'raw_results.jsonl').read_text().splitlines():
        row = json.loads(line)
        rows += 1
        key = row['group'], tuple(row['duplicate_flags']), tuple(row['events'])
        if key in seen:
            issues.append({'history_id': row['history_id'], 'issue': 'duplicate'})
        seen.add(key)
        overlap, steps, scores = oracle(row['events'])
        checked = {'history_id': rows, 'duplicate_count': sum(row['duplicate_flags']),
                   'overlap': overlap, 'steps': steps, 'score': scores}
        for field, value in checked.items():
            if row[field] != value:
                issues.append({'history_id': row['history_id'], 'field': field,
                               'expected': value, 'actual': row[field]})
        points += len(steps)
        for rule in RULES:
            totals[row['group']][rule].update(scores[rule])
            totals[row['group']][rule]['histories'] += 1
    result = {'kind': 'independent audit of saved traces; not a new experiment run',
              'histories': rows, 'event_points': points, 'rule_event_points': points * len(RULES),
              'expected_history_keys': len(expected), 'missing': len(expected - seen),
              'extra': len(seen - expected), 'issues': issues, 'totals': totals,
              'raw_sha256': hashlib.sha256((folder / 'raw_results.jsonl').read_bytes()).hexdigest(),
              'audit_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (folder / 'separate_audit_result.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['totals', 'issues']}, sort_keys=True))
    print(f'Issues: {len(issues)}')
    if issues or expected != seen:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
