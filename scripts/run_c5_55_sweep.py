"""Run the C5.55 official H5 benchmark."""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_55 import CONFIG_PATH, load_config
from mine_env.simulator_c5_55 import (
    run_policy_simulation,
    write_daily_records,
    write_dispatch_events,
    write_route_cycle_time_table,
    write_summary,
)

SUMMARY_DIR = PROJECT_ROOT / "outputs" / "c5_55" / "summary"
LOG_DIR = PROJECT_ROOT / "outputs" / "c5_55" / "logs"
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "c5_55" / "analysis"


def mean(rows, key):
    return statistics.mean(float(r[key]) for r in rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.55 official H5 benchmark sweep.")
    ap.add_argument("--days", type=int, default=None, help="override horizon_days")
    ap.add_argument("--seeds", default=None, help="comma-separated seeds")
    ap.add_argument("--regimes", default="heterogeneous_condition")
    ap.add_argument("--policies", default=None, help="comma-separated policies")
    ap.add_argument("--sensitivities", default="base")
    ap.add_argument("--congestion-alpha", type=float, default=None)
    ap.add_argument("--congestion-beta", type=float, default=None)
    ap.add_argument("--congestion-cost-level", default=None)
    ap.add_argument("--summary-dir", default=str(SUMMARY_DIR))
    ap.add_argument("--log-dir", default=str(LOG_DIR))
    ap.add_argument("--analysis-dir", default=str(ANALYSIS_DIR))
    ap.add_argument("--no-event-log", action="store_true", help="skip dispatch event CSV")
    ap.add_argument("--no-daily-log", action="store_true", help="skip daily summary CSV")
    args = ap.parse_args()

    base_cfg = load_config(CONFIG_PATH)
    write_route_cycle_time_table(base_cfg, args.analysis_dir)
    policies = (
        [p.strip() for p in args.policies.split(",") if p.strip()]
        if args.policies
        else list(base_cfg["policies"]["enabled"])
    )
    seeds = (
        [int(s) for s in args.seeds.split(",") if s.strip()]
        if args.seeds
        else [int(s) for s in base_cfg["evaluation"]["seeds"][:3]]
    )
    regimes = [r.strip() for r in args.regimes.split(",") if r.strip()]
    sensitivities = [s.strip() for s in args.sensitivities.split(",") if s.strip()]
    all_summaries = []
    all_events = []
    all_daily = []

    for regime in regimes:
        config = load_config(CONFIG_PATH, regime=regime)
        eff_days = args.days or int(config["simulation"]["horizon_days"])
        for sensitivity in sensitivities:
            print(
                f"=== C5.55 {regime} sensitivity={sensitivity}: "
                f"{len(policies)} policies x {len(seeds)} seeds x {eff_days} days ===",
                flush=True,
            )
            for policy_id in policies:
                rows = []
                for seed in seeds:
                    result = run_policy_simulation(
                        config,
                        policy_id,
                        seed=seed,
                        days=args.days,
                        shortfall_sensitivity=sensitivity,
                        congestion_alpha=args.congestion_alpha,
                        congestion_beta=args.congestion_beta,
                        congestion_cost_level=args.congestion_cost_level,
                        record_daily=not args.no_daily_log,
                        record_events=not args.no_event_log,
                    )
                    result.summary["regime"] = regime
                    rows.append(result.summary)
                    all_summaries.append(result.summary)
                    all_events.extend(result.dispatch_events)
                    all_daily.extend(result.daily_records)
                print(
                    f"  {policy_id}: "
                    f"TCOv4={mean(rows, 'total_tco_v4_soft_congestion'):.1f} "
                    f"effFul={mean(rows, 'effective_fulfillment_rate'):.3f} "
                    f"HHI={mean(rows, 'route_hhi'):.3f} "
                    f"hardH={mean(rows, 'congestion_delay_hours_hard'):.2f} "
                    f"softH={mean(rows, 'congestion_delay_hours_soft'):.2f} "
                    f"fallback={mean(rows, 'fallback_to_h4_count'):.1f}",
                    flush=True,
                )

    write_summary(all_summaries, args.summary_dir)
    event_path = None
    daily_path = None
    if not args.no_event_log:
        event_path = write_dispatch_events(all_events, args.log_dir)
    if not args.no_daily_log:
        daily_path = write_daily_records(all_daily, args.log_dir)
    print(f"\nWrote {Path(args.summary_dir) / 'c5_55_policy_comparison.csv'}", flush=True)
    if not args.no_event_log:
        print(f"Wrote {event_path}", flush=True)
    if not args.no_daily_log:
        print(f"Wrote {daily_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
