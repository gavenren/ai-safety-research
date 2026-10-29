"""Compare deterministic scientific output from two complete runs."""
import hashlib
import json
import sys
from pathlib import Path

NAMES=['checks.json','controls.json','inputs.json','paired.json','summary.csv',
       'traces.jsonl.gz','witnesses.json']
a,b=map(Path,sys.argv[1:3])
rows={}
for name in NAMES:
    x=(a/name).read_bytes();y=(b/name).read_bytes()
    rows[name]={'bytes':len(x),'sha256':hashlib.sha256(x).hexdigest(),'equal':x==y}
passed=all(v['equal'] for v in rows.values())
print(json.dumps({'passed':passed,'files':rows},indent=2))
if not passed:raise SystemExit(1)
