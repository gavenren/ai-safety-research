#!/usr/bin/env python3
"""Complete synthetic cancellation/restart corpus. Standard library only."""
import argparse
import csv
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
RULES = ['active_commit','modulo2_commit','modulo4_commit','unique_precheck','unique_commit','highwater_commit','cancel_fence_commit']


def schedules(n):
    # Main generator: recursively interleave three chains with N's prerequisite.
    chain = [f'{kind}{i}' for i in range(1,n+1) for kind in ('A','R')]
    def rec(prefix, k, old, new):
        if k == len(chain) and old == 2 and new:
            yield tuple(prefix)
            return
        if k < len(chain):
            yield from rec(prefix+[chain[k]], k+1, old, new)
        if old < 2:
            yield from rec(prefix+['C' if old == 0 else 'O'], k, old+1, new)
        if k == len(chain) and not new:
            yield from rec(prefix+['N'], k, old, True)
    yield from rec([],0,0,False)


def inserted_schedules(n):
    # Independent enumeration: choose C/O positions in one fixed chain ending N.
    fixed = [f'{kind}{i}' for i in range(1,n+1) for kind in ('A','R')] + ['N']
    result = set()
    for c,o in itertools.combinations(range(2*n+3),2):
        tail = iter(fixed)
        result.add(tuple('C' if j == c else 'O' if j == o else next(tail) for j in range(2*n+3)))
    return result


def run_case(n, events, rule):
    active, generation, highwater = True, 0, 0
    checked = None
    old_accept = new_accept = None
    effects, trace = [], []
    old_state = check_state = None
    for event in events:
        accepted = None
        if event.startswith('A'):
            active = False
            generation = int(event[1:])
            if rule == 'cancel_fence_commit':
                highwater = max(highwater, generation)
        elif event.startswith('R'):
            assert generation == int(event[1:])
            active = True
        elif event == 'C':
            checked = active and generation == 0
            check_state = {'active':active,'generation':generation,'highwater':highwater,'passes':checked}
        elif event in ('O','N'):
            token = 0 if event == 'O' else n
            state = {'active':active,'generation':generation,'highwater':highwater}
            if rule == 'active_commit':
                accepted = active
            elif rule == 'modulo2_commit':
                accepted = active and generation % 2 == token % 2
            elif rule == 'modulo4_commit':
                accepted = active and generation % 4 == token % 4
            elif rule == 'unique_precheck' and event == 'O':
                assert checked is not None
                accepted = checked
            elif rule in ('unique_precheck','unique_commit'):
                accepted = active and generation == token
            elif rule in ('highwater_commit','cancel_fence_commit'):
                accepted = token >= highwater
            else:
                raise ValueError(rule)
            if accepted:
                effects.append(event)
                if rule in ('highwater_commit','cancel_fence_commit'):
                    highwater = max(highwater, token)
            if event == 'O':
                old_accept, old_state = accepted, state
            else:
                new_accept = accepted
        trace.append({'event':event,'active':active,'generation':generation,'highwater':highwater,'accepted':accepted,'effects':effects[:]})
    assert old_accept is not None and new_accept is not None
    stale = events.index('O') > events.index('A1')
    return {'n':n,'rule':rule,'schedule':list(events),'check':check_state,'old_state':old_state,
        'old_accepted':old_accept,'new_accepted':new_accept,'stale_attempt':stale,
        'stale_accepted':stale and old_accept,
        'stale_after_new':stale and old_accept and events.index('O') > events.index('N'),
        'stale_while_inactive':stale and old_accept and not old_state['active'],
        'rejected_valid_old':not stale and not old_accept,'effects':effects,'trace':trace,
        'final':{'active':active,'generation':generation,'highwater':highwater}}


def formula(n,events,rule):
    # Index-based oracle. It does not call the transition interpreter.
    p = {event:j for j,event in enumerate(events)}
    cut_count = sum(p[f'A{i}'] < p['O'] for i in range(1,n+1))
    start_count = sum(p[f'R{i}'] < p['O'] for i in range(1,n+1))
    if rule == 'active_commit':
        return cut_count == start_count
    if rule.startswith('modulo'):
        modulus = 2 if rule == 'modulo2_commit' else 4
        return cut_count == start_count and cut_count % modulus == 0
    if rule == 'unique_precheck':
        return p['C'] < p['A1']
    if rule in ('unique_commit','cancel_fence_commit'):
        return p['O'] < p['A1']
    if rule == 'highwater_commit':
        return p['O'] < p['N']
    raise ValueError(rule)


def controls():
    cases = [
      ('before_cancel',1,['C','O','A1','R1','N']),
      ('while_inactive',1,['C','A1','O','R1','N']),
      ('active_reused',1,['A1','R1','C','O','N']),
      ('wrap_two',2,['A1','R1','A2','R2','C','O','N']),
      ('wrap_four',4,['A1','R1','A2','R2','A3','R3','A4','R4','C','O','N']),
      ('check_use_gap',1,['C','A1','R1','O','N']),
      ('highwater_before_new',1,['A1','R1','C','O','N']),
      ('highwater_after_new',1,['A1','R1','N','C','O']),
      ('fence_after_cancel',1,['C','A1','O','R1','N'])]
    rows=[]
    for name,n,events in cases:
        for rule in RULES:
            row=run_case(n,events,rule)
            expected=formula(n,events,rule)
            assert row['old_accepted'] == expected
            assert row['new_accepted']
            rows.append({'control':name,'rule':rule,'expected_old_accepted':expected,'passed':True})
    # Fixed expected witnesses ensure formula itself is not the only control.
    assert run_case(1,cases[0][2],'cancel_fence_commit')['old_accepted']
    assert run_case(1,cases[1][2],'highwater_commit')['old_accepted']
    assert not run_case(1,cases[1][2],'cancel_fence_commit')['old_accepted']
    assert run_case(2,cases[3][2],'modulo2_commit')['old_accepted']
    assert not run_case(2,cases[3][2],'modulo4_commit')['old_accepted']
    assert run_case(4,cases[4][2],'modulo4_commit')['old_accepted']
    assert run_case(1,cases[5][2],'unique_precheck')['old_accepted']
    assert not run_case(1,cases[7][2],'highwater_commit')['old_accepted']
    return rows


def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    names=['raw_results.jsonl','summary.csv','summary.json','controls.json','checks.json','witnesses.json','execution.json','execution.log','failure.json']
    if any((out/x).exists() for x in names):
        raise SystemExit('Refuse to overwrite an existing run')
    config=json.loads((HERE/'config.json').read_text())
    assert config['rules'] == RULES
    resource.setrlimit(resource.RLIMIT_CPU,(config['cpu_limit_seconds'],config['cpu_limit_seconds']+1))
    start=time.monotonic(); cpu=time.process_time()
    execution={'started_at_utc':datetime.now(timezone.utc).isoformat(),'command':['python3','study.py','--out',str(out)],
      'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'config_sha256':hashlib.sha256((HERE/'config.json').read_bytes()).hexdigest(),'pid':os.getpid(),'no_paid_compute':True,'no_model_calls':True}
    dump(out/'execution.json',execution)
    log=open(out/'execution.log','w')
    try:
        ctrl=controls(); dump(out/'controls.json',ctrl); log.write(f'PASS controls: {len(ctrl)} rule rows\n'); log.flush()
        aggregate={r:{'cases':0,'stale_attempts':0,'old_accepted':0,'stale_accepted':0,'stale_after_new':0,'stale_while_inactive':0,'rejected_valid_old':0,'new_accepted':0} for r in RULES}
        by_setting=[]; witnesses={}; unique=0; checked=0
        with open(out/'raw_results.jsonl','w') as raw:
            for n in config['restart_counts']:
                events_list=list(schedules(n))
                assert len(set(events_list)) == len(events_list) == math.comb(2*n+3,2)
                assert set(events_list) == inserted_schedules(n)
                unique += len(events_list)
                setting={r:{key:0 for key in aggregate[r]} for r in RULES}
                for local_id,events in enumerate(events_list,1):
                    for rule in RULES:
                        row=run_case(n,events,rule)
                        row['case_id']=f'n{n}-s{local_id:04d}-{rule}'
                        assert row['old_accepted'] == formula(n,events,rule)
                        assert row['new_accepted'] and not row['rejected_valid_old']
                        for data in (aggregate[rule],setting[rule]):
                            data['cases']+=1
                            data['stale_attempts']+=int(row['stale_attempt'])
                            for key in ['old_accepted','stale_accepted','stale_after_new','stale_while_inactive','rejected_valid_old','new_accepted']:
                                data[key]+=int(row[key])
                        if row['stale_accepted'] and rule not in witnesses:
                            witnesses[rule]=row
                        raw.write(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n')
                        checked+=1
                    if time.monotonic()-start > config['wall_limit_seconds']:
                        raise TimeoutError('Wall-time limit')
                for rule in RULES:
                    by_setting.append({'n':n,'rule':rule,**setting[rule]})
                log.write(f'PASS n={n}: {len(events_list)} schedules, {len(events_list)*len(RULES)} policy cases\n');log.flush()
        with open(out/'summary.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(by_setting[0]));w.writeheader();w.writerows(by_setting)
        dump(out/'summary.json',aggregate);dump(out/'witnesses.json',witnesses)
        hyp={
          'H1':aggregate['active_commit']['stale_accepted']>0,
          'H2':witnesses['modulo2_commit']['n']==2 and witnesses['modulo4_commit']['n']==4,
          'H3':aggregate['unique_precheck']['stale_accepted']>0,
          'H4':all(aggregate[r]['stale_accepted']==0 for r in ['unique_commit','cancel_fence_commit']),
          'H5':aggregate['highwater_commit']['stale_accepted']>0 and aggregate['highwater_commit']['stale_after_new']==0,
          'H6':all(v['new_accepted']==v['cases'] and v['rejected_valid_old']==0 for v in aggregate.values())}
        dump(out/'checks.json',{'schedule_count':unique,'policy_cases':checked,'index_formula_checks':checked,'independent_enumeration_matches':True,'control_rule_rows':len(ctrl),'unknowns':0,'hypotheses':hyp})
        log.write('COMPLETE: all assigned cases retained; no unknowns\n')
        execution['completed']=True
    except BaseException as e:
        dump(out/'failure.json',{'type':type(e).__name__,'message':str(e)})
        execution['completed']=False
        log.write(f'FAIL {type(e).__name__}: {e}\n')
        raise
    finally:
        execution.update({'ended_at_utc':datetime.now(timezone.utc).isoformat(),'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-start,'max_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
        dump(out/'execution.json',execution);log.close()
    print(json.dumps({'out':str(out),'schedules':unique,'policy_cases':checked,'hypotheses':hyp,'cpu_seconds':execution['cpu_seconds']},sort_keys=True))

if __name__ == '__main__':
    main()
