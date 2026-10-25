"""Compare deterministic outputs without repeating the experiment."""
import hashlib
import json
from pathlib import Path
import sys

FILES = ('controls.json','inputs.json','traces.jsonl.gz','summary.csv',
         'paired.json','witnesses.json','checks.json')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: check_reproduction.py FIRST_DIR SECOND_DIR')
    left,right=map(Path,sys.argv[1:])
    result={}
    for name in FILES:
        a,b=(left/name).read_bytes(),(right/name).read_bytes()
        result[name]={'match':a==b,'sha256':hashlib.sha256(a).hexdigest()}
    print(json.dumps(result,indent=2))
    if not all(row['match'] for row in result.values()):
        raise SystemExit('Deterministic output mismatch')
