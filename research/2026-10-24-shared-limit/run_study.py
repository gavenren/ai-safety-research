#!/usr/bin/env python3
"""Scheduled SQLite experiment. No external effects or third-party packages."""
import argparse, csv, gzip, hashlib, itertools, json, platform, resource
import sqlite3, sys, time, traceback
from pathlib import Path

POLICIES = ['OwnCAS', 'SharedEpoch', 'AtomicSum']
READ = '''SELECT q.capacity,q.epoch,q.note,a.units,a.version,b.units,b.version
FROM quotas q JOIN allocations a ON a.case_id=q.id AND a.worker=0
JOIN allocations b ON b.case_id=q.id AND b.worker=1 WHERE q.id=?'''
SCHEMA = '''CREATE TABLE quotas(id TEXT PRIMARY KEY,capacity INTEGER,epoch INTEGER,note INTEGER);
CREATE TABLE allocations(case_id TEXT,worker INTEGER,units INTEGER,version INTEGER,
PRIMARY KEY(case_id,worker),FOREIGN KEY(case_id) REFERENCES quotas(id));'''


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def gzwrite(path, data):
    with path.open('wb') as f:
        with gzip.GzipFile(fileobj=f, mode='wb', filename='', mtime=0) as g:
            g.write(data)


def sql(conn, statement, params, log):
    cur = conn.execute(statement, params)
    rows = [list(x) for x in cur.fetchall()]
    changed = cur.rowcount
    cur.close()
    log.append({'sql': statement, 'params': list(params), 'rows': rows, 'rowcount': changed})
    return rows, changed


def state(conn, cid, log):
    r = sql(conn, READ, (cid,), log)[0][0]
    return {'capacity':r[0], 'epoch':r[1], 'note':r[2],
            'units':[r[3],r[5]], 'versions':[r[4],r[6]]}


def connect(path):
    c = sqlite3.connect(path, isolation_level=None, timeout=1.0)
    c.execute('PRAGMA synchronous=FULL').close()
    c.execute('PRAGMA read_uncommitted=OFF').close()
    c.execute('PRAGMA foreign_keys=ON').close()
    return c


def inputs():
    base = [list(p) for p in itertools.permutations(['RA','CA','RB','CB'])
            if p.index('RA') < p.index('CA') and p.index('RB') < p.index('CB')]
    schedules=[]
    for index, order in enumerate(base):
        schedules.append((index, -1, order))
        for gap in range(5):
            schedules.append((index, gap, order[:gap]+['U']+order[gap:]))
    return [{'capacity':cap,'demands':list(ds),'base_order':idx,'u_position':u,'schedule':s}
            for cap in range(1,5) for ds in itertools.product([1,2],repeat=2)
            for idx,u,s in schedules]


def engine_controls(path):
    a=connect(path); a.execute('PRAGMA journal_mode=WAL').close()
    a.execute('CREATE TABLE control(id INTEGER PRIMARY KEY,units INTEGER,version INTEGER,epoch INTEGER)').close()
    a.execute('INSERT INTO control VALUES(1,0,0,0)').close(); b=connect(path)
    log=[]; checks={}
    sql(a,'SELECT * FROM control',(),log); sql(b,'SELECT * FROM control',(),log)
    first=sql(a,'UPDATE control SET units=1,version=1,epoch=1 WHERE id=1 AND version=0',(),log)[1]
    second=sql(b,'UPDATE control SET units=2,version=2,epoch=2 WHERE id=1 AND version=0',(),log)[1]
    checks['stale_same_row_CAS'] = first==1 and second==0 and sql(a,'SELECT * FROM control',(),log)[0]==[[1,1,1,1]]
    sql(a,'UPDATE control SET units=0,version=0,epoch=0',(),log)
    sql(a,'BEGIN',(),log); sql(a,'SELECT * FROM control',(),log)
    sql(b,'UPDATE control SET units=1,version=1,epoch=1',(),log)
    try:
        sql(a,'UPDATE control SET units=2,version=2,epoch=2',(),log)
        raise AssertionError('Expected stale-snapshot rejection was absent')
    except sqlite3.OperationalError as e:
        log.append({'expected_error':str(e),'sqlite_errorcode':e.sqlite_errorcode,'sqlite_errorname':e.sqlite_errorname})
        checks['held_snapshot_rejected'] = e.sqlite_errorcode == 517
    sql(a,'ROLLBACK',(),log)
    sql(a,'UPDATE control SET units=0,version=0,epoch=0',(),log)
    sql(a,'BEGIN IMMEDIATE',(),log)
    sql(a,'UPDATE control SET units=1,version=1,epoch=1',(),log)
    sql(a,'ROLLBACK',(),log)
    checks['effect_and_epoch_rollback'] = sql(b,'SELECT * FROM control',(),log)[0]==[[1,0,0,0]]
    a.close(); b.close(); assert all(checks.values()), checks
    return {'checks':checks,'sql_log':log}


def case(conns, cid, spec, pair):
    a,b,u,audit=conns; setup=[]
    sql(a,'BEGIN IMMEDIATE',(),setup)
    sql(a,'INSERT INTO quotas VALUES(?,?,0,0)',(cid,spec['capacity']),setup)
    for worker in [0,1]: sql(a,'INSERT INTO allocations VALUES(?,?,0,0)',(cid,worker),setup)
    sql(a,'COMMIT',(),setup)
    observations=[None,None]; jobs=[None,None]; trace=[]; initial=state(audit,cid,setup)
    for event in spec['schedule']:
        log=[]; before=state(audit,cid,log); obs=None; decision=None
        if event=='U':
            sql(u,'BEGIN IMMEDIATE',(),log)
            sql(u,'UPDATE quotas SET note=1-note,epoch=epoch+1 WHERE id=?',(cid,),log)
            sql(u,'COMMIT',(),log)
        else:
            worker=0 if event[-1]=='A' else 1; conn=conns[worker]; demand=spec['demands'][worker]
            if event[0]=='R':
                obs=state(conn,cid,log); observations[worker]=obs
                assert not conn.in_transaction
            else:
                read=observations[worker]; assert read is not None
                eligible=sum(read['units'])+demand<=spec['capacity']; accepted=False
                reason='read_denial'; attempted=0
                if eligible:
                    attempted=1; sql(conn,'BEGIN IMMEDIATE',(),log)
                    query='UPDATE allocations SET units=?,version=version+1 WHERE case_id=? AND worker=? AND units=0 AND version=?'
                    params=[demand,cid,worker,read['versions'][worker]]
                    if pair[worker]=='SharedEpoch':
                        query+=' AND EXISTS(SELECT 1 FROM quotas WHERE id=? AND epoch=?)';params += [cid,read['epoch']]
                    elif pair[worker]=='AtomicSum':
                        query+=' AND (SELECT SUM(units) FROM allocations WHERE case_id=?)+? <= (SELECT capacity FROM quotas WHERE id=?)';params += [cid,demand,cid]
                    accepted=sql(conn,query,params,log)[1]==1
                    if accepted: sql(conn,'UPDATE quotas SET epoch=epoch+1 WHERE id=?',(cid,),log)
                    sql(conn,'COMMIT',(),log)
                    reason='accepted' if accepted else 'guard_refusal'
                decision={'accepted':accepted,'reason':reason,'write_attempt':attempted,
                          'feasible_before':sum(before['units'])+demand<=spec['capacity']}
                jobs[worker]=decision
        after=state(audit,cid,log)
        assert all(not c.in_transaction for c in conns)
        trace.append({'event':event,'before':before,'read':obs,'decision':decision,'after':after,'sql_log':log})
    assert all(j is not None for j in jobs)
    final=trace[-1]['after'];accepted=sum(j['accepted'] for j in jobs)
    bad=sum(bool(e['decision'] and e['decision']['accepted'] and sum(e['after']['units'])>spec['capacity']) for e in trace)
    scores={'breach':int(any(sum(e['after']['units'])>spec['capacity'] for e in trace)),
            'accepted_jobs':accepted,'refused_jobs':2-accepted,'bad_admissions':bad,
            'feasible_refusals':sum(not j['accepted'] and j['feasible_before'] for j in jobs),
            'excess_units':max(0,sum(final['units'])-spec['capacity']),
            'row_errors':sum(final['units'][i] != (spec['demands'][i] if jobs[i]['accepted'] else 0) or final['versions'][i] != int(jobs[i]['accepted']) for i in [0,1]),
            'epoch_errors':int(final['epoch'] != accepted+int(spec['u_position']>=0)),
            'reads':2,'write_attempts':sum(j['write_attempt'] for j in jobs),
            'guard_refusals':sum(j['reason']=='guard_refusal' for j in jobs),
            'read_denials':sum(j['reason']=='read_denial' for j in jobs)}
    return {'case_id':cid,'input':spec,'policies':list(pair),'initial':initial,'setup_sql':setup,
            'trace':trace,'jobs':jobs,'final':final,'scores':scores}


def main(out):
    out.mkdir(parents=True,exist_ok=False)
    cpu=time.process_time(); wall=time.monotonic(); deadline=wall+450
    resource.setrlimit(resource.RLIMIT_CPU,(120,125))
    controls=engine_controls(out/'controls.sqlite')
    (out/'controls.json').write_text(json.dumps(controls,indent=2)+'\n')
    db=out/'evidence.sqlite'; init=connect(db); mode=init.execute('PRAGMA journal_mode=WAL').fetchone()[0]
    init.executescript(SCHEMA);init.close()
    conns=[connect(db) for _ in range(4)]; specs=inputs(); assert len(specs)==576
    (out/'inputs.json').write_text(json.dumps(specs,indent=2)+'\n')
    totals={}; finals={}; case_count=0
    with (out/'traces.jsonl.gz').open('wb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as g:
            for spec in specs:
                for pair in itertools.product(POLICIES,repeat=2):
                    assert time.monotonic()<deadline, '450 wall second gate exceeded'
                    cid=f'c{case_count:05d}'; row=case(conns,cid,spec,pair)
                    g.write((encode(row)+'\n').encode()); finals[cid]=row['final']; case_count+=1
                    for stratum in ['all','no_U' if spec['u_position']<0 else 'with_U']:
                        key=(*pair,stratum)
                        if key not in totals:totals[key]={'policy_A':pair[0],'policy_B':pair[1],'stratum':stratum,'cases':0,**{k:0 for k in row['scores']},'maximum_excess':0}
                        total=totals[key];total['cases']+=1
                        for k,v in row['scores'].items():total[k]+=v
                        total['maximum_excess']=max(total['maximum_excess'],row['scores']['excess_units'])
                    assert row['scores']['row_errors']==row['scores']['epoch_errors']==0
                    if case_count%100==0:
                        assert sum(p.stat().st_size for p in out.iterdir() if p.is_file())<500_000_000
    assert case_count==5184
    settings={'journal_mode':mode,'synchronous':conns[0].execute('PRAGMA synchronous').fetchone()[0],
              'read_uncommitted':conns[0].execute('PRAGMA read_uncommitted').fetchone()[0],
              'compile_options':[r[0] for r in conns[0].execute('PRAGMA compile_options')]}
    for c in conns:c.close()
    check=connect(db);assert check.execute('PRAGMA integrity_check').fetchall()==[('ok',)]
    for cid,expected in finals.items():assert state(check,cid,[])==expected
    logical={'quotas':[list(x) for x in check.execute('SELECT * FROM quotas ORDER BY id')],
             'allocations':[list(x) for x in check.execute('SELECT * FROM allocations ORDER BY case_id,worker')]}
    check.execute('PRAGMA wal_checkpoint(TRUNCATE)').close();check.close()
    gzwrite(out/'logical_database.json.gz',(encode(logical)+'\n').encode())
    gzwrite(out/'evidence.sqlite.gz',db.read_bytes())
    rows=[totals[k] for k in sorted(totals)]
    with (out/'summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    environment={'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'platform':platform.platform(),
                 'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.monotonic()-wall,'cases':case_count,
                 'settings':settings,'seed':None,'stochastic':False,'model_api_calls':0,
                 'integrity_check':'ok','reopened_cases_checked':len(finals),
                 'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    assert environment['cpu_seconds']<120 and environment['wall_seconds']<450
    (out/'environment.json').write_text(json.dumps(environment,indent=2)+'\n')
    print(json.dumps(environment,indent=2))
    print('MAIN RUN PASS')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    try:main(args.out)
    except Exception:
        if args.out.exists():(args.out/'failure.txt').write_text(traceback.format_exc())
        raise
