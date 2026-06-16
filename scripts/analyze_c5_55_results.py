"""Analyze C5.55 official H5 benchmark results."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "c5_55" / "summary" / "c5_55_policy_comparison.csv"
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "c5_55" / "analysis"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "c5_55_h5_policy_benchmark.md"

POLICY_ORDER = [
    "H0",
    "H_TIME",
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "BALANCED_RR_H4_PM",
    "H5_AGGRESSIVE",
]

POLICY_FIELDS = [
    "regime",
    "policy",
    "total_tco_v2",
    "total_tco_v3_hard",
    "total_tco_v4_soft_congestion",
    "effective_fulfillment_rate",
    "effective_output",
    "route_hhi",
    "max_route_share",
    "congestion_delay_hours_hard",
    "congestion_delay_hours_soft",
    "failure_count",
    "cm_count",
    "downtime_hours",
    "pm_visits",
    "avg_realized_cycle_time",
    "guard_skip_count",
    "fallback_to_h4_count",
    "route_guard_violation_count",
    "shovel_guard_violation_count",
    "crusher_guard_violation_count",
    "risk_guard_violation_count",
    "guard_skip_per_completed_load",
    "fallback_per_completed_load",
    "route_violation_per_completed_load",
    "shovel_violation_per_completed_load",
    "crusher_violation_per_completed_load",
    "risk_violation_per_completed_load",
    "dominant_guard",
    "rank_tco_v4_soft",
]

GUARD_FIELDS = [
    "regime",
    "policy",
    "completed_loads",
    "guard_skip_count",
    "fallback_to_h4_count",
    "route_guard_violation_count",
    "shovel_guard_violation_count",
    "crusher_guard_violation_count",
    "risk_guard_violation_count",
    "guard_skip_per_completed_load",
    "fallback_per_completed_load",
    "route_violation_per_completed_load",
    "shovel_violation_per_completed_load",
    "crusher_violation_per_completed_load",
    "risk_violation_per_completed_load",
    "dominant_guard",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def mean(rows: list[dict[str, str]], key: str) -> float:
    vals = [float(row.get(key, 0) or 0) for row in rows]
    return statistics.mean(vals) if vals else 0.0


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["regime"], row["policy_id"])].append(row)

    out: list[dict[str, object]] = []
    for (regime, policy), items in sorted(grouped.items()):
        completed = max(mean(items, "completed_loads"), 1.0)
        guard_counts = {
            "route": mean(items, "route_guard_violation_count"),
            "shovel": mean(items, "shovel_guard_violation_count"),
            "crusher": mean(items, "crusher_guard_violation_count"),
            "risk": mean(items, "risk_guard_violation_count"),
        }
        rates = {key: value / completed for key, value in guard_counts.items()}
        dominant_guard = max(rates, key=rates.get) if max(rates.values()) > 0 else "none"
        out.append(
            {
                "regime": regime,
                "policy": policy,
                "total_tco_v2": mean(items, "total_tco_v2"),
                "total_tco_v3_hard": mean(items, "total_tco_v3_hard"),
                "total_tco_v4_soft_congestion": mean(items, "total_tco_v4_soft_congestion"),
                "effective_fulfillment_rate": mean(items, "effective_fulfillment_rate"),
                "effective_output": mean(items, "effective_output"),
                "route_hhi": mean(items, "route_hhi"),
                "max_route_share": mean(items, "max_route_share"),
                "congestion_delay_hours_hard": mean(items, "congestion_delay_hours_hard"),
                "congestion_delay_hours_soft": mean(items, "congestion_delay_hours_soft"),
                "failure_count": mean(items, "failure_count"),
                "cm_count": mean(items, "cm_count"),
                "downtime_hours": mean(items, "total_downtime_hours"),
                "pm_visits": mean(items, "pm_count"),
                "avg_realized_cycle_time": mean(items, "avg_realized_cycle_time_min"),
                "completed_loads": completed,
                "guard_skip_count": mean(items, "guard_skip_count"),
                "fallback_to_h4_count": mean(items, "fallback_to_h4_count"),
                "route_guard_violation_count": guard_counts["route"],
                "shovel_guard_violation_count": guard_counts["shovel"],
                "crusher_guard_violation_count": guard_counts["crusher"],
                "risk_guard_violation_count": guard_counts["risk"],
                "guard_skip_per_completed_load": mean(items, "guard_skip_count") / completed,
                "fallback_per_completed_load": mean(items, "fallback_to_h4_count") / completed,
                "route_violation_per_completed_load": rates["route"],
                "shovel_violation_per_completed_load": rates["shovel"],
                "crusher_violation_per_completed_load": rates["crusher"],
                "risk_violation_per_completed_load": rates["risk"],
                "dominant_guard": dominant_guard,
                "rank_tco_v4_soft": 0,
            }
        )

    for regime in sorted({row["regime"] for row in out}):
        ranked = sorted(
            [row for row in out if row["regime"] == regime],
            key=lambda row: float(row["total_tco_v4_soft_congestion"]),
        )
        for rank, row in enumerate(ranked, start=1):
            row["rank_tco_v4_soft"] = rank
    return out


def write_csv(rows: list[dict[str, object]], path: Path, fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in row.items()
                    if key in fields
                }
            )


def select_fields(rows: list[dict[str, object]], fields: list[str]) -> list[dict[str, object]]:
    return [{field: row[field] for field in fields} for row in rows]


def get(rows: list[dict[str, object]], regime: str, policy: str) -> dict[str, object]:
    return next(row for row in rows if row["regime"] == regime and row["policy"] == policy)


def has_policy(rows: list[dict[str, object]], regime: str, policy: str) -> bool:
    return any(row["regime"] == regime and row["policy"] == policy for row in rows)


def margin(rows: list[dict[str, object]], regime: str, policy: str, reference: str) -> float:
    return float(get(rows, regime, reference)["total_tco_v4_soft_congestion"]) - float(
        get(rows, regime, policy)["total_tco_v4_soft_congestion"]
    )


def write_report(rows: list[dict[str, object]], raw_count: int, path: Path) -> None:
    regimes = sorted({row["regime"] for row in rows})
    h5_beats_h4 = all(margin(rows, regime, "H5", "H4") > 0 for regime in regimes)
    h5_beats_rr = all(margin(rows, regime, "H5", "BALANCED_RR_H4_PM") > 0 for regime in regimes)
    aggressive_beats_h5 = [
        regime for regime in regimes if margin(rows, regime, "H5_AGGRESSIVE", "H5") > 0
    ]
    ready = h5_beats_h4 and h5_beats_rr

    lines = [
        "# C5.55 H5 Policy Benchmark",
        "",
        "## Why C5.55 Was Created",
        "",
        "C5.55 freezes the C5.54 H5 candidate decision into a separate official benchmark module. It does not replace C5.4; it is a personal follow-up benchmark that preserves prior C5 modules and compares H5 against H0-H4 plus audit/sensitivity comparators.",
        "",
        "## H5 Freeze Decision Recap",
        "",
        "- Default H5: `H4_BALANCED_RR_GUARD`, `soft_utilization_threshold = 0.90`, `risk_guard_level = base`.",
        "- Aggressive alternative: `H5_AGGRESSIVE`, `soft_utilization_threshold = 0.85`, `risk_guard_level = strict`.",
        "- `BALANCED_RR_H4_PM` remains audit-only and is not official.",
        "- `H5_AGGRESSIVE` remains a sensitivity comparator and is not the default.",
        "",
        "## Benchmark Scope",
        "",
        f"- Raw summary rows: {raw_count}. Aggregated policy x regime rows: {len(rows)}.",
        "- Horizon: 90 days.",
        "- Seeds: 101-110.",
        "- Regimes: heterogeneous_condition, high_stress, high_demand_high_stress.",
        "- Event log: disabled.",
        "",
        "## Policy x Regime Soft TCO Ranking",
        "",
        "| regime | rank | policy | soft TCO v4 | eff fulfillment | hard h | soft h | failure | CM | downtime h | fallback/load | dominant guard |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for regime in regimes:
        regime_rows = sorted(
            [row for row in rows if row["regime"] == regime],
            key=lambda row: int(row["rank_tco_v4_soft"]),
        )
        for row in regime_rows:
            lines.append(
                f"| {regime} | {int(row['rank_tco_v4_soft'])} | {row['policy']} | "
                f"{float(row['total_tco_v4_soft_congestion']):.1f} | "
                f"{float(row['effective_fulfillment_rate']):.3f} | "
                f"{float(row['congestion_delay_hours_hard']):.2f} | "
                f"{float(row['congestion_delay_hours_soft']):.2f} | "
                f"{float(row['failure_count']):.1f} | {float(row['cm_count']):.1f} | "
                f"{float(row['downtime_hours']):.1f} | "
                f"{float(row['fallback_per_completed_load']):.3f} | {row['dominant_guard']} |"
            )

    lines += [
        "",
        "## H5 Pairwise Comparisons",
        "",
        "| regime | H5 vs H4 TCO margin | H5 vs BALANCED_RR_H4_PM margin | H5_AGGRESSIVE vs H5 margin | H5 eff fulfillment | H5 failure/CM | H5 downtime h | H5 hard/soft h | H5 fallback/load |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for regime in regimes:
        h5 = get(rows, regime, "H5")
        lines.append(
            f"| {regime} | {margin(rows, regime, 'H5', 'H4'):.1f} | "
            f"{margin(rows, regime, 'H5', 'BALANCED_RR_H4_PM'):.1f} | "
            f"{margin(rows, regime, 'H5_AGGRESSIVE', 'H5'):.1f} | "
            f"{float(h5['effective_fulfillment_rate']):.3f} | "
            f"{float(h5['failure_count']):.1f}/{float(h5['cm_count']):.1f} | "
            f"{float(h5['downtime_hours']):.1f} | "
            f"{float(h5['congestion_delay_hours_hard']):.2f}/{float(h5['congestion_delay_hours_soft']):.2f} | "
            f"{float(h5['fallback_per_completed_load']):.3f} |"
        )

    lines += [
        "",
        "## H5 vs H1/H2 Reliability Frontier",
        "",
        "| regime | H1 failure/CM | H2 failure/CM | H5 failure/CM | H1 soft TCO | H2 soft TCO | H5 soft TCO |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for regime in regimes:
        h1 = get(rows, regime, "H1")
        h2 = get(rows, regime, "H2")
        h5 = get(rows, regime, "H5")
        lines.append(
            f"| {regime} | {float(h1['failure_count']):.1f}/{float(h1['cm_count']):.1f} | "
            f"{float(h2['failure_count']):.1f}/{float(h2['cm_count']):.1f} | "
            f"{float(h5['failure_count']):.1f}/{float(h5['cm_count']):.1f} | "
            f"{float(h1['total_tco_v4_soft_congestion']):.1f} | "
            f"{float(h2['total_tco_v4_soft_congestion']):.1f} | "
            f"{float(h5['total_tco_v4_soft_congestion']):.1f} |"
        )

    route_zero = all(
        float(row["route_violation_per_completed_load"]) == 0.0
        for row in rows
        if row["policy"] in {"H5", "H5_AGGRESSIVE"}
    )
    h5_eff_min = min(float(get(rows, regime, "H5")["effective_fulfillment_rate"]) for regime in regimes)
    lines += [
        "",
        "## Interpretation",
        "",
        f"- H5 beats H4 in all regimes: {'yes' if h5_beats_h4 else 'no'}.",
        f"- H5 beats `BALANCED_RR_H4_PM` in all regimes: {'yes' if h5_beats_rr else 'no'}.",
        f"- H5_AGGRESSIVE beats H5 in: {', '.join(aggressive_beats_h5) if aggressive_beats_h5 else 'no regimes'}.",
        f"- H5 minimum effective fulfillment across regimes: {h5_eff_min:.3f}.",
        f"- Route guard violation remains zero for H5/H5_AGGRESSIVE: {'yes' if route_zero else 'no'}.",
        "- H5 has explicit guard/fallback behavior; fallback dependence should be presented as part of the policy, not hidden as a pure route-balancing win.",
        "- H1/H2 can still be interpreted as reliability-focused policies when their failure/CM profile is competitive, but H5 is the production-congestion benchmark in this experiment.",
        "",
        "## Presentation Readiness",
        "",
        f"H5 is {'robust enough' if ready else 'not yet robust enough'} for the personal presentation under this 90-day benchmark, with the limitation that C5.55 is a follow-up experiment and does not replace the team C5.4 result.",
        "",
        "## Limitations",
        "",
        "- The route guard remains non-binding in these regimes, so shovel/risk/crusher guards and fallback drive most H5 behavior.",
        "- The benchmark uses the C5.53 proxy cycle-time and soft-congestion model, not calibrated site measurements.",
        "- `H5_AGGRESSIVE` is useful for stress sensitivity but should not be treated as the default policy.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze C5.55 official H5 benchmark results.")
    ap.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    ap.add_argument("--analysis-dir", default=str(DEFAULT_ANALYSIS_DIR))
    ap.add_argument("--report", default=str(DEFAULT_REPORT))
    args = ap.parse_args()

    raw_rows = read_csv(Path(args.summary))
    rows = aggregate(raw_rows)
    policy_path = Path(args.analysis_dir) / "c5_55_policy_tradeoff_summary.csv"
    guard_path = Path(args.analysis_dir) / "c5_55_guard_behavior_summary.csv"
    write_csv(select_fields(rows, POLICY_FIELDS), policy_path, POLICY_FIELDS)
    write_csv(select_fields(rows, GUARD_FIELDS), guard_path, GUARD_FIELDS)
    write_report(rows, len(raw_rows), Path(args.report))
    print(f"Wrote {policy_path}")
    print(f"Wrote {guard_path}")
    print(f"Wrote {Path(args.report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
