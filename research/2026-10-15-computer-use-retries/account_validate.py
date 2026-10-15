#!/usr/bin/env python3
"""Independent review of the 30 Drive trials. Uses Python standard library only.

This code does not import the author analyzer. It reads full observations,
applies the published label corrections, and checks every scored transition.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


def stamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def phase(record):
    return record.get('label', record.get('phase', record.get('action', '')))


def count_rows(state, token):
    """Read rows inside Item List. Never count the focus echo or a toast."""
    in_table = False
    depth = None
    rows = []
    for line in state.splitlines():
        indent = len(line) - len(line.lstrip('\t'))
        if re.search(r'^\t*\d+ table Item List$', line):
            in_table, depth = True, indent
            continue
        if in_table and line.strip() and indent <= depth:
            in_table = False
        if in_table and re.match(r'^\t*\d+ row(?: \([^)]*\))? ' + re.escape(token) + r' Folder(?: |$)', line):
            rows.append(line)
    usable = bool(re.search(r'^\t*\d+ table Item List$', state, re.M)) or any(
        x in state for x in ['heading No matching results', 'container empty-view-content-folder'])
    return len(rows) if usable else None


def view(state):
    if 'button Documents filter applied' in state:
        return 'Documents'
    if re.search(r'^\t*\d+ text No filters applied$', state, re.M):
        return 'All'
    return 'unknown'


def exact_receipt(state, token):
    return bool(re.search(r'^\t*\d+ text ' + re.escape(token) + r' created successfully\.$', state, re.M))


def run(base):
    tests, problems, warnings = [], [], []
    def check(label, passed):
        tests.append({'check': label, 'pass': bool(passed)})
        if not passed:
            problems.append(label)

    sample='RETRY-ACCOUNT-20261015-D01'
    table='\t1 table Item List\n\t\t2 row (selected) '+sample+' Folder Owned by me\n'
    check('parser: selected row counted once', count_rows(table+'The focused UI element is 2 row (selected) '+sample+' Folder',sample)==1)
    check('parser: two rows are two', count_rows(table+'\t\t3 row '+sample+' Folder Owned by me\n',sample)==2)
    check('parser: other token not counted', count_rows(table,sample+'x')==0)
    check('parser: prefix is not exact name', count_rows(table.replace(sample,sample+'x'),sample)==0)
    check('parser: out-of-table row not counted', count_rows('\t1 table Item List\n2 row '+sample+' Folder',sample)==0)
    check('parser: loading screen is unknown', count_rows('1 button Documents filter applied',sample) is None)
    check('parser: modal input is unknown', count_rows('1 text field Value: '+sample,sample) is None)
    check('parser: explicit empty result is zero', count_rows('1 heading No matching results',sample)==0)
    check('parser: explicit empty folder is zero', count_rows('1 container empty-view-content-folder',sample)==0)
    check('parser: exact receipt accepted', exact_receipt('1 text '+sample+' created successfully.',sample))
    check('parser: generic receipt rejected', not exact_receipt('1 text Folder created successfully.',sample))
    check('parser: absent toolbar is unknown', view(table)=='unknown')

    assignments = list(csv.DictReader((base/'account_assignments.csv').open()))
    manifest = json.loads((base/'account_plan_manifest.json').read_text())
    for name, expected in manifest['files'].items():
        check('saved plan hash: '+name, hashlib.sha256((base/name).read_bytes()).hexdigest() == expected)
    check('30 distinct planned trial IDs', len(assignments) == len({a['trial_id'] for a in assignments}) == 30)
    check('30 distinct planned names', len({a['token'] for a in assignments}) == 30)
    grouped = defaultdict(list)
    all_raw = {}
    for runner in 'AB':
        raw = [json.loads(line) for line in (base/f'account_runner_{runner}_actions.jsonl').read_text().splitlines()]
        all_raw[runner] = raw
        correction = json.loads((base/'account_runner_B_corrections.json').read_text()) if runner == 'B' else []
        if runner == 'A':
            notes = [r for r in raw if r.get('type') == 'metadata_correction']
            check('A has explicit D01 correction', len(notes) == 1 and notes[0].get('trial_id') == 'D01')
        for n, record in enumerate(raw, 1):
            trial = record.get('trial_id')
            if runner == 'A' and trial == 'setup' and 2 <= n <= 14:
                trial = 'D01'
            if runner == 'B':
                for c in correction:
                    if c['line_start'] <= n <= c['line_end']:
                        check(f'B line {n} original label matches correction', trial in c['source_trial_id'])
                        if record.get('before_utc'):
                            check(f'B line {n} inside correction time range', stamp(c['before_utc_min']) <= stamp(record['before_utc']) <= stamp(record['after_utc']) <= stamp(c['after_utc_max']))
                        trial = c['target_trial_id']
            if record.get('before_utc') and record.get('after_utc'):
                check(f'{runner} line {n} time order', stamp(record['before_utc']) <= stamp(record['after_utc']))
            grouped[trial].append((n, record))

    audit = json.loads((base/'account_connector_audit.json').read_text())
    connector = defaultdict(list)
    for block in audit['blocks']:
        check(f"block {block['block']} count matches", block['returned_count'] == len(block['records']))
        check(f"block {block['block']} below capacity", block['returned_count'] < audit['requested_top_k_per_block'])
        for r in block['records']:
            connector[r['name']].append((block['block'], r))
    all_ids = [r['id'] for block in audit['blocks'] for r in block['records']]
    check('connector has 30 distinct IDs', len(all_ids) == len(set(all_ids)) == 30)
    check('connector names equal planned names', set(connector) == {a['token'] for a in assignments})

    results = []
    for a in assignments:
        tid, token = a['trial_id'], a['token']
        seq = grouped[tid]
        observations = [(n, r) for n, r in seq if r.get('type') == 'observation']
        creates = [(n, r) for n, r in seq if r.get('type') == 'action' and phase(r) in ['initial_create', 'create_initial', 'retry_create', 'create_retry']]
        decisions = [r for _, r in seq if r.get('type') == 'decision']
        check(tid+' one initial Create', len(creates) == 1)
        check(tid+' one decision', len(decisions) == 1)
        first = [r for _, r in observations if phase(r) == 'first_decision']
        check(tid+' one first decision observation', len(first) == 1)
        if not creates or not decisions or not first:
            continue
        create = creates[0][1]
        decision = decisions[0]
        f = first[0]
        start, stop = stamp(create['before_utc']), stamp(decision['decision_utc'])
        check(tid+' plan saved before initial Create', stamp(manifest['saved_utc']) < start)
        secs = (stop-start).total_seconds()
        check(tid+' decision within deadline', 0 <= secs <= 120)
        check(tid+' decision follows full observation', stamp(f['after_utc']) <= stop)
        check(tid+' first observation after Create', stamp(f['before_utc']) >= stamp(create['after_utc']))
        check(tid+' connector audit after decision', stamp(audit['audit_utc']) > stop)
        check(tid+' confirmed row agrees with count', decision['decision'] == 'confirmed' and count_rows(f['state'], token) == 1)
        check(tid+' exported first count matches raw row', decision['first_count'] == count_rows(f['state'], token))
        check(tid+' no retry claimed', decision['retries'] == len(creates)-1 == 0)
        if a['rule'] == 'receipt':
            check(tid+' exact-token receipt present', exact_receipt(f['state'], token))

        # The initial label can be a loading state. Use the last usable pre-write
        # page observation, including the New menu, without using post-write data.
        prior = [(n,r) for n,r in observations if stamp(r['after_utc']) < start and count_rows(r['state'],token) is not None]
        selected = [(n,r) for n,r in prior if view(r['state']) == a['view']]
        baseline = selected[-1] if selected else None
        baseline_count = count_rows(baseline[1]['state'],token) if baseline else None
        if baseline is None:
            warnings.append({'trial_id':tid,'issue':'No usable pre-Create list or empty state in the assigned view. Baseline count remains unknown.'})
        else:
            check(tid+' verified baseline has zero token rows', baseline_count == 0)
        pres = [r for _,r in observations if phase(r) == 'audit_pre_reload']
        posts = [r for _,r in observations if phase(r) in ['audit_post_reload_ready','audit_reload_ready','audit_reload_ready_after_error']]
        check(tid+' one pre-reload audit', len(pres) == 1)
        check(tid+' one ready post-reload audit', len(posts) == 1)
        pre = count_rows(pres[-1]['state'], token) if pres else None
        post = count_rows(posts[-1]['state'], token) if posts else None
        check(tid+' pre-reload has one row', pre == 1)
        check(tid+' ready post-reload has one row', post == 1)
        records = connector[token]
        ccount = len({r['id'] for _,r in records})
        check(tid+' connector has one folder in assigned block', ccount == 1 and all(b == int(a['block']) and r['mime_type'] == 'application/vnd.google-apps.folder' for b,r in records))
        check(tid+' connector confirms private record', all(r.get('shared') is False for _,r in records))
        check(tid+' connector creation time follows click and precedes decision', all(start <= stamp(r['created_time']) <= stop for _,r in records))
        # New-name evidence in immediate/first states ties a corrected label to
        # the actual UI. A stale metadata token cannot supply this evidence.
        check(tid+' actual token visible after Create', token in f['state'])
        inter = [r for _,r in seq if r.get('type') == 'action' and start <= stamp(r['before_utc']) <= stop]
        check(tid+' no unplanned action after Create before decision', len(inter) == 1 and phase(inter[0]) in ['initial_create','create_initial'])
        results.append({'trial_id':tid,'rule':a['rule'],'assigned_view':a['view'],'block':int(a['block']),'runner':a['runner'],
                        'baseline_count':baseline_count,'baseline_source_line':baseline[0] if baseline else None,
                        'first_count':count_rows(f['state'],token),'first_explicit_view':view(f['state']),
                        'first_exact_receipt':exact_receipt(f['state'],token),'decision_seconds':round(secs,3),
                        'initial_submit_utc':create['before_utc'],'decision_utc':decision['decision_utc'],
                        'pre_reload_count':pre,'post_reload_count':post,'connector_count':ccount,
                        'retries':len(creates)-1,'clean':decision['decision']=='confirmed' and 0<=secs<=120 and ccount==1})
    for runner in 'AB':
        chosen = [r for r in results if r['runner'] == runner]
        if chosen:
            elapsed = (max(stamp(r['initial_submit_utc']) for r in chosen)-min(stamp(r['initial_submit_utc']) for r in chosen)).total_seconds()
            check(runner+' admission within 30 minutes', elapsed <= 1800)
    summary = {'trials':len(results),'clean':sum(r['clean'] for r in results),'retries':sum(r['retries'] for r in results),
               'duplicates':sum(r['connector_count']>=2 for r in results),'zero':sum(r['connector_count']==0 for r in results),
               'unverified_baselines':[r['trial_id'] for r in results if r['baseline_count'] is None],
               'first_explicit_view_counts':dict(Counter(r['first_explicit_view'] for r in results)),
               'all_core_controls':sum(r['clean'] and r['retries']==0 for r in results if r['assigned_view']=='All' and r['rule']!='receipt'),
               'receipt_controls_with_both_row_and_receipt':sum(r['first_count']==1 and r['first_exact_receipt'] for r in results if r['rule']=='receipt'),
               'decision_seconds_min':min(r['decision_seconds'] for r in results),'decision_seconds_max':max(r['decision_seconds'] for r in results)}
    # Compare to the author outputs only after the independent derivation.
    author_csv = {r['trial_id']:r for r in csv.DictReader((base/'account_results.csv').open())}
    check('author table has same trial IDs', set(author_csv) == {r['trial_id'] for r in results})
    for r in results:
        a = author_csv[r['trial_id']]
        for own, other in [('first_count','first_row_count'),('pre_reload_count','pre_reload_count'),('post_reload_count','post_reload_count'),('connector_count','connector_count'),('retries','retries')]:
            check(r['trial_id']+' author agrees: '+own, r[own] == int(a[other]))
        check(r['trial_id']+' author agrees: baseline', ('' if r['baseline_count'] is None else str(r['baseline_count'])) == a['baseline_row_count'])
        check(r['trial_id']+' author agrees: seconds', r['decision_seconds'] == float(a['decision_seconds']))
        check(r['trial_id']+' author agrees: first explicit view', ('not_shown' if r['first_explicit_view']=='unknown' else r['first_explicit_view']) == a['first_visible_filter'])
        check(r['trial_id']+' author agrees: clean outcome', str(r['clean']) == a['clean_confirmation'])
        check(r['trial_id']+' author agrees: receipt', str(r['first_exact_receipt']) == a['first_exact_receipt'])
        for field in ['initial_submit_utc','decision_utc']:
            check(r['trial_id']+' author agrees: '+field, r[field] == a[field])
    author_summary=json.loads((base/'account_summary.json').read_text())
    for field in ['clean','retries','duplicates','zero']:
        check('author summary agrees: '+field, summary[field] == author_summary['total'][field])
    check('author summary agrees: baselines', summary['unverified_baselines'] == author_summary['unverified_assigned_baselines'])
    pairs=list(csv.DictReader((base/'account_pairs.csv').open()))
    check('24 core pair comparisons', len(pairs)==24)
    by_id={r['trial_id']:r for r in results}
    expected_pairs=set()
    for block in range(1,5):
        for assigned in ['All','Documents']:
            for ra,rb in [('absence','wait24'),('absence','scope'),('wait24','scope')]:
                expected_pairs.add((block,assigned,ra,rb))
    check('pair design matches all planned comparisons', {(int(p['block']),p['view'],p['rule_a'],p['rule_b']) for p in pairs}==expected_pairs)
    for number,pair in enumerate(pairs,1):
        a,b=by_id[pair['trial_a']],by_id[pair['trial_b']]
        check(f'pair {number} identities and stratum', a['block']==b['block']==int(pair['block']) and a['assigned_view']==b['assigned_view']==pair['view'] and a['rule']==pair['rule_a'] and b['rule']==pair['rule_b'])
        check(f'pair {number} clean difference', int(pair['clean_b_minus_a'])==int(b['clean'])-int(a['clean']))
        check(f'pair {number} duplicate difference', int(pair['duplicate_b_minus_a'])==int(b['connector_count']>=2)-int(a['connector_count']>=2))
        check(f'pair {number} wall-time difference', float(pair['seconds_b_minus_a'])==round(b['decision_seconds']-a['decision_seconds'],3))
    check('author hypothesis interpretation is bounded', author_summary['hypotheses'] == {
        'H-A1_directional_criterion_met':False,'H-A2_directional_criterion_met':False,'H-A3_criterion_met':True,
        'stable_hidden_view_established':False,'interpretation':author_summary['hypotheses']['interpretation']})
    inputs = ['account_assignments.csv','account_runner_A_actions.jsonl','account_runner_B_actions.jsonl','account_runner_B_corrections.json','account_connector_audit.json']
    inputs += ['account_plan.md','account_plan_manifest.json','account_results.csv','account_summary.json','account_pairs.csv']
    return {'review_kind':'Independent agent evidence check; no human review. Not a population reliability estimate.',
            'checks':len(tests),'passed':sum(t['pass'] for t in tests),'failed':len(problems),'problems':problems,'warnings':warnings,
            'summary':summary,'results':results,'tests':tests,
            'input_sha256':{name:hashlib.sha256((base/name).read_bytes()).hexdigest() for name in inputs}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--fresh-copy',action='store_true',help='Run the author analyzer twice in separate temporary copies and compare its saved outputs.')
    args=parser.parse_args()
    out=run(args.base)
    if args.fresh_copy:
        repeat=[]
        for iteration in [1,2]:
            with tempfile.TemporaryDirectory(prefix='account-review-') as temp:
                target=Path(temp)
                for f in args.base.glob('account*'):
                    if f.is_file() and f.suffix in ['.json','.jsonl','.csv','.md','.py']:
                        shutil.copyfile(f,target/f.name)
                proc=subprocess.run([sys.executable,str(target/'account_analyze.py'),'--input-dir',str(target),'--output-dir',str(target)],capture_output=True,text=True)
                same={name:(target/name).read_bytes()==(args.base/name).read_bytes() for name in ['account_results.csv','account_summary.json','account_pairs.csv'] if (target/name).exists()}
                passed=proc.returncode==0 and len(same)==3 and all(same.values())
                repeat.append({'iteration':iteration,'exit_code':proc.returncode,'saved_output_byte_agreement':same,'pass':passed})
                out['checks']+=1
                out['passed']+=int(passed)
                out['failed']+=int(not passed)
                if not passed:out['problems'].append('Fresh analyzer replay '+str(iteration))
        out['fresh_copy_reproduction']=repeat
    (args.output or args.base/'account_validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['checks','passed','failed','warnings','summary']},indent=2))
    raise SystemExit(1 if out['failed'] else 0)


if __name__=='__main__':
    main()
