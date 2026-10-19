"""Local controls; none is a live website trial."""
import copy,json,hashlib
from pathlib import Path
from improved_independent_model import prepare,finish,replay,grade


def obs(x,y,n):return {'x':x,'y':y,'identity':'local-fixture','contract':True,'reloaded':True,'readId':'read-'+str(n),'readAt':'2026-10-19T15:44:'+str(n).zfill(2)+'Z'}
def input_for(full,presented,complete):
    current,_=replay({'x':1,'y':0},full)
    return {'initial':{'x':0,'y':0},'agent':{'x':1,'y':0},'current':obs(**current,n=1),'later':presented,'historyComplete':complete,'expectedIdentity':'local-fixture'}

cases=[('control',[],[],True,None),('independent_y',['flip_y'],['flip_y'],True,None),('addition',['add1'],['add1'],True,None),('assignment_return',['set0','set1'],['set0','set1'],True,None),('incomplete_history',['set0','set1'],[],False,None),('prestate_mismatch',['add1'],[],True,None),('wrong_x_save',[],[],True,'x_plus_two'),('wrong_y_save',[],[],True,'flip_y')]
expected={'baseline_log_provenance':['clean_completion']*4+['false_confirmation','clean_completion','false_confirmation','false_confirmation'],'checked_history':['clean_completion']*4+['abstain_correct','unresolved','unresolved','unresolved']}
checks=[]
for rule in expected:
 for i,(name,full,presented,complete,fault) in enumerate(cases):
  data=input_for(full,presented,complete);d=prepare(rule,data);actual=d['write'] or {'x':data['current']['x'],'y':data['current']['y']}
  actual=copy.deepcopy(actual)
  if fault=='x_plus_two':actual['x']+=2
  if fault=='flip_y':actual['y']=1-actual['y']
  reads=[obs(**actual,n=2),obs(**actual,n=3)];f=finish(rule,d,reads);target,_=replay(data['initial'],full)
  assert grade(f['status'],reads,target)==expected[rule][i];checks.append(rule+'/'+name)
base=input_for([],[],True);decision=prepare('checked_history',base);good=[obs(0,0,2),obs(0,0,3)]
mutations=[('duplicate ID',lambda r:r[1].update(readId=r[0]['readId'])),('pre-read reuse',lambda r:r[0].update(readId='read-1')),('not reloaded',lambda r:r[0].update(reloaded=False)),('equal read times',lambda r:r[1].update(readAt=r[0]['readAt'])),('read before prepare',lambda r:r[0].update(readAt='2026-10-19T15:44:00Z')),('bad time',lambda r:r[1].update(readAt='bad')),('wrong identity',lambda r:r[1].update(identity='other')),('bad contract',lambda r:r[0].update(contract=False))]
for name,change in mutations:
 r=copy.deepcopy(good);change(r);assert finish('checked_history',decision,r)['status']=='unknown';checks.append(name)
assert finish('checked_history',decision,good[:1])['status']=='unknown';checks.append('missing second read')
for index in (0,1):
 r=copy.deepcopy(good);r[index]['x']=2;assert finish('checked_history',decision,r)['status']=='abstain';assert grade('complete',r,{'x':0,'y':0})=='false_confirmation';checks.append('wrong final read '+str(index))
# The complete-log assumption can fail without a current-field mismatch.
data=input_for(['set0','set1'],[],True);d=prepare('checked_history',data);r=[obs(0,0,2),obs(0,0,3)];f=finish('checked_history',d,r);truth,_=replay(data['initial'],['set0','set1']);assert f['status']=='complete' and grade(f['status'],r,truth)=='false_confirmation';checks.append('dishonest-log counterexample')
assert grade('unknown',[],{'x':0,'y':0})=='unknown';assert grade('complete',[],{'x':0,'y':0})=='unsupported_complete';checks.extend(['unknown is not scored','missing evidence is not complete proof'])
result={'status':'PASS','local_controls':len(checks),'checks':checks,'dishonest_log_limit_confirmed':True,'scored_website_trials':0,'model_sha256':hashlib.sha256(Path(__file__).with_name('improved_independent_model.py').read_bytes()).hexdigest(),'reviewer_saw_controller_for_design_review':True,'primary_analyzer_read_during_model_implementation':False}
Path(__file__).with_name('improved_independent_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
