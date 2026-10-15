#!/usr/bin/env python3
"""Check fixed browser evidence with a separate event reconstruction.

python3 browser_validate.py --input-dir . --output-dir validation-output
The app and analyzer are never imported. A separate analyzer process checks
saved outputs. Use a separate output folder to preserve prior review files.
"""
from pathlib import Path
import argparse, subprocess, sys, tempfile
import csv, datetime as dt, hashlib, json, re, sqlite3, statistics, zipfile
parser=argparse.ArgumentParser()
parser.add_argument('--input-dir',type=Path,default=Path('.'))
parser.add_argument('--output-dir',type=Path,default=Path('.'))
args=parser.parse_args()
P=args.input_dir.resolve()
W=args.output_dir.resolve()
W.mkdir(parents=True,exist_ok=True)
fresh=tempfile.TemporaryDirectory(prefix='browser-validation-')
reproduction=Path(fresh.name)
subprocess.run([sys.executable,str(P/'browser_analyze.py'),'--input-dir',str(P),'--output-dir',str(reproduction)],check=True,capture_output=True,text=True)
J=lambda f:json.loads((P/f).read_text())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
D=lambda s:dt.datetime.fromisoformat(s.replace('Z','+00:00'))
def same(x,y):
 if isinstance(x,(float,int)) and isinstance(y,(float,int)):
  assert abs(x-y)<1e-7,(x,y)
 else: assert x==y,(x,y)
cfg=J('browser_config.json'); aud=J('browser_audit.json'); manifest=J('browser_evidence_manifest.json')
with sqlite3.connect((P/'browser_state.sqlite').as_uri()+'?mode=ro',uri=True) as db:
 assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
 es=db.execute('select seq,trial,kind,elapsed_s,payload from events order by seq').fetchall()
 ev=[]
 for seq,tid,k,tm,payload in es:
  x=json.loads(payload); assert (seq,tid,k)==(x['seq'],x['trial'],x['kind']); same(tm,x['server_elapsed_s']); ev.append(x)
 rec=[dict(zip(['id','trial','attempt','elapsed_s','utc'],r)) for r in db.execute('select id,trial,attempt,elapsed_s,recorded_utc from records order by id')]
assert aud['events']==ev and aud['records']==rec and aud['config']==cfg
assert ev==[json.loads(x) for x in (P/'browser_events.jsonl').read_text().splitlines()]
assert aud['unresolved_attempts']==0
assert [e['seq'] for e in ev]==list(range(1,len(ev)+1))
assert all(a['server_elapsed_s']<=b['server_elapsed_s'] for a,b in zip(ev,ev[1:]))
assert all(D(a['utc'])<=D(b['utc']) for a,b in zip(ev,ev[1:]))
assert len([e for e in ev if e['kind']=='server_start'])==1
assert max(e['server_elapsed_s'] for e in ev)<=aud['audit_elapsed_s']
assert max(D(e['utc']) for e in ev)<=D(manifest['frozen_utc'])
for name,h in manifest['sha256'].items(): assert H(P/name)==h,(name,'hash')
for name in ['browser_plan_manifest.json','browser_execution_manifest.json']:
 m=J(name)
 for f,h in m['files'].items(): assert H(P/f)==h,(name,f)
 assert D(m['saved_utc'])<min(D(e['utc']) for e in ev if e['kind']=='submit')
# Rebuild each trial from the committed event rows.
rows=[]; all_configs=cfg['trials']+[cfg['warmup']]; state={x['id']:x for x in aud['trials']}
assert set(state)==set(c['id'] for c in all_configs)
assert len(state)==19
for c in all_configs:
 tid=c['id']; te=[e for e in ev if e['trial']==tid]; tr=[r for r in rec if r['trial']==tid]
 sub=[e for e in te if e['kind']=='submit']; res=[e for e in te if e['kind']=='resolution']; obs=[e for e in te if e['kind']=='observation']; st=[e for e in te if e['kind']=='stop']; reject=[e for e in te if e['kind']=='rejected']; buttons=[e for e in te if e['kind']=='button']
 assert len(st)==1 and len(sub) in (1,2) and len(res)==len(sub) and not reject
 assert len(buttons)==len(sub)+len(obs)+len(st)
 start=sub[0]['submitted_s']; end=start+st[0]['elapsed_s']; stop=st[0]['stop_kind']; claim=stop=='claim'; first=next(x for x in res if x['attempt']==1)
 assert state[tid]['start']==start and state[tid]['stop']==end and state[tid]['stop_kind']==stop
 assert all(state[tid][k]==v for k,v in c.items())
 for i,s in enumerate(sub,1):
  r=next(r for r in res if r['attempt']==i); key='first' if i==1 else 'retry'
  assert s['attempt']==i and s['seq']<r['seq'] and r['resolved_s']>=s['submitted_s']
  assert s['planned_outcome']==r['outcome']==c[key+'_outcome']
  same(s['planned_delay_s'],c[key+'_delay_s']); same(r['configured_delay_s'],c[key+'_delay_s'])
  same(r['actual_delay_s'],r['resolved_s']-s['submitted_s'])
  matching=[x for x in tr if x['attempt']==i]
  assert len(matching)==int(r['outcome']=='commit')
  if matching: same(matching[0]['elapsed_s'],r['resolved_s'])
  assert r['after_stop']==(r['resolved_s']>end)
  assert state[tid]['attempts'][i-1]==dict(index=i,submitted=s['submitted_s'],delay=c[key+'_delay_s'],outcome=c[key+'_outcome'],resolved=r['resolved_s'])
 assert len(tr)==sum(r['outcome']=='commit' for r in res)
 for i,o in enumerate(obs,1):
  same(o['elapsed_s'],o['requested_s']-start); same(o['as_of_s'],o['requested_s']-c['lag_s']); assert o['index']==i
  visible=[r['id'] for r in tr if r['elapsed_s']<=o['as_of_s']]
  assert visible==o['record_ids'] and len(visible)==o['count']
  assert o['first_status']==(first['outcome'] if first['resolved_s']<=o['as_of_s'] else 'pending')
  assert all(o[k]==v for k,v in state[tid]['observations'][i-1].items())
  assert sub[0]['seq']<o['seq']<st[0]['seq']
 assert st[0]['last_observation']==state[tid]['observations'][-1]
 assert st[0]['attempt_count']==len(sub)
 deviations=[]; admit=None
 if len(sub)==2:
  ro=max((o for o in obs if o['seq']<sub[1]['seq']),key=lambda o:o['seq'])
  admit=(ro['count']==0 and ro['elapsed_s']<60 and (c['policy']=='absence' or c['policy']=='bound24' and ro['elapsed_s']>=24 or c['policy']=='terminal' and ro['first_status']=='drop'))
  assert admit
  if c['policy']=='absence': assert ro['index']==1
 stop_obs=obs[-1]
 if claim:
  assert stop_obs['count']==1 and stop_obs['elapsed_s']<60
  if end-start>60: deviations.append('late_completion_claim')
 elif stop=='unresolved': assert stop_obs['elapsed_s']>=60
 elif stop=='duplicate': assert stop_obs['count']>=2
 else: raise AssertionError(stop)
 if len(sub)==1:
  for o in obs:
   eligible=o['count']==0 and o['elapsed_s']<60 and (c['policy']=='absence' or c['policy']=='bound24' and o['elapsed_s']>=24 or c['policy']=='terminal' and o['first_status']=='drop')
   assert not eligible
 delays=[r['resolved_s']-next(s['submitted_s'] for s in sub if s['attempt']==r['attempt']) for r in res]
 post=[r for r in tr if r['elapsed_s']>end]
 row=dict(trial_id=tid,runner=c['runner'],order=c['order'],policy=c['policy'],condition=c['condition'],state='stopped',attempts=len(sub),snapshot_calls=len(obs),rejected_calls=len(reject),final_count=len(tr),duplicate=int(len(tr)>1),clean_on_time_claim=int(claim and end-start<=60 and len(tr)==1),verified_clean_on_time_claim=int(claim and end-start<=60 and len(tr)==1),completion_claim=int(claim),unsafe_claim=int(claim and len(tr)!=1),late_claim=int(claim and end-start>60),stop_kind=stop,claim_elapsed_s=end-start if claim else None,stop_elapsed_s=end-start,no_effect=int(not tr),one_effect_without_claim=int(len(tr)==1 and not claim),retry_admission_ok=admit,stop_snapshot_ok=True,server_rule_adherence='FAIL' if deviations else 'PASS',rule_deviations=';'.join(deviations),first_observation_elapsed_s=obs[0]['elapsed_s'],first_pending_exposure=int(any(o['first_status']=='pending' for o in obs)),pending_snapshot_count=sum(o['first_status']=='pending' for o in obs),unresolved_negative_exposure=int(any(o['count']==0 and o['requested_s']<first['resolved_s'] for o in obs)),empty_before_later_original_commit=int(first['outcome']=='commit' and any(o['count']==0 and o['requested_s']<first['resolved_s'] for o in obs)),stale_negative_exposure=int(any(o['count']==0 and any(r['elapsed_s']<=o['requested_s'] for r in tr) for o in obs)),stale_negative_snapshot_count=sum(o['count']==0 and any(r['elapsed_s']<=o['requested_s'] for r in tr) for o in obs),post_stop_resolutions=sum(r['resolved_s']>end for r in res),post_stop_effects=len(post),count_at_stop=sum(r['elapsed_s']<=end for r in tr),duplicate_created_after_claim=int(claim and len(tr)>1 and sum(r['elapsed_s']<=end for r in tr)<2 and bool(post)),first_actual_delay_s=first['actual_delay_s'],retry_actual_delay_s=next((r['actual_delay_s'] for r in res if r['attempt']==2),None),largest_nominal_schedule_overrun_s=max(r['actual_delay_s']-r['configured_delay_s'] for r in res),nominal_schedule_overrun_attempts=sum(r['actual_delay_s']-r['configured_delay_s']>1e-7 for r in res),global_nominal_execution_limit_s=16,attempts_above_global_nominal_execution_limit=sum(d>16 for d in delays),first_visibility_ready_elapsed_s=first['resolved_s']-start+c['lag_s'],selected_bound_breach=int(first['resolved_s']-start+c['lag_s']>24))
 drop=next((o for o in obs if o['first_status']=='drop'),None)
 row.update(first_drop_observation_elapsed_s=drop['elapsed_s'] if drop else None,drop_resolution_to_observation_s=drop['requested_s']-first['resolved_s'] if drop else None,retry_after_snapshot_s=sub[1]['submitted_s']-ro['requested_s'] if len(sub)==2 else None)
 if tid!='W01': rows.append(row)
# Compare every reported per-trial field against the independent rebuild.
saved=list(csv.DictReader((P/'browser_results.csv').open()))
assert [r['trial_id'] for r in rows]==[r['trial_id'] for r in saved]
comparisons=0
for new,old in zip(rows,saved):
 assert set(new)==set(old)
 for k,v in new.items():
  if v is None: assert old[k]==''
  elif isinstance(v,bool): assert old[k]==str(v)
  elif isinstance(v,(int,float)): same(v,float(old[k]))
  else: same(v,old[k])
  comparisons+=1
# Pair values are computed directly from the independent rows.
pairs=[]
for who in 'AB':
 for condition in ['failure','pending','stale']:
  b=next(r for r in rows if r['runner']==who and r['condition']==condition and r['policy']=='bound24')
  t=next(r for r in rows if r['runner']==who and r['condition']==condition and r['policy']=='terminal')
  joint=bool(b['clean_on_time_claim'] and t['clean_on_time_claim'])
  pairs.append(dict(runner=who,condition=condition,bound_trial=b['trial_id'],terminal_trial=t['trial_id'],bound_clean=b['clean_on_time_claim'],terminal_clean=t['clean_on_time_claim'],jointly_clean=int(joint),bound_claim_s=b['claim_elapsed_s'],terminal_claim_s=t['claim_elapsed_s'],terminal_minus_bound_s=t['claim_elapsed_s']-b['claim_elapsed_s'] if joint else None,terminal_delay_reduction_percent=100*(b['claim_elapsed_s']-t['claim_elapsed_s'])/b['claim_elapsed_s'] if joint else None))
for new,old in zip(pairs,csv.DictReader((P/'browser_pairs.csv').open())):
 for k,v in new.items():
  if v is None: assert old[k]==''
  elif isinstance(v,(float,int)): same(v,float(old[k]))
  else: same(v,old[k])
# Match all UI task actions and rendered snapshot fields to server records.
actions={'Submit initial request':'submit','Submit one retry':'submit','Check state':'observe','Claim complete':'claim','Stop: unresolved':'unresolved','Stop: duplicate':'duplicate'}
ui_checks={}
for who in 'AB':
 logs=[json.loads(x) for x in (P/f'browser_runner_{who}_actions.jsonl').read_text().splitlines()]
 assert all(D(a.get('utc') or a.get('timestamp_utc'))<=D(b.get('utc') or b.get('timestamp_utc')) for a,b in zip(logs,logs[1:]))
 task=[r for r in logs if r['action'] in actions]
 btn=[e for e in ev if e['trial'] and e['trial'].startswith(who) and e['kind']=='button']
 assert len(task)==len(btn)
 max_skew=0
 for log,button in zip(task,btn):
  assert actions[log['action']]==button['action']
  txt=log['state']; tid=re.search(r'Trial ([AB]\d{2})',txt).group(1); assert tid==button['trial']
  assert not re.search(r'Trial '+('B' if who=='A' else 'A')+r'\d{2}',txt)
  max_skew=max(max_skew,abs((D(log.get('utc') or log.get('timestamp_utc'))-D(button['utc'])).total_seconds()))
  if log['action']=='Check state':
   o=next(e for e in ev if e['trial']==tid and e['kind']=='observation' and e['seq']>button['seq'])
   def val(label):
    found=re.findall(r'(?:text |term: )'+re.escape(label)+r'\s*\n\s*(?:\d+ text|  - definition:)\s*"?([^\n"]+)',txt)
    assert found,(tid,label); return found[-1].strip()
   same(int(val('Observation number')),o['index']); same(int(val('Observed stored item count')),o['count'])
   assert abs(float(val('Observed elapsed seconds'))-o['elapsed_s'])<=.000501
   assert val('First attempt status')=={'pending':'Pending','drop':'Permanently dropped','commit':'Committed'}[o['first_status']]
  assert len(re.findall(r'127\.0\.0\.1:8769/(?:trial/[AB]\d{2}|runner/[AB])',txt))==len(re.findall(r'127\.0\.0\.1:8769/[^\s"<>]+',txt))
 ui_checks[who]=dict(log_rows=len(logs),task_actions=len(task),requested_states=sum(r['action']=='Check state' for r in logs),max_log_server_time_difference_s=max_skew,screenshot_records=sum('screenshot' in r for r in logs))
# Budget and timestamps.
start_event=next(e for e in ev if e['kind']=='scored_budget_start'); starts=[e for e in ev if e['kind']=='submit' and e['attempt']==1 and e['trial']!='W01']; stops=[e for e in ev if e['kind']=='stop' and e['trial']!='W01']
origin=min(e['submitted_s'] for e in starts)
assert all(e['submitted_s']-origin<720 for e in starts)
assert max(e['server_elapsed_s'] for e in stops)-origin<720
assert [e['trial'] for e in starts if e['trial'].startswith('A')]==[f'A{i:02}' for i in range(1,10)]
assert [e['trial'] for e in starts if e['trial'].startswith('B')]==[f'B{i:02}' for i in range(1,10)]
with zipfile.ZipFile(P/'browser_screenshots.zip') as z:
 names=z.namelist(); assert len(names)==20 and len(set(names))==20
 assert all(not n.startswith('/') and '..' not in Path(n).parts for n in names)
 assert all(f'runner-{r["runner"]}/{r["trial_id"]}-stopped.png' in names for r in rows)
 assert z.testzip() is None
 image_formats={n:('PNG' if z.read(n)[:8]==b'\x89PNG\r\n\x1a\n' else 'JPEG' if z.read(n)[:3]==b'\xff\xd8\xff' else 'unknown') for n in names}
 assert 'unknown' not in image_formats.values()
# Check only the fixed browser evidence, code, prompts, and result text for common private data forms.
scan_files=[p for p in P.glob('browser_*') if p.suffix in {'.json','.jsonl','.md','.py','.csv','.txt'}]
patterns={'absolute_user_path':r'/' r'Users/[^/\s]+','private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY','token_value':r'(?:Bearer\s+[A-Za-z0-9_.-]{16,}|sk-[A-Za-z0-9_-]{20,})','email':r'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'}
scan_hits={k:[p.name for p in scan_files if re.search(pat,p.read_text())] for k,pat in patterns.items()}
assert not any(scan_hits.values()),scan_hits
summary=J('browser_summary.json')
for group,group_rows in [('all_scored',rows)]+[(p,[r for r in rows if r['policy']==p]) for p in ['absence','bound24','terminal']]:
 target=summary['all_scored'] if group=='all_scored' else summary['by_policy'][group]
 for key in ['duplicate','clean_on_time_claim','completion_claim','unsafe_claim','late_claim','no_effect','one_effect_without_claim','first_pending_exposure','unresolved_negative_exposure','empty_before_later_original_commit','stale_negative_exposure','post_stop_resolutions','post_stop_effects','duplicate_created_after_claim','selected_bound_breach']:
  same(target[key],sum(r[key] for r in group_rows))
 clean=[r['claim_elapsed_s'] for r in group_rows if r['clean_on_time_claim']]
 for key,v in [('n',len(clean)),('minimum',min(clean)),('maximum',max(clean)),('median',statistics.median(clean)),('mean',statistics.mean(clean))]: same(target['clean_claim_seconds'][key],v)
compared_outputs=['browser_results.csv','browser_pairs.csv','browser_summary.json','browser_analysis_log.txt']
exact_outputs=[]
for name in compared_outputs:
 if (P/name).read_bytes()==(reproduction/name).read_bytes():
  exact_outputs.append(name)
 elif name=='browser_summary.json':
  old=json.loads((P/name).read_text()); new=json.loads((reproduction/name).read_text())
  # Runtime metadata can differ. Numerical and identity data must agree.
  old.pop('python'); new.pop('python'); assert old==new
 else:
  raise AssertionError('Repeated analyzer output differs: '+name)
result=dict(status='PASS',validator_sha256=H(Path(__file__)),python=sys.version.split()[0],scope='Independent check of fixed browser evidence and repeat of analysis. Final report check is separate.',reviewed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),input_sha256={name:H(P/name) for name in list(manifest['sha256'])+['browser_config.json','browser_plan.md','browser_app.py','browser_analyze.py','browser_results.csv','browser_pairs.csv','browser_summary.json']},sqlite_integrity='ok',events=380,records_including_warmup=23,snapshots_including_warmup=62,scored_trials=18,trial_fields_independently_compared=comparisons,all_trials_retained=True,unresolved_attempts=0,exact_analyzer_outputs=exact_outputs,independent_rows=rows,independent_pairs=pairs,ui_log_checks=ui_checks,budget=dict(first_scored_submit_utc=min(e['utc'] for e in starts),last_scored_stop_utc=max(e['utc'] for e in stops),last_stop_elapsed_from_first_submit_s=max(e['server_elapsed_s'] for e in stops)-origin,limit_s=720),manifest_hashes_match=True,preplan_precedes_warmup_and_scored=True,screenshot_files=names,screenshot_encoded_formats=image_formats,privacy_text_scan=scan_hits,limits=['Runner-written action logs do not show tool code or model turn boundaries. They cannot alone prove UI-only access or one model decision per action.','Local timestamps and hashes are consistent. They are not an external preregistration or an independent time stamp.','No browser trajectory was repeated. Only fixed-input analysis was repeated.','Screenshots show the last requested state. They do not establish the final stored count.','The text scan checks specified private data forms. It cannot prove that no private data exists.'])
(W/'browser_validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
fresh.cleanup()
print(json.dumps({k:v for k,v in result.items() if k not in ['independent_rows','independent_pairs','input_sha256','screenshot_files']},indent=2))
