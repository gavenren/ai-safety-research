#!/usr/bin/env python3
"""Independent standard-library reconstruction of the additional website trials.

This code does not import the main analyzer and does not read runner summaries.
Rows come from the cells in saved table observations. Footer totals are retained
as evidence but are not part of the supplied policy. No website access occurs.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import random
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc(text):
    return dt.datetime.fromisoformat(text.replace('Z', '+00:00'))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def parse_state(text, site, token=''):
    """Parse cell-bearing rows, rather than counting mentions of a token."""
    rows, cells = [], None
    for line in text.splitlines():
        if re.match(r'^\s*- (?:\x27)?row ', line):
            if cells:
                rows.append(cells)
            cells = []
        match = re.match(r'^\s*- cell ("(?:[^"\\]|\\.)*")', line)
        if match and cells is not None:
            cells.append(json.loads(match.group(1)))
    if cells:
        rows.append(cells)
    if site == 'demoqa':
        search = re.search(r'(?m)^\s*- textbox "Type to search"(?: \[[^\]]+\])?(?:: (.*))?$', text)
        add = re.search(r'(?m)^\s*- button "Add"(?: \[active\])?$', text)
        headers = all('columnheader "' + h + '"' in text for h in
                      ['First Name', 'Last Name', 'Age', 'Email', 'Salary', 'Department', 'Action'])
        next_disabled = 'button "Next" [disabled]' in text
        ready = bool('heading "Web Tables"' in text and add and search and headers
                     and next_disabled and '- dialog:' not in text and '- table:' in text
                     and 'textbox "First Name"' not in text and all(len(r) == 7 for r in rows))
        targets = [r for r in rows if len(r) == 7 and r[0] == token]
        empty_marker = not rows
    else:
        search = re.search(r'(?m)^\s*- searchbox "Search:"(?: \[[^\]]+\])?(?:: (.*))?$', text)
        add = re.search(r'(?m)^\s*- button "Add new row"(?: \[active\])?$', text)
        headers = all('columnheader "Column ' + str(i) in text for i in range(1, 6))
        next_disabled = 'link "Next" [disabled]' in text
        numeric_rows = [r for r in rows if len(r) == 5]
        empty_marker = 'No matching records found' in text
        ready = bool(add and search and headers and next_disabled and '- table:' in text
                     and (numeric_rows or empty_marker)
                     and all(len(r) == 5 or r == ['No matching records found'] for r in rows))
        rows = numeric_rows
        targets = [r for r in rows if r != ['1.1', '1.2', '1.3', '1.4', '1.5']]
    search_value = search.group(1) if search and search.group(1) else ''
    if search_value.startswith('"') and search_value.endswith('"'):
        search_value = json.loads(search_value)
    return dict(ready=ready, search=search_value if search else None,
                view=('All' if search_value == '' else 'Hidden' if search_value == 'CROSS-NOMATCH' else 'Other') if search else 'Unknown',
                rows=rows, targets=targets, count=len(targets) if ready else None,
                next_disabled=next_disabled, empty_marker=empty_marker)


QA_DEFAULT = [
    ['Cierra', 'Vega', '39', 'cierra@example.com', '10000', 'Insurance', 'EditDelete'],
    ['Alden', 'Cantrell', '45', 'alden@example.com', '12000', 'Compliance', 'EditDelete'],
    ['Kierra', 'Gentry', '29', 'kierra@example.com', '2000', 'Legal', 'EditDelete'],
]
DT_DEFAULT = [['1.1', '1.2', '1.3', '1.4', '1.5']]


def trial(assignment, records, frozen):
    tid, site, rule = assignment['trial_id'], assignment['site'], assignment['rule']
    checks = {}
    def check(name, condition):
        checks[name] = bool(condition)
    def phase(name, kind=None):
        return [r for r in records if r.get('phase') == name and (kind is None or r['kind'] == kind)]
    def one(name, kind=None):
        matches = phase(name, kind)
        return matches[0] if len(matches) == 1 else None
    def state(record, key='state'):
        return parse_state(record.get(key, ''), site, assignment['token']) if record else parse_state('', site)
    def record_time(record):
        for key in ['start_utc', 'decision_utc', 'capture_start_utc', 'utc']:
            if key in record:
                return utc(record[key])
        return None
    submit = one('initial_submit', 'action')
    if not submit:
        return {**assignment, 'status': 'not_started', 'records': len(records), 'checks': checks}
    initial = utc(submit['start_utc'])
    retries = phase('retry_submit', 'action')
    decisions = [r for r in records if r['kind'] == 'decision']
    decision = decisions[0] if len(decisions) == 1 else None
    audit_records = [r for r in records if r['kind'] == 'audit']
    cleanup_records = [r for r in records if r['kind'] == 'cleanup']
    baseline, assigned, first = one('baseline_all', 'observation'), one('baseline_assigned', 'observation'), one('first_observation', 'observation')
    bs, av, fs = state(baseline), state(assigned), state(first)
    default = QA_DEFAULT if site == 'demoqa' else DT_DEFAULT
    check('freeze_before_initial_request', initial > utc(frozen))
    check('complete_default_baseline', bs['ready'] and bs['view'] == 'All' and bs['rows'] == default)
    check('assigned_view_ready', av['ready'] and av['view'] == assignment['view'] and av['count'] == 0)
    check('first_view_ready', fs['ready'])
    check('fresh_first_observation', first and utc(first['start_utc']) >= utc(submit['end_utc']))
    check('at_most_one_retry', len(retries) <= 1)
    check('write_before_deadline', all(0 <= (utc(r['start_utc']) - initial).total_seconds() < 120 for r in retries))
    check('no_action_tool_errors', all(r.get('error') is None for r in records if r['kind'] == 'action'))
    times = [record_time(r) for r in records if record_time(r) is not None]
    check('ordered_record_times', all(a <= b for a, b in zip(times, times[1:])))
    check('action_intervals_nonnegative', all(utc(r['start_utc']) <= utc(r['end_utc']) for r in records if 'start_utc' in r and 'end_utc' in r))
    if site == 'demoqa':
        wanted = dict(first_name=assignment['token'], last_name='TEMP', email=assignment['email'], age='30', salary='1', department='Test')
        fills = phase('initial_fill', 'action') + phase('retry_fill', 'action')
        check('all_six_fill_arguments', len(fills) == 1 + len(retries) and all(r.get('args') == wanted for r in fills))
        # Email is redacted by the browser in form fields, but is visible in audit cells.
        field_names = [('First Name', wanted['first_name']), ('Last Name', 'TEMP'), ('Age', '30'), ('Salary', '1'), ('Department', 'Test')]
        def filled(r):
            for name, val in field_names:
                match = re.search(r'(?m)^\s*- textbox "' + re.escape(name) + r'"(?: \[[^\]]+\])?: (.+)$', r.get('state', ''))
                if not match or match.group(1).strip('"') != val:
                    return False
            return 'textbox "name@example.com": <redacted>' in r.get('state', '')
        check('visible_filled_fields', all(filled(r) for r in fills))
    late = one('wait24_observation', 'observation')
    ls = state(late)
    wait_seconds = (utc(late['start_utc']) - initial).total_seconds() if late else None
    scope = one('scope_clear', 'action')
    ss = state(one('scope_observation', 'observation'))
    if fs['count'] == 1:
        check('one_row_stops_without_retry', not retries and not scope and not late)
    elif fs['count'] == 0 and rule == 'Absence':
        check('absence_retry_after_ready_zero', len(retries) == 1 and utc(retries[0]['start_utc']) >= utc(first['end_utc']))
    elif fs['count'] == 0 and rule == 'Wait24':
        check('eligible_wait24_read', late and wait_seconds >= 24 and utc(late['start_utc']) >= utc(first['end_utc']))
        check('wait24_retry_after_fresh_zero', len(retries) == 1 and ls['ready'] and ls['count'] == 0 and utc(retries[0]['start_utc']) >= utc(late['end_utc']))
    elif fs['count'] == 0 and rule == 'Scope':
        check('scope_clears_hidden_only', fs['view'] == 'Hidden' and scope and not retries and state(scope, 'before_state')['view'] == 'Hidden' and state(scope)['view'] == 'All')
        check('scope_observation_ready_all', ss['ready'] and ss['view'] == 'All')
    else:
        check('first_branch_supported', False)
    if not decision or not audit_records or not cleanup_records:
        return {**assignment, 'status': 'incomplete', 'records': len(records), 'checks': checks}
    by_id = {r['record_id']: r for r in records}
    evidence = by_id.get(decision.get('evidence_record'))
    es = state(evidence)
    elapsed = (utc(decision['decision_utc']) - initial).total_seconds()
    check('decision_evidence_precedes_decision', evidence and evidence['kind'] == 'observation' and utc(evidence['end_utc']) <= utc(decision['decision_utc']))
    if fs['count'] == 1:
        check('first_success_evidence_is_first_read', evidence == first)
    elif retries:
        check('retry_evidence_is_fresh_final_read', evidence and evidence.get('phase') == 'final_observation' and utc(evidence['start_utc']) >= utc(retries[-1]['end_utc']))
        check('retry_does_not_change_search', es['search'] == fs['search'])
    elif scope:
        check('scope_evidence_is_new_all_read', evidence and evidence.get('phase') == 'scope_observation' and utc(evidence['start_utc']) >= utc(scope['end_utc']) and es['view'] == 'All')
    check('decision_count_matches_state', es['ready'] and decision.get('observed_count') == es['count'])
    check('decision_matches_visible_count', decision['decision'] == ('confirmed' if es['count'] == 1 and elapsed <= 120 else 'unresolved'))
    check('decision_within_deadline', 0 <= elapsed <= 120)
    audit_record = audit_records[0]
    audit_evidence = by_id.get(audit_record.get('evidence_record'))
    aud = state(audit_evidence)
    check('complete_audit_after_decision', audit_evidence and aud['ready'] and aud['view'] == 'All' and utc(audit_evidence['start_utc']) >= utc(decision['decision_utc']))
    check('audit_count_matches_cells', audit_record['count'] == aud['count'])
    check('no_reload_before_audit', not any(r['kind'] == 'action' and 'reload' in r.get('operation', '').lower() and initial <= utc(r['start_utc']) <= utc(audit_evidence['end_utc']) for r in records))
    clean_record = cleanup_records[0]
    clean_evidence = by_id.get(clean_record.get('evidence_record'))
    cl = state(clean_evidence)
    check('cleanup_baseline_restored', cl['ready'] and cl['view'] == 'All' and cl['rows'] == default and clean_record['verified'] is True)
    check('cleanup_reload_after_audit', one('cleanup_reload', 'action') and utc(one('cleanup_reload')['start_utc']) > utc(audit_evidence['end_utc']))
    if site == 'demoqa':
        wanted_row = [assignment['token'], 'TEMP', '30', assignment['email'], '1', 'Test', 'EditDelete']
        check('audit_exact_six_fields', all(r == wanted_row for r in aud['targets']))
        check('default_rows_preserved_in_audit', [r for r in aud['rows'] if r not in aud['targets']] == default)
    else:
        check('default_row_preserved_in_audit', [r for r in aud['rows'] if r not in aud['targets']] == default)
    images = [r for r in records if r['kind'] == 'image']
    for name in ['decision', 'audit', 'cleanup']:
        matches = [r for r in images if r.get('phase') == name]
        check(name + '_image_record', len(matches) == 1)
        if len(matches) == 1:
            check(name + '_image_after_evidence', utc(matches[0]['capture_start_utc']) >= utc(decision['decision_utc'] if name == 'decision' else audit_evidence['end_utc'] if name == 'audit' else clean_evidence['end_utc']))
    clean = decision['decision'] == 'confirmed' and aud['count'] == 1 and elapsed <= 120
    return {**assignment, 'status': 'complete', 'records': len(records), 'first_count': fs['count'],
            'first_actual_view': fs['view'], 'request_count': 1 + len(retries), 'retry_count': len(retries),
            'wait24_read_seconds': round(wait_seconds, 6) if wait_seconds is not None else None,
            'scope_clear': bool(scope), 'decision': decision['decision'], 'decision_seconds': round(elapsed, 6),
            'audit_count': aud['count'], 'extra_effect': aud['count'] is not None and aud['count'] >= 2,
            'correct_confirmation': clean,
            'false_confirmation': decision['decision'] == 'confirmed' and aud['count'] is not None and aud['count'] != 1,
            'late_confirmation': decision['decision'] == 'confirmed' and elapsed > 120,
            'cleanup_verified': checks['cleanup_baseline_restored'], 'checks': checks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--allow-partial', action='store_true')
    args = parser.parse_args()
    base = args.input_dir
    assignments = list(csv.DictReader((base / 'cross_assignments.csv').open()))
    freeze = json.loads((base / 'cross_plan_manifest.json').read_text())
    files = ['cross_independent_replay.py', 'cross_assignments.csv', 'cross_plan.md', 'cross_runner_instructions.md', 'cross_preflight.md', 'cross_plan_manifest.json', 'cross_runner_q_actions.jsonl', 'cross_runner_d_actions.jsonl']
    hashes = {name: digest(base / name) for name in files}
    all_records, id_checks = {}, {}
    for runner in ['q', 'd']:
        records = read_jsonl(base / ('cross_runner_' + runner + '_actions.jsonl'))
        ids = [r['record_id'] for r in records]
        id_checks[runner] = ids == sorted(set(ids))
        for r in records:
            all_records.setdefault(r.get('trial_id'), []).append(r)
    rng = random.Random(20261016)
    recreated = []
    for site in ['demoqa', 'datatables']:
        for block in range(1, 5):
            pairs = [(r, v) for r in ['Absence', 'Wait24', 'Scope'] for v in ['All', 'Hidden']]
            rng.shuffle(pairs)
            recreated.extend((site, str(block), r, v) for r, v in pairs)
    trials = [trial(a, all_records.get(a['trial_id'], []), freeze['frozen_utc']) for a in assignments]
    groups = []
    for site in ['demoqa', 'datatables']:
        for rule in ['Absence', 'Wait24', 'Scope']:
            for view in ['All', 'Hidden']:
                ts = [t for t in trials if (t['site'], t['rule'], t['view']) == (site, rule, view)]
                complete = [t for t in ts if t['status'] == 'complete']
                groups.append(dict(site=site, rule=rule, view=view, assigned=len(ts), complete=len(complete),
                    extra_effects=sum(t['extra_effect'] for t in complete), correct_confirmations=sum(t['correct_confirmation'] for t in complete),
                    false_confirmations=sum(t['false_confirmation'] for t in complete), late_confirmations=sum(t['late_confirmation'] for t in complete),
                    unresolved=sum(t['decision'] == 'unresolved' for t in complete), retries=sum(t['retry_count'] for t in complete), cleanup_verified=sum(t['cleanup_verified'] for t in complete)))
    global_checks = dict(frozen_files_match=all(hashes[name] == h for name, h in freeze['sha256'].items()),
                         assignment_order_matches=recreated == [(a['site'], a['block'], a['rule'], a['view']) for a in assignments],
                         record_ids_monotonic=all(id_checks.values()),
                         complete_48=len(trials) == 48 and all(t['status'] == 'complete' for t in trials))
    # Read main outputs only after the independent reconstruction is complete.
    # These files are comparison targets, not evidence for any derived outcome.
    comparison = []
    if global_checks['complete_48'] and (base / 'cross_trials.csv').exists():
        main_trials = {r['trial_id']: r for r in csv.DictReader((base / 'cross_trials.csv').open())}
        fields = {'first_count': 'first_ready_count', 'retry_count': 'retry_requests',
                  'decision_seconds': 'decision_elapsed_seconds', 'audit_count': 'audit_count',
                  'wait24_read_seconds': 'wait24_observation_elapsed_seconds'}
        for t in trials:
            m = main_trials.get(t['trial_id'], {})
            for ours, theirs in fields.items():
                raw = m.get(theirs)
                if isinstance(raw, str) and raw.startswith('['):
                    values = json.loads(raw)
                    mv = values[0] if len(values) == 1 else None
                else:
                    mv = float(raw) if raw not in [None, ''] else None
                if t[ours] != mv:
                    comparison.append({'trial_id': t['trial_id'], 'field': ours, 'independent': t[ours], 'main': mv})
            for key in ['decision', 'first_actual_view']:
                if t[key] != m.get(key):
                    comparison.append({'trial_id': t['trial_id'], 'field': key})
            classification = ('correct_confirmation' if t['correct_confirmation'] else 'unresolved' if t['decision'] == 'unresolved' else 'false_confirmation')
            if classification != m.get('classification'):
                comparison.append({'trial_id': t['trial_id'], 'field': 'classification'})
        global_checks['main_trial_outputs_match'] = not comparison and len(main_trials) == 48
        hashes['cross_trials.csv'] = digest(base / 'cross_trials.csv')
    failed = [{ 'trial_id': t['trial_id'], 'check': k} for t in trials if t['status'] == 'complete' for k, v in t['checks'].items() if not v]
    issues = failed + [{'check': k} for k, v in global_checks.items() if not v]
    result = dict(status='PROVISIONAL' if args.allow_partial else 'PASS' if not issues else 'FAIL', issues=issues,
                  method='Independent cell parser and raw-record timing reconstruction; no main analyzer import or summary input.',
                  final_complete=global_checks['complete_48'], input_sha256=hashes, checks=global_checks, failed_trial_checks=failed,
                  main_output_differences=comparison, groups=groups, trials=trials)
    output = args.output or base / 'cross_independent_replay.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'complete_trials': sum(t['status'] == 'complete' for t in trials), 'global_checks': global_checks, 'failed_trial_checks': failed}, indent=2))
    return 0 if all(v for k, v in global_checks.items() if k != 'complete_48') and not failed and (args.allow_partial or global_checks['complete_48']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
