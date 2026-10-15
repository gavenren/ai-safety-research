"""Draw the selected calibration comparison from saved results."""
from pathlib import Path
import csv,json,platform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parent
rows=list(csv.DictReader((R/'results_grid.csv').open()))
series=[('known_sensitivity','none','Known sensitivity','#697a89','o'),('point_estimate','none','Point estimate; no cap','#bd5538','s'),('lower_bound','none','Lower bound; no cap','#24769a','^'),('lower_bound','20','Lower bound; cap','#4d8664','D')]
fig,axes=plt.subplots(1,3,figsize=(13.4,4.7))
for rule,cap,label,color,marker in series:
    base=[next(r for r in rows if r['p0']=='0.01' and r['s']=='0.1' and r['m']==str(m) and r['p_multiplier']=='1' and r['rule']==rule and r['cap_multiplier']==cap) for m in [5,20,100]]
    alt=[next(r for r in rows if r['p0']=='0.01' and r['s']=='0.1' and r['m']==str(m) and r['p_multiplier']=='0.5' and r['rule']==rule and r['cap_multiplier']==cap) for m in [5,20,100]]
    vals=[[100*float(r['acceptance_probability']) for r in base],[100*float(r['acceptance_probability']) for r in alt],[float(r['expected_target_count']) for r in base]]
    for ax,v in zip(axes,vals): ax.plot(range(3),v,label=label,color=color,marker=marker,linewidth=1.8,markersize=6)
axes[0].axhline(5,color='#333333',linestyle=':',linewidth=1,label='Chosen 5% limit')
axes[0].set(title='False declaration at p = 1%',ylabel='Probability (%)',ylim=(0,12.3))
axes[1].set(title='True declaration at p = 0.5%',ylabel='Probability (%)',ylim=(0,24.5))
axes[2].set(title='Planned target workload',ylabel='Expected number of tests')
axes[2].set_ylim(bottom=0)
for ax in axes:
    ax.set_xticks(range(3),['5','20','100']);ax.set_xlabel('Known-positive controls (m)');ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
fig.suptitle('Finite calibration: error control can require many tests',fontsize=15,y=.98)
fig.text(.5,.905,'Synthetic model: target p0 = 1%; detector sensitivity = 10%; cap = 5,980 target tests',ha='center',fontsize=10)
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,ncol=3,loc='lower center',bbox_to_anchor=(.5,.025),frameon=False,fontsize=9)
fig.text(.5,.005,'Points are the three saved designs. Lines only join these points. Workload includes skipped batches as zero.',ha='center',fontsize=8.5)
fig.subplots_adjust(left=.065,right=.985,top=.79,bottom=.28,wspace=.32)
fig.savefig(R/'figure_calibration.png',dpi=180,metadata={'Software':'Matplotlib'})
(R/'plot_environment.json').write_text(json.dumps({'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__,'backend':matplotlib.get_backend(),'figure':'figure_calibration.png'},indent=2)+'\n')
print('Saved figure_calibration.png and plot_environment.json')
