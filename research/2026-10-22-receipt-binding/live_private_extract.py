"""Independent audit of retained receipt records; public extraction. No account calls.

The original recorded decisions remain unchanged. This code does not execute the
runtime or send a second request. Native IDs are compared here and omitted from
public output. All original evidence file names and SHA-256 values are retained.
"""
import base64
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
from urllib.parse import urlparse, parse_qs

from live_receipt_analyze import analyze


def load(p):
    return json.loads(p.read_text())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ref(p):
    return {'file': p.name, 'sha256': digest(p)}


def canonical_hash(v):
    return hashlib.sha256(json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def seconds(t):
    d = datetime.fromisoformat(t.replace('Z', '+00:00'))
    assert d.utcoffset().total_seconds() == 0
    return d.timestamp()


def calendar_id(url):
    u = urlparse(url)
    token = parse_qs(u.query).get('eid', [None])[0]
    if token is None and '/eventedit/' in u.path:
        token = u.path.split('/eventedit/', 1)[1]
    assert token
    return base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode().split(' ')[0]


def content(record):
    assert not record['result'].get('isError', False)
    return record['result']['structuredContent']


def resource_checks(service, raw, fixture, value):
    checks = {'native_id_matches': raw.get('id') == fixture['id']}
    if service == 'drive':
        checks.update({'name_matches': raw.get('title') == fixture['args']['name'].removesuffix('BASE') + value,
                       'url_id_matches': urlparse(raw['url']).path.split('/folders/')[-1] == fixture['id'],
                       'folder_type': raw.get('mime_type') == 'application/vnd.google-apps.folder' and raw.get('file_or_folder') == 'folder',
                       'parent_matches': raw.get('parent_ids') == [fixture['args']['parent_folder']],
                       'not_shared': raw.get('shared') is False,
                       'one_owner_permission': isinstance(raw.get('permissions'), list) and len(raw['permissions']) == 1 and raw['permissions'][0].get('role') == 'owner' and raw['permissions'][0].get('type') == 'user'})
    else:
        attendees, org = raw.get('attendees'), raw.get('organizer', {})
        checks.update({'url_id_matches': calendar_id(raw['url']) == fixture['id'],
                       'title_matches': raw.get('summary') == fixture['args']['title'],
                       'description_matches_after_CRLF_trim': isinstance(raw.get('description'), str) and raw['description'].rstrip('\r\n') == value,
                       'empty_location': raw.get('location') in (None, ''),
                       'status_confirmed': raw.get('status') == 'confirmed',
                       'start_date': raw.get('start') == '2026-10-01T00:00:00',
                       'exclusive_end_date': raw.get('end') == '2026-10-02T00:00:00',
                       'free': raw.get('transparency') == 'transparent', 'private': raw.get('visibility') == 'private',
                       'organizer_self': org.get('is_self') is True,
                       'self_attendee_only': isinstance(attendees, list) and len(attendees) == 1 and attendees[0].get('is_self') is True and attendees[0].get('email') == org.get('email') and attendees[0].get('response_status') == 'accepted',
                       'no_reminders': raw.get('reminders') == {'use_default': False, 'overrides': []},
                       'nonrecurring': all(raw.get(k) is None for k in ('recurrence', 'recurring_event_id', 'original_start_time')),
                       'no_hangout_link': raw.get('hangout_link') is None, 'no_attachments': raw.get('attachments') is None,
                       'default_event_type': raw.get('event_type') == 'default'})
    return checks


def private_strings(manifest):
    found = set()
    def visit(x, key=''):
        if isinstance(x, dict):
            for k, v in x.items():
                visit(v, k)
        elif isinstance(x, list):
            for v in x:
                visit(v, key)
        elif isinstance(x, str) and len(x) > 5 and (key in ('id', 'parent_folder', 'email', 'emailAddress', 'url', 'display_url') or key == 'parent_ids'):
            found.add(x)
    visit(manifest)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=Path(__file__).resolve().parent,
                        help='Private run folder, with private/ and frozen controller files')
    args = parser.parse_args()
    base = args.base.resolve()
    private, out = base / 'private', base / 'receipt'
    out.mkdir(exist_ok=True)
    manifest = load(private / 'manifest.json')
    receipt_ids = [v['id'] for k, v in manifest.items() if ':RECEIPT-' in k]
    assert len(receipt_ids) == len(set(receipt_ids)) == 16
    baselines = {(r['value']['service'], r['value']['alias']): r['value'] for r in load(private / 'baselines.json') if r['status'] == 'fulfilled'}
    freeze = load(base / 'runtime_intent_freeze.json')
    assert all(digest(base / name) == sha for name, sha in freeze['sha256'].items())
    rows = []
    for service in ('drive', 'calendar'):
        for policy in ('K', 'B'):
            for pair in ('EXACT', 'PAYLOAD', 'TARGET'):
                path = private / f'intent-receipt-{service}-{policy}-{pair}.json'
                raw = load(path)
                alias = f'RECEIPT-{policy}-{pair}-A'
                fixture = manifest[service + ':' + alias]
                ui_path = private / f'intent-ui-{service}-{alias}.json'
                ui = load(ui_path)
                dispatch_path = private / f'dispatch-first-{service}-{alias}.json'
                dispatch = load(dispatch_path)
                sent_path = private / f'ui-first-{service}-{alias}-sent.json'
                sent = load(sent_path)
                source_path = private / ui['source_file']
                source = load(source_path)
                first_path = private / f'intent-first-{service}-{alias}.json'
                first = load(first_path)
                after_path = private / f'receipt-after-{service}-{alias}.json'
                after = load(after_path)
                baseline = baselines[(service, alias)]
                baseline_raw, first_raw, after_raw = content(baseline), content(first), content(after)
                stored, second = raw['stored_envelope'], raw['second_envelope']
                evidence = stored['evidence']
                action_evidence = evidence['browser_action_evidence']
                expected_target = alias[:-1] + 'B' if pair == 'TARGET' else alias
                requested = 'PAYLOAD-B' if pair == 'PAYLOAD' else 'PAYLOAD-A'
                fields = ['service', 'account_alias', 'operation_id', 'target', 'action', 'payload']
                mismatched = [k for k in fields if stored[k] != second[k]]
                expected_mismatched = [] if pair == 'EXACT' else ['payload' if pair == 'PAYLOAD' else 'target']
                checks = {
                    'case_labels': (raw['service'], raw['policy'], raw['pair'], raw['first_target_alias'], raw['second_target_alias']) == (service, policy, pair, alias, expected_target),
                    'first_target_native_id': stored['target'] == fixture['id'],
                    'second_target_native_id': second['target'] == manifest[service + ':' + expected_target]['id'],
                    'request_fields': stored['service'] == second['service'] == service and stored['account_alias'] == second['account_alias'] == 'connected-account-1' and stored['operation_id'] == second['operation_id'] == f'FIVE-LIVE-20261022-Q7K:{service}:RECEIPT-{policy}-{pair}' and stored['action'] == second['action'] == ('set_folder_name_suffix' if service == 'drive' else 'set_event_description') and stored['payload'] == {'suffix': 'PAYLOAD-A'} and second['payload'] == {'suffix': requested},
                    'changed_request_fields': mismatched == expected_mismatched,
                    'envelope_hashes': canonical_hash(stored) == raw['stored_envelope_sha256'] and canonical_hash(second) == raw['second_envelope_sha256'],
                    'runtime_hash': raw['helper_sha256'] == digest(base / 'runtime_intent.py'),
                    'rule_hash': raw['rule_sha256'] == digest(base / 'live_intent.py'),
                    'recorded_evidence_complete': raw['evidence_complete'] is True and raw['evidence_errors'] == [] and all(evidence[k] is True for k in ('evidence_complete', 'action_evidence_complete', 'saved_field_checks_complete')) and evidence['check_errors'] == [] and action_evidence['check_errors'] == [],
                    'first_read_reference': evidence['read_file'] == first_path.name and evidence['read_sha256'] == digest(first_path) and evidence['read_time_utc'] == first['time'],
                    'evidence_reference_hashes': all(ref(private / r['file']) == r for r in action_evidence['references'].values()),
                    'evidence_reference_mapping': action_evidence['references'] == {'before_ui': ref(ui_path), 'dispatch': ref(dispatch_path), 'raw_ui_source': ref(source_path), 'sent_ui': ref(sent_path)},
                    'before_UI_native_identity': ui['observed_id'] == fixture['id'] and ui['service'] == service and ui['alias'] == alias,
                    'dispatch_label': dispatch['label'] == f'first-{service}-{alias}' and dispatch['alias'] == alias,
                    'postclick_UI_has_state': isinstance(sent['state'], str) and len(sent['state']) > 0,
                    'one_dispatch_record': len(list(private.glob(f'dispatch-first-{service}-{alias}.json'))) == 1,
                    'no_second_dispatch': not list(private.glob(f'dispatch-second-{service}-{alias}*')) and raw['decision']['dispatch'] is False and raw['second_browser_action_time'] is None and raw['account_mutations_by_helper'] == 0,
                    'stored_evidence_preserved_in_second': stored['evidence'] == second['evidence'],
                    'source_before_UI': seconds(source['time']) <= seconds(ui['time']),
                    'freeze_before_action': seconds(freeze['frozen_at_utc']) < seconds(dispatch['time']),
                }
                if service == 'drive':
                    oldname, newname = fixture['args']['name'], fixture['args']['name'].removesuffix('BASE') + 'PAYLOAD-A'
                    checks.update({'source_native_identity': source['row']['id'] == fixture['id'],
                                   'source_baseline_name': source['row']['text'].split('\n')[0] == oldname,
                                   'source_and_UI_filled_value': source['rename_input_value'] == ui['values']['rename_input_value'] == newname,
                                   'active_parent_observed': ui['values']['active_parent_id'] == fixture['args']['parent_folder'] and urlparse(ui['url']).path.split('/folders/')[-1] == fixture['args']['parent_folder'],
                                   'dispatch_fields': dispatch['action'] == 'rename' and dispatch['oldName'] == oldname and dispatch['newName'] == newname,
                                   'expected_second_fields': raw['expected_second_browser_fields'] == {'name': manifest[service + ':' + expected_target]['args']['name'].removesuffix('BASE') + requested}})
                    allowed = {'title', 'modified_time'}
                else:
                    before_path = private / f'ui-first-calendar-{alias}-before.json'
                    before = load(before_path)
                    checks.update({'observed_URL_native_identity': calendar_id(ui['url']) == fixture['id'] and calendar_id(dispatch['url']) == fixture['id'] and calendar_id(source['url']) == fixture['id'],
                                   'UI_description_and_flags': ui['values'] == {'description': 'PAYLOAD-A', 'all_day': True, 'availability': 'Free', 'visibility': 'Private'} and type(ui['values']['all_day']) is bool,
                                   'source_flags': all(x in source['state'] for x in ('Description: All day, Value: 1', 'Value: Free', 'Value: Private')),
                                   'source_title': fixture['args']['title'] in source['state'],
                                   'before_flags': all(x in before['state'] for x in ('Description: All day, Value: 1', 'Value: Free', 'Value: Private')) and fixture['args']['title'] in before['state'],
                                   'dispatch_fields': dispatch['field'] == 'description' and dispatch['from'] == 'BASE' and dispatch['to'] == 'PAYLOAD-A',
                                   'expected_second_fields': raw['expected_second_browser_fields'] == {'description': requested}})
                    allowed = {'description'}
                before_checks = resource_checks(service, baseline_raw, fixture, 'BASE')
                first_checks = resource_checks(service, first_raw, fixture, 'PAYLOAD-A')
                final_checks = resource_checks(service, after_raw, fixture, 'PAYLOAD-A')
                collateral = {k: baseline_raw.get(k) == first_raw.get(k) for k in set(baseline_raw) | set(first_raw) if k not in allowed}
                checks.update({'baseline_fields': all(before_checks.values()), 'first_fields': all(first_checks.values()), 'final_fields': all(final_checks.values()),
                               'collateral_fields_unchanged': all(collateral.values()), 'first_to_after_all_exposed_fields_equal': first_raw == after_raw})
                response = raw['events'][-1]
                checks['response_matches_record'] = response['event'] == 'receipt_response' and all(response[k] == raw['decision'][k] for k in ('status', 'reason', 'replay', 'dispatch', 'mismatched_fields'))
                chronology = [baseline['ended'], ui['time'], dispatch['time'], sent['time'], first['time'], raw['prepared_at_utc'], *[e['time_utc'] for e in raw['events']], after['time']]
                checks['chronology'] = all(seconds(a) <= seconds(b) for a, b in zip(chronology, chronology[1:]))
                checks['action_evidence_times_match'] = action_evidence['ui_observation_time_utc'] == ui['time'] and action_evidence['browser_dispatch_time_utc'] == dispatch['time'] and action_evidence['postclick_UI_time_utc'] == sent['time'] and action_evidence['first_read_time_utc'] == first['time']
                case_seconds = round(seconds(after['time']) - seconds(ui['time']), 3)
                checks['case_within_eight_minutes'] = case_seconds <= 480
                resources = {'A': {'baseline_checks': before_checks, 'first_checks': first_checks, 'final_checks': final_checks,
                                  'unchanged_collateral_fields': sorted(collateral), 'first_to_after_equal': first_raw == after_raw,
                                  'baseline_time': baseline['ended'], 'first_time': first['time'], 'final_time': after['time'],
                                  'evidence': [ref(private / 'baselines.json'), ref(first_path), ref(after_path)]}}
                final_values = {'A': 'PAYLOAD-A'}
                case_end = after['time']
                refs = [ref(path), ref(ui_path), ref(source_path), ref(dispatch_path), ref(sent_path)]
                if pair == 'TARGET':
                    b_alias = alias[:-1] + 'B'
                    b_fixture = manifest[service + ':' + b_alias]
                    b_base = baselines[(service, b_alias)]
                    b_first_path = private / f'intent-first-{service}-{b_alias}.json'
                    b_after_path = private / f'receipt-after-{service}-{b_alias}.json'
                    b_first, b_after = load(b_first_path), load(b_after_path)
                    br = [content(b_base), content(b_first), content(b_after)]
                    bc = [resource_checks(service, v, b_fixture, 'BASE') for v in br]
                    checks['B_fields_and_unchanged'] = all(all(x.values()) for x in bc) and br[0] == br[1] == br[2]
                    checks['B_chronology'] = seconds(b_base['ended']) <= seconds(b_first['time']) <= seconds(raw['prepared_at_utc']) <= seconds(b_after['time'])
                    resources['B'] = {'baseline_checks': bc[0], 'first_checks': bc[1], 'final_checks': bc[2], 'all_exposed_fields_unchanged': br[0] == br[1] == br[2],
                                      'baseline_time': b_base['ended'], 'first_time': b_first['time'], 'final_time': b_after['time'],
                                      'evidence': [ref(private / 'baselines.json'), ref(b_first_path), ref(b_after_path)]}
                    final_values['B'] = 'BASE'
                    case_end = max((case_end, b_after['time']), key=seconds)
                    case_seconds = round(seconds(case_end) - seconds(ui['time']), 3)
                    checks['case_within_eight_minutes'] = case_seconds <= 480
                assert all(checks.values()), (service, policy, pair, {k: v for k, v in checks.items() if not v})
                interrupted = service == 'drive' and policy == 'K' and pair == 'EXACT'
                if interrupted:
                    interruption = private / 'receipt-interruption-read.json'
                    assert first_path.read_bytes() == interruption.read_bytes()
                    refs.append(ref(interruption))
                rows.append({'case_id': f'{service}-{policy}-{pair}', 'service': service, 'policy': policy, 'pair': pair,
                             'initial_target': 'A', 'initial_value': 'PAYLOAD-A', 'requested_target': 'B' if pair == 'TARGET' else 'A',
                             'requested_value': requested, 'final_values': final_values, 'first_saves': 1, 'second_saves': 0,
                             'decision': raw['decision'], 'checks': checks, 'resource_checks': resources,
                             'original_envelope_hashes': {'stored': raw['stored_envelope_sha256'], 'second': raw['second_envelope_sha256']},
                             'timing_check_known': not interrupted, 'interrupted_reload': interrupted,
                             'times': {'before_UI': ui['time'], 'dispatch': dispatch['time'], 'postclick_UI': sent['time'], 'first_read': first['time'],
                                       'prepared': raw['prepared_at_utc'], 'response': response['time_utc'], 'after_read': after['time'], 'case_end': case_end, 'case_seconds': case_seconds,
                                       'baseline_to_before_UI_seconds': round(seconds(ui['time']) - seconds(baseline['ended']), 3),
                                       'postclick_to_first_read_seconds': round(seconds(first['time']) - seconds(sent['time']), 3)},
                             'evidence': refs})
    evidence = {'schema': 'live-receipt-public-v1', 'cases': rows,
                'scope': 'Real first browser saves; online local second-request decisions; independent connector saved-field audits.',
                'baseline_scope': 'One full connector setup batch, followed by fresh before-save browser identity and field checks. No immediate per-case full metadata baseline is claimed.',
                'interruption': 'drive-K-EXACT timed out on reload after dispatch and postclick evidence. The retained first-read file is a byte copy of receipt-interruption-read.json, not another observation. No first Save was repeated. The failed observation start time is not known; 30-second compliance is unknown.',
                'not_exposed': {'drive': ['trashed', 'version'], 'calendar': ['full conferenceData', 'provider etag/version', 'calendar container ID attestation in read_event output']},
                'hash_scope': 'Original envelopes and raw files were hashed privately before alias extraction. Public envelope hashes do not hash a public alias-substituted envelope.',
                'source_hashes': [ref(base / n) for n in ('plan.md', 'amendment-01.md', 'amendment-02.md', 'design-cancel-receipt.md', 'execution_freeze.json', 'live_intent.py', 'runtime_intent.py', 'runtime_intent_freeze.json', 'runtime_intent_review.md', 'browser_receipt_helpers.txt', 'receipt_browser_module.mjs')]}
    public = json.dumps(evidence, indent=2, sort_keys=True) + '\n'
    assert not [s for s in private_strings(manifest) if s in public], 'Private value retained'
    (out / 'live_evidence.json').write_text(public)
    (out / 'live_results.json').write_text(json.dumps(analyze(evidence), indent=2, sort_keys=True) + '\n')
    for n in ('live_receipt_analyze.py', 'live_intent.py', 'runtime_intent.py', 'runtime_intent_freeze.json', 'runtime_intent_review.md', 'runtime_intent_README.md', 'runtime_intent_checks.json', 'check_runtime_intent.py', 'browser_receipt_helpers.txt', 'receipt_browser_module.mjs'):
        shutil.copyfile(base / n, out / n)
    shutil.copyfile(Path(__file__), out / 'live_private_extract.py')
    (out / 'live_build.json').write_text(json.dumps({'kind': 'local_evidence_analysis', 'account_calls': 0,
        'builder_sha256': digest(Path(__file__)), 'evidence_sha256': digest(out / 'live_evidence.json'),
        'results_sha256': digest(out / 'live_results.json'), 'privacy_scan': 'pass'}, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'cases': len(rows), 'all_checks': 'pass', 'output': 'receipt/', 'false_success': analyze(evidence)['total_false_success']}))


if __name__ == '__main__':
    main()
