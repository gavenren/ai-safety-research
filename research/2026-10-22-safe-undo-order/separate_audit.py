#!/usr/bin/env python3
"""Separate audit of saved undo-order traces. Does not run or import study.py."""
from collections import Counter
from datetime import datetime, timezone
from itertools import permutations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/name).read_text())
def sha(name):
    return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def as_set(bits):
    return frozenset(chr(97+i) for i,b in enumerate(bits) if b=='1')
def as_bits(values,n):
    return ''.join('1' if chr(97+i) in values else '0' for i in range(n))

rows=[json.loads(line) for line in (ROOT/'cases.jsonl').read_text().splitlines()]
assert len(rows)==1179
assert [r['case_id'] for r in rows]==list(range(1,1180))
lookup={}
point_checks=0
for r in rows:
    n=r['bits']; alphabet='abc'[:n]; full=frozenset(alphabet)
    legal={as_set(s) for s in r['valid_states']}
    expected_valid={0,(1<<n)-1}|{s for s in range(1,(1<<n)-1) if r['condition_id'] & (1<<(s-1))}
    assert sorted(int(s,2) for s in r['valid_states'])==sorted(expected_valid)
    assert r['group']==('primary' if n==3 else 'smaller_control')
    assert sorted(r['priority'])==list(alphabet)
    # Bottom-up winning-state set. Every edge removes one letter.
    winning={frozenset()}
    for size in range(1,n+1):
        for state in legal:
            if len(state)==size and any(state-{letter} in winning for letter in state):
                winning.add(state)
    trace=[full]; actions=''; candidate_checks=0
    if r['rule']=='fixed':
        for letter in r['priority']:
            trace.append(trace[-1]-{letter}); actions+=letter
    elif r['rule']=='greedy':
        while trace[-1]:
            current=trace[-1]
            candidates=[letter for letter in r['priority'] if letter in current]
            allowed=[letter for letter in candidates if current-{letter} in legal]
            if not allowed:
                candidate_checks+=len(candidates)
                break
            chosen=allowed[0]
            candidate_checks+=candidates.index(chosen)+1
            trace.append(current-{chosen}); actions+=chosen
    else:
        assert r['rule']=='complete'
        ranks={letter:i for i,letter in enumerate(r['priority'])}
        orders=sorted(permutations(alphabet),key=lambda order:tuple(ranks[x] for x in order))
        for order in orders:
            path=[full-frozenset(order[:i]) for i in range(n+1)]
            bad=next((i for i,state in enumerate(path[1:],1) if state not in legal),None)
            candidate_checks+=bad if bad is not None else n
            if bad is None:
                trace=path; actions=''.join(order)
                break
    status='target_reached' if not trace[-1] else ('partial_stop' if actions else 'refused_before_action')
    flags={'target_reached':not trace[-1], 'all_states_valid':all(s in legal for s in trace),
           'valid_completion':not trace[-1] and all(s in legal for s in trace),
           'partial_stop':status=='partial_stop','refused_before_action':status=='refused_before_action',
           'initial_safe_path':full in winning,'final_safe_path':trace[-1] in winning,
           'avoidable_dead_end':bool(actions) and bool(trace[-1]) and full in winning and trace[-1] not in winning}
    assert r['trace']==[as_bits(s,n) for s in trace],r['case_id']
    assert r['actions']==actions and r['candidate_checks']==candidate_checks
    assert r['status']==status
    assert all(r[k]==v for k,v in flags.items())
    point_checks+=len(trace)
    key=(n,tuple(r['valid_states']),r['priority'],r['rule'])
    assert key not in lookup
    lookup[key]=r
    if n<=2 and r['rule']=='greedy':
        assert not r['avoidable_dead_end']

# Check each name permutation by comparing only existing saved records.
symmetries=0
for r in rows:
    n=r['bits']; letters='abc'[:n]
    for order in permutations(letters):
        mapping=dict(zip(letters,order))
        def mapped(bits):
            return as_bits({mapping[c] for c in as_set(bits)},n)
        new_valid=tuple(sorted(mapped(s) for s in r['valid_states']))
        new_priority=''.join(mapping[x] for x in r['priority'])
        other=lookup[(n,new_valid,new_priority,r['rule'])]
        assert other['trace']==[mapped(s) for s in r['trace']]
        assert other['actions']==''.join(mapping[x] for x in r['actions'])
        assert other['candidate_checks']==r['candidate_checks']
        for k in ('status','target_reached','all_states_valid','valid_completion','partial_stop',
                  'refused_before_action','initial_safe_path','final_safe_path','avoidable_dead_end'):
            assert other[k]==r[k]
        symmetries+=1
assert symmetries==6963

fields=('target_reached','all_states_valid','valid_completion','partial_stop',
        'refused_before_action','initial_safe_path','avoidable_dead_end')
def aggregate(selected):
    return {'cases':len(selected),**{f:sum(r[f] for r in selected) for f in fields}}
summary=read('summary.json'); primary=[r for r in rows if r['group']=='primary']
for rule,saved in summary['primary'].items():
    assert aggregate([r for r in primary if r['rule']==rule])==saved
for priority,rules in summary['by_priority'].items():
    for rule,saved in rules.items():
        assert aggregate([r for r in primary if r['rule']==rule and r['priority']==priority])==saved
for n,rules in summary['smaller_controls'].items():
    for rule,saved in rules.items():
        assert aggregate([r for r in rows if r['bits']==int(n) and r['rule']==rule])==saved
for condition in read('conditions.json'):
    selected=[r for r in primary if r['condition_id']==condition['condition_id']]
    assert condition['valid_states']==selected[0]['valid_states']
    for rule,saved in condition['rules'].items():
        assert aggregate([r for r in selected if r['rule']==rule])==saved
assert summary['conditions_with_safe_path']==46
assert summary['conditions_with_any_greedy_dead_end']==9
witness=read('witness.json')['paired_cases']
for r in witness:
    assert r==rows[r['case_id']-1]
assert [r['case_id'] for r in witness]==[430,431,432]
assert next(r for r in primary if r['avoidable_dead_end'])==witness[1]

# Analytic post-run counts, checked against the table for each priority.
assert 1*8+3*2+3*1+1*1==18
for priority,rules in summary['by_priority'].items():
    assert rules['fixed']['valid_completion']==2**4
    assert rules['complete']['valid_completion']==64-18
    assert rules['greedy']['refused_before_action']==8
    assert rules['greedy']['partial_stop']==8+4+2
    assert rules['greedy']['avoidable_dead_end']==3+1
    assert rules['greedy']['valid_completion']==64-8-14
report=(ROOT/'report.md').read_text()
assert '| Fixed | 384 | 384 | 96 | 288 | 0 | 0 | 0 |' in report
assert '| Greedy | 384 | 252 | 252 | 0 | 84 | 48 | 24 |' in report
assert '| Complete | 384 | 276 | 276 | 0 | 0 | 108 | 0 |' in report
for name,digest in read('freeze.json')['sha256'].items():
    assert sha(name)==digest
assert sha('study.py')==read('implementation_freeze.json')['study_py_sha256']
for name in ('execution_run_1.json','execution_run_2.json'):
    receipt=read(name)
    assert receipt['exit_status']==0 and receipt['unknown_cases']==0
    assert receipt['source_sha256']==sha('study.py')
    assert receipt['cpu_seconds']<60 and receipt['wall_seconds']<120
for name,details in read('reproduction.json')['deterministic_files'].items():
    assert details['equal_bytes'] and sha(name)==details['sha256']
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'pass',
        'saved_rule_cases':len(rows),'saved_trace_states_checked':point_checks,
        'saved_symmetry_comparisons':symmetries,'summary_and_condition_totals_match':True,
        'frozen_inputs_and_source_match':True,'five_reproduction_hashes_match':True,
        'report_table_matches':True,'analytic_argument_matches':True,
        'method':'Set-of-letters states and bottom-up winning-state oracle; no import or execution of study.py',
        'review_limit':'The reviewer read the main code before writing this separate audit. It is not a blinded review.'}
(ROOT/'separate_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
