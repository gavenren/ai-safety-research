"""Independent raw-to-public audit. Does not import the extractor."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def must(c,m):
    if not c:raise ValueError(m)


def observations(t):
    out=[]
    for k in ('baseline','agent','preundo','final'):
        if t.get(k) is not None:out.append((k,t[k]))
    out.extend(('later.'+str(i),q['observation']) for i,q in enumerate(t.get('later',[])))
    return dict(out)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--public',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    receipt=json.loads((args.public/'live_extraction.json').read_text());pubt=read(args.public/'live_trials.jsonl');pube=read(args.public/'live_evidence.jsonl')
    must(sha((args.public/'live_trials.jsonl').read_bytes())==receipt['public_trials_sha256'],'public trial hash changed')
    must(sha((args.public/'live_evidence.jsonl').read_bytes())==receipt['public_evidence_sha256'],'public evidence hash changed')
    rawt={};rawe={};private=set();prefix_rows={};fieldchecks=0;phasechecks=0
    for src in receipt['sources']:
        site=src['site'];p=args.work/site
        terminal_file=src.get('terminal_source_file','trials.jsonl')
        must(terminal_file in ('trials.jsonl','final_trials.jsonl'),'unexpected terminal source file')
        tb=(p/terminal_file).read_bytes().splitlines(keepends=True)[:src['trial_rows']]
        if 'original_trial_file_sha256' in src:
            ob=(p/'trials.jsonl').read_bytes().splitlines(keepends=True)[:src['trial_rows']]
            must(sha(b''.join(ob))==src['original_trial_file_sha256'],'original trial prefix changed')
        eb=(p/'actions.jsonl').read_bytes().splitlines(keepends=True)[:src['raw_log_rows']]
        must(sha(b''.join(tb))==src.get('terminal_source_sha256',src.get('trial_file_sha256')),'raw trial prefix changed')
        must(sha(b''.join(eb))==src['raw_log_sha256'],'raw evidence prefix changed')
        for line in tb:
            t=json.loads(line);rawt[t['trial_id']]=t
            if t.get('native_id'):private.add(t['native_id'])
            if t.get('cleanup',{}).get('native_id'):private.add(t['cleanup']['native_id'])
        for i,line in enumerate(eb,1):
            e=json.loads(line);rawe[(site,i)]=(line.rstrip(b'\r\n'),e)
            if e.get('kind')=='native_identity' and re.fullmatch(r'[0-9a-f]{32}',e.get('id','')):private.add(e['id'])
        prefix_rows[site]=len(eb)
    must(len(rawt)==len(pubt),'trial coverage changed')
    must(len(pube)==len(rawe),'evidence row coverage changed')
    aliases={t.get('native_id') or t.get('cleanup',{}).get('native_id'):t['trial_id']+'-record' for t in rawt.values() if t.get('native_id') or t.get('cleanup',{}).get('native_id')}
    cleanup_sources={}
    if (args.public/'live_cleanup.json').exists():
        for site in ('calendar','notion'):
            cleanup_sources[site]=json.loads((args.work/site/'cleanup_summary.json').read_text())
            for role in ('preflight','parent'):
                identity=cleanup_sources[site].get(role,{}).get('native_id')
                if identity:aliases[identity]=site+'-'+role+'-record';private.add(identity)
    def exact_projection(p,r):
        if isinstance(r,dict):
            expected={('record_alias' if k=='native_id' else k):v for k,v in r.items() if k not in ('url','href','tab_id','parent_id')}
            must(set(p)==set(expected),'cleanup projection key mismatch')
            for k,v in expected.items():exact_projection(p[k],v)
        elif isinstance(r,list):
            must(len(p)==len(r),'cleanup projection length mismatch')
            for x,y in zip(p,r):exact_projection(x,y)
        elif isinstance(r,str):
            must(p==aliases.get(r,r),'cleanup projection value mismatch')
        else:must(p==r,'cleanup projection scalar mismatch')
    seen=set()
    for p in pube:
        key=(p['site'],p['raw_log_line']);must(key not in seen,'duplicate public raw line');seen.add(key)
        b,r=rawe[key];must(sha(b)==p['raw_line_sha256'],'raw line hash mismatch')
        for k in ('trial_id','token','phase','utc'):
            if k in r:must(p.get(k)==r[k],'evidence metadata mismatch '+k)
        must(p.get('type',p.get('kind'))==r.get('type',r.get('kind')),'event type mismatch')
        for k in ('decision','output','input','later','active_matches','status','error'):
            # Strings may contain private values; structured controller data must match.
            if k in p and k in r and isinstance(r[k],(dict,list,int,bool,type(None))):
                if k not in ('input',):must(p[k]==r[k],'evidence payload mismatch '+k)
    for p in pubt:
        r=rawt[p['trial_id']]
        for k in ('trial_id','site','kind','rule','history','token','terminal_status','started_at','ended_at','decision','decision_evidence_id'):
            must(p.get(k)==r.get(k),'trial field mismatch '+k);fieldchecks+=1
        alias=p.get('record_alias');must(alias==(p['trial_id']+'-record' if r.get('native_id') or r.get('cleanup',{}).get('native_id') else None),'alias mapping mismatch')
        must([x['command'] for x in p['later']]==[x['command'] for x in r['later']],'later commands changed')
        po,ro=observations(p),observations(r);must(set(po)==set(ro),'phase coverage changed')
        for label,o in po.items():
            original=ro[label]
            for k in ('x','y','x_raw','y_raw','identity_ok','contract_ok','reloaded','utc','token','evidence_id','checks','contract'):
                if k in original:must(o.get(k)==original[k],'phase data mismatch '+label+'/'+k);fieldchecks+=1
            must(o.get('record_alias')==alias,'phase alias mismatch')
            if 'raw' in original:
                wanted={k:v for k,v in original['raw'].items() if k not in ('url','native_id')}
                must(o.get('raw')==wanted,'raw field projection mismatch')
            matching=[i for (site,i),(b,e) in rawe.items() if site==p['site'] and e.get('trial_id')==p['trial_id'] and e.get('id')==o['evidence_id']]
            must(o['raw_log_lines']==matching,'phase raw-line disambiguation mismatch')
            phasechecks+=1
        for k in ('status','active_matches','evidence_ids'):
            must(p.get('cleanup',{}).get(k)==r.get('cleanup',{}).get(k),'cleanup changed '+k);fieldchecks+=1
        for k in ('cleanup_original','cleanup_adjudication','recovery_note'):
            if k in r:must(k in p,'recovery or cleanup note omitted');exact_projection(p[k],r[k]);fieldchecks+=1
        if r.get('reason') is not None:must(bool(p.get('reason')),'reason omitted')
    public_text=(args.public/'live_trials.jsonl').read_text()+(args.public/'live_evidence.jsonl').read_text()
    cleanup_hash=None
    if cleanup_sources:
        pc=json.loads((args.public/'live_cleanup.json').read_text())
        for site,raw in cleanup_sources.items():
            must(pc['source_hashes'][site]==sha((args.work/site/'cleanup_summary.json').read_bytes()),'cleanup summary source hash mismatch')
            exact_projection(pc['sites'][site],raw)
        must('unsaved browser draft' in pc['limit'],'browser draft limit omitted')
        public_text+=(args.public/'live_cleanup.json').read_text()
        cleanup_hash=sha((args.public/'live_cleanup.json').read_bytes())
    private_names=json.loads((args.work/'private_redactions.json').read_text())['account_names']
    must(all(name.lower() not in public_text.lower() for name in private_names),'private account name remains')
    leaks=[s for s in private if s and s in public_text]
    must(not leaks,'private native identifier remains')
    # These fields are never required for the synthetic public evidence.
    must(not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',public_text),'email remains')
    for forbidden in ('/Users/','https://calendar.google.com/calendar/','https://www.notion.so/'):
        must(forbidden not in public_text,'private account text remains')
    result={'status':'PASS','public_trial_rows':len(pubt),'public_evidence_rows':len(pube),'raw_prefix_rows':prefix_rows,'structured_field_checks':fieldchecks,'saved_phase_checks':phasechecks,'private_name_terms_checked':len(private_names),'known_private_identifiers_checked':len(private),'private_identifier_hits':0,'raw_line_sha256_checks':len(pube),'public_trial_sha256':receipt['public_trials_sha256'],'public_evidence_sha256':receipt['public_evidence_sha256'],'public_cleanup_sha256':cleanup_hash,'limits':['Checks exact current extraction snapshot; later rows require a new extraction and audit.','Public rows omit full private native UI snapshots and screenshots. Independent raw-source audit is separate.','No scored results are inferred for unknown or missing assignments.']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
