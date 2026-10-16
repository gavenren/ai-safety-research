"""Small semantic controls for the synthetic history model."""
import copy,json,tempfile,unittest
from pathlib import Path
from analyze import accepted,load_config,solve,trace

class SemanticControls(unittest.TestCase):
    def test_two_field_mixed_read(self):
        key,events=trace('10',((),(0,1),()),2,1)
        self.assertEqual(key,(2,2,1,False,True))
        self.assertTrue(accepted('values',key,2))
        self.assertFalse(accepted('full_revision',key,2))
    def test_intermediate_target_is_not_lost(self):
        key,_=trace('10',((1,1),(),()),2,1)
        self.assertTrue(key[3]);self.assertFalse(key[4])
    def test_repeated_flip_counts_as_two_writes(self):
        key,_=trace('11',((0,0),(),()),2,1)
        self.assertEqual(key[:3],(3,2,0))
        self.assertTrue(accepted('modulo_2',key,2))
        self.assertFalse(accepted('full_revision',key,2))
    def test_final_gap_changes_truth(self):
        key,_=trace('11',((),(),(0,)),2,1)
        self.assertTrue(key[3]);self.assertTrue(key[4]);self.assertNotEqual(key[0],3)
        self.assertTrue(accepted('partial_revision',key,2));self.assertFalse(accepted('atomic_final',key,2))
    def test_partial_counter_three_fields(self):
        key,_=trace('101',((),(0,1),(),()),3,1)
        self.assertFalse(key[3]);self.assertTrue(key[4]);self.assertEqual(key[2],0)
        self.assertTrue(accepted('partial_revision',key,3))
    def test_zero_write_controls(self):
        for d in (2,3):
            for r in (1,2,3):
                rows,terminal,stages,witnesses=solve(d,r,0)
                self.assertFalse(witnesses);self.assertEqual(len(terminal),2**d)
                for row in rows:
                    self.assertEqual(row['accepted'],1);self.assertEqual(row['wrong_at_decision'],0)
    def test_exact_small_counts(self):
        rows,*_=solve(2,1,1)
        self.assertEqual(rows[0]['total_histories'],108)
        self.assertEqual(next(x for x in rows if x['policy']=='atomic_final')['accepted'],27)
    def test_invalid_configuration(self):
        original=json.loads(Path(__file__).with_name('config.json').read_text())
        cases=[]
        for key,value in [('fields',[True]),('fields',[2,2]),('passes',[0]),('writes_per_gap',[3]),('seed',123),('random_sampling',0),('initial_revision',False)]:
            x=copy.deepcopy(original);x[key]=value;cases.append(x)
        x=copy.deepcopy(original);del x['target'];cases.append(x)
        x=copy.deepcopy(original);x['unplanned']=1;cases.append(x)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json'
            for case in cases:
                p.write_text(json.dumps(case))
                with self.subTest(case=case),self.assertRaises(ValueError):load_config(p)

if __name__=='__main__':unittest.main(verbosity=2)
