#!/usr/bin/env python3
"""Summarize retained production extracts. No network or production write occurs."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from collections import Counter

CASES=('overlap','late','early','release','unknown','compete','invalid','contradiction')


def require(condition,message):
    if not condition:raise ValueError(message)


def load(p):return json.loads(p.read_text())


def csv_text(rows):
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);return f.getvalue()


def analyze(source):
    rows=[];request_rows=[];errors=[];totals=Counter();inputs={};all_aliases=set()
    for site in ('drive','calendar'):
        tp=source/f'{site}_traces.json';lp=source/f'{site}_record_ledger.json'
        inputs[tp.name]=hashlib.sha256(tp.read_bytes()).hexdigest();inputs[lp.name]=hashlib.sha256(lp.read_bytes()).hexdigest()
        traces=load(tp);ledger=load(lp);records=ledger['records']
        require(isinstance(traces,list) and len(traces)==8,'need eight traces per site')
        require({t['state']['case'] for t in traces}==set(CASES),'unexpected case set')
        require(ledger['site']==site,'wrong record ledger site')
        for r in records:
            require(r['case'] in CASES and r['role'] in ('A','B'),'unknown record scope')
            require(r['fields_verified'] is True,'record fields unresolved')
            require(r['alias'] not in all_aliases,'record alias repeated')
            all_aliases.add(r['alias'])
        for case in CASES:
            t=next(x for x in traces if x['state']['case']==case);s=t['state'];v=t['summary'];events=t['events']
            require(s['site']==site,'wrong trace site')
            require([e['seq'] for e in events]==list(range(1,len(events)+1)),'non-contiguous event log')
            require(events[0]['kind']=='init','missing initialization')
            cr=[r for r in records if r['case']==case];aa={r['alias'] for r in cr if r['role']=='A'};bb={r['alias'] for r in cr if r['role']=='B'}
            require(set(s['records'])==aa,'accepted known A set differs from observed A ledger')
            saved={o['record_alias'] for o in s['operations'].values() if o['status']=='saved'}
            require(saved==bb,'settled B set differs from observed B ledger')
            for r in cr:
                if r['role']=='B':
                    k=r.get('key',r.get('intent_key'));require(k in s['operations'],'B has no reserved intent')
                    require(s['operations'][k]['record_alias']==r['alias'],'B intent alias mismatch')
            permits=Counter();decisions=Counter();report_decisions=Counter();observed=Counter();bad_proof_claims=0;min_balance=v['available']
            for e in events:
                after=e['after'];min_balance=min(min_balance,after['available'])
                require(after['available']==s['capacity']-after['q']-after['h']-after['pending_B']-after['saved_B'],'exported balance mismatch')
                require(after['available']>=0,'negative balance in trace')
                if not after['terminal']:require(after['q']+after['h']==s['reservation'],'hold released before terminal')
                else:require(after['h']==0,'terminal residual hold')
                if e['kind']=='request':
                    d=e['result'];decisions[d['decision']]+=1
                    if d['dispatch']:
                        require(d['decision']=='permit','non-permit dispatch')
                        permits[e['input']['key']]+=1
                    request_rows.append({'site':site,'case':case,'seq':e['seq'],'key':e['input']['key'],'decision':d['decision'],'dispatch':d['dispatch'],'completion':d['completion'],'available_before':e['before']['available'],'available_after':after['available']})
                elif e['kind']=='report':report_decisions[e['result']['decision']]+=1
                elif e['kind']=='observe':
                    observed[e['result']['decision']]+=1
                    if e['input']['evidence'].get('fields_verified') is False and e['result']['completion']:bad_proof_claims+=1
            require(all(n==1 for n in permits.values()),'intent has multiple dispatch permits')
            require(set(permits)==set(s['operations']),'operation without exactly one permit')
            require(sum(permits.values())==len(bb),'permitted write unresolved or absent from record ledger')
            require(v['pending_B']==0,'pending B remains unresolved')
            require(bad_proof_claims==0,'bad fields caused completion claim')
            actual=len(aa)+len(bb);excess=max(0,actual-s['capacity'])
            # q is compared with observed A in every case. Only terminal cases call it final booking error.
            observed_error=s['q']-len(aa);final_error=observed_error if s['terminal'] else ''
            require(excess==0 and observed_error==0,'scope excess or observed A count error')
            row={'site':site,'case':case,'actual_A_records':len(aa),'actual_B_records':len(bb),'actual_total_records':actual,'capacity':s['capacity'],'excess_units':excess,'booked_A':s['q'],'residual_A_hold':s['h'],'terminal':s['terminal'],'quarantined':s['quarantined'],'observed_A_count_error':observed_error,'final_A_booking_error':final_error,'pending_B':v['pending_B'],'saved_B':v['saved_B'],'permits':sum(permits.values()),'requests':sum(decisions.values()),'limit_refused':decisions['limit_refused'],'quarantine_refused':decisions['quarantined'],'repeat_pending':decisions['pending'],'repeat_saved':decisions['already_saved'],'payload_conflict':decisions['payload_conflict'],'report_accepted':report_decisions['accepted'],'report_replay':report_decisions['replay'],'report_rejected':report_decisions['rejected'],'proof_rejected':observed['evidence_rejected'],'proof_saved':observed['saved'],'proof_replay_saved':observed['already_saved'],'explicit_false_field_flag_completion_claims':bad_proof_claims,'minimum_available':min_balance,'log_events':len(events)}
            rows.append(row)
            for k in ('actual_A_records','actual_B_records','actual_total_records','excess_units','permits','requests','limit_refused','quarantine_refused','repeat_pending','repeat_saved','payload_conflict','report_accepted','report_replay','report_rejected','proof_rejected','proof_saved','proof_replay_saved','explicit_false_field_flag_completion_claims','log_events'):totals[k]+=row[k]
    summary={'status':'accounting_checks_passed','field_proof_scope':'This calculation checks explicitly false fields_verified inputs only. It cannot detect an unsupported true assertion. The separate Calendar adapter audit records those failures.','cases':len(rows),'sites':2,'totals':dict(totals),'terminal_cases':sum(r['terminal'] for r in rows),'quarantined_cases':sum(r['quarantined'] for r in rows),'unresolved_B':sum(r['pending_B'] for r in rows),'known_A_error_cases':sum(r['observed_A_count_error']!=0 for r in rows),'terminal_final_A_error_cases':sum(r['final_A_booking_error'] not in ('',0) for r in rows),'excess_cases':sum(r['excess_units']>0 for r in rows),'input_sha256':inputs,'scope':'Selected controlled account cases. Counts are not population rates. Alias identity and field checks rely on retained provider evidence.'}
    return rows,request_rows,summary


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    rows,requests,summary=analyze(a.source);a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'guarded_rows.csv').write_text(csv_text(rows),newline='')
    (a.out/'guarded_requests.csv').write_text(csv_text(requests),newline='')
    (a.out/'guarded_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,sort_keys=True))

if __name__=='__main__':main()
