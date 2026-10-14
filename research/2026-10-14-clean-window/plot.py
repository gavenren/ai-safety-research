"""Draw saved model probabilities. No probability model is fitted here."""
import csv
import json
import platform
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
rows = list(csv.DictReader((ROOT/'results_grid.csv').open()))
fig, axes = plt.subplots(1,3,figsize=(12,4.3),sharey=True)
for ax,p0 in zip(axes,['0.001','0.01','0.05']):
    selected=[r for r in rows if r['p0']==p0 and r['rate_multiplier']=='1']
    x=[int(r['horizon_multiplier']) for r in selected]
    for col,label,color,marker in [
        ('single_probability','One planned window','#486581','o'),
        ('separate_probability','Any separate block','#bd6b17','s'),
        ('rolling_probability','Any rolling window','#b3373b','^'),
        ('corrected_rolling_probability','Corrected rolling length','#19856b','D')]:
        ax.plot(x,[float(r[col])*100 for r in selected],label=label,
                color=color,marker=marker,linewidth=1.8,markersize=5)
    ax.axhline(5,color='#666666',linestyle=':',linewidth=1)
    ax.set_title(f'True failure rate = target = {float(p0)*100:g}%\nOne-window length = {selected[0]["nominal_k"]}')
    ax.set_xticks(x)
    ax.set_xlabel('Maximum tests / one-window length')
    ax.grid(axis='y',alpha=.2)
    ax.set_ylim(0,90)
axes[0].set_ylabel('Probability of a false declaration (%)')
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.055),ncol=2,frameon=False)
fig.suptitle('Repeated clean windows change the chance of acceptance',fontsize=14)
fig.text(.5,.015,'Exact synthetic model; independent trials and unchanged system. Lines join the four saved designs.',ha='center',fontsize=9)
fig.subplots_adjust(top=.77,bottom=.29,wspace=.1,left=.065,right=.99)
fig.savefig(ROOT/'figure_windows.png',dpi=160,metadata={'Software':'Matplotlib'})
plt.close(fig)
(ROOT/'plot_environment.json').write_text(json.dumps({'python':platform.python_version(),
    'matplotlib':matplotlib.__version__,'numpy':np.__version__,'backend':'Agg'},indent=2)+'\n')
print('Saved figure_windows.png from results_grid.csv')
