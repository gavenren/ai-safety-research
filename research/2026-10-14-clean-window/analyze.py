"""Finite-horizon clean-run audit. Python standard library only."""
import csv
import hashlib
import json
import platform
import sys
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_path(p, k, horizon):
    """Probability of no clean k-run by t, plus probability of first hit at t."""
    qk = (1 - p) ** k
    survival = [Decimal(1)] * (horizon + 1)
    hits = [Decimal(0)] * (horizon + 1)
    if horizon >= k:
        hits[k] = qk
        survival[k] = 1 - qk
        for t in range(k + 1, horizon + 1):
            hits[t] = p * qk * survival[t - k - 1]
            survival[t] = survival[t - 1] - hits[t]
    return survival, hits


def rolling(p, k, horizon):
    return 1 - run_path(p, k, horizon)[0][-1]


def minimum_length(predicate, upper):
    lo, hi = 1, upper
    assert predicate(hi)
    while lo < hi:
        mid = (lo + hi) // 2
        if predicate(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def save_csv(name, rows):
    with (ROOT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    cfg = json.loads((ROOT / 'config.json').read_text())
    inputs = json.loads((ROOT / 'input_manifest.json').read_text())
    for filename, key in [('analysis_plan.md', 'analysis_plan_sha256'),
                          ('config.json', 'config_sha256')]:
        assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == inputs[key]
    fmt = lambda x: format(x, f'.{cfg["saved_decimal_places"]}f')
    grid, calibrated, trajectories = [], [], []
    with localcontext() as context:
        context.prec = cfg['decimal_precision']
        alpha = Decimal(cfg['alpha'])
        for p0text in cfg['p0']:
            p0 = Decimal(p0text)
            q0 = 1 - p0
            k0 = 1
            while q0 ** k0 > alpha:
                k0 += 1
            assert q0 ** (k0 - 1) > alpha >= q0 ** k0
            for hm in cfg['horizon_multipliers']:
                horizon = hm * k0
                kstar = minimum_length(lambda k: rolling(p0, k, horizon) <= alpha, horizon)
                ub = lambda k: (horizon - k + 1) * q0 ** k
                kunion = minimum_length(lambda k: ub(k) <= alpha, horizon)
                star_p = rolling(p0, kstar, horizon)
                star_prev = rolling(p0, kstar - 1, horizon) if kstar > 1 else Decimal(1)
                assert star_p <= alpha < star_prev
                assert kstar <= kunion
                calibrated.append(dict(p0=p0text, horizon_multiplier=hm, horizon=horizon,
                    nominal_k=k0, exact_k=kstar, union_k=kunion,
                    exact_probability=fmt(star_p), exact_predecessor_probability=fmt(star_prev),
                    union_bound=fmt(ub(kunion)),
                    union_predecessor_bound=fmt(ub(kunion-1)) if kunion>1 else '',
                    rolling_at_union_k=fmt(rolling(p0, kunion, horizon))))
                for multiplier in cfg['rate_multipliers']:
                    p = p0 * multiplier
                    clean = (1-p) ** k0
                    blocks = horizon // k0
                    separate = 1 - (1 - clean) ** blocks
                    roll = rolling(p, k0, horizon)
                    union = min(Decimal(1), (horizon-k0+1)*clean)
                    assert clean <= separate + Decimal('1e-50') <= roll + Decimal('2e-50')
                    assert roll <= union + Decimal('1e-50')
                    grid.append(dict(p0=p0text, rate_multiplier=multiplier, p=str(p),
                        horizon_multiplier=hm, horizon=horizon, nominal_k=k0,
                        single_probability=fmt(clean), separate_probability=fmt(separate),
                        rolling_probability=fmt(roll), window_union_bound=fmt(union),
                        exact_k=kstar, corrected_rolling_probability=fmt(rolling(p,kstar,horizon)),
                        union_k=kunion, union_length_rolling_probability=fmt(rolling(p,kunion,horizon))))
                if p0text == cfg['trajectory_p0'] and hm == cfg['trajectory_horizon_multiplier']:
                    for rule, k in [('nominal', k0), ('corrected', kstar)]:
                        survival, hits = run_path(p0,k,horizon)
                        for t,(s,h) in enumerate(zip(survival,hits)):
                            trajectories.append(dict(rule=rule,p=str(p0),k=k,t=t,
                                first_acceptance=fmt(h),accepted_by_t=fmt(1-s),not_accepted_by_t=fmt(s)))
        save_csv('results_grid.csv',grid)
        save_csv('results_calibration.csv',calibrated)
        save_csv('results_trajectory.csv',trajectories)
        primary = [r for r in grid if r['rate_multiplier']==1 and r['horizon_multiplier']>1]
        summary = {'study_type':'Exact synthetic probability model; no AI model tested',
            'grid_rows':len(grid),'calibration_rows':len(calibrated),'trajectory_rows':len(trajectories),
            'primary_hypothesis_conditions':len(primary),
            'primary_above_alpha':sum(Decimal(r['rolling_probability'])>alpha for r in primary),
            'plan_sha256':inputs['analysis_plan_sha256'],
            'config_sha256':inputs['config_sha256'],
            'example_p0_0p01_horizon_10':[r for r in grid if r['p0']=='0.01' and r['horizon_multiplier']==10],
            'example_calibration':[r for r in calibrated if r['p0']=='0.01' and r['horizon_multiplier']==10]}
        (ROOT/'results_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'environment.json').write_text(json.dumps({'python':platform.python_version(),
        'implementation':platform.python_implementation(),'dependencies':'standard library only',
        'decimal_precision':cfg['decimal_precision'],'platform':sys.platform,
        'random_sampling':False,'new_model_inference':False},indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__ == '__main__':
    main()
