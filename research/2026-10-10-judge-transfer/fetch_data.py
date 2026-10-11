"""Fetch the pinned public records, then retain labels and decisions only."""
import concurrent.futures
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
COMMIT = '82d39d018c5522dfbdf303b49c5d83a8444d03d2'
REPO = 'https://raw.githubusercontent.com/yibo-hu-lab/safety-flag-benchmark/'
MODELS = ['Llama-3.1-8B', 'Mistral-7B', 'OLMo-2-7B', 'Qwen2.5-7B', 'gemma-2-9b']
SETS = ['beavertails', 'xstest', 'ethics', 'wildguard', 'aegis', 'toxicchat', 'toxigen']
ALIASES = dict(zip(MODELS, ['Llama-3.1-8B-Instruct', 'Mistral-7B-Instruct-v0.3', 'OLMo-2-1124-7B-Instruct', 'Qwen2.5-7B-Instruct', 'gemma-2-9b-it']))

def path_for(model, dataset):
    if dataset in SETS[:3]:
        return f'data/results/{model}__{dataset}.jsonl'
    return f'data/results/moderation_ext/{ALIASES[model]}__{dataset}_s0.jsonl'

def fetch(pair):
    model, dataset = pair
    source_path = path_for(model, dataset)
    url = REPO + COMMIT + '/' + source_path
    # curl uses the host trust store. Certificate checks remain enabled.
    result = subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error', url], check=True, capture_output=True)
    blob = result.stdout
    rows = {}
    canonical = {}
    duplicates = 0
    for line in blob.splitlines():
        item = json.loads(line)
        ident = str(item['id'])
        encoded = json.dumps(item, sort_keys=True)
        if ident in rows:
            assert canonical[ident] == encoded, (model, dataset, ident, 'conflicting duplicate')
            duplicates += 1
            continue
        canonical[ident] = encoded
        assert item['dataset'] == dataset, (item['dataset'], dataset)
        assert item['gt'] in ['(A)', '(B)']
        assert item['solo']['answer_lp'] in ['(A)', '(B)']
        rows[ident] = (int(item['gt'] == '(A)'), int(item['solo']['answer_lp'] == '(A)'))
    return pair, rows, dict(path=source_path, url=url, sha256=hashlib.sha256(blob).hexdigest(), bytes=len(blob), unique_records=len(rows), identical_duplicates_removed=duplicates)

def main():
    pairs = [(m,d) for m in MODELS for d in SETS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        fetched = list(pool.map(fetch, pairs))
    data = {pair: rows for pair, rows, _ in fetched}
    manifest = {'repository': 'https://github.com/yibo-hu-lab/safety-flag-benchmark', 'commit': COMMIT,
                'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'license': 'CC-BY-4.0',
                'files': [entry for _, _, entry in fetched], 'selection': {}}
    with (ROOT/'data_labels.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['dataset','item_id','model','reference','prediction'])
        for dataset in SETS:
            shared = sorted(set.intersection(*(set(data[(m,dataset)]) for m in MODELS)))
            manifest['selection'][dataset] = {'common_items': len(shared), 'removed_by_model': {m: len(data[(m,dataset)])-len(shared) for m in MODELS}}
            for ident in shared:
                assert len({data[(m,dataset)][ident][0] for m in MODELS}) == 1
                for model in MODELS:
                    writer.writerow([dataset, ident, model, *data[(model,dataset)][ident]])
    manifest['minimal_data_sha256'] = hashlib.sha256((ROOT/'data_labels.csv').read_bytes()).hexdigest()
    (ROOT/'source_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest['selection'], indent=2))
    print('All 35 source cells passed schema, binary-label, duplicate consistency, and paired-label checks.')
    print('Minimal data SHA256:', manifest['minimal_data_sha256'])

if __name__ == '__main__':
    main()
