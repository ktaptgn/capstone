from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from mine_env.policies_c5_52 import create_grade_aware_policy
from mine_env.simulator_c5_51 import SUMMARY_FIELDS as C5_51_SUMMARY_FIELDS
from mine_env.simulator_c5_51 import run_policy_simulation as _run_c5_51_simulation

GRADE_AWARE_FIELDS = [
    "shortfall_sensitivity",
    "target_effective_output",
    "effective_output_shortfall",
    "effective_output_shortfall_cost",
    "effective_fulfillment_rate",
    "avg_grade_per_load",
    "total_tco_v1",
    "total_tco_v2",
    "total_tco_v2_report_value",
]

SUMMARY_FIELDS = C5_51_SUMMARY_FIELDS + GRADE_AWARE_FIELDS


def _target_effective_output(config: dict[str, Any], total_demand: float) -> float:
    grade_cfg = config.get("grade_aware_objective", {})
    target_grade = float(
        grade_cfg.get(
            "target_effective_grade_index",
            config["demand"].get("target_effective_grade_index", 0.80),
        )
    )
    return float(total_demand) * float(config["mine"]["payload_ton"]) * target_grade


def _shortfall_cost_rate(config: dict[str, Any], sensitivity: str) -> float:
    rates = config["grade_aware_objective"]["shortfall_cost_sensitivity"]
    if sensitivity not in rates:
        raise ValueError(f"Unknown C5.52 shortfall sensitivity: {sensitivity}")
    return float(rates[sensitivity])


def _augment_summary(
    config: dict[str, Any],
    summary: dict[str, Any],
    shortfall_sensitivity: str,
) -> dict[str, Any]:
    out = dict(summary)
    total_demand = float(out["total_demand"])
    completed = float(out["completed_loads"])
    effective_output = float(out["effective_output"])
    target_effective = _target_effective_output(config, total_demand)
    shortfall = max(target_effective - effective_output, 0.0)
    rate = _shortfall_cost_rate(config, shortfall_sensitivity)
    shortfall_cost = shortfall * rate
    total_tco_v1 = float(out["total_tco"])
    total_tco_v2 = total_tco_v1 + shortfall_cost
    avg_grade = (
        effective_output / (completed * float(config["mine"]["payload_ton"]))
        if completed > 0
        else 0.0
    )
    report_multiplier = float(config["simulation"]["report_value_multiplier"])

    out.update(
        {
            "shortfall_sensitivity": shortfall_sensitivity,
            "target_effective_output": round(target_effective, 3),
            "effective_output_shortfall": round(shortfall, 3),
            "effective_output_shortfall_cost": round(shortfall_cost, 6),
            "effective_fulfillment_rate": round(
                effective_output / target_effective if target_effective else 1.0, 6
            ),
            "avg_grade_per_load": round(avg_grade, 6),
            "total_tco_v1": round(total_tco_v1, 6),
            "total_tco_v2": round(total_tco_v2, 6),
            "total_tco_v2_report_value": round(total_tco_v2 * report_multiplier, 3),
        }
    )
    return out


def run_policy_simulation(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    days: int | None = None,
    shortfall_sensitivity: str = "base",
    record_daily: bool = False,
    record_events: bool = False,
):
    """Run C5.52 by injecting C5.52 policies into the C5.51 route simulator."""
    policy = create_grade_aware_policy(policy_id, config)
    result = _run_c5_51_simulation(
        config,
        policy_id=policy_id,
        seed=seed,
        days=days,
        record_daily=record_daily,
        policy=policy,
        record_events=record_events,
    )
    result.summary = _augment_summary(config, result.summary, shortfall_sensitivity)
    return result


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_52_policy_comparison.csv"
    json_path = target_dir / "c5_52_policy_comparison.json"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary_rows)
    with json_path.open("w", encoding="utf-8") as stream:
        json.dump(summary_rows, stream, indent=2)


def run_policy_sweep(
    config: dict[str, Any],
    policies: list[str],
    seeds: list[int],
    sensitivities: list[str],
    summary_dir: str | Path | None = None,
    days: int | None = None,
) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []
    for sensitivity in sensitivities:
        for seed in seeds:
            for policy_id in policies:
                result = run_policy_simulation(
                    config,
                    policy_id=policy_id,
                    seed=seed,
                    days=days,
                    shortfall_sensitivity=sensitivity,
                )
                summary_rows.append(result.summary)
    if summary_dir is not None:
        write_summary(summary_rows, summary_dir)
    return summary_rows
