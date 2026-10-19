"""Compare primary JSON with independently derived live outcomes."""
import argparse,json,hashlib
from collections import Counter,defaultdict
from pathlib import Path


def main():
 p=argparse.ArgumentParser();p.add_argument('--main',type=Path,required=True);p.add_argument('--independent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 primary=json.loads(a.main.read_text());audit=json.loads(a.independent.read_text());assert audit['status']=='PASS'
 own=audit['rows'];assert len(own)==52
 byid={r['trial_id']:r for r in primary['outcomes']};assert len(byid)==len(own)
 counts=Counter();sites=defaultdict(Counter);rules=defaultdict(Counter);comparisons=0
 for r in own:
  q=byid[r['trial_id']]
  for key in ('kind','terminal_status'):assert r[key]==q[key];comparisons+=1
  counts['assigned']+=1;sites[r['site']]['assigned']+=1
  counts[r['kind']+'_assigned']+=1;sites[r['site']][r['kind']+'_assigned']+=1
  if r['kind']=='core':rules[r['rule']]['assigned']+=1
  counts[r['terminal_status']]+=1;sites[r['site']][r['terminal_status']]+=1
  counts['cleanup_'+r['cleanup_status']]+=1
  if r['terminal_status']!='valid':
   assert q['outcome'] is None;comparisons+=1
   counts[r['kind']+'_unscored']+=1;sites[r['site']][r['kind']+'_unscored']+=1
   if r['kind']=='core':rules[r['rule']]['unscored']+=1
   continue
  for ok,pk in [('pre','preundo'),('target','target'),('final','final')]:assert r[ok]==q[pk];comparisons+=1
  if r['kind']=='diagnostic':
   assert q['outcome'] is None;counts['diagnostics_valid']+=1;sites[r['site']]['diagnostics_valid']+=1;comparisons+=1;continue
  label='abstain_correct' if r['outcome']=='correct_state_abstention' else r['outcome']
  assert q['outcome']==label;assert q['decision_saved']==r['final_matches_decision'];assert q['collateral_y']==r['y_target_mismatch'];comparisons+=3
  assert r['decision_matches_rule'];comparisons+=1
  counts['core_valid']+=1;counts[label]+=1;sites[r['site']]['core_valid']+=1;sites[r['site']][label]+=1
  rules[r['rule']]['valid']+=1;rules[r['rule']][label]+=1
  counts['decision_saved']+=int(r['final_matches_decision']);counts['collateral_y']+=int(r['y_target_mismatch'])
 assert dict(counts)==primary['counts'];comparisons+=len(counts)
 assert {k:dict(v) for k,v in sites.items()}==primary['sites'];comparisons+=sum(map(len,sites.values()))
 assert {k:dict(v) for k,v in rules.items()}==primary['rules'];comparisons+=sum(map(len,rules.values()))
 result={'status':'PASS','trial_rows':len(own),'scalar_or_vector_checks':comparisons,'counts':dict(counts),'source_hashes':{'primary':hashlib.sha256(a.main.read_bytes()).hexdigest(),'independent':hashlib.sha256(a.independent.read_bytes()).hexdigest()},'limits':['Equal results do not establish population rates or native field history.','Evidence extraction and native source checks are separate.']}
 a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
