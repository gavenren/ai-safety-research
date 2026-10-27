"""Independent prefix specification. No main implementation is imported.

The drop-rule total is final_value + the sum of values immediately before
strict decreases. This closed prefix expression differs from the main planned
incremental update. All record ordering is reconstructed from the input prefix.
"""
import itertools,json
from collections import defaultdict
from pathlib import Path

RULES=('GlobalMax','ArrivalDrop','SourceOrderDrop','EpochLast','EpochMax')
SOURCE=('P0','T0','P1','T1')
GROUPS={'base':('P0','T0','P1','T1'),'repeat_T0':('P0','T0','T0','P1','T1'),'repeat_T1':('P0','T0','P1','T1','T1')}

def values(p0,z0,p1,z1):
    assert 0<=p0<=z0<=2 and 0<=p1<=z1<=2
    return dict(zip(SOURCE,(p0,z0,p1,z1)))

def first_occurrences(prefix):
    return tuple(item for i,item in enumerate(prefix) if item not in prefix[:i])

def drop_total(sequence):
    return sequence[-1]+sum(a for a,b in zip(sequence,sequence[1:]) if b<a) if sequence else 0

def prefix_state(rule,point_values,prefix):
    unique=first_occurrences(tuple(prefix))
    per_epoch={epoch:tuple(r for r in unique if r.endswith(str(epoch))) for epoch in (0,1)}
    epoch_last={f'E{epoch}':point_values[rs[-1]] for epoch,rs in per_epoch.items() if rs}
    epoch_max={f'E{epoch}':max(point_values[r] for r in rs) for epoch,rs in per_epoch.items() if rs}
    source=tuple(r for r in SOURCE if r in unique)
    if rule=='GlobalMax':q=max((point_values[r] for r in unique),default=0)
    elif rule=='ArrivalDrop':q=drop_total(tuple(point_values[r] for r in unique))
    elif rule=='SourceOrderDrop':q=drop_total(tuple(point_values[r] for r in source))
    elif rule=='EpochLast':q=sum(epoch_last.values())
    elif rule=='EpochMax':q=sum(epoch_max.values())
    else:raise ValueError(rule)
    return {'q':q,'seen':tuple(sorted(unique)),'arrival':unique,
            'last_arrival':point_values[unique[-1]] if unique else 0,
            'source_order':source,'epoch_last':epoch_last,'epoch_max':epoch_max}

def branch(q,total,capacity,demand,closed=True):
    admit=bool(closed and capacity-q>=demand)
    actual=total+(demand if admit else 0)
    return {'C':capacity,'b':demand,'admitted':admit,'actual_use':actual,
            'excess':max(0,actual-capacity),'feasible_refusal':not admit and total+demand<=capacity,
            'local_balance':capacity-q-(demand if admit else 0)}

def all_branches(q,total,closed=True):
    return [branch(q,total,total+extra,demand,closed) for extra in range(3) for demand in (1,2)]

def history(p0,z0,p1,z1,order,rule,closed=True):
    point_values=values(p0,z0,p1,z1)
    states=[prefix_state(rule,point_values,order[:i]) for i in range(len(order)+1)]
    duplicate=[r in order[:i] for i,r in enumerate(order)]
    total=z0+z1;q=states[-1]['q']
    return {'states':states,'duplicate':duplicate,'final_error':q-total,'decisions':all_branches(q,total,closed)}

def enumerate_inputs():
    pairs=[(p,z) for z in range(3) for p in range(z+1)]
    for (p0,z0),(p1,z1) in itertools.product(pairs,repeat=2):
        for group,multiset in GROUPS.items():
            for order in sorted(set(itertools.permutations(multiset))):
                yield {'p0':p0,'z0':z0,'p1':p1,'z1':z1,'group':group,'order':order}

def summarize():
    result={r:defaultdict(int) for r in RULES}
    for case in enumerate_inputs():
        v={k:case[k] for k in ('p0','z0','p1','z1','order')}
        for rule in RULES:
            h=history(**v,rule=rule);s=result[rule];error=h['final_error']
            s['histories']+=1;s['exact']+=error==0;s['undercount']+=error<0;s['overcount']+=error>0
            for d in h['decisions']:
                s['decisions']+=1;s['admitted']+=d['admitted'];s['excess_decisions']+=d['excess']>0
                s['excess_units']+=d['excess'];s['feasible_refusals']+=d['feasible_refusal'];s['local_deficits']+=d['local_balance']<0
            if rule=='SourceOrderDrop':
                expected_q=case['z0']+case['z1'] if case['p1']<case['z0'] else case['z1']
                assert h['states'][-1]['q']==expected_q
            if rule=='GlobalMax':assert h['states'][-1]['q']==max(case['z0'],case['z1'])
            if rule=='EpochMax':assert error==0
    return {k:dict(v) for k,v in result.items()}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    args.out.write_text(json.dumps(summarize(),indent=2,sort_keys=True)+'\n')
