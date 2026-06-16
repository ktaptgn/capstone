"""Run the C5.52 grade-aware route-facility objective sweep."""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_52 import CONFIG_PATH, load_config
from mine_env.simulator_c5_52 import run_policy_simulation, write_summary

SUMMARY_DIR = PROJECT_ROOT / "outputs" / "c5_52" / "summary"


def mean(rows, key):
    return statistics.mean(float(r[key]) for r in rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.52 grade-aware route-facility sweep.")
    ap.add_argument("--days", type=int, default=None, help="override horizon_days")
    ap.add_argument("--seeds", default=None, help="comma-separated seeds")
    ap.add_argument("--regimes", default="heterogeneous_condition,high_stress,high_demand_high_stress")
    ap.add_argument("--sensitivities", default="low,base,high")
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
    sensitivities = [s.strip() for s in args.sensitivities.split(",") if s.strip()]
    all_summaries = []

    for regime in regimes:
        config = load_config(CONFIG_PATH, regime=regime)
        eff_days = args.days or int(config["simulation"]["horizon_days"])
        for sensitivity in sensitivities:
            print(
                f"=== C5.52 {regime} sensitivity={sensitivity}: "
                f"{len(policies)} policies x {len(seeds)} seeds x {eff_days} days ===",
                flush=True,
            )
            for policy_id in policies:
                rows = [
                    run_policy_simulation(
                        config,
                        policy_id,
                        seed=seed,
                        days=args.days,
                        shortfall_sensitivity=sensitivity,
                    ).summary
                    for seed in seeds
                ]
                for row in rows:
                    row["regime"] = regime
                    all_summaries.append(row)
                print(
                    f"  {policy_id}: "
                    f"TCOv1={mean(rows, 'total_tco_v1'):.1f} "
                    f"TCOv2={mean(rows, 'total_tco_v2'):.1f} "
                    f"effFul={mean(rows, 'effective_fulfillment_rate'):.3f} "
                    f"avgGrade={mean(rows, 'avg_grade_per_load'):.3f}",
                    flush=True,
                )

    write_summary(all_summaries, args.summary_dir)
    print(f"\nWrote {Path(args.summary_dir) / 'c5_52_policy_comparison.csv'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
