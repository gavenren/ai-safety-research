#!/usr/bin/env python3
from pathlib import Path
import json, sys
base=Path(__file__).resolve().parent
other=Path(sys.argv[1])
names=json.loads((base/'execution.json').read_text())['output_sha256']
for name in names:
    assert (base/name).read_bytes()==(other/name).read_bytes(), name
print(f'PASS: {len(names)} deterministic files are identical.')
