#!/usr/bin/env python3
"""Draw the exact case-count matrix from summary.csv with standard-library SVG.

No experiment is run. Matplotlib was unavailable in the study environment.
"""
import argparse
import csv
import hashlib
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET


RULES = ("OwnCAS", "SharedEpoch", "AtomicSum")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/summary.csv"))
    parser.add_argument("--output", type=Path, default=Path("results/breach_matrix.svg"))
    args = parser.parse_args()
    raw = args.input.read_bytes()
    with args.input.open(newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["stratum"] == "all"]
    data = {(r["policy_A"], r["policy_B"]): (int(r["breach"]), int(r["cases"])) for r in rows}
    if len(rows) != 9 or set(data) != {(a, b) for a in RULES for b in RULES}:
        raise ValueError("Expected exactly one all-stratum row for each ordered rule pair")
    if any(n != 576 or not 0 <= bad <= n for bad, n in data.values()):
        raise ValueError("Unexpected case denominator or breach count")

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="700" height="412" viewBox="0 0 700 412" role="img" aria-labelledby="title desc">',
        '<title id="title">Shared-limit breaches by worker rule pair</title>',
        '<desc id="desc">Rows are worker A. Columns are worker B. Each cell gives the exact number of cases that exceeded capacity out of 576 assigned cases. These are designed local SQLite cases, not population failure rates.</desc>',
        f'<metadata>Source: summary.csv; SHA-256: {hashlib.sha256(raw).hexdigest()}. Generator: make_figure.py. No experiment was run to make this figure.</metadata>',
        '<rect width="700" height="412" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#202a31">',
        '<text x="28" y="34" font-size="21" font-weight="700">Shared-limit breaches by worker rule pair</text>',
        '<text x="28" y="59" font-size="13">Exact case counts; each cell has 576 assigned cases.</text>',
        '<text x="423" y="92" text-anchor="middle" font-size="13" font-weight="700">Worker B</text>',
        '<text x="28" y="120" font-size="13" font-weight="700">Worker A</text>',
    ]
    x0, y0, width, height = 185, 136, 158, 68
    for col, rule in enumerate(RULES):
        svg.append(f'<text x="{x0 + col * width + width / 2:g}" y="120" text-anchor="middle" font-size="14" font-weight="700">{escape(rule)}</text>')
    for row, rule_a in enumerate(RULES):
        svg.append(f'<text x="169" y="{y0 + row * height + 40}" text-anchor="end" font-size="14" font-weight="700">{escape(rule_a)}</text>')
        for col, rule_b in enumerate(RULES):
            bad, denominator = data[rule_a, rule_b]
            # A fixed zero color and linear count scale make the colors repeatable.
            if bad == 0:
                fill, text = "#eaf3ef", "#193f32"
            else:
                fraction = min(bad / 120, 1)
                light, dark = (249, 226, 216), (150, 51, 28)
                rgb = tuple(round(a + fraction * (b - a)) for a, b in zip(light, dark))
                fill = "#" + "".join(f"{c:02x}" for c in rgb)
                text = "#ffffff" if bad >= 90 else "#31211b"
            x, y = x0 + col * width, y0 + row * height
            svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" stroke="#ffffff" stroke-width="3"/>')
            svg.append(f'<text x="{x + width / 2:g}" y="{y + 42}" text-anchor="middle" font-size="22" font-weight="700" fill="{text}">{bad} / {denominator}</text>')
    svg.extend([
        '<text x="28" y="369" font-size="12">Breach: total allocation exceeded the shared capacity at a scheduled point.</text>',
        '<text x="28" y="389" font-size="12">Designed local SQLite corpus. Counts do not estimate website or AI-agent failure rates.</text>',
        '</g></svg>',
    ])
    result = "\n".join(svg) + "\n"
    ET.fromstring(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    print(f"Wrote {args.output}; 9 cells checked against {args.input}")
    for a in RULES:
        print(a + ": " + ", ".join(str(data[a, b][0]) for b in RULES))


if __name__ == "__main__":
    main()
