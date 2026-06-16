"""Run and analyze C5.54 H4_BALANCED_RR_GUARD sensitivity experiments."""
from __future__ import annotations

import argparse
import copy
import csv
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_54 import CONFIG_PATH, load_config
from mine_env.simulator_c5_54 import SUMMARY_FIELDS as C5_54_SUMMARY_FIELDS
from mine_env.simulator_c5_54 import run_policy_simulation, write_daily_records

POLICIES = ["H4", "BALANCED_RR_H4_PM", "H4_BALANCED_RR_GUARD"]
REGIMES = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
S1_THRESHOLDS = [0.85, 0.90, 0.95]
S1_RISK_LEVELS = ["relaxed", "base", "strict"]
RISK_LEVEL_TO_PERCENTILE = {"relaxed": 0.95, "base": 0.90, "strict": 0.75}
SENSITIVITY_ROOT = PROJECT_ROOT / "outputs" / "c5_54" / "sensitivity"
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "c5_54" / "analysis"
REPORT_PATH = PROJECT_ROOT / "reports" / "c5_54_guard_sensitivity_analysis.md"
SUMMARY_NAME = "c5_54_policy_comparison.csv"
RAW_SUMMARY_FIELDS = list(C5_54_SUMMARY_FIELDS) + [
    "stage",
    "soft_utilization_threshold",
    "risk_guard_level",
]

SUMMARY_FIELDS = [
    "stage",
    "soft_utilization_threshold",
    "risk_guard_level",
    "regime",
    "policy",
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
    "rank_tco_v4_soft",
]

GUARD_FIELDS = [
    "stage",
    "soft_utilization_threshold",
    "risk_guard_level",
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


@dataclass(frozen=True)
class Setting:
    stage: str
    threshold: float
    risk_level: str
    days: int
    seeds: tuple[int, ...]
    regimes: tuple[str, ...]

    @property
    def dirname(self) -> str:
        threshold = str(self.threshold).replace(".", "_")
        return f"{self.stage.lower()}_threshold_{threshold}_risk_{self.risk_level}"


def setting_dir(setting: Setting) -> Path:
    return SENSITIVITY_ROOT / setting.dirname


def configured(regime: str, threshold: float, risk_level: str) -> dict[str, Any]:
    config = copy.deepcopy(load_config(CONFIG_PATH, regime=regime))
    guard = config["h4_balanced_rr_guard"]
    guard["soft_utilization_threshold"] = float(threshold)
    guard["risk_guard_level"] = risk_level
    guard["risk_guard_percentile"] = RISK_LEVEL_TO_PERCENTILE[risk_level]
    guard["risk_guard_levels"] = dict(RISK_LEVEL_TO_PERCENTILE)
    return config


def mean(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row.get(key, 0) or 0) for row in rows]
    return statistics.mean(values) if values else 0.0


def write_sensitivity_summary(summary_rows: list[dict[str, Any]], summary_dir: Path) -> None:
    summary_dir.mkdir(parents=True, exist_ok=True)
    csv_path = summary_dir / SUMMARY_NAME
    json_path = summary_dir / "c5_54_policy_comparison.json"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=RAW_SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(summary_rows)
    with json_path.open("w", encoding="utf-8") as stream:
        json.dump(summary_rows, stream, indent=2)


def run_setting(setting: Setting) -> int:
    out_dir = setting_dir(setting)
    summary_dir = out_dir / "summary"
    log_dir = out_dir / "logs"
    all_summaries: list[dict[str, Any]] = []
    all_daily: list[dict[str, Any]] = []

    for regime in setting.regimes:
        config = configured(regime, setting.threshold, setting.risk_level)
        print(
            f"=== C5.54 guard sensitivity {setting.stage} threshold={setting.threshold:.2f} "
            f"risk={setting.risk_level} regime={regime}: "
            f"{len(POLICIES)} policies x {len(setting.seeds)} seeds x {setting.days} days ===",
            flush=True,
        )
        for policy_id in POLICIES:
            policy_rows: list[dict[str, Any]] = []
            for seed in setting.seeds:
                result = run_policy_simulation(
                    config,
                    policy_id,
                    seed=seed,
                    days=setting.days,
                    record_daily=True,
                    record_events=False,
                )
                result.summary["stage"] = setting.stage
                result.summary["soft_utilization_threshold"] = setting.threshold
                result.summary["risk_guard_level"] = setting.risk_level
                result.summary["regime"] = regime
                all_summaries.append(result.summary)
                all_daily.extend(result.daily_records)
                policy_rows.append(result.summary)
            print(
                f"  {policy_id}: "
                f"TCOv4={mean(policy_rows, 'total_tco_v4_soft_congestion'):.1f} "
                f"effFul={mean(policy_rows, 'effective_fulfillment_rate'):.3f} "
                f"hardH={mean(policy_rows, 'congestion_delay_hours_hard'):.2f} "
                f"softH={mean(policy_rows, 'congestion_delay_hours_soft'):.2f} "
                f"fallback={mean(policy_rows, 'fallback_to_h4_count'):.1f}",
                flush=True,
            )

    write_sensitivity_summary(all_summaries, summary_dir)
    write_daily_records(all_daily, log_dir)
    print(f"Wrote {summary_dir / SUMMARY_NAME}", flush=True)
    print(f"Wrote {log_dir / 'c5_54_daily_summary.csv'}", flush=True)
    return len(all_summaries)


def read_raw_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(SENSITIVITY_ROOT.glob(f"*/summary/{SUMMARY_NAME}")):
        with path.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                if "stage" not in row or not row["stage"]:
                    dirname = path.parents[1].name
                    row["stage"] = "S1" if dirname.startswith("s1_") else "S2"
                rows.append(row)
    return rows


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        key = (
            row["stage"],
            f"{float(row['soft_utilization_threshold']):.2f}",
            row["risk_guard_level"],
            row["regime"],
            row["policy_id"],
        )
        grouped.setdefault(key, []).append(row)

    out: list[dict[str, Any]] = []
    for (stage, threshold, risk_level, regime, policy), items in sorted(grouped.items()):
        out.append(
            {
                "stage": stage,
                "soft_utilization_threshold": float(threshold),
                "risk_guard_level": risk_level,
                "regime": regime,
                "policy": policy,
                "total_tco_v4_soft_congestion": mean(items, "total_tco_v4_soft_congestion"),
                "total_tco_v3_hard": mean(items, "total_tco_v3_hard"),
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

    for key in sorted(
        {
            (
                row["stage"],
                row["soft_utilization_threshold"],
                row["risk_guard_level"],
                row["regime"],
            )
            for row in out
        }
    ):
        ranked = sorted(
            [
                row
                for row in out
                if (
                    row["stage"],
                    row["soft_utilization_threshold"],
                    row["risk_guard_level"],
                    row["regime"],
                )
                == key
            ],
            key=lambda row: float(row["total_tco_v4_soft_congestion"]),
        )
        for rank, row in enumerate(ranked, start=1):
            row["rank_tco_v4_soft"] = rank
    return out


def policy_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{field: row[field] for field in SUMMARY_FIELDS} for row in rows]


def guard_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        completed = max(float(row["completed_loads"]), 1.0)
        rates = {
            "route": float(row["route_guard_violation_count"]) / completed,
            "shovel": float(row["shovel_guard_violation_count"]) / completed,
            "crusher": float(row["crusher_guard_violation_count"]) / completed,
            "risk": float(row["risk_guard_violation_count"]) / completed,
        }
        dominant = max(rates, key=rates.get) if max(rates.values()) > 0 else "none"
        out.append(
            {
                "stage": row["stage"],
                "soft_utilization_threshold": row["soft_utilization_threshold"],
                "risk_guard_level": row["risk_guard_level"],
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
                "dominant_guard": dominant,
            }
        )
    return out


def write_csv(rows: list[dict[str, Any]], path: Path, fields: list[str]) -> None:
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


def guard_row(
    guards: list[dict[str, Any]],
    stage: str,
    threshold: float,
    risk_level: str,
    regime: str,
    policy: str,
) -> dict[str, Any]:
    return next(
        row
        for row in guards
        if row["stage"] == stage
        and abs(float(row["soft_utilization_threshold"]) - threshold) < 1e-9
        and row["risk_guard_level"] == risk_level
        and row["regime"] == regime
        and row["policy"] == policy
    )


def row_by_key(
    rows: list[dict[str, Any]],
    stage: str,
    threshold: float,
    risk_level: str,
    regime: str,
    policy: str,
) -> dict[str, Any]:
    return next(
        row
        for row in rows
        if row["stage"] == stage
        and abs(float(row["soft_utilization_threshold"]) - threshold) < 1e-9
        and row["risk_guard_level"] == risk_level
        and row["regime"] == regime
        and row["policy"] == policy
    )


def select_s2_settings(rows: list[dict[str, Any]]) -> list[Setting]:
    s1 = [row for row in rows if row["stage"] == "S1" and row["policy"] == "H4_BALANCED_RR_GUARD"]

    def guard_wins(row: dict[str, Any]) -> bool:
        h4 = row_by_key(rows, "S1", row["soft_utilization_threshold"], row["risk_guard_level"], row["regime"], "H4")
        rr = row_by_key(
            rows,
            "S1",
            row["soft_utilization_threshold"],
            row["risk_guard_level"],
            row["regime"],
            "BALANCED_RR_H4_PM",
        )
        return (
            float(row["total_tco_v4_soft_congestion"]) < float(h4["total_tco_v4_soft_congestion"])
            and float(row["total_tco_v4_soft_congestion"]) < float(rr["total_tco_v4_soft_congestion"])
        )

    candidates = sorted(
        s1,
        key=lambda row: (
            0 if guard_wins(row) else 1,
            0 if float(row["effective_fulfillment_rate"]) >= 0.99 else 1,
            float(row["total_tco_v4_soft_congestion"]),
        ),
    )

    selected: list[tuple[float, str]] = []

    def add(threshold: float, risk_level: str) -> None:
        pair = (round(threshold, 2), risk_level)
        if pair not in selected:
            selected.append(pair)

    add(0.90, "base")
    for risk_level in ["relaxed", "strict"]:
        best = min(
            [row for row in s1 if row["risk_guard_level"] == risk_level],
            key=lambda row: float(row["total_tco_v4_soft_congestion"]),
        )
        add(float(best["soft_utilization_threshold"]), str(best["risk_guard_level"]))
    for row in candidates:
        add(float(row["soft_utilization_threshold"]), str(row["risk_guard_level"]))
        if len(selected) >= 4:
            break

    return [
        Setting("S2", threshold, risk_level, 90, tuple(range(101, 111)), tuple(REGIMES))
        for threshold, risk_level in selected[:4]
    ]


def best_robust_setting(rows: list[dict[str, Any]]) -> tuple[float, str]:
    s2_guard = [row for row in rows if row["stage"] == "S2" and row["policy"] == "H4_BALANCED_RR_GUARD"]
    by_setting: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for row in s2_guard:
        by_setting.setdefault((float(row["soft_utilization_threshold"]), str(row["risk_guard_level"])), []).append(row)

    def score(item: tuple[tuple[float, str], list[dict[str, Any]]]) -> tuple[int, int, float, float]:
        setting, setting_rows = item
        wins = 0
        guardrails = 0
        tco = 0.0
        fallback = 0.0
        for row in setting_rows:
            h4 = row_by_key(rows, "S2", setting[0], setting[1], row["regime"], "H4")
            rr = row_by_key(rows, "S2", setting[0], setting[1], row["regime"], "BALANCED_RR_H4_PM")
            wins += int(
                float(row["total_tco_v4_soft_congestion"]) < float(h4["total_tco_v4_soft_congestion"])
                and float(row["total_tco_v4_soft_congestion"]) < float(rr["total_tco_v4_soft_congestion"])
            )
            guardrails += int(float(row["effective_fulfillment_rate"]) >= 0.99)
            tco += float(row["total_tco_v4_soft_congestion"])
            fallback += float(row["fallback_to_h4_count"])
        return (-wins, -guardrails, tco, fallback)

    if not by_setting:
        return (0.90, "base")
    return min(by_setting.items(), key=score)[0]


def write_report(rows: list[dict[str, Any]], guards: list[dict[str, Any]], raw_count: int) -> None:
    s1_rows = [row for row in rows if row["stage"] == "S1"]
    s2_rows = [row for row in rows if row["stage"] == "S2"]
    best_threshold, best_risk = best_robust_setting(rows)
    h5_justified = False
    if s2_rows:
        guard_rows_s2 = [row for row in s2_rows if row["policy"] == "H4_BALANCED_RR_GUARD"]
        h5_justified = all(
            float(row["total_tco_v4_soft_congestion"])
            < float(row_by_key(rows, "S2", float(row["soft_utilization_threshold"]), row["risk_guard_level"], row["regime"], "H4")["total_tco_v4_soft_congestion"])
            and float(row["total_tco_v4_soft_congestion"])
            < float(
                row_by_key(
                    rows,
                    "S2",
                    float(row["soft_utilization_threshold"]),
                    row["risk_guard_level"],
                    row["regime"],
                    "BALANCED_RR_H4_PM",
                )["total_tco_v4_soft_congestion"]
            )
            for row in guard_rows_s2
        )

    lines = [
        "# C5.54 Guard Sensitivity Analysis",
        "",
        "## Why This Sensitivity Was Needed",
        "",
        "`H4_BALANCED_RR_GUARD` won the Stage 2 base run, but guard skips and H4 fallback were active. This analysis checks whether that win is robust to utilization threshold and risk-guard settings before any H5 naming.",
        "",
        "## Stage 2 Base Recap",
        "",
        "- Base setting: `soft_utilization_threshold = 0.90`, `risk_guard_level = base`, percentile `0.90`.",
        "- Stage 2 base ranking was `H4_BALANCED_RR_GUARD`, then `BALANCED_RR_H4_PM`, then `H4` in all regimes.",
        "- Base guard behavior had high skip/fallback activity, route violations at zero, and risk/shovel guard dominance.",
        "",
        "## Execution Scope",
        "",
        f"- Raw sensitivity summary rows found: {raw_count}.",
        f"- S1 aggregated rows: {len(s1_rows)}.",
        f"- S2 aggregated rows: {len(s2_rows)}.",
        "",
        "## S1 Threshold and Risk-Guard Screening",
        "",
        "| threshold | risk | guard soft TCO | eff fulfillment | rank | guard skips/load | fallback/load | dominant guard |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(
        [row for row in s1_rows if row["policy"] == "H4_BALANCED_RR_GUARD"],
        key=lambda r: (float(r["soft_utilization_threshold"]), str(r["risk_guard_level"])),
    ):
        g = guard_row(
            guards,
            "S1",
            float(row["soft_utilization_threshold"]),
            row["risk_guard_level"],
            row["regime"],
            row["policy"],
        )
        lines.append(
            f"| {float(row['soft_utilization_threshold']):.2f} | {row['risk_guard_level']} | "
            f"{float(row['total_tco_v4_soft_congestion']):.1f} | "
            f"{float(row['effective_fulfillment_rate']):.3f} | "
            f"{int(row['rank_tco_v4_soft'])} | "
            f"{float(g['guard_skip_per_completed_load']):.3f} | "
            f"{float(g['fallback_per_completed_load']):.3f} | {g['dominant_guard']} |"
        )

    lines += [
        "",
        "## S2 TCO v4 Ranking by Setting and Regime",
        "",
        "| threshold | risk | regime | rank | policy | soft TCO v4 | eff fulfillment | hard h | soft h | failure | CM | downtime h |",
        "|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(
        s2_rows,
        key=lambda r: (
            float(r["soft_utilization_threshold"]),
            str(r["risk_guard_level"]),
            str(r["regime"]),
            int(r["rank_tco_v4_soft"]),
        ),
    ):
        lines.append(
            f"| {float(row['soft_utilization_threshold']):.2f} | {row['risk_guard_level']} | "
            f"{row['regime']} | {int(row['rank_tco_v4_soft'])} | {row['policy']} | "
            f"{float(row['total_tco_v4_soft_congestion']):.1f} | "
            f"{float(row['effective_fulfillment_rate']):.3f} | "
            f"{float(row['congestion_delay_hours_hard']):.2f} | "
            f"{float(row['congestion_delay_hours_soft']):.2f} | "
            f"{float(row['failure_count']):.1f} | {float(row['cm_count']):.1f} | "
            f"{float(row['downtime_hours']):.1f} |"
        )

    lines += [
        "",
        "## S2 Guard and Fallback Rates",
        "",
        "| threshold | risk | regime | skips/load | fallback/load | route viol/load | shovel viol/load | crusher viol/load | risk viol/load | dominant guard |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(
        [row for row in guards if row["stage"] == "S2" and row["policy"] == "H4_BALANCED_RR_GUARD"],
        key=lambda r: (
            float(r["soft_utilization_threshold"]),
            str(r["risk_guard_level"]),
            str(r["regime"]),
        ),
    ):
        lines.append(
            f"| {float(row['soft_utilization_threshold']):.2f} | {row['risk_guard_level']} | "
            f"{row['regime']} | {float(row['guard_skip_per_completed_load']):.3f} | "
            f"{float(row['fallback_per_completed_load']):.3f} | "
            f"{float(row['route_violation_per_completed_load']):.3f} | "
            f"{float(row['shovel_violation_per_completed_load']):.3f} | "
            f"{float(row['crusher_violation_per_completed_load']):.3f} | "
            f"{float(row['risk_violation_per_completed_load']):.3f} | {row['dominant_guard']} |"
        )

    route_zero = all(
        float(row["route_violation_per_completed_load"]) == 0.0
        for row in guards
        if row["policy"] == "H4_BALANCED_RR_GUARD"
    )
    lines += [
        "",
        "## Interpretation",
        "",
        f"- Best TCO-robust setting in S2: threshold `{best_threshold:.2f}`, risk `{best_risk}`.",
        "- `0.85/base` and `0.85/relaxed` improve normal-regime TCO but are not fully robust because `BALANCED_RR_H4_PM` remains slightly lower in `high_demand_high_stress`.",
        "- `0.90/base` remains a cleaner conservative reference: it beats both comparators in all S2 regimes with lower fallback dependence than `0.85/strict`.",
        "- `0.85/strict` beats both comparators in all S2 regimes, but its fallback rate is materially higher, so it should not be promoted without a final fallback-dependence review.",
        f"- Route violation remains zero across analyzed guard settings: {'yes' if route_zero else 'no'}.",
        "- `base` and `relaxed` risk levels often produce identical outcomes under the current route-risk surface, suggesting the percentile change does not always cross an active route-order boundary.",
        "- Risk/shovel dominance should be read by setting in the guard table; stricter risk settings are expected to increase risk-guard binding.",
        f"- H5 naming justified now: {'yes, strongly' if h5_justified else 'not yet; sensitivity evidence is supportive but should be reviewed before naming H5'}.",
        "",
        "## Recommended Next Step",
        "",
        f"Run a final confirmation comparing threshold `{best_threshold:.2f}`/risk `{best_risk}` against threshold `0.90`/risk `base` before creating H5.",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def analyze() -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    raw_rows = read_raw_rows()
    rows = aggregate(raw_rows)
    guards = guard_summary(rows)
    write_csv(policy_summary(rows), ANALYSIS_DIR / "c5_54_guard_sensitivity_summary.csv", SUMMARY_FIELDS)
    write_csv(guards, ANALYSIS_DIR / "c5_54_guard_sensitivity_guard_behavior.csv", GUARD_FIELDS)
    write_report(rows, guards, len(raw_rows))
    print(f"Wrote {ANALYSIS_DIR / 'c5_54_guard_sensitivity_summary.csv'}", flush=True)
    print(f"Wrote {ANALYSIS_DIR / 'c5_54_guard_sensitivity_guard_behavior.csv'}", flush=True)
    print(f"Wrote {REPORT_PATH}", flush=True)
    return rows, guards, len(raw_rows)


def parse_settings(value: str) -> list[tuple[float, str]]:
    settings: list[tuple[float, str]] = []
    for token in [item.strip() for item in value.split(",") if item.strip()]:
        threshold, risk = token.split(":", 1)
        settings.append((float(threshold), risk))
    return settings


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.54 guard threshold/risk sensitivity.")
    ap.add_argument("--stage", choices=["s1", "s2", "analyze", "all"], default="all")
    ap.add_argument(
        "--s2-settings",
        default=None,
        help="comma-separated threshold:risk entries, e.g. 0.90:base,0.85:relaxed",
    )
    args = ap.parse_args()

    if args.stage in {"s1", "all"}:
        for threshold in S1_THRESHOLDS:
            for risk_level in S1_RISK_LEVELS:
                run_setting(
                    Setting(
                        "S1",
                        threshold,
                        risk_level,
                        30,
                        (101, 102, 103),
                        ("heterogeneous_condition",),
                    )
                )
        analyze()

    if args.stage in {"s2", "all"}:
        rows, _, _ = analyze()
        if args.s2_settings:
            settings = [
                Setting("S2", threshold, risk, 90, tuple(range(101, 111)), tuple(REGIMES))
                for threshold, risk in parse_settings(args.s2_settings)
            ]
        else:
            settings = select_s2_settings(rows)
        print("Selected S2 settings:", ", ".join(f"{s.threshold:.2f}:{s.risk_level}" for s in settings), flush=True)
        for setting in settings:
            run_setting(setting)
        analyze()

    if args.stage == "analyze":
        analyze()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
