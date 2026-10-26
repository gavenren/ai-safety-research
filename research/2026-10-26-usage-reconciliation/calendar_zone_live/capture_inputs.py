from pathlib import Path
import json,hashlib,sys,datetime
root=Path('outputs/2026-10-26-usage-reconciliation/calendar_zone_live');work=Path('work/2026-10-26-calendar-zone-live')
sys.path.insert(0,str(root.resolve()))
from evaluate import evaluate
cases=json.loads((root/'cases.json').read_text());rows=[];observations=[]
for case in cases:
 alias=case['alias'];path=work/'private'/f'read-{alias}.json';raw=json.loads(path.read_text());s=raw['result']['structuredContent']
 fields={k:s[k] for k in (*[k for k in case['payload'] if k!='timezone'],'status') if k in s}
 obs=dict(record_alias=alias,observed_at=raw['ended_utc'],evidence_sha256=[hashlib.sha256(path.read_bytes()).hexdigest()],fields=fields,timezone_label_returned=any('zone' in k.lower() for k in s))
 observations.append(obs)
 result=evaluate(case,obs,None,'connector_only');result['evaluated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();rows.append(result)
(root/'observations.json').write_text(json.dumps(observations,indent=2)+'\n')
(root/'connector_only_results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{'alias':x['alias'],'result':x['result'],'field_only_baseline_accepts':x['field_only_baseline_accepts']} for x in rows],indent=2))
