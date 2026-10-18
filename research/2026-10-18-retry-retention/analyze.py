"""Exact synthetic retention audit. No network or account calls."""
import argparse,csv,gzip,hashlib,heapq,itertools,json,platform,sys
from pathlib import Path
POLICIES=('no_retry','new_key','stable_key','send_cutoff','delay_margin','receiver_cutoff','permanent')
LABELS=('duplicate','confirmed','false_exact_claim','wrong_at_receipt','late_duplicate','future_only_false','missed','unconfirmed_one','unconfirmed_duplicate','clean_confirmed')
COUNTS=('effect_count','send_count','arrival_count','cache_hits','receiver_rejections','expired_keys')
WITNESS_LABELS=('duplicate','false_exact_claim','future_only_false','late_duplicate')
EXPECTED_KEYS={'schema_version','slots','retention_ticks','delay_bounds','spacings','policies','stress','primary','cost_example','expiry','cache_hit_renews','tie_order','first_send_always','drain_after_receipt'}

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def sha(b):return hashlib.sha256(b).hexdigest()
def validate(c):
    if type(c)!=dict or set(c)!=EXPECTED_KEYS:raise ValueError('Wrong configuration keys')
    fixed={'schema_version':1,'slots':3,'policies':list(POLICIES),'expiry':'arrival_minus_creation_greater_than_or_equal_retention','cache_hit_renews':False,'tie_order':'prior_arrivals_by_slot_then_send_then_zero_delay_arrival','first_send_always':True,'drain_after_receipt':True}
    for k,v in fixed.items():
        if type(c[k])!=type(v) or c[k]!=v:raise ValueError('Wrong fixed setting: '+k)
    for k,low in [('retention_ticks',1),('delay_bounds',0),('spacings',1)]:
        a=c[k]
        if type(a)!=list or not a or any(type(x)!=int or x<low for x in a) or sorted(set(a))!=a:raise ValueError('Bad grid: '+k)
    fields={'retention':1,'actual_delay_bound':0,'spacing':1}
    for k in ['primary','cost_example','stress']:
        spec=fields|({'declared_delay_bound':0} if k=='stress' else {})
        if type(c[k])!=dict or set(c[k])!=set(spec):raise ValueError('Bad case keys')
        if any(type(c[k][f])!=int or c[k][f]<lo for f,lo in spec.items()):raise ValueError('Bad case value')
        if k!='stress' and not(c[k]['retention'] in c['retention_ticks'] and c[k]['actual_delay_bound'] in c['delay_bounds'] and c[k]['spacing'] in c['spacings']):raise ValueError('Displayed case outside main grid')
    return c

def settings(c):
    for T,D,s in itertools.product(c['retention_ticks'],c['delay_bounds'],c['spacings']):yield ('main',T,D,D,s)
    z=c['stress'];yield ('stress',z['retention'],z['actual_delay_bound'],z['declared_delay_bound'],z['spacing'])

def simulate(suite,T,D,B,s,policy,codes):
    if policy not in POLICIES or len(codes)!=3 or any(type(x)!=int or not 0<=x<2*D+3 for x in codes):raise ValueError('Invalid policy or transport codes')
    queue=[(i*s,1,i) for i in range(3)];heapq.heapify(queue)
    memory={};log=[];sent=[];arrived=[];effects=[];first=None
    hits=rejected=expired=0
    while queue:
        t,kind,i=heapq.heappop(queue)
        key=i if policy=='new_key' else 0
        if kind==1:
            reason=None
            if first is not None:reason='receipt'
            elif i>0 and policy=='no_retry':reason='no_retry'
            elif i>0 and policy in ('send_cutoff','receiver_cutoff') and t>=T:reason='send_cutoff'
            elif i>0 and policy=='delay_margin' and t+B>=T:reason='delay_margin'
            if reason:
                log.append({'tick':t,'kind':'skip','slot':i,'reason':reason});continue
            sent.append(i);log.append({'tick':t,'kind':'send','slot':i,'key':key,'code':codes[i]})
            if codes[i]:heapq.heappush(queue,(t+(codes[i]-1)//2,0,i))
        else:
            arrived.append(i)
            ev={'tick':t,'kind':'arrival','slot':i,'key':key,'expired':False,'visible_success':False,'effect_id':None}
            if policy=='receiver_cutoff' and t>=T:
                rejected+=1;ev['action']='reject_deadline'
            else:
                if key in memory and policy!='permanent' and t-memory[key][0]>=T:
                    del memory[key];expired+=1;ev['expired']=True
                if key in memory:
                    hits+=1;ev['action']='cache_hit';effect_id=memory[key][1]
                else:
                    effect_id=len(effects)+1;memory[key]=(t,effect_id)
                    effects.append({'tick':t,'slot':i,'effect_id':effect_id,'event_index':len(log)})
                    ev['action']='append'
                ev['effect_id']=effect_id;ev['visible_success']=(codes[i]%2==0)
                if ev['visible_success'] and first is None:
                    first={'tick':t,'effect_id':effect_id,'event_index':len(log),'effect_count':len(effects)}
            ev['effect_count']=len(effects);log.append(ev)
    n=len(effects);confirmed=first is not None
    r={'suite':suite,'retention':T,'actual_delay_bound':D,'declared_delay_bound':B,'spacing':s,'policy':policy,'codes':list(codes),'effect_count':n,'send_count':len(sent),'arrival_count':len(arrived),'cache_hits':hits,'receiver_rejections':rejected,'expired_keys':expired,'sent_slots':sent,'arrived_slots':arrived,'first_receipt_time':first['tick'] if first else None,'first_receipt_effect_id':first['effect_id'] if first else None,'first_receipt_event_index':first['event_index'] if first else None,'effect_count_at_receipt':first['effect_count'] if first else None,'final_event_time':log[-1]['tick'],'duplicate':n>1,'confirmed':confirmed,'false_exact_claim':confirmed and n!=1,'wrong_at_receipt':confirmed and first['effect_count']>1,'late_duplicate':confirmed and any(e['effect_id']>=2 and e['event_index']>first['event_index'] for e in effects),'future_only_false':confirmed and n>1 and first['effect_count']==1,'missed':n==0,'unconfirmed_one':n==1 and not confirmed,'unconfirmed_duplicate':n>1 and not confirmed,'clean_confirmed':n==1 and confirmed,'events':log,'effects':effects}
    assert n==len([e for e in log if e['kind']=='arrival' and e['action']=='append'])
    assert sum(r[k] for k in ['missed','unconfirmed_one','unconfirmed_duplicate','clean_confirmed','false_exact_claim'])==1
    assert not confirmed or n>=1
    assert r['false_exact_claim']==(r['wrong_at_receipt'] or r['future_only_false'])
    assert not r['future_only_false'] or r['late_duplicate']
    assert hits+n+rejected==len(arrived)
    return r

def save_json(path,x):path.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run(input_dir,output_dir):
    c=validate(json.loads((input_dir/'config.json').read_text()))
    manifest=json.loads((input_dir/'input_manifest.json').read_text())
    for name,h in manifest['sha256'].items():
        if sha((input_dir/name).read_bytes())!=h:raise ValueError('Frozen input mismatch: '+name)
    output_dir.mkdir(exist_ok=True,parents=True)
    aggregates=[];pairs=[];witnesses=[];total_rows=total_events=main_scenarios=stress_scenarios=0
    with (output_dir/'traces.jsonl.gz').open('wb') as raw:
      with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as gz:
       for suite,T,D,B,s in settings(c):
        common={'suite':suite,'retention':T,'actual_delay_bound':D,'declared_delay_bound':B,'spacing':s}
        agg={pol:common|{'policy':pol,'assignments':0}|{x:0 for x in LABELS+COUNTS} for pol in POLICIES}
        paired={pol:common|{'policy':pol,'assignments':0,'missed_vs_permanent_effect':0,'unconfirmed_vs_permanent_confirmed':0,'duplicate_vs_permanent_clean':0,'clean_confirmed_vs_permanent_unconfirmed':0} for pol in POLICIES}
        witness={}
        for codes in itertools.product(range(2*D+3),repeat=3):
            rows={pol:simulate(suite,T,D,B,s,pol,codes) for pol in POLICIES}
            ref=rows['permanent']
            if suite=='main':main_scenarios+=1
            else:stress_scenarios+=1
            for pol,r in rows.items():
                gz.write((canonical(r)+'\n').encode());total_rows+=1;total_events+=len(r['events'])
                a=agg[pol];a['assignments']+=1
                for k in LABELS+COUNTS:a[k]+=r[k]
                z=paired[pol];z['assignments']+=1
                z['missed_vs_permanent_effect']+=r['missed'] and ref['effect_count']>0
                z['unconfirmed_vs_permanent_confirmed']+=not r['confirmed'] and ref['confirmed']
                z['duplicate_vs_permanent_clean']+=r['duplicate'] and not ref['duplicate']
                z['clean_confirmed_vs_permanent_unconfirmed']+=r['clean_confirmed'] and not ref['confirmed']
                rank=(r['send_count'],r['arrival_count'],r['final_event_time'],tuple(codes))
                for label in WITNESS_LABELS:
                    k=(pol,label)
                    if r[label] and (k not in witness or rank<witness[k][0]):witness[k]=(rank,r)
            for pol in ['new_key','stable_key']:
                for k in ['sent_slots','arrived_slots','first_receipt_time']:assert rows[pol][k]==ref[k]
            assert rows['send_cutoff']['sent_slots']==rows['receiver_cutoff']['sent_slots']
        q=2*D+3;n=q**3
        a=agg['no_retry'];assert a['missed']==q*q and a['clean_confirmed']==(D+1)*q*q and a['unconfirmed_one']==(D+1)*q*q
        a=agg['permanent'];assert a['missed']==1 and a['clean_confirmed']==n-(D+2)**3 and a['unconfirmed_one']==(D+2)**3-1
        aggregates.extend(agg.values());pairs.extend(paired.values())
        for (pol,label),(rank,r) in sorted(witness.items()):witnesses.append({'label':label,'rank':list(rank[:3])+[list(rank[3])],'trace':r})
    main=[a for a in aggregates if a['suite']=='main'];stress=[a for a in aggregates if a['suite']=='stress']
    bad=lambda pol,which:sum(a['duplicate'] for a in which if a['policy']==pol)
    hypotheses={
      'H1':all(bad(pol,main)>0 for pol in ['stable_key','send_cutoff']),
      'H2':all(a['duplicate']==0 and a['false_exact_claim']==0 for a in main if a['policy'] in ['no_retry','delay_margin','receiver_cutoff','permanent']),
      'H3':any(a['future_only_false']>0 for a in main if a['policy']=='send_cutoff'),
      'H4':all(any(a['missed_vs_permanent_effect']>0 for a in pairs if a['suite']=='main' and a['policy']==pol) for pol in ['delay_margin','receiver_cutoff']),
      'H5':bad('delay_margin',stress)>0 and all(bad(pol,stress)==0 for pol in ['receiver_cutoff','permanent'])}
    summary={'main_settings':len(main)//7,'stress_settings':len(stress)//7,'main_scenarios':main_scenarios,'stress_scenarios':stress_scenarios,'main_policy_rows':main_scenarios*7,'stress_policy_rows':stress_scenarios*7,'total_policy_rows':total_rows,'total_events':total_events,'aggregate_rows':len(aggregates),'paired_rows':len(pairs),'witnesses':len(witnesses),'hypotheses':hypotheses}
    write_csv(output_dir/'results.csv',aggregates);save_json(output_dir/'paired_results.json',pairs);save_json(output_dir/'witnesses.json',witnesses);save_json(output_dir/'summary.json',summary)
    save_json(output_dir/'environment.json',{'python':sys.version,'platform':platform.platform(),'dependencies':'Python standard library only','randomness':False,'model':'Codex agents; exact immutable model build unavailable','roles':'Root design, main implementation and report; separate source/proof reviewer; separate independent implementation and result reviewer','external_compute':'No new paid compute or paid API service','data':'Synthetic request schedules; no live account or website experiment'})
    return summary

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input-dir',type=Path,default=Path('.'));ap.add_argument('--output-dir',type=Path,default=Path('.'));a=ap.parse_args()
    print(json.dumps(run(a.input_dir,a.output_dir),indent=2,sort_keys=True))
