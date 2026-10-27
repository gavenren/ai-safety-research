#!/usr/bin/env python3
"""Finite counter-incarnation experiment. Standard library. No network calls."""
import argparse,copy,csv,gzip,hashlib,io,itertools,json,platform,resource,sys,time
from collections import Counter
from pathlib import Path
RULES=['GlobalMax','ArrivalDrop','SourceOrderDrop','EpochLast','EpochMax']
GROUPS={'base':['P0','T0','P1','T1'],'replay_T0':['P0','T0','T0','P1','T1'],'replay_T1':['P0','T0','P1','T1','T1']}

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def reports(values):
 return {label:{'id':label,'epoch':'E'+label[1],'value':values[('p' if label[0]=='P' else 'z')+label[1]],'final':label[0]=='T','source_order':i+1} for i,label in enumerate(['P0','T0','P1','T1'])}
def initial(rule):return {'seen':[],'arrival':[],'q':0,'last':0 if rule=='ArrivalDrop' else None,'by_epoch':{},'all_final_reports_seen':False}
def step(rule,state,label,rep):
 s=copy.deepcopy(state);duplicate=label in s['seen']
 if not duplicate:
  r=rep[label];v=r['value'];s['seen']=sorted(s['seen']+[label]);s['arrival'].append(label)
  if rule=='GlobalMax':s['q']=max(s['q'],v)
  elif rule=='ArrivalDrop':
   s['q']+=v-s['last'] if v>=s['last'] else v;s['last']=v
  elif rule=='SourceOrderDrop':
   q=0;last=0
   for k in sorted(s['seen'],key=lambda k:rep[k]['source_order']):
    value=rep[k]['value'];q+=value-last if value>=last else value;last=value
   s['q']=q
  elif rule=='EpochLast':s['by_epoch'][r['epoch']]=v;s['q']=sum(s['by_epoch'].values())
  elif rule=='EpochMax':s['by_epoch'][r['epoch']]=max(s['by_epoch'].get(r['epoch'],0),v);s['q']=sum(s['by_epoch'].values())
  else:raise ValueError(rule)
  s['all_final_reports_seen']={'T0','T1'}.issubset(s['seen'])
 return {'report_id':label,'duplicate':duplicate,'after':s}
def branch(q,z,capacity,demand,closed):
 admitted=closed and capacity-q>=demand
 actual=z+(demand if admitted else 0)
 return {'capacity':capacity,'demand':demand,'closed':closed,'admitted':admitted,'actual_use':actual,'excess':max(0,actual-capacity),'feasible_refusal':not admitted and z+demand<=capacity,'local_balance':capacity-q-(demand if admitted else 0)}
def simulate(history,rule):
 v=history['values'];rep=reports(v);z=v['z0']+v['z1'];s=initial(rule);steps=[]
 for label in history['order']:
  event=step(rule,s,label,rep);steps.append(event);s=event['after']
 decisions=[branch(s['q'],z,z+extra,b,s['all_final_reports_seen']) for extra in range(3) for b in (1,2)]
 return {'history_id':history['id'],'rule':rule,'initial':initial(rule),'steps':steps,'final_error':s['q']-z,'decisions':decisions}
def histories():
 pairs=[(p,z) for z in range(3) for p in range(z+1)];n=0
 for (p0,z0),(p1,z1) in itertools.product(pairs,repeat=2):
  for group,labels in GROUPS.items():
   for order in sorted(set(itertools.permutations(labels))):
    yield {'id':f'h{n:05d}','values':dict(p0=p0,z0=z0,p1=p1,z1=z1),'group':group,'reset_visibility':'decrease' if p1<z0 else 'no_decrease','order':list(order)}
    n+=1
def controls():
 specs=[('visible_reset',dict(p0=1,z0=2,p1=0,z1=1),['P0','T0','P1','T1']),('hidden_reset',dict(p0=1,z0=1,p1=2,z1=2),['P0','T0','P1','T1']),('late_old_progress',dict(p0=0,z0=2,p1=1,z1=2),['T0','P1','T1','P0']),('equal_values',dict(p0=1,z0=1,p1=1,z1=1),['P0','T0','P1','T1']),('zero_use',dict(p0=0,z0=0,p1=0,z1=0),['P0','T0','P1','T1']),('exact_replay',dict(p0=1,z0=2,p1=1,z1=2),['T0','P1','T0','P0','T1']),('missing_final',dict(p0=1,z0=2,p1=1,z1=2),['P0','T0','P1'])]
 return [{'history':{'id':name,'values':v,'order':order,'primary':name!='missing_final'},'results':[simulate({'id':name,'values':v,'order':order},r) for r in RULES]} for name,v,order in specs]
def empty_summary(rule,group):return {'rule':rule,'group':group,'histories':0,'exact':0,'undercount':0,'overcount':0,'max_under_units':0,'max_over_units':0,'admission_branches':0,'admitted':0,'excess_branches':0,'max_excess_units':0,'feasible_refusals':0,'local_deficit_branches':0}
def add_summary(s,t):
 e=t['final_error'];s['histories']+=1;s['exact']+=e==0;s['undercount']+=e<0;s['overcount']+=e>0;s['max_under_units']=max(s['max_under_units'],-e);s['max_over_units']=max(s['max_over_units'],e)
 for d in t['decisions']:
  s['admission_branches']+=1;s['admitted']+=d['admitted'];s['excess_branches']+=d['excess']>0;s['max_excess_units']=max(s['max_excess_units'],d['excess']);s['feasible_refusals']+=d['feasible_refusal'];s['local_deficit_branches']+=d['local_balance']<0

def run(out):
 if out.exists() and any(out.iterdir()):raise ValueError('output directory must be empty')
 out.mkdir(parents=True,exist_ok=True);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.perf_counter();cpu=time.process_time()
 worlds=list(histories());assert len(worlds)==5184 and len({x['id'] for x in worlds})==5184
 inputs={'rules':RULES,'histories':worlds,'contract':'All provider work and both final reports are complete before admission. Six independent branches per history.'}
 (out/'inputs.json').write_text(canon(inputs)+'\n')
 summaries={(r,g):empty_summary(r,g) for r in RULES for g in ['ALL','base','replay_T0','replay_T1','decrease','no_decrease']};paired={r:Counter() for r in RULES};witnesses={};counts=Counter()
 with (out/'traces.jsonl.gz').open('wb') as binary:
  with gzip.GzipFile(fileobj=binary,mode='wb',filename='',mtime=0) as gz:
   with io.TextIOWrapper(gz,encoding='utf-8',newline='\n') as stream:
    for world in worlds:
     rows=[simulate(world,r) for r in RULES];baseline=rows[-1]
     for t in rows:
      r=t['rule'];counts['rule_histories']+=1;counts['steps']+=len(t['steps']);counts['state_records']+=1+len(t['steps']);counts['admission_branches']+=len(t['decisions'])
      assert all(e['after']['q']>=0 for e in t['steps'])
      prev=t['initial']
      for event in t['steps']:
       if event['duplicate']:assert event['after']==prev;counts['duplicate_deliveries']+=1
       prev=event['after']
      assert t['steps'][-1]['after']['all_final_reports_seen']
      if r=='EpochMax':assert t['final_error']==0 and all(d['excess']==0 and not d['feasible_refusal'] for d in t['decisions'])
      if r=='SourceOrderDrop':
       v=world['values'];assert t['final_error']==(0 if v['p1']<v['z0'] else -v['z0'])
      for group in ['ALL',world['group'],world['reset_visibility']]:add_summary(summaries[r,group],t)
      for d,b in zip(t['decisions'],baseline['decisions']):
       key=('both_admit' if d['admitted'] and b['admitted'] else 'both_refuse' if not d['admitted'] and not b['admitted'] else 'only_rule_admits' if d['admitted'] else 'only_epochmax_admits');paired[r][key]+=1
      for error,condition in [('undercount',t['final_error']<0),('overcount',t['final_error']>0),('excess',any(d['excess']>0 for d in t['decisions'])),('feasible_refusal',any(d['feasible_refusal'] for d in t['decisions']))]:
       key=r+':'+error
       if condition and key not in witnesses:witnesses[key]={'history':world,'trace':t}
      stream.write(canon(t)+'\n')
     if time.perf_counter()-start>300:raise RuntimeError('wall limit')
     if sum(p.stat().st_size for p in out.iterdir())>200_000_000:raise RuntimeError('output limit')
 with (out/'summary.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(next(iter(summaries.values()))));writer.writeheader();writer.writerows(summaries.values())
 control_rows=controls();assert len(control_rows)==7
 for t in control_rows[-1]['results']:assert not t['steps'][-1]['after']['all_final_reports_seen'] and not any(d['admitted'] for d in t['decisions'])
 assert control_rows[-1]['results'][-1]['final_error']==-1
 for filename,data in [('paired.json',{r:dict(c) for r,c in paired.items()}),('controls.json',control_rows),('witnesses.json',witnesses),('checks.json',{'passed':True,'counts':dict(counts),'input_histories':len(worlds),'summary_rows':len(summaries),'control_rule_rows':35,'witnesses':len(witnesses),'source_order_formula_checked':True,'epochmax_exact_checked':True,'duplicate_no_change_checked':True,'missing_final_gate_checked':True})]:
  (out/filename).write_text(canon(data)+'\n')
 size=sum(p.stat().st_size for p in out.iterdir());assert size<=200_000_000
 env={'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),'model':'Codex generated the study; exact model build not exposed','cpu_seconds':time.process_time()-cpu,'wall_seconds':time.perf_counter()-start,'output_bytes_before_environment':size,'seed':None,'limits':{'cpu_seconds':120,'wall_seconds':300,'saved_output_bytes':200000000},'external_calls':0}
 (out/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
 print(json.dumps({'passed':True,**dict(counts),'input_histories':len(worlds),'cpu_seconds':env['cpu_seconds'],'wall_seconds':env['wall_seconds']}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
