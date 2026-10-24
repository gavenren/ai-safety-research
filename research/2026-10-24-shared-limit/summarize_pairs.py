#!/usr/bin/env python3
"""Describe pre-specified paired metadata comparisons from saved SQL evidence."""
import argparse,gzip,json
from pathlib import Path

def key(r):
    s=r['input'];return (s['capacity'],tuple(s['demands']),tuple(r['policies']),tuple(x for x in s['schedule'] if x!='U'))

def main(folder):
    with gzip.open(folder/'traces.jsonl.gz','rt') as f:rows=[json.loads(line) for line in f]
    clean={key(r):r for r in rows if r['input']['u_position']==-1}
    stats={}; witnesses={}
    for r in rows:
        pair='/'.join(r['policies'])
        if r['scores']['breach'] and pair not in witnesses:witnesses[pair]=r
        if r['input']['u_position']<0:continue
        c=clean[key(r)]; t=stats.setdefault(pair,{'pairs':0,'job_decisions_changed':0,'accepted_jobs_delta':0,'breaches_removed':0,'breaches_added':0,'feasible_refusals_delta':0})
        t['pairs']+=1
        t['job_decisions_changed']+=sum(r['jobs'][i]['accepted']!=c['jobs'][i]['accepted'] for i in [0,1])
        t['accepted_jobs_delta']+=r['scores']['accepted_jobs']-c['scores']['accepted_jobs']
        t['breaches_removed']+=bool(c['scores']['breach'] and not r['scores']['breach'])
        t['breaches_added']+=bool(r['scores']['breach'] and not c['scores']['breach'])
        t['feasible_refusals_delta']+=r['scores']['feasible_refusals']-c['scores']['feasible_refusals']
    (folder/'paired_metadata.json').write_text(json.dumps(stats,indent=2,sort_keys=True)+'\n')
    (folder/'minimum_breaches.json').write_text(json.dumps(witnesses,indent=2,sort_keys=True)+'\n')
    print(json.dumps(stats,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('results',type=Path);a=p.parse_args();main(a.results)
