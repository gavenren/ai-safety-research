#!/usr/bin/env python3
"""Independent numerical checks. This file does not import analyze.py."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import platform
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D = Decimal
PRECISION = 90
TOLERANCE = D('6e-29')
CHECKS = {}
MAX_ERROR = D(0)


def probabilities(m, s):
    """Binomial probabilities by recurrence from zero successes."""
    if s == 0:
        return [D(1)] + [D(0)] * m
    if s == 1:
        return [D(0)] * m + [D(1)]
    result = [(1-s)**m]
    for j in range(m):
        result.append(result[-1] * (m-j) * s / ((j+1)*(1-s)))
    return result


def tail(m, k, s):
    if k == 0:
        return D(1)
    # This complement route differs from the main direct upper-tail sum.
    return D(1) - sum(probabilities(m, s)[:k], D(0))


def cp_root(m, k, delta):
    if k == 0:
        return D(0), D(0)
    lo, hi = D(0), D(1)
    for _ in range(290):
        mid = (lo+hi)/2
        if tail(m, k, mid) < delta:
            lo = mid
        else:
            hi = mid
    return lo, hi


def length(p0, a, error):
    """Integer doubling and binary search, without logarithms."""
    if a == 0:
        return None
    base = 1-p0*a
    hi = 1
    while base**hi > error:
        hi *= 2
    lo = 0
    while hi-lo > 1:
        mid = (lo+hi)//2
        if base**mid <= error:
            hi = mid
        else:
            lo = mid
    assert base**hi <= error
    assert hi == 1 or base**(hi-1) > error
    return hi


def close(actual, expected, label, tolerance=TOLERANCE):
    global MAX_ERROR
    error = abs(D(actual)-expected)
    if tolerance == TOLERANCE:
        MAX_ERROR = max(MAX_ERROR, error)
    if error > tolerance:
        raise AssertionError(f'{label}: error {error} exceeds {tolerance}')


def exact_binomial(m, s):
    values = [Fraction(0)] * (m+1)
    for bits in itertools.product((0, 1), repeat=m):
        count = sum(bits)
        values[count] += s**count * (1-s)**(m-count)
    return values


def as_decimal(value):
    return D(value.numerator) / D(value.denominator)


def controls():
    cases = 0
    for m in range(9):
        for s in (Fraction(0), Fraction(1, 10), Fraction(1, 2), Fraction(9, 10), Fraction(1)):
            exact = exact_binomial(m, s)
            result = probabilities(m, as_decimal(s))
            for k in range(m+1):
                close(result[k], as_decimal(exact[k]), 'exact binomial control', D('1e-85'))
            close(sum(result), D(1), 'binomial normalization', D('1e-85'))
            cases += 1
    # Exhaustive control and target sequences; three synthetic branch policies.
    joint_cases = 0
    for m in (1, 2, 3):
        for s in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(1)):
            for p in (Fraction(0), Fraction(1, 4), Fraction(1)):
                for f in (Fraction(0), Fraction(1, 3)):
                    for ns in ([None] + [2]*m, list(range(1, m+2)), [None if k % 2 == 0 else 3 for k in range(m+1)]):
                        exact = Fraction(0)
                        q = p*s + (1-p)*f
                        for controls_bits in itertools.product((0, 1), repeat=m):
                            k = sum(controls_bits)
                            n = ns[k]
                            if n is None:
                                continue
                            cw = s**k * (1-s)**(m-k)
                            for target_bits in itertools.product((0, 1), repeat=n):
                                if sum(target_bits) == 0:
                                    exact += cw * (1-q)**n
                        weights = probabilities(m, as_decimal(s))
                        expected = sum((weights[k] * (1-as_decimal(q))**n for k,n in enumerate(ns) if n is not None), D(0))
                        close(expected, as_decimal(exact), 'joint exact enumeration', D('1e-84'))
                        joint_cases += 1
    CHECKS['binomial_exact_enumeration_cases'] = cases
    CHECKS['joint_exact_enumeration_cases'] = joint_cases


def read_csv(name):
    with (ROOT/name).open(newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    config = json.loads((ROOT/'config.json').read_text())
    manifest = json.loads((ROOT/'input_manifest.json').read_text())
    for name, wanted in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == wanted
    CHECKS['frozen_input_hashes'] = 'PASS'
    controls()
    delta, beta, alpha = map(D, (config['calibration_error'], config['target_error'], config['alpha']))
    null_limit = delta + (1-delta)*beta
    roots = {}
    root_checks = 0
    root_errors = []
    bounds = read_csv('results_bounds.csv')
    assert len(bounds) == sum(m+1 for m in config['calibration_sizes'])
    for row in bounds:
        m, k = int(row['m']), int(row['k'])
        lo, hi = cp_root(m, k, delta)
        roots[m,k] = (lo+hi)/2
        main_lo, main_hi = D(row['lower_lo']), D(row['lower_hi'])
        if k == 0:
            assert main_lo == main_hi == 0
            continue
        assert main_lo <= lo <= hi <= main_hi, (m, k, main_lo, lo, hi, main_hi)
        assert tail(m,k,main_lo) <= delta <= tail(m,k,main_hi)
        close(row['tail_at_lo'], tail(m,k,main_lo), 'saved lower tail', D('1e-66'))
        close(row['tail_at_hi'], tail(m,k,main_hi), 'saved upper tail', D('1e-66'))
        root_errors.append(abs(main_lo-roots[m,k]))
        root_checks += 1
    CHECKS['positive_CP_roots_and_brackets'] = root_checks
    CHECKS['largest_main_lower_root_error'] = str(max(root_errors))
    assert set(roots) == {(m,k) for m in config['calibration_sizes'] for k in range(m+1)}
    for m in config['calibration_sizes']:
        assert all(roots[m,k] < roots[m,k+1] for k in range(m))

    for m in config['calibration_sizes']:
        close(roots[m,1],1-((1-delta).ln()/m).exp(),'first root closed form',D('1e-85'))
        close(roots[m,m],(delta.ln()/m).exp(),'last root closed form',D('1e-85'))
    CHECKS['CP_endpoint_closed_forms'] = 6

    lengths = {}
    policies = {}
    minimum_gap = D(1)
    for ps in config['targets']:
        p0 = D(ps)
        n0 = length(p0,D(1),alpha)
        lengths[ps,'perfect_assumed'] = n0
        for ss in config['sensitivities']:
            lengths[ps,'known_sensitivity',ss] = length(p0,D(ss),alpha)
        for m in config['calibration_sizes']:
            for rule in ('point_estimate','lower_bound'):
                for k in range(m+1):
                    a = D(k)/m if rule == 'point_estimate' else roots[m,k]
                    b = alpha if rule == 'point_estimate' else beta
                    n = length(p0,a,b)
                    if n is not None:
                        minimum_gap = min(minimum_gap, b-(1-p0*a)**n)
                        if n > 1:
                            minimum_gap = min(minimum_gap, (1-p0*a)**(n-1)-b)
                    for capmult in ('none','20'):
                        cap = None if capmult == 'none' else 20*n0
                        active = n is not None and (cap is None or n <= cap)
                        policies[ps,m,rule,capmult,k] = (n,active,a,b,cap)
    saved_policies = read_csv('results_policy.csv')
    assert len(saved_policies) == len(policies)
    seen = set()
    for row in saved_policies:
        key = row['p0'],int(row['m']),row['rule'],row['cap_multiplier'],int(row['k'])
        assert key not in seen
        seen.add(key)
        n,active,a,b,cap = policies[key]
        assert row['required_n'] == ('' if n is None else str(n))
        assert row['launched'] == str(int(active))
        assert row['cap'] == ('' if cap is None else str(cap))
        assert D(row['target_error']) == b
        close(row['s_used'],a,'policy sensitivity',D('1e-66'))
        assert row['reason'] == ('launched' if active else 'zero_sensitivity' if n is None else 'over_cap')
    assert seen == set(policies)
    CHECKS['policy_rows_all_fields'] = len(saved_policies)
    CHECKS['minimum_integer_decision_margin'] = str(minimum_gap)
    assert minimum_gap > D('1e-50')

    coverage = []
    for m in config['calibration_sizes']:
        for ss in ['0']+config['sensitivities']:
            s = D(ss)
            weights = probabilities(m,s)
            close(sum(weights),D(1),'full binomial mass',D('1e-85'))
            bad = sum((w for k,w in enumerate(weights) if roots[m,k] > s),D(0))
            assert bad <= delta + D('1e-85')
            coverage.append(bad)
    CHECKS['CP_coverage_conditions'] = len(coverage)
    CHECKS['largest_CP_noncoverage_probability'] = str(max(coverage))

    rows = read_csv('results_grid.csv')
    assert len(rows) == 1296
    seen_grid = set()
    grid = {}
    for row in rows:
        ps,m,ss,ratio,rule,cm = row['p0'],int(row['m']),row['s'],row['p_multiplier'],row['rule'],row['cap_multiplier']
        key = ps,m,ss,ratio,rule,cm
        assert key not in seen_grid
        seen_grid.add(key)
        p0,s,p = D(ps),D(ss),D(ps)*D(ratio)
        assert D(row['p']) == p and D(row['f']) == 0
        cap = None if cm == 'none' else 20*lengths[ps,'perfect_assumed']
        assert row['cap'] == ('' if cap is None else str(cap))
        weights = probabilities(m,s)
        if rule in ('point_estimate','lower_bound'):
            branches = [policies[ps,m,rule,cm,k][:2] for k in range(m+1)]
        else:
            n = lengths[ps,rule] if rule == 'perfect_assumed' else lengths[ps,rule,ss]
            branches = [(n,n is not None and (cap is None or n <= cap))]*(m+1)
        accepted = launch = expected = D(0)
        maximum = 0
        for w,(n,active) in zip(weights,branches):
            if active:
                accepted += w*(1-p*s)**n
                launch += w
                expected += w*n
                if w > 0:
                    maximum = max(maximum,n)
        close(row['acceptance_probability'],accepted,'acceptance mixture')
        close(row['launch_probability'],launch,'launch mixture')
        close(row['no_declaration_probability'],1-accepted,'no declaration')
        close(row['expected_target_count'],expected,'target workload')
        if launch:
            close(row['conditional_target_count'],expected/launch,'conditional workload')
        else:
            assert row['conditional_target_count'] == ''
        assert int(row['max_target_count']) == maximum
        assert 0 <= accepted <= launch <= 1+D('1e-85')
        if p >= p0 and rule == 'lower_bound':
            assert accepted <= null_limit
        if p >= p0 and rule == 'known_sensitivity':
            assert accepted <= alpha
        grid[key] = (accepted,launch,expected,maximum)
    wanted_grid = set(itertools.product(config['targets'],config['calibration_sizes'],config['sensitivities'],config['failure_rate_multipliers'],config['rules'],('none','20')))
    assert seen_grid == wanted_grid
    CHECKS['grid_rows_all_fields'] = len(rows)
    nesting = 0
    for ps,m,ss,ratio,rule in itertools.product(config['targets'],config['calibration_sizes'],config['sensitivities'],config['failure_rate_multipliers'],config['rules']):
        uncapped = grid[ps,m,ss,ratio,rule,'none']
        capped = grid[ps,m,ss,ratio,rule,'20']
        assert all(x <= y + D('1e-80') for x,y in zip(capped,uncapped))
        nesting += 1
    for ps,m,ss,rule,cm in itertools.product(config['targets'],config['calibration_sizes'],config['sensitivities'],config['rules'],('none','20')):
        values = [grid[ps,m,ss,ratio,rule,cm] for ratio in config['failure_rate_multipliers']]
        assert values[0][0] >= values[1][0] >= values[2][0]
        assert values[0][1:] == values[1][1:] == values[2][1:]
    CHECKS['cap_event_inclusion_cases'] = nesting
    CHECKS['failure_rate_monotonicity_groups'] = 432

    # Endpoint and false-positive controls use actual CP policies.
    endpoint_cases = 0
    for ps,m,rule,cm in itertools.product(config['targets'],config['calibration_sizes'],('point_estimate','lower_bound'),('none','20')):
        for s in (D(0),D(1)):
            weights = probabilities(m,s)
            for p in (D(0),D(1)):
                base = None
                for f in (D(0),D('.01'),D('.3'),D(1)):
                    q = p*s+(1-p)*f
                    value = sum((weights[k]*(1-q)**n for k in range(m+1) for n,active,*_ in [policies[ps,m,rule,cm,k]] if active),D(0))
                    if f == 0:
                        base = value
                        if s == 0:
                            assert value == 0
                        if p == 0:
                            launched = sum((weights[k] for k in range(m+1) if policies[ps,m,rule,cm,k][1]),D(0))
                            assert value == launched
                        if s == 1 and p == 1:
                            assert value == 0
                    assert value <= base
                    endpoint_cases += 1
    CHECKS['endpoint_and_nonzero_false_positive_cases'] = endpoint_cases

    summary = json.loads((ROOT/'results_summary.json').read_text())
    assert summary['grid_rows'] == 1296 and summary['bounds_rows'] == len(bounds) and summary['policy_rows'] == len(saved_policies)
    assert D(summary['unconditional_corrected_bound']) == null_limit
    assert summary['input_manifest_sha256'] == hashlib.sha256((ROOT/'input_manifest.json').read_bytes()).hexdigest()
    boundary = [r for r in rows if r['p_multiplier'] == '1']
    for item in summary['boundary_counts']:
        cell = [r for r in boundary if r['rule'] == item['rule'] and r['cap_multiplier'] == str(item['cap_multiplier'])]
        assert len(cell) == item['cases'] == 54
        assert sum(D(r['acceptance_probability']) > alpha for r in cell) == item['above_005']
        assert sum(D(r['acceptance_probability']) == alpha for r in cell) == item['equal_005']
        mx = max(D(r['acceptance_probability']) for r in cell)
        close(item['maximum_probability'],mx,'summary maximum')
        ties = [{key:int(r[key]) if key == 'm' else r[key] for key in ('p0','m','s')} for r in cell if D(r['acceptance_probability']) == mx]
        assert ties == item['maximum_ties_at_saved_precision']
        assert any(all(str(item['maximum_at'][key]) == r[key] for key in ('p0','m','s')) and D(r['acceptance_probability']) == mx for r in cell)
    assert len(summary['planned_example']) == 24
    for example in summary['planned_example']:
        assert any(all(str(value) == row[key] if value is not None else row[key] == '' for key,value in example.items()) for row in rows)
    CHECKS['summary_counts_maxima_and_example'] = 'PASS'
    CHECKS['all_corrected_null_rows_below_bound'] = 216
    CHECKS['all_oracle_null_rows_below_005'] = 216
    result = {'status':'PASS','python':platform.python_version(),'precision':PRECISION,'root_bisections':290,'saved_output_tolerance':str(TOLERANCE),'largest_saved_output_error':str(MAX_ERROR),'method':'Binomial probability recurrence and lower-CDF complement; 90-digit bisection; integer doubling and binary search. No import of analyze.py.','checks':CHECKS,'unconditional_null_limit':str(null_limit)}
    (ROOT/'validation_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    with localcontext() as context:
        context.prec = PRECISION
        main()
