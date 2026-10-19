import copy
import unittest
from live_analyze import analyze, apply, grade

class LiveEvidenceTests(unittest.TestCase):
    def test_fixed_command_target(self):
        self.assertEqual(apply([0,0],'sub1'),[-1,0])
        self.assertEqual(apply([0,0],'set0'),[0,0])
        self.assertEqual(apply(apply([0,0],'set0'),'set1'),[1,0])
    def test_outcomes_keep_refusal_separate(self):
        self.assertEqual(grade('complete',[0,0],[1,0]),'false_confirmation')
        self.assertEqual(grade('abstain',[0,0],[1,0]),'unresolved')
        self.assertEqual(grade('abstain',[1,0],[1,0]),'abstain_correct')
        self.assertEqual(grade('complete',[1,0],[1,0]),'clean_completion')
    def test_missing_and_duplicate_evidence_rejected(self):
        a={'trial_id':'a','site':'calendar','kind':'core','rule':'full_restore','history':'control','token':'TEMP','later':[]}
        t={**a,'record_alias':None,'terminal_status':'interrupted','reason':'Test fixture, no account access','cleanup':{'status':'not_created'}}
        self.assertEqual(analyze([a],[t])['counts']['interrupted'],1)
        for rows in ([],[t,t]):
            with self.assertRaises(AssertionError):analyze([a],rows)
    def test_empty_and_stale_fields_rejected(self):
        a={'trial_id':'a','site':'notion','kind':'core','rule':'full_restore','history':'control','token':'TEMP','later':[]}
        o={'x':0,'y':0,'record_alias':'r1','token':'TEMP','identity_ok':True,'contract_ok':True,'reloaded':True,'evidence_id':'test','utc':'test'}
        t={**a,'record_alias':'r1','terminal_status':'valid','reason':None,'baseline':o,'agent':{**o,'x':1},'later':[],'preundo':{**o,'x':1},'decision':{'status':'complete','x':0,'y':0},'decision_evidence_id':'test-decision','final':o,'cleanup':{'status':'trashed','active_matches':0,'evidence_ids':['test-cleanup']}}
        self.assertEqual(analyze([a],[t])['counts']['clean_completion'],1)
        for key,value in [('x',None),('reloaded',False),('identity_ok',False),('record_alias','other')]:
            bad=copy.deepcopy(t);bad['baseline'][key]=value
            with self.assertRaises(AssertionError):analyze([a],[bad])

if __name__=='__main__':unittest.main()
