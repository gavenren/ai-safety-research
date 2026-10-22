#!/usr/bin/env python3
"""Separate saved-row audit. No import or execution of study.py."""
from collections import Counter
from datetime import datetime, timezone
from itertools import product
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/name).read_text())
def sha(name):
    return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def record(q, seq):
    return {'account':q[0], 'key':q[1], 'target':q[2], 'delta':q[3], 'effect':seq}

config=read('config.json')
requests=list(product(config['accounts'],config['keys'],config['targets'],config['deltas']))
pairs=list(product(requests,repeat=2))
rows=[json.loads(line) for line in (ROOT/'cases.jsonl').read_text().splitlines()]
assert len(rows)==1280
seen=set()
totals={name:Counter() for name in config['rules']}
classes={}
comparisons=0
for row in rows:
    pair=tuple(tuple(q) for q in row['requests'])
    assert pair==pairs[row['pair_id']]
    assert (row['pair_id'],row['rule']) not in seen
    seen.add((row['pair_id'],row['rule']))
    p,q=pair
    original,new=record(p,1),record(q,2)
    identity_equal=(p[0]==q[0] and p[1]==q[1])
    payload_equal=(p[2]==q[2] and p[3]==q[3])
    category=('exact_retry' if payload_equal else 'payload_conflict') if identity_equal else 'new_identity'
    oracle_action={'new_identity':'apply','exact_retry':'replay','payload_conflict':'conflict'}[category]
    oracle_receipt={'new_identity':new,'exact_retry':original,'payload_conflict':None}[category]
    oracle_effects=[original,new] if category=='new_identity' else [original]
    assert row['class']==category
    assert row['expected_effects']==oracle_effects
    assert row['expected_second']=={'action':oracle_action,'receipt':oracle_receipt}
    classes[row['pair_id']]=category
    rule=row['rule']
    # Closed-form two-request outcomes, with no receipt-store simulation.
    repeated = {
        'global_key': p[1]==q[1],
        'account_key': identity_equal,
        'account_target_key': identity_equal and p[2]==q[2],
        'full_request_key': p==q,
        'bound_receipt': identity_equal,
    }[rule]
    if rule=='bound_receipt' and identity_equal and not payload_equal:
        action, reply, effects='conflict',None,[original]
    elif repeated:
        action, reply, effects='replay',original,[original]
    else:
        action, reply, effects='apply',new,[original,new]
    actions=[{'action':'apply','receipt':original},{'action':action,'receipt':reply}]
    assert row['effects']==effects
    assert row['actions']==actions
    false_success=(action in ('apply','replay') and
                   (category=='payload_conflict' or reply!=oracle_receipt))
    expected={'cases':1,'false_success':int(false_success),
              'missing_effects':int(category=='new_identity' and len(effects)==1),
              'extra_effects':int(category!='new_identity' and len(effects)==2),
              'wrong_effect_history':int(effects!=oracle_effects),
              'exact_contract_match':int(effects==oracle_effects and actions[1]==row['expected_second']),
              'apply':int(action=='apply'),'replay':int(action=='replay'),'conflict':int(action=='conflict')}
    assert row['metrics']==expected
    totals[rule].update(expected)
    comparisons+=9
assert len(seen)==256*5
summary=read('summary.json')
assert {r:dict(t) for r,t in totals.items()}==summary['rules']
assert dict(Counter(classes.values()))==summary['classes']=={
    'new_identity':192,'exact_retry':16,'payload_conflict':48}
# Analytic aggregate expectations from the two-bit identity and two-bit payload.
assert totals['global_key']['false_success']==48+64
assert totals['global_key']['missing_effects']==64
for rule in ('account_key','account_target_key','full_request_key'):
    assert totals[rule]['false_success']==48
assert totals['account_target_key']['extra_effects']==32
assert totals['full_request_key']['extra_effects']==48
assert totals['bound_receipt']['exact_contract_match']==256
frozen=read('freeze.json')
for name,digest in frozen['sha256'].items():
    assert sha(name)==digest
assert sha('study.py')==read('implementation_freeze.json')['study.py_sha256']
for filename in ('execution.json','repeat_execution.json'):
    receipt=read(filename)
    assert receipt['status']=='complete'
    assert receipt['code_sha256']==sha('study.py')
    assert receipt['cpu_seconds']<60
    for name,digest in receipt['output_sha256'].items():
        assert sha(name)==digest
for name,details in read('reproduction.json')['files'].items():
    assert details['identical'] and sha(name)==details['sha256']
controls=read('controls.json')
indexed={(row['pair_id'],row['rule']):row for row in rows}
for named,examples in controls.items():
    assert len(examples)==5
    for example in examples:
        assert example==indexed[(example['pair_id'],example['rule'])]
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'pass',
        'saved_rows':len(rows),'unique_pairs':len(classes),'unique_rule_outcomes':len(seen),
        'row_comparisons':comparisons,'controls_checked':len(controls)*5,
        'original_sources_read':['https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/',
                                 'https://docs.stripe.com/api/idempotent_requests'],
        'code_and_frozen_inputs_match':True,'both_run_output_hashes_match':True,
        'method':'Separate closed-form evaluator of saved data; no full experiment rerun',
        'independence_limit':'Reviewer read the plan and main code before this separate audit. It is not a blinded review.'}
(ROOT/'separate_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
