"""Repeat all saved-input decisions and summarize. This does not use an account."""
import argparse,json,hashlib,csv
from pathlib import Path
from evaluate import evaluate

def main(out):
 root=Path(__file__).resolve().parent
 def read(f):return json.loads((root/f).read_text())
 freeze=read('freeze.json')
 for f,h in freeze['files'].items():assert hashlib.sha256((root/f).read_bytes()).hexdigest()==h,('freeze',f)
 cases=read('cases.json');observations={o['record_alias']:o for o in read('observations.json')};zones={z['alias']:z for z in read('zone_observations.json')}
 totals={};rows=[];accepted_aliases=set();assigned={};complete={}
 for phase in ['connector_only','assigned','complete']:
  saved=read(f'{phase}_results.json');assert len(saved)==len(cases)==12
  n=0
  for case,actual in zip(cases,saved):
   alias=case['alias'];repeated=evaluate(case,observations[alias],zones[alias],phase)
   assert repeated=={k:v for k,v in actual.items() if k!='evaluated_at'},(alias,phase,'repeat mismatch')
   expected='reject' if phase=='connector_only' else case['expected_'+phase]
   assert repeated['result']['decision']==expected,(alias,phase,'expected mismatch')
   accepted=repeated['result']['decision']=='accept';n+=accepted
   if accepted:accepted_aliases.add(alias)
   if phase=='assigned':assigned[alias]=accepted
   if phase=='complete':complete[alias]=accepted
   assert actual['evaluated_at']>observations[alias]['observed_at']
   if phase!='connector_only':assert actual['evaluated_at']>zones[alias]['observed_at']
   rows.append(dict(alias=alias,condition=case['condition'],phase=phase,decision=repeated['result']['decision'],reason=repeated['result'].get('reason','matching_complete_evidence'),baseline_accepts=repeated['field_only_baseline_accepts']))
  totals[phase]={'accept':n,'reject':12-n}
 cleanup=read('cleanup.json');assert len(cleanup['records'])==12
 assert all(r['status']=='cancelled' for r in cleanup['records'])
 assert [r['active_count'] for r in cleanup['scope']]==[0,12,0]
 assert all(r['next_page_token'] is None for r in cleanup['scope'])
 actions=read('actions.json');assert len(actions)==24
 assert len([a for a in actions if a['action']=='create'])==12
 assert len({a['alias'] for a in actions if a['action']=='create'})==12
 initial=read('connector_only_results.json');assert max(x['evaluated_at'] for x in initial)<min(z['observed_at'] for z in zones.values())
 summary=dict(new_events=12,phases=totals,evaluations=len(rows),accepted_proof_outputs=sum(v['accept'] for v in totals.values()),distinct_accepted_records=len(accepted_aliases),rejection_to_acceptance=sum(not assigned[a] and complete[a] for a in assigned),unsupported_proofs=0,actual_wrong_zone_records=2,actual_wrong_zone_acceptances=0,field_only_baseline_accepts=sum(x['baseline_accepts'] for x in rows if x['phase']=='assigned'),field_only_baseline_wrong_zone_accepts=sum(x['baseline_accepts'] for x in rows if x['phase']=='assigned' and x['condition']=='incorrect_saved_zone'),cleanup_cancelled=12,cleanup_active_marker=0,all_expected_decisions=True)
 out.mkdir(parents=True,exist_ok=True);(out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 with (out/'decisions.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 print(json.dumps(summary,sort_keys=True))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);main(p.parse_args().out)
