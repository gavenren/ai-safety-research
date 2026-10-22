"""Independent AI review checks; no hardware or cryptography tested."""
import hashlib
import itertools
import json
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PAPER = 'report.md' if (ROOT/'report.md').exists() else 'technical.md'
INPUTS = [PAPER, 'technical_plan.md', 'technical_simulation.py', 'technical_results.json']
hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS}

# Execute an isolated copy; never overwrite the author's evidence.
rerun_dir = HERE/'technical_rerun'
rerun_dir.mkdir(exist_ok=True)
shutil.copy2(ROOT/'technical_simulation.py', rerun_dir/'technical_simulation.py')
proc = subprocess.run([sys.executable, str(rerun_dir/'technical_simulation.py')], capture_output=True, text=True, check=True)
saved = json.loads((ROOT/'technical_results.json').read_text())
rerun = json.loads((rerun_dir/'technical_results.json').read_text())
assert saved == rerun

# Independent calculation uses complementary sums, not the author's function.
capacities = [400]*20 + [100]*80
truth = [c*(10+(17*d+13*t)%81)//100 for d,c in enumerate(capacities) for t in range(100)]
measured = [x+(d+t)%3-1 for (d,t),x in zip(itertools.product(range(100),range(100)), truth)]
caps = [c for c in capacities for _ in range(100)]
all_i = set(range(10000))
cases = {'complete': set(), 'random_5pct': set(random.Random(20261022).sample(range(10000),500)),
         'high_capacity_5pct': set(range(500)),
         'high_activity_5pct': set(sorted(range(10000), key=lambda i:(-truth[i],i))[:500]),
         'all_high_capacity_20pct': set(range(2000))}
for name,gaps in cases.items():
    observed = sum(measured)-sum(measured[i] for i in gaps)
    n_known = len(all_i-gaps)
    lo = observed-2*n_known
    hi = observed+2*n_known+sum(caps[i] for i in gaps)
    actual = saved['scenarios'][name]
    assert (lo,hi,observed,sum(truth)) == (actual['lower'],actual['upper'],actual['observed'],actual['truth'])
    assert lo <= sum(truth) <= hi

# Independent finite enumeration checks clipping at zero/capacity, including
# negative reports and upper-overshoot reports that remain error-consistent.
interval_checks = 0
for cap in range(5):
    for x in range(cap+1):
        for eps in range(3):
            for y in range(-2,8):
                if abs(y-x) <= eps:
                    lo,hi = max(0,y-eps),min(cap,y+eps)
                    assert lo <= x <= hi
                    for external in range(3):
                        assert lo <= x+external <= hi+2
                    interval_checks += 1

report = {'reviewer':'separate AI agent; not human or external peer review',
          'reviewed_utc':datetime.now(timezone.utc).isoformat(), 'python':sys.version,
          'input_sha256':hashes, 'isolated_author_rerun_equal': True,
          'independently_recomputed_scenarios':5,
          'independent_clipped_interval_cases':interval_checks,
          'external_budget_values_per_case':3,
          'limitations':'No secure meter, attestation, receipt reconciliation, deployment, or adversarial security implementation exists in this simulation.'}
(HERE/'technical_check_results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
