"""Repeat the public data and formula checks without account access.

Run: python3 check_results.py --out portable_checks.json
This checks the saved public evidence. It does not make a fresh website read,
verify a private evidence hash against its contents, or check cleanup.
"""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    root = args.data_dir
    checks = 0

    def check(value, label):
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError(label)

    def read(name):
        return json.loads((root/name).read_text())

    def sha(name):
        return hashlib.sha256((root/name).read_bytes()).hexdigest()

    def stamp(value):
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        check(result.tzinfo is not None, 'Time has a zone offset.')
        return result

    freeze = read('independent_freeze.json')
    check(sha('independent.py') == freeze['sha256'], 'The independent formulas match their freeze.')
    spec = importlib.util.spec_from_file_location('live_formula', root/'independent.py')
    formula = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(formula)
    observations = read('observations.json')
    decisions = read('decisions.json')
    actions = read('actions.json')
    browser = read('browser_actions.json')
    cases = {'credit': (1, ['A2','A1','B1','B2']),
             'upward': (2, ['A2','A1','B1','B2']),
             'replay': (3, ['A2','A2','B2','A1','B1'])}
    identities = {(service, case, rule) for service in 'DC' for case in cases for rule in formula.RULES}
    observation_keys = {f'{service}-{case}-{item}-{rev}' for service in 'DC'
                        for case in cases for item in 'AB' for rev in (1,2)}
    check(set(observations) == observation_keys, 'The source matrix is complete.')
    values = {}
    for key, row in observations.items():
        service, case, item, rev_text = key.split('-')
        rev = int(rev_text)
        alias = f'{service}-{case}-{item}'
        match = re.fullmatch(r'CUA-CORR-20261029 '+re.escape(alias)+rf' r{rev} c([0-2])', row['name'])
        check(match is not None, key+' complete source name')
        check(row['alias'] == alias and row['revision'] == rev, key+' source labels')
        check(row['exact_id_read'] is True, key+' exact-read label')
        check(row['browser_saved_read'] is (rev == 2), key+' browser-read scope')
        check(re.fullmatch(r'[0-9a-f]{64}', row['raw_sha256']) is not None, key+' evidence hash form')
        values[key] = int(match[1])

    correction_rows = [row for row in browser if row['phase'] == 'correction']
    output_rows = [row for row in browser if row['phase'] != 'correction']
    source_aliases = {key[:-2] for key in observation_keys}
    check(len(correction_rows) == 12, 'There are 12 source browser actions.')
    check({row['alias'] for row in correction_rows} == source_aliases, 'Every source has one browser action.')
    for row in correction_rows:
        before = observations[row['alias']+'-1']
        after = observations[row['alias']+'-2']
        check(row['before'] == before['name'], row['alias']+' source before name')
        check(row['intended'] == after['name'], row['alias']+' source saved name')
        check(row['dispatches'] == 1, row['alias']+' one correction dispatch')
        check(stamp(before['time_utc']) < stamp(row['time']) < stamp(after['time_utc']), row['alias']+' source time order')

    check(len(decisions) == 36, 'There are 36 decisions.')
    check(len(actions) == 36 and len(output_rows) == 36, 'Each decision has one action record.')
    decision_map = {(row['service'],row['case'],row['rule']): row for row in decisions}
    action_map = {(row['service'],row['case'],row['rule']): row for row in actions}
    browser_map = {(row['alias'].split('-')[0],row['phase'],row['alias'].split('-')[2]): row for row in output_rows}
    check(set(decision_map) == identities, 'The decision matrix is complete and unique.')
    check(set(action_map) == identities, 'The action matrix is complete and unique.')
    check(set(browser_map) == identities, 'The browser action matrix is complete and unique.')

    state_count = duplicate_count = admitted_count = refusal_count = 0
    totals = {rule: {'decisions': 0, 'admitted': 0, 'over': 0, 'under': 0,
                     'excess_decisions': 0, 'feasible_refusals': 0} for rule in formula.RULES}
    for identity in sorted(identities):
        service, case, rule = identity
        row = decision_map[identity]
        keys = [f'{service}-{case}-{item}-{rev}' for item in 'AB' for rev in (1,2)]
        source_values = [values[key] for key in keys]
        cap, order = cases[case]
        check(row['source_keys'] == keys and row['values'] == source_values, str(identity)+' source binding')
        check(row['cap'] == cap and row['order'] == order and row['demand'] == 1, str(identity)+' fixed branch')
        expected = formula.evaluate(source_values, order, cap)[rule]
        check(len(row['states']) == len(expected['stateq']), str(identity)+' state count')
        seen = set()
        for index, (state, balance) in enumerate(zip(row['states'], expected['stateq'])):
            event = None if index == 0 else order[index-1]
            duplicate = event is not None and event in seen
            if event is not None:
                seen.add(event)
            check(state['q'] == balance, str(identity)+' prefix balance')
            check(state['duplicate'] == duplicate, str(identity)+' duplicate flag')
            check(state['event'] == event and state['seen'] == sorted(seen), str(identity)+' received reports')
            state_count += 1
            duplicate_count += int(duplicate)
        for actual, expected_key in [('q','finalq'),('admitted','admit'),('error','error'),
                                     ('excess','excess'),('feasible_refusal','feasiblerefusal'),('true_charge','true_charge')]:
            check(row[actual] == expected[expected_key], str(identity)+' '+actual)
        alias = f'{service}-out-{rule}'
        required = f'CUA-CORR-20261029 {alias} saved-{case}' if expected['admit'] else None
        check(row['output_alias'] == alias and row['required_name'] == required, str(identity)+' output binding')
        action = action_map[identity]
        browser_action = browser_map[identity]
        check(action['alias'] == alias and browser_action['alias'] == alias, str(identity)+' action alias')
        check(action['admitted'] is expected['admit'], str(identity)+' decision dispatched')
        check(action['dispatches'] == browser_action['dispatches'] == int(expected['admit']), str(identity)+' dispatch count')
        check(action['exact_id_match'] is True and action['expected_field_match'] is True, str(identity)+' readback labels')
        check(action['before'] == browser_action['before'], str(identity)+' browser before field')
        check(action['dispatch_time'] == browser_action['time'], str(identity)+' action time')
        check(stamp(action['before_time']) < stamp(action['dispatch_time']) < stamp(action['after_time']), str(identity)+' observation order')
        check(all(re.fullmatch(r'[0-9a-f]{64}', action[key]) is not None for key in ['before_sha256','after_sha256']), str(identity)+' readback hash forms')
        wanted_after = required if expected['admit'] else action['before']
        check(action['after'] == wanted_after == browser_action['intended'], str(identity)+' saved field or unchanged refusal')
        admitted_count += int(expected['admit'])
        refusal_count += int(not expected['admit'])
        total = totals[rule]
        total['decisions'] += 1
        total['admitted'] += int(expected['admit'])
        total['over'] += int(expected['error'] > 0)
        total['under'] += int(expected['error'] < 0)
        total['excess_decisions'] += int(expected['excess'] > 0)
        total['feasible_refusals'] += int(expected['feasiblerefusal'])

    for service in 'DC':
        for rule in formula.RULES:
            baseline = f'CUA-CORR-20261029 {service}-out-{rule} ready'
            prior_after_time = None
            for case in cases:
                row = action_map[(service,case,rule)]
                check(row['before'] == baseline, f'{service} {rule} {case} sequential output field')
                if prior_after_time is not None:
                    check(prior_after_time < stamp(row['before_time']), f'{service} {rule} {case} separate action period')
                baseline = row['after']
                prior_after_time = stamp(row['after_time'])

    result = {
        'passed': True, 'assertions': checks,
        'source_records': len(source_aliases), 'source_versions': len(observations),
        'source_browser_dispatches': sum(row['dispatches'] for row in correction_rows),
        'rule_decisions': len(decisions), 'prefix_states': state_count,
        'duplicate_steps_across_rules': duplicate_count,
        'output_browser_dispatches': admitted_count,
        'refusals_with_zero_dispatch_and_unchanged_field': refusal_count,
        'rule_totals': totals,
        'input_sha256': {name: sha(name) for name in ['independent.py','observations.json','decisions.json','actions.json','browser_actions.json']},
        'scope': 'Public evidence consistency and independent formula checks. No fresh website read. Private readback hashes are checked for form only; the private evidence audit checks their contents. Cleanup is outside this check.',
    }
    rendered = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.out:
        args.out.write_text(rendered)
    print(rendered, end='')


if __name__ == '__main__':
    main()
