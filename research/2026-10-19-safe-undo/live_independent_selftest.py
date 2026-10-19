import argparse,copy,importlib.util,json,hashlib
from pathlib import Path
p=Path(__file__).with_name('live_independent_audit.py');sp=importlib.util.spec_from_file_location('audit',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path('.'));ap.add_argument('--trials',type=Path,default=Path('live_trials.jsonl'));ap.add_argument('--output',type=Path,default=Path('live_independent_self_checks.json'));args=ap.parse_args()
package=args.package;f=m.stamp(json.loads((package/'live_input_manifest.json').read_text())['frozen_at_utc']);assignments=json.loads((package/'live_assignments.json').read_text());r=next(x for x in m.read_rows(args.trials) if x['trial_id']=='notion-01');a=next(x for x in assignments if x['trial_id']=='notion-01');m.audit_one(a,r,f)
identity_key='native_id' if 'native_id' in r else 'record_alias'
bad=[('baseline omitted',lambda q:q.pop('baseline')),('baseline mismatch',lambda q:q['baseline'].update(x=1,x_raw='1')),('raw Empty',lambda q:q['agent'].update(x_raw='Empty')),('wrong command',lambda q:q['later'][0].update(command='add1')),('boolean integer',lambda q:q['agent'].update(x=True)),('identity mismatch',lambda q:q['preundo'].update({identity_key:'wrong'})),('not reloaded',lambda q:q['final'].update(reloaded=False)),('bad Y',lambda q:q['final'].update(y=2)),('backward time',lambda q:q['final'].update(utc='2020-01-01T00:00:00Z')),('missing decision evidence',lambda q:q.pop('decision_evidence_id')),('invalid status',lambda q:q['decision'].update(status='success')),('marker mismatch',lambda q:q['final'].update(token='wrong')),('before freeze',lambda q:q.update(started_at='2020-01-01T00:00:00Z')),('checkbox parse mismatch',lambda q:q['final']['y_raw'].update(checked=True)),('spaces in integer',lambda q:q['final'].update(x_raw=' 0'))]
checked=[]
for name,change in bad:
 q=copy.deepcopy(r);change(q)
 try:m.audit_one(a,q,f)
 except (ValueError,KeyError,TypeError):checked.append(name)
 else:raise AssertionError('Accepted malformed record '+name)
q=copy.deepcopy(r);q['final'].update(x=1,x_raw='1');z=m.audit_one(a,q,f);assert z['outcome']=='clean_completion' and not z['final_matches_decision']
q=copy.deepcopy(r);q.update(terminal_status='unknown',reason='fixture uncertainty');q.pop('final');z=m.audit_one(a,q,f);assert z['outcome']=='not_scored'
result={'status':'PASS','rule_controls':m.self_test(),'malformed_records_rejected':checked,'observed_final_not_forced_to_decision':True,'unknown_not_scored':True,'audit_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'fixture':'notion-01 recorded row, retained unchanged; only copies were changed'}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
