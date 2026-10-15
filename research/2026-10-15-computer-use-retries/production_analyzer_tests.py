#!/usr/bin/env python3
"""Adversarial parser checks for unknown states, repeated labels, and late audits.

These author checks are not the independent review. They use synthetic strings
that are not study observations and are never included in study trial counts.
"""
import unittest
import production_analyze as a

TOKEN='PROD-RETRY-20261015-N01'
CTOKEN='PROD-RETRY-20261015-C01'


def notion(names=(),view='All'):
    header='''- banner:
  - button "Private":
  - button "Share":
  - button "Actions":
- main:
  - tablist:
    - tab "VIEW" [selected]:
  - button "Settings":
  - button "Automations":
  - button "New"
  - checkbox DISABLED
  - button "Name":
  - button "Add property":
'''.replace('VIEW',view).replace('DISABLED','' if names else '[disabled]')
    for name in names:
        header+='  - checkbox\n  - button'+(' "'+name+'":' if name else '')+'\n'
        header+='    - generic: '+name+'\n'
    return header+'  - button "New page":\n- status\n'


def cal(n=0):
    head='- main:\n  - heading "Search results. '+str(n)+' events found." [level=1]\n'
    if not n:
        return head+'  - generic: No results found\n'
    head+='  - grid:\n    - rowgroup:\n'
    for _ in range(n):
        head+='      - row "Monday, January 3, 2000 11am to 11:05am, '+CTOKEN+', ACCOUNT, No location":\n'
        head+='        - gridcell "11am to 11:05am, '+CTOKEN+', ACCOUNT, No location":\n'
        head+='          - button "11am to 11:05am, '+CTOKEN+', ACCOUNT, No location": '+CTOKEN+'\n'
    return head


def obs(state,url=''):
    return {'state':state,'url':url}


def curl(token=CTOKEN,dates=True):
    return 'https://calendar.google.com/calendar/u/0/r/search?q='+token+('&start=20000101&end=20000131' if dates else '')


class ParserTests(unittest.TestCase):
    def test_notion_exact_rows_not_echoes(self):
        got=a.parse_observation(obs(notion([TOKEN,TOKEN])), 'Notion',TOKEN)
        self.assertTrue(got['ready']);self.assertEqual(got['count'],2)

    def test_notion_blank_is_partial(self):
        got=a.parse_observation(obs(notion([TOKEN,''])), 'Notion',TOKEN)
        self.assertEqual(got['count'],1);self.assertEqual(got['partial'],1)

    def test_notion_loading_positive_unknown(self):
        state=notion([TOKEN],'Hidden').replace('  - button "Settings":\n','')
        got=a.parse_observation(obs(state),'Notion',TOKEN)
        self.assertFalse(got['ready']);self.assertIsNone(got['count'])

    def test_notion_peek_is_not_ready(self):
        got=a.parse_observation(obs(notion([TOKEN])+'- region "Side Peek":\n'),'Notion',TOKEN)
        self.assertIsNone(got['count'])

    def test_notion_missing_empty_marker_unknown(self):
        got=a.parse_observation(obs(notion().replace('[disabled]','')),'Notion',TOKEN)
        self.assertIsNone(got['count'])

    def test_notion_input_mention_is_not_a_row(self):
        state=notion().replace('- main:','- main:\n  - textbox: '+TOKEN)
        got=a.parse_observation(obs(state),'Notion',TOKEN)
        self.assertEqual(got['count'],0)

    def test_calendar_row_is_counted_once(self):
        got=a.parse_observation(obs(cal(2),curl()),'Google Calendar',CTOKEN)
        self.assertTrue(got['ready']);self.assertEqual(got['count'],2)

    def test_calendar_loading_positive_unknown(self):
        got=a.parse_observation(obs(cal(1)+'- progressbar\n',curl()),'Google Calendar',CTOKEN)
        self.assertIsNone(got['count'])

    def test_calendar_sidebar_progressbar_keeps_strict_gate(self):
        state='- progressbar [observed outside retained task region]\n'+cal()
        self.assertIsNone(a.parse_observation(obs(state,curl()),'Google Calendar',CTOKEN)['count'])

    def test_calendar_loading_negative_unknown(self):
        got=a.parse_observation(obs(cal()+'- generic: Searching...\n',curl()),'Google Calendar',CTOKEN)
        self.assertIsNone(got['count'])

    def test_calendar_basic_search_loses_scope(self):
        got=a.parse_observation(obs(cal(),curl(dates=False)),'Google Calendar',CTOKEN)
        self.assertIsNone(got['count'])

    def test_calendar_wrong_token_unknown(self):
        got=a.parse_observation(obs(cal(),curl('WRONG')),'Google Calendar',CTOKEN)
        self.assertIsNone(got['count'])

    def test_calendar_heading_does_not_prove_empty(self):
        state='- main:\n  - heading "Search results. 0 events found." [level=1]\n'
        self.assertIsNone(a.parse_observation(obs(state,curl()),'Google Calendar',CTOKEN)['count'])

    def test_alias_keeps_identity_after_title_change(self):
        link='- region "Side Peek":\n  - link "Open in full page":\n    - /url: /p/PATH?pvs=23\n'
        first=a.notion_page_links(link.replace('PATH','record-0123456789abcdef0123'))
        later=a.notion_page_links(link.replace('PATH',TOKEN+'-record-0123456789abcdef0123'))
        self.assertEqual(first[0][0],later[0][0])

    def test_native_id_keeps_identity_after_title_change(self):
        raw='0123456789abcdef0123456789abcdef'
        link='- link "Open in full page":\n  - /url: /p/'+TOKEN+'-'+raw+'?pvs=23'
        self.assertEqual(a.notion_page_links(link)[0][0],raw)

    def test_raw_event_search_not_declared_count(self):
        raw={'records': [{'id':'x','summary':CTOKEN,'start':'s','end':'e'}], 'target_count':999}
        self.assertEqual(len(list(a.event_objects(raw))),1)

    def test_calendar_clock_remains_unknown(self):
        e={'summary':CTOKEN,'start':'2000-01-03T11:00:00-05:00','end':'2000-01-03T11:05:00-05:00',
           'visibility':'private','transparency':'transparent','description':'\n\n',
           'reminders':{'use_default':False,'overrides':[]}}
        self.assertIsNone(a.field_quality(e,CTOKEN))
        e['attendees']=[{'email':'test@example.com'}]
        self.assertFalse(a.field_quality(e,CTOKEN))

    def audit_fixture(self, decision='unresolved', audit_names=None):
        def record(id_,typ,phase,t,**extra):
            stamp='2026-10-15T20:00:'+str(t).zfill(2)+'.000+00:00'
            return dict(record_id=id_,trial_id='N01',token=TOKEN,type=typ,phase=phase,
                        start_utc=stamp,end_utc=stamp,tab_role='observer',**extra)
        rs=[record('b1','observation','baseline_writer',0,state=notion()),
            record('b2','observation','baseline_observer',1,state=notion()),
            record('w','action','initial_create',2,action='click New',error=None),
            record('r1','action','first_observer_reload',4,action='reload',error=None),
            record('z','observation','first_observer',5,state=notion()),
            record('d','decision','decision',6,decision_utc='2026-10-15T20:00:06.000+00:00',decision=decision,observed_count=0,evidence_record_ids=['z'],initial_request_record_id='w',retry_request_record_id=None),
            record('r2','action','audit_reload',7,action='reload',error=None),
            record('audit','observation','audit_observer',8,state=notion([TOKEN] if audit_names is None else audit_names)),
            record('p','observation','audit_identity',9,state='- link "Open in full page":\n  - /url: /p/'+TOKEN+'-0123456789abcdef0123456789abcdef?pvs=23'),
            record('trash','action','cleanup',10,action='Move to Trash',error=None),
            record('r3','action','cleanup_reload',11,action='reload',error=None),
            record('clean','observation','cleanup_observer',12,state=notion())]
        rs[0]['tab_role']='writer';rs[2]['tab_role']='writer'
        if decision=='confirmed':
            next(r for r in rs if r['record_id']=='z')['state']=notion([TOKEN])
            next(r for r in rs if r['record_id']=='d')['observed_count']=1
        return rs

    def analyze_fixture(self,rs):
        assignment=dict(trial_id='N01',site='Notion',token=TOKEN,block='1',rule='Scope',view='All')
        return a.derive_trial(assignment,rs,[])

    def test_audit_cannot_repair_unresolved_decision(self):
        rs=self.audit_fixture()
        assignment=dict(trial_id='N01',site='Notion',token=TOKEN,block='1',rule='Scope',view='All')
        got=a.derive_trial(assignment,rs,[])
        self.assertEqual(got['audit_count'],1)
        self.assertEqual(got['decision'],'unresolved')
        self.assertFalse(got['clean_confirmation'])

    def test_creation_link_cannot_replace_post_decision_identity(self):
        rs=self.audit_fixture(decision='confirmed')
        link=next(r for r in rs if r['record_id']=='p')
        link.update(phase='initial_create_title_after',start_utc='2026-10-15T20:00:03.000+00:00',end_utc='2026-10-15T20:00:03.000+00:00')
        got=self.analyze_fixture(rs)
        self.assertEqual(got['browser_audit_count'],1)
        self.assertEqual(got['distinct_record_ids'],0)
        self.assertIsNone(got['audit_count'])
        self.assertIsNone(got['clean_confirmation'])
        self.assertIsNone(got['false_confirmation'])

    def test_identity_conflict_is_unknown_not_proven_duplicate(self):
        got=self.analyze_fixture(self.audit_fixture(decision='confirmed',audit_names=[TOKEN,TOKEN]))
        self.assertEqual(got['browser_audit_count'],2)
        self.assertEqual(got['distinct_record_ids'],1)
        self.assertIsNone(got['audit_count'])
        self.assertIsNone(got['duplicate'])
        self.assertIsNone(got['fields_match'])
        self.assertIsNone(got['false_confirmation'])

    def test_read_only_cleanup_menu_does_not_cut_off_identity(self):
        rs=self.audit_fixture()
        menu=dict(next(r for r in rs if r['record_id']=='trash'))
        menu.update(record_id='menu',phase='cleanup_menu',action='right click target row',start_utc='2026-10-15T20:00:08.500+00:00',end_utc='2026-10-15T20:00:08.500+00:00')
        rs.append(menu)
        self.assertEqual(self.analyze_fixture(rs)['audit_count'],1)

    def test_post_delete_identity_cannot_complete_audit(self):
        rs=self.audit_fixture(decision='confirmed')
        link=next(r for r in rs if r['record_id']=='p')
        link.update(start_utc='2026-10-15T20:00:10.500+00:00',end_utc='2026-10-15T20:00:10.500+00:00')
        got=self.analyze_fixture(rs)
        self.assertIsNone(got['audit_count'])
        self.assertIsNone(got['duplicate'])

    def test_later_cleanup_read_keeps_query_time_and_gate_boundaries(self):
        assignment=dict(trial_id='C01',site='Google Calendar',token=CTOKEN,block='1',rule='Scope',view='All')
        def rec(id_,typ,phase,t,**extra):
            stamp='2026-10-15T20:00:'+str(t).zfill(2)+'.000+00:00'
            return dict(record_id=id_,trial_id='C01',token=CTOKEN,site='Google Calendar',type=typ,
                        phase=phase,start_utc=stamp,end_utc=stamp,tab_role='observer',**extra)
        rs=[rec('write','action','initial_create',1,action='save_event'),
            rec('seen','observation','first_observer',2,state=cal(1),url=curl()),
            rec('dec','decision','decision',3,decision='confirmed',decision_utc='2026-10-15T20:00:03.000+00:00',observed_count=1,evidence_record_ids=['seen']),
            rec('trash','action','cleanup',6,action='delete_event'),
            rec('reload','action','cleanup_reload',7,action='reload'),
            rec('uncertain','observation','cleanup_observer',8,state=cal()+'- progressbar\n',url=curl())]
        later=rec('later','observation','baseline_observer_before',9,state=cal(),url=curl())
        later.update(trial_id='C02',token='PROD-RETRY-20261015-C02')
        next_write=rec('next','action','initial_create',10,action='save_event')
        next_write.update(trial_id='C02',token='PROD-RETRY-20261015-C02')
        got=a.derive_trial(assignment,rs,[],rs+[later,next_write])
        self.assertTrue(got['cleanup_verified'])
        self.assertTrue(got['cleanup_verified_later'])
        self.assertFalse(got['cleanup_in_trial_zero'])
        self.assertEqual(got['cleanup_evidence_id'],'later')
        self.assertEqual(got['cleanup_evidence_trial_id'],'C02')
        wrong=dict(later,url=curl('PROD-RETRY-20261015-C02'))
        self.assertFalse(a.derive_trial(assignment,rs,[],rs+[wrong,next_write])['cleanup_verified'])
        late=dict(later,start_utc='2026-10-15T20:00:11.000+00:00',end_utc='2026-10-15T20:00:11.000+00:00')
        self.assertFalse(a.derive_trial(assignment,rs,[],rs+[late,next_write])['cleanup_verified'])
        without_reload=[r for r in rs if r['record_id']!='reload']
        self.assertFalse(a.derive_trial(assignment,without_reload,[],without_reload+[later,next_write])['cleanup_verified'])


if __name__=='__main__':
    unittest.main(verbosity=2)
