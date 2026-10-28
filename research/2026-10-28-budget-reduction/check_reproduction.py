"""Compare durable scientific bytes. Run after each study process exits."""
import hashlib
import json
import sys
from pathlib import Path

NAMES=['checks.json','controls.json','engine_controls.json','final_rows.json','inputs.json',
       'ledger.sqlite','paired.json','sql.jsonl.gz','summary.csv','traces.jsonl.gz','witnesses.json']
a,b=map(Path,sys.argv[1:3])
rows={}
for name in NAMES:
    x=(a/name).read_bytes();y=(b/name).read_bytes()
    rows[name]={'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest(),'equal':x==y}
passed=all(v['equal'] for v in rows.values())
print(json.dumps({'passed':passed,'files':rows},indent=2))
if not passed:raise SystemExit(1)
