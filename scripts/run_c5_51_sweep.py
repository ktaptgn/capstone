"""Run the C5.51 route-on-facilities policy sweep."""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_51 import CONFIG_PATH, load_config
from mine_env.simulator_c5_51 import run_policy_simulation, write_summary

SUMMARY_DIR = PROJECT_ROOT / "outputs" / "c5_51" / "summary"

KPI_COLUMNS = [
    ("total_tco", "TCO", ".1f"),
    ("pm_count", "PMvisits", ".0f"),
    ("cm_count", "CM/run", ".1f"),
    ("failure_count", "fail/run", ".1f"),
    ("demand_fulfillment_rate", "fulfil", ".3f"),
    ("total_downtime_hours", "downHrs", ".0f"),
    ("effective_output", "eff_output", ".0f"),
    ("pm_bay_utilization", "PMutil", ".3f"),
]


def mean(rows, key):
    return statistics.mean(float(r[key]) for r in rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.51 route-on-facilities PM+dispatch sweep.")
    ap.add_argument("--days", type=int, default=None, help="override horizon_days")
    ap.add_argument("--seeds", default=None, help="comma-separated seeds")
    ap.add_argument("--regimes", default="heterogeneous_condition")
    ap.add_argument("--summary-dir", default=str(SUMMARY_DIR))
    args = ap.parse_args()

    base_cfg = load_config(CONFIG_PATH)
    policies = list(base_cfg["policies"]["enabled"])
    seeds = (
        [int(s) for s in args.seeds.split(",") if s.strip()]
        if args.seeds
        else [int(s) for s in base_cfg["evaluation"]["seeds"]]
    )
    regimes = [r.strip() for r in args.regimes.split(",") if r.strip()]
    all_summaries = []

    for regime in regimes:
        config = load_config(CONFIG_PATH, regime=regime)
        eff_days = args.days or int(config["simulation"]["horizon_days"])
        print(
            f"=== C5.51 {regime}: {len(policies)} policies x {len(seeds)} seeds x {eff_days} days ===",
            flush=True,
        )
        for policy_id in policies:
            rows = [
                run_policy_simulation(config, policy_id, seed=seed, days=args.days).summary
                for seed in seeds
            ]
            for row in rows:
                row["regime"] = regime
                all_summaries.append(row)
            metrics = " ".join(
                f"{label}={mean(rows, key):{fmt}}" for key, label, fmt in KPI_COLUMNS
            )
            print(f"  {policy_id}: {metrics}", flush=True)

    write_summary(all_summaries, args.summary_dir)
    print(f"\nWrote {Path(args.summary_dir) / 'c5_51_policy_comparison.csv'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
