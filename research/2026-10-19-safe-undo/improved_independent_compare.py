"""Compare independent and primary results without importing either analyzer."""
import argparse,hashlib,json
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--package',type=Path,default=Path('.'));p.add_argument('--output',type=Path,default=Path('improved_independent_comparison.json'));a=p.parse_args()
 ip=a.package/'improved_independent_results.json';mp=a.package/'improved_results.json';ind=json.loads(ip.read_text());main=json.loads(mp.read_text());checks=[];issues=[]
 def check(label,x,y):
  checks.append(label)
  if x!=y:issues.append({'check':label,'independent':x,'primary':y})
 check('independent status',ind['status'],'PASS');check('primary status',main['status'],'PASS')
 ir={r['trial_id']:r for r in ind['rows']};mr={r['trial_id']:r for r in main['rows']};check('trial IDs',sorted(ir),sorted(mr))
 for key,r in ir.items():
  m=mr[key]
  for field in ('site','scenario','rule','outcome','target'):check(key+'/'+field,r[field],m[field])
  if r['status']=='valid':
   for field,other in [('finish_status','claim'),('final_reads','final'),('write_attempted','write_attempted'),('finish_reason','reason'),('y_target_mismatch','y_mismatch'),('prewrite_refusal','prewrite_refusal'),('fault_saved','fault_literal_observed')]:check(key+'/'+field,r[field],m[other])
   check(key+'/both-final-match',all(v==r['target'] for v in r['final_reads']),m['both_final_match_target'])
 def summary(rs):
  out={'planned':len(rs),'valid':sum(r['status']=='valid' for r in rs),'write_attempts':sum(r.get('write_attempted') is True for r in rs),'prewrite_refusals':sum(r.get('prewrite_refusal',False) for r in rs),'y_mismatches':sum(r.get('y_target_mismatch',False) for r in rs)}
  out.update({k:sum(r['outcome']==k for r in rs) for k in ['clean_completion','false_confirmation','unresolved','abstain_correct','unknown']});return out
 rows=list(ir.values());check('total',summary(rows),main['total'])
 for rule in ('baseline_log_provenance','checked_history'):
  check('rule/'+rule,summary([r for r in rows if r['rule']==rule]),main['by_rule'][rule])
  for site in ('calendar','notion'):check('site-rule/'+site+'/'+rule,summary([r for r in rows if r['site']==site and r['rule']==rule]),main['by_site'][site][rule])
 for pair in ind['pairs']:
  m=next(v for v in main['pairs'] if v['site']==pair['site'] and v['scenario']==pair['scenario'])
  check('pair/'+pair['site']+'/'+pair['scenario'],{'baseline':pair['outcomes']['baseline_log_provenance'],'improved':pair['outcomes']['checked_history'],'valid_pair':pair['paired_valid']},{k:m[k] for k in ('baseline','improved','valid_pair')})
 checked=[r for r in rows if r['rule']=='checked_history'];positive=[r for r in checked if r['scenario'] in ('control','independent_y','addition','assignment_return')];refusals=[r for r in checked if r['scenario'] in ('incomplete_history','prestate_mismatch')];fault=[r for r in checked if r['scenario'].startswith('wrong_')]
 hypotheses={'H1':{'false_confirmations':sum(r['outcome']=='false_confirmation' for r in checked),'valid':sum(r['status']=='valid' for r in checked),'unknown':sum(r['outcome']=='unknown' for r in checked)},'H2':{'planned_positive':len(positive),'clean_positive':sum(r['outcome']=='clean_completion' for r in positive),'unknown':sum(r['outcome']=='unknown' for r in positive)},'H3':{'planned':len(refusals),'observed_prewrite_refusals':sum(r.get('prewrite_refusal',False) for r in refusals)},'H4':{'planned':len(fault),'observed_refusals':sum(r.get('finish_status')=='abstain' for r in fault),'unknown':sum(r['outcome']=='unknown' for r in fault)},'H5':{'baseline_incomplete_or_wrong_save_false':sum(r['rule']=='baseline_log_provenance' and r['scenario'] in ('incomplete_history','wrong_x_save','wrong_y_save') and r['outcome']=='false_confirmation' for r in rows)}}
 check('hypotheses',hypotheses,main['hypotheses'])
 result={'status':'FAIL' if issues else 'PASS','comparisons':len(checks),'issues':issues,'inputs':{ip.name:digest(ip),mp.name:digest(mp)},'scope':'Exact comparison of measured per-trial results, denominators, site/rule counts, pairs and stated hypothesis measures.'};a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
 if issues:raise SystemExit(1)
if __name__=='__main__':main()
