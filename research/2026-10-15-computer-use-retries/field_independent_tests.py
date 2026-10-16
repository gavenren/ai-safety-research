#!/usr/bin/env python3
"""Perturb saved inputs to test the independent parser's evidence gates."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('independent',HERE/'field_independent_replay.py')
i=importlib.util.module_from_spec(spec)
spec.loader.exec_module(i)

class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar=i.Evidence(HERE,'calendar_runner')
        cls.notion=i.Evidence(HERE,'notion_runner')

    def c1(self):
        e=copy.deepcopy(self.calendar)
        return e,e.packets['C01']

    def test_label_is_not_value(self):
        e,p=self.c1();cp=p['checkpoints']['initial']
        e.byid[cp['field_check_record_id']]['overall']='MATCH'
        self.assertEqual(i.check_stage(e,p,'initial')['status'],'MISMATCH')

    def test_missing_connector_description_unknown(self):
        e,p=self.c1();cp=p['checkpoints']['final']
        read=next(e.records[f] for f in cp['connector_files'] if 'read_event' in e.records[f].get('tool',''))
        del read['result']['structuredContent']['description']
        self.assertEqual(i.check_stage(e,p,'final')['status'],'UNKNOWN')

    def test_saved_wrong_description_fails(self):
        e,p=self.c1();cp=p['checkpoints']['final']
        read=next(e.records[f] for f in cp['connector_files'] if 'read_event' in e.records[f].get('tool',''))
        read['result']['structuredContent']['description']=p['token']+'-WRONG'
        self.assertEqual(i.check_stage(e,p,'final')['status'],'MISMATCH')

    def test_unbounded_search_unknown(self):
        e,p=self.c1();cp=p['checkpoints']['final']
        search=next(e.records[f] for f in cp['connector_files'] if 'search_events' in e.records[f].get('tool',''))
        search['args'].pop('time_max')
        self.assertEqual(i.check_stage(e,p,'final')['status'],'UNKNOWN')

    def test_stale_native_source_unknown(self):
        e,p=self.c1();cp=p['checkpoints']['final']
        native=e.byid[cp['native_state_id']]
        for k in ('at_utc','start_utc','end_utc','started_at_utc','ended_at_utc'):
            if k in native:native[k]='2026-01-01T00:00:00Z'
        self.assertEqual(i.check_stage(e,p,'final')['status'],'UNKNOWN')

    def test_wrong_native_identity_does_not_confirm(self):
        e,p=self.c1();cp=p['checkpoints']['final']
        native=e.byid[cp['native_state_id']]
        native['url']='https://calendar.google.com/calendar/u/0/r/eventedit/record-00000000000000000000'
        self.assertNotEqual(i.check_stage(e,p,'final')['status'],'MATCH')

    def test_multi_day_one_record(self):
        p=self.calendar.packets['C07'];r=i.check_stage(self.calendar,p,'initial')
        self.assertEqual(r['rendered_rows'],2)
        self.assertEqual(r['count'],1)
        self.assertEqual(r['status'],'MISMATCH')

    def test_missing_first_record_not_false_match(self):
        p=self.notion.packets['N01'];r=i.check_stage(self.notion,p,'initial')
        self.assertEqual(r['baseline'],'UNKNOWN')
        self.assertEqual(r['status'],'UNKNOWN')

    def test_native_title_is_not_column_header(self):
        p=self.notion.packets['N03'];r=i.check_stage(self.notion,p,'initial')
        self.assertEqual(r['ui']['title'],p['token'])
        self.assertEqual(r['baseline'],'MATCH')

    def test_loading_native_read_unknown(self):
        e=copy.deepcopy(self.notion);p=e.packets['N03']
        e.byid[p['checkpoints']['final']['native_state_id']]['state']+='\n- progressbar'
        self.assertEqual(i.check_stage(e,p,'final')['status'],'UNKNOWN')

    def test_missing_copy_action_breaks_identity_witness(self):
        e=copy.deepcopy(self.notion);p=e.packets['N02']
        for rid in p['checkpoints']['final']['covered_identity_record_ids']:
            e.byid[rid].pop('copy_action_id',None)
        self.assertNotEqual(i.check_stage(e,p,'final')['status'],'MATCH')

    def test_empty_table_disabled_header_is_zero(self):
        p=self.notion.packets['N01'];cp=p['checkpoints']['final']
        t=i.notion_table(self.notion.get(cp['covered_state_id'])['state'])
        self.assertTrue(t['ready']);self.assertEqual(t['count'],0)

if __name__=='__main__':
    unittest.main(verbosity=2)
