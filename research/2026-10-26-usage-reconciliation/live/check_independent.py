#!/usr/bin/env python3
"""Check public branch states against independently frozen prefix equations."""
import argparse
import hashlib
import json
from pathlib import Path
from independent_expected import expected


def normalize(state):
    result = {key: state[key] for key in ('q', 'h', 'f', 'k')}
    result['available'] = 2 - result['q'] - result['h'] - result['k']
    result['seen'] = sorted(value.rsplit('-', 1)[-1] for value in state['seen'])
    return result


def audit(root):
    branches = json.loads((root/'branches.json').read_text())['branches']
    assert len(branches) == len({row['branch'] for row in branches}) == 48
    states = transitions = 0
    for row in branches:
        want = expected(row['receipts']['site'], row['receipts']['case'], row['rule'])
        assert row['status'] == 'completed' and row['integration_pass'] is True
        assert normalize(row['initial']) == want['initial']
        assert normalize(row['state']) == want['final']
        assert row['decision']['accepted'] == want['decision']['accepted']
        assert row['decision']['available'] == want['decision']['available']
        assert row['decision']['terminal_received'] == want['decision']['terminal_seen']
        assert row['actual_b_count'] == want['expected_b_writes']
        assert len(row['trace']) == len(want['events'])
        for actual, target in zip(row['trace'], want['events']):
            assert actual['event'] == target['event']
            for key in ('before', 'after'):
                assert normalize(actual[key]) == target[key]
                states += 1
            transitions += 1
        score = row['scores']
        assert score['final_booking_error'] == want['final_error']
        assert score['scoped_created_count'] == want['expected_scoped_use']
        assert score['scoped_excess'] == want['expected_scoped_excess']
        assert score['feasible_refusal_after_T'] == want['receipt_sufficient_refusal']
        assert score['unsafe_admission'] == (want['expected_scoped_excess'] > 0)
        assert score['final_h'] == want['final']['h']
        assert score['final_q'] == want['final']['q']
    return {
        'status': 'passed', 'branches': len(branches),
        'transitions': transitions, 'before_after_states': states,
        'saved_b_records': sum(row['actual_b_count'] for row in branches),
        'refused_branches': sum(not row['decision']['accepted'] for row in branches),
        'scope_excess_cases': sum(row['scores']['scoped_excess'] > 0 for row in branches),
        'final_overcounts': sum(row['scores']['final_booking_error'] > 0 for row in branches),
        'final_undercounts': sum(row['scores']['final_booking_error'] < 0 for row in branches),
        'feasible_refusals_after_T': sum(row['scores']['feasible_refusal_after_T'] for row in branches),
        'branches_sha256': hashlib.sha256((root/'branches.json').read_bytes()).hexdigest(),
        'expected_source_sha256': hashlib.sha256((root/'independent_expected.py').read_bytes()).hexdigest(),
        'limit': 'This command checks saved public data. It does not repeat website actions or independently prove provider state.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = audit(Path(__file__).resolve().parent)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2))
