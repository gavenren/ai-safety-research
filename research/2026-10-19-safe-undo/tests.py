import itertools
import json
import unittest
from pathlib import Path
from analyze import run_case, validate, step, RULES

class Semantics(unittest.TestCase):
    def test_no_background(self):
        for x,y in itertools.product(range(2), repeat=2):
            self.assertTrue(all(o['clean_completion'] for o in run_case(x,y,[])['outcomes'].values()))
    def test_independent_y(self):
        c=run_case(0,0,['flip_y'])
        self.assertTrue(c['outcomes']['full_restore']['collateral_change'])
        self.assertTrue(all(c['outcomes'][r]['clean_completion'] for r in RULES if r!='full_restore'))
    def test_same_value_set(self):
        c=run_case(0,0,['set1'])
        self.assertEqual(c['before'],c['target'])
        self.assertEqual(c['revision_counts'],[0,1])
        self.assertTrue(c['outcomes']['value_guard']['new_damage'])
        self.assertTrue(c['outcomes']['revision_guard']['abstain_correct'])
        self.assertFalse(c['outcomes']['provenance']['changed'])
    def test_additive_inverse(self):
        for word in itertools.product(['add1','sub1','flip_y'],repeat=4):
            self.assertTrue(run_case(0,1,word)['outcomes']['subtract']['clean_completion'])
    def test_overwritten_contribution(self):
        c=run_case(1,0,['set0','add1'])
        self.assertEqual(c['before'],[1,0]);self.assertEqual(c['target'],[1,0])
        self.assertTrue(c['outcomes']['subtract']['new_damage'])
    def test_same_observation_different_target(self):
        a=run_case(0,0,['add1','sub1']);b=run_case(0,0,['set0','add1'])
        self.assertEqual(a['before'],b['before']);self.assertEqual(a['revision_counts'],b['revision_counts'])
        self.assertNotEqual(a['target'],b['target'])
    def test_each_command_and_partition(self):
        for x,y,cmd in itertools.product(range(2),range(2),['add1','sub1','set0','set1','flip_y']):
            c=run_case(x,y,[cmd])
            for o in c['outcomes'].values():
                self.assertEqual(sum(o[k] for k in ['clean_completion','false_confirmation','unresolved','abstain_correct']),1)
    def test_bad_config(self):
        c=json.loads(Path(__file__).with_name('config.json').read_text())
        validate(c)
        bad=[None,[],{},dict(c,extra=True),dict(c,agent_increment=True),dict(c,lengths=[0,1])]
        for k in c:
            q=c.copy();del q[k];bad.append(q)
        for q in bad:
            with self.assertRaises(ValueError):validate(q)
        self.assertEqual(len(bad),13)
    def test_bad_command(self):
        with self.assertRaises(ValueError):step([0,0],'unknown')

if __name__=='__main__': unittest.main()
