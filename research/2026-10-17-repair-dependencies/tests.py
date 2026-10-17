import copy,unittest
from analyze import run,validate,EXPECTED,POLICIES
class SemanticTests(unittest.TestCase):
 def test_no_changes(self):
  for p in POLICIES:
   r=run(p,(1,0,1,0),[(),(),()]);self.assertEqual((r['success'],r['bad_union'],r['rounds']),(1,0,1))
 def test_fresh_token_old_source(self):
  r=run('refresh_cas',(1,0,1,0),[(1,),()]);self.assertEqual((r['success'],r['source_violation'],r['rejections']),(1,1,1))
 def test_fresh_token_old_permission(self):
  a=run('refresh_cas',(1,0,1,0),[(0,),()]);b=run('replan_cas',(1,0,1,0),[(0,),()]);self.assertEqual(a['permission_violation'],1);self.assertEqual((b['decision'],b['attempts'],b['rounds']),('read_denied',1,2))
 def test_missing_permission_dependency(self):
  a=run('source_only_guard',(1,0,1,0),[(0,)]);b=run('dependency_guard',(1,0,1,0),[(0,)]);self.assertEqual(a['permission_violation'],1);self.assertEqual(b['decision'],'exhausted')
 def test_unrelated_and_return(self):
  for word in [(2,),(1,1),(0,0)]:
   a=run('replan_cas',(1,0,1,0),[word]*3);b=run('dependency_guard',(1,0,1,0),[word]*3);self.assertEqual(a['decision'],'exhausted');self.assertEqual((b['decision'],b['bad_union']),('success',0))
 def test_collateral_uses_pre_effect_state(self):
  a=run('replace',(1,0,1,0),[(1,)]);self.assertEqual(a['collateral_fields'],['X']);self.assertEqual((a['source_violation'],a['final_state'][1],a['final_state'][2]),(1,0,0))
 def test_unconsumed_suffix(self):
  a=run('patch',(1,0,1,0),[(),(0,1)]);b=run('patch',(1,0,1,0),[()]);self.assertEqual(a,b)
 def test_read_denial_consumes_no_gap(self):
  r=run('dependency_guard',(1,0,1,0),[(0,),(1,1)]);self.assertEqual((r['decision'],r['background_writes']),('read_denied',1))
 def test_configuration(self):
  self.assertEqual(validate(copy.deepcopy(EXPECTED)),EXPECTED)
  bad=[]
  for k in EXPECTED:
   x=copy.deepcopy(EXPECTED);del x[k];bad.append(x)
  for k,v in [('random_sampling',0),('initial_permission',True),('attempt_budgets',[1,2,4]),('writes_per_gap',[False,1,2]),('extra',1)]:
   x=copy.deepcopy(EXPECTED);x[k]=v;bad.append(x)
  for x in bad:
   with self.assertRaises(ValueError):validate(x)
if __name__=='__main__':unittest.main()
