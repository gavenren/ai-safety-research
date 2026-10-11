"""Plot the planned model summaries. No model inference is run."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent
s=json.loads((P/'results_summary.json').read_text())['by_model']
models=list(s); labels=['Llama 3.1 8B','Mistral 7B','OLMo 2 7B','Qwen 2.5 7B','Gemma 2 9B']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,(a,b)=plt.subplots(1,2,figsize=(12,4.6),gridspec_kw={'width_ratios':[1.4,1]})
y=np.arange(len(models))
for key,label,color,offset in [('raw_mae','Raw rate','#526777',-.19),('corrected_mae','Correction','#b54a44',0),('clipped_mae','Correction, limited to 0–100%','#007f7b',.19)]:
 a.scatter([s[m][key]*100 for m in models],y+offset,label=label,color=color,s=48)
a.set_yticks(y,labels);a.invert_yaxis();a.set_xscale('log');a.set_xticks([5,10,20,50,100,200],['5','10','20','50','100','200']);a.set_xlim(5,220)
a.set_xlabel('Mean absolute error (percentage points; log scale)');a.grid(axis='x',alpha=.2);a.set_title('A. Rate error across the planned mixtures',loc='left',fontweight='bold');a.legend(frameon=False,loc='lower right',fontsize=8)
b.barh(y,[s[m]['clipped_worse'] for m in models],color='#007f7b',height=.55)
b.set_yticks(y,labels);b.invert_yaxis();b.set_xlim(0,35);b.set_xticks([0,7,14,21,28,35]);b.set_xlabel('Cases worse than the raw rate (out of 35)');b.set_title('B. Failures after limiting the estimate',loc='left',fontweight='bold')
for i,m in enumerate(models): b.text(s[m]['clipped_worse']+.4,i,str(s[m]['clipped_worse']),va='center')
fig.suptitle('Correction does not transfer equally across the five saved judge runs',fontweight='bold',fontsize=14)
fig.text(.01,.015,'Fixed Safety-Flag records; seven held-out test sets × five assumed class shares per model. These are not deployment rates.',fontsize=9,color='#46515a')
fig.tight_layout(rect=(0,.06,1,.91));fig.savefig(P/'figure_transfer.png',dpi=180);print('Saved figure_transfer.png')
