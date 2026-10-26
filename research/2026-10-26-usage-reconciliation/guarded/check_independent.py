#!/usr/bin/env python3
"""Check saved traces using prefix sets, without importing the controller.

The expected final vectors were frozen before source access. This checker was
written after source review, from that contract. It does not prove provider state.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

HERE=Path(__file__).resolve().parent
ALIAS=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$')
HEX=re.compile(r'^[0-9a-f]{64}$')
REPORT_KEYS={'site','fixture','counter_start','id','captured_at','value','records','terminal','producer_stopped','evidence_sha256'}
SAVED_KEYS={'status','observed_at','record_alias','fields_verified','payload_sha256','evidence_sha256'}


def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def stamp(x):
    t=datetime.fromisoformat(x.replace('Z','+00:00'))
    assert t.tzinfo is not None and t.utcoffset().total_seconds()==0
    return t


def valid_alias(x):return isinstance(x,str) and ALIAS.fullmatch(x) is not None

def hashes(x):return isinstance(x,list) and bool(x) and all(isinstance(y,str) and HEX.fullmatch(y) for y in x)


class Prefix:
    def __init__(self,initial):
        self.initial=initial
        self.accepted=[]
        self.invalid=[]
        self.allocated={}
        self.confirmed={}

    def sets(self):
        values={r['value'] for r in self.accepted}
        q=max({0}|values)
        finals=[r for r in self.accepted if r['terminal']]
        terminal=bool(finals)
        records=set().union(*(set(r['records']) for r in self.accepted)) if self.accepted else set()
        return q,terminal,records,(set(finals[0]['records']) if finals else None)

    def summary(self):
        q,terminal,_,_=self.sets();h=0 if terminal else self.initial['reservation']-q
        saved=len(self.confirmed);pending=len(self.allocated)-saved
        return {'q':q,'h':h,'terminal':terminal,'quarantined':bool(self.invalid),
                'pending_B':pending,'saved_B':saved,
                'available':self.initial['capacity']-q-h-len(self.allocated)}

    def valid_report(self,r,event_at):
        try:
            if not isinstance(r,dict) or set(r)!=REPORT_KEYS:return False
            if any(r[k]!=self.initial[k] for k in ('site','fixture','counter_start')):return False
            if not valid_alias(r['id']) or stamp(r['captured_at'])>stamp(event_at):return False
            if type(r['value']) is not int or not 0<=r['value']<=self.initial['reservation']:return False
            if not isinstance(r['records'],list) or not all(valid_alias(x) for x in r['records']):return False
            if len(set(r['records']))!=len(r['records']) or len(r['records'])!=r['value']:return False
            if type(r['terminal']) is not bool or type(r['producer_stopped']) is not bool:return False
            if r['terminal']!=r['producer_stopped'] or not hashes(r['evidence_sha256']):return False
            earlier=[x for x in self.accepted if x['id']==r['id']]
            if earlier and digest(earlier[0])!=digest(r):return False
            _,_,union,final=self.sets();records=set(r['records'])
            if not (records<=union or union<=records):return False
            if final is not None:
                if (r['terminal'] and records!=final) or (not r['terminal'] and not records<=final):return False
            elif r['terminal'] and not union<=records:return False
            if records & {e['record_alias'] for e in self.confirmed.values()}:return False
            return True
        except (AssertionError,KeyError,ValueError,TypeError,AttributeError):return False

    def valid_observation(self,key,e,event_at):
        try:
            if key not in self.allocated or not isinstance(e,dict):return False
            a=self.allocated[key]
            if e.get('status')=='unknown':
                return (set(e)=={'status','observed_at','evidence_sha256'} and hashes(e['evidence_sha256'])
                        and stamp(a['permit_at'])<=stamp(e['observed_at'])<=stamp(event_at))
            if set(e)!=SAVED_KEYS or e['status']!='saved' or not valid_alias(e['record_alias']):return False
            if e['fields_verified'] is not True or e['payload_sha256']!=digest(a['payload']) or not hashes(e['evidence_sha256']):return False
            if not stamp(a['permit_at'])<=stamp(e['observed_at'])<=stamp(event_at):return False
            if e['record_alias'] in self.sets()[2]:return False
            if any(k!=key and old['record_alias']==e['record_alias'] for k,old in self.confirmed.items()):return False
            if key in self.confirmed and self.confirmed[key]['record_alias']!=e['record_alias']:return False
            return True
        except (AssertionError,KeyError,ValueError,TypeError,AttributeError):return False

    def consume(self,event):
        kind=event['kind'];data=event['input'];at=event['at']
        if kind=='report':
            if not self.valid_report(data,at):
                self.invalid.append(event['seq']);return {'decision':'rejected'}
            if data['id'] in {r['id'] for r in self.accepted}:return {'decision':'replay'}
            self.accepted.append(data);return {'decision':'accepted'}
        if kind=='request':
            key=data['key'];payload=data['payload']
            assert data['payload_sha256']==digest(payload)
            if key in self.allocated:
                if digest(payload)!=digest(self.allocated[key]['payload']):
                    return {'decision':'payload_conflict','dispatch':False,'completion':False}
                done=key in self.confirmed
                return {'decision':'already_saved' if done else 'pending','dispatch':False,'completion':done}
            if self.invalid:return {'decision':'quarantined','dispatch':False,'completion':False}
            if self.summary()['available']<1:return {'decision':'limit_refused','dispatch':False,'completion':False}
            permit_at=event['result']['permit_at']
            assert stamp(permit_at)<=stamp(at)
            self.allocated[key]={'payload':payload,'permit_at':permit_at}
            return {'decision':'permit','dispatch':True,'completion':False,'payload_sha256':digest(payload)}
        if kind=='observe':
            key=data['key'];e=data['evidence'];assert key in self.allocated
            if not self.valid_observation(key,e,at):return {'decision':'evidence_rejected','completion':False}
            if e['status']=='unknown':
                done=key in self.confirmed
                return {'decision':'already_saved' if done else 'pending','completion':done}
            if key in self.confirmed:return {'decision':'already_saved','completion':True}
            self.confirmed[key]=e
            return {'decision':'saved','completion':True}
        raise AssertionError('Unexpected trace kind '+kind)


def check_file(path,expected):
    records=json.loads(path.read_text());assert len(records)==8
    found=set();events_checked=0;states_checked=0;decisions={};rows=[]
    for record in records:
        init=record['events'][0];assert init['kind']=='init' and init['seq']==1
        state0=init['state'];case=state0['case'];site=state0['site'];assert case not in found;found.add(case)
        vector=next(x for x in expected['per_site_final'] if x['case']==case)
        assert state0['capacity']==vector['C'] and state0['reservation']==vector['R']
        assert state0['q']==0 and state0['h']==vector['R'] and not state0['terminal'] and not state0['quarantined']
        assert state0['records']==[] and state0['reports']=={} and state0['operations']=={}
        ref=Prefix(state0);assert init['after']==ref.summary();states_checked+=1
        requests=[]
        for index,event in enumerate(record['events'][1:],2):
            assert event['seq']==index
            assert event['before']==ref.summary(),(site,case,index,'before')
            want=ref.consume(event)
            for key,val in want.items():assert event['result'].get(key)==val,(site,case,index,key,val,event['result'])
            assert event['after']==ref.summary(),(site,case,index,'after')
            assert event['after']['available']>=0
            if event['kind']=='request':requests.append(want['decision'])
            decisions[want['decision']]=decisions.get(want['decision'],0)+1
            events_checked+=1;states_checked+=2
        assert record['summary']==ref.summary()
        final=record['state'];q,t,aliases,terminal_records=ref.sets()
        assert final['q']==q and final['h']==ref.summary()['h'] and final['terminal']==t and final['quarantined']==bool(ref.invalid)
        assert final['records']==sorted(aliases)
        assert final['terminal_records']==(sorted(terminal_records) if terminal_records is not None else None)
        assert final['reports']=={r['id']:digest(r) for r in ref.accepted}
        assert set(final['operations'])==set(ref.allocated)
        for key,op in final['operations'].items():
            assert op['payload']==ref.allocated[key]['payload'] and op['payload_sha256']==digest(op['payload'])
            assert op['permit_at']==ref.allocated[key]['permit_at']
            assert op['status']==('saved' if key in ref.confirmed else 'pending')
            if key in ref.confirmed:
                assert op['record_alias']==ref.confirmed[key]['record_alias']
                assert op['observed_at']==ref.confirmed[key]['observed_at']
                assert op['evidence_sha256']==ref.confirmed[key]['evidence_sha256']
            else:assert op['record_alias'] is None
        s=record['summary']
        for actual_key,expected_key in [('q','q'),('h','h'),('terminal','terminal'),('quarantined','quarantined'),('saved_B','saved_operations'),('pending_B','pending_operations')]:
            assert s[actual_key]==vector[expected_key],(site,case,actual_key,s[actual_key],vector[expected_key])
        rows.append({'site':site,'case':case,'summary':s,'request_decisions':requests})
    return {'file':path.name,'cases':len(records),'events_checked':events_checked,'states_checked':states_checked,'decision_counts':decisions,'cases_checked':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=HERE);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    expected=json.loads((HERE/'independent_expected.json').read_text())
    freeze=json.loads((HERE/'independent_expected_freeze.json').read_text())
    for name,hashvalue in freeze['files'].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==hashvalue
    files=[a.directory/'drive_traces.json',a.directory/'calendar_traces.json']
    checks=[check_file(f,expected) for f in files]
    result={'status':'passed','scope':'Saved local ledger traces; provider evidence needs a separate audit.',
            'specification':'Prefix sets plus immutable allocated keys; no controller import.',
            'separation':'Expected case vectors frozen before source access. This checker was written after source review.',
            'cases':sum(x['cases'] for x in checks),'events_checked':sum(x['events_checked'] for x in checks),
            'states_checked':sum(x['states_checked'] for x in checks),
            'trace_hashes':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'site_checks':checks}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
