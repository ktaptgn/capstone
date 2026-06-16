"""Create a compact Markdown analysis from C5.5 summary CSV output."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "c5_5" / "summary" / "c5_5_policy_comparison.csv"
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "c5_5" / "analysis" / "c5_5_summary.md"


def mean(rows, key):
    return statistics.mean(float(row[key]) for row in rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze C5.5 policy comparison CSV.")
    ap.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    ap.add_argument("--out", default=str(DEFAULT_REPORT))
    args = ap.parse_args()

    with Path(args.summary).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["regime"], row["policy_id"])].append(row)

    lines = ["# C5.5 Facility-Destination Summary", ""]
    regimes = sorted({key[0] for key in grouped})
    for regime in regimes:
        policy_rows = {policy: grouped[(regime, policy)] for _, policy in grouped if _ == regime}
        ranked = sorted(policy_rows, key=lambda pid: mean(policy_rows[pid], "total_tco"))
        lines += [
            f"## {regime}",
            "",
            "| rank | policy | mean TCO | fulfillment | failures | PM visits | PM util |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
        for rank, policy_id in enumerate(ranked, start=1):
            rows_for_policy = policy_rows[policy_id]
            lines.append(
                f"| {rank} | {policy_id} | {mean(rows_for_policy, 'total_tco'):.1f} | "
                f"{mean(rows_for_policy, 'demand_fulfillment_rate'):.3f} | "
                f"{mean(rows_for_policy, 'failure_count'):.1f} | "
                f"{mean(rows_for_policy, 'pm_count'):.1f} | "
                f"{mean(rows_for_policy, 'pm_bay_utilization'):.3f} |"
            )
        lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
