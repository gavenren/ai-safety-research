"""Compare saved evidence with the separately frozen prefix formulas.

The main source was read for its schema and control inputs after both source
freezes. This adapter imports no main code. Expected SQL checks the complete
planned statement sequence, while state values come from independent formulas.
"""
import argparse
import csv
import gzip
import hashlib
import json
import sqlite3
from pathlib import Path
from independent_spec import RULES, inputs, evaluate

STATE_NAMES = {'s':'spent', 'r':'hold', 'C':'cap', 'e':'revision'}
SCORE_NAMES = {'u_accepted':'cap_accepted', 'u_refused':'cap_refused',
               'already_spent_excess_at_u':'past_use_excess_at_change',
               'hold_exposure_only_at_u':'hold_exposure_at_change',
               'b_accepted':'b_admitted'}
SUMS = ('cap_accepted','cap_refused','unsafe_change','feasible_refusal',
        'past_use_excess_at_change','hold_exposure_at_change','b_admitted',
        'b_refused','covered_breach','actual_breach','exposure_without_actual')
MAXES = ('max_covered_excess','max_actual_excess','final_actual_excess')


def row(value):
    return {STATE_NAMES[key]: item for key,item in value.items()}


def public_input(setting):
    return {('c0' if key=='C0' else key): value for key,value in setting.items()}


def model_input(setting):
    return {('C0' if key=='c0' else key): value for key,value in setting.items()}


def expected_trace(setting, rule, label='primary'):
    expected=evaluate(setting,rule)
    result={'key':label+':'+setting['id']+':'+rule,'input':public_input(setting),
            'rule':rule,'initial':row(expected['states'][0]),'steps':[]}
    for step in expected['events']:
        event=step['event']
        before,after=row(step['before']),row(step['after'])
        if event=='R':
            decision={'snapshot':row(expected['snapshot'])}
        elif event=='U':
            v=expected['u']
            decision={'accepted':v['accepted'],'requested_cap':setting['n'],
                      'conditions':{'current_spent_ok':v['current_spent_fits'],
                                    'current_cover_ok':v['current_feasible'],
                                    'saved_cover_ok':v['snapshot_fits'],
                                    'same_revision':v['revision_matches']}}
        elif event=='B':
            decision={'accepted':expected['b']['accepted'],'demand':setting['b'],
                      'cover_before':before['spent']+before['hold'],'cap':before['cap']}
        else:
            decision={'settled':setting['x'],'released':setting['a']-setting['x']}
        result['steps'].append({'event':event,'before':before,'decision':decision,'after':after})
    result['score']={SCORE_NAMES.get(key,key):value for key,value in expected['scores'].items()
                     if key not in ('actual_first_at_u','actual_first_at_s','requested_cap_feasible_at_u')}
    return result


def controls():
    # These named fixture inputs were read from the frozen main source.
    settings=(('already_impossible',2,1,0,0,1,1,'RUSB'),
              ('pending_liability',0,2,2,0,1,1,'RUBS'),
              ('intervening_b',0,1,1,2,1,1,'RBUS'),
              ('returned_hold',0,2,0,0,1,1,'RSUB'),
              ('same_covered_total',0,2,2,1,2,1,'RSUB'),
              ('serial_feasible',0,2,0,1,1,1,'SRUB'))
    return [dict(id=name,s0=s,a=a,x=x,slack=k,C0=s+a+k,n=n,b=b,order=list(o))
            for name,s,a,x,k,n,b,o in settings]


def groups(setting):
    order=setting['order']
    b,r,u=(order.index(e) for e in 'BRU')
    return ('all', 'settle_before_U' if order.index('S')<u else 'settle_after_U',
            'B_before_R' if b<r else ('B_between_R_U' if b<u else 'B_after_U'),
            'prior_spent_zero' if setting['s0']==0 else 'prior_spent_positive',
            'full_settlement' if setting['x']==setting['a'] else 'unused_return')


def add_summary(summary,rule,group,score):
    key=(rule,group)
    if key not in summary:
        summary[key]={'rule':rule,'group':group,'cases':0,
                      **dict.fromkeys(SUMS+MAXES,0),'actual_first_U':0,'actual_first_S':0}
    v=summary[key]
    v['cases']+=1
    for name in SUMS:
        v[name]+=int(score[name])
    for name in MAXES:
        v[name]=max(v[name],score[name])
    v['actual_first_U']+=int(score['first_actual_event']=='U')
    v['actual_first_S']+=int(score['first_actual_event']=='S')


def sql_row(case,event,caller,statement):
    return {'case':case,'event':event,'caller':caller,'sql':statement}


def trial_sql(trace):
    key=trace['key']; inp=trace['input']
    select=f"SELECT cap,spent,hold,revision FROM ledger WHERE id='{key}'"
    yield sql_row(key,'initial','setup',f"INSERT INTO ledger VALUES ('{key}',{inp['c0']},{inp['s0']},{inp['a']},0)")
    yield sql_row(key,'initial','audit',select)
    for step in trace['steps']:
        event=step['event']; decision=step['decision']
        yield sql_row(key,event,'audit',select)
        if event=='R':
            yield sql_row(key,event,'cap',select)
        else:
            who={'U':'cap','S':'A','B':'B'}[event]
            yield sql_row(key,event,who,'BEGIN IMMEDIATE')
            yield sql_row(key,event,who,select)
            if event=='U' and decision['accepted']:
                yield sql_row(key,event,who,f"UPDATE ledger SET cap={inp['n']},revision=revision+1 WHERE id='{key}'")
            elif event=='S':
                yield sql_row(key,event,who,f"UPDATE ledger SET spent=spent+{inp['x']},hold=0,revision=revision+1 WHERE id='{key}'")
            elif event=='B' and decision['accepted']:
                yield sql_row(key,event,who,f"UPDATE ledger SET spent=spent+{inp['b']},revision=revision+1 WHERE id='{key}'")
            yield sql_row(key,event,who,'COMMIT')
        yield sql_row(key,event,'audit',select)


def engine_sql():
    key='engine_control'; select="SELECT cap,spent,hold,revision FROM ledger WHERE id='engine_control'"
    statements=[('initial','setup',"INSERT INTO ledger VALUES ('engine_control',5,1,2,0)"),
                ('initial','audit',select),
                ('rollback','cap','BEGIN IMMEDIATE'),
                ('rollback','cap',"UPDATE ledger SET spent=9,cap=1,revision=revision+1 WHERE id='engine_control'"),
                ('rollback','cap',select),('rollback','audit',select),
                ('rollback','cap','ROLLBACK'),('rollback','audit',select),
                ('refused_guard','cap','BEGIN IMMEDIATE'),
                ('refused_guard','cap',"UPDATE ledger SET cap=0,revision=revision+1 WHERE id='engine_control' AND spent+hold<=0"),
                ('refused_guard','cap','COMMIT'),('refused_guard','audit',select)]
    return [sql_row(key,*statement) for statement in statements]


def load_json_lines(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:
        yield from (json.loads(line) for line in f)


def compare(result_dir):
    p=Path(result_dir)
    settings=list(inputs())
    assert json.loads((p/'inputs.json').read_text())==[public_input(i) for i in settings]
    observed=iter(load_json_lines(p/'traces.jsonl.gz'))
    sql=iter(load_json_lines(p/'sql.jsonl.gz'))
    sql_count=0
    def check_sql(want):
        nonlocal sql_count
        got=next(sql)
        assert got==want, ('SQL mismatch',sql_count,got,want)
        sql_count+=1
    check_sql(sql_row('setup','setup','setup','CREATE TABLE ledger (id TEXT PRIMARY KEY, cap INTEGER NOT NULL, spent INTEGER NOT NULL, hold INTEGER NOT NULL, revision INTEGER NOT NULL)'))
    summary={}; witnesses={}; final=[]
    paired={r:dict.fromkeys(('cap_disagreement','b_disagreement','unsafe_extra','feasible_refusal_extra'),0) for r in RULES}
    cases=0
    for setting in settings:
        expected={rule:expected_trace(setting,rule) for rule in RULES}
        baseline=expected['AtomicCover']['score']
        for rule in RULES:
            want=expected[rule]
            got=next(observed)
            assert got==want, ('complete trace mismatch',setting['id'],rule)
            for statement in trial_sql(want):check_sql(statement)
            final.append(dict(id=want['key'],**want['steps'][-1]['after']))
            score=want['score']
            for group in groups(setting):add_summary(summary,rule,group,score)
            for metric in ('unsafe_change','feasible_refusal','actual_breach','exposure_without_actual'):
                if score[metric]:witnesses.setdefault(rule+':'+metric,want)
            v=paired[rule]
            v['cap_disagreement']+=int(score['cap_accepted']!=baseline['cap_accepted'])
            v['b_disagreement']+=int(score['b_admitted']!=baseline['b_admitted'])
            v['unsafe_extra']+=int(score['unsafe_change'])-int(baseline['unsafe_change'])
            v['feasible_refusal_extra']+=int(score['feasible_refusal'])-int(baseline['feasible_refusal'])
            cases+=1
    assert next(observed,None) is None
    expected_controls=[expected_trace(i,r,'control') for i in controls() for r in RULES]
    assert json.loads((p/'controls.json').read_text())==expected_controls
    for trace in expected_controls:
        for statement in trial_sql(trace):check_sql(statement)
        final.append(dict(id=trace['key'],**trace['steps'][-1]['after']))
    initial=dict(cap=5,spent=1,hold=2,revision=0)
    expected_engine={'initial':initial,'inside_uncommitted':dict(cap=1,spent=9,hold=2,revision=1),
                     'outside_during':initial,'after_rollback':initial,'refused_rowcount':0,
                     'after_refusal':initial,'passed':True}
    assert json.loads((p/'engine_controls.json').read_text())==expected_engine
    for statement in engine_sql():check_sql(statement)
    check_sql(sql_row('final','integrity','audit','PRAGMA integrity_check'))
    assert next(sql,None) is None
    final.append(dict(id='engine_control',**initial)); final.sort(key=lambda x:x['id'])
    assert json.loads((p/'final_rows.json').read_text())==final
    with sqlite3.connect(p.resolve().as_uri()+'/ledger.sqlite?mode=ro',uri=True) as db:
        integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
        assert integrity=='ok'
        db_rows=[dict(zip(('id','cap','spent','hold','revision'),r)) for r in db.execute('SELECT id,cap,spent,hold,revision FROM ledger ORDER BY id')]
        assert db_rows==final
    with (p/'summary.csv').open(newline='') as f:
        summary_rows=[{k:(v if k in ('rule','group') else int(v)) for k,v in r.items()} for r in csv.DictReader(f)]
    assert summary_rows==[summary[k] for k in sorted(summary)]
    assert json.loads((p/'paired.json').read_text())==paired
    assert json.loads((p/'witnesses.json').read_text())==witnesses
    checks={'passed':True,'input_histories':len(settings),'rules':len(RULES),'rule_cases':cases,
            'primary_steps':cases*4,'primary_state_records':cases*9,'control_rule_cases':len(expected_controls),
            'final_rows':len(final),'integrity':'ok','reopened_integrity':'ok','sql_statements':sql_count}
    assert json.loads((p/'checks.json').read_text())==checks
    return dict(passed=True,input_histories=len(settings),primary_rule_cases=cases,
                primary_states=cases*9,primary_steps=cases*4,primary_cap_and_b_decisions=cases*2,
                complete_sql_statements=sql_count,control_rule_cases=len(expected_controls),
                control_states=len(expected_controls)*9,summary_rows=len(summary),paired_rules=len(paired),
                first_adverse_examples=len(witnesses),reopened_rows=len(final),reopened_integrity=integrity,
                all_summary=[summary[(r,'all')] for r in RULES],
                independent_source_sha256=hashlib.sha256(Path(__file__).with_name('independent_spec.py').read_bytes()).hexdigest(),
                scope='Every saved input, full trace, decision, score, summary, paired outcome, first witness, control, SQL statement, and reopened ledger row was checked.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--results',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    outcome=compare(args.results)
    Path(args.out).write_text(json.dumps(outcome,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in outcome.items() if k!='all_summary'}))
