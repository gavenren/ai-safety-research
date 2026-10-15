#!/usr/bin/env python3
"""Independent read-only checks of the saved live trial evidence.

This code does not import live_analyze.py. It parses task label lines and their
adjacent checkboxes, then compares the derived results with the analysis files.
No network call or browser action is used. Final text review is a separate step.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from urllib.parse import urlsplit
import zipfile


def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_rows(snapshot):
    """Read only exact task label rows, not input values or counters."""
    found = []
    lines = snapshot.splitlines()
    for index, line in enumerate(lines):
        text = line.strip()
        match = re.fullmatch(r'- generic: (RETRY-20261015-[A-Z0-9-]+)', text)
        style = 'T'
        if not match:
            match = re.fullmatch(r'\d+ text (RETRY-20261015-[A-Z0-9-]+)', text)
            style = 'P'
        if not match:
            continue
        previous = lines[index - 1].strip() if index else ''
        if style == 'T':
            assert previous.startswith('- checkbox'), (text, previous)
            active = '[checked]' not in previous
        else:
            assert re.match(r'\d+ checkbox .*Description: Toggle Todo, Value: [01]$', previous), (text, previous)
            active = previous.endswith('Value: 0')
        found.append((match.group(1), active))
    return found


def selected_view(event):
    fragment = urlsplit(event['url']).fragment.rstrip('/')
    return {'': 'All', '/': 'All', '/all': 'All', '/completed': 'Completed', '/active': 'Active'}[fragment]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fresh-copy', action='store_true', help='Also run the analyzer in a temporary copy and compare outputs.')
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    errors, warnings, checks = [], [], []
    metadata = []

    def check(condition, name, detail=None):
        checks.append({'check': name, 'pass': bool(condition)})
        if not condition:
            errors.append({'check': name, 'detail': detail})

    assignments = list(csv.DictReader((base / 'live_assignments.csv').open()))
    aid = {a['trial_id']: a for a in assignments}
    check(len(assignments) == len(aid) == 60, '60 unique assignments')
    check(len({a['token'] for a in assignments}) == 60, '60 unique trial tokens')
    cells = collections.Counter((a['runner'], a['view'], a['rule']) for a in assignments)
    check(len(cells) == 20 and set(cells.values()) == {3}, 'three repeats in each of 20 design cells')
    plan = json.loads((base / 'live_plan_manifest.json').read_text())
    for name, digest in plan['files'].items():
        check(sha(base / name) == digest, 'plan hash: ' + name)
    manifest = json.loads((base / 'live_evidence_manifest.json').read_text())
    for name, digest in manifest['sha256'].items():
        check(sha(base / name) == digest, 'raw evidence hash: ' + name)
    work = base.parent.parent / 'work' / '2026-10-15-real-web'
    for name, digest in manifest['raw_source_sha256'].items():
        source = work / name
        if source.exists():
            check(sha(source) == digest, 'unchanged source bytes: ' + name)
    older = json.loads((base / 'browser_evidence_manifest.json').read_text())
    for name, digest in older['sha256'].items():
        check(sha(base / name) == digest, 'prior local pilot evidence hash: ' + name)
    prior_browser = json.loads((base / 'browser_reproduction_check.json').read_text())
    for name, digest in prior_browser['input_sha256'].items():
        check(sha(base / name) == digest, 'prior local pilot input or output hash: ' + name)
    simulation = json.loads((base / 'reproduction_check.json').read_text())
    for name, digest in simulation['input_sha256'].items():
        check(sha(base / name) == digest, 'prior simulation input hash: ' + name)
    for record in simulation['files_compared']:
        check(sha(base / record['file']) == record['saved_sha256'], 'prior simulation output hash: ' + record['file'])
    check(len(list(csv.DictReader((base / 'results_runs.csv').open()))) == 13440, 'prior simulation has 13440 runs')
    check(len(list(csv.DictReader((base / 'browser_results.csv').open()))) == 18, 'prior local pilot has 18 trials')
    derived = []
    event_types = {}
    input_holds = []
    all_observations = 0
    raw_counts = {}
    with zipfile.ZipFile(base / 'live_screenshots.zip') as screenshots:
        images = [x for x in screenshots.namelist() if not x.endswith('/')]
        check(len(images) == len(set(images)) == 60, '60 distinct archived screenshots')
        for name in images:
            check(screenshots.read(name).startswith(b'\xff\xd8\xff'), 'JPEG bytes: ' + name)
            if (work / name).exists():
                check(screenshots.read(name) == (work / name).read_bytes(), 'unchanged screenshot: ' + name)

        for runner in 'TP':
            events = [json.loads(s) for s in (base / f'live_runner_{runner}_actions.jsonl').read_text().splitlines()]
            results = json.loads((base / f'live_runner_{runner}_results.json').read_text())
            raw_counts[runner] = {'events': len(events), 'results': len(results),
                'scored_actions': sum(bool(e.get('trial_id')) and e['action'] not in ('clock_check', 'diagnostic_correction') for e in events)}
            event_types[runner] = dict(collections.Counter(e['action'] for e in events))
            expected = [a['trial_id'] for a in assignments if a['runner'] == runner]
            check([r['trial_id'] for r in results] == expected, runner + ' result order is all 30 assignments')
            check([e['trial_id'] for e in events if e['action'] == 'initial_submit'] == expected,
                  runner + ' initial action order is all 30 assignments')
            unknown = {e.get('trial_id') for e in events} - set(expected) - {None}
            check(not unknown, runner + ' has no unassigned trial action', sorted(unknown))
            admission_origin = min(stamp(e['before_utc']) for e in events if e.get('trial_id') and e['action'].startswith('prepare_'))
            previous_audit = {}
            for result in results:
                tid = result['trial_id']
                assignment = aid[tid]
                token = assignment['token']
                local = [e for e in events if e.get('trial_id') == tid]
                observed = [e for e in local if 'snapshot' in e]
                all_observations += len(observed)
                by = collections.defaultdict(list)
                for event in local:
                    by[event['action']].append(event)
                for key in ('trial_id', 'runner', 'site', 'rule', 'view', 'token'):
                    check(result[key] == assignment[key], tid + ' assignment ' + key)
                check(result['repeat'] == int(assignment['repeat']), tid + ' repeat')
                for action in ('initial_submit', 'audit_all', 'audit_reload', 'audit_screenshot'):
                    check(len(by[action]) == 1, tid + ' one ' + action)
                decision_events = by['decision'] + by['model_decision']
                check(len(decision_events) == 1, tid + ' one decision')
                initial, pre, post = (by[k][0] for k in ('initial_submit', 'audit_all', 'audit_reload'))
                decision = decision_events[0]
                prior = [e for e in observed if stamp(e['after_utc']) <= stamp(decision['decision_utc'])]
                latest = prior[-1]
                prep = [e for e in observed if e['action'].startswith('prepare_')]
                check(bool(prep), tid + ' has admission observations')
                check(selected_view(prep[-1]) == assignment['view'], tid + ' starts in assigned view')
                check(any('All' in e['snapshot'] and 'Completed' in e['snapshot'] for e in prep), tid + ' ready filter controls')
                for event in observed:
                    count = sum(label == token for label, active in task_rows(event['snapshot']))
                    count_key = 'visible_exact_task_count' if runner == 'T' else 'visible_exact_token_count'
                    check(count == event[count_key], tid + ' exact raw count: ' + event['action'])
                    check(stamp(event['before_utc']) <= stamp(event['after_utc']), tid + ' action time order: ' + event['action'])
                    check(urlsplit(event['url']).hostname == assignment['site'], tid + ' assigned host: ' + event['action'])
                    if stamp(initial['before_utc']) <= stamp(event['before_utc']) < stamp(pre['before_utc']):
                        expect_view = 'All' if event['action'] == 'scope_all' else assignment['view']
                        check(selected_view(event) == expect_view, tid + ' decision view: ' + event['action'])
                counts = lambda e: sum(label == token for label, active in task_rows(e['snapshot']))
                check(counts(prep[-1]) == 0, tid + ' token absent before submission')
                retries = len(by['retry_submit'])
                check(retries <= 1, tid + ' no more than one retry')
                check(retries == result['retries'] == decision['retries'], tid + ' retry count agrees')
                check(counts(latest) == result['decision_visible_count'] == decision['decision_visible_count'], tid + ' decision count agrees')
                check(decision['decision'] == result['decision'], tid + ' decision is unchanged')
                check(counts(pre) == result['pre_reload_count'], tid + ' pre-reload count agrees')
                check(counts(post) == result['post_reload_count'], tid + ' post-reload count agrees')
                check(selected_view(pre) == selected_view(post) == 'All', tid + ' both audits use All')
                check(stamp(decision['decision_utc']) <= stamp(pre['before_utc']) <= stamp(pre['after_utc']) <= stamp(post['before_utc']), tid + ' audit follows decision')
                matching = [(label, active) for label, active in task_rows(post['snapshot']) if label == token]
                check(all(active for label, active in matching), tid + ' all matching audited tasks are active')
                if runner == 'T':
                    check(len(result['post_reload_matching_checkboxes']) == len(matching), tid + ' saved checkbox count agrees')
                else:
                    check(result['post_reload_active_count'] == sum(active for label, active in matching), tid + ' saved active count agrees')
                current_audit = collections.Counter(label for label, active in task_rows(post['snapshot']))
                check(all(current_audit[label] == n for label, n in previous_audit.items()), tid + ' retains earlier observed task rows')
                previous_audit = current_audit
                initial_time = stamp(initial['before_utc'])
                elapsed = (stamp(decision['decision_utc']) - initial_time).total_seconds()
                clock_gap = (initial_time - stamp(result['initial_submit_utc'])).total_seconds()
                check(clock_gap in (0.0, 0.001), tid + ' start clock difference is at most 1 ms')
                if clock_gap:
                    metadata.append({'trial_id': tid, 'initial_clock_gap_ms': round(clock_gap * 1000)})
                conservative_elapsed = (stamp(decision['decision_utc']) - stamp(result['initial_submit_utc'])).total_seconds()
                check(abs(result['decision_elapsed_ms'] / 1000 - conservative_elapsed) < 1e-8, tid + ' saved elapsed time agrees')
                check((elapsed <= 60) == (conservative_elapsed <= 60), tid + ' clock difference cannot change deadline result')
                admission = min(stamp(e['before_utc']) for e in prep)
                admission_elapsed = (admission - admission_origin).total_seconds()
                check(admission_elapsed < 1200, tid + ' admitted before 20-minute budget')
                check(stamp(plan['saved_utc']) < admission, tid + ' plan saved before admission')
                rule = assignment['rule']
                first_count = counts(initial)
                wait = None
                if rule in ('no_retry', 'closure', 'scope'):
                    check(retries == 0, tid + ' rule forbids retry without closure signal')
                elif rule == 'absence':
                    check(retries == int(first_count == 0), tid + ' absence retry rule')
                    if retries:
                        # The eligibility observation is the initial action record.
                        wait = 0.0
                elif rule == 'timeout24':
                    observations = by['timeout24_observe'] + by['timeout_observe']
                    check(bool(observations) == (first_count == 0), tid + ' timeout observation eligibility')
                    if observations:
                        delayed = observations[0]
                        wait = (stamp(delayed['before_utc']) - initial_time).total_seconds()
                        check(wait >= 24, tid + ' fresh observation begins after 24 seconds')
                        check(retries == int(counts(delayed) == 0), tid + ' timeout retry rule')
                        if retries:
                            check(stamp(delayed['after_utc']) <= stamp(by['retry_submit'][0]['before_utc']), tid + ' retry follows fresh timeout observation')
                if rule == 'scope':
                    check(len(by['scope_all']) == int(first_count == 0), tid + ' All scope check eligibility')
                expected_decision = 'success' if counts(latest) == 1 else 'duplicate' if counts(latest) > 1 else 'unresolved'
                check(result['decision'] == expected_decision, tid + ' decision follows visible count')
                screenshot_path = f'runner_{runner}/' + result['screenshot']
                check(screenshot_path in images, tid + ' result screenshot exists')
                check(by['audit_screenshot'][0]['path'] == result['screenshot'], tid + ' screenshot path agrees')
                check(not result['policy_deviations'] and not result['action_errors'], tid + ' no declared trial deviations or tool errors')
                for event in local:
                    check(not event.get('error'), tid + ' no logged trial tool error: ' + event['action'])
                retained = any(token in line and ('textbox ' in line or 'text field ' in line) for line in initial['snapshot'].splitlines())
                if retained:
                    input_holds.append(tid)
                npre, npost = counts(pre), counts(post)
                derived.append({**assignment, 'initial_visible_count': first_count, 'decision': result['decision'],
                    'decision_visible_count': counts(latest), 'submissions': 1 + retries, 'retries': retries,
                    'pre_reload_count': npre, 'post_reload_count': npost,
                    'post_reload_active_count': sum(active for label, active in matching),
                    'decision_elapsed_s': elapsed, 'retry_observation_elapsed_s': wait,
                    'runner_admission_elapsed_s': admission_elapsed,
                    'clean_confirmed': int(expected_decision == 'success' and npost == 1 and elapsed <= 60),
                    'duplicate': npost >= 2, 'unresolved_decision': int(expected_decision == 'unresolved'),
                    'late_decision': int(elapsed > 60), 'no_stored_item': int(npost == 0),
                    'initial_input_token_visible': retained,
                    'all_control_pass': (first_count == 1 and retries == 0 and npost == 1 and expected_decision == 'success') if assignment['view'] == 'All' else None})

    analysis_rows = {r['trial_id']: r for r in csv.DictReader((base / 'live_results.csv').open())}
    check(set(analysis_rows) == set(aid), 'analysis includes every assigned trial exactly once')
    compare_fields = ['initial_visible_count', 'decision', 'decision_visible_count', 'submissions', 'retries',
        'pre_reload_count', 'post_reload_count', 'post_reload_active_count', 'decision_elapsed_s',
        'retry_observation_elapsed_s', 'runner_admission_elapsed_s', 'clean_confirmed', 'duplicate',
        'unresolved_decision', 'late_decision', 'no_stored_item', 'initial_input_token_visible', 'all_control_pass']
    for row in derived:
        for field in compare_fields:
            actual, expected = analysis_rows[row['trial_id']][field], row[field]
            if expected is None:
                equal = actual == ''
            elif isinstance(expected, bool):
                equal = actual == str(expected)
            elif isinstance(expected, (float, int)):
                equal = math.isclose(float(actual), expected, abs_tol=1e-7)
            else:
                equal = actual == expected
            check(equal, row['trial_id'] + ' independent analysis comparison: ' + field, {'analysis': actual, 'derived': expected})
    summary = {}
    for runner in ('T', 'P', 'both'):
        rows = [r for r in derived if runner == 'both' or r['runner'] == runner]
        summary[runner] = {'trials': len(rows), 'clean_confirmed': sum(r['clean_confirmed'] for r in rows),
            'unresolved': sum(r['unresolved_decision'] for r in rows), 'duplicates': sum(r['duplicate'] for r in rows),
            'zero_after_reload': sum(r['no_stored_item'] for r in rows), 'one_after_reload': sum(r['post_reload_count'] == 1 for r in rows),
            'retries': sum(r['retries'] for r in rows), 'late': sum(r['late_decision'] for r in rows),
            'count_changed_on_reload': sum(r['pre_reload_count'] != r['post_reload_count'] for r in rows),
            'max_decision_seconds': max(r['decision_elapsed_s'] for r in rows),
            'max_admission_seconds': max(r['runner_admission_elapsed_s'] for r in rows),
            'All_controls_pass': sum(r['all_control_pass'] is True for r in rows)}
    cell_results = []
    for (runner, view, rule), _ in sorted(cells.items()):
        rows = [r for r in derived if (r['runner'], r['view'], r['rule']) == (runner, view, rule)]
        cell_results.append({'runner': runner, 'view': view, 'rule': rule,
            'clean': sum(r['clean_confirmed'] for r in rows), 'duplicate': sum(r['duplicate'] for r in rows),
            'zero': sum(r['no_stored_item'] for r in rows), 'retries': sum(r['retries'] for r in rows),
            'trials': [r['trial_id'] for r in rows]})
    analysis_summary = json.loads((base / 'live_summary.json').read_text())
    summary_fields = {'clean_confirmed': 'clean_confirmed', 'verified_clean_confirmed': 'clean_confirmed',
        'duplicate': 'duplicate', 'post_reload_zero': 'no_stored_item', 'pre_reload_zero': 'no_stored_item',
        'unresolved_decisions': 'unresolved_decision', 'late_decisions': 'late_decision',
        'retries': 'retries', 'initial_input_token_visible': 'initial_input_token_visible'}
    for group in [analysis_summary['overall']] + analysis_summary['groups']:
        rows = [r for r in derived if all(r[key] == group[key] for key in group.get('group_by', []))]
        label = ','.join(str(group[key]) for key in group.get('group_by', [])) or 'overall'
        check(group['assigned'] == len(rows), 'group assigned count: ' + label)
        for field, column in summary_fields.items():
            check(group[field] == sum(r[column] for r in rows), 'group comparison: ' + label + ' ' + field)
        if 'all_controls_passed' in group:
            check(group['all_controls_passed'] == sum(r['all_control_pass'] is True for r in rows), 'group All controls: ' + label)
    check(analysis_summary['overall']['raw_observations'] == all_observations == 302, '302 scored UI observations')
    check(analysis_summary['overall']['raw_actions'] == sum(r['scored_actions'] for r in raw_counts.values()) == 428, '428 scored action records')
    pairs = list(csv.DictReader((base / 'live_pairs.csv').open()))
    check(len(pairs) == 120, '120 planned rule-pair comparisons')
    row_index = {r['trial_id']: r for r in derived}
    pair_keys = set()
    for pair in pairs:
        a, b = row_index[pair['trial_a']], row_index[pair['trial_b']]
        key = (pair['site'], pair['view'], pair['repeat'], pair['rule_a'], pair['rule_b'])
        check(key not in pair_keys, 'unique pair: ' + str(key))
        pair_keys.add(key)
        check(a['site'] == b['site'] == pair['site'] and a['view'] == b['view'] == pair['view']
              and a['repeat'] == b['repeat'] == pair['repeat'], 'matched site view repeat: ' + str(key))
        check(a['rule'] == pair['rule_a'] and b['rule'] == pair['rule_b'] and a['rule'] != b['rule'], 'pair rule identities: ' + str(key))
        for prefix, row in [('a', a), ('b', b)]:
            for column, source in [('clean', 'clean_confirmed'), ('duplicate', 'duplicate'), ('retries', 'retries'), ('decision', 'decision')]:
                check(pair[prefix + '_' + column] == str(row[source]), 'pair outcome: ' + str(key) + ' ' + prefix + '_' + column)
            check(math.isclose(float(pair[prefix + '_decision_seconds']), row['decision_elapsed_s'], abs_tol=1e-8), 'pair time: ' + str(key) + ' ' + prefix)
        both_clean = a['clean_confirmed'] and b['clean_confirmed']
        timing = pair['b_minus_a_seconds_both_verified_clean']
        check((math.isclose(float(timing), b['decision_elapsed_s'] - a['decision_elapsed_s'], abs_tol=1e-8) if both_clean else timing == ''), 'pair time comparison eligibility: ' + str(key))
        for column, source in [('clean', 'clean_confirmed'), ('duplicate', 'duplicate')]:
            check(int(pair['b_minus_a_' + column]) == int(b[source]) - int(a[source]), 'pair outcome difference: ' + str(key) + ' ' + column)
    fresh = {'requested': args.fresh_copy, 'status': 'NOT_RUN'}
    if args.fresh_copy:
        # Copy the package, but remove saved outputs before the offline run.
        with tempfile.TemporaryDirectory(prefix='live-independent-recheck-') as folder:
            dest = Path(folder) / 'package'
            shutil.copytree(base, dest, ignore=shutil.ignore_patterns('__pycache__'))
            for name in ('live_results.csv', 'live_pairs.csv', 'live_summary.json'):
                (dest / name).unlink()
            run = subprocess.run([sys.executable, 'live_analyze.py'], cwd=dest, capture_output=True, text=True)
            equal_files = {name: (dest / name).exists() and (base / name).read_bytes() == (dest / name).read_bytes()
                           for name in ('live_results.csv', 'live_pairs.csv', 'live_summary.json')}
            fresh = {'requested': True, 'returncode': run.returncode, 'output_files_equal': equal_files,
                     'status': 'PASS' if run.returncode == 0 and all(equal_files.values()) else 'FAIL'}
            check(fresh['status'] == 'PASS', 'fresh-copy analyzer outputs match', {'stdout': run.stdout[-2000:], 'stderr': run.stderr[-2000:]})
    warnings += ['The saved records show rendered UI observations. They are not a complete tool transcript, so they cannot prove the absence of hidden reads.',
        'The T clock_check record uses T01 while its correction identifies T06. It is a diagnostic, not a browser action.',
        'The saved preflight file is a manual summary. Its raw preliminary observations are not in this package.',
        'Final screenshots show the All audit view. All 60 full task lists were checked in a separate AI image review. They do not prove the earlier decision view or action order.',
        'PASS means the saved data checks passed. Failed control trials remain study results. This file does not certify final paper text or human review.']
    output = {'status': 'PASS' if not errors else 'FAIL', 'independent_code': True,
        'validator_python': sys.version, 'validator_sha256': sha(Path(__file__)),
        'checked_records': raw_counts, 'observations_recounted': all_observations,
        'paired_comparisons_checked': len(pairs),
        'checks_passed': sum(c['pass'] for c in checks), 'checks_total': len(checks),
        'errors': errors, 'warnings': warnings, 'metadata_notes': metadata,
        'summary': summary, 'cells': cell_results, 'initial_input_retains_token_trials': input_holds,
        'event_types': event_types, 'fresh_copy_comparison': fresh,
        'input_sha256': {name: sha(base / name) for name in ['live_assignments.csv', 'live_plan.md',
            'live_runner_T_actions.jsonl', 'live_runner_P_actions.jsonl', 'live_runner_T_results.json',
            'live_runner_P_results.json', 'live_results.csv', 'live_pairs.csv', 'live_summary.json']}}
    (base / 'live_validation.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': output['status'], 'checks_passed': output['checks_passed'],
                      'checks_total': output['checks_total'], 'errors': errors, 'summary': summary}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
