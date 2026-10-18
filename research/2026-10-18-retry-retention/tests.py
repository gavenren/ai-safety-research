import copy,json,unittest
from pathlib import Path
from analyze import simulate,validate,POLICIES

def case(T,D,s,pol,codes,B=None):return simulate('test',T,D,D if B is None else B,s,pol,codes)
class Semantics(unittest.TestCase):
 def test_all_drop_and_immediate_success(self):
  for pol in POLICIES:
   self.assertTrue(case(2,3,1,pol,(0,0,0))['missed'])
   r=case(2,3,1,pol,(2,8,8));self.assertEqual((r['send_count'],r['effect_count'],r['confirmed']),(1,1,True))
 def test_expiry_boundary(self):
  for s,expected in [(1,1),(2,2),(3,2)]:
   r=case(2,0,s,'stable_key',(1,2,0));self.assertEqual(r['effect_count'],expected)
 def test_hit_does_not_renew(self):
  r=case(2,0,1,'stable_key',(1,1,2));self.assertEqual((r['cache_hits'],r['effect_count'],r['expired_keys']),(1,2,1))
 def test_reordered_delivery_after_receipt(self):
  r=case(2,3,1,'send_cutoff',(7,2,0));self.assertEqual(r['arrived_slots'],[1,0]);self.assertEqual(r['first_receipt_time'],1)
  self.assertTrue(r['future_only_false']);self.assertTrue(r['late_duplicate']);self.assertEqual(r['effect_count'],2)
 def test_same_tick_receipt_then_duplicate(self):
  r=case(1,2,1,'new_key',(6,4,0));self.assertEqual(r['effect_count'],2);self.assertTrue(r['late_duplicate']);self.assertTrue(r['future_only_false'])
 def test_receiver_deadline_equality(self):
  r=case(2,2,1,'receiver_cutoff',(6,0,0));self.assertEqual((r['effect_count'],r['receiver_rejections'],r['confirmed']),(0,1,False))
 def test_margin_initial_and_strict_equality(self):
  r=case(2,3,1,'delay_margin',(8,2,2));self.assertEqual(r['sent_slots'],[0]);self.assertEqual(r['effect_count'],1)
  r=case(3,2,1,'delay_margin',(1,6,0));self.assertEqual(r['sent_slots'],[0]);self.assertFalse(r['duplicate'])
 def test_broken_bound(self):
  r=case(3,2,1,'delay_margin',(1,6,0),B=1);self.assertEqual(r['effect_count'],2)
 def test_permanent_preserves_identity(self):
  r=case(1,3,3,'permanent',(1,1,2));self.assertEqual((r['effect_count'],r['cache_hits']),(1,2))
 def test_receipt_is_not_global_count(self):
  r=case(1,0,1,'stable_key',(1,2,0));self.assertEqual(r['first_receipt_effect_id'],2);self.assertTrue(r['wrong_at_receipt']);self.assertFalse(r['future_only_false'])
 def test_configuration_rejects_missing_and_malformed(self):
  c=json.loads(Path('config.json').read_text());validate(c)
  for key in c:
   b=copy.deepcopy(c);del b[key]
   with self.assertRaises(ValueError):validate(b)
  for key,value in [('slots',True),('retention_ticks',[0]),('delay_bounds',[True]),('spacings',[2,1]),('policies',[]),('drain_after_receipt',1),('primary',{'retention':2}),('stress',{})]:
   b=copy.deepcopy(c);b[key]=value
   with self.assertRaises(ValueError):validate(b)
if __name__=='__main__':unittest.main()
