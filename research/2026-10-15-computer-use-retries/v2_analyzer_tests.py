#!/usr/bin/env python3
"""Small parser and evidence-boundary checks. These are not website trials."""
import base64
import unittest
from v2_analyze import observation, native_identity, calendar_fields, calendar_editor, state_identities, is_create, is_repair

TOKEN='V2-RETRY-20261015-X01'


def nstate(rows):
    s='- banner:\n  - button "Private"\n  - button "Share"\n  - button "Actions"\n- main:\n  - tab "All" [selected]\n  - button "Settings"\n  - button "Automations"\n'
    s+='  - checkbox'+(' [disabled]' if not rows else '')+'\n  - button "Name"\n'
    for row in rows:
        s+='  - checkbox\n  - button'+(' "'+row+'"' if row else '')+'\n'
    return s+'  - button "New page"\n'


def cstate(rows):
    s='- main:\n  - heading "Search results. '+str(len(rows))+' events found."\n'
    if not rows:return s+'  - generic: No results found\n'
    s+='  - grid:\n'
    for row in rows:
        s+='    - row "All day, '+row+', Test account, No location":\n      - gridcell "'+row+'"\n'
    return s


def calrec(rows, year=2026):
    return {'state':cstate(rows),'url':f'https://calendar.google.com/calendar/u/0/r/search?q={TOKEN}&start={year}1001&end={year}1031'}


class EvidenceTests(unittest.TestCase):
    def test_blank_notion_is_an_operation_record(self):
        p=observation({'state':nstate(['',TOKEN])},'Notion',TOKEN)
        self.assertEqual((p['exact'],p['total'],p['partial']),(1,2,1))

    def test_disabled_empty_notion_header_is_zero(self):
        p=observation({'state':nstate([])},'Notion',TOKEN)
        self.assertTrue(p['ready']);self.assertEqual(p['total'],0)

    def test_notion_loading_positive_not_ready(self):
        p=observation({'state':nstate([TOKEN])+'- progressbar\n'},'Notion',TOKEN)
        self.assertFalse(p['ready']);self.assertIsNone(p['exact'])

    def test_draft_is_not_exact_title(self):
        p=observation(calrec([TOKEN+'-DRAFT',TOKEN]),'Calendar',TOKEN)
        self.assertEqual((p['exact'],p['total'],p['partial']),(1,2,1))

    def test_calendar_sidebar_loading_blocks_readiness(self):
        r=calrec([TOKEN]);r['state']+='- complementary "Tasks":\n  - progressbar\n'
        self.assertFalse(observation(r,'Calendar',TOKEN)['ready'])

    def test_background_result_under_editor_not_ready(self):
        r=calrec([TOKEN]);r['state']+='- main:\n  - heading "Event edit page"\n'
        self.assertFalse(observation(r,'Calendar',TOKEN)['ready'])

    def test_wrong_date_range_unknown(self):
        self.assertIsNone(observation(calrec([TOKEN],year=2025),'Calendar',TOKEN)['view'])

    def test_native_and_service_event_id_agree(self):
        encoded=base64.urlsafe_b64encode(b'event123 synthetic@example.com').decode().rstrip('=')
        self.assertEqual(native_identity('https://calendar.google.com/calendar/u/0/r/eventedit/'+encoded,'Calendar'),'event123')
        self.assertEqual(native_identity('https://www.google.com/calendar/event?eid='+encoded,'Calendar'),'event123')

    def test_private_alias_native_and_api_agree(self):
        alias='record-'+'a'*20
        self.assertEqual(native_identity('https://calendar.google.com/calendar/u/0/r/eventedit/'+alias,'Calendar'),alias)
        self.assertEqual(native_identity(alias,'Calendar'),alias)

    def test_notion_identity_from_visible_link(self):
        ident='a'*32
        r={'state':'- link "Open in full page":\n  - /url: /p/'+ident+'?pvs=23'}
        self.assertEqual(state_identities(r,'Notion'),{ident})

    def test_cal_normalized_fields_require_marker(self):
        e={'summary':TOKEN,'description':TOKEN,'start':'2026-10-14T00:00:00','end':'2026-10-15T00:00:00',
           'visibility':'private','transparency':'transparent','attendees':[],'location':None,'recurrence':None,'recurring_event_id':None,'hangout_link':None,
           'reminders':{'use_default':False,'overrides':[]}}
        self.assertTrue(calendar_fields(e,TOKEN))
        e['description']='other';self.assertFalse(calendar_fields(e,TOKEN))

    def test_whitespace_marker_has_unknown_strict_match(self):
        e={'summary':TOKEN,'description':TOKEN+'\n\n','start':'2026-10-14T00:00:00','end':'2026-10-15T00:00:00',
           'visibility':'private','transparency':'transparent','attendees':[],'location':None,'recurrence':None,'recurring_event_id':None,'hangout_link':None,
           'reminders':{'use_default':False,'overrides':[]}}
        self.assertIsNone(calendar_fields(e,TOKEN))

    def test_missing_required_service_fields_unknown(self):
        e={'summary':TOKEN,'description':TOKEN,'start':'2026-10-14T00:00:00','end':'2026-10-15T00:00:00',
           'visibility':'private','transparency':'transparent','attendees':[],'location':None,'recurrence':None,'recurring_event_id':None,'hangout_link':None,
           'reminders':{'use_default':False,'overrides':[]}}
        for key in ('reminders','start','end','location','recurrence','recurring_event_id','hangout_link'):
            incomplete=e.copy();del incomplete[key]
            self.assertIsNone(calendar_fields(incomplete,TOKEN))

    def test_cal_wrong_exclusive_end_fails(self):
        e={'summary':TOKEN,'description':TOKEN,'start':'2026-10-14T00:00:00','end':'2026-10-14T00:00:00',
           'visibility':'private','transparency':'transparent','attendees':[],'location':None,'recurrence':None,'recurring_event_id':None,'hangout_link':None,
           'reminders':{'use_default':False,'overrides':[]}}
        self.assertFalse(calendar_fields(e,TOKEN))

    def test_mutation_labels_separate_menu_and_create(self):
        self.assertTrue(is_create({'kind':'action','label':'initial New blank'}))
        self.assertFalse(is_create({'kind':'action','label':'open New options'}))
        self.assertTrue(is_repair({'kind':'action','label':'assign exact title once inline'}))
        self.assertFalse(is_repair({'kind':'action','label':'open inline title repair'}))
        self.assertTrue(is_repair({'kind':'action','label':'save_repair_once'}))
        self.assertTrue(is_repair({'kind':'action','label':'assign full exact title once to inline same-ID row'}))


if __name__=='__main__':unittest.main(verbosity=2)
