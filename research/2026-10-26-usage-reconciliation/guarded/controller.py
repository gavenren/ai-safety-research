#!/usr/bin/env python3
"""CheckedLedger: local record admission only. This program has no network code."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ALIAS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
CASES = ('overlap','late','early','release','unknown','compete','invalid','contradiction')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z')


def canon(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def sha(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()


def file_sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def require(test, message):
    if not test:
        raise ValueError(message)


def alias(x):
    require(isinstance(x,str) and ALIAS.fullmatch(x),'invalid_alias')
    return x


def utc(x):
    require(isinstance(x,str),'invalid_time')
    t=datetime.fromisoformat(x.replace('Z','+00:00'))
    require(t.tzinfo is not None and t.utcoffset().total_seconds()==0,'time_not_utc')
    return t


def evidence_hashes(x):
    require(isinstance(x,list) and len(x)>0 and all(isinstance(v,str) and HASH.fullmatch(v) for v in x),'invalid_evidence_hashes')


def state_summary(s):
    pending=sum(o['status']=='pending' for o in s['operations'].values())
    saved=sum(o['status']=='saved' for o in s['operations'].values())
    return {'q':s['q'],'h':s['h'],'terminal':s['terminal'],'quarantined':s['quarantined'],
            'pending_B':pending,'saved_B':saved,'available':s['capacity']-s['q']-s['h']-pending-saved}


def invariant(s):
    v=state_summary(s)
    require(v['available']>=0,'negative_balance')
    require(s['q']>=0 and s['h']>=0,'negative_accounting')
    require(s['q']+s['h']==(s['q'] if s['terminal'] else s['reservation']),'bad_residual_hold')
    require(s['q']==len(s['records']),'bad_A_count')
    aliases=[o['record_alias'] for o in s['operations'].values() if o['status']=='saved']
    require(len(aliases)==len(set(aliases)),'duplicate_B_record')
    require(not set(aliases)&set(s['records']),'A_B_record_overlap')


def init_db(path,site,case,capacity,reservation):
    require(site in ('drive','calendar') and case in CASES,'bad_scope')
    require(type(capacity) is int and type(reservation) is int and 0<reservation<=capacity,'bad_limit')
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation prevents a new run from silently resetting old permits.
    with path.open('xb'):
        pass
    s={'schema':1,'site':site,'case':case,'fixture':f'{site}-{case}','counter_start':f'{site}-{case}-A',
       'capacity':capacity,'reservation':reservation,'q':0,'h':reservation,'terminal':False,'terminal_records':None,
       'quarantined':False,'records':[],'reports':{},'operations':{},'created_at':now(),
       'controller_sha256':file_sha(__file__),'plan_sha256':file_sha(Path(__file__).with_name('plan.md'))}
    with sqlite3.connect(path) as c:
        c.execute('PRAGMA journal_mode=DELETE');c.execute('PRAGMA synchronous=FULL')
        c.execute('CREATE TABLE ledger(id INTEGER PRIMARY KEY CHECK(id=1),state TEXT NOT NULL)')
        c.execute('CREATE TABLE audit(seq INTEGER PRIMARY KEY AUTOINCREMENT,event TEXT NOT NULL)')
        c.execute('INSERT INTO ledger VALUES(1,?)',(canon(s),))
        c.execute('INSERT INTO audit(event) VALUES(?)',(canon({'kind':'init','at':now(),'state':copy.deepcopy(s),'after':state_summary(s)}),))
    return {'decision':'initialized','state':state_summary(s),'scope':{k:s[k] for k in ('site','fixture','counter_start')}}


@contextmanager
def transaction(path):
    require(Path(path).is_file(),'missing_ledger')
    c=sqlite3.connect(path,timeout=30,isolation_level=None)
    c.execute('PRAGMA synchronous=FULL')
    c.execute('BEGIN IMMEDIATE')
    try:
        s=json.loads(c.execute('SELECT state FROM ledger WHERE id=1').fetchone()[0])
        require(s['controller_sha256']==file_sha(__file__),'controller_changed')
        require(s['plan_sha256']==file_sha(Path(__file__).with_name('plan.md')),'plan_changed')
        yield c,s
        invariant(s)
        c.execute('UPDATE ledger SET state=? WHERE id=1',(canon(s),))
        c.execute('COMMIT')
    except BaseException:
        c.execute('ROLLBACK');raise
    finally:
        c.close()


def log(c,s,kind,inputs,before,result):
    entry={'kind':kind,'at':now(),'input':inputs,'before':before,'after':state_summary(s),'result':result}
    c.execute('INSERT INTO audit(event) VALUES(?)',(canon(entry),))
    return result|{'state':state_summary(s),'seq':c.execute('SELECT last_insert_rowid()').fetchone()[0]}


def report_valid(s,r):
    keys={'site','fixture','counter_start','id','captured_at','value','records','terminal','producer_stopped','evidence_sha256'}
    require(isinstance(r,dict) and set(r)==keys,'report_shape')
    require(all(r[k]==s[k] for k in ('site','fixture','counter_start')),'wrong_scope')
    alias(r['id']);utc(r['captured_at']);require(utc(r['captured_at'])<=utc(now()),'future_report')
    require(type(r['value']) is int and 0<=r['value']<=s['reservation'],'invalid_total')
    require(isinstance(r['records'],list),'invalid_record_list')
    for v in r['records']:alias(v)
    require(len(set(r['records']))==len(r['records'])==r['value'],'record_count_mismatch')
    require(type(r['terminal']) is bool and type(r['producer_stopped']) is bool,'invalid_flags')
    require(r['producer_stopped'] is r['terminal'],'unproven_stop')
    evidence_hashes(r['evidence_sha256'])
    old=s['reports'].get(r['id'])
    require(old is None or old==sha(r),'event_id_conflict')
    records=set(r['records']); prior=set(s['records'])
    require(records<=prior or prior<=records,'incompatible_record_sets')
    if s['terminal']:
        terminal=set(s['terminal_records'])
        require(records==terminal if r['terminal'] else records<=terminal,'terminal_conflict')
    elif r['terminal']:
        require(prior<=records,'terminal_below_progress')
    saved={o['record_alias'] for o in s['operations'].values() if o['status']=='saved'}
    require(not records&saved,'A_B_record_overlap')


def accept_report(path,r):
    with transaction(path) as (c,s):
        before=state_summary(s)
        try:
            report_valid(s,r)
        except (ValueError,TypeError,KeyError) as e:
            s['quarantined']=True
            return log(c,s,'report',r,before,{'decision':'rejected','reason':str(e)})
        if r['id'] in s['reports']:
            return log(c,s,'report',r,before,{'decision':'replay','reason':'same_report_bytes'})
        s['reports'][r['id']]=sha(r)
        if r['value']>s['q']:
            s['q']=r['value'];s['records']=sorted(r['records'])
        if r['terminal']:
            s['terminal']=True;s['terminal_records']=sorted(r['records'])
        s['h']=0 if s['terminal'] else s['reservation']-s['q']
        return log(c,s,'report',r,before,{'decision':'accepted','reason':'valid_cumulative_report'})


def request(path,key,payload):
    alias(key)
    require(isinstance(payload,dict) and payload,'invalid_payload')
    # Actual intended fields belong here, without private account identifiers.
    payload_hash=sha(payload)
    with transaction(path) as (c,s):
        before=state_summary(s); old=s['operations'].get(key)
        inputs={'key':key,'payload':payload,'payload_sha256':payload_hash}
        if old is not None:
            if old['payload_sha256']!=payload_hash:
                result={'decision':'payload_conflict','dispatch':False,'completion':False}
            else:
                result={'decision':'already_saved' if old['status']=='saved' else 'pending','dispatch':False,'completion':old['status']=='saved'}
            return log(c,s,'request',inputs,before,result)
        if s['quarantined']:
            return log(c,s,'request',inputs,before,{'decision':'quarantined','dispatch':False,'completion':False})
        if before['available']<1:
            return log(c,s,'request',inputs,before,{'decision':'limit_refused','dispatch':False,'completion':False})
        permit_at=now()
        s['operations'][key]={'payload':payload,'payload_sha256':payload_hash,'status':'pending','permit_at':permit_at,'record_alias':None,'evidence_sha256':None}
        return log(c,s,'request',inputs,before,{'decision':'permit','dispatch':True,'completion':False,'permit_at':permit_at,'payload_sha256':payload_hash})


def observe(path,key,e):
    alias(key)
    with transaction(path) as (c,s):
        before=state_summary(s);o=s['operations'].get(key)
        require(o is not None,'unreserved_intent')
        result={'decision':'evidence_rejected','completion':False}
        try:
            require(isinstance(e,dict),'evidence_shape')
            if e.get('status')=='unknown':
                require(set(e)=={'status','observed_at','evidence_sha256'},'evidence_shape')
                utc(e['observed_at']);evidence_hashes(e['evidence_sha256'])
                require(utc(o['permit_at'])<=utc(e['observed_at'])<=utc(now()),'invalid_evidence_time')
                result={'decision':'already_saved' if o['status']=='saved' else 'pending','completion':o['status']=='saved'}
            else:
                require(set(e)=={'status','observed_at','record_alias','fields_verified','payload_sha256','evidence_sha256'},'evidence_shape')
                require(e['status']=='saved','invalid_status');alias(e['record_alias']);evidence_hashes(e['evidence_sha256'])
                require(utc(o['permit_at'])<=utc(e['observed_at'])<=utc(now()),'invalid_evidence_time')
                require(e['fields_verified'] is True,'fields_not_verified')
                require(e['payload_sha256']==o['payload_sha256'],'payload_not_verified')
                require(e['record_alias'] not in s['records'],'record_used_by_A')
                require(all(k==key or x['record_alias']!=e['record_alias'] for k,x in s['operations'].items()),'record_used_by_other_intent')
                if o['status']=='saved':
                    require(o['record_alias']==e['record_alias'],'saved_record_changed')
                    result={'decision':'already_saved','completion':True}
                else:
                    o['status']='saved';o['record_alias']=e['record_alias'];o['evidence_sha256']=e['evidence_sha256'];o['observed_at']=e['observed_at']
                    result={'decision':'saved','completion':True}
        except (ValueError,TypeError,KeyError) as ex:
            result={'decision':'evidence_rejected','reason':str(ex),'completion':False}
        return log(c,s,'observe',{'key':key,'evidence':e},before,result)


def export(path):
    require(Path(path).is_file(),'missing_ledger')
    with sqlite3.connect(f'file:{Path(path).resolve()}?mode=ro',uri=True) as c:
        c.execute('BEGIN')
        state=json.loads(c.execute('SELECT state FROM ledger WHERE id=1').fetchone()[0])
        events=[{'seq':i,**json.loads(v)} for i,v in c.execute('SELECT seq,event FROM audit ORDER BY seq')]
    invariant(state)
    return {'state':state,'summary':state_summary(state),'events':events}


def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='command',required=True)
    for n in ('init','report','request','observe','export'):
        q=sp.add_parser(n);q.add_argument('--db',type=Path,required=True)
        if n=='init':
            q.add_argument('--site',choices=['drive','calendar'],required=True);q.add_argument('--case',choices=CASES,required=True)
            q.add_argument('--capacity',type=int,default=2);q.add_argument('--reservation',type=int,default=2)
        if n in ('report','observe'):q.add_argument('--input',type=Path,required=True)
        if n in ('request','observe'):q.add_argument('--key',required=True)
        if n=='request':q.add_argument('--payload',type=Path,required=True)
        if n=='export':q.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.command=='init':value=init_db(a.db,a.site,a.case,a.capacity,a.reservation)
    elif a.command=='report':value=accept_report(a.db,json.loads(a.input.read_text()))
    elif a.command=='request':value=request(a.db,a.key,json.loads(a.payload.read_text()))
    elif a.command=='observe':value=observe(a.db,a.key,json.loads(a.input.read_text()))
    else:
        value=export(a.db)
        if a.out:
            a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
            print(json.dumps({'exported':str(a.out),'summary':value['summary']},sort_keys=True));return
    print(json.dumps(value,sort_keys=True))

if __name__=='__main__':main()
