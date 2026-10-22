"""Separate raw-evidence audit. Does not call the study scorer or any account."""
import base64
from datetime import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs


HERE = Path(__file__).resolve().parent
PRIVATE = HERE.parent / 'private'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sec(t):
    value = datetime.fromisoformat(t.replace('Z', '+00:00'))
    assert value.utcoffset().total_seconds() == 0
    return value.timestamp()


def native_event_id(url):
    u = urlparse(url)
    token = parse_qs(u.query).get('eid', [None])[0]
    if token is None:
        token = u.path.split('/eventedit/')[1]
    return base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)).decode().split(' ')[0]


def audit():
    manifest = read(PRIVATE / 'manifest.json')
    base = {(r['value']['service'], r['value']['alias']): r['value'] for r in read(PRIVATE / 'baselines.json') if r['status'] == 'fulfilled'}
    trace = read(HERE / 'live_trace.json')
    public = {(r['service'], r['case']): r for r in trace['cases']}
    freeze = read(HERE / 'runtime_intent_freeze.json')
    plan = read(HERE / 'live_execution_freeze.json')
    assert sha(HERE / 'runtime_intent.py') == freeze['sha256']['runtime_intent.py']
    assert sha(HERE / 'live_intent.py') == plan['sha256']['live_intent.py']
    assert all(sha(PRIVATE / file) == digest for file, digest in trace['private_evidence_sha256'].items())
    rows = []
    for service in ('drive', 'calendar'):
        for case in ('C1', 'C2', 'C3', 'C4'):
            alias = 'CANCEL-' + case
            native = manifest[service + ':' + alias]
            old = base[(service, alias)]['result']['structuredContent']
            intent = read(PRIVATE / f'intent-cancel-{service}-{case}.json')
            saved = read(PRIVATE / f'cancel-after-{service}-{case}.json')
            now = saved['result']['structuredContent']
            assert not saved['result'].get('isError')
            assert old['id'] == now['id'] == native['id'] == intent['native_target']
            assert intent['helper_sha256'] == sha(HERE / 'runtime_intent.py')
            assert intent['rule_sha256'] == sha(HERE / 'live_intent.py')
            assert sec(plan['timestamp_utc']) < sec(intent['prepared_at_utc'])
            state = None
            checks = []
            times = [intent['prepared_at_utc']]
            events = intent['events']
            assert [e['sequence'] for e in events] == list(range(1, len(events) + 1))
            for e in events:
                times.append(e['time_utc'])
                if e['event'] == 'initial_state':
                    state = {'active': e['active'], 'generation': e['generation']}
                    assert state == {'active': True, 'generation': 0}
                elif e['event'] in ('initial_check', 'final_check'):
                    assert e['observed_state'] == state
                    allow = state['active'] and e['command_generation'] == state['generation']
                    assert allow == e['allow']
                    checks.append((e['event'], allow, state.copy()))
                elif e['event'] == 'cancel_acknowledged_locally':
                    assert e['retired_generation'] == state['generation'] == 0
                    state['active'] = False
                    assert state == e['state']
                elif e['event'] == 'restart':
                    assert state == {'active': False, 'generation': 0}
                    state = {'active': True, 'generation': 1}
                    assert e['state'] == state
                elif e['event'] == 'dispatch_decision':
                    assert checks and e['allow'] == checks[-1][1]
                    assert e['browser_action_performed'] is False
                    assert all(e[k] == intent['decision'][k] for k in ('allow', 'basis', 'dispatch_payload'))
                else:
                    raise AssertionError('Unexpected event')
            assert state == intent['state'] == {'active': True, 'generation': 1}
            assert all(sec(a) <= sec(b) for a, b in zip(times, times[1:]))
            expected = {'C1': 'OLD', 'C2': 'BASE', 'C3': 'OLD', 'C4': 'NEW'}[case]
            dispatch_path = PRIVATE / f'dispatch-cancel-{service}-{case}.json'
            count = int(dispatch_path.exists())
            assert count == int(intent['decision']['allow']) == int(case != 'C2')
            if count:
                d = read(dispatch_path)
                sent = read(PRIVATE / f'ui-cancel-{service}-{case}-sent.json')
                before = read(PRIVATE / f'ui-cancel-{service}-{case}-before.json')
                assert sec(times[-1]) < sec(before['time']) <= sec(d['time']) <= sec(sent['time']) <= sec(saved['time'])
                assert sec(freeze['frozen_at_utc']) < sec(d['time'])
                assert d['alias'] == alias
                if service == 'drive':
                    assert d['oldName'] == old['title'] and d['newName'] == now['title']
                else:
                    assert native_event_id(d['url']) == native['id']
                    assert d['from'] == 'BASE' and d['to'] == expected
            else:
                blocked = read(PRIVATE / f'ui-cancel-{service}-{case}-blocked-read.json')
                assert sec(times[-1]) < min(sec(blocked['time']), sec(saved['time']))
                assert now == old
            if service == 'drive':
                prefix = native['args']['name'].removesuffix('BASE')
                assert now['title'].startswith(prefix)
                observed = now['title'][len(prefix):]
                unchanged = set(now) - {'title', 'modified_time'}
                assert now['parent_ids'] == old['parent_ids'] == [native['args']['parent_folder']]
                assert now['file_or_folder'] == 'folder' and now['mime_type'] == 'application/vnd.google-apps.folder'
            else:
                observed = now['description'].rstrip('\r\n')
                unchanged = set(now) - {'description'}
                assert native_event_id(now['url']) == native['id']
                assert now['transparency'] == 'transparent' and now['visibility'] == 'private'
                assert now['start'] == '2026-10-01T00:00:00' and now['end'] == '2026-10-02T00:00:00'
            assert set(now) == set(old) and all(now[k] == old[k] for k in unchanged)
            assert observed == expected
            p = public[(service, case)]
            assert p['events'] == events and p['decision'] == intent['decision']
            assert p['observed_final_field'] == observed and p['logged_browser_mutations'] == count
            assert p['different_connector_fields'] == sorted(k for k in now if now[k] != old[k])
            assert p['native_target_matches'] and p['collateral_fields_equal']
            assert 0 < p['prepare_to_last_observation_seconds'] <= 480
            rows.append({'case_id': service + '-' + case, 'field': observed, 'logged_saves': count,
                         'helper_freeze_precedes_preparation': sec(freeze['frozen_at_utc']) < sec(intent['prepared_at_utc']),
                         'raw_and_public_agree': True, 'native_ID_and_collateral_checks': True})
    assert len(rows) == 8 and len(list(PRIVATE.glob('dispatch-cancel-*.json'))) == 6
    result = {'audit': 'separate raw-evidence audit; no account calls or study scorer imported',
              'cases': rows, 'old_saved': sum(r['field'] == 'OLD' for r in rows),
              'baseline_preserved': sum(r['field'] == 'BASE' for r in rows), 'new_saved': sum(r['field'] == 'NEW' for r in rows),
              'logged_saves': sum(r['logged_saves'] for r in rows),
              'source_hashes': {n: sha(HERE / n) for n in ('live_trace.json', 'live_analysis.py', 'build_live_trace.py', 'report_extension.md')},
              'audit_sha256': sha(Path(__file__))}
    (HERE / 'separate_audit_results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('cases', 'source_hashes')}))


if __name__ == '__main__':
    audit()
