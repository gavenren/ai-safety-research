#!/usr/bin/env python3
import itertools
import unittest
import fieldcheck as f
TOKEN='FIELD-CHECK-C01'

def ui():
    return dict(title=TOKEN,description=TOKEN,all_day=True,start_date='2026-10-14',
                end_date='2026-10-14',availability='Free',visibility='Private',
                recurrence='Does not repeat',guests=[],location='',conference=False,reminders=[])

def event():
    return dict(id='id-1',summary=TOKEN,description=TOKEN+'\n\n',start='2026-10-14T00:00:00',
                end='2026-10-15T00:00:00',status='confirmed',attendees=[],location=None,
                hangout_link=None,transparency='transparent',visibility='private',recurrence=None,
                recurring_event_id=None,reminders=dict(use_default=False,overrides=[]))

def ctx():
    return dict(first_id='id-1',ui_id='id-1',service_id='id-1',operation_ids=['id-1'],native_ready=True,
                native_fresh=True,service_ready=True,service_fresh=True,coverage_ready=True,
                coverage_fresh=True,scope_covered=True,edit_pending=False)

class FieldTests(unittest.TestCase):
    def test_correct(self):
        r=f.calendar_fields(TOKEN,ui(),event())
        self.assertEqual(r['status'],f.MATCH)
        self.assertEqual(f.check_record(r,**ctx())['status'],f.MATCH)
    def test_marker_suffix_only(self):
        for x in [TOKEN,TOKEN+'\n',TOKEN+'\r\n\r']:
            self.assertEqual(f.description(x,TOKEN,connector=True)['status'],f.MATCH)
        for x in ['',TOKEN+'-WRONG',' '+TOKEN,TOKEN+' ','\n'+TOKEN,TOKEN[:4]+'\n'+TOKEN[4:],TOKEN.lower(),TOKEN+'\t',TOKEN+TOKEN]:
            self.assertEqual(f.description(x,TOKEN,connector=True)['status'],f.MISMATCH)
    def test_visible_marker_is_exact(self):
        self.assertEqual(f.description(TOKEN+'\n',TOKEN)['status'],f.MISMATCH)
    def test_unsupported_marker(self):
        for x in [None,1,[],{},f.MISSING,'<b>'+TOKEN+'</b>',TOKEN+'<br>']:
            self.assertEqual(f.description(x,TOKEN,connector=True)['status'],f.UNKNOWN)
    def test_deliberate_wrong_fields(self):
        for k,v in [('description',TOKEN+'-WRONG'),('description',''),('start','2026-10-13T00:00:00'),('end','2026-10-16T00:00:00'),('transparency','opaque')]:
            e=event(); e[k]=v
            self.assertEqual(f.calendar_fields(TOKEN,ui(),e)['status'],f.MISMATCH)
    def test_wrong_channel_wins(self):
        u=ui(); u['description']='WRONG'
        self.assertEqual(f.calendar_fields(TOKEN,u,event())['status'],f.MISMATCH)
        e=event(); e['description']='WRONG'
        self.assertEqual(f.calendar_fields(TOKEN,ui(),e)['status'],f.MISMATCH)
    def test_missing_is_not_empty(self):
        for k in event():
            if k=='id': continue
            e=event(); del e[k]
            self.assertEqual(f.calendar_fields(TOKEN,ui(),e)['status'],f.UNKNOWN,k)
        for k in ui():
            u=ui(); del u[k]
            self.assertEqual(f.calendar_fields(TOKEN,u,event())['status'],f.UNKNOWN,k)
    def test_wrong_wins_missing(self):
        e=event(); del e['description']; e['transparency']='opaque'
        r=f.calendar_fields(TOKEN,ui(),e)
        self.assertEqual(r['status'],f.MISMATCH)
        self.assertEqual(r['checks']['connector.description']['status'],f.UNKNOWN)
    def test_midnight_does_not_prove_all_day(self):
        for v,want in [(False,f.MISMATCH),(None,f.UNKNOWN),(1,f.UNKNOWN)]:
            u=ui(); u['all_day']=v
            self.assertEqual(f.calendar_fields(TOKEN,u,event())['status'],want)
    def test_date_types_and_exclusive_end(self):
        for v in ['2026-10-15T00:00:00Z','2026-10-15T00:00:00-04:00','2026-10-15','2026-13-15T00:00:00',None]:
            e=event(); e['end']=v
            self.assertEqual(f.calendar_fields(TOKEN,ui(),e)['status'],f.UNKNOWN)
        for v in ['2026-10-14T00:00:00','2026-10-15T01:00:00']:
            e=event(); e['end']=v
            self.assertEqual(f.calendar_fields(TOKEN,ui(),e)['status'],f.MISMATCH)
        u=ui(); u['end_date']='2026-10-15'
        self.assertEqual(f.calendar_fields(TOKEN,u,event())['status'],f.MISMATCH)
    def test_other_wrong_fields(self):
        for k,v in [('visibility','public'),('attendees',[{'email':'temporary@example.invalid'}]),('location','Wrong room'),('hangout_link','https://example.invalid'),('recurrence',['RRULE:FREQ=DAILY']),('recurring_event_id','other'),('status','cancelled')]:
            e=event(); e[k]=v
            self.assertEqual(f.calendar_fields(TOKEN,ui(),e)['status'],f.MISMATCH,k)
    def test_reminder_bool_type(self):
        for v,want in [({'use_default':True,'overrides':[]},f.MISMATCH),({'use_default':False,'overrides':[{'minutes':10}]},f.MISMATCH),({'use_default':0,'overrides':[]},f.UNKNOWN),({'use_default':False},f.UNKNOWN)]:
            self.assertEqual(f.reminders(v)['status'],want)
    def test_notion(self):
        u=dict(title=TOKEN,marker=TOKEN,verified=False,body_empty=True)
        self.assertEqual(f.notion_fields(TOKEN,u)['status'],f.MATCH)
        for k,v in [('marker',''),('marker',TOKEN+'-WRONG'),('verified',True),('body_empty',False)]:
            b=dict(u); b[k]=v
            self.assertEqual(f.notion_fields(TOKEN,b)['status'],f.MISMATCH)
        for k,v in [('verified',0),('marker',None),('body_empty','true')]:
            b=dict(u); b[k]=v
            self.assertEqual(f.notion_fields(TOKEN,b)['status'],f.UNKNOWN)
    def test_identity_and_count(self):
        fields=f.calendar_fields(TOKEN,ui(),event())
        for k,v in [('ui_id','id-2'),('service_id','id-2'),('operation_ids',[]),('operation_ids',['id-1','id-2'])]:
            c=ctx(); c[k]=v
            self.assertEqual(f.check_record(fields,**c)['status'],f.MISMATCH)
        for v in [None,['id-1','id-1'],[1]]:
            c=ctx(); c['operation_ids']=v
            self.assertEqual(f.check_record(fields,**c)['status'],f.UNKNOWN)
    def test_empty_identity_is_unknown(self):
        fields=f.calendar_fields(TOKEN,ui(),event())
        for k in ['first_id','ui_id','service_id']:
            c=ctx();c[k]=''
            self.assertEqual(f.check_record(fields,**c)['status'],f.UNKNOWN)
    def test_readiness_fails_closed(self):
        fields=f.calendar_fields(TOKEN,ui(),event())
        for k in ['native_ready','native_fresh','service_ready','service_fresh','coverage_ready','coverage_fresh','scope_covered']:
            for v in [False,None,1,'true']:
                c=ctx(); c[k]=v
                self.assertEqual(f.check_record(fields,**c)['status'],f.UNKNOWN,k)
        for v in [True,None,0,'false']:
            c=ctx(); c['edit_pending']=v
            self.assertEqual(f.check_record(fields,**c)['status'],f.UNKNOWN)
    def test_pending_draft_cannot_prove_saved_mismatch(self):
        u=ui(); u['description']='WRONG'; c=ctx(); c['edit_pending']=True
        self.assertEqual(f.check_record(f.calendar_fields(TOKEN,u,event()),**c)['status'],f.UNKNOWN)
    def test_stale_service_or_incomplete_scope_cannot_authorize_repair(self):
        e=event(); e['description']='WRONG'
        fields=f.calendar_fields(TOKEN,ui(),e)
        for key in ['native_ready','native_fresh','service_ready','service_fresh','coverage_ready','coverage_fresh','scope_covered']:
            c=ctx(); c[key]=False
            status=f.check_record(fields,**c)['status']
            self.assertEqual(status,f.UNKNOWN,key)
            self.assertEqual(f.next_action(status,creates=1,repairs=0,same_identity=True,target_mismatch=True),'READ',key)
    def test_outer_label_is_not_evidence(self):
        fields=f.calendar_fields(TOKEN,ui(),event()); fields['status']=f.MISMATCH
        self.assertEqual(f.check_record(fields,**ctx())['status'],f.MATCH)
    def test_offline_baseline(self):
        self.assertEqual(f.baseline_title_count(TOKEN,TOKEN,['id-1'],ready=True,fresh=True,scope_covered=True),f.MATCH)
        self.assertEqual(f.baseline_title_count(TOKEN,TOKEN,['id-1']),f.UNKNOWN)
        self.assertEqual(f.baseline_title_count(TOKEN,TOKEN,['id-1','id-2'],ready=True,fresh=True,scope_covered=True),f.MISMATCH)

class ActionTests(unittest.TestCase):
    def test_first_create(self):
        self.assertEqual(f.next_action(f.UNKNOWN,creates=0,repairs=0,baseline_empty=True),'CREATE')
        self.assertEqual(f.next_action(f.UNKNOWN,creates=0,repairs=0),'READ')
    def test_repair(self):
        self.assertEqual(f.next_action(f.MISMATCH,creates=1,repairs=0,same_identity=True,target_mismatch=True),'REPAIR_SAME_ID')
        self.assertEqual(f.next_action(f.MATCH,creates=1,repairs=1,same_identity=True),'CONFIRM')
        self.assertEqual(f.next_action(f.MISMATCH,creates=1,repairs=1,same_identity=True,target_mismatch=True),'UNRESOLVED')
    def test_admitted_never_recreates(self):
        count=0
        for creates,repairs,status,facts in itertools.product((1,2),(0,1,2),(f.MATCH,f.MISMATCH,f.UNKNOWN),itertools.product((False,True),repeat=5)):
            same,target,pending,deadline,empty=facts
            a=f.next_action(status,creates=creates,repairs=repairs,same_identity=same,target_mismatch=target,pending=pending,deadline=deadline,baseline_empty=empty)
            self.assertNotEqual(a,'CREATE'); count+=1
        self.assertEqual(count,576)
    def test_bad_types(self):
        for v in [True,-1,'1',1.0]:
            with self.assertRaises(ValueError): f.next_action(f.MATCH,creates=v,repairs=0)
        with self.assertRaises(ValueError): f.next_action(f.MATCH,creates=1,repairs=0,same_identity=1)

if __name__=='__main__': unittest.main()
