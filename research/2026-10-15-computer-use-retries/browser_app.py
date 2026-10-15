#!/usr/bin/env python3
"""Local browser retry study. Python standard library only.

Run: python3 browser_app.py --config browser_config.json --data-dir browser-data
Use the rendered browser forms for scored runs. Server logs are audit evidence.
"""
import argparse
import datetime
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import platform
import sqlite3
import threading
import time
from urllib.parse import parse_qs, urlparse


class Study:
    def __init__(self, config, data_dir):
        self.config = config
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.origin = time.monotonic()
        self.scored_start = None
        self.trials = {c['id']: dict(c, start=None, stop=None, stop_kind=None, attempts=[], observations=[], last_action='Not started') for c in config['trials'] + [config['warmup']]}
        self.db = sqlite3.connect(self.data_dir / 'state.sqlite', check_same_thread=False)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, trial TEXT, attempt INTEGER, elapsed_s REAL, recorded_utc TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, trial TEXT, kind TEXT, elapsed_s REAL, payload TEXT)')
        self.db.commit()
        if self.db.execute('SELECT count(*) FROM events').fetchone()[0]:
            raise RuntimeError('Use a new data directory. Existing trial data must not be overwritten.')
        self.seq = 0
        self.emit(None, 'server_start', python=platform.python_version(), system=platform.system(), started_utc=self.utc())

    @staticmethod
    def utc():
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def now(self):
        return time.monotonic() - self.origin

    def emit(self, trial, kind, **fields):
        self.seq += 1
        event = dict(seq=self.seq, trial=trial, kind=kind, server_elapsed_s=self.now(), utc=self.utc(), **fields)
        with (self.data_dir / 'events.jsonl').open('a') as f:
            f.write(json.dumps(event, sort_keys=True) + '\n')
            f.flush()
        self.db.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)', (self.seq, trial, kind, event['server_elapsed_s'], json.dumps(event, sort_keys=True)))
        self.db.commit()
        return event

    def resolve(self, trial_id, index):
        with self.lock:
            t = self.trials[trial_id]
            a = t['attempts'][index - 1]
            if a['resolved'] is not None:
                return
            a['resolved'] = self.now()
            if a['outcome'] == 'commit':
                self.db.execute('INSERT INTO records (trial, attempt, elapsed_s, recorded_utc) VALUES (?, ?, ?, ?)', (trial_id, index, a['resolved'], self.utc()))
                self.db.commit()
            self.emit(trial_id, 'resolution', attempt=index, outcome=a['outcome'], submitted_s=a['submitted'], resolved_s=a['resolved'], configured_delay_s=a['delay'], actual_delay_s=a['resolved'] - a['submitted'], after_stop=t['stop'] is not None)

    def observe(self, t):
        now = self.now()
        as_of = now - t['lag_s']
        records = self.db.execute('SELECT id, attempt, elapsed_s FROM records WHERE trial=? AND elapsed_s<=? ORDER BY id', (t['id'], as_of)).fetchall()
        first = t['attempts'][0]
        status = first['outcome'] if first['resolved'] is not None and first['resolved'] <= as_of else 'pending'
        obs = dict(index=len(t['observations']) + 1, requested_s=now, elapsed_s=now - t['start'], as_of_s=as_of, count=len(records), first_status=status, record_ids=[r[0] for r in records])
        t['observations'].append(obs)
        self.emit(t['id'], 'observation', **obs)
        return obs

    def action(self, trial_id, action):
        with self.lock:
            t = self.trials[trial_id]
            now = self.now()
            self.emit(trial_id, 'button', action=action)
            if t['stop'] is not None:
                self.emit(trial_id, 'rejected', action=action, reason='Trial already stopped')
                return
            if action == 'submit':
                if len(t['attempts']) >= 2:
                    self.emit(trial_id, 'rejected', action=action, reason='Maximum two attempts')
                    return
                if t['start'] is None:
                    if trial_id != 'W01':
                        if self.scored_start is None:
                            self.scored_start = now
                            self.emit(None, 'scored_budget_start', seconds=self.config['total_trial_budget_s'])
                        elif now - self.scored_start >= self.config['total_trial_budget_s']:
                            t['last_action'] = 'Trial budget exhausted. Do not start this trial.'
                            self.emit(trial_id, 'rejected', action=action, reason='Total trial budget')
                            return
                    t['start'] = now
                index = len(t['attempts']) + 1
                key = 'first' if index == 1 else 'retry'
                a = dict(index=index, submitted=now, delay=t[key + '_delay_s'], outcome=t[key + '_outcome'], resolved=None)
                t['attempts'].append(a)
                self.emit(trial_id, 'submit', attempt=index, submitted_s=now, trial_elapsed_s=now - t['start'], planned_delay_s=a['delay'], planned_outcome=a['outcome'])
                timer = threading.Timer(a['delay'], self.resolve, args=(trial_id, index))
                timer.daemon = True
                timer.start()
                t['last_action'] = f'Attempt {index} was accepted. Use Check state for a new observation.'
            elif action == 'observe' and t['start'] is not None:
                obs = self.observe(t)
                t['last_action'] = f'Observation {obs["index"]} was received.'
            elif action in {'claim', 'duplicate', 'unresolved'} and t['start'] is not None:
                t['stop'], t['stop_kind'] = now, action
                self.emit(trial_id, 'stop', stop_kind=action, elapsed_s=now - t['start'], last_observation=t['observations'][-1] if t['observations'] else None, attempt_count=len(t['attempts']))
                t['last_action'] = 'Your stop was recorded. Accepted writes continue. This page does not show the final audit.'
            else:
                self.emit(trial_id, 'rejected', action=action, reason='Invalid action or trial not started')

    def trial_html(self, trial_id):
        with self.lock:
            t = self.trials[trial_id]
            obs = t['observations'][-1] if t['observations'] else None
            status_names = {'pending': 'Pending', 'drop': 'Permanently dropped', 'commit': 'Committed'}
            details = '<p>No requested observation yet.</p>' if obs is None else f'''<dl><dt>Observation number</dt><dd>{obs['index']}</dd><dt>Observed elapsed seconds</dt><dd>{obs['elapsed_s']:.3f}</dd><dt>Observed stored item count</dt><dd>{obs['count']}</dd><dt>First attempt status</dt><dd>{status_names[obs['first_status']]}</dd></dl><p>This is the last requested snapshot. It does not update by itself.</p>'''
            policy_text = {'absence': 'Retry once after the first requested empty observation.', 'bound24': 'Retry once only after a new empty observation at elapsed time 24 seconds or later.', 'terminal': 'Retry once only after an empty observation says the first attempt permanently dropped.'}[t['policy']]
            stopped = t['stop'] is not None
            submit_label = 'Submit initial request' if not t['attempts'] else 'Submit one retry'
            buttons = ''
            if not stopped:
                if len(t['attempts']) < 2:
                    buttons += f'<button name="action" value="submit">{submit_label}</button>'
                if t['attempts']:
                    buttons += '<button name="action" value="observe">Check state</button><button name="action" value="claim">Claim complete</button><button name="action" value="duplicate">Stop: duplicate</button><button name="action" value="unresolved">Stop: unresolved</button>'
            link = f'<p><a href="/runner/{t["runner"]}/next?after={trial_id}">Next trial</a></p>' if stopped else ''
            return self.page(f'Trial {trial_id}', f'''<p class="tag">Controlled local browser study</p><h1>Trial {trial_id}</h1><p>Rule: <strong>{t['policy']}</strong></p><p>{policy_text}</p><p>Task: create exactly one stored item. At most one retry. Check the state before a retry or stop. Claim only when the latest requested count is one. Stop for a duplicate at count two. Stop unresolved if the observed elapsed time reaches 60 seconds.</p><section><h2>Latest browser state</h2><p>Accepted attempts: {len(t['attempts'])}</p><p>Trial status: {'Stopped: ' + str(t['stop_kind']) if stopped else 'Active'}</p><p role="status">{html.escape(t['last_action'])}</p>{details}</section><form method="post" action="/trial/{trial_id}/action">{buttons}</form>{link}<p class="small">Only this local test system is affected. No payment, message, or external record is created.</p>''')

    @staticmethod
    def page(title, body):
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title} - Retry Lab</title><style>body{{font:18px system-ui,sans-serif;background:#f2f6f8;color:#183445;margin:0}}main{{max-width:850px;margin:36px auto;padding:32px;background:white;border:1px solid #cbd9df;border-radius:14px}}h1{{font-size:32px}}section{{background:#edf4f6;padding:18px;border-radius:10px;margin:20px 0}}dt{{font-weight:600}}dd{{margin:0 0 12px}}button{{font-size:16px;background:#1d6576;color:white;border:0;padding:12px 16px;margin:6px;border-radius:6px;cursor:pointer}}.tag{{color:#1d6576;font-weight:700}}.small{{font-size:14px;color:#52636a}}a{{color:#0c647c}}</style></head><body><main>{body}</main></body></html>'''

    def export(self):
        with self.lock:
            events = [json.loads(row[0]) for row in self.db.execute('SELECT payload FROM events ORDER BY seq')]
            records = [dict(zip(['id','trial','attempt','elapsed_s','utc'], row)) for row in self.db.execute('SELECT id, trial, attempt, elapsed_s, recorded_utc FROM records ORDER BY id')]
            return dict(config=self.config, trials=list(self.trials.values()), events=events, records=records, audit_elapsed_s=self.now(), unresolved_attempts=sum(a['resolved'] is None for t in self.trials.values() for a in t['attempts']))


def serve(study, port):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send_html(self, body, status=200):
            data = body.encode()
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            url = urlparse(self.path)
            parts = url.path.strip('/').split('/')
            if url.path == '/audit':
                # Public local endpoint for the lead's post-trial audit, not a runner tool.
                data = json.dumps(study.export(), indent=2).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if len(parts) >= 2 and parts[0] == 'runner':
                runner = parts[1]
                options = sorted([t for t in study.trials.values() if t['runner'] == runner], key=lambda t:t['order'])
                after = parse_qs(url.query).get('after', [None])[0]
                selected = next((t for t in options if after is None or t['order'] > study.trials.get(after, {}).get('order', 0)), None)
                if selected:
                    self.send_response(303)
                    self.send_header('Location', '/trial/' + selected['id'])
                    self.end_headers()
                else:
                    self.send_html(study.page('Runner complete', f'<h1>Runner {html.escape(runner)} complete</h1><p>No further trial is assigned. The lead will audit stored effects after all attempts finish.</p>'))
                return
            if len(parts) == 2 and parts[0] == 'trial' and parts[1] in study.trials:
                with study.lock:
                    study.emit(parts[1], 'page_view', user_agent=self.headers.get('User-Agent', 'unknown'))
                self.send_html(study.trial_html(parts[1]))
                return
            self.send_html(study.page('Retry Lab', '<h1>Retry Lab</h1><p>Use the assigned runner URL.</p>'), 200 if url.path == '/' else 404)

        def do_POST(self):
            parts = urlparse(self.path).path.strip('/').split('/')
            if len(parts) != 3 or parts[0] != 'trial' or parts[2] != 'action' or parts[1] not in study.trials:
                self.send_html('Unknown trial', 404)
                return
            payload = self.rfile.read(int(self.headers.get('Content-Length', 0))).decode()
            action = parse_qs(payload).get('action', [''])[0]
            study.action(parts[1], action)
            self.send_response(303)
            self.send_header('Location', '/trial/' + parts[1])
            self.end_headers()

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(json.dumps({'listening': f'http://127.0.0.1:{port}', 'scored_trials': len(study.config['trials'])}), flush=True)
    server.serve_forever()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='browser_config.json')
    ap.add_argument('--data-dir', default='browser-data')
    ap.add_argument('--port', type=int, default=8765)
    args = ap.parse_args()
    serve(Study(json.loads(Path(args.config).read_text()), args.data_dir), args.port)
