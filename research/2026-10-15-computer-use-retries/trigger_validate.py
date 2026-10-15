#!/usr/bin/env python3
"""Replay the two-tab evidence with a separate parser and check saved outputs.

This is a second code path, not a claim of an independent human review. It does
not import trigger_analyze. A separate agent must review the study and code.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def label(row):
    return row.get('phase', row.get('label', row.get('action', '')))


def raw(row):
    return row.get('state', row.get('snapshot', row.get('dom_snapshot', ''))) or ''


def parse_rows(text, exact_name):
    """Use a table subtree; do not count a repeated focus description."""
    table_depth, table_kind, saw_table = None, None, False
    found = 0
    for line in text.splitlines():
        prefix = len(line) - len(line.lstrip())
        content = line.lstrip()
        ax_table = re.fullmatch(r'\d+ table Item List(?:\s.*)?', content)
        dom_table = re.match(r'- (?:table|grid) "Item List"(?::|\s|$)', content)
        if ax_table or dom_table:
            table_depth, table_kind, saw_table = prefix, 'ax' if ax_table else 'dom', True
            continue
        if table_depth is None:
            continue
        if content and prefix <= table_depth:
            table_depth = None
            continue
        if table_kind == 'ax':
            row = re.fullmatch(r'\d+ row(?: \([^)]*\))? (.+)', content)
            if row and row.group(1).startswith(exact_name + ' Folder'):
                remainder = row.group(1)[len(exact_name + ' Folder'):]
                found += int(not remainder or remainder[0].isspace())
        else:
            row = re.match(r'- row "([^\n]+)"', content)
            if row:
                found += int(row.group(1) == exact_name + ' Folder' or row.group(1).startswith(exact_name + ' Folder '))
    if saw_table:
        return found
    has_page = ('Google Drive' in text or 'link "Drive"' in text) and ('Folder Path' in text or 'toolbar Filters' in text)
    has_empty = any(s in text for s in ('No matching results', 'Drop files here', 'empty-view-content-folder'))
    return 0 if has_page and has_empty else None


def parse_view(text):
    if re.search(r'button ["\']?Documents filter applied\b', text):
        return 'Documents'
    return 'All' if 'No filters applied' in text else 'not_shown'


def receipt(text, token):
    for line in text.splitlines():
        content = line.strip()
        if re.fullmatch(r'\d+ text ' + re.escape(token) + r' created successfully\.', content):
            return True
        if re.fullmatch(r'- (?:text|status|generic|region): ["\']?' + re.escape(token) + r' created successfully\.["\']?', content):
            return True
    return False


def is_ready(text, token):
    candidates = []
    for line in text.splitlines():
        content = line.strip()
        if re.match(r'- button "New"(?::|\s|$)', content) or re.match(r'\d+ button(?: \([^)]*\))? New\b', content):
            candidates.append(content)
    return any('disabled' not in s.lower() for s in candidates) and parse_view(text) != 'not_shown' and parse_rows(text, token) is not None


def run(base):
    checks, failures, warnings = [], [], []
    def check(name, result):
        checks.append({'check': name, 'pass': bool(result)})
        if not result:
            failures.append(name)
    token = 'RETRY-EXAMPLE-01'
    table = '1 table Item List\n\t2 row (selected) ' + token + ' Folder Owned by me\n'
    check('parser counts one row', parse_rows(table, token) == 1)
    check('parser ignores focus echo', parse_rows(table + 'The focused UI element is 2 row (selected) ' + token + ' Folder\n', token) == 1)
    check('parser counts duplicate rows', parse_rows(table + '\t3 row ' + token + ' Folder Owned by me\n', token) == 2)
    check('parser requires exact name', parse_rows(table.replace(token, token + 'X'), token) == 0)
    check('parser requires folder type boundary', parse_rows(table.replace(' Folder ', ' Folders '), token) == 0)
    check('parser ignores out of table rows', parse_rows('1 table Item List\n2 row ' + token + ' Folder\n', token) == 0)
    check('parser treats loading as unknown', parse_rows('Google Drive\n1 button Documents filter applied', token) is None)
    check('parser treats a modal as unknown', parse_rows('1 text field Value: ' + token, token) is None)
    check('parser accepts a contextual empty view', parse_rows('Google Drive\n1 heading Folder Path\n2 heading No matching results', token) == 0)
    check('parser rejects an ungrounded empty phrase', parse_rows('No matching results', token) is None)
    check('parser counts DOM rows', parse_rows('- table "Item List":\n  - row "' + token + ' Folder Owned by me":\n', token) == 1)
    check('exact receipt accepted', receipt('1 text ' + token + ' created successfully.', token))
    check('DOM region receipt accepted', receipt('- region: ' + token + ' created successfully.', token))
    check('generic receipt rejected', not receipt('1 text Folder created successfully.', token))
    check('filter not inferred from assignment', parse_view(table) == 'not_shown')
    empty_dom = '- link "Drive"\n- heading "Folder Path"\n- button "New":\n- generic: No filters applied\n- generic: Drop files here'
    check('ready accepts enabled empty All', is_ready(empty_dom, token))
    check('ready rejects disabled New', not is_ready(empty_dom.replace('"New":', '"New" [disabled]:'), token))
    check('ready rejects missing filter', not is_ready(empty_dom.replace('No filters applied', ''), token))

    assignments = [dict(a, trial_id=a.get('trial_id', a.get('trial')), rule=a['rule'].lower(), view=a.get('view', a.get('assigned_view')))
                   for a in csv.DictReader((base / 'trigger_assignments.csv').open())]
    manifest = json.loads((base / 'trigger_plan_manifest.json').read_text())
    for name, entry in manifest['files'].items():
        digest = entry['sha256'] if isinstance(entry, dict) else entry
        check('saved plan hash: ' + name, hashlib.sha256((base / name).read_bytes()).hexdigest() == digest)
    check('32 distinct assignments', len(assignments) == len({a['trial_id'] for a in assignments}) == 32)
    check('32 distinct names', len({a['token'] for a in assignments}) == 32)
    cells = Counter((a['rule'], a['view']) for a in assignments)
    check('eight cells with four repeats', len(cells) == 8 and set(cells.values()) == {4})
    grouped = defaultdict(list)
    input_files = ['trigger_assignments.csv', 'trigger_plan_manifest.json', *manifest['files']]
    for runner in sorted({a['runner'] for a in assignments}):
        name = f'trigger_runner_{runner}_actions.jsonl'
        input_files.append(name)
        for number, line in enumerate((base / name).read_text().splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            tid = record.get('trial_id', record.get('trial'))
            if record.get('before_utc') and record.get('after_utc'):
                check(f'{name}:{number} time order', time(record['before_utc']) <= time(record['after_utc']))
            grouped[tid].append(record)
    audit = json.loads((base / 'trigger_connector_audit.json').read_text())
    connector = defaultdict(list)
    all_ids = []
    for block in audit['blocks']:
        check('audit complete block ' + str(block['block']), block['complete'] is True)
        check('audit count block ' + str(block['block']), block['returned_count'] == len(block['records']))
        limit = block.get('requested_top_k', audit.get('requested_top_k_per_block'))
        check('audit capacity block ' + str(block['block']), limit is not None and block['returned_count'] < limit)
        for item in block['records']:
            connector[(str(block['block']), item['name'])].append(item)
            all_ids.append(item.get('id', item.get('record_id')))
    check('audit IDs unique and present', all(all_ids) and len(set(all_ids)) == len(all_ids))
    author = {r['trial_id']: r for r in csv.DictReader((base / 'trigger_results.csv').open())}
    check('author output includes all assigned IDs', set(author) == {a['trial_id'] for a in assignments})
    rows = []
    for a in assignments:
        tid, token = a['trial_id'], a['token']
        records = grouped[tid]
        observations = [r for r in records if r.get('type') == 'observation' and raw(r)]
        actions = [r for r in records if r.get('type') == 'action']
        decisions = [r for r in records if r.get('type') == 'decision']
        submits = [r for r in actions if r.get('action') == 'click' and r.get('args', {}).get('name') == 'Create' and r.get('args', {}).get('role') == 'button']
        initial = [r for r in submits if label(r) in ('initial_create', 'create_initial')]
        retry = [r for r in submits if label(r) in ('retry_create', 'create_retry')]
        scopes = [r for r in actions if label(r) in ('broaden_scope', 'remove_filter', 'scope_change') and r.get('action') != 'reload']
        check(tid + ' one initial write', len(initial) == 1)
        check(tid + ' at most one retry', len(retry) <= 1)
        check(tid + ' one saved decision', len(decisions) == 1)
        if not initial or not decisions:
            continue
        initial, decision = initial[0], decisions[0]
        start, stop = initial['before_utc'], decision.get('decision_utc', decision.get('after_utc'))
        duration = round((time(stop) - time(start)).total_seconds(), 3)
        check(tid + ' plan precedes first write', time(manifest['saved_utc']) < time(start))
        def observation(*names):
            found = [r for r in observations if label(r) in names]
            return found[-1] if found else None
        def rowcount(obs):
            return parse_rows(raw(obs), token) if obs else None
        first = observation('first_observer', 'first_decision')
        first_ready_states = [r for r in observations if label(r) in ('first_observer', 'first_decision') and is_ready(raw(r), token)]
        if first_ready_states:
            first = first_ready_states[0]
        wait = observation('wait24_observer', 'wait24_decision', 'wait_decision')
        wait_reload = [r for r in actions if label(r) == 'wait24_observer' and r.get('action') == 'reload']
        eligible_wait_reload = [r for r in wait_reload if wait is not None and
                                (time(r['before_utc']) - time(start)).total_seconds() >= 24 and
                                time(r['after_utc']) <= time(wait['before_utc'])]
        for r in wait_reload:
            if (time(r['before_utc']) - time(start)).total_seconds() < 24:
                warnings.append({'trial_id': tid, 'issue': 'Premature Wait24 reload retained in cost but excluded from retry eligibility.'})
        broad = observation('scope_observer', 'broader_decision', 'scope_decision')
        final = observation('final_observer', 'final_decision')
        check(tid + ' first observer evidence exists', first is not None)
        if not first:
            continue
        first_count = rowcount(first)
        first_ready = is_ready(raw(first), token)
        role = lambda r: r.get('tab_role', r.get('role')) if r else None
        exact_receipts = [r for r in observations if role(r) == 'writer' and receipt(raw(r), token)
                          and time(start) <= time(r['after_utc']) <= time(stop)]
        has_receipt = bool(exact_receipts)
        check(tid + ' first observer is correct tab role', role(first) == 'observer')
        check(tid + ' first observer meets ready definition', first_ready)
        check(tid + ' first state inside decision interval', time(start) <= time(first['before_utc']) <= time(first['after_utc']) <= time(stop))
        eligible = first_ready and first_count == 0 and a['rule'] in ('absence', 'wait24')
        if a['rule'] == 'wait24':
            eligible = eligible and wait is not None and is_ready(raw(wait), token) and rowcount(wait) == 0 and bool(eligible_wait_reload)
        if retry:
            check(tid + ' retry eligibility', eligible)
            before_retry = wait if a['rule'] == 'wait24' else first
            check(tid + ' retry follows zero', before_retry is not None and time(before_retry['after_utc']) <= time(retry[0]['before_utc']))
            check(tid + ' retry not after deadline', (time(retry[0]['before_utc']) - time(start)).total_seconds() <= 120)
        if scopes:
            check(tid + ' scope rule expands after zero', a['rule'] == 'scope' and first_count == 0)
            check(tid + ' scope does not retry', not retry)
        selected = observation(decision.get('evidence_phase')) if decision.get('evidence_phase') else (final or broad or wait or first)
        observer_evidence = [r for r in (first, wait, broad, final) if r and role(r) == 'observer' and time(r['after_utc']) <= time(stop)]
        last_observer = max(observer_evidence, key=lambda r: time(r['after_utc'])) if observer_evidence else None
        if decision.get('observer_count') is not None:
            check(tid + ' declared observer count matches actual observer', decision['observer_count'] == rowcount(last_observer))
        confirmed = decision.get('decision') in ('confirmed', 'confirmed_row', 'confirmed_receipt')
        if confirmed:
            check(tid + ' confirmation has allowed evidence',
                  (rowcount(selected) == 1 and role(selected) == 'observer' and is_ready(raw(selected), token)) or
                  (a['rule'] == 'receipt' and first_ready and first_count == 0 and has_receipt))
        service = connector[(str(a['block']), token)]
        service_count = len(service)
        for item in service:
            check(tid + ' audited object is a folder', item.get('mime_type', item.get('mimeType')) == 'application/vnd.google-apps.folder')
            check(tid + ' audited object is private', item.get('shared') is False)
        audit_time = audit.get('audit_utc', audit.get('completed_utc'))
        check(tid + ' service audit follows decision', audit_time is not None and time(audit_time) > time(stop))
        pre = observation('audit_pre_reload', 'audit_before_reload')
        post = observation('audit_post_reload', 'audit_post_reload_ready', 'audit_reload_ready')
        check(tid + ' complete post-reload audit exists', post is not None)
        if post:
            check(tid + ' post-reload audit ready All', is_ready(raw(post), token) and parse_view(raw(post)) == 'All')
            check(tid + ' post-reload audit agrees with service', rowcount(post) == service_count)
        replay = {'trial_id': tid, 'rule': a['rule'], 'assigned_view': a['view'],
                  'first_row_count': first_count, 'first_ready': first_ready, 'first_visible_filter': parse_view(raw(first)),
                  'wait24_row_count': rowcount(wait), 'scope_row_count': rowcount(broad),
                  'last_observer_row_count': rowcount(last_observer),
                  'writer_exact_receipt': has_receipt, 'retries': len(retry),
                  'activated_retry': bool(retry) and eligible,
                  'activated_wait': a['rule'] == 'wait24' and first_ready and first_count == 0 and bool(eligible_wait_reload),
                  'activated_scope': bool(scopes) and first_ready and first_count == 0,
                  'activated_receipt': a['rule'] == 'receipt' and first_ready and first_count == 0 and has_receipt and confirmed,
                  'decision_seconds': duration, 'connector_count': service_count,
                  'decision_within_deadline': 0 <= duration <= 120,
                  'pre_reload_count': rowcount(pre), 'post_reload_count': rowcount(post),
                  'duplicate': service_count >= 2, 'false_confirmation': confirmed and service_count != 1,
                  'clean_confirmation': confirmed and service_count == 1 and 0 <= duration <= 120,
                  'unresolved': not confirmed}
        create_requests = [initial] + retry
        replay.update({'initial_create_request_utc': start, 'initial_create_tool_succeeded': not bool(initial.get('error')),
                       'create_tool_requests': len(create_requests),
                       'successful_create_tool_calls': sum(not bool(r.get('error')) for r in create_requests),
                       'errored_create_tool_calls': sum(bool(r.get('error')) for r in create_requests)})
        expected = author.get(tid, {})
        for key, value in replay.items():
            if key == 'decision_seconds':
                check(tid + ' output agrees: ' + key, float(expected.get(key, 'nan')) == value)
            else:
                check(tid + ' output agrees: ' + key, expected.get(key) == ('' if value is None else str(value)))
        for name, alternatives in [('baseline_writer_count', ('baseline_writer', 'writer_baseline')),
                                   ('baseline_observer_count', ('baseline_observer', 'observer_baseline'))]:
            value = rowcount(observation(*alternatives))
            check(tid + ' output agrees: ' + name, expected.get(name) == ('' if value is None else str(value)))
            if value != 0:
                warnings.append({'trial_id': tid, 'issue': name + ' is not verified as zero'})
        rows.append(replay)
    check('all 32 trials replayed', len(rows) == 32)
    totals = {'n': len(rows), 'clean': sum(r['clean_confirmation'] for r in rows),
              'unresolved': sum(r['unresolved'] for r in rows), 'duplicates': sum(r['duplicate'] for r in rows),
              'zero': sum(r['connector_count'] == 0 for r in rows), 'single': sum(r['connector_count'] == 1 for r in rows),
              'retries': sum(r['retries'] for r in rows), 'first_zero': sum(r['first_ready'] and r['first_row_count'] == 0 for r in rows),
              'retry_activated_trials': sum(r['activated_retry'] for r in rows),
              'wait_activated_trials': sum(r['activated_wait'] for r in rows),
              'scope_activated_trials': sum(r['activated_scope'] for r in rows),
              'receipt_activated_trials': sum(r['activated_receipt'] for r in rows),
              'false_confirmations': sum(r['false_confirmation'] for r in rows),
              'service_records': sum(r['connector_count'] for r in rows)}
    totals['late_or_missing_decisions'] = sum(not r['decision_within_deadline'] for r in rows)
    for field in ('create_tool_requests', 'successful_create_tool_calls', 'errored_create_tool_calls'):
        totals[field] = sum(r[field] for r in rows)
    summary = json.loads((base / 'trigger_summary.json').read_text())
    for key, value in totals.items():
        check('summary agrees: ' + key, summary['total'][key] == value)
    for cell in summary['cells']:
        selected = [r for r in rows if (r['rule'], r['assigned_view']) == (cell['rule'], cell['view'])]
        check('cell size ' + str((cell['rule'], cell['view'])), cell['n'] == len(selected) == 4)
        check('cell duplicates ' + str((cell['rule'], cell['view'])), cell['duplicates'] == sum(r['duplicate'] for r in selected))
        check('cell clean ' + str((cell['rule'], cell['view'])), cell['clean'] == sum(r['clean_confirmation'] for r in selected))
    documents = {rule: [r for r in rows if r['rule'] == rule and r['assigned_view'] == 'Documents'] for rule in ('absence', 'wait24', 'scope')}
    scope_duplicates = sum(r['duplicate'] for r in documents['scope'])
    scope_clean = sum(r['clean_confirmation'] for r in documents['scope'])
    h1 = all(sum(r['duplicate'] for r in documents[rule]) > scope_duplicates for rule in ('absence', 'wait24'))
    h2 = all(scope_clean > sum(r['clean_confirmation'] for r in documents[rule]) and
             scope_duplicates <= sum(r['duplicate'] for r in documents[rule]) for rule in ('absence', 'wait24'))
    h3 = all(r['clean_confirmation'] and r['retries'] == 0 for r in rows if r['assigned_view'] == 'All')
    for name, outcome in [('H_T1_criterion_met', h1), ('H_T2_criterion_met', h2), ('H_T3_criterion_met', h3)]:
        check('saved hypothesis agrees: ' + name, summary['hypotheses'][name] == outcome)
    input_files += ['trigger_connector_audit.json', 'trigger_results.csv', 'trigger_summary.json', 'trigger_cells.csv']
    return {'review_kind': 'Separate evidence replay code path; no human review.', 'checks': len(checks),
            'passed': sum(t['pass'] for t in checks), 'failed': len(failures), 'problems': failures,
            'warnings': warnings, 'summary': totals, 'results': rows, 'tests': checks,
            'input_sha256': {name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in sorted(set(input_files))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', '--input-dir', dest='base', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--fresh-copy', action='store_true')
    args = parser.parse_args()
    try:
        result = run(args.base)
    except FileNotFoundError as error:
        raise SystemExit('Evidence is incomplete: ' + str(error.filename))
    if args.fresh_copy:
        repeats = []
        for iteration in (1, 2):
            with tempfile.TemporaryDirectory(prefix='trigger-replay-') as tmp:
                destination = Path(tmp)
                for source in args.base.glob('trigger*'):
                    if source.is_file() and source.suffix in ('.json', '.jsonl', '.csv', '.md', '.py'):
                        shutil.copyfile(source, destination / source.name)
                process = subprocess.run([sys.executable, str(destination / 'trigger_analyze.py'),
                                          '--input-dir', str(destination), '--output-dir', str(destination)],
                                         capture_output=True, text=True)
                agreement = {name: (destination / name).exists() and (destination / name).read_bytes() == (args.base / name).read_bytes()
                             for name in ('trigger_results.csv', 'trigger_cells.csv', 'trigger_summary.json')}
                passed = process.returncode == 0 and all(agreement.values())
                repeats.append({'iteration': iteration, 'exit_code': process.returncode,
                                'saved_output_byte_agreement': agreement, 'pass': passed})
                result['checks'] += 1
                result['passed'] += int(passed)
                result['failed'] += int(not passed)
                if not passed:
                    result['problems'].append('Fresh copy replay ' + str(iteration))
        result['fresh_copy_reproduction'] = repeats
    (args.output or args.base / 'trigger_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('checks', 'passed', 'failed', 'warnings', 'summary')}, indent=2))
    raise SystemExit(1 if result['failed'] else 0)


if __name__ == '__main__':
    main()
