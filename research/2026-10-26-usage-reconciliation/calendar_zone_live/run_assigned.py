from pathlib import Path
import json,sys,datetime,shutil
root=Path('outputs/2026-10-26-usage-reconciliation/calendar_zone_live');work=Path('work/2026-10-26-calendar-zone-live')
sys.path.insert(0,str(root.resolve()))
from evaluate import evaluate
cases=json.loads((root/'cases.json').read_text());obs={x['record_alias']:x for x in json.loads((root/'observations.json').read_text())};zones={x['alias']:x for x in json.loads((work/'zone_observations.json').read_text())}
shutil.copyfile(work/'zone_observations.json',root/'zone_observations.json')
for phase in ['assigned','complete']:
 rows=[]
 for case in cases:
  r=evaluate(case,obs[case['alias']],zones[case['alias']],phase)
  r['evaluated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();rows.append(r)
 (root/f'{phase}_results.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps({'phase':phase,'decisions':[{'alias':r['alias'],**r['result']} for r in rows]},indent=2))
