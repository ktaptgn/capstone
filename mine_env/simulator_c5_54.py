from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from mine_env.policies_c5_54 import GUARD_METRIC_KEYS, create_route_allocation_policy
from mine_env.simulator_c5_53 import (
    DAILY_RECORD_FIELDS,
    DISPATCH_EVENT_FIELDS,
    SUMMARY_FIELDS as C5_53_SUMMARY_FIELDS,
    run_policy_simulation as _run_c5_53_policy_simulation,
    write_route_cycle_time_table,
)

SUMMARY_FIELDS = C5_53_SUMMARY_FIELDS + list(GUARD_METRIC_KEYS)


def _guard_metrics(policy: Any) -> dict[str, int]:
    if hasattr(policy, "guard_metrics"):
        values = policy.guard_metrics()
    else:
        values = {}
    return {key: int(values.get(key, 0)) for key in GUARD_METRIC_KEYS}


def run_policy_simulation(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    days: int | None = None,
    shortfall_sensitivity: str = "base",
    congestion_alpha: float | None = None,
    congestion_beta: float | None = None,
    congestion_cost_level: str | None = None,
    record_daily: bool = False,
    record_events: bool = False,
):
    """Run one C5.54 route-allocation policy by injecting it into the C5.53 simulator."""
    policy = create_route_allocation_policy(policy_id, config)
    result = _run_c5_53_policy_simulation(
        config,
        policy_id=policy_id,
        seed=seed,
        days=days,
        record_daily=record_daily,
        policy=policy,
        record_events=record_events,
        shortfall_sensitivity=shortfall_sensitivity,
        congestion_alpha=congestion_alpha,
        congestion_beta=congestion_beta,
        congestion_cost_level=congestion_cost_level,
    )
    result.summary.update(_guard_metrics(policy))
    return result


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_54_policy_comparison.csv"
    json_path = target_dir / "c5_54_policy_comparison.json"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary_rows)
    with json_path.open("w", encoding="utf-8") as stream:
        json.dump(summary_rows, stream, indent=2)


def write_daily_records(daily_rows: list[dict[str, Any]], log_dir: str | Path) -> Path:
    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_54_daily_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=DAILY_RECORD_FIELDS)
        writer.writeheader()
        writer.writerows(daily_rows)
    return csv_path


def write_dispatch_events(event_rows: list[dict[str, Any]], log_dir: str | Path) -> Path:
    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_54_dispatch_events.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=DISPATCH_EVENT_FIELDS)
        writer.writeheader()
        writer.writerows(event_rows)
    return csv_path


__all__ = [
    "SUMMARY_FIELDS",
    "run_policy_simulation",
    "write_summary",
    "write_daily_records",
    "write_dispatch_events",
    "write_route_cycle_time_table",
]
