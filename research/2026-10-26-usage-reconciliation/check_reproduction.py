#!/usr/bin/env python3
"""Compare complete deterministic result files from two saved runs."""
import argparse
import hashlib
import json
from pathlib import Path

FILES = ('inputs.json', 'controls.json', 'traces.jsonl.gz', 'summary.csv',
         'paired.json', 'witnesses.json', 'checks.json')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('first',type=Path); p.add_argument('second',type=Path)
    a=p.parse_args(); result={}
    for name in FILES:
        one=(a.first/name).read_bytes(); two=(a.second/name).read_bytes()
        result[name]={'equal':one==two,'bytes':len(one),
                      'sha256':hashlib.sha256(one).hexdigest()}
    ok=all(row['equal'] for row in result.values())
    print(json.dumps({'status':'pass' if ok else 'fail','files':result},indent=2))
    if not ok: raise SystemExit(1)


if __name__=='__main__':main()
