#!/usr/bin/env python3
"""Finite pagination-claim study; no website or provider requests."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

HERE=Path(__file__).resolve().parent
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def run_rule(pages, rule, budget, requested):
    matches=[]; seen_incomplete=False; consumed=0
    for page in pages:
        consumed+=1
        matches.extend(page['matches'])
        seen_incomplete |= page['incompleteSearch']
        has_more=page['next_token'] is not None
        size=len(page['matches'])+len(page['unrelated'])
        stop=(not has_more or
              rule=='empty_page' and size==0 or
              rule=='short_page' and size<requested or
              rule=='no_match_page' and not page['matches'] or
              rule=='bounded_checked' and consumed>=budget)
        if stop:
            checked=rule in ('token_and_coverage','bounded_checked')
            claim=not checked or not (has_more or seen_incomplete)
            return matches,consumed,claim,has_more,seen_incomplete
    raise AssertionError('Every finite stream must end.')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); out=args.out; out.mkdir(parents=True,exist_ok=True)
    if (out/'cases.jsonl').exists():
        raise SystemExit('Refuse to overwrite an existing run.')
    cfg=json.loads((HERE/'config.json').read_text()); frozen=json.loads((HERE/'freeze.json').read_text())['sha256']
    assert all(digest(HERE/n)==v for n,v in frozen.items())
    cpu=time.process_time(); wall=time.monotonic()
    write(out/'execution.json',{'status':'running','started_at_utc':datetime.now(timezone.utc).isoformat(),
        'python':sys.version,'platform':platform.platform(),'command':sys.argv,'input_sha256':frozen,
        'code_sha256':digest(HERE/'study.py'),'random_seed':None,'reason':'complete enumeration',
        'model_api_calls':0,'paid_compute':False})
    totals={r:Counter() for r in cfg['rules']}; bymode={}; control_rows={}; world_id=0
    names={((0,0),(1,0)):'empty_then_match',((1,0),(1,0)):'short_then_match',
           ((0,2),(1,0)):'unrelated_then_match',((0,0),):'empty_final',
           ((2,0),(2,0),(1,0)):'budget_with_more'}
    with (out/'worlds.jsonl').open('w') as worlds,(out/'cases.jsonl').open('w') as cases:
        for length in cfg['lengths']:
            for raw_stream in product(cfg['page_types'],repeat=length):
                stream=tuple(map(tuple,raw_stream))
                for mode in cfg['modes']:
                    incomplete=mode!='complete'; hidden=1 if mode=='incomplete_one_hidden' else 0
                    pages=[]
                    for index,(m,u) in enumerate(stream):
                        pages.append({'matches':[f'p{index}m{i}' for i in range(m)],
                            'unrelated':[f'p{index}u{i}' for i in range(u)],
                            'next_token':f'page-{index+1}' if index+1<length else None,
                            'incompleteSearch':incomplete})
                    truth=[v for p in pages for v in p['matches']]+(['hidden-match'] if hidden else [])
                    world={'world_id':world_id,'mode':mode,'page_counts':stream,'pages':pages,'truth':truth}
                    worlds.write(json.dumps(world,sort_keys=True,separators=(',',':'))+'\n')
                    for rule in cfg['rules']:
                        matches,read,claim,token,flag=run_rule(pages,rule,cfg['budget'],cfg['page_size'])
                        # Oracle reads the complete synthetic world, not the stop predicate.
                        unsupported=claim and (read<length or incomplete)
                        wrong=claim and set(matches)!=set(truth)
                        false_absence=claim and not matches and bool(truth)
                        metrics={'cases':1,'complete_claims':int(claim),'unknown':int(not claim),
                            'unsupported_completion':int(unsupported),'incorrect_complete_inventory':int(wrong),
                            'false_absence':int(false_absence),'missing_matches':len(set(truth)-set(matches)),
                            'pages_read':read,'supported_complete':int(claim and not unsupported)}
                        totals[rule].update(metrics); bymode.setdefault(mode,{r:Counter() for r in cfg['rules']})[rule].update(metrics)
                        row={'world_id':world_id,'mode':mode,'rule':rule,'returned_matches':matches,
                            'pages_read':read,'complete_claim':claim,'remaining_token':token,'seen_incomplete':flag,
                            'metrics':metrics}
                        cases.write(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n')
                        if stream in names:
                            control_rows.setdefault(names[stream]+'/'+mode,[]).append(row)
                        if rule in ('token_and_coverage','bounded_checked'):
                            assert not unsupported and not false_absence
                        if rule=='token_and_coverage' and mode=='complete':
                            assert claim and not wrong
                        assert token==(read<length) and flag==incomplete
                    world_id+=1
    assert world_id==4662
    assert all(totals[r]['unsupported_completion']>0 for r in cfg['rules'][:4])
    assert totals['bounded_checked']['unknown']>totals['token_and_coverage']['unknown']
    assert time.process_time()-cpu<60
    write(out/'summary.json',{'streams':1554,'worlds':world_id,'rule_cases':world_id*6,'rules':totals,'by_mode':bymode})
    write(out/'controls.json',control_rows)
    write(out/'checks.json',{'frozen_inputs':True,'complete_world_count':True,'truthful_tokens':True,
        'truthful_coverage_flags':True,'checked_rules_zero_false_claims':True,
        'unlimited_checked_finishes_all_complete_worlds':True,'four_baselines_have_counterexample':True,
        'failed_assertions':0,'unscored_cases':0})
    rec=json.loads((out/'execution.json').read_text())
    rec.update(status='complete',ended_at_utc=datetime.now(timezone.utc).isoformat(),
        cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-wall,
        output_sha256={n:digest(out/n) for n in ('worlds.jsonl','cases.jsonl','summary.json','controls.json','checks.json')})
    write(out/'execution.json',rec)
    print(json.dumps({'status':'complete','worlds':world_id,'rule_cases':world_id*6,'rules':totals},sort_keys=True))
if __name__=='__main__':
    main()
