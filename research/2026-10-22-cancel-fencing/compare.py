#!/usr/bin/env python3
"""Compare deterministic evidence; does not run the study."""
import argparse, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
names=['raw_results.jsonl','summary.csv','summary.json','controls.json','checks.json','witnesses.json']
rows=[]
for name in names:
    b=(a.baseline/name).read_bytes();c=(a.candidate/name).read_bytes()
    assert b==c,name
    rows.append({'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'equal':True})
manifest=a.baseline/'reproduction.json'
if manifest.exists():
    assert rows == json.loads(manifest.read_text())['files'], 'Saved reproduction hashes differ'
print(json.dumps({'all_equal':True,'files':rows},indent=2))
