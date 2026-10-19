"""Create bounded public extracts from private browser logs; no network access."""
import argparse, hashlib, json, re
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def read_jsonl(path):return [json.loads(line) for line in path.read_text().splitlines() if line]

def extract(private,output):
    output.mkdir(parents=True,exist_ok=True); aliases={}; sources={}; rows=[]; evidence=[]; hashes={}
    for site in ['calendar','notion']:
        folder=private/site
        original=folder/'trials.jsonl';final=folder/'final_trials.jsonl'
        chosen=final if final.exists() else original
        data=read_jsonl(chosen);hashes[site]={'terminal_file':chosen.name,'terminal_sha256':digest(chosen.read_bytes()),'original_terminal_sha256':digest(original.read_bytes()),'actions_sha256':digest((folder/'actions.jsonl').read_bytes())}
        for row in data:
            if row.get('native_id'):aliases[row['native_id']]='record-'+row['trial_id']
        rawlines=(folder/'actions.jsonl').read_bytes().splitlines(keepends=True)
        lookup={}
        for line,raw in enumerate(rawlines,1):
            r=json.loads(raw);key=r['id'];assert key not in lookup,'Repeated event ID in new run'
            ref={'site':site,'id':key,'line':line,'sha256':digest(raw)};lookup[key]=(r,ref)
            item={**ref,'type':r.get('type',r.get('kind')),'label':r.get('label'),'utc':r.get('utc'),'trial_id':r.get('trial_id')}
            # Raw UI, private URLs and arbitrary page strings are not exported.
            for k in ['x','y','x_raw','y_raw','identity_ok','contract_ok','reloaded','phase','active_matches','status']:
                if k in r:item[k]=r[k]
            evidence.append(item)
        sources[site]=lookup
        for row in data:rows.append((site,row))
    def replace(value):
        if isinstance(value,dict):return {k:replace(v) for k,v in value.items()}
        if isinstance(value,list):return [replace(v) for v in value]
        if isinstance(value,str):
            for native,alias in sorted(aliases.items(),key=lambda x:-len(x[0])):value=value.replace(native,alias)
            value=re.sub(r'https?://(?:calendar\.google\.com|(?:app\.)?notion\.so|(?:app\.)?notion\.com)/\S+','<PRIVATE_URL>',value)
            return value
        return value
    def source(site,identity):
        if not identity:return None
        return sources[site][identity][1]
    def observation(site,o):
        if o is None:return None
        eid=o.get('evidence_id',o.get('id'));raw,ref=sources[site][eid]
        native=o.get('identity',o.get('native_id'));assert native in aliases,'Unknown native identity'
        contract=o.get('contract_ok',o.get('contract')) is True and o.get('identity_ok',True) is True
        return {'x':o.get('x'),'y':o.get('y'),'identity':aliases[native],'contract':contract,'readId':o.get('readId',eid),'readAt':o.get('readAt',o.get('utc')),'reloaded':o.get('reloaded') is True,'x_raw':o.get('x_raw'),'y_raw':o.get('y_raw'),'checks':o.get('checks',o.get('contract')),'source':ref,'ui_source':source(site,raw.get('source_observation',raw.get('source')))}
    public=[]
    for site,row in rows:
        out={k:replace(row.get(k)) for k in ['trial_id','assignment','status','reason','started_at','ended_at','failed_phase','prepare_input','decision','finish_input','finish']}
        out['site']=site
        for name in ['baseline','agent','preundo']:out[name]=observation(site,row.get(name))
        out['later_phases']=[{'command':phase['command'],'observation':observation(site,phase['observation'])} for phase in row.get('later_phases',[])]
        out['final_reads']=[observation(site,o) for o in row.get('final_reads',[])]
        seal=row.get('seal') or {};seal_id=seal.get('evidence_id',seal.get('id'));out['seal']={'source':source(site,seal_id),'utc':seal.get('utc'),'presented_later':row['assignment']['presented_later'],'history_complete':row['assignment']['history_complete'],'before_later':row['assignment']['seal_before_later']}
        a=row.get('actuator') or {};out['actuator']={'requested':a.get('requested'),'literal':a.get('literal',a.get('actual_literal')),'fault':a.get('fault'),'attempted':a.get('attempted',a.get('write_attempted',False)),'source':source(site,a.get('evidence_id'))}
        for label in ['prepare','finish']:
            eid=row.get(label+'_evidence_id') or (row.get(label+'_evidence') or {}).get('id')
            out[label+'_source']=source(site,eid)
        cl=row.get('cleanup',{});out['cleanup']={k:replace(cl.get(k)) for k in ['status','active_matches','reason']};out['cleanup']['sources']=[source(site,eid) for eid in cl.get('evidence_ids',[])]
        for optional in ['cleanup_original','cleanup_adjudication','recovery_note']:
            if optional in row:out[optional]=replace(row[optional])
        public.append(out)
    alltext='\n'.join(json.dumps(replace(r),sort_keys=True) for r in public)+'\n'
    evidencetext='\n'.join(json.dumps(replace(r),sort_keys=True) for r in evidence)+'\n'
    # This is a bounded exclusion check, not a proof that no private information exists.
    for value in aliases:assert value not in alltext and value not in evidencetext,'Native identity leak'
    (output/'improved_trials.jsonl').write_text(alltext);(output/'improved_evidence.jsonl').write_text(evidencetext)
    (private/'private_alias_map.json').write_text(json.dumps(aliases,indent=2)+'\n')
    receipt={'status':'EXTRACTED_REQUIRES_REVIEW','terminal_rows':len(public),'source_lines':len(evidence),'source_files':hashes,'public_sha256':{'improved_trials.jsonl':digest(alltext.encode()),'improved_evidence.jsonl':digest(evidencetext.encode())},'scope':'Only synthetic selected fields, controller inputs/outputs, action metadata and source hashes. Full private UI remains local.'}
    (output/'improved_extraction.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--private-dir',required=True);p.add_argument('--output-dir',default='.');a=p.parse_args();r=extract(Path(a.private_dir),Path(a.output_dir));print(json.dumps({k:r[k] for k in ['status','terminal_rows','source_lines']}))
