#!/usr/bin/env python3
"""Recompute the authenticated Drive extension from saved, redacted evidence.

Python standard library only. No network or browser access. A decision record is
not evidence of a row: row and receipt counts are parsed from saved UI text.
Assigned filter and visible filter are kept separate. The app can change its UI
without an agent filter action. All outputs describe these trials only.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re
import statistics

RULES = ('absence', 'wait24', 'scope', 'receipt')
VIEWS = ('All', 'Documents')
EXPECTED = 30
DEADLINE = 120.0
TOKEN = re.compile(r'RETRY-ACCOUNT-20261015-D\d{2}')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dt(s):
    if not s:
        return None
    t = datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    return t if t.tzinfo else None


def seconds(a, b):
    return (dt(b) - dt(a)).total_seconds() if a and b else None


def phase(r):
    return r.get('label', r.get('phase', r.get('action', '')))


def state(r):
    return r.get('state', r.get('snapshot', r.get('dom_snapshot', '')))


def filter_text(text):
    """Only explicit visible filter state, not an assigned view or absent chip."""
    if re.search(r'button Documents filter applied\b', text):
        return 'Documents'
    if 'No filters applied' in text:
        return 'All'
    return 'not_shown'


def exact_receipt(text, token):
    """A matching success text; modal value and generic Working do not count."""
    return bool(re.search(r'^\s*(?:\d+ text |\- (?:status|text|generic): )' +
                          re.escape(token) + r' created successfully\.["\s]*$', text, re.M))


def rows_from_ui(text, token):
    """Count exact-token folder rows only inside Item List.

    Native AX trees repeat the focused row after the tree. That repeated prose
    is not a second item. The modal and toast do not belong to Item List. A
    usable empty view counts as zero; an incomplete or modal-only state is
    unknown, not zero. A nonempty list can contain an unmatched token.
    """
    lines = text.splitlines()
    count = 0
    table_seen = False
    table_indent = None
    in_table = False
    matched = []
    for line in lines:
        if re.match(r'^\s*\d+ table Item List(?:\s|$)', line):
            table_seen = True
            table_indent = len(line) - len(line.lstrip())
            in_table = True
            continue
        if in_table:
            indent = len(line) - len(line.lstrip())
            if line.strip() and indent <= table_indent:
                in_table = False
                continue
            # An exact token followed by the visible Folder type.
            if re.match(r'^\s*\d+ row(?: \([^\n)]*\))? ' + re.escape(token) +
                        r' Folder(?:\s|$)', line):
                count += 1
                matched.append(line.strip())
    if table_seen:
        return count, matched
    empty = ('No matching results' in text or 'Drop files here' in text)
    page = 'Google Drive' in text and ('Folder Path' in text or 'toolbar Filters' in text)
    modal_only = bool(re.search(r'^\s*\d+ heading New folder', text, re.M)) and not page
    if page and empty and not modal_only:
        return 0, []
    return None, []


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as h:
        if not rows:
            return
        w = csv.DictWriter(h, list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (list, dict)) else v for k, v in r.items()})


def dist(xs):
    xs = [x for x in xs if x is not None]
    return dict(n=len(xs), minimum=min(xs) if xs else None,
                median=statistics.median(xs) if xs else None,
                maximum=max(xs) if xs else None,
                mean=statistics.mean(xs) if xs else None)


class Analysis:
    def __init__(self, source):
        self.source = source
        self.issues = []
        self.checks = 0
        self.inputs = {}

    def issue(self, severity, code, trial_id, detail):
        self.issues.append(dict(severity=severity, code=code, trial_id=trial_id, detail=detail))

    def check(self, condition, code, trial_id, detail):
        self.checks += 1
        if not condition:
            self.issue('error', code, trial_id, detail)
        return condition

    def read_json(self, name):
        p = self.source / name
        self.inputs[name] = sha(p)
        return json.loads(p.read_text())

    def read_logs(self, runner):
        name = f'account_runner_{runner}_actions.jsonl'
        p = self.source / name
        self.inputs[name] = sha(p)
        records = [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
        # Apply only explicit correction evidence. Raw lines remain unchanged.
        correction_path = self.source / f'account_runner_{runner}_corrections.json'
        corrections = self.read_json(correction_path.name) if correction_path.exists() else []
        corrections += [r for r in records if r.get('type') in ('metadata_correction', 'correction')]
        seen_corrections = set()
        for c in corrections:
            target = c.get('target_trial_id', c.get('trial_id'))
            lo, hi = c.get('before_utc_min'), c.get('after_utc_max')
            sources = c.get('source_trial_id', 'setup')
            sources = sources if isinstance(sources, list) else [sources]
            first_line, last_line = c.get('line_start', 1), c.get('line_end', len(records))
            if target == 'D01' and '17:51:36.641' in c.get('correction', ''):
                lo, hi = '2026-10-15T17:51:19.371Z', '2026-10-15T17:51:36.641Z'
            correction_key = (target, lo, hi, first_line, last_line)
            if correction_key in seen_corrections:
                continue
            seen_corrections.add(correction_key)
            if lo and hi:
                changed = []
                for n, r in enumerate(records, 1):
                    before = r.get('before_utc', r.get('decision_utc'))
                    after = r.get('after_utc', r.get('decision_utc'))
                    in_range = first_line <= n <= last_line
                    in_time = before and after and dt(lo) <= dt(before) and dt(after) <= dt(hi)
                    if in_range and in_time and r.get('trial_id') in sources:
                        if r.get('trial_id') != target:
                            r = dict(r, original_trial_id=r['trial_id'], trial_id=target)
                            records[n-1] = r
                            changed.append(n)
                self.issue('warning', 'explicit_metadata_correction', target,
                           {'source_trial_ids': sources, 'changed_lines': changed,
                            'line_start': first_line, 'line_end': last_line,
                            'before_utc_min': lo, 'after_utc_max': hi})
            else:
                self.issue('warning', 'correction_not_applied', target, c)
        for n, r in enumerate(records, 1):
            r['_line'] = n
            r['_runner'] = runner
            if r.get('before_utc') and r.get('after_utc'):
                self.check(dt(r['before_utc']) <= dt(r['after_utc']), 'negative_record_duration', r.get('trial_id'), n)
        return records

    def run(self):
        p = self.source / 'account_assignments.csv'
        self.inputs[p.name] = sha(p)
        assignments = list(csv.DictReader(p.open()))
        plan_manifest = self.read_json('account_plan_manifest.json')
        for filename, expected_hash in plan_manifest.get('files', {}).items():
            actual_hash = sha(self.source / filename)
            self.inputs[filename] = actual_hash
            self.check(actual_hash == expected_hash, 'saved_plan_hash_mismatch', None, filename)
        for a in assignments:
            self.check(a['rule'] in RULES and a['view'] in VIEWS, 'unknown_assignment', a['trial_id'], a)
            self.check(a['token'] == 'RETRY-ACCOUNT-20261015-' + a['trial_id'],
                       'assignment_token_mismatch', a['trial_id'], a['token'])
        for rule in RULES:
            for view in VIEWS:
                n = sum(a['rule']==rule and a['view']==view for a in assignments)
                self.check(n == (3 if rule=='receipt' else 4), 'assignment_group_size', None, [rule,view,n])
        self.check(len(assignments) == EXPECTED, 'assignment_count', None, len(assignments))
        self.check(len({x['trial_id'] for x in assignments}) == EXPECTED, 'assignment_unique', None, '')
        all_logs = []
        results = []
        for runner in ('A', 'B'):
            all_logs.extend(self.read_logs(runner))
            raw = self.read_json(f'account_runner_{runner}_results.json')
            if isinstance(raw, dict):
                raw = raw.get('results', raw.get('trials', []))
            for r in raw:
                results.append(dict(r, _runner=runner))
        indexed = defaultdict(list)
        for r in results:
            indexed[r['trial_id']].append(r)
        logs = defaultdict(list)
        for r in all_logs:
            logs[r.get('trial_id')].append(r)
        audit = self.read_json('account_connector_audit.json')
        audit_time = audit.get('audit_utc', audit.get('completed_utc'))
        records = []
        for block in audit.get('blocks', []):
            bn = str(block.get('block'))
            self.check(block.get('complete') is True, 'incomplete_connector_block', None, bn)
            for item in block.get('records', []):
                records.append(dict(item, block=bn))
        self.check(len({str(b.get('block')) for b in audit.get('blocks', [])}) == 4,
                   'connector_block_count', None, len(audit.get('blocks', [])))
        audit_ids = [r.get('id', r.get('record_id')) for r in records]
        self.check(all(audit_ids) and len(set(audit_ids)) == len(audit_ids), 'connector_id_unique', None, audit_ids)
        rows = []
        for a in assignments:
            tid, token, rule, view = (a[x] for x in ('trial_id', 'token', 'rule', 'view'))
            rlist = indexed[tid]
            self.check(len(rlist) == 1, 'result_count', tid, len(rlist))
            if len(rlist) != 1:
                continue
            r = rlist[0]
            for field in ('rule', 'view', 'token', 'block'):
                self.check(str(r.get(field)) == str(a[field]), 'assignment_mismatch', tid, field)
            self.check(r['_runner'] == a['runner'], 'runner_mismatch', tid, '')
            lr = logs[tid]
            observations = [x for x in lr if x.get('type') == 'observation' and state(x)]
            actions = [x for x in lr if x.get('type') == 'action']
            def observed(labels, last=True):
                found = [x for x in observations if phase(x) in labels]
                return (found[-1] if last else found[0]) if found else None
            baseline = observed(('baseline', 'before_trial', 'trial_ready'))
            first = observed(('first_decision',), last=False)
            pre = observed(('audit_pre_reload', 'audit_before_reload'))
            post = observed(('audit_post_reload', 'audit_post_reload_ready', 'audit_after_reload', 'audit_reload_ready_after_error'))
            decision_time = r.get('decision_utc')
            initial = [x for x in actions if phase(x) in ('initial_create', 'create_initial')]
            retry = [x for x in actions if phase(x) in ('retry_create', 'create_retry')]
            self.check(len(initial) == 1, 'initial_create_count', tid, len(initial))
            initial_time = initial[0]['before_utc'] if len(initial) == 1 else r.get('initial_submit_utc')
            declared_initial = r.get('initial_submit_utc')
            if initial_time and declared_initial and initial_time != declared_initial:
                difference = abs(seconds(initial_time, declared_initial))
                if difference <= 0.001:
                    self.issue('warning', 'initial_clock_rounding', tid, difference)
                else:
                    self.check(False, 'initial_time_mismatch', tid, [initial_time, declared_initial])
            raw_decisions = [x for x in lr if x.get('type') == 'decision']
            self.check(len(raw_decisions) == 1, 'raw_decision_count', tid, len(raw_decisions))
            if len(raw_decisions) == 1:
                for key in ('decision', 'decision_utc', 'decision_basis', 'retries'):
                    self.check(raw_decisions[0].get(key) == r.get(key), 'raw_decision_mismatch', tid, key)
            self.check(initial_time is not None, 'initial_time_missing', tid, '')
            self.check(initial_time is not None and dt(plan_manifest['saved_utc']) < dt(initial_time),
                       'plan_not_before_trial', tid, initial_time)
            # Opening the New menu can show the settled empty view after an
            # earlier baseline was still loading. Use the last readable state
            # before Create. This never treats a missing list as zero.
            prewrite = [x for x in observations if initial_time and
                        dt(x['after_utc']) <= dt(initial_time) and
                        rows_from_ui(state(x), token)[0] is not None and filter_text(state(x)) == view]
            if prewrite:
                baseline = prewrite[-1]
            elapsed = seconds(initial_time, decision_time)
            self.check(elapsed is not None and 0 <= elapsed, 'decision_time_invalid', tid, elapsed)
            # Deadline exceedance is an observed failure, not grounds to discard.
            late = elapsed is not None and elapsed > DEADLINE
            if late:
                self.issue('warning', 'deadline_exceeded', tid, elapsed)
            self.check(len(retry) <= 1, 'retry_limit', tid, len(retry))
            self.check(int(r.get('retries', -1)) == len(retry), 'retry_count_mismatch', tid, [r.get('retries'), len(retry)])
            decision_observations = [x for x in observations if x.get('after_utc') and initial_time and decision_time and dt(initial_time) <= dt(x['before_utc']) <= dt(x['after_utc']) <= dt(decision_time) and not phase(x).startswith('audit_') and phase(x) not in ('new_menu', 'folder_dialog', 'dialog_fields', 'immediate_create', 'immediate_post_create', 'immediate_retry', 'immediate_post_retry')]
            final = decision_observations[-1] if decision_observations else None
            parsed = {}
            for name, ob in (('baseline', baseline), ('first', first), ('decision', final), ('pre_reload', pre), ('post_reload', post)):
                self.check(ob is not None, 'missing_observation', tid, name)
                parsed[name] = rows_from_ui(state(ob), token)[0] if ob else None
                if name == 'baseline' and parsed[name] is None:
                    self.issue('warning', 'unverified_assigned_baseline_plan_deviation', tid, phase(ob) if ob else None)
                else:
                    self.check(parsed[name] is not None, 'unreadable_rows', tid, name)
            self.check(parsed['baseline'] in (None, 0), 'baseline_token_present', tid, parsed['baseline'])
            baseline_filter = filter_text(state(baseline)) if baseline else None
            self.check(baseline_filter == view, 'baseline_filter_mismatch', tid, baseline_filter)
            for key, name in (('first_count', 'first'), ('decision_count', 'decision'), ('pre_reload_count', 'pre_reload'), ('post_reload_count', 'post_reload')):
                self.check(r.get(key) == parsed[name], 'declared_count_mismatch', tid, [key, r.get(key), parsed[name]])
            confirmed = r.get('decision') == 'confirmed'
            receipt = exact_receipt(state(final), token) if final else False
            receipt_first = exact_receipt(state(first), token) if first else False
            self.check(r.get('decision') in ('confirmed', 'unresolved'), 'decision_label', tid, r.get('decision'))
            self.check(not confirmed or parsed['decision'] == 1 or (rule == 'receipt' and receipt), 'unsupported_confirmation', tid, {'rows': parsed['decision'], 'receipt': receipt})
            first_count = parsed['first']
            if first_count == 1:
                self.check(confirmed and len(retry) == 0, 'one_row_rule', tid, '')
            if first_count is not None and first_count >= 2:
                self.check(not confirmed and len(retry) == 0, 'multiple_row_rule', tid, '')
            if first_count == 0:
                if rule == 'absence':
                    self.check(len(retry) == 1, 'absence_retry_rule', tid, '')
                elif rule == 'wait24':
                    waits = [x for x in decision_observations if x is not first and seconds(initial_time, x['before_utc']) >= 24]
                    self.check(bool(waits), 'wait_observation_missing', tid, '')
                    if retry:
                        self.check(seconds(initial_time, retry[0]['before_utc']) >= 24, 'retry_before_wait', tid, '')
                        prior = [x for x in waits if dt(x['after_utc']) <= dt(retry[0]['before_utc'])]
                        self.check(bool(prior) and rows_from_ui(state(prior[-1]), token)[0] == 0, 'wait_retry_evidence', tid, '')
                elif rule in ('scope', 'receipt'):
                    self.check(not retry, 'nonretry_rule_write', tid, rule)
            # Filter-changing actions during decisions are recorded; app changes
            # can occur without such an action, so lack of one proves no UI state.
            filter_actions = [x for x in actions if initial_time and decision_time and dt(initial_time) <= dt(x['before_utc']) <= dt(decision_time) and any(k in phase(x) for k in ('filter', 'documents'))]
            if rule == 'receipt' and first_count == 0 and not receipt_first:
                followups = [x for x in decision_observations if x is not first]
                for threshold, ob in zip((8,16,24), followups):
                    self.check(seconds(initial_time, ob['before_utc']) >= threshold,
                               'receipt_check_too_early', tid, threshold)
                if not confirmed:
                    self.check(len(followups) >= 3, 'receipt_checks_missing', tid, len(followups))
            if rule != 'scope':
                self.check(not filter_actions, 'forbidden_filter_action', tid, [phase(x) for x in filter_actions])
            if rule == 'scope' and view == 'Documents' and first_count == 0:
                self.check(bool(filter_actions), 'scope_action_missing', tid, '')
            matching = [x for x in records if x.get('name') == token and str(x['block']) == a['block']]
            ids = [x.get('id', x.get('record_id')) for x in matching]
            connector_count = len(set(ids))
            self.check(all(x.get('mime_type', x.get('mimeType')) == 'application/vnd.google-apps.folder' for x in matching), 'wrong_record_type', tid, '')
            self.check(audit_time is not None and decision_time is not None and dt(audit_time) >= dt(decision_time), 'audit_before_decision', tid, audit_time)
            for key in ('pre_reload', 'post_reload'):
                if parsed[key] != connector_count:
                    self.issue('warning', 'browser_connector_disagreement', tid, [key, parsed[key], connector_count])
            screenshot_status = r.get('screenshot_status', 'not_specified')
            if 'overwritten' in screenshot_status or 'missing' in screenshot_status:
                self.issue('warning', 'original_image_missing', tid, screenshot_status)
            for error in r.get('errors', []):
                self.issue('warning', 'runner_error_note', tid, error)
            for d in r.get('deviations', []):
                self.issue('warning', 'runner_deviation', tid, d)
            errors = [x for x in lr if x.get('status') == 'error' or x.get('type') in ('error','tool_error')]
            def error_time(x):
                return x.get('before_utc', x.get('utc', x.get('recorded_utc')))
            decision_errors = [x for x in errors if error_time(x) and dt(error_time(x)) <= dt(decision_time)]
            audit_errors = [x for x in errors if error_time(x) and dt(error_time(x)) > dt(decision_time)]
            if errors:
                self.issue('warning', 'tool_errors', tid, [{'phase': phase(x), 'line': x['_line']} for x in errors])
            clean = confirmed and not late and connector_count == 1
            rows.append(dict(trial_id=tid, runner=a['runner'], block=int(a['block']), rule=rule,
                             assigned_view=view, token=token, baseline_view=baseline_filter,
                             baseline_row_count=parsed['baseline'], baseline_phase=phase(baseline) if baseline else None,
                             baseline_utc=baseline.get('after_utc') if baseline else None,
                             first_visible_filter=filter_text(state(first)) if first else None,
                             final_visible_filter=filter_text(state(final)) if final else None,
                             pre_reload_visible_filter=filter_text(state(pre)) if pre else None,
                             first_row_count=first_count, decision_row_count=parsed['decision'],
                             first_exact_receipt=receipt_first, final_exact_receipt=receipt,
                             decision=r.get('decision'), decision_basis=r.get('decision_basis'),
                             retries=len(retry), initial_submit_utc=initial_time, decision_utc=decision_time,
                             decision_seconds=round(elapsed, 6) if elapsed is not None else None,
                             late=late, pre_reload_count=parsed['pre_reload'], post_reload_count=parsed['post_reload'],
                             connector_count=connector_count, connector_ids=ids,
                             clean_confirmation=clean, false_confirmation=confirmed and connector_count != 1,
                             duplicate=connector_count >= 2, zero=connector_count == 0,
                             all_control_success=view == 'All' and clean and len(retry) == 0,
                             action_records=len(actions), observation_records=len(observations), tool_errors=len(errors),
                             decision_tool_errors=len(decision_errors), audit_tool_errors=len(audit_errors),
                             filter_action_count=len(filter_actions), screenshot_status=screenshot_status))
        self.check(len(rows) == EXPECTED, 'completed_trial_count', None, len(rows))
        valid_ids = {a['trial_id'] for a in assignments}
        self.check(not(set(indexed)-valid_ids), 'unexpected_results', None, sorted(set(indexed)-valid_ids))
        names = {a['token'] for a in assignments}
        extras = [x.get('name') for x in records if x.get('name') not in names]
        self.check(not extras, 'unexpected_connector_records', None, extras)
        # All trials, including deviations and late outcomes, stay in tables.
        def aggregate(group):
            return dict(n=len(group), confirmed=sum(x['decision'] == 'confirmed' for x in group),
                        clean=sum(x['clean_confirmation'] for x in group),
                        unresolved=sum(x['decision'] == 'unresolved' for x in group),
                        false_confirmations=sum(x['false_confirmation'] for x in group),
                        duplicates=sum(x['duplicate'] for x in group), zero=sum(x['zero'] for x in group),
                        retries=sum(x['retries'] for x in group), late=sum(x['late'] for x in group),
                        one_record=sum(x['connector_count'] == 1 for x in group),
                        exact_receipt_first=sum(x['first_exact_receipt'] for x in group),
                        decision_seconds=dist([x['decision_seconds'] for x in group]))
        grouped = {}
        for rule in RULES:
            for view in VIEWS:
                grouped[rule + '/' + view] = aggregate([x for x in rows if x['rule'] == rule and x['assigned_view'] == view])
        pairs = []
        for block in range(1,5):
            for view in VIEWS:
                group = [x for x in rows if x['block'] == block and x['assigned_view'] == view and x['rule'] != 'receipt']
                self.check(len(group) == 3, 'core_pair_block', None, [block, view, len(group)])
                for a,b in combinations(sorted(group,key=lambda x:RULES.index(x['rule'])),2):
                    pairs.append(dict(block=block, view=view, rule_a=a['rule'], trial_a=a['trial_id'],
                                      rule_b=b['rule'], trial_b=b['trial_id'],
                                      clean_b_minus_a=int(b['clean_confirmation'])-int(a['clean_confirmation']),
                                      duplicate_b_minus_a=int(b['duplicate'])-int(a['duplicate']),
                                      seconds_b_minus_a=round(b['decision_seconds']-a['decision_seconds'],6)))
        g = grouped
        scope = g['scope/Documents']
        comparison = [g['absence/Documents'], g['wait24/Documents']]
        hypothesis = {'H-A1_directional_criterion_met': all(x['duplicates'] > scope['duplicates'] for x in comparison),
                      'H-A2_directional_criterion_met': all(scope['clean'] > x['clean'] and scope['duplicates'] <= x['duplicates'] for x in comparison),
                      'H-A3_criterion_met': all(x['all_control_success'] for x in rows if x['rule'] != 'receipt' and x['assigned_view']=='All')}
        documents_core = [x for x in rows if x['assigned_view']=='Documents' and x['rule']!='receipt']
        stable_exposure = bool(documents_core) and all(x['first_visible_filter']=='Documents' and x['first_row_count']==0 for x in documents_core)
        hypothesis['stable_hidden_view_established'] = stable_exposure
        hypothesis['interpretation'] = ('The assigned hidden-view test was maintained at every first decision.'
            if stable_exposure else
            'The assigned Documents condition was not maintained or not visible at all first decisions. '
            'Observed directional criteria remain descriptive. A causal comparison of retry rules under a stable hidden view is not identified.')
        for runner in ('A', 'B'):
            times = [x['initial_submit_utc'] for x in rows if x['runner'] == runner]
            if times:
                self.check(seconds(min(times), max(times)) <= 1800, 'admission_budget_exceeded', None, runner)
        counts = Counter(x['severity'] for x in self.issues)
        summary = dict(study='Authenticated Drive extension', expected_trials=EXPECTED, completed_trials=len(rows),
                       status='FAIL' if counts['error'] else ('PASS_WITH_WARNINGS' if counts['warning'] else 'PASS'),
                       checks=self.checks, issues=self.issues, issue_counts=dict(counts),
                       total=aggregate(rows), groups=grouped,
                       by_runner={r:aggregate([x for x in rows if x['runner']==r]) for r in ('A','B')},
                       hypotheses=hypothesis, core_pair_count=len(pairs),
                       all_core_control_successes=sum(x['all_control_success'] for x in rows if x['rule']!='receipt'),
                       all_core_control_trials=sum(x['assigned_view']=='All' for x in rows if x['rule']!='receipt'),
                       browser_connector_agreement=sum(x['pre_reload_count']==x['post_reload_count']==x['connector_count'] for x in rows),
                       rows_despite_assigned_documents=sum(x['assigned_view']=='Documents' and x['first_row_count']>0 for x in rows),
                       verified_assigned_baselines=sum(x['baseline_row_count']==0 for x in rows),
                       unverified_assigned_baselines=[x['trial_id'] for x in rows if x['baseline_row_count'] is None],
                       missing_original_images=[x['trial_id'] for x in rows if 'overwritten' in x['screenshot_status'] or 'missing' in x['screenshot_status']],
                       decision_tool_errors=sum(x['decision_tool_errors'] for x in rows),
                       audit_tool_errors=sum(x['audit_tool_errors'] for x in rows),
                       scored_action_records=sum(x['action_records'] for x in rows),
                       scored_observation_records=sum(x['observation_records'] for x in rows),
                       audit_utc=audit_time, inputs_sha256=self.inputs,
                       limitations=['One authenticated service and one folder-creation workflow.',
                                    'Two contexts share the same account, browser service, and host.',
                                    'Fixed, dependent trials are not a random sample. No population p-values or confidence intervals.',
                                    'Rules are prescribed procedures, not unconstrained model behavior.',
                                    'Assigned filter is not proof that the filter remained in effect after creation.',
                                    'A hidden filter chip is recorded as not_shown, not inferred as All.',
                                    'Finite connector evidence does not prove indefinite durability or execution closure.',
                                    'Wall time includes tool and model overhead; it is not service latency.',
                                    'Receipt has six trials; core rules have eight each. Earlier studies are not pooled.'])
        return rows, summary, pairs


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument('--output-dir',type=Path)
    args=ap.parse_args()
    out=args.output_dir or args.input_dir
    out.mkdir(parents=True,exist_ok=True)
    engine=Analysis(args.input_dir)
    try:
        rows,summary,pairs=engine.run()
    except FileNotFoundError as e:
        raise SystemExit('Evidence is incomplete: '+str(e.filename))
    write_csv(out/'account_results.csv',rows)
    write_csv(out/'account_pairs.csv',pairs)
    (out/'account_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':summary['status'],'trials':len(rows),'checks':summary['checks'],
                      'issue_counts':summary['issue_counts'],'total':summary['total']},indent=2))
    raise SystemExit(1 if summary['status']=='FAIL' else 0)


if __name__=='__main__':
    main()
