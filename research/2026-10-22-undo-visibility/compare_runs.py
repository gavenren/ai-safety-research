#!/usr/bin/env python3
"""Compare saved logical experiment outputs; this does not execute a trial."""
import argparse
import hashlib
import json
from pathlib import Path

NAMES = ('cases.jsonl', 'database_dumps.jsonl', 'summary.json', 'summary.csv',
         'witnesses.json', 'hand_controls.json')


def compare(first, second):
    rows = []
    for name in NAMES:
        a = hashlib.sha256((first / name).read_bytes()).hexdigest()
        b = hashlib.sha256((second / name).read_bytes()).hexdigest()
        rows.append({'file': name, 'first_sha256': a, 'second_sha256': b, 'match': a == b})
    return {'match': all(r['match'] for r in rows), 'files': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--first', type=Path, required=True)
    p.add_argument('--second', type=Path, required=True)
    args = p.parse_args()
    result = compare(args.first, args.second)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result['match'] else 1)
