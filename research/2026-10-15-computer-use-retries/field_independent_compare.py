#!/usr/bin/env python3
"""Compare the completed, separately derived result to the main result table."""
import argparse
import csv
import json
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('--independent',type=Path,required=True)
ap.add_argument('--main',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
args=ap.parse_args()
ind=json.loads(args.independent.read_text())
main={r['trial_id']:r for r in csv.DictReader(args.main.open())}
tested=0
issues=[]
for r in ind['trials']:
    expected={
        'service':r['service'],'condition':r['condition'],
        'initial':r['phases']['initial']['status'],'final':r['phases']['final']['status'],
        'audit':r['phases']['audit']['status'],'initial_baseline':r['phases']['initial']['baseline'],
        'injection_exposed':r['initial_injection_exposed'],'wrong_detected':r['detected_injected_error'],
        'baseline_false_match':r['initial_baseline_false_match'],
        'create_calls':r['creates'],'repair_calls':r['repairs'],
        'initial_visible_rows':r['phases']['initial']['rendered_rows'],
        'initial_distinct_records':r['phases']['initial']['count'],
        'same_identity':r['same_identity'],'audit_records':r['phases']['audit']['count'],
        'extra_records':r['extra_record_case'],'claimed':r['decision']=='CONFIRM',
        'proved_false_claim':r['false_confirmation'],'clean_claim':r['confirmed_clean'],
        'unknown_claim':r['unknown_confirmation'],'elapsed_seconds':r['elapsed_seconds'],
        'late':not r['on_time'],
        'cleanup_zero':r['cleanup_browser_zero'] and r['cleanup_connector_zero'] is not False,
        'repair_success':r['repairs']==1 and r['same_identity'] and r['final_full_match']
                         and r['phases']['final']['count']==1,
    }
    row=main.get(r['trial_id'],{})
    for key,want in expected.items():
        tested+=1
        raw=row.get(key)
        if isinstance(want,bool):
            got={'True':True,'False':False,'true':True,'false':False}.get(raw)
        elif type(want) is int:
            got=int(raw) if raw is not None else None
        elif type(want) is float:
            got=float(raw) if raw is not None else None
        else:
            got=raw
        equal=(abs(got-want)<0.0011 if type(want) is float and type(got) is float else got==want)
        if not equal:
            issues.append(dict(trial_id=r['trial_id'],field=key,main=got,independent=want))
out=dict(status='PASS' if not issues else 'FAIL',trials=len(ind['trials']),compared_fields=tested,
         mismatches=issues,missing_from_independent=sorted(set(main)-{r['trial_id'] for r in ind['trials']}))
args.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
