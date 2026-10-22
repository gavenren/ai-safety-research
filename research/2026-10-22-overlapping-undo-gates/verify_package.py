#!/usr/bin/env python3
"""Check saved evidence and report tables. Does not execute the experiment."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

p = Path(__file__).resolve().parent
def read(name):
    return json.loads((p/name).read_text())
def sha(name):
    return hashlib.sha256((p/name).read_bytes()).hexdigest()

checks = []
for name, wanted in read('freeze.json')['sha256'].items():
    assert sha(name) == wanted
    checks.append('Frozen input: '+name)
initial = read('freeze_initial.json')
assert sha('plan_initial.md') == initial['sha256']['plan.md']
assert sha('study.py') == read('implementation.json')['study_sha256']
checks.append('Initial plan and implementation hash')
for name in ('execution.json','reproduction_execution.json'):
    receipt = read(name)
    assert receipt['status'] == 'complete'
    assert receipt['source_sha256'] == sha('study.py')
    assert receipt['cpu_seconds'] < 60 and receipt['wall_seconds'] < 120
    for output, wanted in receipt['output_sha256'].items():
        assert sha(output) == wanted
    checks.append('Execution and output hashes: '+name)
for name, result in read('reproduction.json')['files'].items():
    assert result['equal'] and sha(name) == result['sha256']
checks.append('All six deterministic files match both execution records')
rows = [json.loads(line) for line in (p/'raw_results.jsonl').read_text().splitlines()]
assert len(rows) == 1603
assert [r['history_id'] for r in rows] == list(range(1,1604))
assert len({tuple(r['events']) for r in rows}) == 1603
summary = read('summary.json')
for group, key in [('two_operations','primary'),('single_operation','one_operation_controls')]:
    selected = [r for r in rows if r['group']==group]
    assert len(selected) == summary[key]['histories']
    assert sum(len(r['events']) for r in selected) == summary[key]['points']
    for rule, totals in summary[key]['rules'].items():
        for metric, number in totals.items():
            assert sum(r['score'][rule][metric] for r in selected)==number
checks.append('Saved rows, unique IDs, group scores, and point totals')
report = (p/'report.md').read_text()
labels = {'boolean':'Boolean','nonnegative_count':'Nonnegative count',
          'active_ids':'Active-ID set','lifecycle_registry':'Lifecycle registry'}
for rule, label in labels.items():
    s=summary['primary']['rules'][rule]
    expected='| '+label+' | 1,596 | '+f"{s['unsafe_history']:,} | {s['overblocked_history']:,} | {s['final_closed']:,} |"
    assert expected in report
    expected='| '+label+' | '+f"{s['unsafe_points']:,} | {s['unnecessary_closed_points']:,} |"
    assert expected in report
checks.append('Every primary report table row matches measured summary')
for path in p.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
        if '://' not in target and not target.startswith('#'):
            assert (path.parent/target.split('#')[0]).exists(), (path.name,target)
checks.append('All local Markdown links resolve')
assert summary['unknown_histories']==0 and all(summary['hypotheses'].values())
checks.append('Hypothesis and unknown-result claims')
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'all_passed':True,
        'checks':checks,'scope':'Saved data and report audit; no new experimental run'}
(p/'package_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
