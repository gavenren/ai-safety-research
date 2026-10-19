"""Publish generated browser helper source with account-name literals removed."""
import argparse,hashlib,json
from pathlib import Path

def digest(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--private-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,default=Path('.'));a=p.parse_args()
    names=json.loads((a.private_dir/'private_redactions.json').read_text())['account_names']
    records=[]
    for site in ('calendar','notion'):
        for src in sorted((a.private_dir/site).iterdir()):
            if src.suffix not in ('.js','.mjs'):continue
            b=src.read_bytes();text=b.decode();changes=0
            for name in sorted(names,key=len,reverse=True):
                changes+=text.count(name);text=text.replace(name,'<ACCOUNT_DISPLAY_NAME>')
            target='live_'+site+'_'+src.name
            (a.output_dir/target).write_text(text)
            records.append({'private_source':site+'/'+src.name,'public_file':target,'original_sha256':digest(b),'public_sha256':digest(text.encode()),'account_name_literal_replacements':changes})
    manifest={'files':records,'scope':'Actual generated helper source and preserved versions. Account-name literals are replaced with <ACCOUNT_DISPLAY_NAME>. Supply your own authorized test account name when reproducing. No browser client library source is included.'}
    (a.output_dir/'live_helper_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Exported',len(records),'helper source files')
if __name__=='__main__':main()
