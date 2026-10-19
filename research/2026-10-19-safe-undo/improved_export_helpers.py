"""Export actual helper versions, remove account literals and adapt local imports."""
import argparse,hashlib,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--private-dir',required=True);ap.add_argument('--output-dir',default='.');a=ap.parse_args();private=Path(a.private_dir);output=Path(a.output_dir)
    names=json.loads((private/'private_redactions.json').read_text())['account_names'];items=[]
    for site in ['calendar','notion']:
        sources=sorted(f for f in (private/site).iterdir() if f.suffix in ['.mjs','.js'])
        for src in sources:
            raw=src.read_bytes();text=raw.decode();replacements=[]
            for name in sorted(names,key=len,reverse=True):
                if name in text:replacements.append({'kind':'account_name','count':text.count(name)});text=text.replace(name,'<ACCOUNT_DISPLAY_NAME>')
            for other in sources:
                for quote in ["'",'"']:
                    old=quote+'./'+other.name+quote;new=quote+'./improved_'+site+'_'+other.name+quote
                    if old in text:replacements.append({'kind':'local_import','source':other.name,'count':text.count(old)});text=text.replace(old,new)
            name='improved_'+site+'_'+src.name;(output/name).write_text(text)
            items.append({'private_source':site+'/'+src.name,'public_file':name,'original_sha256':hashlib.sha256(raw).hexdigest(),'public_sha256':hashlib.sha256(text.encode()).hexdigest(),'changes':replacements})
    result={'files':items,'scope':'Actual helper source versions. Account-name literals are removed and relative imports use the published prefixed filenames. The browser client and credentials are not included.'}
    (output/'improved_helper_manifest.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('Exported',len(items),'helper files')

if __name__=='__main__':main()
