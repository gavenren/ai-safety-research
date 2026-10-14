#!/usr/bin/env python3
"""Independent checks. Do not import analyze.py. Uses Decimal at 90 digits."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PRECISION = 90
TOLERANCE = Decimal('1e-28')
CONTROL_TOLERANCE = Decimal('1e-75')
CHECKS = {}
LARGEST_SAVED_ERROR = Decimal(0)


def decimal_fraction(value):
    return Decimal(value.numerator) / Decimal(value.denominator)


def coefficient(n, k, a):
    """[z**n] 1/(1-z+a*z**(k+1)); zero when n is negative."""
    if n < 0:
        return Decimal(0)
    terms = []
    power = Decimal(1)
    for j in range(n // (k + 1) + 1):
        terms.append(power * math.comb(n - k * j, j))
        power *= -a
    return sum(terms, Decimal(0))


def no_run(n, k, p):
    """Finite coefficient formula; no recursive use of earlier F values."""
    if k < 1 or n < 0 or not Decimal(0) <= p <= Decimal(1):
        raise ValueError('Invalid n, k, or p')
    if n < k:
        return Decimal(1)
    if p == 0:
        return Decimal(0)
    if p == 1:
        return Decimal(1)
    if k == 1:
        return p ** n
    qk = (1 - p) ** k
    a = p * qk
    return coefficient(n, k, a) - qk * coefficient(n - k, k, a)


def rolling(n, k, p):
    return 1 - no_run(n, k, p)


def state_probability(n, k, p):
    """Independent run-length state vector; small control cases only."""
    states = [Fraction(1)] + [Fraction(0)] * (k - 1)
    q = 1 - p
    accepted = Fraction(0)
    for _ in range(n):
        accepted += states[-1] * q
        states = [sum(states) * p] + [x * q for x in states[:-1]]
    assert accepted + sum(states) == 1
    return accepted


def brute_probability(n, k, p):
    """Enumerate every binary sequence, with its exact rational weight."""
    answer = Fraction(0)
    q = 1 - p
    for bits in itertools.product((0, 1), repeat=n):
        run = longest = 0
        successes = 0
        for bit in bits:
            successes += bit
            run = run + 1 if bit else 0
            longest = max(longest, run)
        if longest >= k:
            answer += q ** successes * p ** (n - successes)
    return answer


def close(actual, expected, label, tolerance=TOLERANCE):
    global LARGEST_SAVED_ERROR
    actual = Decimal(actual)
    error = abs(actual - expected)
    if tolerance == TOLERANCE:
        LARGEST_SAVED_ERROR = max(LARGEST_SAVED_ERROR, error)
    if error > tolerance:
        raise AssertionError(f'{label}: {actual} differs from {expected}')


def check_controls():
    cases = 0
    largest_error = Decimal(0)
    for n in range(11):
        for k in range(1, n + 2):
            for p in (Fraction(1, 10), Fraction(1, 2), Fraction(9, 10)):
                exact = brute_probability(n, k, p)
                state = state_probability(n, k, p)
                assert exact == state, (n, k, p)
                error = abs(rolling(n, k, decimal_fraction(p)) - decimal_fraction(exact))
                assert error < CONTROL_TOLERANCE, (n, k, p, error)
                largest_error = max(largest_error, error)
                cases += 1
    state_cases = 0
    for n in (12, 17, 24):
        for k in (1, 2, 3, 5, 8, n, n + 1):
            for p in (Fraction(1, 1000), Fraction(1, 20), Fraction(1, 2), Fraction(19, 20)):
                exact = state_probability(n, k, p)
                close(rolling(n, k, decimal_fraction(p)), decimal_fraction(exact),
                      f'state control {n,k,p}', CONTROL_TOLERANCE)
                state_cases += 1
    for k in (1, 2, 9):
        for n in (0, 1, 8, 9, 10, 30):
            assert rolling(n, k, Decimal(0)) == int(n >= k)
            assert rolling(n, k, Decimal(1)) == 0
    for p in (Decimal('0.001'), Decimal('0.01'), Decimal('0.05'), Decimal('0.5')):
        for k in (1, 2, 9, 59):
            close(rolling(k - 1, k, p), Decimal(0), 'H < k', CONTROL_TOLERANCE)
            close(rolling(k, k, p), (1 - p) ** k, 'H = k', CONTROL_TOLERANCE)
        for n in (0, 1, 10, 300):
            close(rolling(n, 1, p), 1 - p ** n, 'k = 1', CONTROL_TOLERANCE)
    CHECKS['small_controls'] = {
        'status': 'PASS', 'exhaustive_binary_cases': cases,
        'additional_exact_state_cases': state_cases,
        'maximum_absolute_coefficient_error': str(largest_error),
        'boundaries': ['p=0', 'p=1', 'H<k', 'H=k', 'k=1'],
        'state_probability_conservation': 'exact Fraction equality'
    }


def read_csv(name):
    with (ROOT / name).open(newline='') as stream:
        return list(csv.DictReader(stream))


def saved(row, key, expected):
    assert re.fullmatch(r'\d+\.\d{30}', row[key]), (key, row[key])
    close(row[key], expected, key)


def check_outputs():
    config = json.loads((ROOT / 'config.json').read_text())
    manifest = json.loads((ROOT / 'input_manifest.json').read_text())
    alpha = Decimal(config['alpha'])
    for name, key in [('analysis_plan.md', 'analysis_plan_sha256'),
                      ('config.json', 'config_sha256')]:
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == manifest[key]
    nominal = {}
    for ptext in config['p0']:
        p = Decimal(ptext)
        # A closed-form starting value, followed by direct integer checks.
        k = int((alpha.ln() / (1 - p).ln()).to_integral_value(rounding='ROUND_CEILING'))
        assert (1 - p) ** k <= alpha < (1 - p) ** (k - 1)
        nominal[ptext] = k
    cal_rows = read_csv('results_calibration.csv')
    expected_cal_keys = set(itertools.product(config['p0'], config['horizon_multipliers']))
    cal_map = {(row['p0'], int(row['horizon_multiplier'])): row for row in cal_rows}
    assert len(cal_map) == len(cal_rows) == 12 and set(cal_map) == expected_cal_keys
    calibrated = {}
    minimum_distance_to_alpha = Decimal(1)
    for key, row in cal_map.items():
        ptext, hm = key
        p = Decimal(ptext)
        k0 = nominal[ptext]
        horizon = hm * k0
        assert int(row['nominal_k']) == k0 and int(row['horizon']) == horizon
        # Linear search is independent of the main binary search. No k < k0
        # can pass: its first-window probability already exceeds alpha.
        k = k0
        while rolling(horizon, k, p) > alpha:
            k += 1
        ku = k0
        while (horizon - ku + 1) * (1 - p) ** ku > alpha:
            ku += 1
        assert int(row['exact_k']) == k and int(row['union_k']) == ku
        assert k0 <= k <= ku <= horizon
        actual = rolling(horizon, k, p)
        previous = rolling(horizon, k - 1, p)
        upper = (horizon - ku + 1) * (1 - p) ** ku
        upper_previous = (horizon - ku + 2) * (1 - p) ** (ku - 1)
        assert actual <= alpha < previous
        assert upper <= alpha < upper_previous
        saved(row, 'exact_probability', actual)
        saved(row, 'exact_predecessor_probability', previous)
        saved(row, 'union_bound', upper)
        saved(row, 'union_predecessor_bound', upper_previous)
        saved(row, 'rolling_at_union_k', rolling(horizon, ku, p))
        minimum_distance_to_alpha = min(minimum_distance_to_alpha,
            alpha - actual, previous - alpha, alpha - upper, upper_previous - alpha)
        calibrated[key] = (k, ku)
    rows = read_csv('results_grid.csv')
    expected_keys = set(itertools.product(config['p0'], config['horizon_multipliers'],
                                         config['rate_multipliers']))
    row_map = {(row['p0'], int(row['horizon_multiplier']), int(row['rate_multiplier'])):
               row for row in rows}
    assert len(rows) == len(row_map) == 36 and set(row_map) == expected_keys
    numerical = {}
    primary_conditions = primary_above = 0
    for key, row in row_map.items():
        ptext, hm, multiplier = key
        p = Decimal(ptext) * multiplier
        k0 = nominal[ptext]
        horizon = k0 * hm
        k, ku = calibrated[(ptext, hm)]
        assert Decimal(row['p']) == p
        assert int(row['nominal_k']) == k0 and int(row['horizon']) == horizon
        assert int(row['exact_k']) == k and int(row['union_k']) == ku
        single = (1 - p) ** k0
        separate = 1 - (1 - single) ** (horizon // k0)
        roll = rolling(horizon, k0, p)
        upper = min(Decimal(1), (horizon - k0 + 1) * single)
        corrected = rolling(horizon, k, p)
        at_union = rolling(horizon, ku, p)
        values = dict(single_probability=single, separate_probability=separate,
            rolling_probability=roll, window_union_bound=upper,
            corrected_rolling_probability=corrected, union_length_rolling_probability=at_union)
        for name, value in values.items():
            assert -CONTROL_TOLERANCE <= value <= 1 + CONTROL_TOLERANCE
            saved(row, name, value)
        assert single <= separate + CONTROL_TOLERANCE <= roll + 2 * CONTROL_TOLERANCE
        assert roll <= upper + CONTROL_TOLERANCE
        assert at_union <= corrected + CONTROL_TOLERANCE <= roll + 2 * CONTROL_TOLERANCE
        assert corrected <= alpha + CONTROL_TOLERANCE
        if multiplier == 1 and hm > 1:
            primary_conditions += 1
            primary_above += roll > alpha
        numerical[key] = values
    # Monotonicity uses unchanged k0 and p, or unchanged k0 and H.
    for ptext, hm in expected_cal_keys:
        ordered = [numerical[(ptext, hm, m)] for m in config['rate_multipliers']]
        for left, right in zip(ordered, ordered[1:]):
            for name in left:
                assert left[name] + CONTROL_TOLERANCE >= right[name], ('p monotonicity', name)
    for ptext in config['p0']:
        for m in config['rate_multipliers']:
            ordered = [numerical[(ptext, hm, m)] for hm in config['horizon_multipliers']]
            for left, right in zip(ordered, ordered[1:]):
                for name in ('single_probability', 'separate_probability',
                             'rolling_probability', 'window_union_bound'):
                    assert left[name] <= right[name] + CONTROL_TOLERANCE, ('H monotonicity', name)
        lengths = [calibrated[(ptext, hm)] for hm in config['horizon_multipliers']]
        for left, right in zip(lengths, lengths[1:]):
            assert left[0] <= right[0] and left[1] <= right[1]
    trajectory = read_csv('results_trajectory.csv')
    ptext = config['trajectory_p0']
    hm = config['trajectory_horizon_multiplier']
    p = Decimal(ptext)
    horizon = nominal[ptext] * hm
    lengths = {'nominal': nominal[ptext], 'corrected': calibrated[(ptext, hm)][0]}
    trajectory_map = {(row['rule'], int(row['t'])): row for row in trajectory}
    assert len(trajectory) == len(trajectory_map) == 2 * (horizon + 1)
    assert set(trajectory_map) == set(itertools.product(lengths, range(horizon + 1)))
    for rule, k in lengths.items():
        previous = Decimal(0)
        saved_hits = Decimal(0)
        for t in range(horizon + 1):
            row = trajectory_map[(rule, t)]
            assert Decimal(row['p']) == p and int(row['k']) == k
            current = rolling(t, k, p)
            # First-acceptance mass is the difference of two independently
            # evaluated coefficients, not the main first-hit recurrence.
            first = current - previous
            saved(row, 'accepted_by_t', current)
            saved(row, 'not_accepted_by_t', 1 - current)
            saved(row, 'first_acceptance', first)
            assert first >= -CONTROL_TOLERANCE
            close(Decimal(row['accepted_by_t']) + Decimal(row['not_accepted_by_t']),
                  Decimal(1), 'saved probability conservation')
            saved_hits += Decimal(row['first_acceptance'])
            previous = current
        assert abs(saved_hits + Decimal(row['not_accepted_by_t']) - 1) <= (
            Decimal(horizon + 2) * Decimal('5e-31'))
        expected_end = numerical[(ptext, hm, 1)][
            'rolling_probability' if rule == 'nominal' else 'corrected_rolling_probability']
        close(previous, expected_end, 'trajectory/grid endpoint', CONTROL_TOLERANCE)
    summary = json.loads((ROOT / 'results_summary.json').read_text())
    assert summary['grid_rows'] == len(rows)
    assert summary['calibration_rows'] == len(cal_rows)
    assert summary['trajectory_rows'] == len(trajectory)
    assert summary['primary_hypothesis_conditions'] == primary_conditions
    assert summary['primary_above_alpha'] == primary_above
    assert summary['plan_sha256'] == manifest['analysis_plan_sha256']
    assert summary['config_sha256'] == manifest['config_sha256']
    CHECKS['full_outputs'] = {
        'status': 'PASS', 'grid_rows': len(rows), 'calibration_rows': len(cal_rows),
        'trajectory_rows': len(trajectory),
        'minimum_search': 'Independent linear search, with every candidate and predecessor checked',
        'maximum_saved_probability_error': str(LARGEST_SAVED_ERROR),
        'minimum_calibration_distance_from_alpha': str(minimum_distance_to_alpha),
        'primary_conditions_above_alpha': f'{primary_above}/{primary_conditions}',
        'monotonicity': 'PASS for p, H at fixed k, and calibrated k across H',
        'nesting_and_union_bound': 'PASS', 'trajectory_conservation': 'PASS',
        'input_plan_and_config_hashes': 'PASS'
    }


def main():
    with localcontext() as context:
        context.prec = PRECISION
        check_controls()
        check_outputs()
        CHECKS['status'] = 'PASS'
        CHECKS['decimal_precision'] = PRECISION
        CHECKS['saved_probability_tolerance'] = str(TOLERANCE)
        (ROOT / 'validation_results.json').write_text(json.dumps(CHECKS, indent=2) + '\n')
        print(json.dumps(CHECKS, indent=2))


if __name__ == '__main__':
    main()
