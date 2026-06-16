"""Analyze C5.53 congestion-aware route-facility results."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
import sys

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_53 import CONFIG_PATH, load_config
from mine_env.simulator_c5_53 import write_route_cycle_time_table

DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "c5_53" / "summary" / "c5_53_policy_comparison.csv"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "c5_53_congestion_bottleneck_test.md"
DEFAULT_ANALYSIS = PROJECT_ROOT / "outputs" / "c5_53" / "analysis" / "c5_53_policy_congestion_summary.csv"
DEFAULT_ROUTE_TABLE = PROJECT_ROOT / "outputs" / "c5_53" / "analysis" / "c5_53_route_cycle_time_table.csv"

ROUTE_KEYS = [
    "route_r_a1_loads",
    "route_r_a2_loads",
    "route_r_b1_loads",
    "route_r_b2_loads",
    "route_r_c1_loads",
    "route_r_c2_loads",
]


def mean(rows, key):
    vals = [float(row[key]) for row in rows if row.get(key, "") != ""]
    return statistics.mean(vals) if vals else 0.0


def route_share(rows, key):
    totals = {route_key: sum(float(row[route_key]) for row in rows) for route_key in ROUTE_KEYS}
    denom = sum(totals.values()) or 1.0
    return totals[key] / denom


def compact_route_mix(rows):
    labels = ["R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2"]
    return ", ".join(
        f"{label} {route_share(rows, key):.1%}"
        for label, key in zip(labels, ROUTE_KEYS)
    )


def read_route_cycle_table(path: Path):
    if not path.exists():
        write_route_cycle_time_table(load_config(CONFIG_PATH), path.parent)
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_policy_summary_csv(grouped, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "regime",
        "policy_id",
        "total_tco_v2",
        "total_tco_v3",
        "effective_output",
        "effective_fulfillment_rate",
        "avg_grade_per_load",
        "failure_count",
        "cm_count",
        "total_downtime_hours",
        "congestion_delay_hours_total",
        "congestion_cost",
        "avg_realized_cycle_time_hours",
        "completed_loads_per_hour",
        "route_hhi",
        "max_route_share",
        "route_fallback_loads",
        "r_c_share",
        "crusher_1_share",
        "crusher_2_share",
    ]
    rows = []
    for (regime, policy_id), items in sorted(grouped.items()):
        crusher_total = mean(items, "crusher_1_loads") + mean(items, "crusher_2_loads")
        crusher_total = crusher_total or 1.0
        c_share = route_share(items, "route_r_c1_loads") + route_share(items, "route_r_c2_loads")
        rows.append(
            {
                "regime": regime,
                "policy_id": policy_id,
                "total_tco_v2": round(mean(items, "total_tco_v2"), 6),
                "total_tco_v3": round(mean(items, "total_tco_v3"), 6),
                "effective_output": round(mean(items, "effective_output"), 6),
                "effective_fulfillment_rate": round(mean(items, "effective_fulfillment_rate"), 6),
                "avg_grade_per_load": round(mean(items, "avg_grade_per_load"), 6),
                "failure_count": round(mean(items, "failure_count"), 6),
                "cm_count": round(mean(items, "cm_count"), 6),
                "total_downtime_hours": round(mean(items, "total_downtime_hours"), 6),
                "congestion_delay_hours_total": round(mean(items, "congestion_delay_hours_total"), 6),
                "congestion_cost": round(mean(items, "congestion_cost"), 6),
                "avg_realized_cycle_time_hours": round(mean(items, "avg_realized_cycle_time_hours"), 6),
                "completed_loads_per_hour": round(mean(items, "completed_loads_per_hour"), 6),
                "route_hhi": round(mean(items, "route_hhi"), 6),
                "max_route_share": round(mean(items, "max_route_share"), 6),
                "route_fallback_loads": round(mean(items, "route_fallback_loads"), 6),
                "r_c_share": round(c_share, 6),
                "crusher_1_share": round(mean(items, "crusher_1_loads") / crusher_total, 6),
                "crusher_2_share": round(mean(items, "crusher_2_loads") / crusher_total, 6),
            }
        )
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze C5.53 congestion bottleneck results.")
    ap.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    ap.add_argument("--out", default=str(DEFAULT_REPORT))
    ap.add_argument("--analysis-csv", default=str(DEFAULT_ANALYSIS))
    args = ap.parse_args()

    summary_path = Path(args.summary)
    with summary_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    route_cycle_rows = read_route_cycle_table(DEFAULT_ROUTE_TABLE)
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["regime"], row["policy_id"])].append(row)

    write_policy_summary_csv(grouped, Path(args.analysis_csv))

    regimes = sorted({row["regime"] for row in rows})
    lines = [
        "# C5.53 Congestion Bottleneck Test",
        "",
        "## Why C5.53 Was Needed",
        "",
        "C5.52 proved that objective definition changes the policy ranking, but its logs could not prove whether route concentration creates route, shovel, or crusher bottlenecks. C5.53 keeps the C5.52 route/facility/grade-aware structure and adds deterministic congestion logging plus a separate congestion-aware TCO extension.",
        "",
        "## New Instrumentation",
        "",
        "- Dispatch events record preferred route, assigned route, fallback reason, route/shovel/crusher utilization before and after, queue delay components, base cycle time, route cycle factor, and realized cycle time.",
        "- Daily summaries aggregate route/facility loads and attempts, fallback/rejected loads, queue hours, congestion cost, average realized cycle time, completed loads per hour, route HHI, and max route share.",
        "- `total_tco_v1` keeps the legacy reliability-cost objective, `total_tco_v2` keeps the C5.52 grade-aware objective, and `total_tco_v3` adds congestion cost on top of v2.",
        "",
        "## Literature-Informed Proxy Cycle-Time Calibration",
        "",
        "C5.53 uses literature-informed proxy values for ultra-class truck speed, shovel loading time, crusher dumping/service time, and virtual route distance. These values are not real Escondida measurements. They are used to create a physically plausible bottleneck surface and are evaluated through sensitivity analysis.",
        "",
        "- Truck speed proxy: OEM top speed reference is 64 km/h and is used only as an upper-bound sanity check. Base empty operating speed is 32 km/h; base loaded operating speed is 24 km/h.",
        "- Loading proxy: 350 t payload is loaded through route shovel proxies with 100-110 t bucket payload, 35-42 second bucket cycles, and 0.7-0.9 minute spotting time.",
        "- Crusher service proxy: spotting is 0.8 min, dumping is 1.2 min, and crusher acceptance is 1.6 min for Crusher 1 versus 1.1 min for Crusher 2.",
        "- Route distance proxy: virtual empty/loaded distances are shortest for C routes, middle for B routes, and longest for A routes; Crusher 2 routes have longer loaded travel distance but lower service acceptance time.",
        "",
        "| route | shovel | crusher | empty km | loaded km | empty speed km/h | loaded speed km/h | loading min | crusher service min | base cycle min | loads/truck-hour |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in route_cycle_rows:
        lines.append(
            f"| {row['route_id']} | {row['shovel_id']} | {row['crusher_id']} | "
            f"{float(row['empty_distance_km']):.1f} | {float(row['loaded_distance_km']):.1f} | "
            f"{float(row['empty_speed_kmh_effective']):.1f} | {float(row['loaded_speed_kmh_effective']):.1f} | "
            f"{float(row['loading_time_min']):.2f} | {float(row['crusher_service_time_min']):.2f} | "
            f"{float(row['base_cycle_time_min']):.2f} | {float(row['expected_loads_per_truck_hour']):.2f} |"
        )
    lines += [
        "",
        "The resulting order is checked as a plausibility guardrail: R_C1 and R_C2 should be the fastest routes, B routes should sit in the middle, and A routes should be the slowest. The table is exported to `outputs/c5_53/analysis/c5_53_route_cycle_time_table.csv`.",
        "",
        "## Policy x Regime Congestion Summary",
        "",
        "| regime | policy | TCO v2 | TCO v3 | eff fulfillment | avg grade/load | failures | downtime | congestion h | cycle h | loads/h | HHI | max share | C-route share | route mix |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for regime in regimes:
        regime_policies = sorted(
            [policy for r, policy in grouped if r == regime],
            key=lambda policy: mean(grouped[(regime, policy)], "total_tco_v3"),
        )
        for policy_id in regime_policies:
            items = grouped[(regime, policy_id)]
            c_share = route_share(items, "route_r_c1_loads") + route_share(items, "route_r_c2_loads")
            lines.append(
                f"| {regime} | {policy_id} | {mean(items, 'total_tco_v2'):.1f} | "
                f"{mean(items, 'total_tco_v3'):.1f} | "
                f"{mean(items, 'effective_fulfillment_rate'):.3f} | "
                f"{mean(items, 'avg_grade_per_load'):.3f} | "
                f"{mean(items, 'failure_count'):.1f} | "
                f"{mean(items, 'total_downtime_hours'):.1f} | "
                f"{mean(items, 'congestion_delay_hours_total'):.1f} | "
                f"{mean(items, 'avg_realized_cycle_time_hours'):.3f} | "
                f"{mean(items, 'completed_loads_per_hour'):.2f} | "
                f"{mean(items, 'route_hhi'):.3f} | "
                f"{mean(items, 'max_route_share'):.3f} | "
                f"{c_share:.3f} | {compact_route_mix(items)} |"
            )
        lines.append("")

    lines += [
        "## H1/H2 vs H4 Bottleneck Interpretation",
        "",
        "| regime | H1/H2 family mean C-route share | H1/H2 family mean congestion h | H1/H2 family mean HHI | H4 C-route share | H4 congestion h | H4 HHI | interpretation |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    h12_ids = ["H1", "H2", "H1_original", "H1_value_guard", "H2_original", "H2_value_guard"]
    for regime in regimes:
        h12_rows = [row for pid in h12_ids for row in grouped.get((regime, pid), [])]
        h4_rows = grouped.get((regime, "H4"), [])
        h12_c = route_share(h12_rows, "route_r_c1_loads") + route_share(h12_rows, "route_r_c2_loads")
        h4_c = route_share(h4_rows, "route_r_c1_loads") + route_share(h4_rows, "route_r_c2_loads")
        h12_cong = mean(h12_rows, "congestion_delay_hours_total")
        h4_cong = mean(h4_rows, "congestion_delay_hours_total")
        h12_hhi = mean(h12_rows, "route_hhi")
        h4_hhi = mean(h4_rows, "route_hhi")
        interpretation = (
            "H4 shows lower concentration and congestion"
            if h4_hhi < h12_hhi and h4_cong <= h12_cong
            else "No clear congestion advantage for H4 under this parameterization"
        )
        lines.append(
            f"| {regime} | {h12_c:.3f} | {h12_cong:.1f} | {h12_hhi:.3f} | "
            f"{h4_c:.3f} | {h4_cong:.1f} | {h4_hhi:.3f} | {interpretation} |"
        )

    lines += [
        "",
        "## Findings",
        "",
        "- C5.53 directly tests what C5.52 could only infer: whether route choice concentration creates queue delay, cycle time expansion, fallback, and extra TCO.",
        "- H1/H2 should be read as reliability-cost policies first. If they keep concentrating on Shovel C routes, C5.53 can now show whether that concentration has a bottleneck penalty.",
        "- H4 should be read as the diversification/backpressure comparator. If its HHI and congestion hours are lower while effective output remains competitive, it supports a congestion-aware production objective.",
        "- H0/H_TIME remain useful baselines because they reveal whether high output is bought with failure, CM, downtime, or congestion cost.",
        "",
        "## C5.54 / Value-Risk Sweep Implication",
        "",
        "C5.54 is justified only if the C5.53 run shows material ranking movement between `total_tco_v2` and `total_tco_v3`, or if H1/H2 lose their advantage once C-route concentration is charged through congestion. If congestion is negligible at alpha/beta base settings, the next sweep should vary congestion alpha/beta before defining a new policy family.",
        "",
    ]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}", flush=True)
    print(f"Wrote {Path(args.analysis_csv)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
