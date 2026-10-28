"""Synthetic ordered schedules on real local SQLite. Standard library only."""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import platform
import resource
import sqlite3
import sys
import time
from pathlib import Path

RULES = ['BlindSet', 'SpentOnly', 'CachedCover', 'VersionedCover', 'AtomicCover']
FIELDS = ['cap', 'spent', 'hold', 'revision']
ORDERS = sorted(p for p in itertools.permutations('RUSB') if p.index('R') < p.index('U'))

def jdump(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))

def gzopen(path):
    return gzip.GzipFile(filename='', fileobj=path.open('wb'), mode='wb', mtime=0)

def inputs():
    rows = []
    for s0 in range(3):
        for a in (1, 2):
            for x in range(a+1):
                for slack in range(3):
                    c0 = s0+a+slack
                    for n in range(c0):
                        for b in (1, 2):
                            for order in ORDERS:
                                rows.append(dict(id=f'h{len(rows):05d}', s0=s0, a=a, x=x,
                                                 slack=slack, c0=c0, n=n, b=b, order=list(order)))
    return rows

def control_inputs():
    settings = [
        ('already_impossible',2,1,0,0,1,1,'RUSB'),
        ('pending_liability',0,2,2,0,1,1,'RUBS'),
        ('intervening_b',0,1,1,2,1,1,'RBUS'),
        ('returned_hold',0,2,0,0,1,1,'RSUB'),
        ('same_covered_total',0,2,2,1,2,1,'RSUB'),
        ('serial_feasible',0,2,0,1,1,1,'SRUB')]
    return [dict(id=name,s0=s,a=a,x=x,slack=k,c0=s+a+k,n=n,b=b,order=list(o))
            for name,s,a,x,k,n,b,o in settings]

def exposure(state):
    return state['spent']+state['hold']

def score(trace):
    steps = trace['steps']
    u = next(t for t in steps if t['event']=='U')
    b = next(t for t in steps if t['event']=='B')
    states = [('initial',trace['initial'])]+[(t['event'],t['after']) for t in steps]
    covered = [(e,max(0,exposure(s)-s['cap'])) for e,s in states]
    actual = [(e,max(0,s['spent']-s['cap'])) for e,s in states]
    uc = u['decision']['accepted']
    n = trace['input']['n']
    first_cov = next((e for e,v in covered if v),None)
    first_act = next((e for e,v in actual if v),None)
    return dict(cap_accepted=uc, cap_refused=not uc,
                unsafe_change=uc and exposure(u['before'])>n,
                feasible_refusal=not uc and exposure(u['before'])<=n,
                past_use_excess_at_change=uc and u['before']['spent']>n,
                hold_exposure_at_change=uc and u['before']['spent']<=n<exposure(u['before']),
                b_admitted=b['decision']['accepted'], b_refused=not b['decision']['accepted'],
                covered_breach=first_cov is not None, actual_breach=first_act is not None,
                exposure_without_actual=first_cov is not None and first_act is None,
                first_covered_event=first_cov, first_actual_event=first_act,
                max_covered_excess=max(v for _,v in covered), max_actual_excess=max(v for _,v in actual),
                final_actual_excess=max(0,states[-1][1]['spent']-states[-1][1]['cap']))

class Experiment:
    def __init__(self, out):
        self.out=out
        self.log=gzopen(out/'sql.jsonl.gz')
        self.context={'case':'setup','event':'setup'}
        self.sql_count=0
        self.db=out/'ledger.sqlite'
        self.connections={}
        for who in ('setup','cap','A','B','audit'):
            c=sqlite3.connect(self.db, isolation_level=None)
            c.execute('PRAGMA journal_mode=WAL')
            c.execute('PRAGMA synchronous=FULL')
            c.execute('PRAGMA read_uncommitted=OFF')
            c.set_trace_callback(lambda sql,who=who:self.sql(who,sql))
            self.connections[who]=c
        self.connections['setup'].execute('CREATE TABLE ledger (id TEXT PRIMARY KEY, cap INTEGER NOT NULL, spent INTEGER NOT NULL, hold INTEGER NOT NULL, revision INTEGER NOT NULL)')

    def sql(self, who, sql):
        self.log.write((jdump(dict(self.context,caller=who,sql=sql))+'\n').encode())
        self.sql_count+=1

    def read(self, who, key):
        cur=self.connections[who].execute('SELECT cap,spent,hold,revision FROM ledger WHERE id=?',(key,))
        row=cur.fetchone(); cur.close()
        assert row is not None
        return dict(zip(FIELDS,row))

    def trial(self, inp, rule, label='primary'):
        key=label+':'+inp['id']+':'+rule
        self.context={'case':key,'event':'initial'}
        self.connections['setup'].execute('INSERT INTO ledger VALUES (?,?,?,?,?)',(key,inp['c0'],inp['s0'],inp['a'],0))
        trace={'key':key,'input':inp,'rule':rule,'initial':self.read('audit',key),'steps':[]}
        snapshot=None
        for event in inp['order']:
            self.context={'case':key,'event':event}
            before=self.read('audit',key)
            decision=None
            if event=='R':
                snapshot=self.read('cap',key)
                assert not self.connections['cap'].in_transaction
                decision={'snapshot':snapshot}
            else:
                who={'U':'cap','S':'A','B':'B'}[event]
                c=self.connections[who]
                c.execute('BEGIN IMMEDIATE')
                current=self.read(who,key)
                if event=='U':
                    assert snapshot is not None
                    conditions={'current_spent_ok':current['spent']<=inp['n'],
                                'current_cover_ok':exposure(current)<=inp['n'],
                                'saved_cover_ok':exposure(snapshot)<=inp['n'],
                                'same_revision':current['revision']==snapshot['revision']}
                    accepted={'BlindSet':True,'SpentOnly':conditions['current_spent_ok'],
                              'CachedCover':conditions['saved_cover_ok'],
                              'VersionedCover':conditions['saved_cover_ok'] and conditions['same_revision'],
                              'AtomicCover':conditions['current_cover_ok']}[rule]
                    if accepted:
                        c.execute('UPDATE ledger SET cap=?,revision=revision+1 WHERE id=?',(inp['n'],key))
                    decision=dict(accepted=accepted,requested_cap=inp['n'],conditions=conditions)
                elif event=='S':
                    assert current['hold']==inp['a']
                    c.execute('UPDATE ledger SET spent=spent+?,hold=0,revision=revision+1 WHERE id=?',(inp['x'],key))
                    decision={'settled':inp['x'],'released':inp['a']-inp['x']}
                else:
                    accepted=exposure(current)+inp['b']<=current['cap']
                    if accepted:
                        c.execute('UPDATE ledger SET spent=spent+?,revision=revision+1 WHERE id=?',(inp['b'],key))
                    decision={'accepted':accepted,'demand':inp['b'],'cover_before':exposure(current),'cap':current['cap']}
                c.execute('COMMIT')
            after=self.read('audit',key)
            if event in ('U','B') and not decision['accepted']:
                assert after==before
            if event=='B' and decision['accepted']:
                assert exposure(after)<=after['cap']
            trace['steps'].append(dict(event=event,before=before,decision=decision,after=after))
        trace['score']=score(trace)
        return trace

    def engine_controls(self):
        self.context={'case':'engine_control','event':'initial'}
        c=self.connections['cap']; setup=self.connections['setup']
        setup.execute('INSERT INTO ledger VALUES (?,?,?,?,?)',('engine_control',5,1,2,0))
        initial=self.read('audit','engine_control')
        self.context['event']='rollback'
        c.execute('BEGIN IMMEDIATE')
        c.execute("UPDATE ledger SET spent=9,cap=1,revision=revision+1 WHERE id='engine_control'")
        inside=self.read('cap','engine_control')
        outside=self.read('audit','engine_control')
        c.execute('ROLLBACK')
        after=self.read('audit','engine_control')
        assert outside==after==initial and inside!=initial
        self.context['event']='refused_guard'
        c.execute('BEGIN IMMEDIATE')
        changed=c.execute("UPDATE ledger SET cap=0,revision=revision+1 WHERE id='engine_control' AND spent+hold<=0").rowcount
        c.execute('COMMIT')
        refused_after=self.read('audit','engine_control')
        assert changed==0 and refused_after==initial
        return dict(initial=initial,inside_uncommitted=inside,outside_during=outside,after_rollback=after,
                    refused_rowcount=changed,after_refusal=refused_after,passed=True)

    def close(self):
        self.context={'case':'final','event':'integrity'}
        integrity=self.connections['audit'].execute('PRAGMA integrity_check').fetchone()[0]
        assert integrity=='ok'
        for c in self.connections.values(): c.close()
        self.log.close()
        with sqlite3.connect(self.db) as c:
            reopened_integrity=c.execute('PRAGMA integrity_check').fetchone()[0]
            rows=[dict(id=r[0],**dict(zip(FIELDS,r[1:]))) for r in c.execute('SELECT id,cap,spent,hold,revision FROM ledger ORDER BY id')]
        assert reopened_integrity=='ok'
        return dict(integrity=integrity,reopened_integrity=reopened_integrity,sql_statements=self.sql_count),rows

def groups(inp):
    o=inp['order']; b=o.index('B'); r=o.index('R'); u=o.index('U')
    return ['all','settle_before_U' if o.index('S')<u else 'settle_after_U',
            'B_before_R' if b<r else ('B_between_R_U' if b<u else 'B_after_U'),
            'prior_spent_zero' if inp['s0']==0 else 'prior_spent_positive',
            'full_settlement' if inp['x']==inp['a'] else 'unused_return']

SUM_KEYS=['cap_accepted','cap_refused','unsafe_change','feasible_refusal','past_use_excess_at_change',
          'hold_exposure_at_change','b_admitted','b_refused','covered_breach','actual_breach',
          'exposure_without_actual']
MAX_KEYS=['max_covered_excess','max_actual_excess','final_actual_excess']
def add_summary(summary, rule, group, s):
    row=summary.setdefault((rule,group),dict(rule=rule,group=group,cases=0,
        **{k:0 for k in SUM_KEYS+MAX_KEYS},actual_first_U=0,actual_first_S=0))
    row['cases']+=1
    for k in SUM_KEYS: row[k]+=int(s[k])
    for k in MAX_KEYS: row[k]=max(row[k],s[k])
    row['actual_first_U']+=int(s['first_actual_event']=='U')
    row['actual_first_S']+=int(s['first_actual_event']=='S')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=False)
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    start_cpu=time.process_time();start_wall=time.monotonic()
    matrix=inputs(); (out/'inputs.json').write_text(json.dumps(matrix,indent=2)+'\n')
    exp=Experiment(out); traces=gzopen(out/'traces.jsonl.gz')
    summary={};witnesses={};paired={r:{'cap_disagreement':0,'b_disagreement':0,'unsafe_extra':0,'feasible_refusal_extra':0} for r in RULES}
    states=steps=case_count=0
    for inp in matrix:
        bundle={}
        for rule in RULES:
            trace=exp.trial(inp,rule);bundle[rule]=trace
            traces.write((jdump(trace)+'\n').encode())
            case_count+=1;steps+=4;states+=9
            s=trace['score']
            for g in groups(inp):add_summary(summary,rule,g,s)
            for metric in ('unsafe_change','feasible_refusal','actual_breach','exposure_without_actual'):
                if s[metric]:witnesses.setdefault(rule+':'+metric,trace)
        baseline=bundle['AtomicCover']['score']
        for rule,t in bundle.items():
            for target,field in [('cap_disagreement','cap_accepted'),('b_disagreement','b_admitted')]:
                paired[rule][target]+=int(t['score'][field]!=baseline[field])
            paired[rule]['unsafe_extra']+=int(t['score']['unsafe_change'])-int(baseline['unsafe_change'])
            paired[rule]['feasible_refusal_extra']+=int(t['score']['feasible_refusal'])-int(baseline['feasible_refusal'])
        if time.monotonic()-start_wall>450:raise RuntimeError('wall limit')
        if inp['id'].endswith('00') and sum(p.stat().st_size for p in out.iterdir() if p.is_file())>200_000_000:raise RuntimeError('output limit')
    traces.close()
    controls=[exp.trial(i,r,'control') for i in control_inputs() for r in RULES]
    engine=exp.engine_controls()
    dbcheck,rows=exp.close()
    summary_rows=[summary[k] for k in sorted(summary)]
    with (out/'summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary_rows[0]));writer.writeheader();writer.writerows(summary_rows)
    for name,obj in [('paired.json',paired),('controls.json',controls),('engine_controls.json',engine),('witnesses.json',witnesses),('final_rows.json',rows)]:
        (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
    totals={r:summary[(r,'all')] for r in RULES}
    assert all(totals[r]['covered_breach']==0 for r in ['VersionedCover','AtomicCover'])
    assert totals['AtomicCover']['feasible_refusal']==0
    assert all(row['unsafe_change']==row['covered_breach'] for row in totals.values())
    checks=dict(passed=True,input_histories=len(matrix),rules=len(RULES),rule_cases=case_count,
                primary_steps=steps,primary_state_records=states,control_rule_cases=len(controls),
                final_rows=len(rows),**dbcheck)
    (out/'checks.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    cpu=time.process_time()-start_cpu;wall=time.monotonic()-start_wall
    size=sum(p.stat().st_size for p in out.iterdir() if p.is_file())
    assert size<=200_000_000 and wall<=450
    env=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform(),machine=platform.machine(),
             cpu_seconds=cpu,wall_seconds=wall,output_bytes_before_environment=size,
             model='Codex generated the study; exact model build not exposed',seed=None,external_calls=0,
             limits=dict(cpu_seconds=120,wall_seconds=450,saved_output_bytes=200_000_000),
             sqlite_settings=dict(journal_mode='WAL',synchronous='FULL',read_uncommitted=False,shared_cache=False),
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
    print(json.dumps(dict(checks,cpu_seconds=cpu,wall_seconds=wall)))

if __name__=='__main__':main()
