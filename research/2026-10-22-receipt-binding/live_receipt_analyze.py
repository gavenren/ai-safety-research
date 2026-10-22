"""Replay scores from alias-only observed evidence. No account or network calls."""
import argparse
import json
from pathlib import Path


def analyze(evidence):
    rows = evidence['cases']
    expected = {(s, p, k) for s in ('drive', 'calendar') for p in ('K', 'B')
                for k in ('EXACT', 'PAYLOAD', 'TARGET')}
    assert len(rows) == 12
    assert {(c['service'], c['policy'], c['pair']) for c in rows} == expected
    outcomes = []
    totals = {}
    for c in rows:
        assert all(c['checks'].values()), c['case_id']
        assert c['initial_target'] == 'A' and c['initial_value'] == 'PAYLOAD-A'
        assert c['requested_target'] == ('B' if c['pair'] == 'TARGET' else 'A')
        assert c['requested_value'] == ('PAYLOAD-B' if c['pair'] == 'PAYLOAD' else 'PAYLOAD-A')
        assert c['first_saves'] == 1 and c['second_saves'] == 0
        assert c['decision']['dispatch'] is False
        same_request = c['requested_target'] == c['initial_target'] and c['requested_value'] == c['initial_value']
        expected_status = 'success' if c['policy'] == 'K' or same_request else 'conflict'
        assert c['decision']['status'] == expected_status
        expected_mismatch = [] if c['policy'] == 'K' or same_request else ['payload' if c['pair'] == 'PAYLOAD' else 'target']
        assert c['decision']['mismatched_fields'] == expected_mismatch
        actual = c['final_values'][c['requested_target']]
        state_match = actual == c['requested_value']
        false_success = c['decision']['status'] == 'success' and not state_match
        contract_match = c['decision']['status'] == ('success' if same_request else 'conflict')
        row = {'case_id': c['case_id'], 'service': c['service'], 'policy': c['policy'], 'pair': c['pair'],
               'decision': c['decision']['status'], 'requested_target': c['requested_target'],
               'requested_value': c['requested_value'], 'observed_value': actual,
               'requested_state_matches': state_match, 'false_success': false_success,
               'contract_matches': contract_match, 'timing_check_known': c['timing_check_known']}
        outcomes.append(row)
        t = totals.setdefault(c['policy'], {'cases': 0, 'success': 0, 'conflict': 0, 'false_success': 0,
                                           'contract_matches': 0, 'first_saves': 0, 'second_saves': 0})
        t['cases'] += 1
        t[c['decision']['status']] += 1
        t['false_success'] += int(false_success)
        t['contract_matches'] += int(contract_match)
        t['first_saves'] += c['first_saves']
        t['second_saves'] += c['second_saves']
    strict = [r for r in outcomes if r['timing_check_known']]
    return {'cases': 12, 'first_browser_saves': 12, 'second_browser_saves': 0,
            'distinct_fixture_records': sum(len(c['final_values']) for c in rows),
            'total_false_success': sum(r['false_success'] for r in outcomes),
            'by_policy': totals, 'outcomes': outcomes,
            'timing_known_subset': {'cases': len(strict), 'false_success': sum(r['false_success'] for r in strict),
                                    'excluded': [r['case_id'] for r in outcomes if not r['timing_check_known']]},
            'duration_seconds': {'min': min(c['times']['case_seconds'] for c in rows),
                                 'max': max(c['times']['case_seconds'] for c in rows)},
            'baseline_age_seconds': {'min': min(c['times']['baseline_to_before_UI_seconds'] for c in rows),
                                     'max': max(c['times']['baseline_to_before_UI_seconds'] for c in rows)},
            'postclick_to_first_read_seconds': {'min': min(c['times']['postclick_to_first_read_seconds'] for c in rows),
                                               'max': max(c['times']['postclick_to_first_read_seconds'] for c in rows)},
            'scope': 'Selected local-controller cases with production saved records; not provider idempotency trials.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', default='live_evidence.json')
    parser.add_argument('--output', default='live_results.json')
    args = parser.parse_args()
    result = analyze(json.loads(Path(args.evidence).read_text()))
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'cases': result['cases'], 'false_success': result['total_false_success'], 'second_saves': result['second_browser_saves']}))


if __name__ == '__main__':
    main()
