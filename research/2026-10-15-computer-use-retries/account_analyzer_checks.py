#!/usr/bin/env python3
"""Check parser edge cases and deterministic offline analysis.

These checks are by the analyzer's author. They are not a separate agent review.
Run after all evidence files exist: python3 account_analyzer_checks.py
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    source = args.input_dir.resolve()
    spec = importlib.util.spec_from_file_location('account_analyze', source/'account_analyze.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checks = []
    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
    token = 'RETRY-ACCOUNT-20261015-D01'
    text = ('Google Drive\n\t1 table Item List\n'
            '\t\t2 row (selected) '+token+' Folder Owned by me\n'
            '\t3 text '+token+' created successfully.\n'
            'The focused UI element is 2 row (selected) '+token+' Folder Owned by me')
    check('focused_row_not_counted_twice', module.rows_from_ui(text, token)[0] == 1)
    check('other_token_not_counted', module.rows_from_ui(text, 'RETRY-ACCOUNT-20261015-D02')[0] == 0)
    check('exact_receipt_matches', module.exact_receipt(text, token))
    check('other_token_receipt_does_not_match', not module.exact_receipt(text, 'RETRY-ACCOUNT-20261015-D02'))
    check('modal_only_is_unknown', module.rows_from_ui('1 heading New folder\n2 text field Value: '+token,token)[0] is None)
    check('toast_only_is_unknown', module.rows_from_ui('1 text '+token+' created successfully.',token)[0] is None)
    check('two_distinct_rows_are_two', module.rows_from_ui(text.replace('\t3 text', '\t\t9 row '+token+' Folder Size not available\n\t3 text'),token)[0] == 2)
    check('prefix_collision_not_counted', module.rows_from_ui(text.replace(token,token+'1'),token)[0] == 0)
    check('nonfolder_row_not_counted', module.rows_from_ui(text.replace(' Folder Owned',' Document Owned'),token)[0] == 0)
    check('rows_outside_item_list_not_counted', module.rows_from_ui(text.replace('table Item List','table Other'),token)[0] is None)
    check('incomplete_ui_not_empty', module.rows_from_ui('Google Drive\n1 toolbar Filters\n2 button Documents filter applied',token)[0] is None)
    check('ready_empty_view_is_zero', module.rows_from_ui('Google Drive\n1 toolbar Filters\n2 heading No matching results',token)[0] == 0)
    check('missing_filter_not_all', module.filter_text('1 table Item List') == 'not_shown')
    check('documents_filter_read', module.filter_text('1 button Documents filter applied') == 'Documents')
    check('explicit_all_filter_read', module.filter_text('1 text No filters applied') == 'All')
    check('generic_working_not_receipt', not module.exact_receipt('1 text Working…',token))
    names = ['account_results.csv','account_summary.json','account_pairs.csv']
    inputs = sorted(p for p in source.glob('account_*') if p.is_file() and p.name not in names and p.suffix in ('.py','.json','.jsonl','.csv','.md'))
    before = {p.name:digest(p) for p in inputs}
    outputs = {}
    with tempfile.TemporaryDirectory(prefix='account-repro-') as folder:
        base=Path(folder)
        for run in ('one','two'):
            out=base/run
            proc=subprocess.run([sys.executable,str(source/'account_analyze.py'),'--input-dir',str(source),'--output-dir',str(out)],text=True,capture_output=True)
            check('analysis_'+run+'_completed',proc.returncode == 0)
            outputs[run]={name:digest(out/name) for name in names if (out/name).exists()}
        check('two_replays_byte_identical', outputs['one']==outputs['two'] and len(outputs['one'])==len(names))
        check('published_outputs_match_replay', all((source/name).exists() and digest(source/name)==outputs['one'].get(name) for name in names))
    check('input_files_unchanged', before=={p.name:digest(p) for p in inputs})
    result={'status':'PASS' if all(x['passed'] for x in checks) else 'FAIL',
            'checks':checks,'count':len(checks),'replay_output_sha256':outputs,
            'review_status':'Checks by the analyzer author; separate review required.'}
    (source/'account_analyzer_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__':
    main()
