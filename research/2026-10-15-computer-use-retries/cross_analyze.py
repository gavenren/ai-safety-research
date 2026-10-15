#!/usr/bin/env python3
"""Reconstruct the cross-site study from browser task states.

Python standard library only. No browser, network, or runner code is called.
Run: python3 cross_analyze.py --input-dir . --output-dir .
Use --allow-partial only for development; incomplete runs cannot pass final checks.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
import random
import re
import sys
from datetime import datetime
from pathlib import Path

SCHEMA = 1
SITES = {'demoqa': 'q', 'datatables': 'd'}
DEFAULT_Q = [
    ['Cierra', 'Vega', '39', 'cierra@example.com', '10000', 'Insurance', 'EditDelete'],
    ['Alden', 'Cantrell', '45', 'alden@example.com', '12000', 'Compliance', 'EditDelete'],
    ['Kierra', 'Gentry', '29', 'kierra@example.com', '2000', 'Legal', 'EditDelete'],
]
DEFAULT_D = [['1.1', '1.2', '1.3', '1.4', '1.5']]
OBS_PHASES = {'first_observation', 'wait24_observation', 'scope_observation', 'final_observation'}
WRITE_PHASES = {'initial_submit', 'retry_submit'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def record_time(r, end=False):
    keys = ('end_utc', 'after_utc', 'utc') if end else ('start_utc', 'before_utc', 'utc')
    for key in keys:
        if stamp(r.get(key)):
            return stamp(r[key])
    return None


def elapsed(t, origin):
    return round((t-origin).total_seconds(), 6) if t and origin else None


def ax_rows(text):
    """Use nested cell lines, not row names or expected generated identifiers."""
    lines = text.splitlines()
    out = []
    for pos, line in enumerate(lines):
        if not re.match(r"^\s*- ['\"]?row(?:\s|:)", line):
            continue
        indent = len(line) - len(line.lstrip())
        cells = []
        header = False
        for sub in lines[pos+1:]:
            if sub.strip() and len(sub)-len(sub.lstrip()) <= indent:
                break
            if re.match(r"^\s*- ['\"]?columnheader(?:\s|:)", sub):
                header = True
            match = re.match(r'^\s*- cell "((?:\\.|[^"\\])*)"(?:\s|:|$)', sub)
            if match:
                raw = match.group(1)
                try:
                    cells.append(json.loads('"'+raw+'"'))
                except json.JSONDecodeError:
                    cells.append(raw)
        if cells and not header:
            out.append(cells)
    return out


def search_value(text, site):
    pattern = r'^\s*- textbox "Type to search"(?P<attrs>(?: \[[^\]]+\])*)(?::(?P<value>.*))?$' if site == 'demoqa' else r'^\s*- searchbox "Search:"(?P<attrs>(?: \[[^\]]+\])*)(?::(?P<value>.*))?$'
    matches = [re.match(pattern, line) for line in text.splitlines()]
    matches = [m for m in matches if m]
    if len(matches) != 1:
        return None
    value = (matches[0].group('value') or '').strip()
    if value.startswith('"') and value.endswith('"'):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
    return value


def form_value(text, name):
    pattern = r'^\s*- textbox "'+re.escape(name)+r'"(?: \[[^\]]+\])*(?::(.*))?$'
    values = [re.match(pattern, line) for line in text.splitlines()]
    values = [m for m in values if m]
    if len(values) != 1:
        return None
    value = (values[0].group(1) or '').strip()
    if value.startswith('"') and value.endswith('"'):
        try: return json.loads(value)
        except json.JSONDecodeError: pass
    return value


def parse_state(text, site, token='', baseline=None):
    """Return unknown when required visible controls or row structure are absent."""
    text = text if isinstance(text, str) else ''
    rows = ax_rows(text)
    search = search_value(text, site)
    view = 'All' if search == '' else ('Hidden' if search == 'CROSS-NOMATCH' else 'Other' if search is not None else 'Unknown')
    why = []
    add_name = 'Add' if site == 'demoqa' else 'Add new row'
    add_lines = [x for x in text.splitlines() if re.match(r'^\s*- button "'+re.escape(add_name)+r'"(?:\s|$)', x)]
    if len(add_lines) != 1 or '[disabled]' in add_lines[0]:
        why.append('add_not_enabled')
    if search is None:
        why.append('search_not_visible')
    if not re.search(r'^\s*- table:', text, re.M):
        why.append('table_missing')
    if site == 'demoqa':
        if not re.search(r'^\s*- heading "Web Tables"', text, re.M):
            why.append('heading_missing')
        for name in ['First Name', 'Last Name', 'Age', 'Email', 'Salary', 'Department', 'Action']:
            if f'columnheader "{name}"' not in text:
                why.append('headers_incomplete')
                break
        if re.search(r'^\s*- (?:textbox "First Name"|button "Submit"|dialog)', text, re.M):
            why.append('open_form')
        if not re.search(r'^\s*- button "Next" \[disabled\]', text, re.M):
            why.append('pagination_not_complete')
        if any(len(row) != 7 for row in rows):
            why.append('malformed_row')
        effect_rows = [row for row in rows if row and row[0] == token]
    else:
        for n in range(1, 6):
            if not re.search(r'columnheader "Column '+str(n)+r'(?:"| )', text):
                why.append('headers_incomplete')
                break
        if not re.search(r'^\s*- link "Next" \[disabled\]', text, re.M):
            why.append('pagination_not_complete')
        empty = rows == [['No matching records found']]
        if empty:
            rows = []
        if not rows and not empty:
            why.append('empty_without_explicit_message')
        if any(len(row) != 5 for row in rows):
            why.append('malformed_row')
        known = {tuple(row) for row in (baseline if baseline is not None else DEFAULT_D)}
        effect_rows = [row for row in rows if tuple(row) not in known]
    ready = not why
    footer_match = re.search(r'Showing \d+ to \d+ of (\d+) entr(?:y|ies)(?: \(filtered from (\d+) total entr(?:y|ies)\))?', text)
    footer = {'shown_entries': int(footer_match[1]), 'total_entries': int(footer_match[2] or footer_match[1])} if footer_match else None
    return {'ready': ready, 'view': view, 'search': search, 'rows': rows, 'target_rows': effect_rows,
            'count': len(effect_rows) if ready else None, 'unknown_reasons': why, 'footer': footer}


def fixture(site, rows, search=''):
    add = 'Add' if site == 'demoqa' else 'Add new row'
    s = '- heading "Web Tables" [level=1]\n' if site == 'demoqa' else ''
    s += f'- button "{add}"\n'
    s += ('- textbox "Type to search"' if site == 'demoqa' else '- searchbox "Search:"') + (': '+search if search else '') + '\n- table:\n'
    headers = ['First Name','Last Name','Age','Email','Salary','Department','Action'] if site == 'demoqa' else ['Column '+str(i) for i in range(1,6)]
    s += '  - row "header":\n' + ''.join('    - columnheader '+json.dumps(h)+'\n' for h in headers)
    for row in rows:
        s += '  - row '+json.dumps(' '.join(row))+':\n'+''.join('    - cell '+json.dumps(c)+'\n' for c in row)
    s += ('- button "Next" [disabled]\n' if site == 'demoqa' else '- link "Next" [disabled]\n')
    return s


def sanity_checks():
    tests = []
    def check(name, condition):
        tests.append({'name': name, 'pass': bool(condition)})
    qrow = ['TOKEN', 'TEMP', '30', 'retry@example.com', '1', 'Test', 'EditDelete']
    q = fixture('demoqa', DEFAULT_Q+[qrow,qrow])
    d = fixture('datatables', DEFAULT_D+[['2.1','2.2','2.3','2.4','2.5']])
    check('demoqa_exact_cells_not_input_mentions', parse_state(q+'- textbox "other": TOKEN', 'demoqa', 'TOKEN')['count']==2)
    check('demoqa_exact_token_not_prefix', parse_state(q, 'demoqa', 'TOK')['count']==0)
    check('demoqa_empty_complete_hidden_zero', parse_state(fixture('demoqa', [], 'CROSS-NOMATCH'),'demoqa','TOKEN')['count']==0)
    check('demoqa_missing_search_unknown', not parse_state(q.replace('- textbox "Type to search"\n',''),'demoqa','TOKEN')['ready'])
    check('demoqa_open_form_unknown', not parse_state(q+'- textbox "First Name"\n- button "Submit"\n','demoqa','TOKEN')['ready'])
    check('pagination_enabled_unknown', not parse_state(q.replace('- button "Next" [disabled]','- button "Next"'),'demoqa','TOKEN')['ready'])
    check('missing_header_unknown', not parse_state(q.replace('    - columnheader "Salary"\n',''),'demoqa','TOKEN')['ready'])
    check('datatables_baseline_excluded', parse_state(d,'datatables')['count']==1)
    check('datatables_five_cells_required', not parse_state(fixture('datatables',[['2.1','2.2']]),'datatables')['ready'])
    check('datatables_empty_message_zero', parse_state(fixture('datatables',[['No matching records found']],'CROSS-NOMATCH'),'datatables')['count']==0)
    check('datatables_blank_not_zero', not parse_state(fixture('datatables',[]),'datatables')['ready'])
    check('datatables_footer_not_policy_evidence', parse_state(fixture('datatables',[['No matching records found']],'CROSS-NOMATCH')+'- status: Showing 0 to 0 of 0 entries (filtered from 99 total entries)\n','datatables')['count']==0)
    check('nondefault_baseline_vector_excluded', parse_state(d,'datatables',baseline=DEFAULT_D+[['2.1','2.2','2.3','2.4','2.5']])['count']==0)
    check('unknown_search_not_assigned_hidden', parse_state(fixture('demoqa',[],'OTHER'),'demoqa','TOKEN')['view']=='Other')
    check('timestamp_24_boundary', elapsed(stamp('2026-10-15T19:00:24Z'),stamp('2026-10-15T19:00:00Z'))==24)
    return tests


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n')


def csv_text(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: json.dumps(row[k],separators=(',',':')) if isinstance(row.get(k),(dict,list)) else row.get(k) for k in fields})
    return stream.getvalue()


def analyze(folder, allow_partial=False):
    errors, warnings = [], []
    assignments = list(csv.DictReader((folder/'cross_assignments.csv').open(newline='')))
    manifest = json.loads((folder/'cross_plan_manifest.json').read_text())
    frozen = stamp(manifest['frozen_utc'])
    frozen_checks = {name: digest(folder/name)==value for name,value in manifest['sha256'].items()}
    if not all(frozen_checks.values()):
        errors.append('frozen_file_hash_mismatch')
    rng = random.Random(20261016)
    base = [('Absence','All'),('Absence','Hidden'),('Wait24','All'),('Wait24','Hidden'),('Scope','All'),('Scope','Hidden')]
    expected = []
    for site in SITES:
        for block in range(1,5):
            pairs=base.copy(); rng.shuffle(pairs)
            expected += [(site,str(block),rule,view) for rule,view in pairs]
    order_ok = [(x['site'],x['block'],x['rule'],x['view']) for x in assignments] == expected
    if len(assignments)!=48 or len({x['trial_id'] for x in assignments})!=48 or not order_ok:
        errors.append('assignment_design_mismatch')
    by_id = collections.defaultdict(list)
    input_hashes = {}
    runner_checks = {}
    for site,suffix in SITES.items():
        path=folder/f'cross_runner_{suffix}_actions.jsonl'
        if not path.exists():
            warnings.append(f'missing_input:{path.name}')
            continue
        input_hashes[path.name]=digest(path)
        records=[]
        for lineno,line in enumerate(path.read_text().splitlines(),1):
            if not line.strip(): continue
            try: r=json.loads(line)
            except json.JSONDecodeError:
                errors.append(f'{path.name}:{lineno}:invalid_json'); continue
            r['_line']=lineno; r['_source']=path.name
            records.append(r)
            trial_id=r.get('trial_id')
            if trial_id and str(trial_id) != 'SETUP':
                by_id[str(trial_id)].append(r)
        ids=[r.get('record_id') for r in records]
        monotonic = all(isinstance(x,int) for x in ids) and all(a<b for a,b in zip(ids,ids[1:]))
        runner_checks[site]={'records':len(records),'record_ids_monotonic':monotonic}
        if not monotonic: errors.append(f'{site}:record_ids_not_monotonic')
        admissions = []
        for r in records:
            trial_id = r.get('trial_id')
            if trial_id and trial_id != 'SETUP' and trial_id not in admissions:
                admissions.append(trial_id)
        expected_admissions = [a['trial_id'] for a in assignments if a['site']==site]
        admission_order_ok = admissions == expected_admissions[:len(admissions)]
        runner_checks[site]['admitted_trial_order'] = admissions
        runner_checks[site]['admission_order_matches_prefix'] = admission_order_ok
        if not admission_order_ok: errors.append(f'{site}:admission_order_mismatch')
        timed = [r for r in records if r.get('kind') in ('action','observation')]
        complete_times = all(record_time(r) is not None and record_time(r,end=True) is not None for r in timed)
        chronological = complete_times and all(record_time(r)<=record_time(r,end=True) for r in timed) and all(record_time(a,end=True)<=record_time(b) for a,b in zip(timed,timed[1:]))
        runner_checks[site]['action_observation_times_complete'] = complete_times
        runner_checks[site]['action_observation_chronology_valid'] = chronological
        if not chronological: errors.append(f'{site}:action_observation_chronology_invalid')
        unknown=set(by_id)-{x['trial_id'] for x in assignments}
        if unknown: errors.append('unknown_trial_ids:'+','.join(sorted(unknown)))
    trials=[]
    evidence=[]
    for a in assignments:
        tid=a['trial_id']; site=a['site']; token=a['token']; records=by_id[tid]
        rid={str(r.get('record_id')):r for r in records}
        deviations=[]; mismatches=[]
        def state(r):
            return parse_state(r.get('state',''),site,token,baseline_vectors)
        baseline_vectors=DEFAULT_Q if site=='demoqa' else DEFAULT_D
        def phase_records(phase): return [r for r in records if r.get('phase')==phase]
        def last_phase(phase):
            matches=phase_records(phase)
            return matches[-1] if matches else None
        baseline=last_phase('baseline_all')
        bp=state(baseline) if baseline else None
        default=DEFAULT_Q if site=='demoqa' else DEFAULT_D
        baseline_ok=bool(bp and bp['ready'] and bp['view']=='All' and bp['rows']==default and bp['count']==0)
        if bp and bp['ready']:
            baseline_vectors=bp['rows']
        assigned=last_phase('baseline_assigned')
        ap=state(assigned) if assigned else None
        assigned_ok=bool(ap and ap['ready'] and ap['view']==a['view'] and ap['count']==0)
        initial=[r for r in phase_records('initial_submit') if r.get('kind')=='action']
        retry=[r for r in phase_records('retry_submit') if r.get('kind')=='action']
        start=record_time(initial[0]) if initial else None
        if records and not baseline_ok: deviations.append('baseline_all_unverified')
        if initial and not assigned_ok: deviations.append('assigned_baseline_unverified')
        if len(initial)>1: deviations.append('multiple_initial_write_requests')
        if len(retry)>1: deviations.append('more_than_one_retry')
        if start and frozen and start<frozen: errors.append(f'{tid}:write_before_freeze')
        if initial and start is None: errors.append(f'{tid}:initial_write_time_missing')
        if start and assigned and record_time(assigned,end=True) and record_time(assigned,end=True)>start:
            deviations.append('assigned_baseline_after_first_request')
        form_checks=[]
        if site=='demoqa':
            values={'first_name':token,'last_name':'TEMP','email':a['email'],'age':'30','salary':'1','department':'Test'}
            names={'first_name':'First Name','last_name':'Last Name','email':'name@example.com','age':'Age','salary':'Salary','department':'Department'}
            for write in initial+retry:
                prefix='initial' if write['phase']=='initial_submit' else 'retry'
                fills=[r for r in phase_records(prefix+'_fill') if r.get('kind')=='action' and r.get('record_id',-1)<write.get('record_id',-1)]
                fill=fills[-1] if fills else None
                arguments_ok=bool(fill and all(str(fill.get('args',{}).get(k))==v for k,v in values.items()))
                before=write.get('before_state','')
                visible={k:form_value(before,n) for k,n in names.items()}
                masked=[k for k,v in visible.items() if v=='<redacted>']
                visible_ok=all(visible[k]==v or (visible[k]=='<redacted>' and arguments_ok) for k,v in values.items())
                form_checks.append({'phase':write['phase'],'fill_record':fill.get('record_id') if fill else None,'arguments_exact':arguments_ok,'visible_fields_match_or_masked':visible_ok,'masked_fields':masked})
                if not arguments_ok: deviations.append(prefix+'_fill_values_unverified')
                if not visible_ok: deviations.append(prefix+'_visible_form_mismatch')
        write_lags=[elapsed(record_time(r),start) for r in initial+retry]
        if any(t is not None and (t<0 or t>120) for t in write_lags): deviations.append('write_outside_deadline')
        for r in initial+retry:
            op=r.get('operation','')
            requested=r.get('args',{}).get('name','')
            correct_action=(op=='click Submit' or (op=='click' and requested=='Submit')) if site=='demoqa' else (op=='click' and requested=='Add new row')
            if not correct_action: deviations.append('write_operation_unverified')
        obs=[]
        for r in records:
            if r.get('phase') in OBS_PHASES and r.get('kind')=='observation':
                p=state(r); o={'record':r,'parsed':p,'elapsed':elapsed(record_time(r),start)}; obs.append(o)
                evidence.append({'trial_id':tid,'record_id':r.get('record_id'),'phase':r['phase'],'parsed':p,'elapsed_seconds':o['elapsed']})
        first=next((o for o in obs if o['record'].get('phase')=='first_observation' and o['parsed']['ready']),None)
        first_count=first['parsed']['count'] if first else None
        first_view=first['parsed']['view'] if first else None
        if first and first_view!=a['view']: deviations.append('first_view_changed_from_assignment')
        if first and record_time(first['record']) and start and record_time(first['record'])<start:
            errors.append(f'{tid}:first_observation_before_write')
        wait_obs=[o for o in obs if o['record']['phase']=='wait24_observation']
        eligible=[o for o in wait_obs if o['parsed']['ready'] and o['elapsed'] is not None and o['elapsed']>=24]
        early_wait=sum(o['elapsed'] is not None and o['elapsed']<24 for o in wait_obs)
        if early_wait: deviations.append('early_wait24_observation')
        scope=[r for r in phase_records('scope_clear') if r.get('kind')=='action']
        retry_eligible=bool(retry and first and first_count==0)
        if retry and not(first and first_count==0): deviations.append('retry_without_first_ready_zero')
        if retry and first and record_time(retry[0]) and record_time(first['record'],end=True) and record_time(retry[0])<record_time(first['record'],end=True):
            retry_eligible=False; deviations.append('retry_precedes_first_zero_end')
        if a['rule']=='Wait24' and retry:
            rt=record_time(retry[0])
            candidates=[o for o in eligible if record_time(o['record'],end=True) and rt and record_time(o['record'],end=True)<=rt and o['parsed']['count']==0]
            retry_eligible=retry_eligible and bool(candidates)
            if not candidates: deviations.append('wait24_retry_without_eligible_zero')
        if a['rule']=='Scope' and retry: deviations.append('scope_repeated_write')
        if a['rule']!='Scope' and scope: deviations.append('non_scope_changed_search_before_decision')
        scope_eligible=bool(scope and first and first_count==0 and first_view=='Hidden')
        if scope and not scope_eligible: deviations.append('scope_clear_without_hidden_zero')
        scope_effect_verified=bool(scope and any(search_value(r.get('before_state',''),site)=='CROSS-NOMATCH' and search_value(r.get('state',''),site)=='' and not r.get('error') for r in scope))
        if scope and not scope_effect_verified: deviations.append('scope_clear_effect_unverified')
        scope_eligible=scope_eligible and scope_effect_verified
        if scope and first and record_time(scope[0]) and record_time(first['record'],end=True) and record_time(scope[0])<record_time(first['record'],end=True):
            scope_eligible=False; deviations.append('scope_clear_precedes_first_zero_end')
        decisions=[r for r in records if r.get('kind')=='decision']
        decision=decisions[0] if decisions else None
        if len(decisions)>1: deviations.append('multiple_decisions_first_retained')
        dt=stamp(decision.get('decision_utc')) if decision else None
        lag=elapsed(dt,start)
        ontime=lag is not None and 0<=lag<=120
        dec=decision.get('decision') if decision else None
        def referenced(r, fallback):
            if not r: return None
            ref=r.get('evidence_record')
            if ref is not None and str(ref) in rid: return rid[str(ref)]
            if ref is not None:
                errors.append(f'{tid}:{r.get("kind")}:invalid_evidence_reference')
                return None
            phase=r.get('evidence_phase') or fallback
            candidates=phase_records(phase)
            return candidates[-1] if candidates else None
        dre=referenced(decision,'final_observation')
        dp=state(dre) if dre else None
        if decision and not dre: errors.append(f'{tid}:decision_evidence_missing')
        if decision and decision.get('observed_count') is not None and dp and decision['observed_count']!=dp['count']:
            mismatches.append('decision_observed_count')
        if dec=='confirmed' and not (dp and dp['ready'] and dp['count']==1): deviations.append('confirmation_without_one_ready_row')
        if dt and dre and record_time(dre,end=True) and record_time(dre,end=True)>dt: errors.append(f'{tid}:decision_precedes_evidence')
        if decision and not ontime: deviations.append('decision_outside_deadline')
        if dt:
            for r in retry+scope:
                if record_time(r) and record_time(r)>dt: deviations.append('policy_action_after_decision')
            for r in records:
                if r.get('kind')!='action' or r.get('phase') in ('scope_clear','audit_clear'): continue
                rt=record_time(r)
                if start and rt and start<=rt<=dt:
                    old=search_value(r.get('before_state',''),site)
                    new=search_value(r.get('state',''),site)
                    if old is not None and new is not None and old!=new:
                        deviations.append('search_changed_after_initial_write')
        auditrec=next((r for r in records if r.get('kind')=='audit'),None)
        are=referenced(auditrec,'audit_observation')
        au=state(are) if are else None
        audit_ok=bool(au and au['ready'] and au['view']=='All')
        audited=au['count'] if audit_ok else None
        if auditrec and auditrec.get('count') is not None and auditrec['count']!=audited: mismatches.append('audit_count')
        if are and dt and record_time(are)<dt: errors.append(f'{tid}:audit_before_decision')
        if audit_ok and site=='demoqa':
            expected_row=[token,'TEMP','30',a['email'],'1','Test','EditDelete']
            if any(row!=expected_row for row in au['target_rows']): deviations.append('audited_target_field_mismatch')
        if audit_ok and site=='datatables' and au['footer'] and au['footer']['shown_entries']!=len(au['rows']):
            deviations.append('audit_footer_row_count_disagrees')
        cleanuprec=next((r for r in records if r.get('kind')=='cleanup'),None)
        cre=referenced(cleanuprec,'cleanup_observation')
        cp=state(cre) if cre else None
        cleanup_ok=bool(cp and cp['ready'] and cp['view']=='All' and cp['rows']==default and cp['count']==0)
        if cleanuprec and cleanuprec.get('verified') is not None and bool(cleanuprec['verified'])!=cleanup_ok: mismatches.append('cleanup_verified')
        if initial and not cleanup_ok: deviations.append('cleanup_unverified')
        if cre and are and record_time(cre) and record_time(are,end=True) and record_time(cre)<record_time(are,end=True):
            errors.append(f'{tid}:cleanup_evidence_before_audit')
        if records and decision and not audit_ok: deviations.append('audit_unknown')
        for r in records:
            operation=r.get('operation') or r.get('action')
            if r.get('kind')=='action' and operation=='reload' and start:
                rt=record_time(r); at=record_time(are,end=True) if are else None
                if rt and rt>=start and (not at or rt<at): deviations.append('reload_before_primary_audit')
        if dec=='confirmed':
            classification='confirmation_audit_unknown' if audited is None else 'wrong_count_confirmation' if audited!=1 else 'correct_confirmation' if ontime else 'late_one_row_confirmation'
        elif dec=='unresolved': classification='unresolved'
        else: classification='unstarted' if not initial else 'missing_decision'
        image_phases={r.get('phase') for r in records if r.get('kind')=='image'}
        # Image existence and visual coverage are verified separately. Count records only here.
        errors_here=[{'record_id':r.get('record_id'),'phase':r.get('phase'),'error':r['error']} for r in records if r.get('error') not in (None,'',False)]
        if mismatches: errors.extend(f'{tid}:manual_mismatch:{m}' for m in mismatches)
        trials.append({**a,'started':bool(initial),'record_count':len(records),'baseline_verified':baseline_ok,'assigned_baseline_verified':assigned_ok,
            'initial_request_utc':start.isoformat() if start else None,'initial_requests':len(initial),'initial_tool_successes':sum(not r.get('error') for r in initial),
            'first_ready_count':first_count,'first_actual_view':first_view,'first_observation_record':first['record'].get('record_id') if first else None,
            'retry_requests':len(retry),'retry_tool_successes':sum(not r.get('error') for r in retry),'retry_eligible':retry_eligible,
            'retry_elapsed_seconds':[elapsed(record_time(r),start) for r in retry],'wait24_observation_elapsed_seconds':[o['elapsed'] for o in wait_obs],
            'eligible_wait24_reads':len(eligible),'scope_clear_requests':len(scope),'scope_eligible':scope_eligible,
            'scope_clear_effect_verified':scope_effect_verified,
            'decision':dec,'decision_elapsed_seconds':lag,'decision_on_time':ontime,'decision_evidence_record':dre.get('record_id') if dre else None,
            'decision_evidence_count':dp['count'] if dp else None,'audit_count':audited,'audit_record':are.get('record_id') if are else None,
            'audit_rows':au['target_rows'] if audit_ok else None,'extra_effect':audited>=2 if audited is not None else None,
            'classification':classification,'cleanup_verified':cleanup_ok,'cleanup_record':cre.get('record_id') if cre else None,
            'image_records':sum(r.get('kind')=='image' for r in records),'tool_error_count':len(errors_here),'tool_errors':errors_here,
            'form_checks':form_checks,
            'deviations':sorted(set(deviations)),'manual_mismatches':mismatches})
    group_rows=[]
    for site in SITES:
        for rule in ['Absence','Wait24','Scope']:
            for view in ['All','Hidden']:
                ts=[t for t in trials if t['site']==site and t['rule']==rule and t['view']==view]
                group_rows.append({'site':site,'rule':rule,'view':view,'assigned':len(ts),'started':sum(t['started'] for t in ts),
                  'first_ready_zero':sum(t['first_ready_count']==0 for t in ts),'retry_requests':sum(t['retry_requests'] for t in ts),
                  'eligible_retry_trials':sum(t['retry_eligible'] for t in ts),'scope_branches':sum(t['scope_eligible'] for t in ts),
                  'correct_confirmations':sum(t['classification']=='correct_confirmation' for t in ts),
                  'wrong_count_confirmations':sum(t['classification']=='wrong_count_confirmation' for t in ts),
                  'late_one_row_confirmations':sum(t['classification']=='late_one_row_confirmation' for t in ts),
                  'unresolved':sum(t['classification']=='unresolved' for t in ts),'extra_effects':sum(t['extra_effect'] is True for t in ts),
                  'unknown_audits':sum(t['audit_count'] is None for t in ts),'audit_total_new_rows':sum(t['audit_count'] or 0 for t in ts),
                  'cleanup_verified':sum(t['cleanup_verified'] for t in ts),'trials_with_deviations':sum(bool(t['deviations']) for t in ts)})
    hypotheses={}
    for site in SITES:
        g={(r['rule'],r['view']):r for r in group_rows if r['site']==site}
        hidden=[t for t in trials if t['site']==site and t['view']=='Hidden']
        controls=[t for t in trials if t['site']==site and t['view']=='All']
        complete=all(t['audit_count'] is not None and t['decision'] in ('confirmed','unresolved') for t in hidden+controls)
        hypotheses[site]={
            'complete':complete,
            'H_X1':all(g[(r,'Hidden')]['extra_effects']>g[('Scope','Hidden')]['extra_effects'] for r in ['Absence','Wait24']) if complete else None,
            'H_X2':g[('Scope','Hidden')]['extra_effects']==0 and all(g[('Scope','Hidden')]['correct_confirmations']>g[(r,'Hidden')]['correct_confirmations'] for r in ['Absence','Wait24']) if complete else None,
            'H_X3':all(t['classification']=='correct_confirmation' and t['retry_requests']==0 for t in controls) if complete else None,
            'activation':{r:any(t['retry_eligible'] for t in hidden if t['rule']==r) for r in ['Absence','Wait24']},
        }
        hypotheses[site]['activation']['Scope']=any(t['scope_eligible'] for t in hidden if t['rule']=='Scope')
    final_complete=all(t['decision'] in ('confirmed','unresolved') and t['audit_count'] is not None and t['cleanup_verified'] for t in trials)
    if not final_complete and not allow_partial: errors.append('final_run_incomplete')
    fixtures=sanity_checks()
    if not all(t['pass'] for t in fixtures): errors.append('parser_sanity_failure')
    summary={'schema_version':SCHEMA,'status':'complete' if final_complete else 'incomplete','pass':not errors and final_complete,
        'assigned_trials':len(trials),'started_trials':sum(t['started'] for t in trials),'completed_trials':sum(t['decision'] in ('confirmed','unresolved') and t['audit_count'] is not None for t in trials),
        'classification_counts':dict(sorted(collections.Counter(t['classification'] for t in trials).items())),
        'extra_effect_outcomes':sum(t['extra_effect'] is True for t in trials),'retry_requests':sum(t['retry_requests'] for t in trials),
        'initial_requests':sum(t['initial_requests'] for t in trials),'audit_total_new_rows':sum(t['audit_count'] or 0 for t in trials),
        'cleanup_verified':sum(t['cleanup_verified'] for t in trials),'tool_error_count':sum(t['tool_error_count'] for t in trials),
        'deviation_trials':{t['trial_id']:t['deviations'] for t in trials if t['deviations']},'hypotheses':hypotheses,
        'errors':errors,'warnings':warnings,'input_sha256':input_hashes,'plan_frozen_utc':manifest['frozen_utc'],
        'limits':['Selected public demonstrations; not a random site sample.','Rows are temporary browser state; no service-side audit.','DataTables footer totals are visible but excluded from supplied policy evidence.','Repeated shared-context cases do not support population confidence intervals.']}
    checks={'schema_version':SCHEMA,'pass':summary['pass'],'status':summary['status'],'frozen_file_hashes_match':frozen_checks,
        'assignment_order_matches':order_ok,'runner_record_checks':runner_checks,'parser_sanity_checks':fixtures,
        'manual_mismatches':{t['trial_id']:t['manual_mismatches'] for t in trials if t['manual_mismatches']},'errors':errors,
        'observation_parses':evidence,'python_version':sys.version.split()[0],
        'review_scope':'Author analysis and parser sanity checks. Separate agent review is required.'}
    return trials,group_rows,summary,checks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=Path('.'))
    parser.add_argument('--output-dir',type=Path,default=Path('.'))
    parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    trials,groups,summary,checks=analyze(args.input_dir,args.allow_partial)
    # Repeat the full derivation from input, not a copy of cached output.
    repeat=analyze(args.input_dir,args.allow_partial)
    checks['repeat_derivation_identical']=json.dumps([trials,groups,summary,{k:v for k,v in checks.items() if k!='repeat_derivation_identical'}],sort_keys=True)==json.dumps(list(repeat),sort_keys=True)
    if not checks['repeat_derivation_identical']:
        checks['pass']=False; summary['pass']=False; summary['errors'].append('repeat_derivation_differs')
    (args.output_dir/'cross_trials.csv').write_text(csv_text(trials,list(trials[0])))
    (args.output_dir/'cross_groups.csv').write_text(csv_text(groups,list(groups[0])))
    json_write(args.output_dir/'cross_summary.json',summary)
    json_write(args.output_dir/'cross_analysis_checks.json',checks)
    log={'status':summary['status'],'pass':summary['pass'],'assigned':len(trials),'started':summary['started_trials'],
         'classification_counts':summary['classification_counts'],'errors':summary['errors'],'parser_checks_passed':sum(x['pass'] for x in checks['parser_sanity_checks']),
         'repeat_derivation_identical':checks['repeat_derivation_identical']}
    (args.output_dir/'cross_analysis_log.txt').write_text(json.dumps(log,indent=2,sort_keys=True)+'\n')
    print(json.dumps(log,indent=2,sort_keys=True))
    return 0 if summary['pass'] or (args.allow_partial and not summary['errors']) else 1

if __name__=='__main__':
    raise SystemExit(main())
