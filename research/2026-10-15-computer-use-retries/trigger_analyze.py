#!/usr/bin/env python3
"""Recompute the two-tab Drive study from saved evidence (standard library only).

No network calls are made. A missing or loading list is unknown, never zero.
Assigned views and visible views remain separate. These are selected cases,
not a random sample of agent tasks. All planned trials remain in the output.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import statistics

RULES = ('absence', 'wait24', 'scope', 'receipt')
VIEWS = ('All', 'Documents')
EXPECTED_N = 32
DEADLINE_SECONDS = 120


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(value):
    value = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError('UTC offset is required')
    return value


def elapsed(start, end):
    return round((stamp(end) - stamp(start)).total_seconds(), 3) if start and end else None


def phase(record):
    return record.get('phase', record.get('label', record.get('action', '')))


def state(record):
    return record.get('state', record.get('snapshot', record.get('dom_snapshot', ''))) or ''


def is_submission(record):
    """Identify a Create tool request, including a request that returns an error.

    A successful tool call is not proof of a committed service write. The later
    independent record audit supplies the service-record count.
    """
    args = record.get('args', {})
    return record.get('type') == 'action' and record.get('action') == 'click' and args.get('name') == 'Create' and args.get('role') == 'button'


def visible_filter(text):
    if re.search(r'(?:button |button ")Documents filter applied\b', text):
        return 'Documents'
    if 'No filters applied' in text:
        return 'All'
    return 'not_shown'


def exact_receipt(text, token):
    """A current exact-name success text, excluding fields and generic toasts."""
    return bool(re.search(r'^\s*(?:\d+ text |\- (?:status|text|generic|region): ["\']?)' +
                          re.escape(token) + r' created successfully\.["\'\s]*$', text, re.M))


def list_rows(text, token):
    """Read exact folder rows within Item List; ignore the focus echo.

    Native AX and textual DOM snapshots have different row syntax. Neither a
    toast nor a text field is a row. An explicit empty folder/result view is
    usable only with page context and without a modal-only snapshot.
    """
    inside, table_seen, depth, syntax = False, False, None, None
    matches = []
    for line in text.splitlines():
        indentation = len(line) - len(line.lstrip())
        if re.match(r'^\s*\d+ table Item List(?:\s|$)', line):
            inside, table_seen, depth, syntax = True, True, indentation, 'AX'
            continue
        if re.match(r'^\s*- (?:table|grid) "Item List"(?:\s|:|$)', line):
            inside, table_seen, depth, syntax = True, True, indentation, 'DOM'
            continue
        if inside and line.strip() and indentation <= depth:
            inside = False
        if not inside:
            continue
        if syntax == 'AX':
            matched = re.match(r'^\s*\d+ row(?: \([^\n)]*\))? ' + re.escape(token) + r' Folder(?:\s|$)', line)
        else:
            matched = re.match(r'^\s*- row "' + re.escape(token) + r' Folder(?:\s|["\'])', line)
        if matched:
            matches.append(line.strip())
    if table_seen:
        return len(matches), matches
    empty = any(x in text for x in ('No matching results', 'Drop files here', 'empty-view-content-folder'))
    page = ('Google Drive' in text or 'link "Drive"' in text) and ('Folder Path' in text or 'toolbar Filters' in text)
    if page and empty:
        return 0, []
    return None, []


def ready(text, token):
    """The plan requires enabled New, explicit view, and usable list content."""
    new_lines = [line for line in text.splitlines()
                 if re.match(r'^\s*(?:- button "New"|\d+ button(?: \([^)]*\))? New\b)', line)]
    enabled_new = any('disabled' not in line.lower() for line in new_lines)
    return enabled_new and visible_filter(text) in VIEWS and list_rows(text, token)[0] is not None


def distribution(values):
    values = [x for x in values if x is not None]
    return {'n': len(values), 'minimum': min(values) if values else None,
            'median': statistics.median(values) if values else None,
            'maximum': max(values) if values else None}


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        if not rows:
            return
        writer = csv.DictWriter(handle, list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


class Analysis:
    def __init__(self, source):
        self.source, self.inputs, self.issues, self.checks = source, {}, [], 0

    def check(self, condition, code, trial_id=None, detail=None):
        self.checks += 1
        if not condition:
            self.issues.append({'severity': 'error', 'code': code, 'trial_id': trial_id, 'detail': detail})
        return bool(condition)

    def warn(self, code, trial_id=None, detail=None):
        self.issues.append({'severity': 'warning', 'code': code, 'trial_id': trial_id, 'detail': detail})

    def read(self, name):
        path = self.source / name
        self.inputs[name] = sha(path)
        return path.read_text(encoding='utf-8')

    def json(self, name):
        return json.loads(self.read(name))

    def run(self):
        assignments = [dict(a, trial_id=a.get('trial_id', a.get('trial')), rule=a['rule'].lower(),
                            view=a.get('view', a.get('assigned_view')))
                       for a in csv.DictReader(self.read('trigger_assignments.csv').splitlines())]
        manifest = self.json('trigger_plan_manifest.json')
        for name, expected in manifest['files'].items():
            expected_hash = expected.get('sha256') if isinstance(expected, dict) else expected
            actual_hash = sha(self.source / name)
            self.inputs[name] = actual_hash
            self.check(expected_hash == actual_hash, 'saved_plan_hash', detail=name)
        self.check(len(assignments) == EXPECTED_N, 'assignment_count', detail=len(assignments))
        self.check(len({a['trial_id'] for a in assignments}) == len(assignments), 'unique_trial_ids')
        self.check(len({a['token'] for a in assignments}) == len(assignments), 'unique_tokens')
        for rule in RULES:
            for view in VIEWS:
                count = sum(a['rule'] == rule and a['view'] == view for a in assignments)
                self.check(count == 4, 'cell_size', detail=[rule, view, count])
        logs = defaultdict(list)
        for runner in sorted({a['runner'] for a in assignments}):
            name = f'trigger_runner_{runner}_actions.jsonl'
            seen_record_ids = set()
            for line, content in enumerate(self.read(name).splitlines(), 1):
                if not content.strip():
                    continue
                record = dict(json.loads(content), _line=line, _runner=runner, _file=name)
                record['trial_id'] = record.get('trial_id', record.get('trial'))
                if record.get('record_id') is not None:
                    if record['record_id'] in seen_record_ids:
                        self.warn('repeated_record_id_line_order_used', record['trial_id'], [name, line, record['record_id']])
                    seen_record_ids.add(record['record_id'])
                if record.get('type') in ('correction', 'metadata_correction'):
                    self.warn('raw_metadata_correction_retained', record['trial_id'], [name, line, record.get('reason', record.get('correction'))])
                if record.get('before_utc') and record.get('after_utc'):
                    self.check(stamp(record['before_utc']) <= stamp(record['after_utc']),
                               'record_time_order', record.get('trial_id'), [name, line])
                logs[record.get('trial_id')].append(record)
        audit = self.json('trigger_connector_audit.json')
        audit_records = []
        for block in audit['blocks']:
            bn = str(block['block'])
            capacity = block.get('requested_top_k', audit.get('requested_top_k_per_block'))
            self.check(block.get('complete') is True, 'audit_complete', detail=bn)
            self.check(block['returned_count'] == len(block['records']), 'audit_returned_count', detail=bn)
            self.check(capacity is not None and block['returned_count'] < capacity, 'audit_below_capacity', detail=bn)
            audit_records.extend(dict(r, _block=bn) for r in block['records'])
        identifiers = [r.get('id', r.get('record_id')) for r in audit_records]
        self.check(all(identifiers) and len(identifiers) == len(set(identifiers)), 'unique_service_ids')
        self.check({r.get('name') for r in audit_records}.issubset({a['token'] for a in assignments}), 'audit_names_belong_to_assignments')
        self.check({str(a['block']) for a in assignments} == {str(b['block']) for b in audit['blocks']}, 'audit_blocks')
        rows = []
        for assignment in assignments:
            rows.append(self.trial(assignment, logs[assignment['trial_id']], audit_records, audit, manifest))
        cells = []
        for rule in RULES:
            for view in VIEWS:
                selected = [r for r in rows if r['rule'] == rule and r['assigned_view'] == view]
                cells.append(dict(rule=rule, view=view, **self.aggregate(selected)))
        activation = {
            'absence_retry_after_zero': any(r['rule'] == 'absence' and r['assigned_view'] == 'Documents' and r['activated_retry'] for r in rows),
            'wait24_retry_after_eligible_zero': any(r['rule'] == 'wait24' and r['assigned_view'] == 'Documents' and r['activated_retry'] for r in rows),
            'scope_zero_to_broader_view': any(r['rule'] == 'scope' and r['assigned_view'] == 'Documents' and r['activated_scope'] for r in rows),
            'receipt_while_observer_zero': any(r['rule'] == 'receipt' and r['assigned_view'] == 'Documents' and r['activated_receipt'] for r in rows)}
        by_cell = {(r['rule'], r['view']): r for r in cells}
        scope_documents = by_cell[('scope', 'Documents')]
        h1 = all(by_cell[(rule, 'Documents')]['duplicates'] > scope_documents['duplicates'] for rule in ('absence', 'wait24'))
        h2 = all(scope_documents['clean'] > by_cell[(rule, 'Documents')]['clean'] and
                 scope_documents['duplicates'] <= by_cell[(rule, 'Documents')]['duplicates'] for rule in ('absence', 'wait24'))
        h3 = all(r['clean_confirmation'] and r['retries'] == 0 for r in rows if r['assigned_view'] == 'All')
        issue_counts = dict(Counter(r['severity'] for r in self.issues))
        summary = {'status': 'FAIL' if issue_counts.get('error') else ('PASS_WITH_WARNINGS' if self.issues else 'PASS'),
                   'study': '32 selected two-tab Drive trials; descriptive counts only',
                   'checks': self.checks, 'issue_counts': issue_counts, 'issues': self.issues,
                   'total': self.aggregate(rows), 'cells': cells, 'mechanism_criteria': activation,
                   'all_required_branches_observed': all(activation.values()),
                   'hypotheses': {'H_T1_criterion_met': h1, 'H_T2_criterion_met': h2, 'H_T3_criterion_met': h3,
                                  'interpretation': 'These are the saved directional criteria for this finite case set. They are not significance tests.'},
                   'all_view_first_zero_count': sum(r['assigned_view'] == 'All' and r['first_zero'] for r in rows),
                   'all_view_first_one_count': sum(r['assigned_view'] == 'All' and r['first_ready'] and r['first_row_count'] == 1 for r in rows),
                   'all_view_clean_without_retry_count': sum(r['assigned_view'] == 'All' and r['clean_confirmation'] and r['retries'] == 0 for r in rows),
                   'first_visible_filter_counts': dict(Counter(r['first_visible_filter'] for r in rows)),
                   'limitations': ['Purposeful workflow selection.', 'One account and one service.',
                                   'Repeated cases share service state and two concurrent runners; trials are not independent population samples.',
                                   'Core rules deliberately exclude writer feedback.',
                                   'Timing includes model, browser, tool, and orchestration time.',
                                   'Counts are not population estimates; no confidence intervals or significance tests.'],
                   'input_sha256': dict(sorted(self.inputs.items()))}
        return rows, cells, summary

    def trial(self, a, records, service_records, audit, manifest):
        tid, token, rule = a['trial_id'], a['token'], a['rule']
        self.check(rule in RULES and a['view'] in VIEWS, 'valid_assignment', tid)
        observations = [r for r in records if r.get('type') == 'observation' and state(r)]
        actions = [r for r in records if r.get('type') == 'action']
        decisions = [r for r in records if r.get('type') == 'decision']
        for record in records:
            if record.get('type') in ('observation', 'action', 'decision'):
                self.check(record.get('token') == token, 'record_token_matches_assignment', tid, record['_line'])
                self.check(str(record.get('block')) == str(a['block']), 'record_block_matches_assignment', tid, record['_line'])
                self.check(record['_runner'] == a['runner'], 'record_runner_matches_assignment', tid, record['_line'])
                self.check(str(record.get('rule', rule)).lower() == rule, 'record_rule_matches_assignment', tid, record['_line'])
        def obs(*phases):
            found = [r for r in observations if phase(r) in phases]
            return found[-1] if found else None
        def count(record):
            return list_rows(state(record), token)[0] if record else None
        def clock(record, end=True):
            return record.get('after_utc' if end else 'before_utc') if record else None
        def role(record):
            return record.get('tab_role', record.get('role')) if record else None
        initial = [r for r in actions if phase(r) in ('initial_create', 'create_initial') and is_submission(r)]
        retries = [r for r in actions if phase(r) in ('retry_create', 'create_retry') and is_submission(r)]
        scopes = [r for r in actions if phase(r) in ('broaden_scope', 'remove_filter', 'scope_change') and r.get('action') != 'reload']
        self.check(len(initial) == 1, 'one_initial_create', tid, len(initial))
        self.check(len(retries) <= 1, 'at_most_one_retry', tid, len(retries))
        self.check(len(decisions) == 1, 'one_saved_decision', tid, len(decisions))
        initial = initial[0] if initial else {}
        decision = decisions[0] if decisions else {}
        start, stop = initial.get('before_utc'), decision.get('decision_utc', decision.get('after_utc'))
        duration = elapsed(start, stop)
        if start:
            self.check(stamp(manifest['saved_utc']) < stamp(start), 'plan_saved_before_create', tid)
        baseline_w = obs('baseline_writer', 'writer_baseline')
        baseline_o = obs('baseline_observer', 'observer_baseline')
        first = obs('first_observer', 'first_decision')
        first_ready_states = [r for r in observations if phase(r) in ('first_observer', 'first_decision') and ready(state(r), token)]
        if first_ready_states:
            first = first_ready_states[0]
        wait = obs('wait24_observer', 'wait24_decision', 'wait_decision')
        scope = obs('scope_observer', 'broader_decision', 'scope_decision')
        final = obs('final_observer', 'final_decision')
        first_count, wait_count, scope_count = count(first), count(wait), count(scope)
        first_ready = bool(first and ready(state(first), token))
        wait_ready = bool(wait and ready(state(wait), token))
        first_reload = [r for r in actions if phase(r) == 'first_observer' and r.get('action') == 'reload']
        wait_reload = [r for r in actions if phase(r) == 'wait24_observer' and r.get('action') == 'reload']
        eligible_wait_reload = [r for r in wait_reload if start and wait and
                                elapsed(start, r['before_utc']) >= 24 and
                                stamp(r['after_utc']) <= stamp(wait['before_utc'])]
        for r in wait_reload:
            if start and elapsed(start, r['before_utc']) < 24:
                self.warn('premature_wait_reload_excluded', tid, {'line': r['_line'], 'start_seconds': elapsed(start, r['before_utc'])})
        first_filter = visible_filter(state(first)) if first else 'not_shown'
        writer_receipts = [r for r in observations if role(r) == 'writer' and exact_receipt(state(r), token)
                           and clock(r) and start and stop and stamp(start) <= stamp(clock(r)) <= stamp(stop)]
        receipt_at_first = bool(first and any(stamp(clock(r)) <= stamp(clock(first)) for r in writer_receipts))
        working_at_first = bool(first and any(role(r) == 'writer' and 'Working' in state(r) and
                                start and stamp(start) <= stamp(clock(r)) <= stamp(clock(first)) for r in observations))
        for label, record, required_view in [('writer', baseline_w, 'All'), ('observer', baseline_o, a['view'])]:
            if record and start:
                self.check(clock(record) and stamp(clock(record)) < stamp(start), 'baseline_before_create', tid, label)
                self.check(role(record) == label, 'baseline_tab_role', tid, label)
            if count(record) != 0 or not record or visible_filter(state(record)) != required_view or not ready(state(record), token):
                self.warn('baseline_not_fully_verified', tid, {'role': label, 'count': count(record),
                          'visible_view': visible_filter(state(record)) if record else 'not_shown'})
        self.check(first is not None, 'first_observer_present', tid)
        self.check(len(first_reload) == 1, 'one_first_observer_reload', tid, len(first_reload))
        if first:
            self.check(role(first) == 'observer', 'first_is_observer', tid)
            if first_filter not in VIEWS:
                self.warn('first_ready_filter_not_explicit', tid)
            self.check(first_ready, 'first_observer_meets_ready_definition', tid)
            if start and stop:
                self.check(stamp(start) <= stamp(first['before_utc']) <= stamp(clock(first)) <= stamp(stop), 'first_inside_decision_interval', tid)
        if first_count is None:
            self.warn('first_list_unknown', tid)
        if duration is None or not 0 <= duration <= DEADLINE_SECONDS:
            self.warn('decision_outside_deadline', tid, duration)
        evidence_phase = decision.get('evidence_phase')
        chosen = obs(evidence_phase) if evidence_phase else (final or scope or wait or first)
        chosen_count = count(chosen)
        observer_candidates = [r for r in (first, wait, scope, final) if r and role(r) == 'observer' and
                               stop and stamp(clock(r)) <= stamp(stop)]
        last_observer = max(observer_candidates, key=lambda r: stamp(clock(r))) if observer_candidates else None
        last_observer_count = count(last_observer)
        confirmed = decision.get('decision') in ('confirmed', 'confirmed_row', 'confirmed_receipt')
        if evidence_phase:
            self.check(chosen is not None, 'decision_evidence_present', tid, evidence_phase)
        if chosen and stop:
            self.check(stamp(clock(chosen)) <= stamp(stop), 'evidence_before_decision', tid)
        positive_receipt = rule == 'receipt' and bool(writer_receipts)
        if confirmed:
            self.check((chosen_count == 1 and role(chosen) == 'observer' and ready(state(chosen), token)) or
                       (first_ready and first_count == 0 and positive_receipt),
                       'confirmed_claim_has_allowed_evidence', tid, evidence_phase)
        if decision.get('observer_count') is not None:
            self.check(decision['observer_count'] == last_observer_count, 'declared_observer_count_matches_raw', tid)
        if decision.get('retry_count', decision.get('retries')) is not None:
            self.check(decision.get('retry_count', decision.get('retries')) == len(retries), 'declared_retry_count_matches_actions', tid)
        retry_eligible = first_ready and first_count == 0
        if rule == 'wait24':
            retry_eligible = retry_eligible and wait_ready and wait_count == 0 and bool(eligible_wait_reload)
        if rule not in ('absence', 'wait24'):
            retry_eligible = False
        if retries:
            self.check(retry_eligible, 'retry_has_eligible_zero', tid)
            source = wait if rule == 'wait24' else first
            if source:
                self.check(stamp(clock(source)) <= stamp(retries[0]['before_utc']), 'zero_before_retry', tid)
            self.check(elapsed(start, retries[0]['before_utc']) <= DEADLINE_SECONDS, 'retry_before_deadline', tid)
        scope_active = bool(scopes) and first_ready and first_count == 0
        if scopes:
            self.check(rule == 'scope' and first_count == 0, 'scope_action_after_zero_for_scope_rule', tid)
            self.check(first_filter == 'Documents', 'scope_expands_documents_only', tid)
            self.check(scope is not None and role(scope) == 'observer', 'broader_observation_present', tid)
            if scope and visible_filter(state(scope)) != 'All':
                self.warn('broader_all_filter_not_explicit', tid)
            if first:
                self.check(stamp(clock(first)) <= stamp(scopes[0]['before_utc']), 'zero_before_scope', tid)
        if rule in ('scope', 'receipt'):
            self.check(not retries, 'no_retry_for_scope_or_receipt', tid)
        exact = [r for r in service_records if r.get('name') == token and str(r['_block']) == str(a['block'])]
        count_service = len(exact)
        for r in exact:
            self.check(r.get('mime_type', r.get('mimeType')) == 'application/vnd.google-apps.folder', 'audit_folder_type', tid)
            self.check(r.get('shared') is False, 'audit_private', tid)
        audit_time = audit.get('audit_utc', audit.get('completed_utc'))
        if audit_time and stop:
            self.check(stamp(audit_time) > stamp(stop), 'audit_after_decision', tid)
        pre, post = obs('audit_pre_reload', 'audit_before_reload'), obs('audit_post_reload', 'audit_post_reload_ready', 'audit_reload_ready')
        self.check(post is not None, 'post_reload_audit_present', tid)
        if post:
            self.check(ready(state(post), token) and visible_filter(state(post)) == 'All', 'post_reload_audit_ready_all', tid)
            self.check(count(post) == count_service, 'post_reload_audit_agrees_with_service', tid)
        for label, record in [('pre_reload', pre), ('post_reload', post)]:
            if record and stop:
                self.check(stamp(record['before_utc']) >= stamp(stop), 'audit_observation_after_decision', tid, label)
                if count(record) != count_service:
                    self.warn('browser_service_count_disagreement', tid, {'phase': label, 'browser': count(record), 'service': count_service})
        during = [r for r in records if r.get('before_utc') and start and stop and stamp(start) <= stamp(r['before_utc']) <= stamp(stop)]
        reads = [r for r in during if r.get('type') == 'observation']
        elapsed_first, elapsed_wait = elapsed(start, clock(first)), elapsed(start, clock(wait))
        branch = ('retry' if retries else 'scope' if scopes else 'receipt' if first_count == 0 and positive_receipt and confirmed else 'row' if confirmed else 'unresolved')
        create_requests = ([initial] if initial else []) + retries
        create_errors = [r for r in create_requests if r.get('error')]
        for r in create_errors:
            self.warn('create_tool_request_error', tid, {'phase': phase(r), 'line': r['_line'], 'error': r['error']})
        return {'trial_id': tid, 'rule': rule, 'assigned_view': a['view'], 'block': a['block'], 'runner': a['runner'], 'token': token,
                'baseline_writer_count': count(baseline_w), 'baseline_observer_count': count(baseline_o),
                'first_row_count': first_count, 'first_ready': first_ready, 'first_visible_filter': first_filter, 'first_seconds': elapsed_first,
                'wait24_row_count': wait_count, 'wait24_seconds': elapsed_wait,
                'wait24_reload_start_seconds': elapsed(start, clock(eligible_wait_reload[-1], False)) if eligible_wait_reload else None,
                'wait24_reload_actions': len(wait_reload),
                'scope_row_count': scope_count, 'final_evidence_row_count': chosen_count,
                'last_observer_row_count': last_observer_count,
                'writer_exact_receipt': bool(writer_receipts), 'first_zero': first_ready and first_count == 0,
                'writer_exact_receipt_at_first_observer': receipt_at_first,
                'writer_working_observed_by_first_observer': working_at_first,
                'activated_retry': bool(retries) and retry_eligible, 'activated_scope': scope_active,
                'activated_wait': rule == 'wait24' and first_ready and first_count == 0 and bool(eligible_wait_reload),
                'activated_receipt': rule == 'receipt' and first_ready and first_count == 0 and positive_receipt and confirmed,
                'branch': branch, 'retries': len(retries), 'scope_actions': len(scopes),
                'decision': decision.get('decision', 'missing'), 'evidence_phase': evidence_phase,
                'initial_create_request_utc': start, 'initial_create_tool_succeeded': bool(initial and not initial.get('error')),
                'decision_utc': stop, 'decision_seconds': duration,
                'decision_within_deadline': duration is not None and 0 <= duration <= DEADLINE_SECONDS,
                'connector_count': count_service, 'pre_reload_count': count(pre), 'post_reload_count': count(post),
                'duplicate': count_service >= 2, 'false_confirmation': confirmed and count_service != 1,
                'clean_confirmation': confirmed and count_service == 1 and duration is not None and 0 <= duration <= DEADLINE_SECONDS,
                'unresolved': not confirmed, 'writer_reads': sum(role(r) == 'writer' for r in reads),
                'observer_reads': sum(role(r) == 'observer' for r in reads),
                'explicit_tab_switch_actions': sum(phase(r) in ('switch_writer', 'switch_observer', 'tab_switch') for r in during),
                'observer_reload_actions': sum(r.get('type') == 'action' and role(r) == 'observer' and r.get('action') == 'reload' for r in during),
                'create_tool_requests': len(create_requests),
                'successful_create_tool_calls': len(create_requests) - len(create_errors),
                'errored_create_tool_calls': len(create_errors)}

    @staticmethod
    def aggregate(rows):
        return {'n': len(rows), 'first_zero': sum(r['first_zero'] for r in rows),
                'retries': sum(r['retries'] for r in rows), 'retry_activated_trials': sum(r['activated_retry'] for r in rows),
                'wait_activated_trials': sum(r['activated_wait'] for r in rows),
                'scope_activated_trials': sum(r['activated_scope'] for r in rows),
                'receipt_activated_trials': sum(r['activated_receipt'] for r in rows),
                'clean': sum(r['clean_confirmation'] for r in rows), 'unresolved': sum(r['unresolved'] for r in rows),
                'false_confirmations': sum(r['false_confirmation'] for r in rows),
                'duplicates': sum(r['duplicate'] for r in rows), 'zero': sum(r['connector_count'] == 0 for r in rows),
                'single': sum(r['connector_count'] == 1 for r in rows), 'service_records': sum(r['connector_count'] for r in rows),
                'create_tool_requests': sum(r['create_tool_requests'] for r in rows),
                'successful_create_tool_calls': sum(r['successful_create_tool_calls'] for r in rows),
                'errored_create_tool_calls': sum(r['errored_create_tool_calls'] for r in rows),
                'late_or_missing_decisions': sum(not r['decision_within_deadline'] for r in rows),
                'decision_seconds': distribution(r['decision_seconds'] for r in rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    output = args.output_dir or args.input_dir
    output.mkdir(parents=True, exist_ok=True)
    try:
        rows, cells, summary = Analysis(args.input_dir).run()
    except FileNotFoundError as error:
        raise SystemExit('Evidence is incomplete: ' + str(error.filename))
    write_csv(output / 'trigger_results.csv', rows)
    write_csv(output / 'trigger_cells.csv', cells)
    (output / 'trigger_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: summary[k] for k in ('status', 'checks', 'issue_counts', 'total', 'mechanism_criteria')}, indent=2))
    raise SystemExit(1 if summary['status'] == 'FAIL' else 0)


if __name__ == '__main__':
    main()
