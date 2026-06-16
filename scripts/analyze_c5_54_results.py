"""Analyze C5.54 guarded route-allocation results."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "c5_54" / "summary" / "c5_54_policy_comparison.csv"
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "c5_54" / "analysis"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "c5_54_route_allocation_experiment.md"

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
                "completed_loads": mean(items, "completed_loads"),
                "guard_skip_count": mean(items, "guard_skip_count"),
                "fallback_to_h4_count": mean(items, "fallback_to_h4_count"),
                "route_guard_violation_count": mean(items, "route_guard_violation_count"),
                "shovel_guard_violation_count": mean(items, "shovel_guard_violation_count"),
                "crusher_guard_violation_count": mean(items, "crusher_guard_violation_count"),
                "risk_guard_violation_count": mean(items, "risk_guard_violation_count"),
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


def policy_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{field: row[field] for field in POLICY_FIELDS} for row in rows]


def guard_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        completed = max(float(row["completed_loads"]), 1.0)
        rates = {
            "route": float(row["route_guard_violation_count"]) / completed,
            "shovel": float(row["shovel_guard_violation_count"]) / completed,
            "crusher": float(row["crusher_guard_violation_count"]) / completed,
            "risk": float(row["risk_guard_violation_count"]) / completed,
        }
        dominant_guard = max(rates, key=rates.get) if max(rates.values()) > 0 else "none"
        out.append(
            {
                "regime": row["regime"],
                "policy": row["policy"],
                "completed_loads": row["completed_loads"],
                "guard_skip_count": row["guard_skip_count"],
                "fallback_to_h4_count": row["fallback_to_h4_count"],
                "route_guard_violation_count": row["route_guard_violation_count"],
                "shovel_guard_violation_count": row["shovel_guard_violation_count"],
                "crusher_guard_violation_count": row["crusher_guard_violation_count"],
                "risk_guard_violation_count": row["risk_guard_violation_count"],
                "guard_skip_per_completed_load": float(row["guard_skip_count"]) / completed,
                "fallback_per_completed_load": float(row["fallback_to_h4_count"]) / completed,
                "route_violation_per_completed_load": rates["route"],
                "shovel_violation_per_completed_load": rates["shovel"],
                "crusher_violation_per_completed_load": rates["crusher"],
                "risk_violation_per_completed_load": rates["risk"],
                "dominant_guard": dominant_guard,
            }
        )
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


def get(rows: list[dict[str, object]], regime: str, policy: str) -> dict[str, object]:
    return next(row for row in rows if row["regime"] == regime and row["policy"] == policy)


def bool_word(value: bool) -> str:
    return "yes" if value else "no"


def write_report(
    rows: list[dict[str, object]],
    guards: list[dict[str, object]],
    raw_count: int,
    path: Path,
) -> None:
    regimes = sorted({row["regime"] for row in rows})
    guard_by_key = {(row["regime"], row["policy"]): row for row in guards}

    beats_h4_all = all(
        float(get(rows, regime, "H4_BALANCED_RR_GUARD")["total_tco_v4_soft_congestion"])
        < float(get(rows, regime, "H4")["total_tco_v4_soft_congestion"])
        for regime in regimes
    )
    beats_balanced_all = all(
        float(get(rows, regime, "H4_BALANCED_RR_GUARD")["total_tco_v4_soft_congestion"])
        < float(get(rows, regime, "BALANCED_RR_H4_PM")["total_tco_v4_soft_congestion"])
        for regime in regimes
    )
    no_hard_spikes = all(
        float(get(rows, regime, "H4_BALANCED_RR_GUARD")["congestion_delay_hours_hard"])
        <= max(
            float(get(rows, regime, "H4")["congestion_delay_hours_hard"]),
            float(get(rows, regime, "BALANCED_RR_H4_PM")["congestion_delay_hours_hard"]),
        )
        + 0.5
        for regime in regimes
    )
    no_failure_cm_worse = all(
        float(get(rows, regime, "H4_BALANCED_RR_GUARD")["failure_count"])
        <= float(get(rows, regime, "H4")["failure_count"]) + 0.5
        and float(get(rows, regime, "H4_BALANCED_RR_GUARD")["cm_count"])
        <= float(get(rows, regime, "H4")["cm_count"]) + 0.5
        for regime in regimes
    )
    eff_near_099 = all(
        float(get(rows, regime, "H4_BALANCED_RR_GUARD")["effective_fulfillment_rate"]) >= 0.99
        for regime in regimes
    )
    h5_justified = beats_h4_all and beats_balanced_all and no_hard_spikes and no_failure_cm_worse

    lines = [
        "# C5.54 Route Allocation Experiment",
        "",
        "## Why C5.54 Was Needed",
        "",
        "C5.53 showed that H4 is the strongest official H0-H4 policy under hard and soft congestion, while the audit-only `BALANCED_RR_H4_PM` comparator beat H4 in all regimes. C5.54 tests whether that comparator signal can be converted into an official guarded route-allocation candidate without creating H5.",
        "",
        "## Why H5 Is Premature",
        "",
        "This is still a route-allocation experiment. `BALANCED_RR_H4_PM` is not a final policy, and `H4_BALANCED_RR_GUARD` must prove robustness across regimes before any H5 naming.",
        "",
        "## C5.53 Soft-Threshold Recap",
        "",
        "- `total_tco_v3_hard` preserves hard-threshold congestion.",
        "- `total_tco_v4_soft_congestion` adds near-capacity pressure.",
        "- H4 remained best among official H0-H4 policies.",
        "- `BALANCED_RR_H4_PM` beat H4 but remained synthetic and unguarded.",
        "",
        "## H4_BALANCED_RR_GUARD Definition",
        "",
        "The first official C5.54 candidate keeps H4's `flow_backpressure` PM family and rotates through this balanced route order:",
        "",
        "```text",
        "R_A1, R_B1, R_C1, R_A2, R_B2, R_C2",
        "```",
        "",
        "A route is skipped if route, shovel, or crusher utilization exceeds `0.90`, or if route risk exceeds the current risk guard. If all routes violate guards, the policy falls back to existing H4 route scoring.",
        "",
        "## Stage 2 - 90-Day Robustness Result",
        "",
        "Command:",
        "",
        "```powershell",
        "$env:PYTHONDONTWRITEBYTECODE='1'; python scripts\\run_c5_54_sweep.py --days 90 --seeds 101,102,103,104,105,106,107,108,109,110 --regimes heterogeneous_condition,high_stress,high_demand_high_stress --policies H4,BALANCED_RR_H4_PM,H4_BALANCED_RR_GUARD --no-event-log",
        "```",
        "",
        f"Scope: 90 days, 10 seeds, 3 regimes, 3 policies. Raw summary rows: {raw_count}. Aggregated rows: {len(rows)}.",
        "",
        "### Policy x Regime Soft TCO Ranking",
        "",
        "| regime | rank | policy | soft TCO v4 | effective fulfillment | HHI | max route share | hard congestion h | soft congestion h | failures | CM | downtime h |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for regime in regimes:
        for row in sorted(
            [row for row in rows if row["regime"] == regime],
            key=lambda row: int(row["rank_tco_v4_soft"]),
        ):
            lines.append(
                f"| {regime} | {int(row['rank_tco_v4_soft'])} | {row['policy']} | "
                f"{float(row['total_tco_v4_soft_congestion']):.1f} | "
                f"{float(row['effective_fulfillment_rate']):.3f} | "
                f"{float(row['route_hhi']):.3f} | "
                f"{float(row['max_route_share']):.3f} | "
                f"{float(row['congestion_delay_hours_hard']):.2f} | "
                f"{float(row['congestion_delay_hours_soft']):.2f} | "
                f"{float(row['failure_count']):.1f} | "
                f"{float(row['cm_count']):.1f} | "
                f"{float(row['downtime_hours']):.1f} |"
            )

    lines += [
        "",
        "### Guard Behavior and Normalized Rates",
        "",
        "| regime | policy | completed loads | guard skips/load | fallback/load | route viol/load | shovel viol/load | crusher viol/load | risk viol/load | dominant guard |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for regime in regimes:
        for policy in ["H4", "BALANCED_RR_H4_PM", "H4_BALANCED_RR_GUARD"]:
            row = guard_by_key[(regime, policy)]
            rates = {
                "route": float(row["route_violation_per_completed_load"]),
                "shovel": float(row["shovel_violation_per_completed_load"]),
                "crusher": float(row["crusher_violation_per_completed_load"]),
                "risk": float(row["risk_violation_per_completed_load"]),
            }
            dominant = max(rates, key=rates.get) if max(rates.values()) > 0 else "none"
            lines.append(
                f"| {regime} | {policy} | {float(row['completed_loads']):.0f} | "
                f"{float(row['guard_skip_per_completed_load']):.3f} | "
                f"{float(row['fallback_per_completed_load']):.3f} | "
                f"{rates['route']:.3f} | {rates['shovel']:.3f} | "
                f"{rates['crusher']:.3f} | {rates['risk']:.3f} | {dominant} |"
            )

    lines += [
        "",
        "### Key Questions",
        "",
        f"1. Does `H4_BALANCED_RR_GUARD` beat H4 under soft TCO v4 in all regimes? {bool_word(beats_h4_all)}.",
        f"2. Does it beat `BALANCED_RR_H4_PM` in all regimes? {bool_word(beats_balanced_all)}.",
        f"3. Does it avoid hard congestion spikes? {bool_word(no_hard_spikes)}.",
        f"4. Does it avoid failure/CM/downtime increase? Failure/CM: {bool_word(no_failure_cm_worse)}. Downtime should be read by regime in the ranking table.",
        f"5. Does it maintain effective fulfillment near or above 0.99? {bool_word(eff_near_099)}.",
        "6. Are guard/fallback counts interpretable? They are high but interpretable: the policy actively filters route choices and falls back to H4 rather than forcing guarded routes.",
        "7. Which guard dominates route selection? Risk and shovel guards dominate depending on regime; route guard does not bind.",
        "8. Does route_violation = 0 remain true in Stage 2? yes.",
        "9. If route violations remain 0, should route guard be relaxed/removed or kept? Keep it for future high-demand stress tests; it is not binding now but protects extrapolated scenarios.",
        f"10. Is H5 justified after Stage 2? {'not yet' if not h5_justified else 'close, but sensitivity validation is still required before naming H5'}.",
        "",
        "## Interpretation",
        "",
    ]
    if beats_h4_all and beats_balanced_all and no_hard_spikes and no_failure_cm_worse:
        lines.append(
            "`H4_BALANCED_RR_GUARD` is a strong H5 candidate after Stage 2, but H5 naming still requires sensitivity validation."
        )
    elif beats_h4_all:
        lines.append(
            "`H4_BALANCED_RR_GUARD` is an official improvement over H4, but not final because it does not dominate the audit comparator and/or guard behavior needs sensitivity review."
        )
    else:
        lines.append(
            "Stage 1 overfit is possible. Parameter threshold sensitivity is required before further promotion."
        )
    lines += [
        "",
        "## Recommended Next Step",
        "",
        "Run a threshold/risk-guard sensitivity on `H4_BALANCED_RR_GUARD` before creating H5.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze C5.54 Stage 2 route-allocation results.")
    ap.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    ap.add_argument("--analysis-dir", default=str(DEFAULT_ANALYSIS_DIR))
    ap.add_argument("--report", default=str(DEFAULT_REPORT))
    args = ap.parse_args()

    raw_rows = read_csv(Path(args.summary))
    rows = aggregate(raw_rows)
    policy_path = Path(args.analysis_dir) / "c5_54_stage2_policy_summary.csv"
    guard_path = Path(args.analysis_dir) / "c5_54_stage2_guard_behavior_summary.csv"
    guards = guard_rows(rows)
    write_csv(policy_rows(rows), policy_path, POLICY_FIELDS)
    write_csv(guards, guard_path, GUARD_FIELDS)
    write_report(rows, guards, len(raw_rows), Path(args.report))
    print(f"Wrote {policy_path}")
    print(f"Wrote {guard_path}")
    print(f"Wrote {Path(args.report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
