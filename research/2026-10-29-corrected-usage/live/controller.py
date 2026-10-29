"""Evaluate captured test names with the unchanged parent study rules."""
import argparse
import importlib.util
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('parent_study', BASE.parent/'run_study.py')
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
CASES = {
    'credit': {'order':['A2','A1','B1','B2'], 'cap':1},
    'upward': {'order':['A2','A1','B1','B2'], 'cap':2},
    'replay': {'order':['A2','A2','B2','A1','B1'], 'cap':3},
}

def analyze(observations):
    output=[]
    for service in ['D','C']:
        for case, config in CASES.items():
            values=[]; provenance=[]
            for item in 'AB':
                for rev in [1,2]:
                    key=f'{service}-{case}-{item}-{rev}'
                    o=observations[key]
                    pattern=rf'CUA-CORR-20261029 {service}-{case}-{item} r{rev} c([0-2])'
                    m=re.fullmatch(pattern,o['name'])
                    if not m or not o['exact_id_read'] or (rev==2 and not o['browser_saved_read']):
                        raise ValueError('Incomplete source evidence: '+key)
                    values.append(int(m[1]));provenance.append(key)
            source=dict(id=service+'-'+case,values=values,order=config['order'])
            for rule in study.RULES:
                t=study.evaluate(source,rule)
                q=t['states'][-1]['q'];z=values[1]+values[3];cap=config['cap']
                admitted=t['closure']['passed'] and q+1<=cap
                output.append(dict(service=service,case=case,rule=rule,source_keys=provenance,
                    values=values,order=config['order'],states=t['states'],q=q,true_charge=z,
                    cap=cap,demand=1,admitted=admitted,error=q-z,
                    excess=max(0,z+int(admitted)-cap),
                    feasible_refusal=not admitted and z+1<=cap,
                    output_alias=service+'-out-'+rule,
                    required_name=f'CUA-CORR-20261029 {service}-out-{rule} saved-{case}' if admitted else None))
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('observations');p.add_argument('output');a=p.parse_args()
    result=analyze(json.loads(Path(a.observations).read_text()))
    Path(a.output).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'cases':6,'decisions':len(result),'admitted':sum(x['admitted'] for x in result)}))
