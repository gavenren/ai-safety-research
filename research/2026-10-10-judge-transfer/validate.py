#!/usr/bin/env python3
"""Independent check of the saved study. Uses the Python standard library.

The point calculations use exact fractions. Bootstrap interval checks use the
saved rates, rather than the analysis program. This does not validate the
source labels or the item-exchangeability assumption.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELS = sorted(["Llama-3.1-8B", "Mistral-7B", "OLMo-2-7B", "Qwen2.5-7B", "gemma-2-9b"])
SETS = sorted(["beavertails", "xstest", "ethics", "wildguard", "aegis", "toxicchat", "toxigen"])
SHARES = list(map(F, [".01", ".05", ".10", ".25", ".50"]))
TOLERANCE = 1e-10
checks = 0


def check(condition, message):
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


def close(observed, expected, name):
    check(math.isclose(float(observed), float(expected), rel_tol=TOLERANCE,
                       abs_tol=TOLERANCE),
          f"{name}: observed {observed}; expected {expected}")


def read_csv(name):
    with (ROOT / name).open(newline="") as file:
        return list(csv.DictReader(file))


def percentile(values, p):
    """Linear interpolation, equivalent to the NumPy default percentile."""
    values = sorted(values)
    position = (len(values) - 1) * p
    left = math.floor(position)
    weight = position - left
    return values[left] * (1 - weight) + values[min(left + 1, len(values) - 1)] * weight


rows = read_csv("data_labels.csv")
check(set(rows[0]) == {"dataset", "item_id", "model", "reference", "prediction"},
      "Minimal input schema")
check(len(rows) == 6990, "Input decision count")
check(sorted({r["model"] for r in rows}) == MODELS, "Model names")
check(sorted({r["dataset"] for r in rows}) == SETS, "Test-set names")
manifest = json.loads((ROOT / "source_manifest.json").read_text())
check(hashlib.sha256((ROOT / "data_labels.csv").read_bytes()).hexdigest()
      == manifest["minimal_data_sha256"], "Minimal data hash")

by_cell = defaultdict(Counter)
item_models = defaultdict(set)
item_labels = defaultdict(set)
keys_by_set = defaultdict(set)
seen = set()
for row in rows:
    dataset, item, model = row["dataset"], row["item_id"], row["model"]
    check(row["reference"] in {"0", "1"} and row["prediction"] in {"0", "1"},
          "Binary input labels")
    key = (dataset, item, model)
    check(key not in seen, "No repeated model-item key")
    seen.add(key)
    item_models[dataset, item].add(model)
    item_labels[dataset, item].add(row["reference"])
    keys_by_set[dataset].add((dataset, item))
    by_cell[dataset, model][int(row["reference"]), int(row["prediction"])] += 1
check(len(item_models) == 1398, "Unique common items")
for key in item_models:
    check(item_models[key] == set(MODELS), "Complete five-model pairing")
    check(len(item_labels[key]) == 1, "Reference labels match across models")
for target in SETS:
    source_keys = set().union(*(keys_by_set[d] for d in SETS if d != target))
    check(source_keys.isdisjoint(keys_by_set[target]), "Compound-key split separation")


def rates(counts):
    positive = counts[1, 0] + counts[1, 1]
    negative = counts[0, 0] + counts[0, 1]
    check(positive > 0 and negative > 0, "Both reference classes present")
    return F(counts[1, 1], positive), F(counts[0, 1], negative)


expected_confusion = {}
expected_grid = {}
singular = []
for target in SETS:
    for model in MODELS:
        counts = by_cell[target, model]
        pool = Counter()
        for dataset in SETS:
            if dataset != target:
                pool.update(by_cell[dataset, model])
        st, ft = rates(counts)
        sc, fc = rates(pool)
        jc = sc - fc
        check(jc > 0, "Eligible source correction")
        c = dict(n=sum(counts.values()), tn=counts[0, 0], fp=counts[0, 1],
                 fn=counts[1, 0], tp=counts[1, 1], source_tn=pool[0, 0],
                 source_fp=pool[0, 1], source_fn=pool[1, 0], source_tp=pool[1, 1],
                 target_fpr=ft, target_sensitivity=st, source_fpr=fc,
                 source_sensitivity=sc, source_J=jc)
        expected_confusion[target, model] = c
        for p in SHARES:
            q = p * st + (1 - p) * ft
            corrected = (q - fc) / jc
            clipped = max(F(0), min(F(1), corrected))
            check(corrected - p == (p * (st - sc) + (1 - p) * (ft - fc)) / jc,
                  "Exact correction-bias identity")
            if st != ft:
                check((q - ft) / (st - ft) == p, "Exact target-oracle control")
            else:
                singular.append((model, target, float(p)))
            expected_grid[target, model, p] = dict(
                raw=q, source_J=jc, corrected=corrected, clipped=clipped,
                raw_bias=q-p, corrected_bias=corrected-p, clipped_bias=clipped-p,
                absolute_error_change=abs(corrected-p)-abs(q-p),
                clipped_absolute_error_change=abs(clipped-p)-abs(q-p),
                fixed_half_bias=F(1, 2)-p)

confusion = read_csv("results_confusion.csv")
check(len(confusion) == 35, "Confusion table count")
check(len({(r["target"], r["model"]) for r in confusion}) == 35,
      "Unique confusion rows")
for row in confusion:
    for name, value in expected_confusion[row["target"], row["model"]].items():
        close(row[name], value, f"Confusion {name}")

grid = read_csv("results_grid.csv")
check(len(grid) == 175, "Grid count")
grid_by_key = {(r["target"], r["model"], F(r["assumed_share"])): r for r in grid}
check(set(grid_by_key) == set(expected_grid), "Unique complete planned grid")
for key, expected in expected_grid.items():
    row = grid_by_key[key]
    check(row["eligible"] == "True", "Grid eligibility")
    for name, value in expected.items():
        close(row[name], value, f"Grid {name}")

bootstrap = read_csv("results_bootstrap_rates.csv")
check(len(bootstrap) == 70000, "Bootstrap rate count")
draws = {}
for row in bootstrap:
    draw = int(row["draw"])
    target, model = row["target"], row["model"]
    key = (draw, target, model)
    check(0 <= draw < 2000 and key not in draws, "Unique bootstrap rate key")
    draws[key] = {name: float(row[name]) for name in
                  ["target_fpr", "target_sensitivity", "source_fpr", "source_sensitivity"]}
    for name, value in draws[key].items():
        check(0 <= value <= 1, "Bootstrap rate bounds")
    counts = by_cell[target, model]
    close(draws[key]["target_fpr"] * (counts[0, 0] + counts[0, 1]),
          round(draws[key]["target_fpr"] * (counts[0, 0] + counts[0, 1])),
          "Integer negative-class bootstrap count")
    close(draws[key]["target_sensitivity"] * (counts[1, 0] + counts[1, 1]),
          round(draws[key]["target_sensitivity"] * (counts[1, 0] + counts[1, 1])),
          "Integer positive-class bootstrap count")

for (draw, target, model), row in draws.items():
    numerator_p = numerator_n = denominator_p = denominator_n = 0
    for dataset in SETS:
        if dataset == target:
            continue
        counts = by_cell[dataset, model]
        n_p = counts[1, 0] + counts[1, 1]
        n_n = counts[0, 0] + counts[0, 1]
        numerator_p += n_p * draws[draw, dataset, model]["target_sensitivity"]
        numerator_n += n_n * draws[draw, dataset, model]["target_fpr"]
        denominator_p += n_p
        denominator_n += n_n
    close(row["source_sensitivity"], numerator_p / denominator_p,
          "Bootstrap pooled source sensitivity")
    close(row["source_fpr"], numerator_n / denominator_n, "Bootstrap pooled source FPR")

suppressed = 0
interval_fractions = {}
for (target, model, p), result in grid_by_key.items():
    bias_values, change_values = [], []
    invalid = 0
    p_float = float(p)
    for draw in range(2000):
        row = draws[draw, target, model]
        jc = row["source_sensitivity"] - row["source_fpr"]
        if jc <= 0:
            invalid += 1
            continue
        q = p_float * row["target_sensitivity"] + (1-p_float) * row["target_fpr"]
        bias = (q-row["source_fpr"]) / jc - p_float
        bias_values.append(bias)
        change_values.append(abs(bias) - abs(q-p_float))
    fraction = invalid / 2000
    interval_fractions[target, model, p] = fraction
    close(result["bootstrap_nonpositive_J_fraction"], fraction, "Invalid-J fraction")
    if invalid:
        suppressed += 1
        check(all(result[name] == "" for name in
                  ["bias_low", "bias_high", "change_low", "change_high"]),
              "Intervals suppressed across singular correction")
    else:
        for prefix, values in [("bias", bias_values), ("change", change_values)]:
            close(result[prefix+"_low"], percentile(values, .025), "Lower percentile")
            close(result[prefix+"_high"], percentile(values, .975), "Upper percentile")


def summarize(keys):
    values = [expected_grid[key] for key in keys]
    def count(name, side):
        if side == "improved":
            return sum(float(v[name]) < -1e-12 for v in values)
        if side == "worse":
            return sum(float(v[name]) > 1e-12 for v in values)
        return sum(abs(float(v[name])) <= 1e-12 for v in values)
    summary = dict(cells=len(values), eligible=len(values),
                   out_of_range=sum(not 0 <= v["corrected"] <= 1 for v in values),
                   intervals_suppressed=sum(interval_fractions[key] > 0 for key in keys))
    for prefix, change in [("", "absolute_error_change"),
                           ("clipped_", "clipped_absolute_error_change")]:
        for side in ["improved", "worse", "tied"]:
            summary[prefix+side] = count(change, side)
    for prefix in ["raw", "corrected", "clipped", "fixed_half"]:
        summary[prefix+"_mae"] = sum(abs(v[prefix+"_bias"]) for v in values) / len(values)
    return summary


summary = json.loads((ROOT / "results_summary.json").read_text())
for name, keys in [("overall", list(expected_grid))]:
    expected = summarize(keys)
    for field, value in summary[name].items():
        check(field in expected, "Known summary field")
        close(value, expected[field], f"Summary {field}")
for model, group in summary["by_model"].items():
    expected = summarize([key for key in expected_grid if key[1] == model])
    for field, value in group.items():
        close(value, expected[field], f"Model summary {field}")
for p, group in summary["by_share"].items():
    expected = summarize([key for key in expected_grid if key[2] == F(p)])
    for field, value in group.items():
        close(value, expected[field], f"Share summary {field}")
check(summary["data_rows"] == len(rows), "Summary input rows")
check(summary["unique_items"] == len(item_models), "Summary unique items")
check(summary["bootstrap_draws"] == 2000 and summary["seed"] == 20261010,
      "Summary bootstrap design")
for dataset, group in summary["items_by_set"].items():
    counts = by_cell[dataset, MODELS[0]]
    check(group == {"negative": counts[0, 0] + counts[0, 1],
                    "positive": counts[1, 0] + counts[1, 1]}, "Summary class sizes")
close(summary["source_J_min"], min(v["source_J"] for v in expected_confusion.values()),
      "Minimum source J")
close(summary["source_J_max"], max(v["source_J"] for v in expected_confusion.values()),
      "Maximum source J")
check(sorted(singular) == sorted((r["model"], r["target"], r["assumed_share"])
                                for r in summary["oracle_singular_cases"]),
      "Recorded singular oracle cells")

receipt = dict(status="pass", checks=checks, input_decisions=len(rows),
               unique_items=len(item_models), confusion_rows=len(confusion), grid_cells=len(grid),
               bootstrap_rate_rows=len(bootstrap), interval_cells_checked=len(grid),
               intervals_suppressed=suppressed, oracle_singular_cells=len(singular),
               exact_fraction_point_checks=True,
               limits="No source-label validation or population coverage claim. Bootstrap draws were checked from saved rates; random draw generation was not independently repeated.")
(ROOT / "validation_results.json").write_text(json.dumps(receipt, indent=2)+"\n")
print(json.dumps(receipt, indent=2))
