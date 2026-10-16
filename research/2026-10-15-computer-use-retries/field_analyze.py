"""Derive field-study results from saved UI and connector evidence, offline."""
import argparse, base64, csv, datetime as dt, hashlib, json, re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import fieldcheck as fc

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def when(r, end=False):
    keys = ('end_utc', 'ended_at_utc', 'at_utc', 'start_utc') if end else ('start_utc', 'started_at_utc', 'at_utc', 'end_utc')
    s = next((r[k] for k in keys if r.get(k)), None)
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None

def kind(r):
    return r.get('kind', r.get('type'))

def identity(value):
    if not isinstance(value, str) or not value:
        return None
    if re.fullmatch('record-[0-9a-f]{20}', value):
        return value
    if '/eventedit/' in value:
        enc = value.split('/eventedit/', 1)[1].split('?', 1)[0]
        if enc.startswith('record-'):
            return enc
        try:
            return base64.urlsafe_b64decode(enc + '=' * (-len(enc) % 4)).decode().split(' ', 1)[0]
        except (ValueError, UnicodeDecodeError):
            return None
    if '/p/' in value:
        part = value.split('/p/', 1)[1].split('?', 1)[0]
        m = re.findall('record-[0-9a-f]{20}|[0-9a-f]{32}', part)
        return m[-1] if m else None
    if re.fullmatch('[0-9a-f-]{32,36}', value):
        return value.replace('-', '')
    return value if re.fullmatch('[A-Za-z0-9_-]{10,80}', value) else None

def state_block(s, label):
    lines = s.splitlines()
    start = None
    indent = None
    for i, l in enumerate(lines):
        if re.search('- ' + re.escape(label) + '(?:\\s*\\[[^\\]]+\\])?:', l):
            start = i
            indent = len(l) - len(l.lstrip())
            break
    if start is None:
        return ''
    stop = next((i for i in range(start + 1, len(lines)) if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent), len(lines))
    return '\n'.join(lines[start:stop])

def one(pattern, s):
    m = re.search(pattern, s, re.M)
    return m.group(1) if m else None

def cal_ui(s, dom):
    u = {}
    b = state_block(s, 'textbox "Title"')
    title = one('^\\s+- text: (.*)$', b)
    if title is not None:
        u['title'] = title
    for key, label in [('start_date', 'Start date'), ('end_date', 'End date')]:
        v = one('- textbox "' + label + '"(?: \\[[^\\]]+\\])?: ([^\\n]+)', s)
        if v is not None:
            try:
                v = dt.datetime.strptime(v, '%b %d, %Y').date().isoformat()
            except ValueError:
                pass
            u[key] = v
    m = re.search('- checkbox "All day"([^\\n]*)', s)
    if m:
        u['all_day'] = '[checked]' in m.group(1)
    for key, label in [('availability', 'Show as'), ('visibility', 'Visibility'), ('recurrence', 'Recurrence')]:
        b = state_block(s, 'combobox "' + label + '"')
        m = re.search('- generic(?:: ([^\\n]+)| "([^\\n"]+)")', b)
        if m:
            u[key] = m.group(1) or m.group(2)
    b = state_block(s, 'tabpanel "Guests"')
    if re.search('- combobox "Guests"\\n\\s+- group "Guest permissions":', b):
        u['guests'] = []
    if re.search('^\\s+- combobox "Add location"\\s*$', s, re.M):
        u['location'] = ''
    if '- button "Add Google Meet video conferencing":' in s:
        u['conference'] = False
    if re.search('- list "Notifications"\\n\\s+- button "Add notification":', s):
        u['reminders'] = []
    v = dom.get('value', {})
    if v.get('tag') == 'DIV' and v.get('role') == 'textbox' and (v.get('contenteditable') == 'true') and isinstance(v.get('innerText'), str):
        u['description'] = v['innerText']
    return u

def notion_ui(s, dom):
    u = {}
    if isinstance(dom.get('raw_title'), str) and 'button ' + json.dumps(dom['raw_title']) in state_block(s, 'banner'):
        u['title'] = dom['raw_title']
    b = state_block(s, 'row "Marker"')
    v = one('^\\s+- button "([^\\n"]*)"', b)
    if v is not None:
        u['marker'] = '' if v == 'Empty' else v
    b = state_block(s, 'row "Verified"')
    m = re.search('- checkbox([^\\n]*)', b)
    if m:
        u['verified'] = '[checked]' in m.group(1)
    if 'continue with an empty page' in s:
        u['body_empty'] = True
    return u

def notion_titles(s):
    values = re.findall('^  - checkbox[^\\n]*\\n  - button "(?:Open in side peek )?([^\\n"]+)"', s, re.M)
    return values[1:] if values and values[0] == 'Name' else []

def notion_count(s):
    if not notion_ready(s):
        return None
    return max(0, len(re.findall('^  - checkbox(?: \\[[^\\]]+\\])?$', s, re.M)) - 1)

def notion_ready(s):
    header = one('(^  - checkbox[^\\n]*)', s)
    required = ['tab "Table" [selected]', 'button "Name"', 'button "Marker"', 'button "Verified"', 'button "Filter"', 'button "New"', 'button "New page"']
    return bool(header) and all((x in s for x in required)) and ('progressbar' not in s) and ('button "New" [disabled]' not in s)

def cal_count(s):
    m = re.search('heading "Search results\\. (No events found|([0-9]+) events? found)\\.', s)
    return (int(m.group(2)) if m.group(2) else 0) if m and 'progressbar' not in s and ('Searching' not in s) else None

class Data:

    def __init__(self, p, group):
        self.group = group
        self.path = p / ('field_' + group + '_actions.jsonl')
        self.rows = [json.loads(l) for l in self.path.read_text().splitlines()]
        self.by = {r['record_id']: r for r in self.rows}
        if len(self.by) != len(self.rows):
            raise ValueError('duplicate record IDs')
        self.files = json.loads((p / ('field_' + group + '_records.json')).read_text())
        self.issues = []

    def ref(self, k):
        if k is None:
            return {}
        if k not in self.by:
            raise ValueError('missing source ' + str(k))
        return self.by[k]

    def file(self, k):
        if k not in self.files:
            raise ValueError('missing member ' + k)
        return self.files[k]

    def packet(self, trial):
        vals = [v for k, v in self.files.items() if isinstance(v, dict) and v.get('trial_id') == trial and ('checkpoints' in v) and ('final_decision_record_id' in v)]
        if len(vals) != 1:
            raise ValueError('Expected one packet for ' + trial + '; found ' + str(len(vals)))
        return vals[0]

def identity_witness(data, record, site):
    value = identity(record.get('href') or record.get('url') or record.get('native_id'))
    source = data.ref(record.get('source_state_id', record.get('source_state')))
    direct = value is not None and (identity(source.get('url')) == value or (record.get('href') and record['href'] in source.get('state', '')))
    copied = False
    if site == 'Notion' and record.get('copy_action_id'):
        action = data.ref(record['copy_action_id'])
        before = data.ref(action.get('before'))
        copied = bool(value and kind(action) == 'action' and (not action.get('error')) and ('Copy link' in before.get('state', '')) and ('1 selected' in before.get('state', '')) and ('Copied page link to clipboard' in source.get('state', '')) and (when(action, True) <= when(source) <= when(record)))
    direct_url = site == 'Calendar' and value is not None and ('/eventedit/' in record.get('url', ''))
    return dict(value=value, valid=bool(direct or copied or direct_url), direct_source=bool(direct), copied_source=copied, source_id=source.get('record_id'), record_id=record.get('record_id'))

def ckpt(data, packet, phase, latest, expected):
    cp = packet['checkpoints'][phase]
    native = data.ref(cp.get('native_state_id'))
    dom = data.ref(cp.get('native_value_read_id'))
    covered = data.ref(cp.get('covered_state_id'))
    s = native.get('state', '')
    cs = covered.get('state', '')
    token = expected['token']
    site = expected['service']
    first = identity(packet.get('first_native_id'))
    current = identity(native.get('url'))

    def fresh(r):
        return bool(when(r) and latest and (when(r) > latest))
    witnesses = [identity_witness(data, r, site) for r in data.rows if r.get('trial_id') == expected['trial_id'] and kind(r) == 'native_identity' and (when(r) <= when(data.ref(cp.get('field_check_record_id'))))]
    first_witness = next((w for w in witnesses if w['valid']), None)
    if first_witness is None or first_witness['value'] != first:
        first = None
    ids = []
    id_witness = []
    for rid in cp.get('covered_identity_record_ids', []):
        r = data.ref(rid)
        w = identity_witness(data, r, site)
        v = w['value']
        id_witness.append(w)
        if w['valid']:
            ids.append(v)
    count = cal_count(cs) if site == 'Calendar' else notion_count(cs)
    visible_rows = count
    row_identity_record = None
    row_identity_valid = True
    if site == 'Calendar' and count is not None and (count > 1):
        rowref = cp.get('covered_row_identity_read_id') or next((data.ref(k).get('row_identity_source') for k in cp.get('covered_identity_record_ids', []) if data.ref(k).get('row_identity_source')), None)
        row_identity_record = data.ref(rowref)
        rr = row_identity_record
        rawrows = rr.get('rows', [])
        rowids = [identity('/eventedit/' + r.get('event_id_attribute', '')) for r in rawrows]
        row_identity_valid = bool(rawrows) and len(rawrows) == count and all(rowids) and (rr.get('source_state', rr.get('source_state_id')) == cp['covered_state_id']) and fresh(rr) and all((r.get('label') in cs and token in r.get('text', '') for r in rawrows))
        if row_identity_valid:
            distinct = list(dict.fromkeys(rowids))
            row_identity_valid = set(ids).issubset(set(distinct)) and bool(ids)
            ids = distinct
            count = len(distinct)
    values = cal_ui(s, dom) if site == 'Calendar' else notion_ui(s, dom)
    fields = fc.calendar_fields(token, values, {}) if site == 'Calendar' else fc.notion_fields(token, values)
    service_id = None
    service_ready = False
    service_fresh = False
    service_count = None
    service_files = []
    event = {}
    if site == 'Calendar':
        named = [(n, data.file(n)) for n in cp.get('connector_files', [])]
        searches = [(n, v) for n, v in named if isinstance(v.get('result', {}).get('structuredContent'), dict) and 'events' in v['result']['structuredContent']]
        reads = [(n, v) for n, v in named if isinstance(v.get('result', {}).get('structuredContent'), dict) and 'id' in v['result']['structuredContent']]
        if len(searches) == 1 and len(reads) == 1:
            sn, search = searches[0]
            rn, read = reads[0]
            sr = search['result']
            rr = read['result']
            body = sr['structuredContent']
            event = rr['structuredContent']
            service_id = event.get('id')
            service_count = len(body.get('events', []))
            service_files = [sn, rn]
            service_ids = [x['id'] for x in body.get('events', [])]
            args = search.get('args', {})
            service_ready = sr.get('isError') is False and rr.get('isError') is False and (body.get('next_page_token', 'missing') is None) and (args.get('calendar_id') == 'primary') and (args.get('query') == token) and (args.get('time_min') == '2026-10-01T00:00:00-04:00') and (args.get('time_max') == '2026-11-01T00:00:00-04:00') and (args.get('timezone_str') == 'America/Toronto') and (args.get('max_results') == 100)
            service_fresh = fresh(search) and fresh(read)
            ids = list(dict.fromkeys(ids))
            native_ids = list(ids)
            ids = service_ids
            if count != service_count or set(native_ids) != set(ids):
                service_ready = False
        fields = fc.calendar_fields(token, values, event)
        qs = parse_qs(urlparse(covered.get('url', '')).query)
        scope = qs.get('q') == [token] and qs.get('start') == ['20261001'] and (qs.get('end') == ['20261031']) and row_identity_valid
        native_ready = all((x in s for x in ['heading "Event edit page"', 'textbox "Title"', 'textbox "Start date"', 'textbox "End date"', 'checkbox "All day"', 'textbox "Description"'])) and 'progressbar' not in s and ('- dialog' not in s)
        pending = False if native_ready and dom.get('source_state', dom.get('source_state_id')) == cp.get('native_state_id') else True
    else:
        ids = list(dict.fromkeys(ids))
        scope = notion_ready(cs) and 'FIELD-CHECK-20261015' in cs
        native_ready = all((x in s for x in ['table "Page properties"', 'row "Marker"', 'row "Verified"', token])) and 'progressbar' not in s and ('Writing' not in state_block(s, 'textbox'))
        dialogs = re.findall('^- dialog(?: "([^"]+)")?', s, re.M)
        native_ready = native_ready and all((x == 'Turn on Writing Replay' for x in dialogs))
        pending = False if native_ready and dom.get('source_state_id') == cp.get('native_state_id') and ('textbox' not in state_block(s, 'row "Marker"')) and ('textbox' not in state_block(s, 'row "Verified"')) and (dom.get('raw_checkbox', {}).get('disabled') is False) else True
        if count is not None and count != len(ids):
            scope = False
        if 'raw_checkbox' in dom and dom['raw_checkbox'].get('checked') != values.get('verified'):
            native_ready = False
        if 'raw_marker_button' in dom and ('' if dom['raw_marker_button'] == 'Empty' else dom['raw_marker_button']) != values.get('marker'):
            native_ready = False
    facts = dict(first_id=first, ui_id=current, service_id=service_id, operation_ids=ids, native_ready=native_ready, native_fresh=fresh(native) and fresh(dom) and (when(native, True) <= when(dom)), service_ready=service_ready, service_fresh=service_fresh, coverage_ready=count is not None, coverage_fresh=fresh(covered), scope_covered=scope, edit_pending=pending, needs_service=site == 'Calendar')
    result = fc.check_record(fields, **facts)
    titles = notion_titles(cs) if site == 'Notion' else []
    title = values.get('title') if site == 'Calendar' else titles[0] if count == 1 and len(titles) == 1 else None
    baseline = fc.baseline_title_count(title, token, ids, ready=count is not None, fresh=fresh(covered), scope_covered=scope)
    online = data.ref(cp.get('field_check_record_id'))
    observed_online = online.get('overall', online.get('status'))
    return {'status': result['status'], 'online_status': observed_online, 'field_status': fields['status'], 'checks': result['checks'], 'facts': facts, 'values': values, 'count': count, 'visible_rows': visible_rows, 'row_identity_record_id': row_identity_record.get('record_id') if row_identity_record else None, 'row_identity_valid': row_identity_valid, 'service_count': service_count, 'baseline': baseline, 'sources': cp, 'service_files': service_files, 'reading_prompt': 'Turn on Writing Replay' in s, 'identity_witnesses': id_witness, 'first_identity_witness': first_witness, 'latest_write_utc': latest.isoformat()}

def run(p, out, only=None):
    manifest = json.loads((p / 'field_plan_manifest.json').read_text())
    frozen = {n: sha(p / n) == h for n, h in manifest['sha256'].items()}
    assert all(frozen.values()), frozen
    assignments = list(csv.DictReader((p / 'field_assignments.csv').read_text().splitlines()))
    assignments = [a for a in assignments if only is None or a['trial_id'] in only]
    data = {s: Data(p, g) for s, g in [('Calendar', 'calendar_runner'), ('Notion', 'notion_runner')]}
    details = []
    checks = []
    rows = []
    for a in assignments:
        trial = a['trial_id']
        d = data[a['service']]
        packet = d.packet(trial)
        assert packet['token'] == a['token'] and packet['condition'] == a['condition']
        create = [d.ref(x) for x in packet['create_admission_ids']]
        repair = [d.ref(x) for x in packet['repair_admission_ids']]
        actions = [d.ref(x) for x in packet['create_action_ids'] + packet['repair_action_ids']]
        decision = d.ref(packet['final_decision_record_id'])
        initialtime = when(create[0])
        decisontime = when(decision)
        elapsed = (decisontime - initialtime).total_seconds()
        cps = {}
        for phase in ['initial', 'final', 'audit']:
            cp = packet['checkpoints'][phase]
            cut = when(d.ref(cp['field_check_record_id']))
            effective = [r for r in d.rows if r.get('trial_id') == trial and kind(r) == 'action' and when(r, True) and (when(r, True) <= cut) and (r['record_id'] in [x['record_id'] for x in actions] or (a['service'] == 'Notion' and r.get('phase') in ['entry', 'repair']))]
            latest = max([when(r, True) for r in effective], default=initialtime)
            cps[phase] = ckpt(d, packet, phase, latest, a)
            checks.append({'trial': trial, 'phase': phase, 'check': 'online_reconstruction', 'status': 'PASS' if cps[phase]['status'] == cps[phase]['online_status'] else 'FAIL', 'derived': cps[phase]['status'], 'online': cps[phase]['online_status']})
        initial, final, audit = (cps[x] for x in ['initial', 'final', 'audit'])
        decision_text = decision.get('decision', decision.get('label', ''))
        claimed = 'CONFIRM' in decision_text.upper() and 'UNRESOLVED' not in decision_text.upper()
        count = audit['service_count'] if a['service'] == 'Calendar' else audit['count']
        knownwrong = initial['field_status'] == 'MISMATCH' and initial['facts']['native_ready'] and initial['facts']['native_fresh']
        targetkeys = {'wrong_checkbox': ['ui.verified'], 'wrong_marker': ['ui.marker'] if a['service'] == 'Notion' else ['ui.description', 'connector.description'], 'empty_marker': ['ui.marker'] if a['service'] == 'Notion' else ['ui.description', 'connector.description'], 'wrong_date': ['ui.start_date', 'ui.end_date', 'connector.start', 'connector.end'], 'wrong_end': ['ui.end_date', 'connector.end'], 'wrong_availability': ['ui.availability', 'connector.transparency']}.get(a['condition'], [])
        exposed = bool(targetkeys) and any((initial['checks'].get(k, {}).get('status') == 'MISMATCH' for k in targetkeys)) and initial['facts']['native_ready'] and initial['facts']['native_fresh']
        cleanup = []
        for rid in packet['cleanup_record_ids']:
            r = d.ref(rid)
            src = r if 'state' in r else d.ref(r.get('parent_zero_source_id', r.get('covered_state_id', r.get('source_state_id', r.get('source_state')))))
            s = src.get('state', '')
            zero = cal_count(s) == 0 if a['service'] == 'Calendar' else notion_count(s) == 0
            cleanup.append({'record_id': rid, 'source': src.get('record_id'), 'zero_from_state': zero, 'after_decision': bool(when(r) and when(r) > decisontime)})
        cleanzero = any((x['zero_from_state'] and x['after_decision'] for x in cleanup))
        if a['service'] == 'Calendar':
            cf = d.file(packet['cleanup_connector_file'])
            cr = cf.get('result', {})
            cb = cr.get('structuredContent', {})
            ca = cf.get('args', {})
            cleanzero = cleanzero and cr.get('isError') is False and (cb.get('events') == []) and (cb.get('next_page_token', 'missing') is None) and (ca.get('query') == a['token']) and (ca.get('time_min') == '2026-10-01T00:00:00-04:00') and (ca.get('time_max') == '2026-11-01T00:00:00-04:00') and (when(cf) > decisontime)
        row = {'trial_id': trial, 'service': a['service'], 'condition': a['condition'], 'repeat': int(a['repeat']), 'initial': initial['status'], 'final': final['status'], 'audit': audit['status'], 'initial_baseline': initial['baseline'], 'injection_exposed': exposed, 'wrong_detected': exposed and initial['status'] == 'MISMATCH', 'baseline_false_match': initial['baseline'] == 'MATCH' and knownwrong, 'create_calls': len(packet['create_action_ids']), 'repair_calls': len(packet['repair_action_ids']), 'initial_visible_rows': initial['visible_rows'], 'initial_distinct_records': initial['count'], 'same_identity': bool(packet.get('first_native_id')) and all((v['facts']['ui_id'] == identity(packet['first_native_id']) for v in cps.values())), 'audit_records': count, 'extra_records': count is not None and count > 1, 'claimed': claimed, 'proved_false_claim': claimed and audit['status'] == 'MISMATCH', 'clean_claim': claimed and audit['status'] == 'MATCH' and (elapsed <= int(a['deadline_seconds'])), 'unknown_claim': claimed and audit['status'] == 'UNKNOWN', 'elapsed_seconds': round(elapsed, 3), 'late': elapsed > int(a['deadline_seconds']), 'cleanup_zero': cleanzero}
        row['repair_success'] = bool(row['repair_calls']) and row['same_identity'] and (final['status'] == 'MATCH') and (audit['status'] == 'MATCH') and (count == 1)
        checks.append({'trial': trial, 'check': 'mutation_budget', 'status': 'PASS' if len(create) == len(packet['create_action_ids']) == 1 and len(repair) == len(packet['repair_action_ids']) <= 1 else 'FAIL'})
        trial_admissions = [r for r in d.rows if r.get('trial_id') == trial and kind(r) in ['mutation_admission', 'mutation_admitted']]
        baseline_sources = [r for r in d.rows if r.get('trial_id') == trial and 'state' in r and (when(r, True) < initialtime) and (cal_count(r['state']) == 0 and parse_qs(urlparse(r.get('url', '')).query).get('q') == [a['token']] if a['service'] == 'Calendar' else notion_count(r['state']) == 0 and 'FIELD-CHECK-20261015' in r['state'])]
        sequence = {'baseline_zero_before_create': bool(baseline_sources), 'all_admissions_listed': {r['record_id'] for r in trial_admissions} == set(packet['create_admission_ids'] + packet['repair_admission_ids']), 'freeze_before_create': dt.datetime.fromisoformat(manifest['frozen_utc']) < initialtime, 'create_admission_before_action': all((when(d.ref(x)) <= when(d.ref(y)) for x, y in zip(packet['create_admission_ids'], packet['create_action_ids']))), 'repair_admission_before_action': all((when(d.ref(x)) <= when(d.ref(y)) for x, y in zip(packet['repair_admission_ids'], packet['repair_action_ids']))), 'initial_before_repair': all((when(d.ref(packet['checkpoints']['initial']['field_check_record_id'])) < when(r) for r in repair)), 'final_before_decision': when(d.ref(packet['checkpoints']['final']['field_check_record_id'])) <= decisontime, 'audit_after_decision': when(d.ref(packet['checkpoints']['audit']['field_check_record_id'])) > decisontime, 'repair_only_after_mismatch': not repair or (initial['status'] == 'MISMATCH' and exposed), 'confirm_only_after_match': not claimed or (final['status'] == 'MATCH' and elapsed <= int(a['deadline_seconds'])), 'cleanup_active_zero': cleanzero}
        for phase in ['initial', 'final', 'audit']:
            cp = packet['checkpoints'][phase]
            cut = when(d.ref(cp['field_check_record_id']))
            refs = [d.ref(cp[k]) for k in ['native_state_id', 'native_value_read_id', 'covered_state_id'] if cp.get(k)] + [d.ref(k) for k in cp.get('covered_identity_record_ids', [])] + [d.file(k) for k in cp.get('connector_files', [])]
            sequence[phase + '_sources_before_check'] = all((when(r, True) and when(r, True) <= cut for r in refs))
            if phase == 'audit':
                sequence['audit_sources_after_decision'] = all((when(r) and when(r) > decisontime for r in refs))
        for name, ok in sequence.items():
            checks.append(dict(trial=trial, check=name, status='PASS' if ok else 'FAIL'))
        rows.append(row)
        details.append({'trial_id': trial, 'checkpoints': cps, 'cleanup': cleanup, 'decision': decision, 'packet': packet})
    groups = []
    for site in ['Calendar', 'Notion']:
        rs = [r for r in rows if r['service'] == site]
        sums = {k: sum((bool(r[k]) for r in rs)) for k in ['injection_exposed', 'wrong_detected', 'baseline_false_match', 'repair_success', 'extra_records', 'claimed', 'proved_false_claim', 'clean_claim', 'unknown_claim', 'late', 'cleanup_zero']}
        sums.update(service=site, assigned=len(rs), initial_match=sum((r['initial'] == 'MATCH' for r in rs)), initial_unknown=sum((r['initial'] == 'UNKNOWN' for r in rs)), correct_controls=sum((r['condition'] == 'correct' for r in rs)), control_matches=sum((r['condition'] == 'correct' and r['initial'] == 'MATCH' for r in rs)), repairs=sum((r['repair_calls'] for r in rs)), creates=sum((r['create_calls'] for r in rs)), audited_records=sum((r['audit_records'] or 0 for r in rs)))
        groups.append(sums)
    inputs = {f.name: sha(f) for f in sorted(p.glob('field_*')) if f.is_file() and (f.name.endswith('_actions.jsonl') or f.name.endswith('_records.json') or f.name in ['field_assignments.csv', 'field_plan_manifest.json'])}
    inputs['fieldcheck.py'] = sha(p / 'fieldcheck.py')
    summary = {'status': 'COMPLETE' if only is None else 'DEVELOPMENT_SUBSET', 'assigned': len(rows), 'groups': groups, 'frozen_checks': frozen, 'input_sha256': inputs, 'check_failures': [c for c in checks if c['status'] == 'FAIL'], 'interpretation': 'Selected deliberately wrong values; paired baseline is offline; unknown fields and failed injections stay in the results.'}
    out.mkdir(parents=True, exist_ok=True)
    for name, obj in [('field_summary.json', summary), ('field_details.json', details), ('field_analysis_checks.json', checks)]:
        (out / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    with (out / 'field_trials.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (out / 'field_groups.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(groups[0]))
        w.writeheader()
        w.writerows(groups)
    print(json.dumps(summary, indent=2, sort_keys=True))
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-dir', type=Path, default=Path('.'))
    ap.add_argument('--output-dir', type=Path, default=Path('.'))
    ap.add_argument('--trials', help='Development subset only; omit for release')
    args = ap.parse_args()
    run(args.input_dir, args.output_dir, args.trials.split(',') if args.trials else None)
