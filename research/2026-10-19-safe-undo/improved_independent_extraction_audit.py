"""Check a public extract against private source lines. Does not import extractor."""
import argparse,hashlib,json,re
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s]
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--public',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-growing',action='store_true');a=p.parse_args();checks=0;issues=[];raw={};events={};aliases={};file_receipts=[]
 def check(label,x,y):
  nonlocal checks
  checks+=1
  if x!=y:issues.append(label)
 def require(label,c):check(label,bool(c),True)
 receipt=json.loads((a.public/'improved_extraction.json').read_text());trials=read(a.public/'improved_trials.jsonl');evidence=read(a.public/'improved_evidence.jsonl');byid={t['trial_id']:t for t in trials}
 for name,h in receipt['public_sha256'].items():check('public file hash '+name,digest((a.public/name).read_bytes()),h)
 for site in ('calendar','notion'):
  folder=a.work/site;meta=receipt['source_files'][site];tp=folder/meta['terminal_file'];original=folder/'trials.jsonl';allts=read(tp);site_public=[t for t in trials if t['site']==site];chosen=allts[:len(site_public)] if a.allow_growing else allts
  raw.update({t['trial_id']:t for t in chosen})
  for t in chosen:
   if t.get('native_id'):aliases[t['native_id']]='record-'+t['trial_id']
  lines=(folder/'actions.jsonl').read_bytes().splitlines(keepends=True);pub=[e for e in evidence if e['site']==site];lines=lines[:len(pub)] if a.allow_growing else lines
  check(site+' evidence count',len(pub),len(lines))
  for n,b in enumerate(lines,1):
   e=json.loads(b);ref={'site':site,'id':e['id'],'line':n,'sha256':digest(b)};require(site+' duplicate source ID '+e['id'],(site,e['id']) not in events);events[(site,e['id'])]=(e,ref)
  expected_actions=digest(b''.join(lines));check(site+' actions hash',expected_actions,meta['actions_sha256'])
  if a.allow_growing:
   tbytes=b''.join(tp.read_bytes().splitlines(keepends=True)[:len(site_public)]);obytes=b''.join(original.read_bytes().splitlines(keepends=True)[:len(site_public)])
  else:tbytes=tp.read_bytes();obytes=original.read_bytes()
  check(site+' terminal hash',digest(tbytes),meta['terminal_sha256']);check(site+' original terminal hash',digest(obytes),meta['original_terminal_sha256'])
  if tp.name!='trials.jsonl':
   originals={t['trial_id']:t for t in read(original)}
   allowed={'cleanup','cleanup_original','cleanup_adjudication','recovery_note'}
   for t in chosen:
    old=originals[t['trial_id']];changed={k for k in set(old)|set(t) if old.get(k)!=t.get(k)};require(t['trial_id']+' final change restricted',changed<=allowed)
    if changed:require(t['trial_id']+' original cleanup retained',t.get('cleanup_original')==old.get('cleanup'))
  file_receipts.append({'site':site,'terminal_file':tp.name,'terminal_sha256':digest(tbytes),'original_terminal_sha256':digest(obytes),'actions_sha256':expected_actions})
 def redact(v):
  if isinstance(v,dict):return {k:redact(x) for k,x in v.items()}
  if isinstance(v,list):return [redact(x) for x in v]
  if isinstance(v,str):
   if v in aliases:return aliases[v]
   for native in sorted(aliases,key=len,reverse=True):v=v.replace(native,aliases[native])
   return re.sub(r'https?://(?:calendar\.google\.com|(?:app\.)?notion\.so|(?:app\.)?notion\.com)/\S+','<PRIVATE_URL>',v)
  return v
 def ref(site,eid):return events[(site,eid)][1] if eid else None
 def obs(site,o,p,label):
  if not o:check(label,p,None);return
  eid=o.get('evidence_id',o.get('id'));e,r=events[(site,eid)]
  expected={'x':o.get('x'),'y':o.get('y'),'identity':aliases[o.get('native_id',o.get('identity'))],'contract':o.get('contract_ok',o.get('contract')) is True and o.get('identity_ok',True) is True,'readId':o.get('readId',eid),'readAt':o.get('readAt',o.get('utc')),'reloaded':o.get('reloaded') is True,'x_raw':o.get('x_raw'),'y_raw':o.get('y_raw'),'checks':o.get('checks',o.get('contract')),'source':r,'ui_source':ref(site,e.get('source_observation',e.get('source')))}
  for k in set(expected)|set(p):check(label+'/'+k,p.get(k),redact(expected.get(k)))
 if not a.allow_growing:check('full assignment count',len(trials),32)
 check('terminal count',len(raw),len(trials));check('terminal ID set',sorted(raw),sorted(byid))
 for t in trials:
  r=raw[t['trial_id']];site=t['site'];label=t['trial_id']
  for k in ['trial_id','assignment','status','reason','started_at','ended_at','failed_phase','prepare_input','decision','finish_input','finish']:check(label+'/'+k,t.get(k),redact(r.get(k)))
  for k in ['baseline','agent','preundo']:obs(site,r.get(k),t.get(k),label+'/'+k)
  for k in ['later_phases','final_reads']:check(label+'/'+k+'/length',len(r.get(k,[])),len(t.get(k,[])))
  for n,(rr,pp) in enumerate(zip(r.get('later_phases',[]),t['later_phases'])):check(label+'/later command/'+str(n),rr['command'],pp['command']);obs(site,rr['observation'],pp['observation'],label+'/later/'+str(n))
  for n,(rr,pp) in enumerate(zip(r.get('final_reads',[]),t['final_reads'])):obs(site,rr,pp,label+'/final/'+str(n))
  seal=r.get('seal') or {};actual=t['seal']
  for k,private_key in [('utc','utc'),('presented_later','presented_later'),('history_complete','history_complete')]:
   # An unknown run before seal may have no raw seal. No synthetic value is used as evidence.
   if seal:check(label+'/seal/'+k,actual[k],seal[private_key])
  if seal:check(label+'/seal/before_later',actual['before_later'],seal.get('before_later',seal.get('seal_before_later')))
  check(label+'/seal/source',actual['source'],ref(site,seal.get('evidence_id',seal.get('id'))))
  aa=r.get('actuator') or {};expected={'requested':aa.get('requested'),'literal':aa.get('literal',aa.get('actual_literal')),'fault':aa.get('fault'),'attempted':aa.get('attempted',aa.get('write_attempted',False)),'source':ref(site,aa.get('evidence_id'))};check(label+'/actuator',t['actuator'],redact(expected))
  for k in ['prepare','finish']:
   eid=r.get(k+'_evidence_id') or (r.get(k+'_evidence') or {}).get('id');check(label+'/'+k+'/source',t[k+'_source'],ref(site,eid))
  cl=r.get('cleanup') or {};expected={k:redact(cl.get(k)) for k in ['status','active_matches','reason']};expected['sources']=[ref(site,eid) for eid in cl.get('evidence_ids',[])];check(label+'/cleanup',t['cleanup'],expected)
  for k in ['cleanup_original','cleanup_adjudication','recovery_note']:check(label+'/'+k,t.get(k),redact(r.get(k)))
 for pub in evidence:
  e,r=events[(pub['site'],pub['id'])];expected={**r,'type':e.get('type',e.get('kind')),'label':e.get('label'),'utc':e.get('utc'),'trial_id':e.get('trial_id')}
  for k in ['x','y','x_raw','y_raw','identity_ok','contract_ok','reloaded','phase','active_matches','status']:
   if k in e:expected[k]=e[k]
  check(pub['site']+'/evidence/'+pub['id'],pub,redact(expected))
 cleanup_file=a.public/'improved_cleanup.json';cleanup_text=''
 if cleanup_file.exists():
  cp=json.loads(cleanup_file.read_text());cleanup_text=cleanup_file.read_text();c=json.loads((a.work/'calendar'/'cleanup_summary.json').read_text());n=json.loads((a.work/'notion'/'cleanup_summary.json').read_text())
  for site in ('calendar','notion'):check(site+'/cleanup summary hash',cp['private_input_sha256'][site+'/cleanup_summary.json'],digest((a.work/site/'cleanup_summary.json').read_bytes()))
  check('public cleanup record counts',[cp[k] for k in ['created_trial_records','created_parent_records','preflight_records_created','permanent_deletion']],[c['created_records']+n['created_children'],n['created_parents'],c['preflight_records_created'],False])
  check('public trial cleanup rows',cp['trial_records'],[{'trial_id':t['trial_id'],'cleanup':t['cleanup']} for t in trials])
  cc=cp['calendar'];nn=cp['notion']
  for k in ['created_records','active_saved_records','old_trial23_touched']:check('public calendar cleanup/'+k,cc[k],c[k])
  check('public prefix query',cc['prefix_query'],{k:c['final_prefix_query'][k] for k in ['id','utc','date_from','date_to','active_matches','evidence_ids']})
  check('public calendar tab statements',cc['browser_tabs'],[{k:t.get(k) for k in ['id','trial_id','utc','status','error','note']} for t in c['browser_tabs']])
  check('public calendar inventory source',cc['final_inventory_source'],c['final_tab_inventory']['id'])
  for k in ['created_children','created_parents','browser_draft_remaining','browser_tab_closed','browser_tab_closed_evidence']:check('public notion cleanup/'+k,nn[k],n[k])
  check('public notion parent cleanup',nn['parent'],{k:n['parent'][k] for k in ['status','source','active_absence_source']})
  require('public cleanup browser limit',cp['status']=='SAVED_RECORDS_REMOVED_BROWSER_LIMITS_REMAIN' and any('Calendar13 tab failed to close' in v for v in cp['limits']))
  require('private tab IDs absent',all(str(t['tab_id']) not in cleanup_text for t in c['browser_tabs']))
 elif not a.allow_growing:require('final cleanup extract exists',False)
 text=(a.public/'improved_trials.jsonl').read_text()+(a.public/'improved_evidence.jsonl').read_text()+cleanup_text;private_strings=list(aliases)
 redactions=a.work/'private_redactions.json'
 if redactions.exists():
  data=json.loads(redactions.read_text())
  def strings(v):
   if isinstance(v,str):return [v]
   if isinstance(v,list):return [s for x in v for s in strings(x)]
   if isinstance(v,dict):return [s for x in v.values() for s in strings(x)]
   return []
  private_strings+=strings(data)
 require('private strings absent',all(v not in text for v in private_strings if v))
 require('account email absent',not re.search(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',text))
 require('native account URLs absent',not re.search(r'https?://(?:calendar\.google\.com|(?:app\.)?notion\.(?:so|com))/',text))
 require('local private paths absent','/Users/' not in text and '/home/' not in text)
 out={'status':'FAIL' if issues else ('PASS_PREFIX' if a.allow_growing else 'PASS'),'field_and_hash_checks':checks,'terminal_rows':len(trials),'source_lines':len(evidence),'issues':issues,'source_files':file_receipts,'public_sha256':{**receipt['public_sha256'],**({'improved_cleanup.json':digest(cleanup_file.read_bytes())} if cleanup_file.exists() else {})},'privacy_checks':['Exact native IDs and supplied private strings absent','No email pattern, native account URL or local home path'],'limitations':['Full browser UI is private. Public evidence hashes do not let an outside reader inspect the private source.','An unknown trial before a seal has no seal evidence; exported assignment defaults do not establish a completed seal.']};a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:out[k] for k in ['status','field_and_hash_checks','terminal_rows','source_lines','issues']}))
 if issues:raise SystemExit(1)
if __name__=='__main__':main()
