"""Audit cleanup changes against private source logs. No browser access.

The receipt contains synthetic evidence IDs and hashes, not account identities.
Saved-record absence and an unresolved browser draft are separate findings.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def must(c,m):
    if not c:raise ValueError(m)
def indexed(rows):
    out={}
    for i,r in enumerate(rows,1):out.setdefault(r['id'],[]).append((i,r))
    return out
def unique(index,eid):
    must(len(index.get(eid,[]))==1,'missing or ambiguous cleanup ID: '+eid)
    return index[eid][0]
def ready(index,eid,marker):
    line,e=unique(index,eid);s=e.get('state','')
    must(marker in s and 'No events found' in s and 'Searching for' not in s and 'progressbar' not in s,'search is not ready exact-marker zero: '+eid)
    q=parse_qs(urlparse(e['url']).query)
    must(q.get('q')==[marker] and q.get('start')==['20261001'] and q.get('end')==['20261031'],'search marker or date coverage mismatch: '+eid)
    return {'evidence_id':eid,'raw_log_line':line,'marker':marker,'date_from':'2026-10-01','date_to':'2026-10-31'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();w=args.work
    ce=read(w/'calendar'/'actions.jsonl');ci=indexed(ce)
    old=read(w/'calendar'/'trials.jsonl');new=read(w/'calendar'/'final_trials.jsonl')
    must([t['trial_id'] for t in old]==[t['trial_id'] for t in new],'terminal row order/coverage changed')
    changes=[];searches=[]
    for a,b in zip(old,new):
        tid=a['trial_id'];changed={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
        allowed={'cleanup','cleanup_original','cleanup_adjudication'}
        if tid=='calendar-14':allowed.add('native_id')
        if tid=='calendar-23':allowed.add('browser_draft')
        must(changed<=allowed,'non-cleanup result fields changed: '+tid)
        if not changed:continue
        must(b['cleanup_original']==a['cleanup'],'original cleanup not retained: '+tid)
        adj=b['cleanup_adjudication'];must(adj['outcome_unchanged'] is True and bool(adj['reason']),'missing cleanup explanation')
        must(adj['superseded_cleanup_status']==a['cleanup']['status'],'superseded status mismatch')
        must(adj['source_ids']==b['cleanup']['evidence_ids'],'adjudication/source mismatch')
        must(b['terminal_status']=='unknown','cleanup altered a scored trial')
        must(ce[adj['source_jsonl_line']-1]['id'] in adj['source_ids'],'adjudication line mismatch')
        for eid in adj['source_ids']:
            _,e=unique(ci,eid);must(e['trial_id']==tid and e['token']==b['token'],'cleanup scope mismatch')
            if e.get('type')=='observation':searches.append(ready(ci,eid,b['token']))
            else:must(e['type']=='ready_cleanup_result' and e['active_matches']==0,'unexpected cleanup source')
        if tid=='calendar-14':
            _,recovered=unique(ci,'UCN-00150');must(b['native_id']==recovered['native_id'],'recovered identity unsupported')
        if tid=='calendar-23':
            must(b['cleanup']['status']=='no_saved_record_found','uncertain creation became not-created')
            must(b['browser_draft']['status']=='unresolved_unsaved_form','browser draft uncertainty removed')
        changes.append({'trial_id':tid,'changed_keys':sorted(changed),'old_cleanup_status':a['cleanup']['status'],'new_cleanup_status':b['cleanup']['status'],'source_ids':adj['source_ids'],'scored_fields_unchanged':True})
    must({r['trial_id'] for r in changes}=={'calendar-01','calendar-02','calendar-12','calendar-14','calendar-23'},'unexpected cleanup change set')
    # The earlier failed assertions stay in the original log.
    _,transient=unique(ci,'UC-00152');must('Searching for' in transient['state'],'earlier Calendar02 pending search lost')
    _,stale=unique(ci,'UCN-00142');must('No events found' not in stale['state'],'Calendar14 stale view changed')
    _,withdrawal=unique(ci,'UCN-00145');must(withdrawal['type']=='adjudication_correction','Calendar14 withdrawal lost')
    _,corrected=unique(ci,'UCN-00148');must('No events found' in corrected['state'] and 'Searching for' not in corrected['state'],'Calendar14 corrected view missing')
    cs=json.loads((w/'calendar'/'cleanup_summary.json').read_text())
    for key in ('global_search_evidence','preflight_cleanup_evidence'):
        finding=cs[key]
        _,r=unique(ci,finding['id']);must(r==finding,'summary cleanup row differs')
        for eid in finding['evidence_ids']:searches.append(ready(ci,eid,finding['token']))
    must(cs['created_trial_record_count']==23 and len(cs['created_trial_records'])==23,'known created record count mismatch')
    must(cs['browser_draft']['status']=='unresolved_unsaved_form','Calendar draft uncertainty missing')
    delete_actions=[]
    for record in cs['created_trial_records']:
        tid=record['trial_id']
        action_ids=['UC-00146'] if tid=='calendar-02' else [e['id'] for e in ce if e.get('trial_id')==tid and e.get('type')=='action' and e.get('label') in ('cleanup_trash','trial14_trash')]
        must(len(action_ids)==1,'missing or duplicate Calendar delete action: '+tid)
        _,action=unique(ci,action_ids[0]);must(action.get('error') is None,'Calendar delete action has error')
        _,before=unique(ci,action['before']);must(record['token'] in before.get('state',''),'Calendar delete marker absent')
        delete_actions.append({'trial_id':tid,'evidence_id':action['id']})
    ne=read(w/'notion'/'actions.jsonl');ni=indexed(ne);ns=json.loads((w/'notion'/'cleanup_summary.json').read_text())
    for record in ns['created_children']:
        tid=record['trial_id'];actions=[e for e in ne if e.get('trial_id')==tid and e.get('kind')=='action' and e.get('label')=='Move child to recoverable Trash']
        must(len(actions)==1 and actions[0].get('error') is None,'Notion child Trash action missing or failed')
        _,before=unique(ni,actions[0]['before']);must(record['token'] in before.get('state',''),'Notion delete marker absent')
        must(record['native_id'].replace('-','') in before['url'].replace('-',''),'Notion delete native identity mismatch')
        delete_actions.append({'trial_id':tid,'evidence_id':actions[0]['id']})
    must(len(delete_actions)==49,'known saved-record deletion count differs')
    parent=ns['parent']['native_id'].replace('-','')
    _,private=unique(ni,'NU-00014');must(parent in private['url'].replace('-','') and 'Private' in private['state'],'Notion parent privacy not supported')
    _,empty=unique(ni,ns['complete_active_view']['evidence_id']);must(parent in empty['url'].replace('-',''),'wrong final Notion parent')
    must('TEMP-UNDO-20261019-NOTION-' not in empty['state'] and 'button "New page"' in empty['state'],'active Notion table not empty')
    _,pending=unique(ni,'NU-06064');must(pending['kind']=='cleanup_pending','Notion incomplete confirmation not retained')
    _,trash=unique(ni,'NU-06089');must(parent in trash['url'].replace('-','') and 'moved this page to Trash' in trash['state'] and 'Restore page' in trash['state'],'Notion parent Trash unverified')
    must(ns['parent']['evidence_ids']==['NU-06089'] and ns['temporary_objects_created']==28,'Notion final cleanup summary mismatch')
    _,closed=unique(ni,'NU-06092');must(closed['kind']=='session_close' and closed['error'] is None,'Notion runner tab close failed')
    result={'status':'PASS_BOUNDED_SAVED_RECORD_CHECKS','known_saved_record_delete_actions':delete_actions,'calendar_terminal_changes':changes,'calendar_ready_searches':searches,'calendar_known_created_trial_records':23,'calendar_unresolved_browser_draft':True,'calendar_23_creation_uncertain':True,'notion_private_parent_source':'NU-00014','notion_empty_parent_source':ns['complete_active_view']['evidence_id'],'notion_final_parent_trash_source':'NU-06089','notion_closed_tab_source':'NU-06092','retained_corrections':{'calendar_02_transient_zero':'UC-00152','calendar_14_withdrawal':'UCN-00145','calendar_14_later_zero':'UCN-00148','notion_parent_confirmation_pending':'NU-06064'},'source_hashes':{site:{name:sha(w/site/name) for name in (['actions.jsonl','trials.jsonl','final_trials.jsonl','cleanup_summary.json'] if site=='calendar' else ['actions.jsonl','trials.jsonl','cleanup_summary.json'])} for site in ('calendar','notion')},'limits':['The ready searches establish active saved-record absence for the exact markers in the stated date window at the recorded time.','Calendar23 is not proof of non-creation. Two close calls timed out; an unsaved form remains unresolved.','Recoverable deletion is not permanent erasure. Calendar Trash inventory was not inspected.','No unknown outcome was filled from a later cleanup observation.']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'terminal_cleanup_changes':len(changes),'ready_calendar_searches':len(searches),'calendar_unresolved_browser_draft':True}))

if __name__=='__main__':main()
