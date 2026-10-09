"""Independent checks with 60-digit decimal arithmetic. No third-party packages.

This file does not import analyze.py. Run it after analyze.py.
"""
import csv
from decimal import Decimal, getcontext
import hashlib
from itertools import product
from pathlib import Path
import platform

getcontext().prec = 60
D = Decimal
ROOT = Path(__file__).resolve().parent
N = 300
RATES = tuple(map(D, ('0.001', '0.01', '0.05')))
RHOS = tuple(map(D, ('0', '0.01', '0.1', '0.5')))
REPEATS = (1, 2, 5, 10, 30, 100, 300)
MODELS = ('beta', 'zero_atom', 'one_atom')
TOL = D('5e-13')
CONTROL_TOL = D('1e-55')


def close(actual, expected, tolerance=CONTROL_TOL):
    error = abs(actual - expected)
    if error > tolerance:
        raise AssertionError(f'{actual} != {expected}; error={error}')
    return error


def moments(p, rho, model):
    """Return the first two raw moments from each distribution definition."""
    if rho == 0:
        return p, p * p
    if rho == 1:
        return p, p
    if model == 'beta':
        c = (1 - rho) / rho
        a = p * c
        return a / c, a * (a + 1) / (c * (c + 1))
    if model == 'zero_atom':
        high = p + rho * (1 - p)
        weight = p / high
        return weight * high, weight * high ** 2
    low = p * (1 - rho)
    weight = (p - low) / (1 - low)
    return (1 - weight) * low + weight, (1 - weight) * low ** 2 + weight


def group_zero(p, rho, m, model):
    """Direct mixture expectations, without logarithms used by analyze.py."""
    if p == 0:
        return D(1)
    if p == 1:
        return D(0)
    if rho == 0:
        return (1 - p) ** m
    if rho == 1:
        return 1 - p
    if model == 'beta':
        c = (1 - rho) / rho
        b = (1 - p) * c
        answer = D(1)
        for j in range(m):
            answer *= (b + j) / (c + j)
        return answer
    if model == 'zero_atom':
        high = p + rho * (1 - p)
        weight = p / high
        return (1 - weight) + weight * (1 - high) ** m
    low = p * (1 - rho)
    weight = (p - low) / (1 - low)
    return (1 - weight) * (1 - low) ** m


def probability(p, rho, m, model):
    return group_zero(p, rho, m, model) ** (N // m)


def boundary(rho, m, model):
    low, high = D(0), D(1)
    for _ in range(210):
        mid = (low + high) / 2
        if probability(mid, rho, m, model) > D('0.05'):
            low = mid
        else:
            high = mid
    return (low + high) / 2


def main():
    print(f'Independent validation. Python {platform.python_version()}.')
    print('Decimal precision: 60 digits. No import from analyze.py.')
    print(f'Published result tolerance: {TOL}. Algebra control tolerance: {CONTROL_TOL}.')
    for name in ('analysis_plan.md', 'analyze.py', 'results_grid.csv', 'results_boundaries.csv'):
        print(f'SHA256 {name}: {hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}')
    rows = list(csv.DictReader((ROOT / 'results_grid.csv').open()))
    expected_keys = set(product(RATES, RHOS, REPEATS, MODELS))
    seen = set()
    max_p_error = D(0)
    max_other_error = D(0)
    for row in rows:
        p, rho = D(row['p']), D(row['rho'])
        m, model = int(row['repeats']), row['model']
        key = (p, rho, m, model)
        assert key in expected_keys and key not in seen, key
        seen.add(key)
        assert int(row['groups']) == N // m
        actual = probability(p, rho, m, model)
        assert 0 <= actual <= 1
        max_p_error = max(max_p_error, close(D(row['zero_failure_probability']), actual, TOL))
        size = D(N) / (1 + (m - 1) * rho)
        for column, value in (
            ('independent_probability', (1 - p) ** N),
            ('variance_effective_n', size),
            ('effective_n_plugin_probability', ((1 - p).ln() * size).exp()),
        ):
            max_other_error = max(max_other_error, close(D(row[column]), value, TOL))
    assert seen == expected_keys and len(rows) == 252
    print(f'PASS: all 252 grid rows. Maximum P0 error: {max_p_error}.')
    print(f'PASS: all baseline, variance size, and plug-in values. Maximum error: {max_other_error}.')

    rows = list(csv.DictReader((ROOT / 'results_boundaries.csv').open()))
    expected_keys = set(product(RHOS, REPEATS, MODELS))
    seen = set()
    max_boundary_error = D(0)
    max_boundary_residual = D(0)
    for row in rows:
        rho, m, model = D(row['rho']), int(row['repeats']), row['model']
        key = (rho, m, model)
        assert key in expected_keys and key not in seen, key
        seen.add(key)
        assert int(row['groups']) == N // m
        root = boundary(rho, m, model)
        close(probability(root, rho, m, model), D('0.05'))
        published_root = D(row['p_boundary'])
        max_boundary_error = max(max_boundary_error, close(published_root, root, TOL))
        at_root = probability(published_root, rho, m, model)
        max_boundary_residual = max(max_boundary_residual, close(at_root, D('0.05'), TOL))
        close(D(row['probability_at_boundary']), at_root, TOL)
        target = probability(D('0.01'), rho, m, model)
        close(D(row['probability_at_target']), target, TOL)
        assert row['target_false_clearance_above_5pct'] == str(target > D('0.05'))
    assert seen == expected_keys and len(rows) == 84
    print(f'PASS: all 84 boundaries. Maximum root error: {max_boundary_error}.')
    print(f'PASS: boundary values and flags. Maximum published-root residual: {max_boundary_residual}.')

    controls = 0
    for p, rho, model in product(RATES, RHOS + (D(1),), MODELS):
        mean, second = moments(p, rho, model)
        close(mean, p)
        close(second, p * p + rho * p * (1 - p))
        close((second - mean * mean) / (p * (1 - p)), rho)
        close(group_zero(p, rho, 1, model), 1 - p)
        close(group_zero(p, rho, 2, model), (1 - p) ** 2 + rho * p * (1 - p))
        controls += 5
    for p, m, model in product(RATES, REPEATS, MODELS):
        close(probability(p, D(0), m, model), (1 - p) ** N)
        close(probability(p, D(1), m, model), (1 - p) ** (N // m))
        close(probability(D(0), D('0.1'), m, model), D(1))
        close(probability(D(1), D('0.1'), m, model), D(0))
        controls += 4
    # For m=3, the two atom models have different third moments in the interior.
    for p, rho in product(RATES, RHOS[1:]):
        gap = group_zero(p, rho, 3, 'zero_atom') - group_zero(p, rho, 3, 'one_atom')
        close(gap, rho * (1 - rho) * p * (1 - p))
        controls += 1
    print(f'PASS: {controls} moment, correlation, small-group, and limit controls.')
    count = 0
    for rho, m, model in product(RHOS + (D(1),), REPEATS, MODELS):
        values = [probability(D(i) / 100, rho, m, model) for i in range(101)]
        assert all(a > b for a, b in zip(values, values[1:]))
        count += 100
    print(f'PASS: {count} strict monotonicity comparisons. The proof is separate.')
    print('PASS: all independent validation checks.')


if __name__ == '__main__':
    main()
