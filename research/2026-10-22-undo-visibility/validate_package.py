#!/usr/bin/env python3
"""Check frozen hashes, result tables, witness, links, and basic release hygiene."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def main():
    checks = []

    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})

    for name, digest in read('freeze.json')['files'].items():
        check('frozen/' + name, hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest)
    for name, digest in read('results/implementation_receipt.json')['sha256'].items():
        check('implementation/' + name, hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest)
    for name, digest in read('results/logical_sha256.json').items():
        check('logical/' + name, hashlib.sha256((ROOT / 'results' / name).read_bytes()).hexdigest() == digest)
    report = (ROOT / 'report.md').read_text()
    summary = read('results/summary.json')
    labels = ['Separate', 'Durable gate', 'Whole transaction', 'Forced open gate', 'Serial boundary controls']
    columns = ['assigned', 'source_complete', 'accepted_primary_jobs', 'refused_primary_jobs',
               'serial_violation', 'local_endpoint_failure', 'joint_only_violation']
    for label, row in zip(labels, summary):
        expected = '| ' + label + ' | ' + ' | '.join(f'{row[c]:,}' for c in columns) + ' |'
        check('report_table/' + label, expected in report)
    check('total_cases', sum(r['assigned'] for r in summary) == 2816)
    check('no_unknowns', all(r['unknown'] == 0 and r['valid'] == r['assigned'] for r in summary))
    witness = read('results/witnesses.json')['predeclared_xy']
    check('witness203', witness['case_id'] == 203 and witness['accepted_sequence'] == [0, 1]
          and witness['joint_only_violation'] and witness['source_complete'])
    check('no_pending_report', not re.search(r'PENDING|TODO|TBD', report))
    check('ai_disclosure', 'Codex generated this study and report.' in report)
    check('no_human_review_disclosure', 'No human review or external peer review occurred.' in report)
    check('run_complete', read('results/execution_receipt.json')['status'] == 'completed')
    review = read('independent_checks/independent_comparison.json')
    check('independent_check', review['match'] and review['physical_databases_reopened'] == 2825
          and review['worker_logs_checked'] == 4872 and not review['differences'])
    broken = []
    inspected = 0
    private_hits = []
    patterns = [r'/Users/[^/\s]+/', r'/home/[^/\s]+/', r'gh[pousr]_[A-Za-z0-9]{25,}',
                r'github_pat_[A-Za-z0-9_]{25,}', r'-----BEGIN [A-Z ]*PRIVATE KEY-----']
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        check('file_size/' + str(path.relative_to(ROOT)), path.stat().st_size < 25_000_000)
        if path.suffix in ('.md', '.json', '.jsonl', '.csv', '.bib', '.sql', '.py'):
            text = path.read_text()
            inspected += 1
            if path.name != Path(__file__).name:
                for pattern in patterns:
                    if re.search(pattern, text):
                        private_hits.append(str(path.relative_to(ROOT)))
            if path.suffix == '.md':
                for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                    if re.match(r'https?://|#|mailto:', link):
                        continue
                    target = link.split('#')[0]
                    if target and not (path.parent / target).exists():
                        broken.append({'file': str(path.relative_to(ROOT)), 'target': target})
    check('relative_links', not broken)
    check('basic_private_data_patterns', not private_hits)
    result = {'passed': all(c['passed'] for c in checks), 'checks': checks,
              'text_files_inspected': inspected, 'broken_relative_links': broken,
              'private_pattern_hits': sorted(set(private_hits)),
              'limits': 'Local checks only. External references and claim support require the source and content reviews. Pattern checks do not prove absence of secrets.'}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
