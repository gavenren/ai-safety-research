"""Draw class-specific gaps from saved point results and paired ranges."""
from pathlib import Path
import csv, json, platform
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
base=Path(__file__).resolve().parent
rows=list(csv.DictReader((base/'results_intervals.csv').open()))
labels={'aegis':'Aegis','beavertails':'BeaverTails','ethics':'Ethics','toxicchat':'ToxiChat','toxigen':'ToxiGen','wildguard':'WildGuard','xstest':'XSTest'}
fig,axes=plt.subplots(1,2,figsize=(11,5.5),sharey=True,layout='constrained')
for ref,ax,color,title in [(0,axes[0],'#176b87','False alarms'),(1,axes[1],'#8a4b2a','Missed flags')]:
 data=[r for r in rows if int(r['reference'])==ref]
 val=np.array([float(r['gap'])*100 for r in data]); low=np.array([float(r['lower'])*100 for r in data]); high=np.array([float(r['upper'])*100 for r in data]); y=np.arange(len(data))
 ax.errorbar(val,y,xerr=np.stack([val-low,high-val]),fmt='o',color=color,capsize=3,lw=1.5)
 ax.axvline(0,color='#555555',lw=1);ax.axvline(5,color='#bbbbbb',ls='--',lw=1)
 ax.set_title(title);ax.set_yticks(y,[labels[r['dataset']] for r in data]);ax.grid(axis='x',alpha=.18);ax.set_xlim(-2.5,17);ax.set_xlabel('Observed minus independent error (percentage points)')
axes[0].invert_yaxis()
fig.suptitle('Five-judge majority in this sample: gaps from the independent model',fontsize=14)
fig.supxlabel('Dots: fixed sample gaps. Bars: pointwise 2.5th–97.5th paired bootstrap percentiles.\nThese ranges do not include label error or unknown item clusters.',fontsize=10)
fig.savefig(base/'figure_gaps.png',dpi=170)
(base/'plot_environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},indent=2)+'\n')
print('Saved figure_gaps.png; matplotlib '+matplotlib.__version__)
