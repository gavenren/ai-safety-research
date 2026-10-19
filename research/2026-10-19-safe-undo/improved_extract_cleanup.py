"""Export selected cleanup facts, with private source file hashes. No network use."""
import argparse,hashlib,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--private-dir',type=Path,required=True);ap.add_argument('--output-dir',type=Path,default=Path('.'));a=ap.parse_args()
 files={site:a.private_dir/site/'cleanup_summary.json' for site in ['calendar','notion']}
 c,n=(json.loads(files[s].read_text()) for s in ['calendar','notion'])
 rows=[json.loads(x) for x in (a.output_dir/'improved_trials.jsonl').read_text().splitlines()]
 assert len(rows)==32 and all(r['cleanup']['status']=='trashed' and r['cleanup']['active_matches']==0 for r in rows)
 result={'status':'SAVED_RECORDS_REMOVED_BROWSER_LIMITS_REMAIN','created_trial_records':c['created_records']+n['created_children'],'created_parent_records':n['created_parents'],'preflight_records_created':c['preflight_records_created'],'permanent_deletion':False,
 'trial_records':[{'trial_id':r['trial_id'],'cleanup':r['cleanup']} for r in rows],
 'calendar':{'created_records':c['created_records'],'active_saved_records':c['active_saved_records'],'prefix_query':{k:c['final_prefix_query'][k] for k in ['id','utc','date_from','date_to','active_matches','evidence_ids']},'browser_tabs':[{k:r.get(k) for k in ['id','trial_id','utc','status','error','note']} for r in c['browser_tabs']],'final_inventory_source':c['final_tab_inventory']['id'],'old_trial23_touched':c['old_trial23_touched']},
 'notion':{'created_children':n['created_children'],'created_parents':n['created_parents'],'parent':{k:n['parent'][k] for k in ['status','source','active_absence_source']},'browser_draft_remaining':n['browser_draft_remaining'],'browser_tab_closed':n['browser_tab_closed'],'browser_tab_closed_evidence':n['browser_tab_closed_evidence']},
 'private_input_sha256':{site+'/cleanup_summary.json':hashlib.sha256(f.read_bytes()).hexdigest() for site,f in files.items()},
 'limits':['All 32 new saved trial records and the one new Notion parent were moved to recoverable Trash. No Trash was emptied.','The new Calendar13 tab failed to close. Its saved record is in Trash. No Save was sent during tab cleanup.','The earlier possible unsaved Calendar23 form was not opened or saved in this extension. Its earlier browser uncertainty remains.','Saved-record cleanup is separate from unknown trial outcomes and browser-tab closure.']}
 assert result['created_trial_records']==32 and result['created_parent_records']==1 and result['preflight_records_created']==0
 (a.output_dir/'improved_cleanup.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k] for k in ['status','created_trial_records','created_parent_records']}))
if __name__=='__main__':main()
