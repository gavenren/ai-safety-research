"""Compare deterministic files from two complete runs."""
import argparse,json,hashlib
from pathlib import Path
FILES=['inputs.json','traces.jsonl.gz','summary.csv','paired.json','controls.json','witnesses.json','checks.json']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);a=p.parse_args();rows={}
 for f in FILES:
  x=(a.first/f).read_bytes();y=(a.second/f).read_bytes();assert x==y,f
  rows[f]={'equal':True,'sha256':hashlib.sha256(x).hexdigest(),'bytes':len(x)}
 print(json.dumps({'passed':True,'deterministic_files':rows},indent=2,sort_keys=True))
