"""Independent prefix formulas from the frozen October 29 plan.

This module does not import the main runner. It does not use a mutable merge
loop to produce expected balances. Every prefix is evaluated from its distinct
reports, their positions, and the minimum of its signed prefix sums.
"""
from itertools import accumulate, permutations, product


RULES = ('Net', 'GlobalClamp', 'ItemClamp', 'ArrivalReplace',
         'MaxReplace', 'RevisionReplace')
ITEMS = ('A', 'B')
EVENT_IDS = ('A1', 'A2', 'B1', 'B2')
MULTISETS = (
    ('none', ('A1', 'A2', 'B1', 'B2')),
    ('repeat_A2', ('A1', 'A2', 'A2', 'B1', 'B2')),
    ('repeat_B2', ('A1', 'A2', 'B1', 'B2', 'B2')),
)


def reports(values):
    """Return the four immutable records for (uA,vA,uB,vB)."""
    assert len(values) == 4 and all(v in range(3) for v in values)
    return {
        item + str(rev): {
            'id': item + str(rev), 'item': item, 'revision': rev,
            'value': values[2 * idx + rev - 1],
            'delta': (values[2 * idx] if rev == 1
                      else values[2 * idx + 1] - values[2 * idx]),
        }
        for idx, item in enumerate(ITEMS) for rev in (1, 2)
    }


def directions(values):
    def sign(a, b):
        return 'down' if b < a else 'up' if b > a else 'equal'
    return sign(*values[:2]), sign(*values[2:])


def cases():
    """Yield numeric settings, duplicate group, and sorted unique orders."""
    orders = [(group, sorted(set(permutations(events))))
              for group, events in MULTISETS]
    for values in product(range(3), repeat=4):
        for group, candidates in orders:
            for order in candidates:
                yield values, group, order


def prefix_sums(deltas):
    return (0,) + tuple(accumulate(deltas))


def reflected(deltas):
    """Closed prefix formula for a reflected sum, including the empty prefix."""
    sums = prefix_sums(deltas)
    return sums[-1] - min(sums)


def state_for(rule, values, prefix):
    """Evaluate one state directly from a delivery prefix.

    balances and revisions are dictionaries keyed by A,B when needed and empty
    dictionaries otherwise. duplicate describes the final delivered event only.
    """
    assert rule in RULES
    source = reports(values)
    assert all(e in source for e in prefix)
    distinct = tuple(dict.fromkeys(prefix))
    delivered = [source[e] for e in distinct]
    by_item = {i: [r for r in delivered if r['item'] == i] for i in ITEMS}
    balances = {}
    revisions = {}
    if rule == 'Net':
        q = sum(r['delta'] for r in delivered)
    elif rule == 'GlobalClamp':
        q = reflected([r['delta'] for r in delivered])
    else:
        for item, rs in by_item.items():
            if rule == 'ItemClamp':
                balances[item] = reflected([r['delta'] for r in rs])
            elif rule == 'ArrivalReplace':
                balances[item] = rs[-1]['value'] if rs else 0
            elif rule == 'MaxReplace':
                balances[item] = max((r['value'] for r in rs), default=0)
            elif rule == 'RevisionReplace':
                chosen = max(rs, key=lambda r: r['revision']) if rs else None
                balances[item] = chosen['value'] if chosen else 0
                revisions[item] = chosen['revision'] if chosen else 0
        q = sum(balances.values())
    return {
        'q': q,
        'seen': sorted(distinct),
        'balances': balances,
        'revisions': revisions,
        'duplicate': bool(prefix and prefix[-1] in prefix[:-1]),
    }


def expected_case(rule, values, order, finality=True):
    states = [state_for(rule, values, order[:k]) for k in range(len(order) + 1)]
    z = values[1] + values[3]
    q = states[-1]['q']
    complete = set(order) == set(EVENT_IDS)
    closed = finality and complete
    decisions = [
        branch(q, z, cap, b, closed)
        for cap in range(z, z + 3) for b in (1, 2)
    ]
    return {
        'states': states,
        'q': q,
        'truth': z,
        'error': q - z,
        'under': q < z,
        'exact': q == z,
        'over': q > z,
        'negative_intermediate': any(s['q'] < 0 for s in states),
        'complete': complete,
        'finality': finality,
        'closed': closed,
        'decisions': decisions,
    }


def branch(q, z, cap, b, closed):
    accepted = bool(closed and q + b <= cap)
    charge = z + (b if accepted else 0)
    return {
        'cap': cap, 'request': b, 'accepted': accepted, 'charge': charge,
        'excess': max(0, charge - cap),
        'feasible_refusal': bool(not accepted and z + b <= cap),
        'local_balance': cap - q - (b if accepted else 0),
    }


def controls():
    """Named inputs written directly from the plan, without a main import."""
    return [
        ('early_credit', (2, 0, 0, 0), ('A2', 'A1', 'B1', 'B2'), True),
        ('late_original_upward', (0, 2, 0, 0), ('A2', 'A1', 'B1', 'B2'), True),
        ('offset_across_items', (2, 0, 2, 2), ('B1', 'A2', 'A1', 'B2'), True),
        ('equal_revisions', (1, 1, 1, 1), ('A2', 'B2', 'A1', 'B1'), True),
        ('zero_values', (0, 0, 0, 0), ('A1', 'A2', 'B1', 'B2'), True),
        ('exact_replay', (2, 0, 0, 2), ('A2', 'A2', 'B2', 'A1', 'B1'), True),
        ('missing_report', (2, 0, 0, 2), ('A1', 'A2', 'B1'), True),
        ('open_period', (2, 0, 0, 2), ('A1', 'A2', 'B1', 'B2'), False),
    ]


def reflection_details(values, prefix):
    """Independent components used to test H4 on every prefix."""
    rs = reports(values)
    distinct = tuple(dict.fromkeys(prefix))
    all_sums = prefix_sums([rs[e]['delta'] for e in distinct])
    per_item = {i: prefix_sums([rs[e]['delta'] for e in distinct if rs[e]['item'] == i])
                for i in ITEMS}
    return {
        'net': all_sums[-1],
        'global_lift': -min(all_sums),
        'item_lifts': {i: -min(sums) for i, sums in per_item.items()},
    }
