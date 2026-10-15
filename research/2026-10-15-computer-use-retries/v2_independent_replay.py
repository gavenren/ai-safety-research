#!/usr/bin/env python3
"""Independent evidence check. Standard library only; no main-analysis imports or network."""
import argparse, collections, csv, hashlib, html, json, re
from datetime import datetime
from pathlib import Path

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def kind(r): return r.get('kind',r.get('type'))
def label(r): return r.get('action',r.get('label',''))
def start(r): return r.get('started_at_utc',r.get('start_utc',''))
def end(r): return r.get('ended_at_utc',r.get('end_utc',start(r)))
def dt(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
def rid(v):
 m=re.search(r'record-[a-f0-9]{20}',str(v));return m.group() if m else None

def notion_table(r):
 s=r.get('state',''); required=['- banner:', 'button "Private"','button "Share"','button "Actions"','button "Settings"','button "Automations"','button "Name"']
 if not all(x in s for x in required) or any(x in s for x in ['progressbar','Side Peek','- dialog','- menu','\n- table:']):return None
 m=re.search(r'tab "(All|Hidden)" \[selected\]',s)
 if not m:return None
 a=s.split('  - button "Name"',1)[1].split('  - button "New page"',1)[0]
 # Each complete data row has a same-level checkbox and following same-level button.
 titles=[]
 lines=a.splitlines()
 for i,l in enumerate(lines):
  if l=='  - checkbox' or l.startswith('  - checkbox [checked]'):
   following=next((q for q in lines[i+1:] if q.startswith('  - ')),None)
   if following is None or not following.startswith('  - button'):return None
   t=re.match(r'  - button(?: "([^"]*)")?',following);titles.append(t.group(1) or '')
 if not titles and 'checkbox [disabled]' not in s:return None
 return {'scope':m.group(1),'titles':titles,'record_id':r['record_id']}

def notion_native(r):
 s=r.get('state','');u=r.get('url','')
 if 'table "Page properties"' not in s or 'progressbar' in s or 'Side Peek' in s:return None
 if not rid(u) or '?v=' in u:return None
 b=s.split('- main:',1)[0]
 m=re.search(r'  - generic: /\n  - button "([^"]*)"',b)
 if not m:return None
 return {'id':rid(u),'title':'' if m.group(1)=='New page' else m.group(1),
         'prompt':'dialog "Turn on Writing Replay"' in s,'record_id':r['record_id'],
         'empty_body':'continue with an empty page' in s,
         'parent':'link "V2-RETRY-20261015"' in b}

def calendar_table(r,token):
 s=r.get('state','');u=r.get('url','')
 if not ('heading "Search results.' in s and 'combobox "Search"' in s):return None
 if any(x in s for x in ['progressbar','Searching','- dialog','Event edit page']):return None
 if token not in s or not ('start=20261001&end=20261031' in u or 'start=20271001&end=20271031' in u):return None
 titles=[]
 for l in s.splitlines():
  if re.match(r'\s*- row "',l):
   m=re.search(r'(V2-RETRY-20261015-[CN]\d{2}(?:-DRAFT)?)',l)
   if m:titles.append(m.group(1))
 if not titles and 'No results found' not in s:return None
 return {'scope':'Hidden' if 'start=20271001' in u else 'All','titles':titles,'record_id':r['record_id']}

def calendar_editor(r,token):
 s=r.get('state','')
 if 'heading "Event edit page"' not in s or not rid(r.get('url')) or 'progressbar' in s:return None
 m=re.search(r'textbox "Title"[^\n]*\n(?:[^\n]*\n)*?\s+- text: ([^\n]+)',s)
 title=m.group(1) if m else None
 checks={'all_day':'checkbox "All day" [checked]' in s,
         'dates':'textbox "Start date": Oct 14, 2026' in s and 'textbox "End date": Oct 14, 2026' in s,
         'free':bool(re.search(r'combobox "Show as"[^\n]*\n\s+- generic: Free',s)),
         'private':bool(re.search(r'combobox "Visibility"[^\n]*\n\s+- generic(?: "Private"|: Private)',s)),
         'nonrecurring':'generic "Does not repeat"' in s,
         'empty_location':bool(re.search(r'^\s+- combobox "Add location"$',s,re.M)),
         'empty_guests':bool(re.search(r'^\s+- combobox "Guests"$',s,re.M)),
         'no_conference':'button "Add Google Meet video conferencing"' in s,
         'no_notifications':'list "Notifications"\n' in s and 'Remove notification' not in s}
 return {'id':rid(r['url']),'title':title,'checks':checks,'record_id':r['record_id']}

def actual_creates(rs,site):
 return [r for r in rs if kind(r)=='action' and ((site=='Calendar' and label(r)=='create') or (site=='Notion' and re.match(r'^(initial|repeat) New(?: |$)',label(r))))]
def actual_repairs(rs,site):
 return [r for r in rs if kind(r)=='action' and ((site=='Calendar' and label(r)=='save_repair_once') or (site=='Notion' and re.match(r'^assign (?:full )?exact title once',label(r))))]

def payload(x):
 if isinstance(x,dict) and isinstance(x.get('structuredContent'),dict):return x['structuredContent']
 return {}

def correct_query(d,token):
 q=d.get('args',{})
 return q.get('calendar_id')=='primary' and q.get('query')==token and q.get('time_min')=='2026-10-01T00:00:00-04:00' and q.get('time_max')=='2026-11-01T00:00:00-04:00'

def calendar_audit(path,rs,token,after):
 if not path.exists():return None
 d=json.loads(path.read_text());p=payload(d.get('result',{}));es=p.get('events')
 if not correct_query(d,token) or not isinstance(es,list) or 'next_page_token' not in p or p['next_page_token'] is not None:return None
 details=[payload(x.get('result',{})) for x in d.get('read_events',[])]
 if {e.get('id') for e in es}!={e.get('id') for e in details}:return None
 if len(es)!=len({e.get('id') for e in es}):return None
 fields=[]
 for e in details:
  required={'summary','description','start','end','transparency','visibility','attendees','reminders','recurrence','location','hangout_link'}
  missing=sorted(required-set(e))
  raw=e.get('description');normalized=html.unescape(re.sub('<[^>]*>','',raw or '')).strip()
  checks={'title':e.get('summary')==token,'start':e.get('start')=='2026-10-14T00:00:00','end':e.get('end')=='2026-10-15T00:00:00',
  'free':e.get('transparency')=='transparent','private':e.get('visibility')=='private','guests':e.get('attendees')==[],
  'reminders':e.get('reminders')=={'use_default':False,'overrides':[]},'recurrence':e.get('recurrence') in [None,[]],
  'location':e.get('location') in [None,''],'conference':e.get('hangout_link') in [None,'']}
  editors=[calendar_editor(r,token) for r in rs if kind(r)=='observation' and start(r)>=after and r.get('phase','').startswith('audit')]
  editors=[x for x in editors if x and x['id']==e.get('id')]
  browser=any(all(x['checks'].values()) and x['title']==e.get('summary') for x in editors)
  exact=raw==token
  state='pass' if all(checks.values()) and exact and browser and not missing else ('unknown' if all(checks.values()) and normalized==token and browser else 'fail')
  if missing:state='unknown'
  fields.append({'id':e.get('id'),'title':e.get('summary'),'description_literal':exact,'description_marker':normalized==token,
  'other_checks':checks,'browser_editor':browser,'browser_refs':[x['record_id'] for x in editors], 'status':state,'missing':missing})
 return {'count':len(es),'ids':sorted(e.get('id') for e in es),'titles':[e.get('summary') for e in es],'fields':fields,'field_status':'fail' if any(x['status']=='fail' for x in fields) else ('unknown' if any(x['status']=='unknown' for x in fields) else 'pass'),
 'normalized_fields_pass':all(all(x['other_checks'].values()) and x['description_marker'] and x['browser_editor'] and not x['missing'] for x in fields),
 'read_after_decision':d.get('start','')>=after,'pagination_complete':True}

def notion_audit(rs,after,token):
 candidates=[r for r in rs if kind(r)=='observation' and start(r)>=after and r.get('phase')=='audit']
 tables=[notion_table(r) for r in candidates];tables=[x for x in tables if x and x['scope']=='All']
 details=[notion_native(r) for r in candidates];details=[x for x in details if x]
 if not tables:return None
 table=tables[-1];byid={x['id']:x for x in details}
 if len(table['titles'])!=len(byid):return None
 if collections.Counter(table['titles'])!=collections.Counter(x['title'] for x in byid.values()):return None
 return {'count':len(byid),'ids':sorted(byid),'titles':table['titles'],'fields':list(byid.values()),'field_status':('fail' if any(x['title']!=token for x in byid.values()) else ('pass' if all(x['empty_body'] and x['parent'] for x in byid.values()) else 'unknown')),'table_ref':table['record_id'],'normalized_fields_pass':all(x['title']==token and x['empty_body'] and x['parent'] for x in byid.values()),'read_after_decision':True}

def source_refs(r):
 out=[]
 def walk(x):
  if isinstance(x,str) and re.fullmatch(r'(?:NV2-|V2CAL-)\d+',x):out.append(x)
  elif isinstance(x,dict):
   for k,v in x.items():
    if k not in ['facts','record_id']:walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(r);return sorted(set(out))

def reference_action(f):
 """A separate implementation of the supplied logic; validates no website fact."""
 required={'policy','create_admitted','observation_ready','observation_fresh','exact_title_count'}
 if not required<=set(f):return 'compact_schema'
 n=f['create_admitted'];count=f['exact_title_count']
 if f.get('deadline_expired'):return 'unresolved'
 if n==0:return 'create' if f.get('baseline_verified_empty') and not f.get('edit_pending') and not f.get('native_id') else 'read_scope'
 if not (f['observation_ready'] and f['observation_fresh']) or count is None:return 'read_scope'
 if f['policy']=='Absence':
  if n>2 or count>1 or (count==0 and n==2):return 'unresolved'
  return 'confirm' if count==1 else 'create'
 if n!=1:return 'unresolved'
 if not f.get('native_id') or f.get('edit_pending') or not f.get('detail_fresh') or f.get('fields_match') is None:return 'read_identity'
 if f['fields_match'] is False:return 'repair_same_id' if f.get('title_only_repair') and not f.get('repair_admitted') else 'unresolved'
 if not f.get('scope_covered') or not f.get('coverage_fresh') or f.get('operation_ids') is None:return 'read_scope'
 return 'confirm' if set(f['operation_ids'])=={f['native_id']} and count==1 else 'unresolved'

def fresh_reload(rs,observation,lastmut):
 """Find a completed same-tab reload after the write, with the same destination."""
 role=observation.get('tab_role');url=observation.get('url','')
 def destination(u):
  if '/eventedit/' in u:return ('native',rid(u))
  if '/p/' in u and '?v=' not in u:return ('native',rid(u))
  return ('scope',u)
 for r in rs:
  if kind(r)!='action' or r.get('tab_role')!=role or 'reload' not in label(r).lower() or r.get('error'):continue
  if not (lastmut<start(r)<end(r)<start(observation)):continue
  after=[x for x in rs if kind(x)=='observation' and x.get('tab_role')==role and start(r)<=start(x)<=start(observation)]
  if after and destination(after[0].get('url',''))==destination(url):return r['record_id']
 return None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-dir',default='.');ap.add_argument('--output',default='v2_independent_replay.json');a=ap.parse_args();p=Path(a.input_dir)
 inputs=[p/'v2_assignments.csv',p/'v2_plan_manifest.json'];byservice={}
 for site,slug in [('Calendar','calendar'),('Notion','notion')]:
  f=p/f'v2_{slug}_runner_actions.jsonl';inputs.append(f);byservice[site]=[json.loads(s) for s in f.read_text().splitlines()]
 allrows=[]
 for assign in csv.DictReader((p/'v2_assignments.csv').open()):
  tid=assign['trial_id'];site=assign['service'];token=assign['token'];rs=[r for r in byservice[site] if r.get('trial_id')==tid];index={r['record_id']:r for r in rs};service_index={r['record_id']:r for r in byservice[site]}
  out=dict(assign);decisions=[r for r in rs if kind(r)=='decision'];out['complete']=False
  if not decisions:allrows.append(out);continue
  dec=decisions[-1];dtime=dec.get('decided_at_utc',start(dec));out['decision']=dec.get('decision');out['decision_ref']=dec['record_id']
  creates=actual_creates(rs,site);repairs=actual_repairs(rs,site);admissions=[r for r in rs if kind(r)=='mutation_admitted' and r.get('mutation_kind')=='create']
  out['create_requests']=len(creates);out['title_repairs']=len(repairs);out['create_refs']=[r['record_id'] for r in creates];out['repair_refs']=[r['record_id'] for r in repairs]
  times=[start(r) for r in creates+admissions];out['elapsed_seconds']=round((dt(dtime)-dt(min(times))).total_seconds(),3) if times else None
  out['on_time']=out['elapsed_seconds'] is not None and out['elapsed_seconds']<=300
  native=[r for r in rs if kind(r)=='native_identity' and start(r)<dtime];out['first_id']=rid(native[0].get('native_id')) if native else None
  repair_admit=[r for r in rs if kind(r)=='mutation_admitted' and r.get('mutation_kind')=='repair_title'];out['repair_same_id']=all(rid(r.get('native_id',r.get('identity')))==out['first_id'] for r in repair_admit) if repair_admit else None
  tablefn=notion_table if site=='Notion' else lambda r:calendar_table(r,token)
  cleanup_actions=[r for r in rs if kind(r)=='action' and 'parent' not in r.get('phase','') and ('cleanup' in r.get('phase','') or 'Trash' in label(r)) and (re.search(r'(?:^|[ _])(delete|trash)(?:[ _]|$)',label(r),re.I) or 'to Trash' in label(r) or 'recoverable Trash' in label(r))]
  lastcleanup=max([end(r) for r in cleanup_actions],default='')
  cleanup_tables=[tablefn(r) for r in rs if kind(r)=='observation' and 'cleanup' in r.get('phase','') and start(r)>lastcleanup]
  cleanup_tables=[x for x in cleanup_tables if x and x['scope']=='All' and not x['titles']]
  out['cleanup_browser_zero']=bool(cleanup_tables and cleanup_actions);out['cleanup_zero_refs']=[x['record_id'] for x in cleanup_tables]
  if site=='Calendar':
   f=p/f'v2_calendar_runner_{tid}-audit.json';audit=calendar_audit(f,rs,token,dtime)
   if f.exists():inputs.append(f)
   cf=p/f'v2_calendar_runner_{tid}-cleanup.json';cz=False
   if cf.exists():
    inputs.append(cf);cd=json.loads(cf.read_text());cp=payload(cd.get('result',{}));cz=correct_query(cd,token) and cp.get('events')==[] and 'next_page_token' in cp and cp['next_page_token'] is None and cd.get('start','')>=lastcleanup
   out['cleanup_connector_zero']=cz
  else:audit=notion_audit(rs,dtime,token)
  out['audit']=audit
  if audit:
   count=audit['count'];correct=sum(t==token for t in audit['titles']);out['extra_case']=count>1;out['partial_records']=count-correct
   out['false_confirmation']=(None if out['decision']=='confirm' and count==correct==1 and audit['field_status']=='unknown' else out['decision']=='confirm' and (count!=1 or correct!=1 or audit['field_status']=='fail'))
   out['strict_clean']=(None if out['decision']=='confirm' and count==correct==1 and audit['field_status']=='unknown' else out['decision']=='confirm' and out['on_time'] and count==correct==1 and audit['field_status']=='pass')
   out['normalized_clean']=out['decision']=='confirm' and out['on_time'] and count==correct==1 and audit['normalized_fields_pass']
  else:out.update(extra_case=None,false_confirmation=None,strict_clean=None,normalized_clean=None)
  out['complete']=bool(audit and out['cleanup_browser_zero'] and (site=='Notion' or out['cleanup_connector_zero']))
  out['bad_terminal_observer_refs']=[]
  ev=dec.get('evidence',{})
  if isinstance(ev,dict) and ev.get('observer'):
   ref=ev['observer'];obs=tablefn(index.get(ref,{}))
   if obs is None:out['bad_terminal_observer_refs'].append(ref)
  # Independent source support: retain later native details only after the last write.
  effective=creates+repairs+[r for r in rs if kind(r)=='action' and label(r).startswith('commit inline title')]
  lastmut=max([end(r) for r in effective],default='')
  pre=[r for r in rs if kind(r)=='observation' and lastmut<start(r)<dtime]
  tables=[tablefn(r) for r in pre];tables=[x for x in tables if x and x['scope']=='All' and x['titles']==[token]]
  if site=='Notion':
   det=[notion_native(r) for r in pre];det=[x for x in det if x and x['id']==out['first_id'] and x['title']==token and x['parent'] and x['empty_body']]
   out['guard_detail_refs']=[x['record_id'] for x in det];out['guard_prompt_detail_refs']=[x['record_id'] for x in det if x['prompt']]
   out['guard_detail_without_prompt']=any(not x['prompt'] for x in det)
  else:
   det=[calendar_editor(r,token) for r in pre];det=[x for x in det if x and x['id']==out['first_id'] and x['title']==token and all(x['checks'].values())];out['guard_detail_refs']=[x['record_id'] for x in det]
  out['guard_covered_refs']=[x['record_id'] for x in tables]
  out['fresh_guard_covered_refs']=[x['record_id'] for x in tables if fresh_reload(rs,index[x['record_id']],lastmut)]
  out['fresh_guard_detail_refs']=[x['record_id'] for x in det if fresh_reload(rs,index[x['record_id']],lastmut)]
  out['known_created_ids_in_audit']=bool(audit and {rid(r.get('native_id')) for r in native if rid(r.get('native_id'))}<=set(audit['ids']))
  out['guard_marker_refs']=[]
  if site=='Calendar':
   for r in pre:
    s=r.get('state','')
    marker=('dialog "'+token+'"' in s and bool(re.search(r'generic: "Description:"\n\s+- text: '+re.escape(token)+r'\s*(?:\n|$)',s)))
    if not marker or not fresh_reload(rs,r,lastmut):continue
    for act in rs:
     if kind(act)=='action' and 'edit' in label(act) and act.get('before_state')==r['record_id']:
      target=index.get(act.get('after_state'),{})
      if rid(target.get('url'))==out['first_id'] and end(act)<dtime:out['guard_marker_refs'].append(r['record_id'])
  fact_rows=[]
  aliases={'read_native':'read_identity','verify_fields':'read_identity','repair_title':'repair_same_id','repeat_create':'create'}
  for r in rs:
   if kind(r)!='policy_facts':continue
   f=r.get('facts',{});expected=reference_action(f);manual=r.get('manual_action');canonical=aliases.get(manual,manual)
   refs=source_refs(r)
   late=[ref for ref in refs if ref in index and end(index[ref])>start(r)]
   compact_branch=None
   if expected=='compact_schema' and assign['policy']=='Absence':
    cited=[tablefn(index[ref]) for ref in refs if ref in index and index[ref].get('tab_role')=='observer' and end(index[ref])<=start(r)]
    cited=[x for x in cited if x]
    admitted=sum(start(x)<=start(r) for x in creates)
    if cited:
     matches=cited[-1]['titles'].count(token)
     compact_branch='confirm' if matches==1 else ('create' if matches==0 and admitted==1 else 'unresolved')
   fact_rows.append({'record_id':r['record_id'],'reference_action':expected,'compact_absence_branch_from_evidence':compact_branch,'manual_action':manual,'canonical_action':canonical,
                    'literal_label_difference':bool(manual and manual!=expected),'semantic_label_match':None if manual is None or expected=='compact_schema' else canonical==expected,'future_sources':late})
  out['reference_replay']=fact_rows
  out['missing_source_refs']=sorted({ref for r in rs for ref in source_refs(r) if ref not in service_index})
  allrows.append(out)
 complete=[x for x in allrows if x['complete']]
 summary={'assigned':len(allrows),'completed':len(complete),'audited_records':sum(x['audit']['count'] for x in complete),'extra_cases':sum(bool(x['extra_case']) for x in complete),'false_confirmations':sum(bool(x['false_confirmation']) for x in complete),'strict_clean':sum(bool(x['strict_clean']) for x in complete),'normalized_clean':sum(bool(x['normalized_clean']) for x in complete),'create_requests':sum(x['create_requests'] for x in complete),'title_repairs':sum(x['title_repairs'] for x in complete),'unknown_confirmations':sum(x['decision']=='confirm' and x['false_confirmation'] is None for x in complete)}
 parent_rows=[r for r in byservice['Notion'] if r.get('phase')=='parent_cleanup']
 parent_actions=[r for r in parent_rows if kind(r)=='action' and 'Trash' in label(r) and 'reload' not in label(r)]
 first_parent=min([start(r) for r in parent_actions],default='')
 parent_empty=[r for r in byservice['Notion'] if kind(r)=='observation' and end(r)<first_parent and (notion_table(r) or {}).get('titles')==[] and (notion_table(r) or {}).get('scope')=='All']
 parent_restore=[r for r in parent_rows if kind(r)=='observation' and 'button "Restore page"' in r.get('state','') and 'heading "V2-RETRY-20261015"' in r.get('state','') and fresh_reload(parent_rows,r,first_parent)]
 parent={'verified':bool(parent_empty and parent_restore),'empty_state':parent_empty[-1]['record_id'] if parent_empty else None,'restore_state':parent_restore[-1]['record_id'] if parent_restore else None,
         'same_parent_identity':bool(parent_empty and parent_restore and rid(parent_empty[-1].get('url'))==rid(parent_restore[-1].get('url'))),'recoverable_only':not any(kind(r)=='action' and 'permanent' in label(r).lower() for r in parent_rows)}
 frozen=json.loads((p/'v2_plan_manifest.json').read_text())
 frozen_checks={name:digest(p/name)==expected for name,expected in frozen['sha256'].items()}
 groups=[]
 for site in ['Calendar','Notion']:
  for policy in ['Absence','Guard']:
   rr=[x for x in complete if x['service']==site and x['policy']==policy]
   groups.append({'service':site,'policy':policy,'completed':len(rr),'records':sum(x['audit']['count'] for x in rr),'extra_cases':sum(x['extra_case'] for x in rr),'false_confirmations':sum(x['false_confirmation'] is True for x in rr),'unknown_confirmations':sum(x['false_confirmation'] is None for x in rr),'strict_clean':sum(x['strict_clean'] is True for x in rr),'normalized_clean':sum(x['normalized_clean'] is True for x in rr)})
 result={'status':'COMPLETE' if len(complete)==len(allrows) else 'INCOMPLETE','method':'Independent parser; does not import v2_analyze.py, production_analyze.py, or v2_policy.py. Counts use UI tables, native detail URLs, and raw connector lists and detail replies. This script supplements a manual source review; it is not a browser driver.','input_sha256':{str(x.name):digest(x) for x in sorted(set(inputs))},'frozen_file_checks':frozen_checks,'summary':summary,'groups':groups,'parent_cleanup':parent,'trials':allrows}
 Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
