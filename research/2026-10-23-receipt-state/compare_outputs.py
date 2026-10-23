#!/usr/bin/env python3
"""Compare deterministic saved and repeated research outputs."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
groups = [
    ('results', 'reproduced', ['cases.jsonl', 'results.jsonl', 'summary.csv',
                             'paired_differences.csv', 'examples.json', 'checks.json']),
    ('independent_verified', 'independent_reproduced',
     ['rows.jsonl', 'summary.json', 'paired_examples.json']),
]
record = {}
for saved, repeated, names in groups:
    for name in names:
        source = (root/saved/name).read_bytes()
        replica = (root/repeated/name).read_bytes()
        if source != replica:
            raise AssertionError(f'Output differs: {saved}/{name}')
        record[f'{saved}/{name}'] = {'match': True,
                                    'sha256': hashlib.sha256(source).hexdigest()}
print(json.dumps({'status': 'pass', 'deterministic_files': record}, indent=2))
