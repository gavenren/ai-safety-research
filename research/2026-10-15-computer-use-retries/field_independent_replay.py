#!/usr/bin/env python3
"""Independent evidence extraction for the field-check study.

This module imports no study checker, runner adapter, or main analyzer. Values
must come from native snapshots, DOM read records, and service replies. It is
written after plan freeze and before final results. It is not trial execution.
"""
import base64
import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs

ABSENT = object()
MATCH, MISMATCH, UNKNOWN = "MATCH", "MISMATCH", "UNKNOWN"


def aggregate(items):
    vals = list(items)
    if not vals or any(x not in (MATCH, MISMATCH, UNKNOWN) for x in vals):
        return UNKNOWN
    if MISMATCH in vals:
        return MISMATCH
    return UNKNOWN if UNKNOWN in vals else MATCH


def compare(observed, expected):
    if observed is ABSENT or type(observed) != type(expected):
        return UNKNOWN
    return MATCH if observed == expected else MISMATCH


def marker(observed, expected, connector=False):
    if type(observed) is not str or '<' in observed or '>' in observed:
        return UNKNOWN
    if connector:
        while observed.endswith(('\r', '\n')):
            observed = observed[:-1]
    return MATCH if observed == expected else MISMATCH


def calendar_date(observed, expected, connector=False):
    if not isinstance(observed, str):
        return UNKNOWN
    fmt = '%Y-%m-%dT%H:%M:%S' if connector else '%Y-%m-%d'
    try:
        parsed = dt.datetime.strptime(observed, fmt)
        if parsed.strftime(fmt) != observed:
            return UNKNOWN
    except ValueError:
        return UNKNOWN
    return MATCH if observed == expected else MISMATCH


def ax_tree(state):
    """Small indentation tree. It keeps duplicate controls and their scopes."""
    root = {'line': '', 'children': [], 'indent': -1}
    stack = [root]
    for line in state.splitlines():
        match = re.match(r'^(\s*)- (.*)$', line)
        if not match:
            continue
        n = {'line': match[2], 'children': [], 'indent': len(match[1])}
        while stack[-1]['indent'] >= n['indent']:
            stack.pop()
        stack[-1]['children'].append(n)
        stack.append(n)
    return root


def walk(node):
    for c in node['children']:
        yield c
        yield from walk(c)


def nodes(root, role, name=None):
    prefix = role + (' "' + name + '"' if name is not None else '')
    return [n for n in walk(root) if n['line'].startswith(prefix)
            and (len(n['line']) == len(prefix) or n['line'][len(prefix)] in ': [')]


def only(items):
    return items[0] if len(items) == 1 else None


def named_value(node):
    if node is None:
        return ABSENT
    line = node['line']
    m = re.search(r': (.+)$', line)
    if m:
        return m[1]
    values = []
    for c in node['children']:
        m = re.match(r'(?:text|generic): (.*)$', c['line'])
        if m:
            values.append(m[1])
        m = re.match(r'generic "(.*)"$', c['line'])
        if m:
            values.append(m[1])
    return values[0] if len(values) == 1 else ABSENT


def all_lines(node):
    return '\n'.join(n['line'] for n in walk(node))


def calendar_ui(state, dom):
    t = ax_tree(state)
    main = only(nodes(t, 'main'))
    if main is None:
        main = t
    out = {}
    for key, name, role in [('title','Title','textbox'),
                            ('availability','Show as','combobox'),
                            ('visibility','Visibility','combobox'),
                            ('recurrence','Recurrence','combobox')]:
        v = named_value(only(nodes(main, role, name)))
        if v is not ABSENT:
            out[key] = v
    for key, name in [('start_date', 'Start date'), ('end_date', 'End date')]:
        value = named_value(only(nodes(main, 'textbox', name)))
        if value is not ABSENT:
            try:
                value = dt.datetime.strptime(value, '%b %d, %Y').date().isoformat()
            except ValueError:
                pass
            out[key] = value
    check = only(nodes(main, 'checkbox', 'All day'))
    if check is not None:
        out['all_day'] = '[checked]' in check['line']
    guests = only(nodes(main, 'tabpanel', 'Guests'))
    if guests is not None:
        direct = guests['children']
        if (len(direct) == 2 and direct[0]['line'] == 'combobox "Guests"'
                and direct[1]['line'].startswith('group "Guest permissions"')):
            out['guests'] = []
    location = only(nodes(main, 'combobox', 'Add location'))
    if location is not None and not location['children'] and location['line'] == 'combobox "Add location"':
        out['location'] = ''
    if only(nodes(main, 'button', 'Add Google Meet video conferencing')) is not None:
        out['conference'] = False
    notice = only(nodes(main, 'list', 'Notifications'))
    if notice is not None and not notice['children'] and only(nodes(main,'button','Add notification')) is not None:
        out['reminders'] = []
    if type(dom) is dict and dom.get('tag') == 'DIV' and dom.get('role') == 'textbox' and dom.get('contenteditable') == 'true':
        text = dom.get('innerText', ABSENT)
        # The contract compares visible native text. DOM serialization markup
        # is diagnostic and must not impose an extra HTML-equality requirement.
        if type(text) is str:
            out['description'] = text
    return out


def notion_ui(state, dom):
    t = ax_tree(state)
    out = {}
    props = only(nodes(t, 'table', 'Page properties'))
    if props is not None:
        row = only(nodes(props, 'row', 'Marker'))
        if row is not None:
            bs = nodes(row, 'button')
            if len(bs) == 1:
                match = re.match(r'button "(.*)"(?: \[[^]]+\])?:?$', bs[0]['line'])
                if match:
                    out['marker'] = '' if match[1] == 'Empty' else match[1]
        row = only(nodes(props, 'row', 'Verified'))
        if row is not None:
            check = only(nodes(row, 'checkbox'))
            if check is not None:
                out['verified'] = '[checked]' in check['line']
    if 'Press ‘enter’ to continue with an empty page, or' in state:
        out['body_empty'] = True
    # Both the saved banner and the read-only title text must support the title.
    title = None
    if type(dom) is dict:
        for k in ('raw_title', 'title', 'innerText', 'textContent'):
            if type(dom.get(k)) is str:
                title = dom[k]
                break
    banner = only(nodes(t, 'banner'))
    if title is not None and banner is not None:
        if title in all_lines(banner):
            out['title'] = title
    return out


def field_statuses(service, token, ui, event=None):
    checks = {}
    if service == 'Notion':
        expected = dict(title=token, marker=token, verified=False, body_empty=True)
        return {'ui.'+k:compare(ui.get(k,ABSENT), v) for k,v in expected.items()}
    expected = dict(title=token, all_day=True, availability='Free', visibility='Private',
                    recurrence='Does not repeat', guests=[], location='', conference=False, reminders=[])
    checks.update({'ui.'+k:compare(ui.get(k,ABSENT),v) for k,v in expected.items()})
    checks['ui.description'] = marker(ui.get('description',ABSENT),token)
    for k in ('start_date','end_date'):
        checks['ui.'+k] = calendar_date(ui.get(k,ABSENT),'2026-10-14')
    event = event if type(event) is dict else {}
    for k,v in dict(summary=token,status='confirmed',attendees=[],transparency='transparent',visibility='private').items():
        checks['connector.'+k] = compare(event.get(k,ABSENT),v)
    checks['connector.description'] = marker(event.get('description',ABSENT),token,True)
    checks['connector.start'] = calendar_date(event.get('start',ABSENT),'2026-10-14T00:00:00',True)
    checks['connector.end'] = calendar_date(event.get('end',ABSENT),'2026-10-15T00:00:00',True)
    for k,kind in [('location',str),('hangout_link',str),('recurrence',list),('recurring_event_id',str)]:
        v = event.get(k,ABSENT)
        checks['connector.'+k] = (UNKNOWN if v is ABSENT or (v is not None and type(v) != kind)
                                  else MATCH if v is None or v == kind() else MISMATCH)
    v = event.get('reminders',ABSENT)
    checks['connector.reminders'] = (aggregate([compare(v.get('use_default',ABSENT),False),
                                       compare(v.get('overrides',ABSENT),[])]) if type(v) is dict else UNKNOWN)
    return checks


def notion_table(state):
    tree = ax_tree(state)
    main = only(nodes(tree,'main'))
    bad = ('progressbar' in state or 'region "Side Peek"' in state or 'menuitem' in state)
    if main is None or bad:
        return {'ready':False,'count':None,'titles':[]}
    child = main['children']
    ready = (only(nodes(main,'tab','Table')) is not None
             and 'tab "Table" [selected]' in all_lines(main)
             and all(only(nodes(main,'button',n)) is not None for n in ['Name','New page','Filter','Search'])
             and only(nodes(main,'table','Page properties')) is None)
    direct_checks = [i for i,n in enumerate(child) if n['line'].startswith('checkbox')]
    if not ready or not direct_checks:
        return {'ready':False,'count':None,'titles':[]}
    header_end=direct_checks[1] if len(direct_checks)>1 else len(child)
    header=child[direct_checks[0]+1:header_end]
    if not all(sum(n['line'].startswith('button "'+name+'"') for n in header)==1 for name in ['Name','Marker','Verified']):
        return {'ready':False,'count':None,'titles':[]}
    # The first direct checkbox is the column header selection control. A row
    # starts at each later direct checkbox. Verified checkboxes are nested.
    starts = direct_checks[1:]
    titles = []
    for i,start in enumerate(starts):
        end = starts[i+1] if i+1 < len(starts) else len(child)
        row = child[start+1:end]
        buttons = [n for n in row if n['line'].startswith('button')]
        if not buttons:
            return {'ready':False,'count':None,'titles':titles}
        # The first row button is Name. A same-text Marker button is a field.
        m = re.match(r'button "(.*)"(?: \[[^]]+\])?:?$',buttons[0]['line'])
        titles.append(m[1] if m else '')
    return {'ready':True,'count':len(starts),'titles':titles}


def calendar_table(state):
    tree=ax_tree(state)
    main=only(nodes(tree,'main'))
    if main is None or 'progressbar' in state or 'Searching' in state:
        return {'ready':False,'count':None,'titles':[]}
    headings=[n for n in nodes(main,'heading') if 'Search results.' in n['line']]
    if len(headings)!=1:
        return {'ready':False,'count':None,'titles':[]}
    line=headings[0]['line']
    if 'No events found.' in line:
        return {'ready':True,'count':0,'titles':[]}
    m=re.search(r'Search results\. (\d+) events? found\.',line)
    if not m:
        return {'ready':False,'count':None,'titles':[]}
    count=int(m[1])
    tokens=re.findall(r'FIELD-CHECK-20261015-C\d{2}',all_lines(main))
    return {'ready':True,'count':count,'titles':list(dict.fromkeys(tokens))}


def start_time(r):
    value=r.get('start_utc') or r.get('started_at_utc') or r.get('at_utc') or ''
    return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(dt.timezone.utc).isoformat(timespec='microseconds') if value else ''


def end_time(r):
    value=r.get('end_utc') or r.get('ended_at_utc') or r.get('at_utc') or ''
    return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(dt.timezone.utc).isoformat(timespec='microseconds') if value else ''


def seconds(a,b):
    return (dt.datetime.fromisoformat(b.replace('Z','+00:00'))-
            dt.datetime.fromisoformat(a.replace('Z','+00:00'))).total_seconds()


def record_kind(r):
    return r.get('kind') or r.get('type')


def record_label(r):
    return r.get('label') or r.get('action') or ''


class Evidence:
    def __init__(self, root, group):
        self.root = Path(root)
        raw = self.root/group
        if raw.is_dir():
            self.records = {str(p.relative_to(raw)):json.loads(p.read_text())
                            for p in raw.rglob('*.json')}
            self.actions = [json.loads(s) for s in (raw/'actions.jsonl').read_text().splitlines()]
        else:
            self.records = json.loads((self.root/('field_'+group+'_records.json')).read_text())
            if 'records' in self.records and isinstance(self.records['records'],dict):
                self.records = self.records['records']
            self.actions = [json.loads(s) for s in (self.root/('field_'+group+'_actions.jsonl')).read_text().splitlines()]
        self.byid = {r['record_id']:r for r in self.actions}
        self.packets = {v['trial_id']:v for n,v in self.records.items()
                        if isinstance(v,dict) and 'checkpoints' in v and 'trial_id' in v}

    def get(self, rid):
        return self.byid.get(rid,{})


def parsed_identity(record, service):
    for k in ('url','href','native_id','first_native_id'):
        v = record.get(k)
        if isinstance(v,str):
            ident = native_id(v,service)
            if ident:
                return ident
    return None


def check_stage(evidence, packet, name):
    cp = packet['checkpoints'][name]
    service,token = packet['service'],packet['token']
    native = evidence.get(cp.get('native_state_id'))
    value = evidence.get(cp.get('native_value_read_id'))
    cover = evidence.get(cp.get('covered_state_id'))
    check = evidence.get(cp.get('field_check_record_id'))
    rows = [r for r in evidence.actions if r.get('trial_id') == packet['trial_id']]
    cutoff = start_time(check)
    prior = [r for r in rows if end_time(r) < cutoff]
    mutations = [r for r in prior if record_kind(r)=='action' and
        ((service=='Calendar' and record_label(r) in ('create_save','repair_save')) or
         (service=='Notion' and r.get('phase') in ('entry','repair') and
          not any(x in record_label(r).lower() for x in ('wait','reload','read','navigate','navigation','open'))))]
    # N01 has stale phase labels. Its only admitted Create remains the cutoff.
    mutations += [evidence.get(rid) for rid in packet.get('create_action_ids',[])
                  if evidence.get(rid) and end_time(evidence.get(rid)) < cutoff]
    last_write = max(mutations,key=end_time) if mutations else {}
    last_end = end_time(last_write)
    ns,cs = native.get('state',''),cover.get('state','')
    table = calendar_table(cs) if service=='Calendar' else notion_table(cs)
    vals = value.get('value',{}) if service=='Calendar' else value
    ui = calendar_ui(ns,vals) if service=='Calendar' else notion_ui(ns,vals)
    event = {}
    data=[]
    service_ok,service_fresh = True,True
    service_ids=[]
    connector_inputs=[]
    if service=='Calendar':
        data=[evidence.records.get(n,{}) for n in cp.get('connector_files',[])]
        reads=[r for r in data if 'read_event' in r.get('tool','')]
        searches=[r for r in data if 'search_events' in r.get('tool','')]
        event=reads[0].get('result',{}).get('structuredContent',{}) if len(reads)==1 else {}
        scope=[]
        for r in searches:
            a=r.get('args',{});out=r.get('result',{});sc=out.get('structuredContent',{})
            scope.append(a.get('calendar_id')=='primary' and a.get('query')==token
                         and a.get('time_min')=='2026-10-01T00:00:00-04:00'
                         and a.get('time_max')=='2026-11-01T00:00:00-04:00'
                         and out.get('isError') is False and sc.get('next_page_token',ABSENT) is None
                         and isinstance(sc.get('events'),list))
            service_ids.extend(x.get('id') for x in sc.get('events',[]) if isinstance(x,dict))
        service_ok=(len(reads)==1 and len(searches)==1 and all(scope)
                    and reads[0].get('result',{}).get('isError') is False
                    and reads[0].get('args',{}).get('calendar_id')=='primary'
                    and reads[0].get('args',{}).get('event_id')==event.get('id'))
        service_fresh=bool(data) and all(last_end < start_time(r) and end_time(r) <= cutoff for r in data)
        connector_inputs=cp.get('connector_files',[])
    checks=field_statuses(service,token,ui,event)
    first=packet.get('first_native_id')
    if isinstance(first,str) and ('/' in first or '?' in first):
        first=native_id(first,service)
    current=parsed_identity(native,service)
    identities=[]
    identity_witnesses=[]
    row_identity_sets=[]
    identity_sources_valid=True
    for rid in cp.get('covered_identity_record_ids',[]):
        rec=evidence.get(rid);ident=parsed_identity(rec,service)
        sid=rec.get('source_state_id') or rec.get('source_state')
        witness=evidence.get(sid) if sid else {}
        if service=='Calendar' and record_kind(rec)=='visible_row_identities':
            row_ids=[native_id('/eventedit/'+r.get('event_id_attribute',''),service) for r in rec.get('rows',[])]
            supported=(sid==cp.get('covered_state_id') and bool(row_ids) and all(row_ids)
                       and len(row_ids)==table['count'] and end_time(witness)<=start_time(rec)<=end_time(rec)<=cutoff
                       and all(token in r.get('label','') and r.get('label','') in witness.get('state','') for r in rec.get('rows',[])))
            row_identity_sets.append(set(row_ids) if supported else None)
            identity_sources_valid &= bool(supported)
            identity_witnesses.append(dict(record_id=rid,declared_source=sid,used_source=sid,
                                           visible_row_identities=True,rendered_rows=len(row_ids),
                                           distinct_ids=sorted(set(row_ids)) if all(row_ids) else [],supported=bool(supported)))
            continue
        # A captured native link must occur in its cited snapshot or have the
        # same native URL. Identity text alone does not prove a link was read.
        href=rec.get('href') or rec.get('url') or rec.get('native_id')
        supported=(isinstance(href,str) and bool(witness)
                   and (href in witness.get('state','') or parsed_identity(witness,service)==ident))
        used=sid
        copy=evidence.get(rec.get('copy_action_id'))
        before_copy=evidence.get(copy.get('before') or copy.get('before_state'))
        clipboard_witness=(service=='Notion' and not supported and bool(ident)
                           and record_kind(copy)=='action' and not copy.get('error')
                           and 'copy' in record_label(copy).lower()
                           and 'option "Copy link"' in before_copy.get('state','')
                           and 'button "1 selected"' in before_copy.get('state','')
                           and token in before_copy.get('state','')
                           and 'Copied page link to clipboard' in witness.get('state','')
                           and end_time(copy)<=start_time(witness)<=end_time(witness)<=start_time(rec))
        if clipboard_witness:
            supported=True
        # A URL read can race the immediate snapshot. A later cited, ready
        # native snapshot before this decision can prove the same URL. Keep
        # this alternate witness explicit; never rewrite the old citation.
        alternate=(not supported and service=='Calendar' and ident is not None
                   and parsed_identity(native,service)==ident
                   and end_time(rec)<=start_time(native)<=end_time(native)<=cutoff)
        if alternate:
            supported=True
            used=native.get('record_id')
        identity_witnesses.append(dict(record_id=rid,declared_source=sid,used_source=used,
                                       later_native_witness=bool(alternate),clipboard_witness=bool(clipboard_witness),
                                       copy_action_id=rec.get('copy_action_id'),supported=bool(supported)))
        identity_sources_valid &= bool(ident) and supported and end_time(rec) <= cutoff
        identities.append(ident)
    if service=='Calendar':
        operation_ids=service_ids
        identity_sources_valid &= set(identities)==set(service_ids)
        if row_identity_sets:
            identity_sources_valid &= all(ids==set(service_ids) for ids in row_identity_sets)
    else:
        operation_ids=identities
    record_count=table['count']
    if service=='Calendar' and row_identity_sets and identity_sources_valid:
        record_count=len(set(service_ids))
    tree=ax_tree(ns)
    if service=='Calendar':
        native_ready=all(only(nodes(tree,r,n)) is not None for r,n in
                         [('heading','Event edit page'),('textbox','Title'),('textbox','Start date'),
                          ('textbox','End date'),('checkbox','All day'),('textbox','Description')])
        pending=bool(nodes(tree,'dialog') or nodes(tree,'menu'))
    else:
        native_ready=only(nodes(tree,'banner')) is not None and only(nodes(tree,'table','Page properties')) is not None
        dialogs=nodes(tree,'dialog')
        pending=bool(nodes(tree,'region','Side Peek') or nodes(tree,'menu') or
                     any(not n['line'].startswith('dialog "Turn on Writing Replay"') for n in dialogs))
    native_ready &= 'progressbar' not in ns and not pending
    same_tab_reloads=[r for r in prior if record_kind(r)=='action' and 'reload' in record_label(r).lower()
                      and not r.get('error') and last_end < start_time(r) <= end_time(r) <= start_time(native)
                      and (service=='Notion' or r.get('tab_role')==native.get('tab_role'))
                      and ('native' in record_label(r).lower() or 'saved' in record_label(r).lower())]
    native_fresh=bool(native) and last_end < start_time(native) <= end_time(native) <= cutoff and bool(same_tab_reloads)
    dom_source=value.get('source_state') or value.get('source_state_id')
    value_fresh=(bool(value) and dom_source==cp.get('native_state_id')
                 and end_time(native)<=start_time(value)<=end_time(value)<=cutoff)
    if not value_fresh:
        checks['ui.description' if service=='Calendar' else 'ui.title']=UNKNOWN
    coverage_fresh=bool(cover) and last_end < start_time(cover) <= end_time(cover) <= cutoff
    if service=='Calendar':
        url=cover.get('url','')
        query=parse_qs(urlsplit(url).query)
        scope_covered=(query.get('q')==[token] and query.get('start')==['20261001'] and query.get('end')==['20261031'])
    else:
        scope_covered=table['ready'] and 'Filter:' not in cs and 'Sort:' not in cs
    gates=dict(native_ready=bool(native_ready),native_fresh=native_fresh,
               coverage_ready=table['ready'],coverage_fresh=coverage_fresh,
               scope_covered=scope_covered,service_ready=service_ok,service_fresh=service_fresh,
               no_pending_edit=not pending)
    if name!='initial':
        barrier=(end_time(evidence.get(packet['checkpoints']['initial']['field_check_record_id']))
                 if name=='final' else end_time(evidence.get(packet.get('final_decision_record_id'))))
        required=[native,value,cover]+data
        gates['new_checkpoint_reads']=bool(barrier) and all(r and start_time(r)>barrier for r in required)
    identity=dict(first=first,ui=current,service=event.get('id') if service=='Calendar' else None,
                  operation_ids=operation_ids,source_links_valid=identity_sources_valid,
                  witnesses=identity_witnesses)
    checks['identity.first']=MATCH if isinstance(first,str) and bool(first) else UNKNOWN
    checks['identity.ui']=compare(current,first) if first and current else UNKNOWN
    if service=='Calendar':
        checks['identity.service']=compare(event.get('id',ABSENT),first) if first else UNKNOWN
    checks['identity.coverage']=(UNKNOWN if not first or not identity_sources_valid or any(not x for x in operation_ids)
                                or len(set(operation_ids))!=len(operation_ids)
                                else MATCH if operation_ids==[first] else MISMATCH)
    checks['coverage.count']=UNKNOWN if record_count is None else MATCH if record_count==len(operation_ids) else MISMATCH
    status=aggregate(checks.values()) if all(gates.values()) else UNKNOWN
    baseline=(UNKNOWN if not table['ready'] or not coverage_fresh or not scope_covered
              or type(ui.get('title')) is not str or not identity_sources_valid
              or any(type(x) is not str or not x for x in operation_ids)
              or len(set(operation_ids))!=len(operation_ids) or record_count!=len(operation_ids)
              else MATCH if len(operation_ids)==1 and ui['title']==token else MISMATCH)
    online_fields={}
    if isinstance(check.get('per_field_checks'),dict):
        online_fields={k:v.get('status') for k,v in check['per_field_checks'].items() if isinstance(v,dict)}
    elif isinstance(check.get('per_field_statuses'),dict):
        online_fields={k if '.' in k else 'ui.'+k:v for k,v in check['per_field_statuses'].items()}
    return dict(status=status,field_statuses=checks,ui=ui,
                connector_values={k:event[k] for k in ('summary','description','start','end','transparency') if k in event},
                identity=identity,gates=gates,
                count=record_count,rendered_rows=table['count'],titles=table['titles'],baseline=baseline,
                source_ids={k:cp.get(k) for k in ('native_state_id','native_value_read_id','covered_state_id','field_check_record_id')},
                connector_inputs=connector_inputs,last_mutation_id=last_write.get('record_id'),
                recorded_status=check.get('overall'),recorded_field_statuses=online_fields,
                writing_prompt='dialog "Turn on Writing Replay"' in ns)


def check_trial(e, packet):
    tid,service,condition=packet['trial_id'],packet['service'],packet['condition']
    rows=[r for r in e.actions if r.get('trial_id')==tid]
    phases={n:check_stage(e,packet,n) for n in ('initial','final','audit')}
    admissions={k:[r for r in rows if record_kind(r) in ('mutation_admission','mutation_admitted')
                   and r.get('mutation_kind')==k] for k in ('create','repair')}
    creates=[r for r in rows if record_kind(r)=='action' and
             ((service=='Calendar' and record_label(r)=='create_save') or
              (service=='Notion' and (record_label(r).endswith('Create once') or record_label(r)=='create assigned record')))]
    repairs=[r for r in rows if record_kind(r)=='action' and
             ((service=='Calendar' and record_label(r)=='repair_save') or
              (service=='Notion' and bool(re.search(r'(?:repair Marker full value once|full Marker repair once|set Verified false once)$',record_label(r)))))]
    decision=e.get(packet.get('final_decision_record_id'))
    elapsed=seconds(start_time(admissions['create'][0]),start_time(decision)) if len(admissions['create'])==1 and decision else None
    issues=[]
    observed_first_records=[r for r in rows if record_kind(r)=='native_identity' and parsed_identity(r,service)]
    observed_first=(parsed_identity(observed_first_records[0],service) if observed_first_records else None)
    if observed_first != packet.get('first_native_id'):
        issues.append('packet_first_identity_not_earliest_observed_identity')
    for k,rs in [('create',creates),('repair',repairs)]:
        declared=packet.get(k+'_action_ids',[])
        if [r.get('record_id') for r in rs] != declared:
            issues.append(k+'_action_list_mismatch')
        if [r['record_id'] for r in admissions[k]] != packet.get(k+'_admission_ids',[]):
            issues.append(k+'_admission_list_mismatch')
        if len(admissions[k]) != len(rs):
            issues.append(k+'_admission_action_count_mismatch')
        if any(not r or record_kind(r)!='action' for r in rs):
            issues.append(k+'_action_reference_invalid')
        if any(start_time(a)>start_time(r) for a,r in zip(admissions[k],rs)):
            issues.append(k+'_reservation_after_action')
    if len(creates)!=1 or len(repairs)>1:
        issues.append('mutation_budget')
    field_keys={'wrong_availability':['ui.availability','connector.transparency'],
                'wrong_marker':['ui.description','connector.description'] if service=='Calendar' else ['ui.marker'],
                'empty_marker':['ui.description','connector.description'] if service=='Calendar' else ['ui.marker'],
                'wrong_date':['ui.start_date','ui.end_date','connector.start','connector.end'],
                'wrong_end':['ui.end_date','connector.end'],
                'wrong_checkbox':['ui.verified']}
    initial=phases['initial'];final=phases['final'];audit=phases['audit']
    target_statuses={k:initial['field_statuses'][k] for k in field_keys.get(condition,[])}
    nontarget_statuses={k:v for k,v in initial['field_statuses'].items()
                       if k.startswith(('ui.','connector.')) and k not in target_statuses}
    u=initial['ui'];v=initial['connector_values'];t=packet['token']
    observed_description=v.get('description')
    normalized_description=observed_description.rstrip('\r\n') if type(observed_description) is str else None
    if service=='Notion':
        exposed=({'wrong_checkbox':u.get('verified') is True,
                  'wrong_marker':u.get('marker')==t+'-WRONG',
                  'empty_marker':u.get('marker')==''}.get(condition,False))
    else:
        exposed=({'wrong_availability':u.get('availability')=='Busy' or v.get('transparency')=='opaque',
                  'wrong_marker':u.get('description')==t+'-WRONG' or normalized_description==t+'-WRONG',
                  'empty_marker':u.get('description')=='' or normalized_description=='',
                  'wrong_date':(u.get('start_date')==u.get('end_date')=='2026-10-13') or
                               (v.get('start')=='2026-10-13T00:00:00' and v.get('end')=='2026-10-14T00:00:00'),
                  'wrong_end':u.get('end_date')=='2026-10-15' or v.get('end')=='2026-10-16T00:00:00'}.get(condition,False))
    exposed=exposed and all(initial['gates'].values())
    detected=exposed and initial['status']==MISMATCH
    same_id=bool(packet.get('first_native_id')) and all(p['identity']['ui']==packet['first_native_id'] for p in phases.values())
    if repairs:
        ir=e.get(packet['checkpoints']['initial']['field_check_record_id'])
        if end_time(ir)>=start_time(admissions['repair'][0]) or initial['status']!=MISMATCH or not exposed:
            issues.append('repair_without_prior_supported_target_mismatch')
        if not same_id:
            issues.append('repair_identity_not_supported')
        for repair in repairs:
            before=e.get(repair.get('before') or repair.get('before_state'))
            if parsed_identity(before,service) != observed_first:
                issues.append('repair_action_before_state_identity_unresolved')
    if decision.get('field_check_record_id') != packet['checkpoints']['final']['field_check_record_id']:
        issues.append('decision_final_reference')
    if start_time(decision)<end_time(e.get(packet['checkpoints']['final']['field_check_record_id'])):
        issues.append('decision_before_final_check')
    if start_time(e.get(packet['checkpoints']['audit']['field_check_record_id']))<=end_time(decision):
        issues.append('audit_not_later')
    confirm=decision.get('decision')=='CONFIRM'
    if confirm and (final['status']!=MATCH or elapsed is None or elapsed>300):
        issues.append('unsupported_final_confirmation')
    cleanup=[e.get(rid) for rid in packet.get('cleanup_record_ids',[])]
    cleanup_states=[r for r in cleanup if r.get('state')]
    cleanup_writes=[r for r in rows if record_kind(r)=='action' and r.get('phase')=='cleanup'
                    and (record_label(r)=='delete_to_recoverable_trash'
                         or re.search(r'move .*trash',record_label(r),re.I))]
    cleanup_barrier=max([end_time(decision)]+[end_time(r) for r in cleanup_writes])
    for r in cleanup:
        for k in ('source_state_id','source_state','after_state','after','covered_state_id','native_state_id',
                  'parent_zero_source_id','native_trash_source_id'):
            if e.get(r.get(k)).get('state'):
                cleanup_states.append(e.get(r[k]))
    zeros=[]
    for r in cleanup_states:
        table=calendar_table(r['state']) if service=='Calendar' else notion_table(r['state'])
        if table['ready'] and table['count']==0 and start_time(r)>cleanup_barrier:
            zeros.append(r['record_id'])
    connector_zero=None
    if service=='Calendar':
        raw=e.records.get(packet.get('cleanup_connector_file'),{})
        args=raw.get('args',{});result=raw.get('result',{});sc=result.get('structuredContent',{})
        connector_zero=(args.get('calendar_id')=='primary' and args.get('query')==packet['token']
                        and args.get('time_min')=='2026-10-01T00:00:00-04:00'
                        and args.get('time_max')=='2026-11-01T00:00:00-04:00'
                        and result.get('isError') is False and sc.get('events',ABSENT)==[]
                        and sc.get('next_page_token',ABSENT) is None and start_time(raw)>cleanup_barrier)
    restores=[r['record_id'] for r in cleanup_states if 'button "Restore page"' in r.get('state','')
              and parsed_identity(r,service)==observed_first and start_time(r)>cleanup_barrier]
    errors=[r['record_id'] for r in rows if r.get('error') or record_kind(r) in ('runner_error','read_error')]
    return dict(trial_id=tid,service=service,condition=condition,phases=phases,
                first_identity_record_id=observed_first_records[0]['record_id'] if observed_first_records else None,
                creates=len(creates),repairs=len(repairs),same_identity=same_id,
                initial_injection_exposed=exposed,initial_target_statuses=target_statuses,
                initial_other_fields_match=bool(nontarget_statuses) and all(v==MATCH for v in nontarget_statuses.values()),
                detected_injected_error=detected,initial_baseline_false_match=exposed and initial['baseline']==MATCH,
                decision=decision.get('decision'),elapsed_seconds=elapsed,on_time=elapsed is not None and elapsed<=300,
                final_full_match=final['status']==MATCH,audit_full_match=audit['status']==MATCH,
                confirmed_clean=confirm and audit['status']==MATCH and final['status']==MATCH and elapsed is not None and elapsed<=300,
                false_confirmation=confirm and audit['status']==MISMATCH,
                unknown_confirmation=confirm and audit['status']==UNKNOWN,
                extra_record_case=audit['count'] is not None and audit['count']>1,
                cleanup_browser_zero=bool(zeros),cleanup_browser_sources=sorted(set(zeros)),
                cleanup_connector_zero=connector_zero,cleanup_restore_sources=sorted(set(restores)),
                errors=errors,procedure_issues=issues)


def check_calendar_prefix_cleanup(e):
    result=e.records.get('final-prefix-cleanup.json',{})
    args=result.get('args',{});reply=result.get('result',{});data=reply.get('structuredContent',{})
    writes=[r for r in e.actions if record_kind(r)=='action' and record_label(r)=='delete_to_recoverable_trash']
    barrier=max((end_time(r) for r in writes),default='')
    native=[]
    for r in e.actions:
        if r.get('trial_id')!='RUN-END' or not r.get('state') or start_time(r)<=barrier:
            continue
        query=parse_qs(urlsplit(r.get('url','')).query)
        count=calendar_table(r['state'])
        if (query.get('q')==['FIELD-CHECK-20261015-C'] and query.get('start')==['20261001']
            and query.get('end')==['20261031'] and count['ready'] and count['count']==0):
            native.append(r['record_id'])
    covered=(args.get('calendar_id')=='primary' and args.get('query')=='FIELD-CHECK-20261015-C'
             and args.get('time_min')=='2026-10-01T00:00:00-04:00'
             and args.get('time_max')=='2026-11-01T00:00:00-04:00')
    connector=bool(result) and reply.get('isError') is False and data.get('events',ABSENT)==[] and data.get('next_page_token',ABSENT) is None and start_time(result)>barrier
    return dict(source_file='final-prefix-cleanup.json',browser_zero_sources=native,
                scope_complete=covered,connector_zero=connector,supported=bool(native and covered and connector))


def check_parent_cleanup(e):
    """Check the empty Notion parent and its later recoverable Trash state."""
    records=[r for r in e.actions if record_kind(r)=='parent_cleanup']
    out=[]
    for record in records:
        zero=e.get(record.get('parent_zero_source_id'))
        trash=e.get(record.get('trash_source_id'))
        actions=[e.get(rid) for rid in record.get('trash_action_ids',[])]
        first_write=min((start_time(r) for r in actions),default='')
        last_write=max((end_time(r) for r in actions),default='')
        parent=record.get('native_id')
        table=notion_table(zero.get('state',''))
        same_parent=bool(parent) and parsed_identity(zero,'Notion')==parent and parsed_identity(trash,'Notion')==parent
        zero_supported=table['ready'] and table['count']==0 and end_time(zero)<first_write
        writes_supported=bool(actions) and all(record_kind(r)=='action' and not r.get('error')
                            and 'trash' in record_label(r).lower() and 'permanent' not in record_label(r).lower()
                            and parsed_identity(e.get(r.get('before') or r.get('before_state')),'Notion')==parent
                            for r in actions)
        reloads=[r for r in e.actions if record_kind(r)=='action' and r.get('phase')=='parent_cleanup'
                 and 'reload' in record_label(r).lower() and not r.get('error')
                 and last_write<start_time(r)<=end_time(r)<start_time(trash)]
        trash_supported=(bool(reloads) and 'button "Restore page"' in trash.get('state','')
                         and 'progressbar' not in trash.get('state','') and '- dialog' not in trash.get('state','')
                         and end_time(trash)<=start_time(record))
        out.append(dict(record_id=record.get('record_id'),parent_native_id=parent,
                        zero_source_id=zero.get('record_id'),trash_source_id=trash.get('record_id'),
                        trash_action_ids=[r.get('record_id') for r in actions],
                        reload_ids=[r.get('record_id') for r in reloads],
                        same_parent=same_parent,empty_before_trash=bool(zero_supported),
                        action_sequence_supported=bool(writes_supported),recoverable_trash=bool(trash_supported),
                        supported=bool(same_parent and zero_supported and writes_supported and trash_supported)))
    return out


def native_id(url, service):
    if not isinstance(url,str):
        return None
    # Public extraction uses stable aliases in place of private URL components.
    if service == 'Calendar':
        m = re.search(r'/eventedit/([^/?#]+)',url)
        if not m:
            return None
        encoded = unquote(m[1])
        if encoded.startswith(('record-', 'CAL_', 'CAL-', 'calendar-')):
            return encoded
        try:
            return base64.urlsafe_b64decode(encoded + '=' * (-len(encoded)%4)).decode().split(' ')[0]
        except (ValueError,UnicodeDecodeError):
            return None
    last = urlsplit(url).path.rstrip('/').split('/')[-1]
    m = re.search(r'([0-9a-f]{32})$',last)
    if m:
        return m[1]
    alias_match=re.search(r'(record-[0-9a-f]{20})$',last)
    if alias_match:
        return alias_match[1]
    return last if last.startswith(('NOTION_', 'NOTION-', 'notion-')) else None


def self_check():
    assert marker('X\r\n','X',True) == MATCH
    assert marker('X ','X',True) == MISMATCH
    assert marker('X\n','X') == MISMATCH
    assert marker('<b>X</b>','X',True) == UNKNOWN
    assert calendar_date('2026-10-15T00:00:00Z','2026-10-15T00:00:00',True) == UNKNOWN
    assert calendar_date('2026-10-16T00:00:00','2026-10-15T00:00:00',True) == MISMATCH
    assert compare(0,False) == UNKNOWN
    assert aggregate([MATCH,UNKNOWN,MISMATCH]) == MISMATCH


if __name__ == '__main__':
    self_check()
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--plan-dir',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    plan=args.plan_dir or args.input_dir
    assignments=list(csv.DictReader((plan/'field_assignments.csv').open()))
    trials=[]
    parent_cleanup=[]
    scored_mutations=[]
    packets={}
    for group in ('calendar_runner','notion_runner'):
        e=Evidence(args.input_dir,group)
        trials.extend(check_trial(e,p) for _,p in sorted(e.packets.items()))
        packets.update(e.packets)
        scored_mutations.extend(r for r in e.actions if record_kind(r) in ('mutation_admission','mutation_admitted'))
        if group=='notion_runner':
            parent_cleanup=check_parent_cleanup(e)
        else:
            prefix_cleanup=check_calendar_prefix_cleanup(e)
    trials.sort(key=lambda r:r['trial_id'])
    byid={r['trial_id']:r for r in trials}
    manifest=json.loads((plan/'field_plan_manifest.json').read_text())
    frozen={n:hashlib.sha256((plan/n).read_bytes()).hexdigest()==h for n,h in manifest['sha256'].items()}
    online_differences=[dict(trial_id=r['trial_id'],phase=n,online=p['recorded_status'],independent=p['status'])
                        for r in trials for n,p in r['phases'].items() if p['recorded_status']!=p['status']]
    field_differences=[dict(trial_id=r['trial_id'],phase=n,field=k,online=p['recorded_field_statuses'].get(k),independent=v)
                       for r in trials for n,p in r['phases'].items() for k,v in p['field_statuses'].items()
                       if k.startswith(('ui.','connector.')) and p['recorded_field_statuses'].get(k)!=v]
    totals=dict(assigned=len(assignments),packets=len(trials),
                creates=sum(r['creates'] for r in trials),repairs=sum(r['repairs'] for r in trials),
                verified_wrong_cases=sum(r['initial_injection_exposed'] for r in trials),
                detected_wrong_cases=sum(r['detected_injected_error'] for r in trials),
                correct_controls=sum(r['condition']=='correct' for r in trials),
                correct_control_initial_match=sum(r['condition']=='correct' and r['phases']['initial']['status']==MATCH and r['repairs']==0 for r in trials),
                confirmed_clean=sum(r['confirmed_clean'] for r in trials),
                unresolved=sum(r['decision']=='UNRESOLVED' for r in trials),
                on_time=sum(r['on_time'] for r in trials),
                final_matches=sum(r['final_full_match'] for r in trials),
                audit_matches=sum(r['audit_full_match'] for r in trials),
                baseline_false_matches=sum(r['initial_baseline_false_match'] for r in trials),
                false_confirmations=sum(r['false_confirmation'] for r in trials),
                unknown_confirmations=sum(r['unknown_confirmation'] for r in trials),
                extra_record_cases=sum(r['extra_record_case'] for r in trials),
                active_zero_cleanup=sum(r['cleanup_browser_zero'] and r['cleanup_connector_zero'] is not False for r in trials))
    out=dict(review_method='Separate source parser; no import of checker, runner, or main analyzer.',
             status='COMPLETE' if len(trials)==len(assignments) else 'PARTIAL',totals=totals,
             missing_trials=[a['trial_id'] for a in assignments if a['trial_id'] not in byid],
             frozen_hashes_match=frozen,online_status_differences=online_differences,trials=trials)
    out['online_field_differences']=field_differences
    out['parent_cleanup']=parent_cleanup
    out['calendar_prefix_cleanup']=prefix_cleanup
    out['assignment_checks']={a['trial_id']:all(str(packets.get(a['trial_id'],{}).get(k))==a[k] for k in ('service','condition','token')) for a in assignments}
    frozen_time=start_time({'at_utc':manifest['frozen_utc']})
    out['freeze_before_all_scored_admissions']=bool(scored_mutations) and all(start_time(r)>frozen_time for r in scored_mutations)
    earliest=min(scored_mutations,key=start_time) if scored_mutations else {}
    out['first_scored_admission']={'record_id':earliest.get('record_id'),'time_utc':start_time(earliest)}
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'totals':totals,'online_status_differences':online_differences,
                      'online_field_differences':field_differences,
                      'procedure_issues':{r['trial_id']:r['procedure_issues'] for r in trials if r['procedure_issues']}}))
