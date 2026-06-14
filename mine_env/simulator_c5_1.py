from __future__ import annotations

import csv
import json
import random
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mine_env.costs_c5_1 import C5_1CostModel
from mine_env.logger_c5_1 import write_policy_log
from mine_env.maintenance_c5_1 import C5_1MaintenanceModel
from mine_env.policies import create_policy
from mine_env.reliability_c5_1 import C5_1ReliabilityModel


SUMMARY_FIELDS = [
    "policy_id",
    "seed",
    "days",
    "total_demand",
    "completed_loads",
    "unmet_demand",
    "demand_fulfillment_rate",
    "total_cost",
    "total_cost_report_value",
    "pm_cost",
    "downtime_cost",
    "degradation_cost",
    "unmet_demand_cost",
    "breakdown_cost",
    "failure_count",
    "pm_count",
    "total_downtime_hours",
    "avg_queue_time",
    "availability_rate",
]


@dataclass(frozen=True)
class SimulationResult:
    policy_id: str
    seed: int
    records: list[dict[str, Any]]
    summary: dict[str, Any]


def generate_demand_scenario(
    config: dict[str, Any], seed: int, days: int | None = None
) -> list[int]:
    rng = random.Random(seed)
    horizon_days = int(days or config["simulation"]["horizon_days"])
    base_loads = int(config["demand"]["daily_loads"])
    variation = int(config["demand"]["daily_variation_loads"])
    return [
        max(0, base_loads + rng.randint(-variation, variation))
        for _ in range(horizon_days)
    ]


def build_initial_trucks(config: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed + 10_000)
    truck_count = int(config["mine"]["truck_count"])
    jitter = float(config["fleet"]["initial_hi_jitter"])
    trucks = []
    for index in range(truck_count):
        truck_hi = float(config["fleet"]["initial_truck_hi"]) - rng.random() * jitter
        tire_hi = float(config["fleet"]["initial_tire_hi"]) - rng.random() * jitter
        trucks.append(
            {
                "truck_id": f"T{index + 1:02d}",
                "truck_hi": round(max(truck_hi, 0.0), 4),
                "tire_hi": round(max(tire_hi, 0.0), 4),
                "pm_due_hours": float(config["fleet"]["pm_due_start_hours"])
                - rng.randint(0, 12),
                "truck_state": "STANDBY",
                "location": "Yard",
            }
        )
    return trucks


def _next_crusher(config: dict[str, Any], completed_loads: int) -> str:
    crusher_count = int(config["mine"]["crushers"])
    crusher_index = (completed_loads % crusher_count) + 1
    return f"Crusher {crusher_index}"


def _queue_time(config: dict[str, Any], completed_loads: int) -> float:
    return round(
        float(config["operations"]["base_queue_time_hours"])
        + completed_loads * float(config["operations"]["queue_time_per_load_hours"]),
        3,
    )


def _run_loads(config: dict[str, Any], completed_loads: int, daily_demand: int) -> int:
    remaining = max(daily_demand - completed_loads, 0)
    return min(int(config["operations"]["max_loads_per_truck_per_day"]), remaining)


def _apply_pm(
    truck: dict[str, Any],
    action: str,
    maintenance_model: C5_1MaintenanceModel,
    config: dict[str, Any],
) -> tuple[float, float]:
    maintenance_action = maintenance_model.resolve_action(action)
    if action == "PM_TIRE":
        truck["tire_hi"] = 1.0
        truck["truck_state"] = "PM"
    elif action == "PM_VEHICLE":
        truck["truck_hi"] = 1.0
        truck["pm_due_hours"] = float(config["fleet"]["pm_due_recovery_hours"])
        truck["truck_state"] = "PM"
    truck["location"] = "PM Bay"
    return maintenance_action.duration_hours, maintenance_action.cost_multiplier


def _apply_run(
    truck: dict[str, Any],
    loads: int,
    destination: str,
    config: dict[str, Any],
) -> float:
    truck_hi_loss = float(config["fleet"]["truck_hi_loss_per_load"]) * loads
    tire_hi_loss = float(config["fleet"]["tire_hi_loss_per_load"]) * loads
    truck["truck_hi"] = round(max(float(truck["truck_hi"]) - truck_hi_loss, 0.0), 4)
    truck["tire_hi"] = round(max(float(truck["tire_hi"]) - tire_hi_loss, 0.0), 4)
    truck["pm_due_hours"] = max(
        float(truck["pm_due_hours"])
        - float(config["fleet"]["pm_due_loss_per_load"]) * loads,
        0.0,
    )
    truck["truck_state"] = "DUMPING"
    truck["location"] = destination
    return truck_hi_loss + tire_hi_loss


def _apply_standby(
    truck: dict[str, Any],
    config: dict[str, Any],
    reliability: C5_1ReliabilityModel,
) -> None:
    recovery = reliability.standby_recovery(
        float(config["fleet"]["standby_hi_recovery"])
    )
    truck["truck_hi"] = round(min(float(truck["truck_hi"]) + recovery, 1.0), 4)
    truck["tire_hi"] = round(min(float(truck["tire_hi"]) + recovery, 1.0), 4)
    truck["truck_state"] = "STANDBY"
    truck["location"] = "Yard"


def _apply_breakdown(
    truck: dict[str, Any],
    breakdown: Any,
    config: dict[str, Any],
) -> None:
    # Reactive failure: only a partial health restore (NOT a free full-health PM), and the
    # truck is pulled offline (REPAIR) for the turn so its demand goes unmet.
    truck["truck_hi"] = round(breakdown.restored_truck_hi, 4)
    truck["tire_hi"] = round(breakdown.restored_tire_hi, 4)
    truck["pm_due_hours"] = float(config["fleet"]["pm_due_recovery_hours"])
    truck["truck_state"] = "REPAIR"
    truck["location"] = "PM Bay"


def _record(
    config: dict[str, Any],
    policy_id: str,
    day: int,
    decision: dict[str, Any],
    truck: dict[str, Any],
    payload_ton: float,
    produced_copper: float,
    pm_cost: float,
    downtime_hours: float,
    daily_demand: int,
    completed_loads: int,
    available_trucks: int,
    queue_time: float,
    total_cost: float,
    breakdown_events: int = 0,
) -> dict[str, Any]:
    return {
        "time": f"day_{day:03d}",
        "policy_id": policy_id,
        "truck_id": truck["truck_id"],
        "truck_state": truck["truck_state"],
        "location": truck["location"],
        "destination": decision.get("destination"),
        "action": decision["action"],
        "reason_code": decision["reason_code"],
        "payload_ton": round(payload_ton, 3),
        "ore_grade": float(config["demand"]["ore_grade"]),
        "produced_copper": round(produced_copper, 3),
        "truck_hi": round(float(truck["truck_hi"]), 4),
        "tire_hi": round(float(truck["tire_hi"]), 4),
        "pm_due_hours": round(float(truck["pm_due_hours"]), 3),
        "pm_cost": round(pm_cost, 6),
        "downtime_hours": round(downtime_hours, 3),
        "breakdown": int(breakdown_events),
        "daily_demand": float(daily_demand),
        "completed_loads": float(completed_loads),
        "available_trucks": float(available_trucks),
        "queue_time": round(queue_time, 3),
        "total_cost": round(total_cost, 6),
    }


def run_policy_simulation(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    demand_scenario: list[int] | None = None,
    days: int | None = None,
) -> SimulationResult:
    horizon_days = int(days or config["simulation"]["horizon_days"])
    scenario = demand_scenario or generate_demand_scenario(config, seed, horizon_days)
    scenario = scenario[:horizon_days]
    policy = create_policy(policy_id, config)
    cost_model = C5_1CostModel(config)
    maintenance_model = C5_1MaintenanceModel(config)
    reliability = C5_1ReliabilityModel(config)
    breakdown_rng = random.Random(seed + 20_000)
    trucks = build_initial_trucks(config, seed)

    records: list[dict[str, Any]] = []
    total_cost = 0.0
    pm_cost_total = 0.0
    downtime_cost_total = 0.0
    degradation_cost_total = 0.0
    unmet_demand_cost_total = 0.0
    breakdown_cost_total = 0.0
    total_downtime_hours = 0.0
    pm_count_total = 0
    failure_count_total = 0
    unmet_demand_total = 0
    total_demand = 0
    completed_total = 0
    queue_time_samples: list[float] = []
    availability_samples: list[int] = []

    for day, daily_demand in enumerate(scenario, start=1):
        completed_loads = 0
        pm_actions_today = 0
        remaining_truck_ids = [truck["truck_id"] for truck in trucks]

        while remaining_truck_ids:
            queue_time = _queue_time(config, completed_loads)
            state = {
                "day": day,
                "seed": seed,
                "daily_demand": daily_demand,
                "completed_loads": completed_loads,
                "queue_time": queue_time,
                "available_trucks": len(remaining_truck_ids),
                "remaining_truck_ids": remaining_truck_ids.copy(),
                "next_crusher": _next_crusher(config, completed_loads),
                "trucks": deepcopy(trucks),
            }
            decision = policy.decide(state)
            selected_id = decision["truck_id"]
            if selected_id not in remaining_truck_ids:
                selected_id = remaining_truck_ids[0]
                decision["truck_id"] = selected_id

            truck = next(item for item in trucks if item["truck_id"] == selected_id)
            remaining_truck_ids.remove(selected_id)

            action = decision["action"]
            loads = 0
            payload_ton = 0.0
            produced_copper = 0.0
            downtime_hours = 0.0
            pm_cost = 0.0
            hi_loss = 0.0
            breakdown_events = 0

            if (
                action in {"PM_TIRE", "PM_VEHICLE"}
                and pm_actions_today >= maintenance_model.pm_bay_capacity
            ):
                action = "STANDBY"
                decision["action"] = action
                decision["destination"] = None
                decision["reason_code"] = "PM_BAY_CAPACITY_FULL"

            if action in {"RUN_TO_SHOVEL", "RUN_TO_CRUSHER"}:
                loads = _run_loads(config, completed_loads, daily_demand)
                if loads == 0:
                    action = "STANDBY"
                    decision["action"] = action
                    decision["destination"] = None
                    decision["reason_code"] = "DEMAND_ALREADY_MET"
                    _apply_standby(truck, config, reliability)
                else:
                    breakdown = (
                        reliability.maybe_breakdown(truck, breakdown_rng)
                        if reliability.enabled
                        else None
                    )
                    if breakdown is not None:
                        # Health-driven failure overrides the dispatch: nothing is hauled
                        # this turn (its loads fall to unmet demand) and a breakdown cost
                        # plus repair downtime is incurred.
                        _apply_breakdown(truck, breakdown, config)
                        downtime_hours = breakdown.downtime_hours
                        breakdown_events = 1
                        loads = 0
                        decision["destination"] = None
                        decision["reason_code"] = f"BREAKDOWN_{breakdown.trigger}"
                    else:
                        destination = decision.get("destination") or _next_crusher(
                            config, completed_loads
                        )
                        decision["destination"] = destination
                        hi_loss = _apply_run(truck, loads, destination, config)
                        completed_loads += loads
                        payload_ton = loads * float(
                            config["mine"]["truck_avg_payload_ton"]
                        )
                        produced_copper = payload_ton * float(
                            config["demand"]["ore_grade"]
                        )
            elif action in {"PM_TIRE", "PM_VEHICLE"}:
                downtime_hours, _ = _apply_pm(truck, action, maintenance_model, config)
                pm_cost = cost_model.pm_cost(action)
                pm_actions_today += 1
                pm_count_total += 1
            else:
                _apply_standby(truck, config, reliability)

            step_cost = cost_model.step_cost(
                action,
                downtime_hours=downtime_hours,
                hi_loss=hi_loss,
                breakdown_events=breakdown_events,
            )
            total_cost += step_cost.total
            pm_cost_total += step_cost.pm_cost
            downtime_cost_total += step_cost.downtime_cost
            degradation_cost_total += step_cost.degradation_cost
            breakdown_cost_total += step_cost.breakdown_cost
            total_downtime_hours += downtime_hours
            failure_count_total += breakdown_events
            queue_time_samples.append(queue_time)
            availability_samples.append(
                sum(
                    1
                    for item in trucks
                    if item["truck_state"] not in {"PM", "REPAIR"}
                )
            )

            records.append(
                _record(
                    config,
                    policy_id,
                    day,
                    decision,
                    truck,
                    payload_ton,
                    produced_copper,
                    pm_cost,
                    downtime_hours,
                    daily_demand,
                    completed_loads,
                    len(remaining_truck_ids),
                    queue_time,
                    total_cost,
                    breakdown_events,
                )
            )

        unmet = max(daily_demand - completed_loads, 0)
        unmet_cost = cost_model.unmet_demand_cost(unmet)
        total_cost += unmet_cost
        unmet_demand_cost_total += unmet_cost
        if records:
            records[-1]["total_cost"] = round(total_cost, 6)
        unmet_demand_total += unmet
        total_demand += daily_demand
        completed_total += completed_loads

    fulfillment = completed_total / total_demand if total_demand else 1.0
    summary = {
        "policy_id": policy_id,
        "seed": seed,
        "days": horizon_days,
        "total_demand": total_demand,
        "completed_loads": completed_total,
        "unmet_demand": unmet_demand_total,
        "demand_fulfillment_rate": round(fulfillment, 6),
        "total_cost": round(total_cost, 6),
        "total_cost_report_value": round(cost_model.to_report_value(total_cost), 3),
        "pm_cost": round(pm_cost_total, 6),
        "downtime_cost": round(downtime_cost_total, 6),
        "degradation_cost": round(degradation_cost_total, 6),
        "unmet_demand_cost": round(unmet_demand_cost_total, 6),
        "breakdown_cost": round(breakdown_cost_total, 6),
        "failure_count": failure_count_total,
        "pm_count": pm_count_total,
        "total_downtime_hours": round(total_downtime_hours, 6),
        "avg_queue_time": round(
            sum(queue_time_samples) / len(queue_time_samples), 6
        )
        if queue_time_samples
        else 0.0,
        "availability_rate": round(
            sum(availability_samples)
            / (len(availability_samples) * max(len(trucks), 1)),
            6,
        )
        if availability_samples
        else 1.0,
    }
    return SimulationResult(policy_id=policy_id, seed=seed, records=records, summary=summary)


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "policy_comparison.csv"
    json_path = target_dir / "policy_comparison.json"

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
    log_dir: str | Path,
    summary_dir: str | Path,
    days: int | None = None,
) -> list[dict[str, Any]]:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, Any]] = []

    for seed in seeds:
        scenario = generate_demand_scenario(config, seed, days)
        for policy_id in policies:
            result = run_policy_simulation(
                config,
                policy_id=policy_id,
                seed=seed,
                demand_scenario=scenario,
                days=days,
            )
            payload = {
                "schema": "c5_1_policy_log_v1",
                "policy_id": policy_id,
                "seed": seed,
                "demand_scenario": scenario,
                "summary": result.summary,
                "records": result.records,
            }
            write_policy_log(log_path / f"{policy_id}_seed_{seed}.json", payload)
            summary_rows.append(result.summary)

    write_summary(summary_rows, summary_dir)
    return summary_rows
