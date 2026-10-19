"""Read-only source-link and field audit for private live evidence.

The output contains synthetic trial/evidence identifiers only. It checks the
complete available set, including saved wrong results. It does not edit data.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def rows(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def must(c,m):
    if not c:raise ValueError(m)


def cleanup_check(t,events):
    c=t['cleanup']
    must(c['status'] in ('trashed','not_created','no_saved_record_found'),'cleanup status unresolved or unknown')
    must(c['active_matches']==0 and bool(c['evidence_ids']),'cleanup zero evidence absent')
    for eid in c['evidence_ids']:must(eid in events,'cleanup evidence absent')
    strings=[events[eid].get('state','') for eid in c['evidence_ids']]
    if t['site']=='calendar':
        must(any(('No events found' in s or 'No results found' in s) and t['token'] in s and 'Searching for' not in s for s in strings),'Calendar exact-marker zero search not shown')
    else:
        observed=[events[eid] for eid in c['evidence_ids'] if events[eid].get('kind')=='cleanup_result']
        must(observed and all(x.get('active_matches')==0 for x in observed),'Notion cleanup count absent')
        must(any(t['token'] not in s and s for s in strings),'Notion active-absence snapshot absent')


def audit_trial(t, events, require_cleanup=False):
    out={'trial_id':t['trial_id'],'terminal_status':t['terminal_status'],'observation_checks':0,'cleanup_checks':0,'issues':[]}
    if t['terminal_status']!='valid':
        if t.get('cleanup',{}).get('status')!='unresolved':
            try:cleanup_check(t,events);out['cleanup_checks']=1
            except (KeyError,ValueError) as ex:out['issues'].append({'issue':'cleanup: '+str(ex)})
        elif require_cleanup:out['issues'].append({'issue':'cleanup unresolved'})
        return out
    seq=[t['baseline'],t['agent']]+[e['observation'] for e in t['later']]+[t['preundo'],t['final']]
    for o in seq:
        try:
            e=events[o['evidence_id']]
            for k in ('x','y','x_raw','y_raw','native_id','token','utc','identity_ok','contract_ok','reloaded'):
                must(e.get(k)==o.get(k),'saved row differs from evidence: '+k)
            source=e.get('source') or e.get('source_observation');must(source in events,'missing native state source')
            s=events[source].get('state','');must(bool(s),'empty source snapshot')
            must(t['native_id'] in events[source].get('url',''),'native source identity mismatch')
            must(t['token'] in s,'source marker absent')
            if t['site']=='notion':
                xpart=s.split('row "X":',1)[1].split('row "Y":',1)[0]
                m=re.search(r'button "([+-]?\d+)"',xpart);must(m is not None,'native X text missing')
                must(int(m.group(1))==o['x'],'native X differs')
                ypart=s.split('row "Y":',1)[1].split('button "Add a property"',1)[0]
                must('checkbox' in ypart,'native Y control missing')
                must(int('checkbox [checked]' in ypart)==o['y'],'native Y differs')
                must('empty page' in s,'body-empty evidence missing')
                must('moved this page to Trash' not in s,'saved read already trashed')
                c=o['contract'];must(all(c[k] is True for k in ('name_matches','body_empty','x_exact_integer','y_checkbox','no_property_editor','not_in_trash')),'Notion contract failed')
                must(c['schema_evidence']==['NU-00030','NU-00039'],'unexpected schema source')
            else:
                raw=o['raw'];must(raw==e['raw'],'Calendar raw read differs')
                must(raw['x_raw']==o['x_raw'],'Calendar description read mismatch')
                must(raw['title']==t['token'],'Calendar native title mismatch')
                must(raw['start']==raw['end']=='Oct 14, 2026','Calendar date mismatch')
                must(raw['all_day'] is True and 'checkbox "All day" [checked]' in s,'Calendar all-day not checked')
                must(raw['visibility']=='Private' and ('generic "Private"' in s or 'generic: Private' in s),'Calendar privacy mismatch')
                must(raw['recurrence']=='Does not repeat' and 'Does not repeat' in s,'Calendar recurrence mismatch')
                must(raw['guests']==raw['notifications']==raw['location']=='','Calendar nonempty side field')
                must(raw['conference_absent'] is True and 'Add Google Meet video conferencing' in s,'Calendar conference present')
                must(raw['y_raw']==o['y_raw'] and ('generic: '+o['y_raw']) in s,'Calendar availability differs')
                must(all(o['checks'].values()),'Calendar contract flag false')
                # Description text is absent from the accessibility snapshot.
                # Its evidence is the explicit visible-field innerText read.
            out['observation_checks']+=1
        except (KeyError,ValueError,IndexError,TypeError) as ex:
            out['issues'].append({'evidence_id':o.get('evidence_id'),'issue':str(ex)})
    if t['kind']=='core':
        try:
            d=events[t['decision_evidence_id']]
            must(d.get('decision',d.get('output'))==t['decision'],'decision row differs')
            must(d['utc']>=t['preundo']['utc'] and d['utc']<=t['final']['utc'],'decision time outside read/write interval')
        except (KeyError,ValueError) as ex:out['issues'].append({'issue':'decision: '+str(ex)})
    try:
        cleanup_check(t,events)
        out['cleanup_checks']=1
    except (KeyError,ValueError) as ex:out['issues'].append({'issue':'cleanup: '+str(ex)})
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--require-cleanup',action='store_true');args=ap.parse_args()
    results=[];sources=[];dup=[]
    for site in ('calendar','notion'):
        p=args.work/site;tp=p/'final_trials.jsonl' if (p/'final_trials.jsonl').exists() else p/'trials.jsonl';ts=rows(tp);es=rows(p/'actions.jsonl');sources.append({'site':site,'terminal_file':tp.name,'terminal_sha256':sha(tp),'original_trials_sha256':sha(p/'trials.jsonl'),'actions_sha256':sha(p/'actions.jsonl')})
        for t in ts:
            matches=[e for e in es if e.get('trial_id')==t['trial_id']]
            mapping={e['id']:e for e in matches};must(len(mapping)==len(matches),'duplicate evidence within a trial')
            results.append(audit_trial(t,mapping,args.require_cleanup))
        counts={}
        for e in es:counts[e['id']]=counts.get(e['id'],0)+1
        dup.extend({'site':site,'evidence_id':k,'uses':v,'resolution':'scope by trial ID; preflight is separate'} for k,v in counts.items() if v>1)
    total_issues=sum(len(r['issues']) for r in results)
    result={'status':'PASS' if not total_issues else 'FAIL','rows':results,'sources':sources,'observation_checks':sum(r['observation_checks'] for r in results),'cleanup_checks':sum(r['cleanup_checks'] for r in results),'issues':total_issues,'cleanup_required':args.require_cleanup,'cross_phase_id_reuse':dup,'limits':['Calendar X uses explicit visible Description innerText reads; the accessibility snapshot omits that text.','Structured/native-source checks do not prove native revisions or atomicity.','Only available terminal rows are checked; this receipt does not establish complete assignment coverage.']}
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'rows':len(results),'observation_checks':result['observation_checks'],'cleanup_checks':result['cleanup_checks'],'issues':[(r['trial_id'],r['issues']) for r in results if r['issues']]}))
    if total_issues:raise SystemExit(1)

if __name__=='__main__':main()
