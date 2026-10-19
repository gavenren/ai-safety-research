"""Extract synthetic fields from private local browser records.

Private account logs are required only for extraction, not public result replay.
This script does not contact a browser or change an account.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

def sha(data):return hashlib.sha256(data).hexdigest()
def lines(path):return [json.loads(v) for v in path.read_text().splitlines() if v]

def extract(work,output):
    private_names=json.loads((work/'private_redactions.json').read_text())['account_names']
    source_paths={site:(work/site/'final_trials.jsonl' if (work/site/'final_trials.jsonl').exists() else work/site/'trials.jsonl') for site in ('calendar','notion')}
    sources={site:lines(path) for site,path in source_paths.items()}
    def identity(t):return t.get('native_id') or t.get('cleanup',{}).get('native_id')
    mapping={identity(t):t['trial_id']+'-record' for rows in sources.values() for t in rows if identity(t)}
    cleanup_sources={site:json.loads((work/site/'cleanup_summary.json').read_text()) for site in sources if (work/site/'cleanup_summary.json').exists()}
    for site,data in cleanup_sources.items():
        for role in ('preflight','parent'):
            if isinstance(data.get(role),dict) and data[role].get('native_id'):
                mapping[data[role]['native_id']]=site+'-'+role+'-record'
    def clean(value):
        if isinstance(value,dict):
            return {('record_alias' if k=='native_id' else k):clean(v) for k,v in value.items() if k not in ('href','url','tab_id','parent_id')}
        if isinstance(value,list):return [clean(v) for v in value]
        if not isinstance(value,str):return value
        for old,new in sorted(mapping.items(),key=lambda x:-len(x[0])):value=value.replace(old,new)
        value=re.sub(r'https?://[^\s"<>\\]+','[private-url]',value)
        value=re.sub(r'/Users/[^\s"\n]+','[local-path]',value)
        value=re.sub(r'\b[0-9a-f]{32}\b','[private-id]',value,flags=re.I)
        value=re.sub(r'\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b','[private-id]',value,flags=re.I)
        value=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[private-email]',value)
        for name in sorted(private_names,key=len,reverse=True):
            value=re.sub(re.escape(name),'[account-name]',value,flags=re.I)
        return value
    public=[];evidence=[];metadata=[]
    for site,rows in sources.items():
        logpath=work/site/'actions.jsonl';rawlines=logpath.read_text().splitlines();raw=[json.loads(v) for v in rawlines if v]
        index={}
        for number,r in enumerate(raw,1):index.setdefault(r.get('id'),[]).append(number)
        def observation(o):
            if o is None:return None
            keys=('x','y','x_raw','y_raw','native_id','token','identity_ok','contract_ok','reloaded','evidence_id','utc','source','contract','checks','raw')
            out=clean({k:o[k] for k in keys if k in o})
            out['raw_log_lines']=index.get(o.get('evidence_id'),[])
            return out
        for t in rows:
            keys=('trial_id','site','kind','rule','history','token','native_id','terminal_status','reason','started_at','ended_at','uncertain_saves','decision','decision_evidence_id','cleanup','cleanup_original','cleanup_adjudication','reconstruction','recovery_note')
            row=clean({k:t[k] for k in keys if k in t})
            row['record_alias']=mapping.get(identity(t))
            for key in ('baseline','agent','preundo','final'):row[key]=observation(t.get(key))
            row['later']=[{'command':v['command'],'observation':observation(v.get('observation'))} for v in t.get('later',[])]
            row['reason']=row.get('reason')
            public.append(row)
        for number,r in enumerate(raw,1):
            kind=r.get('type',r.get('kind'))
            keep=('id','trial_id','token','phase','utc','type','kind','label','args','start','end','before','after','source','error','decision','rule','later','command')
            # Whole DOM text, unrelated UI and private screenshots are excluded.
            item=clean({k:r[k] for k in keep if k in r and k!='later'})
            item.update(site=site,raw_log_line=number,raw_line_sha256=sha(rawlines[number-1].encode()))
            if kind=='saved_fields':item['field_evidence']=observation(r.get('fields',r))
            evidence.append(item)
        metadata.append({'site':site,'trial_rows':len(rows),'raw_log_rows':len(raw),'raw_log_sha256':sha(logpath.read_bytes()),'original_trial_file_sha256':sha((work/site/'trials.jsonl').read_bytes()),'terminal_source_file':source_paths[site].name,'terminal_source_sha256':sha(source_paths[site].read_bytes()),'duplicate_ids':{k:v for k,v in index.items() if len(v)>1}})
    output.mkdir(parents=True,exist_ok=True)
    (output/'live_trials.jsonl').write_text(''.join(json.dumps(v,sort_keys=True)+'\n' for v in public))
    (output/'live_evidence.jsonl').write_text(''.join(json.dumps(v,sort_keys=True)+'\n' for v in evidence))
    (output/'live_extraction.json').write_text(json.dumps({'sources':metadata,'privacy':'Only selected synthetic fields and action metadata are public. Native identities use per-record aliases. Full private DOM and screenshots are omitted. Raw line numbers disambiguate early duplicate Calendar IDs.','public_trials_sha256':sha((output/'live_trials.jsonl').read_bytes()),'public_evidence_sha256':sha((output/'live_evidence.jsonl').read_bytes())},indent=2)+'\n')
    if len(cleanup_sources)==2:
        (output/'live_cleanup.json').write_text(json.dumps({'sites':clean(cleanup_sources),'source_hashes':{site:sha((work/site/'cleanup_summary.json').read_bytes()) for site in cleanup_sources},'limit':'Calendar trial23 can still have an unsaved browser draft. Zero active saved records does not prove that this draft was closed.'},indent=2,sort_keys=True)+'\n')
    (work/'private_alias_map.json').write_text(json.dumps(mapping,indent=2)+'\n')
    return public

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private-dir',required=True);p.add_argument('--output-dir',default='.')
    a=p.parse_args();result=extract(Path(a.private_dir),Path(a.output_dir));print('Extracted',len(result),'trial rows')
