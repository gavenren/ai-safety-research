"""Compare the seven deterministic study outputs without running experiments."""
import hashlib
import json
import pathlib
import sys

NAMES = (
    'inputs.json', 'controls.json', 'traces.jsonl.gz', 'summary.csv',
    'logical_database.json.gz', 'paired_metadata.json', 'minimum_breaches.json',
)

def compare(left, right):
    result = {}
    for name in NAMES:
        a, b = (left / name).read_bytes(), (right / name).read_bytes()
        result[name] = {'match': a == b, 'sha256': hashlib.sha256(a).hexdigest()}
    print(json.dumps(result, indent=2))
    if not all(item['match'] for item in result.values()):
        raise SystemExit('Deterministic output mismatch')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: check_reproduction.py FIRST_DIR SECOND_DIR')
    compare(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
