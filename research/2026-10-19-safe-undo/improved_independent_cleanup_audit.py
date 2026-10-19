"""Check temporary-record cleanup against private native UI evidence."""
import argparse,collections,hashlib,json
from pathlib import Path
from urllib.parse import urlparse,parse_qs

def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,m):
 if not c:raise ValueError(m)
def kind(e):return e.get('type',e.get('kind'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-partial',action='store_true');a=p.parse_args();rows=[];issues=[];inputs=[];summary_checks=[]
 for site in ('calendar','notion'):
  folder=a.work/site;tp=folder/'final_trials.jsonl' if (folder/'final_trials.jsonl').exists() else folder/'trials.jsonl';ts=read(tp);es=read(folder/'actions.jsonl');byid={e['id']:e for e in es};inputs.append({'site':site,'terminal_file':tp.name,'terminal_sha256':digest(tp),'actions_sha256':digest(folder/'actions.jsonl')})
  for t in ts:
   cl=t.get('cleanup') or {};row={'trial_id':t['trial_id'],'status':cl.get('status','unresolved'),'active_matches':cl.get('active_matches'),'sources':cl.get('evidence_ids',[]),'checked':False};rows.append(row)
   if row['status']=='unresolved':continue
   try:
    require(row['status']=='trashed','unexpected cleanup category');require(row['active_matches']==0,'active matches not zero');linked=[byid[x] for x in row['sources']];observed=[e for e in linked if kind(e)=='observation'];require(observed,'cleanup lacks native observation')
    marker=t['assignment']['marker'];tes=[e for e in es if e.get('trial_id')==t['trial_id'] or (t['trial_id']=='calendar-13' and e.get('label','').startswith('trial13_'))]
    if site=='calendar':
     ready=[e for e in observed if 'Search results. No events found.' in e['state'] and 'No results found' in e['state'] and 'Searching for' not in e['state'] and ('combobox "Search": '+marker) in e['state']];require(ready,'Calendar exact search not ready and empty')
     deletes=[e for e in tes if kind(e)=='action_result' and e.get('label') in ('trash','failed05_trash_dialog','trial13_trash') and e['utc']<ready[-1]['utc'] and not e.get('error')];require(deletes,'Calendar delete action not recorded')
     if t.get('native_id'):
      gate=[e for e in tes if kind(e)=='observation' and marker in e.get('state','') and t['native_id']==e.get('url') and e['utc']<=deletes[-1]['utc']];require(gate,'Calendar stable-ID cleanup context absent')
     else:
      gate=[e for e in tes if kind(e)=='observation' and ('dialog "'+marker+'"') in e.get('state','') and e['utc']<=deletes[-1]['utc']];require(gate,'Calendar unknown-record marker dialog absent')
     row['identity_basis']='stable ID and exact marker' if t.get('native_id') else 'exact marker dialog; stable edit ID unavailable';row['ready_source']=ready[-1]['id'];row['delete_source']=deletes[-1]['id']
    else:
     final=observed[-1];schema=json.loads((folder/'schema.json').read_text());require(schema['parent_name'] in final['state'] and marker not in final['state'],'Notion parent active absence not shown')
     gate=[e for e in tes if kind(e)=='observation' and e.get('label')=='Cleanup identity gate' and marker in e['state'] and t['native_id'].replace('-','') in e['url'].replace('-','')];require(gate,'Notion cleanup identity absent')
     deletes=[e for e in tes if kind(e)=='action' and e.get('label')=='Move child to recoverable Trash' and gate[-1]['utc']<e['utc']<final['utc'] and not e.get('error')];require(deletes,'Notion child trash action absent')
     alerts=[e for e in tes if kind(e)=='observation' and 'Moved to Trash' in e.get('state','') and deletes[-1]['utc']<e['utc']<final['utc']];require(alerts,'Notion Trash receipt absent')
     reloads=[e for e in tes if kind(e)=='action' and e.get('label')=='Reload parent cleanup' and deletes[-1]['utc']<e['utc']<final['utc'] and not e.get('error')];require(reloads,'Notion parent reload absent')
     row.update(identity_basis='stable ID and exact marker',ready_source=final['id'],delete_source=deletes[-1]['id'],trash_receipt=alerts[-1]['id'])
    row['checked']=True
   except (ValueError,KeyError,TypeError) as ex:issues.append({'trial_id':t['trial_id'],'issue':str(ex)})
  summary_path=folder/'cleanup_summary.json'
  if site=='calendar' and summary_path.exists():
   try:
    summary=json.loads(summary_path.read_text());require(summary['planned_assignments']==summary['created_records']==len(ts)==16 and summary['preflight_records_created']==0,'Calendar object count differs')
    require(summary['active_saved_records']==0 and summary['terminal_counts']==dict(collections.Counter(t['status'] for t in ts)),'Calendar final summary count differs')
    for record in summary['records']:require(record['cleanup']==next(t['cleanup'] for t in ts if t['trial_id']==record['trial_id']),'Calendar summary cleanup differs')
    query=summary['final_prefix_query'];require(byid[query['id']]==query and query['active_matches']==0,'Calendar prefix summary source differs')
    ready=byid[query['evidence_ids'][0]];q=parse_qs(urlparse(ready['url']).query);require(q=={'q':['UNDO2-20261019-CALENDAR'],'start':['20261001'],'end':['20261031']},'Calendar prefix query does not cover test date')
    require('Search results. No events found.' in ready['state'] and 'No results found' in ready['state'] and 'Searching for' not in ready['state'] and 'combobox "Search": UNDO2-20261019-CALENDAR' in ready['state'],'Calendar final prefix search not ready and empty')
    for t in ts:
     if t.get('cleanup_adjudication'):
      observation=byid[t['cleanup']['evidence_ids'][0]];q=parse_qs(urlparse(observation['url']).query);require(q=={'q':[t['assignment']['marker']],'start':['20261001'],'end':['20261031']},'Calendar adjudicated cleanup date coverage differs')
    for tab in summary['browser_tabs']:require(tab==byid[tab['id']],'Calendar tab cleanup source differs')
    inv=summary['final_tab_inventory'];require(inv==byid[inv['id']],'Calendar final tab inventory source differs')
    remaining=[v for v in summary['browser_tabs'] if v['status']=='closure_unresolved'];require(len(remaining)==1 and remaining[0]['trial_id']=='calendar-13','Calendar unresolved tab state changed')
    native=next(t['native_id'] for t in ts if t['trial_id']=='calendar-13');require(len(inv['tabs'])==1 and inv['tabs'][0]['url']==native,'Calendar remaining tab identity differs')
    require(summary['actions_sha256']==digest(folder/'actions.jsonl') and summary['last_record_id']==es[-1]['id'],'Calendar final source digest differs')
    summary_checks.append({'site':site,'summary_sha256':digest(summary_path),'all_saved_records_absent_source':ready['id'],'date_from':'2026-10-01','date_to':'2026-10-31','remaining_editor_trial':'calendar-13','closure_status':'unresolved','tab_inventory_source':inv['id'],'status':'PASS'})
   except (ValueError,KeyError,TypeError,StopIteration) as ex:issues.append({'site':site,'issue':'final summary: '+str(ex)})
  if site=='notion' and summary_path.exists():
   try:
    summary=json.loads(summary_path.read_text());schema=json.loads((folder/'schema.json').read_text());parent=summary['parent'];e=byid[parent['source']];ui=e['state']
    require(summary['created_children']==len(ts)==16 and summary['created_parents']==1,'Notion object count differs')
    for child in summary['children']:require(child['cleanup']==next(t['cleanup'] for t in ts if t['trial_id']==child['trial_id']),'Notion child summary changed')
    require(parent['status']=='trashed' and schema['parent_name'] in ui and 'moved this page to Trash' in ui and 'button "Restore page"' in ui,'Notion parent Trash receipt absent')
    require(e['url']==schema['parent_url'],'Notion parent identity differs')
    absent=byid[parent['active_absence_source']];require(absent['url']==schema['parent_url'] and schema['parent_name'] in absent['state'] and all(t['assignment']['marker'] not in absent['state'] for t in ts),'Notion final active child absence differs')
    tab=byid[summary['browser_tab_closed_evidence']];require(tab.get('success') is True and kind(tab)=='tab_cleanup','Notion tab close not reported successful')
    require(summary['permanent_deletion'] is False,'Permanent deletion claim changed')
    summary_checks.append({'site':site,'summary_sha256':digest(summary_path),'parent_trash_source':parent['source'],'all_children_absent_source':parent['active_absence_source'],'tab_close_source':tab['id'],'status':'PASS'})
   except (ValueError,KeyError,TypeError,StopIteration) as ex:issues.append({'site':site,'issue':'final summary: '+str(ex)})
 if not a.allow_partial:
  require(len(rows)==32 and all(sum(r['trial_id'].startswith(site+'-') for r in rows)==16 for site in ('calendar','notion')),'full cleanup audit requires all 32 assignments')
  require(all(r['checked'] for r in rows),'unresolved saved-record cleanup')
  require(len(summary_checks)==2,'both final site cleanup summaries must be checked')
 counts=dict(collections.Counter(r['status'] for r in rows));out={'status':'FAIL' if issues else ('PASS_AVAILABLE_ROWS' if a.allow_partial else 'PASS'),'rows':rows,'counts':counts,'verified_rows':sum(r['checked'] for r in rows),'issues':issues,'inputs':inputs,'summary_checks':summary_checks,'scope':'Only saved temporary records in these terminal rows. Final site summaries check parent cleanup, the Calendar date-covered search, and the known remaining Calendar13 editor tab. Recoverable Trash is not permanent deletion.'};a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:out[k] for k in ['status','counts','verified_rows','issues']}))
 if issues:raise SystemExit(1)
if __name__=='__main__':main()
