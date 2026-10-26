#!/usr/bin/env python3
"""Replay Calendar adapter checks from saved evidence. No network action."""
import argparse,copy,json
from pathlib import Path
from calendar_adapter import make_proof

def analyze(root):
    original=json.loads((root/'calendar_initial_traces.json').read_text())
    observations=json.loads((root/'calendar_adapter_observations.json').read_text())
    zones=json.loads((root/'calendar_timezone_checks.json').read_text())['observations']
    proofs=json.loads((root/'calendar_corrected_proofs.json').read_text())
    rows=[]
    for trace in original:
        for key,op in trace['state']['operations'].items():
            if op['status']!='saved':continue
            alias=op['record_alias'];obs=next(x for x in observations if x['record_alias']==alias)
            zone=next(x for x in zones if x['alias']==alias)
            def result(o,z):
                try:return make_proof(op['payload'],o,z,alias,op['payload_sha256'])
                except ValueError as e:return {'rejected':str(e)}
            missing=result(obs,None);badzone=result(obs,{**zone,'verified':False});wrongzone=result(obs,{**zone,'observed_label':'London','end_observed_label':'London'})
            wrong=copy.deepcopy(obs);wrong['fields']['start']='2026-11-03T13:00:00-05:00';badfield=result(wrong,zone)
            missing_recurrence=copy.deepcopy(obs);del missing_recurrence['fields']['recurrence']
            missing_meet=copy.deepcopy(obs);del missing_meet['fields']['hangout_link']
            good=result(obs,zone);saved=next(x for x in proofs if x['alias']==alias)['proof']
            assert missing=={'rejected':'missing_exact_record_timezone'}
            assert badzone=={'rejected':'timezone_not_verified'}
            assert wrongzone=={'rejected':'timezone_label_mismatch'}
            assert badfield=={'rejected':'returned_field_mismatch'}
            assert result(missing_recurrence,zone)=={'rejected':'missing_returned_field'}
            assert result(missing_meet,zone)=={'rejected':'missing_returned_field'}
            assert good==saved
            rows.append({'case':trace['state']['case'],'key':key,'alias':alias,'missing_zone_rejected':True,'unverified_zone_rejected':True,'wrong_zone_label_rejected':True,'wrong_start_rejected':True,'missing_recurrence_rejected':True,'missing_meet_field_rejected':True,'complete_evidence_proof_matches':True})
    claims=[{'case':t['state']['case'],'seq':e['seq'],'kind':e['kind'],'decision':e['result']['decision']} for t in original for e in t['events'] if e.get('result',{}).get('completion') is True]
    return {'description':'Local replay checks on saved evidence, not new production trials. Initial completion outputs lacked IANA zone proof. Later checks do not repair that earlier evidence time.','initial_affected_records':len(rows),'initial_incomplete_completion_outputs':len(claims),'initial_incomplete_claims':claims,'corrected_adapter_checks':len(rows)*7,'rows':rows,'passed':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=analyze(Path(__file__).resolve().parent);a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'passed':True,'checks':result['corrected_adapter_checks'],'initial_incomplete_completion_outputs':result['initial_incomplete_completion_outputs']}))
