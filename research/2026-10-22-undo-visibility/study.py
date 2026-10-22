#!/usr/bin/env python3
"""Run the frozen local SQLite undo-visibility experiment. Standard library only."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import sqlite3
import subprocess
import sys
import tarfile
import time
import traceback
import zlib

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / 'config.json').read_text())
GATED = {'durable_gate', 'forced_open_gate'}


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def connect(path):
    conn = sqlite3.connect(path.resolve().as_uri() + '?cache=private', uri=True,
                           timeout=5, isolation_level=None)
    conn.execute('PRAGMA busy_timeout=5000')
    conn.execute('PRAGMA read_uncommitted=0')
    conn.execute('PRAGMA synchronous=FULL')
    conn.execute('PRAGMA foreign_keys=ON')
    assert conn.execute('PRAGMA busy_timeout').fetchone()[0] == 5000
    assert conn.execute('PRAGMA read_uncommitted').fetchone()[0] == 0
    assert conn.execute('PRAGMA synchronous').fetchone()[0] == 2
    return conn


def setup(path):
    assert not path.exists(), 'A database must be fresh.'
    c = connect(path)
    assert c.execute('PRAGMA journal_mode=WAL').fetchone()[0] == 'wal'
    c.executescript((ROOT / 'schema.sql').read_text())
    c.execute('BEGIN IMMEDIATE')
    c.executemany('INSERT INTO fields VALUES (?,1)', [('x',), ('y',)])
    c.execute('INSERT INTO gate VALUES (1,0)')
    c.execute('COMMIT')
    c.close()


def snapshot(path):
    c = connect(path)
    c.execute('BEGIN IMMEDIATE')
    result = {
        'fields': dict(c.execute('SELECT name,value FROM fields ORDER BY name')),
        'receipts': [r[0] for r in c.execute('SELECT field FROM receipts ORDER BY field')],
        'gate': c.execute('SELECT closed FROM gate WHERE singleton=1').fetchone()[0],
        'decisions': [dict(zip(('job', 'phase', 'predicate', 'observed_x', 'observed_y', 'decision'), r))
                      for r in c.execute('SELECT * FROM decisions ORDER BY job')],
        'actions': [r[0] for r in c.execute('SELECT job FROM actions ORDER BY job')],
    }
    c.execute('COMMIT')
    c.close()
    return result


def predicate(p, x, y):
    return (p >> (2*x+y)) & 1


def serial_sequences(predicates):
    result = []
    for k in range(len(predicates)+1):
        row = [predicate(p, *(CONFIG['pre'] if i < k else CONFIG['post']))
               for i, p in enumerate(predicates)]
        if row not in result:
            result.append(row)
    return result


def score(attempts):
    accepted = [r for r in attempts if r['status'] == 'accepted']
    ps = [r['predicate'] for r in accepted]
    bits = [r['decision'] for r in accepted]
    allowed = serial_sequences(ps)
    checks = [b in (predicate(p, 1, 1), predicate(p, 0, 0)) for p, b in zip(ps, bits)]
    violation = bits not in allowed
    return {'accepted_sequence': bits, 'allowed_sequences': allowed,
            'local_endpoint_checks': checks, 'serial_violation': violation,
            'joint_only_violation': violation and all(checks),
            'local_endpoint_failure': not all(checks), 'action_vector': bits}


def set_gate(path, closed):
    c = connect(path)
    c.execute('BEGIN IMMEDIATE')
    c.execute('UPDATE gate SET closed=? WHERE singleton=1', (closed,))
    c.execute('COMMIT')
    c.close()


def reader(path, rule, job, p, phase, commit=True):
    c = connect(path)
    c.execute('BEGIN IMMEDIATE')
    row = {'job': job, 'phase': phase, 'predicate': p, 'status': 'refused',
           'observed_x': None, 'observed_y': None, 'decision': None}
    closed = c.execute('SELECT closed FROM gate WHERE singleton=1').fetchone()[0] if rule in GATED else 0
    if not closed:
        values = dict(c.execute('SELECT name,value FROM fields ORDER BY name'))
        bit = predicate(p, values['x'], values['y'])
        c.execute('INSERT INTO decisions VALUES (?,?,?,?,?,?)',
                  (job, phase, p, values['x'], values['y'], bit))
        if bit:
            c.execute('INSERT INTO actions VALUES (?)', (job,))
        row.update(status='accepted', observed_x=values['x'], observed_y=values['y'], decision=bit)
    c.execute('COMMIT' if commit else 'ROLLBACK')
    c.close()
    return row


def worker(path, rule, order, mode):
    c = connect(path)
    if c.execute('PRAGMA journal_mode').fetchone()[0] != 'wal':
        raise RuntimeError('The worker did not find WAL mode.')

    def phase(name, committed=None):
        print(stable({'phase': name, 'rule': rule, 'order': order,
                      'mode': mode, 'committed': committed}), flush=True)

    def apply(field):
        if not c.execute('SELECT 1 FROM receipts WHERE field=?', (field,)).fetchone():
            c.execute('UPDATE fields SET value=value-1 WHERE name=?', (field,))
            c.execute('INSERT INTO receipts VALUES (?)', (field,))

    if rule in GATED:
        c.execute('BEGIN IMMEDIATE')
        c.execute('UPDATE gate SET closed=1 WHERE singleton=1')
        c.execute('COMMIT')
    if rule == 'whole_transaction':
        c.execute('BEGIN IMMEDIATE')
        if mode == 'exit_before':
            phase('before_first_update', False)
            os._exit(CONFIG['worker_exit_code'])
        for i, field in enumerate(order):
            apply(field)
            if i == 0 and mode == 'interrupted':
                phase('after_first_step', False)
                os._exit(CONFIG['worker_exit_code'])
        c.execute('COMMIT')
    else:
        for i, field in enumerate(order):
            c.execute('BEGIN IMMEDIATE')
            if i == 0 and mode == 'exit_before':
                phase('before_first_update', False)
                os._exit(CONFIG['worker_exit_code'])
            apply(field)
            c.execute('COMMIT')
            if i == 0 and mode == 'interrupted':
                phase('after_first_step', True)
                os._exit(CONFIG['worker_exit_code'])
    if rule in GATED:
        c.execute('BEGIN IMMEDIATE')
        values = dict(c.execute('SELECT name,value FROM fields'))
        receipts = {r[0] for r in c.execute('SELECT field FROM receipts')}
        if values != {'x': 0, 'y': 0} or receipts != {'x', 'y'}:
            raise RuntimeError('The gate cannot open before completion.')
        c.execute('UPDATE gate SET closed=0 WHERE singleton=1')
        c.execute('COMMIT')
    c.close()
    phase('completed', True)


def cases():
    case_id = 0
    for group, rules in [('primary', CONFIG['primary_rules']), ('sensitivity', CONFIG['sensitivity_rules'])]:
        for rule, order, f, g in itertools.product(rules, CONFIG['orders'], CONFIG['predicates'], CONFIG['predicates']):
            case_id += 1
            yield dict(case_id=case_id, group=group, rule=rule, order=order, f=f, g=g, cut=None)
    for cut, f, g in itertools.product(CONFIG['serial_control_cuts'], CONFIG['predicates'], CONFIG['predicates']):
        case_id += 1
        yield dict(case_id=case_id, group='serial_control', rule='whole_transaction', order='xy', f=f, g=g, cut=cut)


def complete(tables):
    return tables['fields'] == {'x': 0, 'y': 0} and tables['receipts'] == ['x', 'y'] and tables['gate'] == 0


class Experiment:
    def __init__(self, out, dbdir):
        self.out, self.dbdir = out, dbdir
        if out.exists() or dbdir.exists():
            raise RuntimeError('Output and database directories must not already exist.')
        out.mkdir(parents=True)
        dbdir.mkdir(parents=True)
        self.start_wall = time.monotonic()
        self.start_cpu = self.cpu()
        self.started = dt.datetime.now(dt.timezone.utc).isoformat()
        self.rows = []
        self.calls = 0
        self.worker_log = (out/'worker_logs.jsonl').open('w')
        self.case_log = (out/'cases.jsonl').open('w')
        self.dump_log = (out/'database_dumps.jsonl').open('w')
        self.hashes = {name: sha(ROOT/name) for name in ['study.py', 'schema.sql', 'config.json', 'plan.md']}
        write_json(out/'implementation_receipt.json', {'saved_before_trials': True, 'utc': self.started, 'sha256': self.hashes})
        write_json(out/'environment.json', {
            'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version,
            'zlib_compile': zlib.ZLIB_VERSION, 'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION,
            'platform': platform.system(), 'platform_release': platform.release(), 'machine': platform.machine(),
            'cpu_count': os.cpu_count(), 'cpu_limit_seconds': CONFIG['cpu_limit_seconds'],
            'wall_limit_seconds': CONFIG['wall_limit_seconds'],
            'seed': None, 'external_packages': [],
        })

    @staticmethod
    def cpu():
        a = resource.getrusage(resource.RUSAGE_SELF)
        b = resource.getrusage(resource.RUSAGE_CHILDREN)
        return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime

    def usage(self):
        return {'cpu_seconds': self.cpu()-self.start_cpu,
                'wall_seconds': time.monotonic()-self.start_wall,
                'worker_calls': self.calls, 'scored_rows_saved': len(self.rows)}

    def budget(self):
        u = self.usage()
        if u['cpu_seconds'] >= CONFIG['cpu_limit_seconds'] or u['wall_seconds'] >= CONFIG['wall_limit_seconds']:
            raise RuntimeError('The resource gate was reached.')

    def launch(self, path, rule, order, mode, label):
        self.budget()
        start = time.monotonic()
        before = self.cpu()
        self.calls += 1
        p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker', str(path.resolve()), rule, order, mode],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = p.communicate(timeout=min(30, CONFIG['wall_limit_seconds'] - self.usage()['wall_seconds']))
        except subprocess.TimeoutExpired:
            p.kill()
            stdout, stderr = p.communicate()
            self.save_worker(label, mode, p, stdout, stderr, start, before, 'timeout')
            raise RuntimeError('A worker timed out.')
        self.save_worker(label, mode, p, stdout, stderr, start, before, None)
        expected = CONFIG['worker_exit_code'] if mode in ('interrupted', 'exit_before') else 0
        if p.returncode != expected or stderr or not stdout.strip():
            raise RuntimeError(f'Unexpected worker result: status {p.returncode}, expected {expected}.')
        phases = [json.loads(line) for line in stdout.splitlines()]
        phase_name = {'interrupted': 'after_first_step', 'exit_before': 'before_first_update', 'recovery': 'completed', 'complete': 'completed'}[mode]
        if len(phases) != 1 or phases[0]['phase'] != phase_name:
            raise RuntimeError('The worker phase log is incomplete.')
        return p.returncode, phases[0]

    def save_worker(self, label, mode, process, stdout, stderr, start, before, error):
        stderr = stderr.replace(str(ROOT), '<study>').replace(str(self.dbdir.resolve()), '<databases>')
        row = {'label': label, 'mode': mode, 'pid': process.pid, 'returncode': process.returncode,
               'stdout': stdout, 'stderr': stderr, 'elapsed_seconds': time.monotonic()-start,
               'cumulative_cpu_increment_seconds': self.cpu()-before, 'error': error}
        self.worker_log.write(stable(row)+'\n')
        self.worker_log.flush()

    def save_database(self, path, tables):
        c = connect(path)
        c.execute('BEGIN IMMEDIATE')
        integrity = [r[0] for r in c.execute('PRAGMA integrity_check')]
        sql = '\n'.join(c.iterdump())+'\n'
        c.execute('COMMIT')
        checkpoint = list(c.execute('PRAGMA wal_checkpoint(TRUNCATE)'))
        c.close()
        if integrity != ['ok'] or checkpoint != [(0, 0, 0)]:
            raise RuntimeError('Database integrity or checkpoint check failed.')
        self.dump_log.write(stable({'database': path.name, 'tables': tables, 'sql_dump': sql})+'\n')
        self.dump_log.flush()
        return 'ok'

    def hands(self):
        records = []
        def check(name, observed, expected):
            row = {'name': name, 'observed': observed, 'expected': expected, 'passed': observed == expected}
            records.append(row)
            write_json(self.out/'hand_controls.json', records)
            if not row['passed']:
                raise RuntimeError('A hand control failed: '+name)
        states = list(itertools.product((0, 1), repeat=2))
        for name, p, expected in [('x',12,[0,0,1,1]), ('y',10,[0,1,0,1]), ('zero',0,[0,0,0,0]),
                                  ('one',15,[1,1,1,1]), ('xor',6,[0,1,1,0]), ('equality',9,[1,0,0,1])]:
            check('truth_'+name, [predicate(p, *s) for s in states], expected)
        check('three_serial_cuts_xy', serial_sequences([12,10]), [[0,0],[1,0],[1,1]])
        witness = [{'status':'accepted', 'predicate':p, 'decision':predicate(p,0,1)} for p in (12,10)]
        check('joint_only_witness', score(witness)['joint_only_violation'], True)
        check('outside_endpoints', score([{'status':'accepted','predicate':6,'decision':1}])['local_endpoint_failure'], True)
        check('empty_sequence', score([])['serial_violation'], False)
        path = self.dbdir/'hand-reader-rollback.sqlite3'
        setup(path)
        attempted = reader(path, 'separate', 0, 15, 'primary', commit=False)
        snap = snapshot(path)
        check('rolled_back_reader', [attempted['decision'],snap['decisions'],snap['actions']], [1,[],[]])
        self.save_database(path, snap)
        for rule, order in itertools.product(CONFIG['primary_rules']+CONFIG['sensitivity_rules'], CONFIG['orders']):
            self.budget()
            path = self.dbdir/f'hand-before-{rule}-{order}.sqlite3'
            setup(path)
            status, phase = self.launch(path, rule, order, 'exit_before', path.stem)
            snap = snapshot(path)
            check(path.stem, {'fields':snap['fields'], 'receipts':snap['receipts'], 'gate':snap['gate'], 'status':status},
                  {'fields':{'x':1,'y':1}, 'receipts':[], 'gate':int(rule in GATED), 'status':73})
            self.save_database(path, snap)

    def trial(self, spec):
        row = dict(spec)
        row.update(valid=False, unknown_reason=None)
        path = self.dbdir/f"trial-{spec['case_id']:04d}.sqlite3"
        rule, order = spec['rule'], spec['order']
        try:
            self.budget()
            setup(path)
            attempts = []
            row.update(expected_exit_status=None, exit_status=None, recovery_status=None, worker_phase=None,
                       audit=None, post_intervention_audit=None, exact_cut_expected=None, exact_cut_match=None)
            if spec['group'] == 'serial_control':
                row['audit'] = snapshot(path)
                for i in range(3):
                    if i == spec['cut']:
                        row['recovery_status'], row['worker_phase'] = self.launch(path, rule, order, 'complete', path.stem)
                    if i < 2:
                        attempts.append(reader(path, rule, i, (spec['f'],spec['g'])[i], 'primary'))
                expected = [predicate(p, *(CONFIG['pre'] if i < spec['cut'] else CONFIG['post']))
                            for i,p in enumerate((spec['f'],spec['g']))]
                row['exact_cut_expected'] = expected
                row['exact_cut_match'] = [a['decision'] for a in attempts] == expected
            else:
                row['expected_exit_status'] = 73
                row['exit_status'], row['worker_phase'] = self.launch(path, rule, order, 'interrupted', path.stem)
                row['audit'] = snapshot(path)
                if rule == 'forced_open_gate':
                    set_gate(path, 0)
                    row['post_intervention_audit'] = snapshot(path)
                attempts = [reader(path, rule, i, p, 'primary') for i,p in enumerate((spec['f'],spec['g']))]
                row['recovery_status'], row['recovery_phase'] = self.launch(path, rule, order, 'recovery', path.stem)
            row['reader_attempts'] = attempts
            row.update(score(attempts))
            row['final'] = snapshot(path)
            row['source_complete'] = complete(row['final'])
            row['probes'] = [reader(path, rule, i+2, p, 'probe') for i,p in enumerate((spec['f'],spec['g']))]
            row['probe_success'] = all(a['status']=='accepted' and [a['observed_x'],a['observed_y']]==[0,0]
                                       and a['decision']==predicate(a['predicate'],0,0) for a in row['probes'])
            row['final_with_probes'] = snapshot(path)
            row['integrity'] = self.save_database(path, row['final_with_probes'])
            row['valid'] = True
        except Exception as exc:
            row['unknown_reason'] = f'{type(exc).__name__}: {exc}'
            row['integrity'] = row.get('integrity', 'unknown')
            self.record(row)
            raise
        self.record(row)

    def record(self, row):
        self.rows.append(row)
        self.case_log.write(stable(row)+'\n')
        self.case_log.flush()
        if len(self.rows)%128 == 0 or not row['valid']:
            progress = dict(self.usage(), utc=dt.datetime.now(dt.timezone.utc).isoformat(), last_case_id=row['case_id'])
            write_json(self.out/'progress.json', progress)
            print(stable(progress), flush=True)

    def summary(self):
        result = []
        keys = list(dict.fromkeys((r['group'],r['rule']) for r in self.rows))
        for group, rule in keys:
            rows = [r for r in self.rows if (r['group'],r['rule'])==(group,rule)]
            valid = [r for r in rows if r['valid']]
            item = {'group':group,'rule':rule,'assigned':len(rows),'valid':len(valid),'unknown':len(rows)-len(valid)}
            for key in ['source_complete','serial_violation','joint_only_violation','local_endpoint_failure','probe_success']:
                item[key] = sum(r[key] for r in valid)
            item['accepted_primary_jobs'] = sum(a['status']=='accepted' for r in valid for a in r['reader_attempts'])
            item['refused_primary_jobs'] = sum(a['status']=='refused' for r in valid for a in r['reader_attempts'])
            item['exact_cut_matches'] = sum(r['exact_cut_match'] is True for r in valid)
            result.append(item)
        write_json(self.out/'summary.json', result)
        if result:
            with (self.out/'summary.csv').open('w',newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(result[0]))
                writer.writeheader()
                writer.writerows(result)
        witnesses = {}
        for key in ['serial_violation','joint_only_violation','local_endpoint_failure']:
            matches = [r for r in self.rows if r['valid'] and r[key]]
            witnesses[key] = matches[0] if matches else None
        named = [r for r in self.rows if r['group']=='primary' and r['rule']=='separate'
                 and r['order']=='xy' and r['f']==12 and r['g']==10]
        witnesses['predeclared_xy'] = named[0] if named else None
        write_json(self.out/'witnesses.json', witnesses)

    def archive(self):
        with (self.out/'physical_databases.tar.gz').open('wb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed:
                with tarfile.open(mode='w|',fileobj=compressed) as archive:
                    for path in sorted(self.dbdir.glob('*.sqlite3')):
                        info = archive.gettarinfo(str(path),arcname=path.name)
                        info.uid=info.gid=0
                        info.uname=info.gname=''
                        info.mtime=0
                        info.mode=0o600
                        with path.open('rb') as data:
                            archive.addfile(info,data)

    def run(self):
        status='failed'
        error=None
        try:
            self.hands()
            for spec in cases():
                self.trial(spec)
            self.budget()
            status='completed'
        except Exception as exc:
            error = {'type':type(exc).__name__,'message':str(exc),'source_sha256':self.hashes}
            write_json(self.out/'failure.json',error)
        finally:
            self.summary()
            self.worker_log.close()
            self.case_log.close()
            self.dump_log.close()
            self.archive()
            receipt = {'status':status,'error':error,'started_utc':self.started,
                       'finished_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
                       'usage':self.usage(),'source_sha256':self.hashes,
                       'databases_retained':len(list(self.dbdir.glob('*.sqlite3')))}
            write_json(self.out/'execution_receipt.json',receipt)
            deterministic = ['cases.jsonl','database_dumps.jsonl','summary.json','summary.csv','witnesses.json','hand_controls.json']
            write_json(self.out/'logical_sha256.json',{name:sha(self.out/name) for name in deterministic if (self.out/name).exists()})
            print(stable(receipt),flush=True)
        if status != 'completed':
            raise SystemExit(1)


def main():
    if len(sys.argv)>1 and sys.argv[1]=='--worker':
        worker(Path(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5])
        return
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--db-dir',type=Path,required=True)
    args=parser.parse_args()
    Experiment(args.out,args.db_dir).run()


if __name__=='__main__':
    main()
