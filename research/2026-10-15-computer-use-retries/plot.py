"""Plot saved model results. No calculation of experimental outcomes."""
import csv
import json
import platform
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

P = Path(__file__).resolve().parent
rows = {(r['schedule'],r['policy']): r for r in csv.DictReader((P/'results_summary.csv').open()) if r['suite']=='main' and r['server_mode']=='append'}
schedules = ['every1','every2','every4','backoff']
labels = ['Every tick','Every 2','Every 4','Backoff']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
fig, axes = plt.subplots(3,1,figsize=(8,10),layout='constrained')
x=np.arange(4)
for ax,(field,title,ylabel,policies) in zip(axes,[('duplicate_sum','A  Duplicate effects','Cases out of 256',['absence_retry','timeout8']),('clean_time_mean','B  Confirmation time','Mean ticks in 192 jointly clean cases',['bound12','terminal_retry']),('query_calls_mean','C  Observation cost','Mean queries across all 256 cases',['bound12','terminal_retry'])]):
    for off,pol,color,name in zip([-.19,.19],policies,['#ba5739','#1c7972'],['Absence retry','Timeout 8'] if field=='duplicate_sum' else ['Bound 12','Terminal status']):
        vals=[float(rows[(s,pol)][field]) for s in schedules]
        bars=ax.bar(x+off,vals,.36,color=color,label=name)
        ax.bar_label(bars,labels=[str(int(v)) if field=='duplicate_sum' else f'{v:.2f}' for v in vals],padding=3,fontsize=10)
    ax.set_xticks(x,labels,rotation=0)
    ax.set_title(title,loc='left',fontweight='bold')
    ax.set_ylabel(ylabel)
    ax.set_ylim(0,ax.get_ylim()[1]*1.45)
    ax.grid(axis='y',alpha=.18)
    ax.set_axisbelow(True)
    ax.legend(frameon=False,loc='upper right',fontsize=10)
fig.suptitle('Retry safety and observation cost in the main synthetic grid',fontsize=14,fontweight='bold')
fig.savefig(P/'figure_retry_cost.png',dpi=180)
plt.close(fig)
(P/'plot_environment.json').write_text(json.dumps({'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__,'backend':'Agg'},indent=2)+'\n')
print('Saved figure_retry_cost.png from results_summary.csv.')
