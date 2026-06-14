"""C5.4 joint (PM-scheduling + dispatch) sweep: H0-H4 + H_TIME recast as PM-family x dispatch-family
pairs, 3-component reliability (frailty + sensor noise) in the 25-truck C5 mine.

Runs every enabled joint policy across held-out seeds and one or more operating regimes, then writes
a per-regime ranked KPI table, a per-seed robustness matrix (paired vs the H0 fully-blind baseline),
and a cross-regime summary that flags where the failure/CM path activates and whether the ranking
flips. Lower total_tco is better. In-lab benchmark; not an official C5.1 ranking.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_4 import load_config
from mine_env.simulator_c5_4 import run_policy_simulation, write_summary

CONFIG_PATH = PROJECT_ROOT / "configs" / "c5_4.yaml"
REPORT_PATH = PROJECT_ROOT / "docs" / "source" / "07_C5_4_RESULTS.md"
SUMMARY_DIR = PROJECT_ROOT / "outputs" / "c5_4" / "summary"

KPI_COLUMNS = [
    ("total_tco", "TCO", ".1f"),
    ("pm_count", "PMvisits", ".0f"),
    ("pm_component_count", "PMcomps", ".0f"),
    ("cm_count", "CM/run", ".1f"),
    ("failure_count", "fail/run", ".1f"),
    ("demand_fulfillment_rate", "fulfil", ".3f"),
    ("avg_truck_hi", "endHI", ".3f"),
    ("total_downtime_hours", "downHrs", ".0f"),
]


def mean(rows, key):
    return statistics.mean(float(r[key]) for r in rows)


def run_regime(config, policies, seeds, days):
    """Return {policy_id: [summary per seed]} for one regime config."""
    return {
        pid: [run_policy_simulation(config, pid, seed=s, days=days).summary for s in seeds]
        for pid in policies
    }


def regime_report_lines(regime, results, seeds, days):
    means = {pid: mean(rows, "total_tco") for pid, rows in results.items()}
    ranked = sorted(means, key=means.get)
    best = ranked[0]
    lines = [
        f"## Regime: `{regime}`",
        "",
        f"- {days} days x {len(seeds)} held-out seeds {seeds}; lower TCO is better; "
        f"best = **{best}** ({means[best]:.1f}).",
        "",
        "| rank | policy | " + " | ".join(c[1] for c in KPI_COLUMNS) + " |",
        "|---|---|" + "|".join("---:" for _ in KPI_COLUMNS) + "|",
    ]
    for rank, pid in enumerate(ranked, start=1):
        rows = results[pid]
        cells = [f"{mean(rows, key):{fmt}}" for key, _label, fmt in KPI_COLUMNS]
        star = " **(best)**" if pid == best else ""
        lines.append(f"| {rank} | {pid}{star} | " + " | ".join(cells) + " |")

    # per-seed robustness: paired diff vs H0 baseline (negative = beats baseline)
    if "H0" in results:
        base = {s: float(results["H0"][i]["total_tco"]) for i, s in enumerate(seeds)}
        lines += ["", "Paired per-seed TCO vs H0 baseline (negative = cheaper than H0):", ""]
        lines.append("| seed | " + " | ".join(ranked) + " |")
        lines.append("|---|" + "|".join("---:" for _ in ranked) + "|")
        for i, s in enumerate(seeds):
            cells = [f"{float(results[pid][i]['total_tco']) - base[s]:+.1f}" for pid in ranked]
            lines.append(f"| {s} | " + " | ".join(cells) + " |")
        wins = {
            pid: sum(
                1
                for i, s in enumerate(seeds)
                if float(results[pid][i]["total_tco"]) < base[s]
            )
            for pid in ranked
            if pid != "H0"
        }
        win_str = ", ".join(f"{pid} {w}/{len(seeds)}" for pid, w in wins.items())
        lines += ["", f"- Seeds where each policy beats H0: {win_str}."]
    lines.append("")
    return lines, ranked, means


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.4 joint PM+dispatch sweep.")
    ap.add_argument("--days", type=int, default=None, help="override horizon_days (default: config 365)")
    ap.add_argument("--seeds", default=None, help="comma seeds (default: config evaluation.seeds)")
    ap.add_argument("--regimes", default="heterogeneous_condition,high_stress,high_demand_high_stress")
    ap.add_argument("--report", default=str(REPORT_PATH))
    args = ap.parse_args()

    base_cfg = load_config(CONFIG_PATH)
    policies = list(base_cfg["policies"]["enabled"])
    seeds = (
        [int(s) for s in args.seeds.split(",") if s.strip()]
        if args.seeds
        else [int(s) for s in base_cfg["evaluation"]["seeds"]]
    )
    regimes = [r.strip() for r in args.regimes.split(",") if r.strip()]
    days = args.days

    header = [
        "# C5.4 Joint PM-Scheduling + Dispatch Results: H0-H4 + H_TIME (recast)",
        "",
        "- Environment: 25-truck C5 mine + C6 routes A/B/C; 3-component HI (tire/engine/brake), "
        "frailty (Gamma wear heterogeneity) and C6 sensor noise. Decision target = JOINT "
        "PM-scheduling + dispatch; objective = total TCO (pm+cm+downtime+degradation+unmet).",
        "- Policies (PM-family x dispatch-family pairs): H0 calendar+route-blind, H_TIME "
        "operating-hours+route-blind, H1 CBM+health, H2 risk+risk-aware, H3 cost-value+value, "
        "H4 flow+capacity.",
        "- In-lab benchmark; not an official C5.1 ranking.",
        "",
    ]
    report_lines = list(header)
    all_summaries = []
    per_regime_rank = {}

    for regime in regimes:
        config = load_config(CONFIG_PATH, regime=regime)
        eff_days = days or int(config["simulation"]["horizon_days"])
        print(f"=== regime {regime}: {len(policies)} policies x {len(seeds)} seeds x {eff_days} days ===", flush=True)
        results = run_regime(config, policies, seeds, days)
        for pid, rows in results.items():
            for row in rows:
                row["regime"] = regime
                all_summaries.append(row)
            print(f"  {pid}: TCO={mean(rows,'total_tco'):.1f} CM={mean(rows,'cm_count'):.1f} "
                  f"fail={mean(rows,'failure_count'):.1f} PMvisits={mean(rows,'pm_count'):.0f}", flush=True)
        lines, ranked, _means = regime_report_lines(regime, results, seeds, eff_days)
        report_lines += lines
        per_regime_rank[regime] = ranked

    # cross-regime summary
    report_lines += ["## Cross-regime summary", "", "| regime | ranking (best->worst) | best |", "|---|---|---|"]
    for regime, ranked in per_regime_rank.items():
        report_lines.append(f"| {regime} | {' < '.join(ranked)} | {ranked[0]} |")
    report_lines.append("")

    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    write_summary(all_summaries, SUMMARY_DIR)
    Path(args.report).write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"\nWrote {args.report}\nWrote {SUMMARY_DIR / 'c5_4_policy_comparison.csv'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
