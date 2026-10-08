"""Download and verify the two fixed source archives. No credentials required."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--cache-dir', type=Path, default=ROOT/'.cache')
args = parser.parse_args()
args.cache_dir.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT/'source_manifest.json').read_text())
for source in manifest['archives']:
    path = args.cache_dir/source['file']
    if not path.exists():
        print('Downloading', source['file'], flush=True)
        urllib.request.urlretrieve(source['url'], path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != source['sha256']:
        raise ValueError(f'Archive hash mismatch: {source["file"]}')
    current = '20261005' in source['file']
    wanted = {'incidents.csv': 'incidents.csv' if current else 'incidents-january.csv'}
    if current:
        wanted.update({f'classifications_CSETv{v}.csv': f'classifications_CSETv{v}.csv' for v in [0, 1]})
    with tarfile.open(path, 'r|bz2') as archive:
        for member in archive:
            name = Path(member.name).name
            if member.isfile() and member.name == 'mongodump_full_snapshot/'+name and name in wanted:
                dest = args.cache_dir/wanted.pop(name)
                dest.write_bytes(archive.extractfile(member).read())
                print('Extracted', dest.name, flush=True)
                if not wanted:
                    break
    if wanted:
        raise ValueError(f'Missing source members: {wanted}')
for source in manifest['extracted_files']:
    path = args.cache_dir/source['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError(f'Extracted file hash mismatch: {path.name}')
print('All source hashes match. Run analyze.py --source-dir with this cache directory.')
