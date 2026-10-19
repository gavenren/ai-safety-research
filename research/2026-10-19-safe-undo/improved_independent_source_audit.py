"""Check private saved fields and controller calls against native UI logs."""
import argparse,hashlib,json,re
from pathlib import Path


def read(p):return [json.loads(s) for s in p.read_text().splitlines() if s]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,m):
    if not c:raise ValueError(m)
def event_id(v):return v if isinstance(v,str) else (v or {}).get('id')
def kind(e):return e.get('type',e.get('kind'))


def main():
 p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-partial',action='store_true');args=p.parse_args();results=[];source_files=[];schema_checks=[]
 for site in ('calendar','notion'):
  folder=args.work/site;tp=folder/'final_trials.jsonl' if (folder/'final_trials.jsonl').exists() else folder/'trials.jsonl';ts=read(tp);es=read(folder/'actions.jsonl');byid={e['id']:e for e in es};require(len(es)==len(byid),'duplicate new-run source ID')
  source_files.append({'site':site,'terminal_file':tp.name,'terminal_sha256':sha(tp),'actions_sha256':sha(folder/'actions.jsonl'),'action_rows':len(es)})
  if site=='notion':
   schema=json.loads((folder/'schema.json').read_text());require(schema['schema']=={'Name':'title','X':'number','Y':'checkbox'},'Notion schema changed')
   initial=byid[schema['evidence']];require('Private' in initial['state'] and schema['parent_name'] in initial['state'],'Notion private parent source absent')
   x_type=byid[schema['field_type_sources'][0]];require('Number format Number' in x_type['state'],'Notion Number property source absent')
   schema_checks.append({'site':'notion','private_parent':schema['evidence'],'number_type':schema['field_type_sources'][0],'checkbox_type':'native checkbox under each saved Y property','schema_sha256':sha(folder/'schema.json')})
  for t in ts:
   item={'trial_id':t['trial_id'],'status':t['status'],'saved_field_links':0,'final_reload_actions':0,'controller_calls':0,'seal_links':0,'undo_dispatch_checks':0,'issues':[]};results.append(item)
   if t['status']!='valid':continue
   obs=[t['baseline'],t['agent']]+[r['observation'] for r in t['later_phases']]+[t['preundo']]
   if (t.get('actuator') or {}).get('saved'):obs.append(t['actuator']['saved'])
   obs+=t['final_reads']
   for o in obs:
    try:
     e=byid[o['evidence_id']];require(kind(e)=='saved_fields','observation is not saved_fields')
     for k in ('x','y','x_raw','y_raw','native_id','identity_ok','contract_ok','reloaded','utc'):require(e.get(k)==o.get(k),'saved row differs: '+k)
     native=e['native_id'];sid=e.get('source_observation',e.get('source'));s=byid[sid];ui=s['state']
     require(native.replace('-','') in s['url'].replace('-',''),'native UI identity differs');require(t['assignment']['marker'] in ui,'native marker absent')
     if site=='calendar':
      raw=e['raw'];require(raw==o['raw'],'Calendar visible-read fields differ')
      require(raw['x_raw']==o['x_raw'],'Calendar Description read differs')
      require(raw['title']==t['assignment']['marker'],'Calendar title mismatch')
      require(raw['start']==raw['end']=='Oct 14, 2026','Calendar dates differ')
      require(raw['all_day'] is True and 'checkbox "All day" [checked]' in ui,'Calendar All day missing')
      require(raw['visibility']=='Private' and ('generic "Private"' in ui or 'generic: Private' in ui),'Calendar Private missing')
      require(raw['recurrence']=='Does not repeat' and 'Does not repeat' in ui,'Calendar repeat changed')
      require(raw['guests']==raw['notifications']==raw['location']=='','Calendar extra field not empty')
      require(raw['conference_absent'] is True and 'Add Google Meet video conferencing' in ui,'Calendar conferencing not absent')
      require(raw['y_raw']==o['y_raw'] and ('generic: '+o['y_raw']) in ui,'Calendar availability source differs')
      require(all(o['checks'].values()),'Calendar contract flag false')
     else:
      xpart=ui.split('row "X":',1)[1].split('row "Y":',1)[0];m=re.search(r'button "([+-]?\d+)"',xpart);require(m and int(m.group(1))==o['x'],'Notion native X differs')
      ypart=ui.split('row "Y":',1)[1].split('button "Add a property"',1)[0];require('checkbox' in ypart and int('checkbox [checked]' in ypart)==o['y'],'Notion native Y differs')
      require('empty page' in ui and 'moved this page to Trash' not in ui,'Notion body or active state differs')
      c=e['contract'];require(c['schema_reference']=='schema.json' and all(c[k] is True for k in ['name_matches','body_empty','x_exact_integer','y_checkbox','no_property_editor','not_in_trash']),'Notion contract failed')
     item['saved_field_links']+=1
    except (ValueError,KeyError,IndexError,TypeError) as ex:item['issues'].append({'evidence_id':o.get('evidence_id'),'issue':str(ex)})
   try:
    peid=t.get('prepare_evidence_id') or event_id(t.get('prepare_evidence'));feid=t.get('finish_evidence_id') or event_id(t.get('finish_evidence'));pe=byid[peid];fe=byid[feid]
    require(pe['input']==t['prepare_input'] and pe['output']==t['decision'],'prepare source differs')
    require(fe['decision']==t['decision'] and fe['observations']==t['finish_input'] and fe['output']==t['finish'],'finish source differs')
    require(t['preundo']['utc']<=pe['utc']<t['final_reads'][0]['utc']<=t['final_reads'][1]['utc']<=fe['utc'],'controller-source order wrong')
    item['controller_calls']=2
    seal=t['seal'];se=byid[seal.get('evidence_id',seal.get('id'))]
    for k in ('utc','presented_later','history_complete'):require(se[k]==seal[k],'seal source differs: '+k)
    before=seal.get('before_later',seal.get('seal_before_later'));require(se.get('before_later',se.get('seal_before_later')) is before,'seal source position differs')
    require(t['agent']['utc']<=seal['utc']<t['preundo']['utc'],'seal not between agent and pre-read')
    if before:require(t['later_phases'] and seal['utc']<t['later_phases'][0]['observation']['utc'],'post-seal edit order wrong')
    elif t['later_phases']:require(t['later_phases'][-1]['observation']['utc']<=seal['utc'],'included edit saved after seal')
    if t['assignment']['scenario']=='incomplete_history':require([v['command'] for v in t['later_phases']]==['set0','set1'] and seal['presented_later']==[] and seal['history_complete'] is False,'incomplete log control absent')
    item['seal_links']=1
    act=t['actuator']
    if act.get('evidence_id'):
     ae=byid[act['evidence_id']]
     for k in ('requested','fault'):require(ae.get(k)==act.get(k),'actuator source differs: '+k)
     require(ae.get('literal',ae.get('actual_literal'))==act.get('literal',act.get('actual_literal')),'actuator literal source differs')
    else:
     require(act.get('attempted',act.get('write_attempted')) is False and t['decision']['write'] is None,'unlogged actuator dispatch')
    actions=[e for e in es if e.get('trial_id')==t['trial_id'] and kind(e)=='action_attempt' and pe['utc']<e['utc']<t['final_reads'][0]['utc']]
    if site=='calendar':require(sum(e.get('label')=='undo_save' for e in actions)==int(t['decision']['write'] is not None),'Calendar undo save count differs')
    else:
     labels=[e.get('label') for e in actions if e.get('label','').startswith('undo single attempt')]
     for label in ('undo single attempt fill X','undo single attempt set Y'):require(labels.count(label)<=1,'Notion property update retried')
     if t['decision']['write'] is None:require(not labels,'Notion wrote after no-write decision')
    item['undo_dispatch_checks']=1
    lower=pe['utc']
    for i,o in enumerate(t['final_reads'],1):
     expected_label=('final_read_'+str(i)+'_reload') if site=='calendar' else ('final saved read '+str(i)+' reload')
     matches=[e for e in es if e.get('trial_id')==t['trial_id'] and kind(e)==('action_result' if site=='calendar' else 'action') and e.get('label')==expected_label and lower<e['utc']<o['utc']]
     require(len(matches)==1 and matches[0].get('error') is None,'distinct successful final reload not shown')
     item['final_reload_actions']+=1;lower=o['utc']
   except (ValueError,KeyError,TypeError) as ex:item['issues'].append({'issue':'controller/read action: '+str(ex)})
 if not args.allow_partial:
  require(len(results)==32 and all(sum(r['trial_id'].startswith(site+'-') for r in results)==16 for site in ('calendar','notion')),'full audit requires all 32 assignments')
 issues=[{'trial_id':r['trial_id'],**v} for r in results for v in r['issues']]
 output={'status':'FAIL' if issues else ('PASS_AVAILABLE_ROWS' if args.allow_partial else 'PASS'),'rows':results,'issues':issues,'source_files':source_files,'schema_checks':schema_checks,'saved_field_links':sum(r['saved_field_links'] for r in results),'final_reload_actions':sum(r['final_reload_actions'] for r in results),'controller_calls':sum(r['controller_calls'] for r in results),'seal_links':sum(r['seal_links'] for r in results),'undo_dispatch_checks':sum(r['undo_dispatch_checks'] for r in results),'limits':['Only available terminal rows are checked; assignment coverage and cleanup need separate checks.','Calendar Description uses the explicit visible-field read; its text is absent from the DOM snapshot.','This audit checks saved evidence and read actions, not server atomicity or true history completeness.']}
 args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n');print(json.dumps({k:output[k] for k in ['status','saved_field_links','final_reload_actions','controller_calls','issues']}))
 if issues:raise SystemExit(1)

if __name__=='__main__':main()
