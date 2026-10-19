"""Synthetic unit controls for the result grader, not website measurements."""
import copy,unittest
from improved_analyze import grade

class GradingControls(unittest.TestCase):
    def make(self):
        a={'trial_id':'unit-01','site':'unit','scenario':'control','rule':'checked_history','full_later':[],'presented_later':[],'history_complete':True,'fault':None,'seal_before_later':False,'marker':'unit'}
        def o(x,read):return {'x':x,'y':0,'identity':'unit-record','contract':True,'readId':read,'readAt':'2026-10-19T00:00:00Z','reloaded':True,'source':{'line':1,'sha256':'unit-fixture'}}
        pre=o(1,'pre');r={'trial_id':a['trial_id'],'assignment':a,'status':'valid','baseline':o(0,'initial'),'agent':o(1,'agent'),'later_phases':[],'preundo':pre,'prepare_input':{'initial':{'x':0,'y':0},'agent':{'x':1,'y':0},'current':{k:pre[k] for k in ['x','y','identity','contract','readId','readAt','reloaded']},'later':[],'historyComplete':True,'expectedIdentity':'unit-record'},'decision':{'status':'pending'},'final_reads':[o(0,'first'),o(0,'second')],'finish':{'status':'complete','reason':'unit'},'actuator':{'attempted':True,'literal':{'x':0,'y':0}}};return a,r
    def test_complete_requires_actual_fields(self):
        a,r=self.make();self.assertEqual(grade(r,a)['outcome'],'clean_completion');r['final_reads'][1]['x']=9;self.assertEqual(grade(r,a)['outcome'],'false_confirmation')
    def test_abstention_costs_remain_visible(self):
        a,r=self.make();r['finish']['status']='abstain';self.assertEqual(grade(r,a)['outcome'],'abstain_correct');r['final_reads'][0]['x']=9;self.assertEqual(grade(r,a)['outcome'],'unresolved')
    def test_unknown_does_not_infer_success(self):
        a,r=self.make();r['status']='unknown';r['final_reads']=[];self.assertEqual(grade(r,a)['outcome'],'unknown')
    def test_wrong_saved_setup_rejected(self):
        a,r=self.make();r['baseline']['x']=3
        with self.assertRaises(AssertionError):grade(r,a)
    def test_wrong_identity_rejected(self):
        a,r=self.make();r['final_reads'][1]['identity']='different'
        with self.assertRaises(AssertionError):grade(r,a)
    def test_presented_history_drift_rejected(self):
        a,r=self.make();r['prepare_input']['later']=['set1']
        with self.assertRaises(AssertionError):grade(r,a)

if __name__=='__main__':unittest.main()
