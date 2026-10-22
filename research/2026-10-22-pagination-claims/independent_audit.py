#!/usr/bin/env python3
"""Audit saved evidence with a separately frozen rule evaluator."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,time
from independent_evaluator import corpus,evaluate,RULES,TYPES,MODES

P=Path(__file__).resolve().parent
started=time.process_time()
expected={(tuple(stream),mode,rule):result for stream,mode,rule,result in corpus()}
assert len(expected)==27972
worlds={}
worldkeys=set()
for line in (P/'worlds.jsonl').open():
    w=json.loads(line);wid=w['world_id'];assert wid not in worlds
    stream=tuple(tuple(x) for x in w['page_counts']);mode=w['mode'];pages=w['pages']
    assert (stream,mode) not in worldkeys
    worldkeys.add((stream,mode));worlds[wid]=w
    assert len(stream)==len(pages)
    ids=[];truth=[]
    for index,(counts,page) in enumerate(zip(stream,pages)):
        assert counts == (len(page['matches']),len(page['unrelated']))
        assert counts in TYPES
        assert (page['next_token'] is not None)==(index<len(pages)-1)
        assert page['incompleteSearch']==(mode!='complete')
        ids+=page['matches']+page['unrelated'];truth+=page['matches']
    if mode=='incomplete_one_hidden':
        assert len(set(w['truth'])-set(truth))==1
        truth+=list(set(w['truth'])-set(truth))
    assert set(w['truth'])==set(truth)
    assert len(ids)==len(set(ids)) and len(w['truth'])==len(set(w['truth']))
assert len(worlds)==4662 and len(worldkeys)==4662
expectedkeys={(tuple(stream),mode) for stream,mode,rule,result in corpus()}
assert worldkeys == expectedkeys
summary={r:Counter() for r in RULES};bymode={m:{r:Counter() for r in RULES} for m in MODES}
seen=set();cases=0
for line in (P/'cases.jsonl').open():
    row=json.loads(line);w=worlds[row['world_id']];r=row['rule'];mode=row['mode']
    assert mode==w['mode'];key=(row['world_id'],r);assert key not in seen;seen.add(key)
    stream=tuple(tuple(x) for x in w['page_counts']);e=expected[(stream,mode,r)]
    for field in ['pages_read','complete_claim','remaining_token','seen_incomplete']:
        assert row[field] == e[field],(key,field)
    ids=[v for page in w['pages'][:e['pages_read']] for v in page['matches']]
    assert row['returned_matches']==ids and len(ids)==e['returned_count']
    assert len(w['truth'])==e['truth_count']
    metrics={'cases':1,'complete_claims':int(e['complete_claim']),'unknown':int(e['unknown']),
        'unsupported_completion':int(e['unsupported_completion']),'incorrect_complete_inventory':int(e['incorrect_inventory']),
        'false_absence':int(e['false_absence']),'missing_matches':e['missing_matches'],
        'pages_read':e['pages_read'],'supported_complete':int(e['complete_claim'] and not e['unsupported_completion'])}
    assert row['metrics']==metrics,key
    summary[r].update(metrics);bymode[mode][r].update(metrics);cases+=1
assert cases==27972 and len(seen)==27972
saved=json.loads((P/'summary.json').read_text())
assert saved['rules']==summary and saved['by_mode']==bymode
assert saved['streams']==1554 and saved['worlds']==4662 and saved['rule_cases']==27972
freeze=json.loads((P/'independent_freeze.json').read_text())
assert hashlib.sha256((P/'independent_evaluator.py').read_bytes()).hexdigest()==freeze['sha256']
result={'status':'passed','worlds_checked':len(worlds),'cases_checked':cases,'all_worlds_present_once':True,
  'all_rule_cases_present_once':True,'all_case_fields_and_metrics_match':True,'aggregate_and_mode_totals_match':True,
  'main_study_executed_by_reviewer':False,'independent_evaluator_frozen_before_main_code_or_results_read':True,
  'independent_evaluator_sha256':freeze['sha256'],'reviewed_files_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['study.py','worlds.jsonl','cases.jsonl','summary.json','plan.md','config.json']},
  'checked_at_utc':datetime.now(timezone.utc).isoformat(),'audit_cpu_seconds':time.process_time()-started,
  'human_review':False}
(P/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
