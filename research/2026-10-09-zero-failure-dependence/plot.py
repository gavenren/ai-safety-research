"""Draw the pre-planned p=.01, rho=.1 comparison from saved results."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/'results_grid.csv').open()))
selected=[r for r in rows if float(r['p'])==.01 and float(r['rho'])==.1]
fig,ax=plt.subplots(figsize=(10,6),layout='constrained')
styles=[('zero_atom','Zero-atom distribution','#C35032','o'),('beta','Beta distribution','#27659A','s'),('one_atom','One-atom distribution','#248477','^')]
for model,label,color,marker in styles:
    r=[x for x in selected if x['model']==model]
    ax.plot(range(7),[100*float(x['zero_failure_probability']) for x in r],label=label,color=color,marker=marker,lw=2.2)
r=[x for x in selected if x['model']=='beta']
ax.plot(range(7),[100*float(x['effective_n_plugin_probability']) for x in r],label='Variance-size plug-in (approximation)',color='#777777',ls='--',lw=1.5)
ax.axhline(5,color='#333333',ls=':',lw=1.4,label='5% decision limit')
ax.set_xticks(range(7),['300 × 1','150 × 2','60 × 5','30 × 10','10 × 30','3 × 100','1 × 300'])
ax.set_xlabel('Independent groups × tests per group (300 total tests)',labelpad=10)
ax.set_ylabel('Probability of zero observed failures (%)')
ax.set_ylim(0,100)
ax.set_title('Equal failure rate and correlation do not fix zero-failure probability',loc='left',fontsize=14,pad=35)
ax.text(0,1.035,'Exact model calculation | Mean failure rate: 1% | Within-group correlation: 0.1',transform=ax.transAxes,fontsize=10,color='#555555')
ax.grid(axis='y',alpha=.22); ax.spines[['top','right']].set_visible(False)
ax.legend(loc='upper left',frameon=False,fontsize=9)
fig.savefig(ROOT/'figure_zero_failures.png',dpi=180,metadata={'Description':'Synthetic exact model comparison; no AI model was tested.'})
print('Saved figure_zero_failures.png')
