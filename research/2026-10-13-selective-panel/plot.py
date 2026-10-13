"""Draw the three measured policies; do not interpolate a risk curve."""
import csv
import json
import platform
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parent
rows = list(csv.DictReader((root/'results_groups.csv').open()))
names = {'aegis':'Aegis','beavertails':'BeaverTails','ethics':'Ethics','toxicchat':'ToxiChat',
         'toxigen':'ToxiGen','wildguard':'WildGuard','xstest':'XSTest'}
fig, axes = plt.subplots(2,4,figsize=(13,7),sharex=True,sharey=True)
colors = {3:'#64748b',4:'#167d9a',5:'#c05a17'}
markers = {3:'o',4:'s',5:'^'}
for ax,(dataset,title) in zip(axes.flat,names.items()):
    for t in (3,4,5):
        r = next(r for r in rows if r['dataset']==dataset and r['reference']=='all' and int(r['threshold'])==t)
        ax.scatter(100*float(r['coverage']),100*float(r['selective_error']),color=colors[t],marker=markers[t],s=75,zorder=3)
        ax.annotate(str(t),(100*float(r['coverage']),100*float(r['selective_error'])),xytext=(-10,7),textcoords='offset points',fontsize=9)
    ax.set(title=title,xlim=(0,108),ylim=(0,33))
    ax.grid(alpha=.18)
    ax.set_xlabel('Accepted items / all items (%)')
    ax.set_ylabel('Wrong / accepted items (%)')
axes.flat[-1].axis('off')
axes.flat[-1].text(.02,.88,'Agreement threshold\n\n3: accept every majority\n4: at least four agree\n5: all five agree\n\nEach point is one measured policy.\nNo connecting curve is implied.\nSaved labels; no reviewer outcomes.',va='top',fontsize=10,linespacing=1.55,transform=axes.flat[-1].transAxes)
fig.suptitle('Agreement rules change accepted error and coverage',fontsize=16,y=.98)
fig.text(.5,.018,'Class-specific counts and errors are in the report. These points do not measure harm during use.',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.05,1,.94))
fig.savefig(root/'figure_routing.png',dpi=160,metadata={'Software':'Matplotlib'})
plt.close(fig)
(root/'plot_environment.json').write_text(json.dumps({'python':platform.python_version(),'matplotlib':matplotlib.__version__,'numpy':np.__version__},indent=2,sort_keys=True)+'\n')
print('Saved figure_routing.png from the 21 primary result rows.')
