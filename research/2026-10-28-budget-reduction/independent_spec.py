"""Independent prefix formulas for the budget-reduction plan.

This file does not import the main study or use SQL. It calculates a row
from the positions of completed events and their earlier decisions.
"""
from functools import lru_cache
from itertools import permutations

RULES = ('BlindSet', 'SpentOnly', 'CachedCover', 'VersionedCover', 'AtomicCover')
ORDERS = tuple(sorted(p for p in permutations('RUSB') if p.index('R') < p.index('U')))


def inputs():
    """Yield the complete planned corpus in numeric, then schedule order."""
    number = 0
    for s0 in range(3):
        for a in (1, 2):
            for x in range(a + 1):
                for slack in range(3):
                    c0 = s0 + a + slack
                    for n in range(c0):
                        for b in (1, 2):
                            for order in ORDERS:
                                yield dict(id=f'h{number:05d}', s0=s0, a=a, x=x,
                                           slack=slack, C0=c0, n=n, b=b,
                                           order=list(order))
                                number += 1


def evaluate(setting, rule):
    """Compute each prefix directly; decisions refer only to earlier cuts."""
    order = tuple(setting['order'])
    position = {event: order.index(event) for event in order}
    assert set(position) == set('RUSB') and position['R'] < position['U']
    assert rule in RULES
    s0, a, x, c0, n, b = (setting[k] for k in ('s0', 'a', 'x', 'C0', 'n', 'b'))

    @lru_cache(None)
    def state(cut):
        # A cut gives the number of completed events. No stored row is updated.
        settled = int(position['S'] < cut)
        b_done = int(position['B'] < cut and accepted('B'))
        u_done = int(position['U'] < cut and accepted('U'))
        return {'s': s0 + settled * x + b_done * b,
                'r': (1 - settled) * a,
                'C': n if u_done else c0,
                'e': settled + b_done + u_done}

    @lru_cache(None)
    def accepted(event):
        current = state(position[event])
        if event == 'B':
            return current['s'] + current['r'] + b <= current['C']
        assert event == 'U'
        saved = state(position['R'])
        if rule == 'BlindSet':
            return True
        if rule == 'SpentOnly':
            return current['s'] <= n
        if rule == 'CachedCover':
            return saved['s'] + saved['r'] <= n
        if rule == 'VersionedCover':
            return saved['s'] + saved['r'] <= n and current['e'] == saved['e']
        return current['s'] + current['r'] <= n

    states = [state(cut) for cut in range(5)]
    events = [{'event': event, 'before': states[i], 'after': states[i+1]}
              for i, event in enumerate(order)]
    u_before, u_after = states[position['U']], states[position['U']+1]
    b_before, b_after = states[position['B']], states[position['B']+1]
    u_ok, b_ok = accepted('U'), accepted('B')
    feasible = u_before['s'] + u_before['r'] <= n
    cover = [max(0, row['s'] + row['r'] - row['C']) for row in states]
    actual = [max(0, row['s'] - row['C']) for row in states]
    first_cover = next((order[i-1] for i in range(1, 5) if cover[i]), None)
    first_actual = next((order[i-1] for i in range(1, 5) if actual[i]), None)
    scores = {
        'u_accepted': u_ok,
        'u_refused': not u_ok,
        'unsafe_change': u_ok and not feasible,
        'feasible_refusal': not u_ok and feasible,
        'already_spent_excess_at_u': u_ok and u_after['s'] > n,
        'hold_exposure_only_at_u': u_ok and u_after['s'] <= n < u_after['s'] + u_after['r'],
        'b_accepted': b_ok,
        'b_refused': not b_ok,
        'covered_breach': max(cover) > 0,
        'actual_breach': max(actual) > 0,
        'exposure_without_actual': max(cover) > 0 and max(actual) == 0,
        'final_actual_excess': actual[-1],
        'max_actual_excess': max(actual),
        'max_covered_excess': max(cover),
        'first_covered_event': first_cover,
        'first_actual_event': first_actual,
        'actual_first_at_u': first_actual == 'U',
        'actual_first_at_s': first_actual == 'S',
        'requested_cap_feasible_at_u': feasible,
    }
    # Consequences of the plan are checked independently of summary counts.
    assert scores['unsafe_change'] == scores['covered_breach']
    assert not b_ok or b_after['s'] + b_after['r'] <= b_after['C']
    assert first_cover in (None, 'U')
    assert first_actual in (None, 'U', 'S')
    if rule in ('AtomicCover', 'VersionedCover'):
        assert not scores['covered_breach']
    if rule == 'AtomicCover':
        assert u_ok == feasible
    return {'states': states, 'events': events,
            'snapshot': states[position['R']],
            'u': {'accepted': u_ok, 'current_feasible': feasible,
                  'current_spent_fits': u_before['s'] <= n,
                  'snapshot_fits': states[position['R']]['s'] + states[position['R']]['r'] <= n,
                  'revision_matches': u_before['e'] == states[position['R']]['e']},
            'b': {'accepted': b_ok,
                  'guard': b_before['s'] + b_before['r'] + b <= b_before['C']},
            'scores': scores}


def groups(setting):
    p = {event: setting['order'].index(event) for event in 'RUSB'}
    b_order = 'before_R' if p['B'] < p['R'] else ('between_R_U' if p['B'] < p['U'] else 'after_U')
    return ('all', 'S_before_U' if p['S'] < p['U'] else 'S_after_U',
            'B_' + b_order, 's0_' + str(setting['s0']),
            'x_equals_a' if setting['x'] == setting['a'] else 'x_less_a')


def expected_totals():
    totals = {rule: {'cases': 0} for rule in RULES}
    for setting in inputs():
        for rule in RULES:
            outcome = evaluate(setting, rule)
            row = totals[rule]
            row['cases'] += 1
            for key, value in outcome['scores'].items():
                if isinstance(value, bool):
                    row[key] = row.get(key, 0) + int(value)
                elif key.startswith('max_'):
                    row[key] = max(row.get(key, 0), value)
    return totals
