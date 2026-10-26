#!/usr/bin/env python3
"""Offline adversarial checks by the separate reviewer. No account action occurs."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('guarded_controller',HERE/'controller.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
CHECKS=[]

def check(label,condition):
    if not condition:raise AssertionError(label)
    CHECKS.append(label)

def report(case,value,terminal=False,tag='P',records=None):
    return {'site':'drive','fixture':'drive-'+case,'counter_start':'drive-'+case+'-A',
            'id':tag,'captured_at':c.now(),'value':value,
            'records':records if records is not None else ['A'+str(i+1) for i in range(value)],
            'terminal':terminal,'producer_stopped':terminal,'evidence_sha256':['1'*64]}

def saved(alias,payload):
    return {'status':'saved','observed_at':c.now(),'record_alias':alias,'fields_verified':True,
            'payload_sha256':c.sha(payload),'evidence_sha256':['2'*64]}

def run():
    CHECKS.clear()
    with tempfile.TemporaryDirectory(prefix='usage-independent-') as td:
        root=Path(td)
        def db(tag,case='overlap',cap=2,res=2):
            path=root/(tag+'.sqlite');c.init_db(path,'drive',case,cap,res);return path
        d=db('maximum')
        p=report('overlap',1);t=report('overlap',1,True,'T')
        for r in [p,t,p,t]:c.accept_report(d,r)
        check('overlapping values and exact replay book one',c.export(d)['summary']=={'q':1,'h':0,'terminal':True,'quarantined':False,'pending_B':0,'saved_B':0,'available':1})
        a={'name':'B'}
        permit=c.request(d,'intent',a);check('first intent has one permit',permit['dispatch'] is True)
        check('pending repeat has no permit',c.request(d,'intent',a)['dispatch'] is False)
        check('pending payload change refused',c.request(d,'intent',{'name':'C'})['decision']=='payload_conflict')
        good=saved('B1',a)
        check('matching evidence saves once',c.observe(d,'intent',good)['decision']=='saved')
        check('exact confirmation replay is a no-op',c.observe(d,'intent',good)['decision']=='already_saved')
        check('saved repeat has no permit',c.request(d,'intent',a)['dispatch'] is False)
        check('all cumulative and intent replay leaves total two',c.export(d)['summary']['q']+c.export(d)['summary']['saved_B']==2)
        check('second intent is refused at full capacity',c.request(d,'other',{'name':'other'})['decision']=='limit_refused')
        d=db('early',case='early');c.accept_report(d,report('early',0))
        check('zero progress keeps full hold',c.export(d)['summary']['h']==2)
        check('zero progress gives no permit',c.request(d,'B',a)['decision']=='limit_refused')
        c.accept_report(d,report('early',2,True,'T'))
        check('terminal two remains full',c.request(d,'B2',a)['decision']=='limit_refused')
        d=db('late',case='late');t=report('late',2,True,'T');p=report('late',1)
        c.accept_report(d,t);c.accept_report(d,p)
        check('late progress cannot lower final use',c.export(d)['summary']['q']==2)
        check('late progress gives no permit',c.request(d,'B',a)['decision']=='limit_refused')
        mutations={
            'wrong_site':lambda r:r.update(site='calendar'),
            'wrong_fixture':lambda r:r.update(fixture='other'),
            'wrong_counter':lambda r:r.update(counter_start='other'),
            'boolean_value':lambda r:r.update(value=True),
            'negative_value':lambda r:r.update(value=-1),
            'over_reservation':lambda r:r.update(value=3,records=['A1','A2','A3']),
            'duplicate_alias':lambda r:r.update(value=2,records=['A1','A1']),
            'missing_stop':lambda r:r.update(terminal=True,producer_stopped=False),
            'bad_evidence_hash':lambda r:r.update(evidence_sha256=['bad']),
        }
        for name,mutate in mutations.items():
            d=db(name,case='invalid');r=report('invalid',1);mutate(r)
            check(name+' is rejected',c.accept_report(d,r)['decision']=='rejected')
            check(name+' cannot release capacity',c.export(d)['summary']['h']==2 and c.request(d,'B',a)['decision']=='quarantined')
        d=db('event_conflict',case='invalid');p=report('invalid',1);c.accept_report(d,p);bad=copy.deepcopy(p);bad.update(value=0,records=[])
        check('changed same-ID payload rejected',c.accept_report(d,bad)['decision']=='rejected')
        check('changed same-ID leaves prior total',c.export(d)['summary']['q']==1)
        d=db('terminal_lower',case='contradiction');c.accept_report(d,report('contradiction',1));r=report('contradiction',0,True,'T')
        check('terminal below prior progress rejected',c.accept_report(d,r)['decision']=='rejected')
        check('bad terminal retains residual hold',c.export(d)['summary']['h']==1)
        d=db('terminal_conflict',case='contradiction');c.accept_report(d,report('contradiction',1,True,'T'))
        check('conflicting terminal set rejected',c.accept_report(d,report('contradiction',1,True,'T2',['different']))['decision']=='rejected')
        check('conflicting terminal blocks admission',c.request(d,'B',a)['decision']=='quarantined')
        d=db('unknown',case='unknown',cap=1,res=1);c.accept_report(d,report('unknown',0,True,'T'));c.request(d,'B',a)
        e={'status':'unknown','observed_at':c.now(),'evidence_sha256':['3'*64]};c.observe(d,'B',e)
        check('unknown retains one hold',c.export(d)['summary']['pending_B']==1)
        bad=saved('B1',a);bad['fields_verified']=False
        check('wrong saved fields do not confirm',c.observe(d,'B',bad)['completion'] is False)
        check('wrong fields retain hold',c.export(d)['summary']['pending_B']==1)
        bad=saved('B1',{'name':'wrong'})
        check('wrong payload evidence does not confirm',c.observe(d,'B',bad)['completion'] is False)
        good=saved('B1',a);c.observe(d,'B',good)
        check('fresh correct evidence resolves pending',c.export(d)['summary']['pending_B']==0 and c.export(d)['summary']['saved_B']==1)
        d=db('alias_reuse',cap=3,res=2);c.accept_report(d,report('overlap',1,True,'T'));c.request(d,'B',a);c.request(d,'C',{'name':'C'})
        check('A alias cannot settle B',c.observe(d,'B',saved('A1',a))['completion'] is False)
        c.observe(d,'B',saved('B1',a))
        check('same saved alias cannot settle another intent',c.observe(d,'C',saved('B1',{'name':'C'}))['completion'] is False)
        check('bad second settlement keeps hold',c.export(d)['summary']['pending_B']==1)
        races=[]
        for i in range(12):
            d=db('race'+str(i),case='compete');c.accept_report(d,report('compete',1,True,'T'));barrier=threading.Barrier(2)
            def allocate(key):
                barrier.wait();return c.request(d,key,{'name':key})
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(allocate,['B','C']))
            races.append(sorted(x['decision'] for x in results))
            check('race '+str(i)+' has exactly one permit',sum(x['dispatch'] for x in results)==1)
            check('race '+str(i)+' retains one allocation',c.export(d)['summary']['pending_B']==1)
    return {'status':'passed','scope':'offline checks only; no production writes',
            'checks':len(CHECKS),'check_names':CHECKS,'competing_rounds':12,
            'competing_results':races,'controller_sha256':c.file_sha(HERE/'controller.py')}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(run(),indent=2,sort_keys=True)+'\n')
