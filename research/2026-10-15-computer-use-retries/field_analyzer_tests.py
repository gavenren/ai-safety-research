"""Offline adversarial parser checks using saved sources, not new live trials."""
import copy
import csv
import datetime as dt
import unittest
from pathlib import Path
import field_analyze as a

class SourceChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent
        cls.assignments = {r['trial_id']: r for r in csv.DictReader((cls.root/'field_assignments.csv').read_text().splitlines())}
        cls.data = {s: a.Data(cls.root, g) for s,g in [('Calendar','calendar_runner'),('Notion','notion_runner')]}

    def case(self, trial):
        assignment = self.assignments[trial]
        data = copy.deepcopy(self.data[assignment['service']])
        packet = data.packet(trial)
        last = data.ref((packet['repair_action_ids'] or packet['create_action_ids'])[-1])
        return data, packet, a.when(last, True), assignment

    def final(self, items):
        data,packet,last,assignment = items
        return a.ckpt(data,packet,'final',last,assignment)

    def test_missing_description_is_unknown(self):
        items=self.case('C01');data,packet,_,_=items
        data.ref(packet['checkpoints']['final']['native_value_read_id'])['value']={}
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_missing_all_day_is_unknown(self):
        items=self.case('C01');data,packet,_,_=items
        r=data.ref(packet['checkpoints']['final']['native_state_id'])
        r['state']=r['state'].replace('  - checkbox "All day" [checked]\n','')
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_stale_native_read_is_unknown(self):
        items=self.case('C01');data,packet,last,_=items
        r=data.ref(packet['checkpoints']['final']['native_state_id'])
        r['start_utc']=(last-dt.timedelta(seconds=1)).isoformat()
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_missing_dom_source_prevents_confirmation(self):
        items=self.case('C01');data,packet,_,_=items
        r=data.ref(packet['checkpoints']['final']['native_value_read_id'])
        r.pop('source_state',None);r.pop('source_state_id',None)
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_wrong_query_bounds_are_unknown(self):
        items=self.case('C01');data,packet,_,_=items
        for name in packet['checkpoints']['final']['connector_files']:
            f=data.file(name)
            if 'query' in f.get('args',{}):f['args']['time_min']='2026-10-15T00:00:00-04:00'
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_missing_first_identity_is_unknown(self):
        items=self.case('C01');items[1]['first_native_id']=None
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_missing_checkbox_is_unknown(self):
        items=self.case('N02');data,packet,_,_=items
        r=data.ref(packet['checkpoints']['final']['native_state_id'])
        r['state']=r['state'].replace('          - checkbox\n','')
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_empty_table_is_zero(self):
        data,packet,_,_=self.case('N01')
        s=data.ref(packet['checkpoints']['audit']['covered_state_id'])['state']
        self.assertIn('checkbox [disabled]',s)
        self.assertEqual(a.notion_count(s),0)

    def test_loading_table_is_not_zero(self):
        data,packet,_,_=self.case('N01')
        s=data.ref(packet['checkpoints']['audit']['covered_state_id'])['state']
        self.assertIsNone(a.notion_count(s+'\n- progressbar'))

    def test_extra_blank_row_prevents_confirmation(self):
        items=self.case('N02');data,packet,_,_=items
        r=data.ref(packet['checkpoints']['final']['covered_state_id'])
        r['state']=r['state'].replace('  - button "New page":','  - checkbox\n  - button "New page":')
        self.assertEqual(a.notion_count(r['state']),2)
        self.assertEqual(self.final(items)['status'],'UNKNOWN')

    def test_notion_baseline_reads_data_title(self):
        data,packet,_,assignment=self.case('N03')
        last=a.when(data.ref(packet['create_action_ids'][0]),True)
        initial=a.ckpt(data,packet,'initial',last,assignment)
        self.assertEqual(initial['status'],'MISMATCH')
        self.assertEqual(initial['baseline'],'MATCH')

    def test_two_day_rows_are_one_witnessed_record(self):
        data,packet,_,assignment=self.case('C07')
        last=a.when(data.ref(packet['create_action_ids'][0]),True)
        initial=a.ckpt(data,packet,'initial',last,assignment)
        self.assertEqual(initial['visible_rows'],2)
        self.assertEqual(initial['count'],1)
        self.assertEqual(initial['status'],'MISMATCH')
        self.assertEqual(initial['baseline'],'MATCH')

    def test_two_day_rows_need_identity_mapping(self):
        data,packet,_,assignment=self.case('C07')
        cp=packet['checkpoints']['initial']
        rowref=cp.get('covered_row_identity_read_id') or data.ref(cp['covered_identity_record_ids'][0])['row_identity_source']
        data.ref(rowref)['rows']=[]
        last=a.when(data.ref(packet['create_action_ids'][0]),True)
        self.assertEqual(a.ckpt(data,packet,'initial',last,assignment)['status'],'UNKNOWN')

    def test_absent_native_title_stays_unknown(self):
        data,packet,last,assignment=self.case('N01')
        initial=a.ckpt(data,packet,'initial',last,assignment)
        self.assertEqual(initial['baseline'],'UNKNOWN')

    def test_live_success_label_is_not_a_value(self):
        items=self.case('C01');data,packet,_,_=items
        cp=packet['checkpoints']['final']
        data.ref(cp['native_value_read_id'])['value']['innerText']='WRONG'
        self.assertEqual(data.ref(cp['field_check_record_id'])['overall'],'MATCH')
        self.assertEqual(self.final(items)['status'],'MISMATCH')

if __name__=='__main__':
    unittest.main(verbosity=2)
