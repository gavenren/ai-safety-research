#!/usr/bin/env python3
"""Finite receipt-contract study; Python standard library only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, obj):
    p.write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')

def receipt(q, number):
    return dict(zip(('account','key','target','delta'), q), effect=number)

def simulate(pair, rule):
    store, effects, actions = {}, [], []
    for q in pair:
        a,k,t,d = q
        identity = {'global_key':(k,), 'account_key':(a,k),
                    'account_target_key':(a,t,k), 'full_request_key':q,
                    'bound_receipt':(a,k)}[rule]
        old = store.get(identity)
        if old is not None:
            if rule == 'bound_receipt' and (old['target'],old['delta']) != (t,d):
                actions.append({'action':'conflict','receipt':None})
            else:
                actions.append({'action':'replay','receipt':old})
        else:
            rec = receipt(q, len(effects)+1)
            effects.append(rec)
            store[identity] = rec
            actions.append({'action':'apply','receipt':rec})
    return effects, actions

def oracle(pair):
    first, second = pair
    rec1, rec2 = receipt(first,1), receipt(second,2)
    if first[:2] != second[:2]:
        return [rec1, rec2], {'action':'apply','receipt':rec2}, 'new_identity'
    if first[2:] == second[2:]:
        return [rec1], {'action':'replay','receipt':rec1}, 'exact_retry'
    return [rec1], {'action':'conflict','receipt':None}, 'payload_conflict'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); out=args.out
    out.mkdir(parents=True,exist_ok=True)
    if (out/'cases.jsonl').exists():
        raise SystemExit('Refuse to overwrite an existing run.')
    cfg=json.loads((HERE/'config.json').read_text())
    frozen=json.loads((HERE/'freeze.json').read_text())['sha256']
    assert all(digest(HERE/n)==v for n,v in frozen.items())
    started=datetime.now(timezone.utc).isoformat(); cpu=time.process_time(); wall=time.monotonic()
    write(out/'execution.json',{'started_at_utc':started,'status':'running',
        'python':sys.version,'platform':platform.platform(),'command':sys.argv,
        'input_sha256':frozen,'code_sha256':digest(HERE/'study.py'),
        'random_seed':None,'reason':'complete enumeration; no random generator',
        'model_api_calls':0,'paid_compute':False})
    requests=list(product(cfg['accounts'],cfg['keys'],cfg['targets'],cfg['deltas']))
    totals={r:Counter() for r in cfg['rules']}; classes=Counter(); controls={}
    base=('A',0,'x',1)
    named={base:'exact_retry',('B',0,'x',1):'other_account',('A',0,'y',1):'changed_target',
           ('A',0,'x',-1):'changed_delta_net_cancel',('A',1,'x',1):'new_key_same_payload'}
    with (out/'cases.jsonl').open('w') as f:
        for pair_id,pair in enumerate(product(requests, repeat=2)):
            expected, second_expected, kind=oracle(pair); classes[kind]+=1
            for rule in cfg['rules']:
                effects,actions=simulate(pair,rule); second=actions[1]
                false_success=second['action']!='conflict' and (
                    second_expected['action']=='conflict' or second['receipt']!=second_expected['receipt'])
                metrics={'cases':1,'false_success':int(false_success),
                    'missing_effects':max(0,len(expected)-len(effects)),
                    'extra_effects':max(0,len(effects)-len(expected)),
                    'wrong_effect_history':int(effects!=expected),
                    'exact_contract_match':int(effects==expected and second==second_expected),
                    'apply':int(second['action']=='apply'), 'replay':int(second['action']=='replay'),
                    'conflict':int(second['action']=='conflict')}
                totals[rule].update(metrics)
                row={'pair_id':pair_id,'requests':pair,'rule':rule,'class':kind,
                     'expected_effects':expected,'expected_second':second_expected,
                     'effects':effects,'actions':actions,'metrics':metrics}
                f.write(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n')
                if pair[0]==base and pair[1] in named:
                    controls.setdefault(named[pair[1]],[]).append(row)
    assert len(requests)==16 and sum(classes.values())==256
    assert classes=={'new_identity':192,'exact_retry':16,'payload_conflict':48}
    assert totals['bound_receipt']['exact_contract_match']==256
    assert all(totals[r]['false_success']>0 for r in cfg['rules'] if r!='bound_receipt')
    # All exact retries must replay one original effect under all five rules.
    assert all(row['metrics']['exact_contract_match'] for row in controls['exact_retry'])
    assert time.process_time()-cpu<60
    write(out/'summary.json',{'request_count':16,'pair_count':256,'rule_cases':1280,
        'classes':classes,'rules':totals})
    write(out/'controls.json',controls)
    write(out/'checks.json',{'frozen_inputs':True,'complete_case_count':True,
        'oracle_class_counts':True,'bound_receipt_exact':True,'all_baselines_have_counterexample':True,
        'exact_retry_controls':True,'unknown_cases':0,'failed_assertions':0})
    execution=json.loads((out/'execution.json').read_text())
    execution.update(status='complete',ended_at_utc=datetime.now(timezone.utc).isoformat(),
        cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-wall,
        output_sha256={n:digest(out/n) for n in ('cases.jsonl','summary.json','controls.json','checks.json')})
    write(out/'execution.json',execution)
    print(json.dumps({'status':'complete','pairs':256,'rule_cases':1280,'rules':totals},sort_keys=True))
if __name__=='__main__':
    main()
