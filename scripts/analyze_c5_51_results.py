"""Create a compact Markdown analysis from C5.51 summary CSV output."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "c5_51" / "summary" / "c5_51_policy_comparison.csv"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "c5_51" / "analysis" / "c5_51_summary.md"


def mean(rows, key):
    return statistics.mean(float(row[key]) for row in rows)


def route_distribution(rows):
    keys = ["route_r_a1_loads", "route_r_a2_loads", "route_r_b1_loads", "route_r_b2_loads", "route_r_c1_loads", "route_r_c2_loads"]
    totals = {key: sum(float(row[key]) for row in rows) for key in keys}
    denom = sum(totals.values()) or 1.0
    return ", ".join(f"{key.replace('route_', '').replace('_loads', '').upper()} {totals[key] / denom:.1%}" for key in keys)


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze C5.51 policy comparison CSV.")
    ap.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    ap.add_argument("--out", default=str(DEFAULT_REPORT))
    args = ap.parse_args()

    with Path(args.summary).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["regime"], row["policy_id"])].append(row)

    lines = ["# C5.51 Facility Route Summary", ""]
    regimes = sorted({key[0] for key in grouped})
    for regime in regimes:
        policy_rows = {policy: grouped[(r, policy)] for r, policy in grouped if r == regime}
        ranked = sorted(policy_rows, key=lambda pid: mean(policy_rows[pid], "total_tco"))
        lines += [
            f"## {regime}",
            "",
            "| rank | policy | mean TCO | fulfillment | failures | CM | PM visits | downtime | route distribution |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for rank, policy_id in enumerate(ranked, start=1):
            rows_for_policy = policy_rows[policy_id]
            lines.append(
                f"| {rank} | {policy_id} | {mean(rows_for_policy, 'total_tco'):.1f} | "
                f"{mean(rows_for_policy, 'demand_fulfillment_rate'):.3f} | "
                f"{mean(rows_for_policy, 'failure_count'):.1f} | "
                f"{mean(rows_for_policy, 'cm_count'):.1f} | "
                f"{mean(rows_for_policy, 'pm_count'):.1f} | "
                f"{mean(rows_for_policy, 'total_downtime_hours'):.0f} | "
                f"{route_distribution(rows_for_policy)} |"
            )
        lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
