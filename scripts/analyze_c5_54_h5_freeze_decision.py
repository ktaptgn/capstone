"""Create the C5.54 H5 candidate freeze decision report."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = PROJECT_ROOT / "outputs" / "c5_54" / "analysis" / "c5_54_guard_sensitivity_summary.csv"
GUARD_PATH = PROJECT_ROOT / "outputs" / "c5_54" / "analysis" / "c5_54_guard_sensitivity_guard_behavior.csv"
OUT_CSV = PROJECT_ROOT / "outputs" / "c5_54" / "analysis" / "c5_54_h5_candidate_freeze_table.csv"
OUT_REPORT = PROJECT_ROOT / "reports" / "c5_54_h5_candidate_freeze_decision.md"

SETTINGS = [(0.90, "base"), (0.85, "strict")]
REGIMES = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
POLICY = "H4_BALANCED_RR_GUARD"

FREEZE_FIELDS = [
    "soft_utilization_threshold",
    "risk_guard_level",
    "regime",
    "total_tco_v4_soft_congestion",
    "total_tco_v3_hard",
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
    "guard_skip_per_completed_load",
    "fallback_per_completed_load",
    "route_violation_per_completed_load",
    "shovel_violation_per_completed_load",
    "crusher_violation_per_completed_load",
    "risk_violation_per_completed_load",
    "dominant_guard",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def f(row: dict[str, Any], key: str) -> float:
    return float(row.get(key, 0) or 0)


def matches(row: dict[str, str], threshold: float, risk_level: str, regime: str, policy: str) -> bool:
    return (
        row.get("stage") == "S2"
        and abs(float(row["soft_utilization_threshold"]) - threshold) < 1e-9
        and row["risk_guard_level"] == risk_level
        and row["regime"] == regime
        and row.get("policy") == policy
    )


def get_row(rows: list[dict[str, str]], threshold: float, risk_level: str, regime: str, policy: str) -> dict[str, str]:
    return next(row for row in rows if matches(row, threshold, risk_level, regime, policy))


def freeze_rows(summary_rows: list[dict[str, str]], guard_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for threshold, risk_level in SETTINGS:
        for regime in REGIMES:
            summary = get_row(summary_rows, threshold, risk_level, regime, POLICY)
            guard = get_row(guard_rows, threshold, risk_level, regime, POLICY)
            out.append(
                {
                    "soft_utilization_threshold": threshold,
                    "risk_guard_level": risk_level,
                    "regime": regime,
                    "total_tco_v4_soft_congestion": f(summary, "total_tco_v4_soft_congestion"),
                    "total_tco_v3_hard": f(summary, "total_tco_v3_hard"),
                    "effective_fulfillment_rate": f(summary, "effective_fulfillment_rate"),
                    "effective_output": f(summary, "effective_output"),
                    "route_hhi": f(summary, "route_hhi"),
                    "max_route_share": f(summary, "max_route_share"),
                    "congestion_delay_hours_hard": f(summary, "congestion_delay_hours_hard"),
                    "congestion_delay_hours_soft": f(summary, "congestion_delay_hours_soft"),
                    "failure_count": f(summary, "failure_count"),
                    "cm_count": f(summary, "cm_count"),
                    "downtime_hours": f(summary, "downtime_hours"),
                    "pm_visits": f(summary, "pm_visits"),
                    "guard_skip_per_completed_load": f(guard, "guard_skip_per_completed_load"),
                    "fallback_per_completed_load": f(guard, "fallback_per_completed_load"),
                    "route_violation_per_completed_load": f(guard, "route_violation_per_completed_load"),
                    "shovel_violation_per_completed_load": f(guard, "shovel_violation_per_completed_load"),
                    "crusher_violation_per_completed_load": f(guard, "crusher_violation_per_completed_load"),
                    "risk_violation_per_completed_load": f(guard, "risk_violation_per_completed_load"),
                    "dominant_guard": guard["dominant_guard"],
                }
            )
    return out


def write_freeze_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FREEZE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def by_setting(rows: list[dict[str, Any]], threshold: float, risk_level: str, regime: str) -> dict[str, Any]:
    return next(
        row
        for row in rows
        if abs(float(row["soft_utilization_threshold"]) - threshold) < 1e-9
        and row["risk_guard_level"] == risk_level
        and row["regime"] == regime
    )


def reference_margin(
    summary_rows: list[dict[str, str]],
    threshold: float,
    risk_level: str,
    regime: str,
    reference_policy: str,
) -> float:
    guard = get_row(summary_rows, threshold, risk_level, regime, POLICY)
    ref = get_row(summary_rows, threshold, risk_level, regime, reference_policy)
    return f(ref, "total_tco_v4_soft_congestion") - f(guard, "total_tco_v4_soft_congestion")


def fmt(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def write_report(rows: list[dict[str, Any]], summary_rows: list[dict[str, str]]) -> None:
    lines = [
        "# C5.54 H5 Candidate Freeze Decision",
        "",
        "## Why This Decision Is Needed",
        "",
        "C5.54 sensitivity narrowed `H4_BALANCED_RR_GUARD` to two viable settings. The remaining decision is not whether the policy can beat H4, but which setting should become the default H5 candidate without hiding fallback dependence.",
        "",
        "## Sensitivity Recap",
        "",
        "- `0.90/base` beat H4 and `BALANCED_RR_H4_PM` in all S2 regimes.",
        "- `0.85/strict` also beat H4 and `BALANCED_RR_H4_PM` in all S2 regimes.",
        "- `0.85/strict` has better high-demand TCO, but materially higher guard skips and fallback-to-H4.",
        "- Route guard violations remained zero, so the route guard is non-binding under current regimes.",
        "",
        "## Candidate Comparison Table",
        "",
        "| threshold | risk | regime | soft TCO v4 | hard TCO v3 | eff fulfillment | eff output | HHI | max route share | hard h | soft h | failure | CM | downtime h | PM | skips/load | fallback/load | route viol/load | shovel viol/load | crusher viol/load | risk viol/load | dominant |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {f(row, 'soft_utilization_threshold'):.2f} | {row['risk_guard_level']} | {row['regime']} | "
            f"{fmt(f(row, 'total_tco_v4_soft_congestion'))} | {fmt(f(row, 'total_tco_v3_hard'))} | "
            f"{f(row, 'effective_fulfillment_rate'):.3f} | {fmt(f(row, 'effective_output'))} | "
            f"{f(row, 'route_hhi'):.3f} | {f(row, 'max_route_share'):.3f} | "
            f"{f(row, 'congestion_delay_hours_hard'):.2f} | {f(row, 'congestion_delay_hours_soft'):.2f} | "
            f"{fmt(f(row, 'failure_count'))} | {fmt(f(row, 'cm_count'))} | {fmt(f(row, 'downtime_hours'))} | "
            f"{fmt(f(row, 'pm_visits'))} | {f(row, 'guard_skip_per_completed_load'):.3f} | "
            f"{f(row, 'fallback_per_completed_load'):.3f} | {f(row, 'route_violation_per_completed_load'):.3f} | "
            f"{f(row, 'shovel_violation_per_completed_load'):.3f} | {f(row, 'crusher_violation_per_completed_load'):.3f} | "
            f"{f(row, 'risk_violation_per_completed_load'):.3f} | {row['dominant_guard']} |"
        )

    lines += [
        "",
        "## Pairwise Differences",
        "",
        "`strict - base` is shown below. Negative TCO means `0.85/strict` is lower cost; positive fallback means more fallback dependence.",
        "",
        "| regime | TCO v4 diff | eff fulfillment diff | failure diff | CM diff | downtime h diff | hard h diff | soft h diff | fallback/load diff | H4 TCO margin, base | RR TCO margin, base | H4 TCO margin, strict | RR TCO margin, strict |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for regime in REGIMES:
        base = by_setting(rows, 0.90, "base", regime)
        strict = by_setting(rows, 0.85, "strict", regime)
        lines.append(
            f"| {regime} | "
            f"{fmt(f(strict, 'total_tco_v4_soft_congestion') - f(base, 'total_tco_v4_soft_congestion'))} | "
            f"{f(strict, 'effective_fulfillment_rate') - f(base, 'effective_fulfillment_rate'):.4f} | "
            f"{fmt(f(strict, 'failure_count') - f(base, 'failure_count'))} | "
            f"{fmt(f(strict, 'cm_count') - f(base, 'cm_count'))} | "
            f"{fmt(f(strict, 'downtime_hours') - f(base, 'downtime_hours'))} | "
            f"{f(strict, 'congestion_delay_hours_hard') - f(base, 'congestion_delay_hours_hard'):.2f} | "
            f"{f(strict, 'congestion_delay_hours_soft') - f(base, 'congestion_delay_hours_soft'):.2f} | "
            f"{f(strict, 'fallback_per_completed_load') - f(base, 'fallback_per_completed_load'):.3f} | "
            f"{fmt(reference_margin(summary_rows, 0.90, 'base', regime, 'H4'))} | "
            f"{fmt(reference_margin(summary_rows, 0.90, 'base', regime, 'BALANCED_RR_H4_PM'))} | "
            f"{fmt(reference_margin(summary_rows, 0.85, 'strict', regime, 'H4'))} | "
            f"{fmt(reference_margin(summary_rows, 0.85, 'strict', regime, 'BALANCED_RR_H4_PM'))} |"
        )

    lines += [
        "",
        "## Decision",
        "",
        "- Recommended default H5 candidate setting: `H4_BALANCED_RR_GUARD`, `soft_utilization_threshold = 0.90`, `risk_guard_level = base`.",
        "- Recommended aggressive alternative: `soft_utilization_threshold = 0.85`, `risk_guard_level = strict`.",
        "- Reason: `0.85/strict` is lower TCO in `high_demand_high_stress`, but it is not consistently lower TCO in the two lower-stress regimes and it roughly doubles fallback/load versus `0.90/base` in normal regimes.",
        "- `0.90/base` keeps the all-regime win over both H4 and the audit comparator while preserving cleaner interpretability and lower fallback dependence.",
        "- Route violation equals zero for both settings in all regimes. This means the route guard is not currently binding; the active decision surface is shovel/risk/crusher guard plus fallback.",
        "",
        "## H5 Naming",
        "",
        "H5 naming is now justified as a next implementation step, with `0.90/base` as the default candidate. This report does not create H5 and does not modify prior C5 modules.",
        "",
        "## Next Command",
        "",
        "```powershell",
        "$env:PYTHONDONTWRITEBYTECODE='1'; python -B scripts\\run_c5_54_guard_sensitivity.py --stage s2 --s2-settings 0.90:base,0.85:strict",
        "```",
        "",
    ]
    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    summary_rows = read_csv(SUMMARY_PATH)
    guard_rows = read_csv(GUARD_PATH)
    rows = freeze_rows(summary_rows, guard_rows)
    if len(rows) != 6:
        raise RuntimeError(f"Expected 6 candidate rows, found {len(rows)}")
    write_freeze_csv(rows)
    write_report(rows, summary_rows)
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
