"""Independent formulas for the selected live-record accounting tests.

This module reads no account and makes no website change. Values must come from
the separate record evidence. Delayed and repeated delivery is a local test.
The test credits are not provider charges. Source revisions are study labels.

Method: reduce each delivery prefix to its first occurrences. Use sums and
prefix minima for additive rules. Select records for replacement rules.
The author did not read the new live implementation or its results before this
file was frozen. The inherited chat did include original study code excerpts.
"""

from itertools import accumulate

RULES = (
    "Net", "GlobalClamp", "ItemClamp", "ArrivalReplace", "MaxReplace",
    "RevisionReplace",
)
EVENT_IDS = ("A1", "A2", "B1", "B2")


def _prefix_total(deltas):
    """Return the signed sum and the reflected sum, including the zero prefix."""
    sums = [0, *accumulate(deltas)]
    return sums[-1], sums[-1] - min(sums)


def _records(values):
    if len(values) != 4 or any(type(v) is not int or v < 0 for v in values):
        raise ValueError("Use four nonnegative integer values.")
    u_a, v_a, u_b, v_b = values
    return {
        "A1": ("A", 1, u_a, u_a),
        "A2": ("A", 2, v_a, v_a - u_a),
        "B1": ("B", 1, u_b, u_b),
        "B2": ("B", 2, v_b, v_b - u_b),
    }


def _prefix_values(records, delivered):
    # dict preserves the first position of each ID. A replay is not a new event.
    unique_ids = list(dict.fromkeys(delivered))
    selected = [records[event_id] for event_id in unique_ids]
    net, shared = _prefix_total([row[3] for row in selected])
    groups = [[row for row in selected if row[0] == item] for item in ("A", "B")]
    item_clamp = sum(_prefix_total([row[3] for row in group])[1] for group in groups)
    arrival = sum(group[-1][2] if group else 0 for group in groups)
    maximum = sum(max((row[2] for row in group), default=0) for group in groups)
    revision = sum(max(group, key=lambda row: row[1])[2] if group else 0 for group in groups)
    return dict(zip(RULES, (net, shared, item_clamp, arrival, maximum, revision)))


def evaluate(values, order, cap, demand=1, finality=True):
    """Return the state totals and one decision for each of the six rules.

    `stateq` includes the zero state, then the state after each delivered ID.
    `finality` is the test operator's closure statement. It is not a website
    property. The common gate also needs all four reports.
    """
    records = _records(values)
    order = list(order)
    if any(event_id not in records for event_id in order):
        raise ValueError("Unknown report ID.")
    if type(cap) is not int or cap < 0 or type(demand) is not int or demand <= 0:
        raise ValueError("Use a nonnegative integer cap and a positive integer demand.")
    if type(finality) is not bool:
        raise ValueError("Finality must be true or false.")
    prefix_rows = [_prefix_values(records, order[:length]) for length in range(len(order) + 1)]
    complete = set(order) == set(EVENT_IDS)
    gate = finality and complete
    true_charge = values[1] + values[3]
    output = {}
    for rule in RULES:
        stateq = [row[rule] for row in prefix_rows]
        finalq = stateq[-1]
        admit = gate and finalq + demand <= cap
        final_charge = true_charge + (demand if admit else 0)
        output[rule] = {
            "stateq": stateq,
            "finalq": finalq,
            "admit": admit,
            "excess": max(0, final_charge - cap),
            "feasiblerefusal": not admit and true_charge + demand <= cap,
            "error": finalq - true_charge,
            "true_charge": true_charge,
            "final_charge": final_charge,
            "complete": complete,
            "finality": finality,
            "gate": gate,
        }
    return output
