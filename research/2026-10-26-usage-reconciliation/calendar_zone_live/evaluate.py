"""Run one evidence check. No network calls or account writes."""
import argparse,json,copy
from pathlib import Path
from calendar_adapter import make_proof,sha

def evaluate(case,observation,zone,phase):
 z=copy.deepcopy(zone)
 c=case['condition']
 injection='none'
 if phase=='connector_only':z=None;injection='zone_not_returned_by_connector'
 elif phase=='assigned':
  if c=='missing_zone':z=None;injection='withheld_zone_object'
  elif c=='missing_end_zone':z.pop('end_observed_label',None);injection='removed_end_label'
  elif c=='incorrect_supplied_zone':
   z['observed_label']='(GMT-04:00) Eastern Time - New York'
   z['end_observed_label']=z['observed_label'];injection='replaced_labels_locally'
  elif c=='unverified_zone':z['verified']=False;injection='set_verified_false'
 try:
  proof=make_proof(case['payload'],observation,z,case['alias'],sha(case['payload']))
  result={'decision':'accept','proof':proof}
 except ValueError as exc:result={'decision':'reject','reason':str(exc)}
 required={k:v for k,v in case['payload'].items() if k!='timezone'}
 baseline=all(k in observation['fields'] and observation['fields'][k]==v for k,v in required.items()) and observation['fields'].get('status')=='confirmed'
 return dict(alias=case['alias'],condition=c,phase=phase,injection=injection,observation=observation,zone_input=z,result=result,field_only_baseline_accepts=baseline)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 x=json.loads(a.input.read_text());r=evaluate(**x);a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({'alias':r['alias'],'phase':r['phase'],'result':r['result']}))
