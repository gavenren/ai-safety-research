#!/usr/bin/env python3
"""Independent expected vectors. Written before reading the guarded implementation."""
import argparse
import json
from pathlib import Path

CASES = (
    ('overlap', 2, 2, 1, True, False, 1, 0),
    ('late', 2, 2, 2, True, False, 0, 0),
    ('early', 2, 2, 2, True, False, 0, 0),
    ('release', 2, 2, 1, True, False, 1, 0),
    ('unknown', 1, 1, 0, True, False, 1, 0),
    ('compete', 2, 2, 1, True, False, 1, 0),
    ('invalid', 2, 2, 1, False, True, 0, 1),
    ('contradiction', 2, 2, 1, True, True, 0, 0),
)


def prefix_amount(values, reservation, terminal=None):
    """Set-based total; each accepted cumulative total overlaps earlier totals."""
    q = max([0, *set(values), *([] if terminal is None else [terminal])])
    assert 0 <= q <= reservation
    assert terminal is None or terminal == q
    return {'q': q, 'h': reservation-q if terminal is None else 0}


def expected():
    final = []
    for name, cap, reserve, a, terminal, quarantine, b, h in CASES:
        state = prefix_amount([a], reserve, a if terminal else None)
        assert state['h'] == h
        final.append({'case': name, 'C': cap, 'R': reserve, 'A_created': a,
                      'B_created': b, 'q': state['q'], 'h': state['h'],
                      'terminal': terminal, 'quarantined': quarantine,
                      'saved_operations': b, 'pending_operations': 0,
                      'committed': state['q']+h+b,
                      'actual_created': a+b, 'excess': max(0,a+b-cap),
                      'final_A_error': state['q']-a})
    # Named intermediate checks derive their balance from the written prefix.
    checkpoints = [
        {'case':'overlap','point':'after P1,T1,P1,T1','q':1,'h':0,'available':1},
        {'case':'late','point':'after T2,P1','q':2,'h':0,'available':0},
        {'case':'early','point':'after P0 before T2','q':0,'h':2,'available':0},
        {'case':'release','point':'after P1 before T1','q':1,'h':1,'available':0},
        {'case':'release','point':'after T1','q':1,'h':0,'available':1},
        {'case':'unknown','point':'after allocation and before evidence','q':0,'h':0,'pending_operations':1,'available':0},
        {'case':'unknown','point':'after wrong evidence','q':0,'h':0,'pending_operations':1,'available':0},
        {'case':'unknown','point':'after matching evidence and exact replay','q':0,'h':0,'saved_operations':1,'pending_operations':0,'available':0},
        {'case':'compete','point':'after two competing requests','q':1,'h':0,'pending_operations':1,'saved_operations':0,'available':0},
        {'case':'invalid','point':'after rejected inputs','q':1,'h':1,'quarantined':True,'available':0},
        {'case':'contradiction','point':'after conflicting final','q':1,'h':0,'quarantined':True,'available':1},
    ]
    decisions = {
        'overlap':['permit','no_repeat_permit','payload_conflict_refusal'],
        'late':['limit_refusal'],
        'early':['limit_refusal','limit_refusal'],
        'release':['limit_refusal','permit'],
        'unknown':['permit','pending_no_permit','limit_refusal','saved_no_permit'],
        'compete':['one_permit_one_limit_refusal_in_either_order'],
        'invalid':['quarantine_refusal'],
        'contradiction':['quarantine_refusal'],
    }
    return {'status':'independent_planned_expectations_not_observations',
            'basis':'Written contract and fixed eight-case matrix; no implementation or result was read.',
            'sites':['drive','calendar'],'per_site_final':final,'checkpoints':checkpoints,
            'request_expectations':decisions,
            'totals':{'cases_per_site':8,'sites':2,'cases':16,'A_created':18,'B_created':8,
                      'counted_created':26,'excess_cases':0,'final_A_error_cases':0,
                      'quarantined_cases':4,'pending_final':0},
            'limits':['Competing winner identity is not predicted.',
                      'Local planned outcomes do not prove website creation or cleanup.',
                      'Final confirmation replay must not add another saved operation.']}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(expected(),indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
