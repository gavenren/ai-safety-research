"""Deterministic finite-state study. Python standard library only."""
import csv
import gzip
import hashlib
import itertools
import json
import platform
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = 'case_id suite d1 outcome1 d2 outcome2 lag schedule policy server_mode retry_tick stop_tick stop_reason declared observed_count_at_stop effects_at_stop final_effects audit_tick duplicate clean_confirmed unsafe_completion detected_duplicate deadline_stop no_claim zero_effect one_effect_unconfirmed submit_calls query_calls capped_clean_time'.split()
MEASURES = 'duplicate clean_confirmed unsafe_completion detected_duplicate deadline_stop no_claim zero_effect one_effect_unconfirmed submit_calls query_calls capped_clean_time'.split()

def write_csv(name, rows, fields=None):
    with (ROOT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def cases(config):
    suites = {'main': {'attempt_delays': config['attempt_delays'], 'read_lags': config['read_lags']}, **config['stress_suites']}
    for suite, grid in suites.items():
        for i, (d1, o1, d2, o2, lag) in enumerate(itertools.product(grid['attempt_delays'], config['outcomes'], grid['attempt_delays'], config['outcomes'], grid['read_lags'])):
            yield dict(case_id=f'{suite}-{i:03}', suite=suite, d1=d1, outcome1=o1, d2=d2, outcome2=o2, lag=lag)

def run(case, schedule, ticks, policy, mode, cfg):
    # The controller uses only snapshot(), the schedule, and declared bounds.
    events = [dict(tick=0, event='submit', attempt=1)]
    pending = [dict(attempt=1, launch=0, due=case['d1'], outcome=case['outcome1'])]
    commits = []
    resolved = set()
    retry_tick = None
    stop = None
    declared = 0
    reads = 0
    stop_count = 0
    effects_stop = None

    def count_at(t):
        n = sum(x <= t for x in commits)
        return min(n, 1) if mode == 'deduplicate' else n

    def snapshot(t):
        asof = max(0, t - case['lag'])
        status = case['outcome1'] if case['d1'] <= asof else 'pending'
        return asof, count_at(asof), status

    end = cfg['deadline'] + max(case['d1'], case['d2'])
    for t in range(1, end + 1):
        # Settle all due writes before reading at the same time.
        for a in pending:
            if a['due'] == t and a['attempt'] not in resolved:
                resolved.add(a['attempt'])
                if a['outcome'] == 'commit':
                    commits.append(t)
                events.append(dict(tick=t, event='resolve', attempt=a['attempt'], outcome=a['outcome'], effects=count_at(t)))
        if stop is None and t in ticks:
            reads += 1
            asof, n, state1 = snapshot(t)
            events.append(dict(tick=t, event='query', as_of=asof, observed_count=n, first_attempt_state=state1))
            stop_count = n
            if n:
                stop = t
                declared = int(n == 1)
                reason = 'confirmed' if declared else 'detected_duplicate'
            else:
                trigger = (policy == 'absence_retry' or
                           policy == 'timeout8' and t >= cfg['execution_bound'] or
                           policy == 'bound12' and t >= cfg['execution_bound'] + cfg['lag_bound'] or
                           policy == 'terminal_retry' and state1 == 'drop')
                if retry_tick is None and trigger:
                    retry_tick = t
                    pending.append(dict(attempt=2, launch=t, due=t + case['d2'], outcome=case['outcome2']))
                    events.append(dict(tick=t, event='submit', attempt=2))
                if t == cfg['deadline']:
                    stop = t
                    reason = 'deadline'
            if stop is not None:
                effects_stop = count_at(t)
                events.append(dict(tick=t, event='stop', reason=reason, declared=declared, effects=effects_stop))
        if stop is not None and len(resolved) == len(pending):
            break
    assert stop is not None and len(resolved) == len(pending)
    final = count_at(t)
    clean = int(declared and final == 1)
    row = dict(case, schedule=schedule, policy=policy, server_mode=mode,
               retry_tick='' if retry_tick is None else retry_tick, stop_tick=stop,
               stop_reason=reason, declared=declared, observed_count_at_stop=stop_count,
               effects_at_stop=effects_stop, final_effects=final,
               audit_tick=max(stop, max(a['due'] for a in pending)),
               duplicate=int(final > 1), clean_confirmed=clean,
               unsafe_completion=int(declared and final != 1),
               detected_duplicate=int(reason == 'detected_duplicate'),
               deadline_stop=int(reason == 'deadline'), no_claim=int(not declared),
               zero_effect=int(final == 0), one_effect_unconfirmed=int(final == 1 and not declared),
               submit_calls=len(pending), query_calls=reads,
               capped_clean_time=stop if clean else cfg['deadline'])
    events.append(dict(tick=row['audit_tick'], event='final_audit', final_effects=final))
    return row, events

def aggregate(rows, keys):
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in keys)].append(r)
    result = []
    for key, rs in sorted(groups.items()):
        g = dict(zip(keys, key), runs=len(rs))
        for measure in MEASURES:
            total = sum(r[measure] for r in rs)
            g[measure + '_sum'] = total
            g[measure + '_mean'] = f'{total / len(rs):.9f}'
        clean = [r for r in rs if r['clean_confirmed']]
        g['clean_time_sum'] = sum(r['stop_tick'] for r in clean)
        g['clean_time_mean'] = f"{g['clean_time_sum'] / len(clean):.9f}" if clean else ''
        result.append(g)
    return result

def main():
    cfg = json.loads((ROOT / 'config.json').read_text())
    manifest = json.loads((ROOT / 'input_manifest.json').read_text())
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    worlds = list(cases(cfg))
    write_csv('cases.csv', worlds)
    rows, examples = [], []
    with (ROOT / 'traces.jsonl.gz').open('wb') as f:
        with gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0) as z:
            for case in worlds:
                for schedule, ticks in cfg['schedules'].items():
                    for policy in cfg['policies']:
                        for mode in cfg['server_modes']:
                            row, trace = run(case, schedule, ticks, policy, mode, cfg)
                            rows.append(row)
                            record = {'run': row, 'events': trace}
                            z.write((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
                            if (case['suite'] == 'main' and case['lag'] == 0 and case['d1'] == 8 and case['outcome1'] == 'commit' and case['d2'] == 1 and case['outcome2'] == 'commit' and schedule == 'every1' and mode == 'append'):
                                examples.append(record)
    write_csv('results_runs.csv', rows, FIELDS)
    summary = aggregate(rows, ['suite', 'server_mode', 'schedule', 'policy'])
    write_csv('results_summary.csv', summary)
    write_csv('results_by_outcome.csv', aggregate(rows, ['suite', 'server_mode', 'schedule', 'policy', 'outcome1']))
    write_csv('results_by_lag.csv', aggregate(rows, ['suite', 'server_mode', 'schedule', 'policy', 'lag']))
    paired = []
    for suite in ['main', *cfg['stress_suites']]:
        for schedule in cfg['schedules']:
            a = {r['case_id']: r for r in rows if r['suite'] == suite and r['schedule'] == schedule and r['server_mode'] == 'append' and r['policy'] == 'terminal_retry'}
            for baseline in ['bound12', 'no_retry', 'absence_retry', 'timeout8']:
                b = {r['case_id']: r for r in rows if r['suite'] == suite and r['schedule'] == schedule and r['server_mode'] == 'append' and r['policy'] == baseline}
                common = [k for k in a if a[k]['clean_confirmed'] and b[k]['clean_confirmed']]
                delta = sum(a[k]['stop_tick'] - b[k]['stop_tick'] for k in common)
                paired.append(dict(suite=suite, schedule=schedule, comparison='terminal_retry minus ' + baseline, cases=len(a), jointly_clean=len(common), clean_gain=sum(a[k]['clean_confirmed'] - b[k]['clean_confirmed'] for k in a), duplicate_delta=sum(a[k]['duplicate'] - b[k]['duplicate'] for k in a), paired_time_delta_sum=delta, paired_time_delta_mean=f'{delta / len(common):.9f}' if common else ''))
    write_csv('results_paired.csv', paired)
    (ROOT / 'trace_examples.json').write_text(json.dumps(examples, indent=2) + '\n')
    h = {'main_cases': sum(c['suite'] == 'main' for c in worlds), 'all_cases': len(worlds), 'all_runs': len(rows), 'main_runs': sum(r['suite'] == 'main' for r in rows), 'summary_rows': len(summary)}
    main_append = [r for r in rows if r['suite'] == 'main' and r['server_mode'] == 'append']
    h['H1_fresh_absence_duplicates_by_schedule'] = {s: sum(r['duplicate'] for r in main_append if r['policy'] == 'absence_retry' and r['lag'] == 0 and r['schedule'] == s) for s in cfg['schedules']}
    h['H2_terminal_and_bound_duplicates'] = {p: sum(r['duplicate'] for r in main_append if r['policy'] == p) for p in ['terminal_retry', 'bound12']}
    h['H2_paired_main'] = [x for x in paired if x['suite'] == 'main' and x['comparison'] == 'terminal_retry minus bound12']
    h['H3_absence_duplicates'] = {s: sum(r['duplicate'] for r in main_append if r['policy'] == 'absence_retry' and r['schedule'] == s) for s in cfg['schedules']}
    h['H4_stress_duplicates'] = {suite: {p: sum(r['duplicate'] for r in rows if r['suite'] == suite and r['server_mode'] == 'append' and r['policy'] == p) for p in cfg['policies']} for suite in cfg['stress_suites']}
    h['deduplication_duplicates_all_suites'] = sum(r['duplicate'] for r in rows if r['server_mode'] == 'deduplicate')
    (ROOT / 'hypothesis_checks.json').write_text(json.dumps(h, indent=2) + '\n')
    (ROOT / 'environment.json').write_text(json.dumps({'python': platform.python_version(), 'implementation': platform.python_implementation(), 'system': platform.system(), 'dependencies': 'Python standard library', 'random_sampling': False, 'model_experiments': False, 'timing_unit': 'synthetic integer tick'}, indent=2) + '\n')
    print(json.dumps(h, indent=2))

if __name__ == '__main__':
    main()
