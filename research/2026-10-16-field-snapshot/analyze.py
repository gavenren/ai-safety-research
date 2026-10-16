#!/usr/bin/env python3
"""Exact finite history counts for synthetic saved-field checks. No network calls."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
POLICIES=('values','full_revision','modulo_2','modulo_4','partial_revision','atomic_final')
def bits(s,d):return ''.join(str((s>>i)&1) for i in range(d))
def parse_bits(v):return sum(int(x)<<i for i,x in enumerate(v))
def load_config(path):
    c=json.loads(Path(path).read_text());allowed={'fields':{2,3},'passes':{1,2,3},'writes_per_gap':{0,1,2}}
    required={'policies':list(POLICIES),'partial_revision_field':'last','read_order':'ascending','target':'all_ones','writes':'atomic_single_bit_flip','initial_revision':0,'seed':None,'random_sampling':False}
    if set(c)!=set(allowed)|set(required):raise ValueError('Missing or unknown configuration key')
    for key,values in allowed.items():
        x=c[key]
        if not isinstance(x,list) or not x or any(type(v) is not int or v not in values for v in x) or len(x)!=len(set(x)):raise ValueError('Invalid or repeated grid value: '+key)
    for k,v in required.items():
        if type(c[k]) is not type(v) or c[k]!=v:raise ValueError('Unsupported model: '+k)
    return c

def words(d,b):return sorted(w for k in range(b+1) for w in itertools.product(range(d),repeat=k))
def accepted(policy,key,d):
    state,n,last,ever,ok=key
    if policy=='atomic_final':return state==(1<<d)-1
    if not ok:return False
    if policy=='values':return True
    if policy=='full_revision':return n==0
    if policy=='modulo_2':return n%2==0
    if policy=='modulo_4':return n%4==0
    if policy=='partial_revision':return last==0
    raise ValueError(policy)

def trace(initial,gaps,d,r):
    state=parse_bits(initial);target=(1<<d)-1;revision=0;partial=0;ever=state==target;reads=[]
    events=[{'operation':'initial_revision','state':bits(state,d),'revision':0,'partial_revision':0}]
    for i,word in enumerate(gaps):
        for field in word:
            state^=1<<field;revision+=1;partial+=field==d-1;ever|=state==target
            events.append({'operation':'write','gap':i,'field':field,'state':bits(state,d),'revision':revision,'partial_revision':partial})
        if i<d*r:
            field=i%d;value=(state>>field)&1;reads.append(value)
            events.append({'operation':'field_read','index':i,'field':field,'value':value,'state':bits(state,d),'revision':revision,'partial_revision':partial})
    events.append({'operation':'final_revision_and_decision','state':bits(state,d),'revision':revision,'partial_revision':partial})
    return (state,revision,partial,ever,all(reads)),events

def solve(d,r,b):
    target=(1<<d)-1;ws=words(d,b);ngaps=d*r+1;counts={};best={};stages=[]
    for s in range(1<<d):
        k=(s,0,0,s==target,True);counts[k]=1;best[k]=(bits(s,d),())
    for g in range(ngaps):
        nxt=defaultdict(int);paths={}
        for key,count in counts.items():
            state,n,last,ever,ok=key
            for word in ws:
                s=state;e=ever
                for field in word:s^=1<<field;e|=s==target
                good=ok and (g==d*r or bool((s>>(g%d))&1))
                k=(s,n+len(word),last+word.count(d-1),e,good);nxt[k]+=count
                candidate=(best[key][0],best[key][1]+(word,))
                if k not in paths or candidate<paths[k]:paths[k]=candidate
        counts=dict(nxt);best=paths;expected=(1<<d)*len(ws)**(g+1)
        assert sum(counts.values())==expected
        stages.append({'fields':d,'passes':r,'writes_per_gap':b,'gaps_done':g+1,'merged_states':len(counts),'histories':expected})
    total=(1<<d)*len(ws)**ngaps;rows=[];witnesses=[];final_correct=sum(v for k,v in counts.items() if k[0]==target)
    assert final_correct==total//(1<<d)
    for policy in POLICIES:
        accept=never=wrong=missed=0;minimum={'no_common_target':None,'wrong_at_decision':None}
        for k,count in counts.items():
            a=accepted(policy,k,d);accept+=count*a;no_target=a and not k[3];bad_final=a and k[0]!=target
            never+=count*no_target;wrong+=count*bad_final;missed+=count*(not a and k[0]==target)
            for outcome,flag in [('no_common_target',no_target),('wrong_at_decision',bad_final)]:
                if flag:
                    candidate=(k[1],)+best[k]
                    if minimum[outcome] is None or candidate<minimum[outcome]:minimum[outcome]=candidate
        row={'fields':d,'passes':r,'writes_per_gap':b,'policy':policy,'total_histories':total,'accepted':accept,'no_common_target':never,'wrong_at_decision':wrong,'rejected_correct_final':missed,'min_no_common_target_writes':None if minimum['no_common_target'] is None else minimum['no_common_target'][0],'min_wrong_at_decision_writes':None if minimum['wrong_at_decision'] is None else minimum['wrong_at_decision'][0]}
        assert 0<=never<=wrong<=accept<=total
        if policy=='full_revision':assert accept==1 and never==wrong==0
        if policy=='atomic_final':assert accept==final_correct and never==wrong==missed==0
        if b==0:assert accept==1 and never==wrong==missed==0
        rows.append(row)
        for outcome,value in minimum.items():
            if value is None:continue
            n,initial,gaps=value;k,events=trace(initial,gaps,d,r);assert k[1]==n and accepted(policy,k,d)
            assert not k[3] if outcome=='no_common_target' else k[0]!=target
            witnesses.append({'fields':d,'passes':r,'writes_per_gap':b,'policy':policy,'outcome':outcome,'minimum_writes':n,'initial':initial,'gap_words':gaps,'events':events})
    terminal=[{'fields':d,'passes':r,'writes_per_gap':b,'current':bits(k[0],d),'total_writes':k[1],'last_field_writes':k[2],'ever_target':k[3],'all_reads_target':k[4],'histories':v} for k,v in sorted(counts.items())]
    return rows,terminal,stages,witnesses

def write_json(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,default=Path('.'));ap.add_argument('--output-dir',type=Path,default=Path('.'));a=ap.parse_args();c=load_config(a.input_dir/'config.json');manifest=json.loads((a.input_dir/'input_manifest.json').read_text())
    for n,h in manifest['sha256'].items():assert hashlib.sha256((a.input_dir/n).read_bytes()).hexdigest()==h,n
    a.output_dir.mkdir(exist_ok=True,parents=True);rows=[];terminal=[];stages=[];witnesses=[]
    for d,r,b in itertools.product(c['fields'],c['passes'],c['writes_per_gap']):
        x,t,s,w=solve(d,r,b);rows+=x;terminal+=t;stages+=s;witnesses+=w
    with (a.output_dir/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    raw=''.join(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n' for x in terminal).encode()
    with (a.output_dir/'terminal_counts.jsonl.gz').open('wb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:z.write(raw)
    write_json(a.output_dir/'stage_totals.json',stages);write_json(a.output_dir/'witnesses.json',witnesses)
    h1=all(next(x for x in rows if x['fields']==2 and x['passes']==r and x['writes_per_gap']==2 and x['policy']=='values')['min_no_common_target_writes']==2*(2*r-1) for r in c['passes'])
    h2=all(x['no_common_target']==x['wrong_at_decision']==0 for x in rows if x['policy'] in ['full_revision','atomic_final'])
    h3=all(any(x['no_common_target'] for x in rows if x['policy']==p) for p in ['modulo_2','modulo_4','partial_revision'])
    h4=any(x['rejected_correct_final'] for x in rows if x['policy']=='full_revision')
    summary={'status':'COMPLETE','settings':len(rows)//len(POLICIES),'policy_rows':len(rows),'terminal_count_rows':len(terminal),'stage_rows':len(stages),'witness_count':len(witnesses),'hypotheses':{'H1':h1,'H2':h2,'H3':h3,'H4':h4},'policies':{p:{'settings':sum(x['policy']==p for x in rows),'settings_with_no_common_target':sum(bool(x['no_common_target']) for x in rows if x['policy']==p),'settings_with_wrong_at_decision':sum(bool(x['wrong_at_decision']) for x in rows if x['policy']==p)} for p in POLICIES},'largest_history_set':max(x['total_histories'] for x in rows),'input_sha256':{n:hashlib.sha256((a.input_dir/n).read_bytes()).hexdigest() for n in ['config.json','analysis_plan.md','source_search.md','input_manifest.json']},'claims':'Exact synthetic counts only. No empirical probability or provider result.'}
    write_json(a.output_dir/'summary.json',summary);print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
