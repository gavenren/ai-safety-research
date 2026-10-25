#!/usr/bin/env python3
"""Render the saved summary as a deterministic SVG. Does not run the model."""

import argparse
import csv
from html import escape
from pathlib import Path


RULES = [
    "Timeout",
    "ZeroObservation",
    "FenceOnly",
    "ClosureCertificate",
    "TerminalOnly",
]
MEASURES = [
    ("actual_excess_case", "Actual budget breach", "#a33830"),
    ("exposure_excess_case", "Exposure above budget", "#805492"),
    ("uncovered_case", "Uncovered A liability", "#276f96"),
]


def render(summary_path: Path, output_path: Path) -> None:
    with summary_path.open(newline="", encoding="utf-8") as handle:
        all_rows = [row for row in csv.DictReader(handle) if row["branch"] == "all"]
    if len(all_rows) != len(RULES):
        raise ValueError("Expected exactly five summary rows with branch=all")
    rows = {row["rule"]: row for row in all_rows}
    if set(rows) != set(RULES):
        raise ValueError("Expected each declared rule exactly once")
    for row in rows.values():
        if int(row["cases"]) != 1680:
            raise ValueError("The figure requires 1,680 cases per rule")
        for key, _, _ in MEASURES:
            if not 0 <= int(row[key]) <= 600:
                raise ValueError("Measure exceeds the declared 0 to 600 count axis")

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="520" '
        'viewBox="0 0 1160 520" role="img" aria-labelledby="title description">',
        '<title id="title">Reservation release: three separate safety measures</title>',
        '<desc id="description">Synthetic finite model, 1680 cases per rule. '
        + escape("; ".join(
            rule + ": " + ", ".join(
                name + " " + rows[rule][key] for key, name, _ in MEASURES
            ) for rule in RULES
        ))
        + '. Counts overlap and must not be added. These are not risk-rate estimates.</desc>',
        '<rect width="1160" height="520" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#202a33}'
        '.title{font-size:24px;font-weight:700}.sub{font-size:15px;fill:#4a5560}'
        '.head{font-size:16px;font-weight:700}.rule{font-size:16px}'
        '.tick{font-size:12px;fill:#65717c}.value{font-size:15px;font-weight:700}'
        '.note{font-size:14px;fill:#4a5560}</style>',
        '<text x="28" y="42" class="title">Reservation release: three separate safety measures</text>',
        '<text x="28" y="70" class="sub">Synthetic finite model · Counts out of 1,680 input worlds per rule</text>',
    ]
    panel_starts = [250, 550, 850]
    bar_width = 240
    top = 153
    row_gap = 54
    bottom = top + 4 * row_gap + 18
    for index, (key, name, color) in enumerate(MEASURES):
        x = panel_starts[index]
        parts.append(f'<text x="{x}" y="111" class="head">{escape(name)}</text>')
        for tick in (0, 200, 400, 600):
            tx = x + bar_width * tick / 600
            parts.append(
                f'<line x1="{tx:g}" y1="132" x2="{tx:g}" y2="{bottom}" '
                'stroke="#e4e8eb" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{tx:g}" y="414" text-anchor="middle" class="tick">{tick}</text>'
            )
        for row_index, rule in enumerate(RULES):
            y = top + row_index * row_gap
            value = int(rows[rule][key])
            width = bar_width * value / 600
            if value:
                parts.append(
                    f'<rect x="{x}" y="{y - 12}" width="{width:g}" height="24" '
                    f'rx="2" fill="{color}"/>'
                )
            else:
                parts.append(
                    f'<circle cx="{x}" cy="{y}" r="3" fill="#ffffff" '
                    f'stroke="{color}" stroke-width="2"/>'
                )
            parts.append(
                f'<text x="{x + width + 8:g}" y="{y + 5}" class="value">{value}</text>'
            )
    for row_index, rule in enumerate(RULES):
        parts.append(
            f'<text x="28" y="{top + row_index * row_gap + 5}" class="rule">{escape(rule)}</text>'
        )
    parts += [
        '<text x="28" y="454" class="note">Each count marks cases with the condition at any event. Measures overlap; do not add them.</text>',
        '<text x="28" y="480" class="note">Exact counts for this designed corpus. No estimate of production risk or agent error rates.</text>',
        '<text x="28" y="503" class="tick">Source: results/summary.csv, branch=all. Each panel uses the same 0–600 count axis.</text>',
        '</svg>',
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=base / "results" / "summary.csv")
    parser.add_argument("--output", type=Path, default=base / "results" / "breach_comparison.svg")
    args = parser.parse_args()
    render(args.summary, args.output)
    print(f"Wrote {args.output}")
