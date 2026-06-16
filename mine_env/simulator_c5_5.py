from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from mine_env.costs_c5_4 import C5_4CostModel
from mine_env.policies_c5_5 import (
    CRUSHER_ACTION_TO_ID,
    SHOVEL_ACTION_TO_ID,
    create_facility_policy,
)
from mine_env.reliability_c5_4 import COMPONENTS, C5_4ReliabilityModel

SHOVELS = ("SHOVEL_A", "SHOVEL_B", "SHOVEL_C")
CRUSHERS = ("CRUSHER_1", "CRUSHER_2")

SUMMARY_FIELDS = [
    "policy_id",
    "regime",
    "seed",
    "days",
    "total_demand",
    "completed_loads",
    "unmet_demand",
    "demand_fulfillment_rate",
    "effective_output",
    "total_tco",
    "total_tco_report_value",
    "pm_cost",
    "cm_cost",
    "downtime_cost",
    "degradation_cost",
    "unmet_demand_cost",
    "pm_count",
    "pm_component_count",
    "pm_tire",
    "pm_engine",
    "pm_brake",
    "cm_count",
    "cm_tire",
    "cm_engine",
    "cm_brake",
    "failure_count",
    "total_downtime_hours",
    "avg_truck_hi",
    "avg_tire_hi",
    "avg_engine_hi",
    "avg_brake_hi",
    "avg_frailty",
    "max_frailty",
    "availability_rate",
    "shovel_a_loads",
    "shovel_b_loads",
    "shovel_c_loads",
    "crusher_1_loads",
    "crusher_2_loads",
    "pm_bay_utilization",
    "max_simultaneous_pm",
    "standby_reserve_activations",
    "standby_decisions",
]


@dataclass
class C5_5Result:
    policy_id: str
    seed: int
    summary: dict[str, Any]
    daily_records: list[dict[str, Any]] = field(default_factory=list)
    event_log: list[dict[str, Any]] = field(default_factory=list)
    failure_log: list[dict[str, Any]] = field(default_factory=list)


def _build_trucks(
    config: dict[str, Any], reliability: C5_4ReliabilityModel, rng: np.random.Generator
) -> list[dict[str, Any]]:
    count = int(config["mine"]["truck_count"])
    operating_count = int(config["mine"]["operating_truck_count"])
    initial = reliability.initial_hi()
    trucks: list[dict[str, Any]] = []
    for index in range(count):
        frailty = reliability.draw_frailty(rng)
        is_operating = index < operating_count
        truck: dict[str, Any] = {
            "truck_id": f"T{index + 1:02d}",
            "role": "OPERATING" if is_operating else "STANDBY_RESERVE",
            "status": "AVAILABLE_EMPTY" if is_operating else "STANDBY_RESERVE",
            "downtime_remaining": 0,
            "load_origin": None,
            "assigned_destination": None,
            "loads_completed": 0,
            "operating_hours_since_pm": 0.0,
            "last_pm_day": 0,
            "pm_event_count": 0,
        }
        for component in COMPONENTS:
            truck[f"{component}_hi"] = initial[component]
            truck[f"{component}_wear_multiplier"] = frailty[component]
        reliability.truck_hi(truck)
        reliability.observe(truck, rng)
        trucks.append(truck)
    return trucks


def _pm_capacity(config: dict[str, Any]) -> int:
    return int(config["mine"].get("pm_service_capacity", config["mine"].get("pm_bay_count", 1)))


def _apply_pm_visit(
    truck: dict[str, Any],
    components: tuple[str, ...],
    day: int,
    cost_model: C5_4CostModel,
    reliability: C5_4ReliabilityModel,
    totals: dict[str, float],
    counts: dict[str, int],
) -> None:
    total_cost = 0.0
    total_duration = 0.0
    for component in components:
        rec = cost_model.pm[component]
        truck[f"{component}_hi"] = min(truck[f"{component}_hi"] + rec["recovery"], reliability.max_hi)
        total_cost += rec["cost"]
        total_duration += rec["duration"]
        counts["pm_component_count"] += 1
        counts[f"pm_{component}"] += 1
    reliability.truck_hi(truck)
    truck["status"] = "PM"
    truck["downtime_remaining"] = max(int(round(total_duration)), 1)
    truck["operating_hours_since_pm"] = 0.0
    truck["last_pm_day"] = day
    truck["pm_event_count"] += 1
    truck["load_origin"] = None
    truck["assigned_destination"] = "PM_BAY"
    totals["pm"] += total_cost
    counts["pm_count"] += 1


def _apply_cm(
    truck: dict[str, Any],
    failed: list[str],
    day: int,
    hour: int,
    step: int,
    destination: str,
    cost_model: C5_4CostModel,
    reliability: C5_4ReliabilityModel,
    totals: dict[str, float],
    counts: dict[str, int],
    failure_log: list[dict[str, Any]],
    record_events: bool,
) -> None:
    max_duration = 0.0
    for component in failed:
        cm = cost_model.cm[component]
        truck[f"{component}_hi"] = min(truck[f"{component}_hi"] + cm["recovery"], reliability.max_hi)
        totals["cm"] += cm["cost"]
        counts["cm_count"] += 1
        counts[f"cm_{component}"] += 1
        counts["failure_count"] += 1
        max_duration = max(max_duration, cm["duration"])
        if record_events:
            failure_log.append(
                {
                    "day": day,
                    "hour": hour,
                    "step": step,
                    "truck_id": truck["truck_id"],
                    "component": component,
                    "destination": destination,
                    "truck_hi_after": round(float(truck[f"{component}_hi"]), 4),
                }
            )
    reliability.truck_hi(truck)
    truck["status"] = "CM"
    truck["downtime_remaining"] = max(int(round(max_duration)), 1)
    truck["load_origin"] = None
    truck["assigned_destination"] = "CM"


def _combined_crusher_profile(config: dict[str, Any], truck: dict[str, Any], crusher_id: str) -> dict[str, Any]:
    crusher = dict(config["facilities"]["crushers"][crusher_id])
    origin = truck.get("load_origin")
    if not origin:
        return crusher
    shovel = config["facilities"]["shovels"][origin]
    hardness = float(shovel.get("hardness_factor", 1.0))
    for component in COMPONENTS:
        key = f"{component}_wear_multiplier"
        crusher[key] = float(crusher.get(key, 1.0)) * (0.75 + 0.25 * hardness)
    return crusher


def _first_valid_action(
    ranked_actions: list[str],
    valid: set[str],
    capacity_remaining: dict[str, int],
    action_to_id: dict[str, str],
) -> str | None:
    for action in ranked_actions:
        if action not in valid:
            continue
        facility_id = action_to_id.get(action)
        if facility_id is None or capacity_remaining.get(facility_id, 0) > 0:
            return action
    return None


def run_policy_simulation(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    days: int | None = None,
    record_daily: bool = False,
    policy: Any | None = None,
    record_events: bool = False,
) -> C5_5Result:
    """Run one C5.5 facility-destination policy for one seed."""
    reliability = C5_4ReliabilityModel(config)
    cost_model = C5_4CostModel(config)
    if policy is None:
        policy = create_facility_policy(policy_id, config)

    rng = np.random.default_rng(seed)
    trucks = _build_trucks(config, reliability, rng)
    by_id = {truck["truck_id"]: truck for truck in trucks}
    fleet_size = len(trucks)
    sim = config["simulation"]
    total_days = int(days or sim["horizon_days"])
    steps_per_day = int(config["demand"]["operating_hours_per_day"])
    daily_demand = int(config["demand"]["daily_demand_loads"])
    per_step_cap = max(int(math.ceil(daily_demand / steps_per_day)), 1)
    pm_capacity = _pm_capacity(config)

    totals = {"pm": 0.0, "cm": 0.0, "downtime": 0.0, "degradation": 0.0, "unmet": 0.0}
    counts = {
        "pm_count": 0,
        "pm_component_count": 0,
        "pm_tire": 0,
        "pm_engine": 0,
        "pm_brake": 0,
        "cm_count": 0,
        "cm_tire": 0,
        "cm_engine": 0,
        "cm_brake": 0,
        "failure_count": 0,
        "completed_loads": 0,
        "unmet_loads": 0,
        "total_demand": 0,
        "downtime_hours": 0,
        "standby_reserve_activations": 0,
        "standby_decisions": 0,
    }
    shovel_loads = {sid: 0 for sid in SHOVELS}
    crusher_loads = {cid: 0 for cid in CRUSHERS}
    effective_output = 0.0
    pm_slot_hours = 0
    max_simultaneous_pm = 0
    availability_samples: list[int] = []
    daily_records: list[dict[str, Any]] = []
    event_log: list[dict[str, Any]] = []
    failure_log: list[dict[str, Any]] = []

    policy.reset()
    global_step = 0

    for day in range(1, total_days + 1):
        demand_remaining = daily_demand
        counts["total_demand"] += daily_demand
        completed_today = 0
        shovel_cap = {
            sid: int(config["facilities"]["shovels"][sid]["capacity_loads_per_day"])
            for sid in SHOVELS
        }
        crusher_cap = {
            cid: int(config["facilities"]["crushers"][cid]["capacity_loads_per_day"])
            for cid in CRUSHERS
        }

        for hour in range(steps_per_day):
            global_step += 1

            for truck in trucks:
                if truck["downtime_remaining"] > 0:
                    truck["downtime_remaining"] -= 1
                    totals["downtime"] += cost_model.downtime_rate
                    counts["downtime_hours"] += 1
                    if truck["downtime_remaining"] <= 0:
                        truck["status"] = "AVAILABLE_EMPTY"
                        truck["assigned_destination"] = None

            active_serviceable = sum(
                1
                for t in trucks
                if t["status"] in {"AVAILABLE_EMPTY", "LOADED", "PM", "CM"} and t["role"] != "STANDBY_RESERVE"
            )
            target_operating = int(config["mine"]["operating_truck_count"])
            for truck in trucks:
                if active_serviceable >= target_operating or demand_remaining <= 0:
                    break
                if truck["status"] == "STANDBY_RESERVE":
                    truck["status"] = "AVAILABLE_EMPTY"
                    truck["role"] = "RESERVE_ACTIVE"
                    counts["standby_reserve_activations"] += 1
                    active_serviceable += 1

            for truck in trucks:
                reliability.observe(truck, rng)

            available_empty = [t for t in trucks if t["status"] == "AVAILABLE_EMPTY"]
            loaded = [t for t in trucks if t["status"] == "LOADED"]
            available_ids = {t["truck_id"] for t in available_empty}
            availability_samples.append(len(available_empty) + len(loaded))
            in_pm = sum(1 for t in trucks if t["status"] == "PM")
            max_simultaneous_pm = max(max_simultaneous_pm, in_pm)
            pm_slot_hours += in_pm
            free_bays = max(pm_capacity - in_pm, 0)
            slots = min(per_step_cap, demand_remaining)

            state = {
                "trucks": trucks,
                "available_ids": available_ids,
                "step": global_step,
                "free_bays": free_bays,
                "pm_context": {
                    "day": day,
                    "hour": hour,
                    "step": global_step,
                    "demand_remaining": demand_remaining,
                    "slots_this_step": slots,
                    "available_count": len(available_empty),
                },
                "dispatch_state": {
                    "dispatch_trucks": available_empty + loaded,
                    "shovel_capacity_remaining": shovel_cap,
                    "crusher_capacity_remaining": crusher_cap,
                    "demand_remaining": demand_remaining,
                    "day": day,
                    "hour": hour,
                },
            }
            decision = policy.decide(state)

            pm_ids: set[str] = set()
            applied = 0
            for truck_id, components, _risk in decision.get("pm", []):
                if applied >= free_bays:
                    break
                if truck_id in pm_ids or truck_id not in available_ids:
                    continue
                _apply_pm_visit(
                    by_id[truck_id],
                    tuple(components),
                    day,
                    cost_model,
                    reliability,
                    totals,
                    counts,
                )
                applied += 1
                pm_ids.add(truck_id)

            remaining_pm_slots = max(free_bays - applied, 0)
            dispatch_map = dict(decision.get("dispatch", []))

            for truck in list(available_empty):
                if truck["truck_id"] in pm_ids or truck["status"] != "AVAILABLE_EMPTY":
                    continue
                ranked = dispatch_map.get(truck["truck_id"], [])
                action = _first_valid_action(
                    ranked,
                    set(SHOVEL_ACTION_TO_ID) | {"SEND_TO_PM_BAY", "STANDBY"},
                    shovel_cap,
                    SHOVEL_ACTION_TO_ID,
                )
                if action == "SEND_TO_PM_BAY" and remaining_pm_slots > 0:
                    weakest = min(COMPONENTS, key=lambda c: float(truck[f"observed_{c}_hi"]))
                    _apply_pm_visit(truck, (weakest,), day, cost_model, reliability, totals, counts)
                    remaining_pm_slots -= 1
                elif action in SHOVEL_ACTION_TO_ID:
                    shovel_id = SHOVEL_ACTION_TO_ID[action]
                    shovel = config["facilities"]["shovels"][shovel_id]
                    losses = reliability.apply_route_wear(truck, shovel, rng)
                    totals["degradation"] += cost_model.degradation_cost(losses)
                    truck["operating_hours_since_pm"] += 0.5
                    failed = reliability.check_failures(truck, rng)
                    if failed:
                        _apply_cm(
                            truck,
                            failed,
                            day,
                            hour,
                            global_step,
                            shovel_id,
                            cost_model,
                            reliability,
                            totals,
                            counts,
                            failure_log,
                            record_events,
                        )
                    else:
                        shovel_cap[shovel_id] -= 1
                        shovel_loads[shovel_id] += 1
                        truck["status"] = "LOADED"
                        truck["load_origin"] = shovel_id
                        truck["assigned_destination"] = shovel_id
                        if record_events:
                            event_log.append(
                                {
                                    "day": day,
                                    "hour": hour,
                                    "step": global_step,
                                    "truck_id": truck["truck_id"],
                                    "event": "loaded",
                                    "facility": shovel_id,
                                }
                            )
                else:
                    counts["standby_decisions"] += 1

            crusher_attempts = 0
            for truck in list(loaded):
                if truck["status"] != "LOADED" or demand_remaining <= 0 or crusher_attempts >= slots:
                    continue
                ranked = dispatch_map.get(truck["truck_id"], [])
                action = _first_valid_action(
                    ranked,
                    set(CRUSHER_ACTION_TO_ID) | {"EMERGENCY_PM", "SAFE_STOP"},
                    crusher_cap,
                    CRUSHER_ACTION_TO_ID,
                )
                if action in {"EMERGENCY_PM", "SAFE_STOP"}:
                    weakest = min(COMPONENTS, key=lambda c: float(truck[f"observed_{c}_hi"]))
                    if action == "EMERGENCY_PM" and remaining_pm_slots > 0:
                        _apply_pm_visit(truck, (weakest,), day, cost_model, reliability, totals, counts)
                        remaining_pm_slots -= 1
                    else:
                        truck["assigned_destination"] = action
                    continue
                if action not in CRUSHER_ACTION_TO_ID:
                    continue
                crusher_id = CRUSHER_ACTION_TO_ID[action]
                crusher_profile = _combined_crusher_profile(config, truck, crusher_id)
                losses = reliability.apply_route_wear(truck, crusher_profile, rng)
                totals["degradation"] += cost_model.degradation_cost(losses)
                truck["operating_hours_since_pm"] += 0.5
                failed = reliability.check_failures(truck, rng)
                crusher_attempts += 1
                if failed:
                    _apply_cm(
                        truck,
                        failed,
                        day,
                        hour,
                        global_step,
                        crusher_id,
                        cost_model,
                        reliability,
                        totals,
                        counts,
                        failure_log,
                        record_events,
                    )
                    continue
                origin = truck.get("load_origin") or "SHOVEL_B"
                grade_index = float(config["facilities"]["shovels"][origin]["grade_index"])
                effective_output += float(config["mine"]["payload_ton"]) * grade_index
                demand_remaining -= 1
                completed_today += 1
                crusher_cap[crusher_id] -= 1
                crusher_loads[crusher_id] += 1
                counts["completed_loads"] += 1
                truck["loads_completed"] += 1
                truck["status"] = "AVAILABLE_EMPTY"
                truck["load_origin"] = None
                truck["assigned_destination"] = crusher_id
                if record_events:
                    event_log.append(
                        {
                            "day": day,
                            "hour": hour,
                            "step": global_step,
                            "truck_id": truck["truck_id"],
                            "event": "dumped",
                            "facility": crusher_id,
                        }
                    )

        unmet = max(demand_remaining, 0)
        totals["unmet"] += cost_model.unmet_demand_cost(unmet)
        counts["unmet_loads"] += unmet
        if record_daily:
            daily_records.append(
                {
                    "day": day,
                    "completed": completed_today,
                    "unmet": unmet,
                    "pm_count": counts["pm_count"],
                    "cm_count": counts["cm_count"],
                    "failure_count": counts["failure_count"],
                    "avg_truck_hi": round(float(np.mean([reliability.truck_hi(t) for t in trucks])), 4),
                }
            )

    total_tco = sum(totals.values())
    fulfillment = counts["completed_loads"] / counts["total_demand"] if counts["total_demand"] else 1.0
    frailty_vals = [
        float(truck[f"{component}_wear_multiplier"])
        for truck in trucks
        for component in COMPONENTS
    ]
    total_steps = max(total_days * steps_per_day, 1)
    summary = {
        "policy_id": policy_id,
        "regime": config.get("active_regime"),
        "seed": seed,
        "days": total_days,
        "total_demand": counts["total_demand"],
        "completed_loads": counts["completed_loads"],
        "unmet_demand": counts["unmet_loads"],
        "demand_fulfillment_rate": round(fulfillment, 6),
        "effective_output": round(effective_output, 3),
        "total_tco": round(total_tco, 6),
        "total_tco_report_value": round(cost_model.to_report_value(total_tco), 3),
        "pm_cost": round(totals["pm"], 6),
        "cm_cost": round(totals["cm"], 6),
        "downtime_cost": round(totals["downtime"], 6),
        "degradation_cost": round(totals["degradation"], 6),
        "unmet_demand_cost": round(totals["unmet"], 6),
        "pm_count": counts["pm_count"],
        "pm_component_count": counts["pm_component_count"],
        "pm_tire": counts["pm_tire"],
        "pm_engine": counts["pm_engine"],
        "pm_brake": counts["pm_brake"],
        "cm_count": counts["cm_count"],
        "cm_tire": counts["cm_tire"],
        "cm_engine": counts["cm_engine"],
        "cm_brake": counts["cm_brake"],
        "failure_count": counts["failure_count"],
        "total_downtime_hours": counts["downtime_hours"],
        "avg_truck_hi": round(float(np.mean([reliability.truck_hi(t) for t in trucks])), 6),
        "avg_tire_hi": round(float(np.mean([t["tire_hi"] for t in trucks])), 6),
        "avg_engine_hi": round(float(np.mean([t["engine_hi"] for t in trucks])), 6),
        "avg_brake_hi": round(float(np.mean([t["brake_hi"] for t in trucks])), 6),
        "avg_frailty": round(float(np.mean(frailty_vals)), 6),
        "max_frailty": round(float(np.max(frailty_vals)), 6),
        "availability_rate": round(float(np.mean(availability_samples)) / max(fleet_size, 1), 6)
        if availability_samples
        else 1.0,
        "shovel_a_loads": shovel_loads["SHOVEL_A"],
        "shovel_b_loads": shovel_loads["SHOVEL_B"],
        "shovel_c_loads": shovel_loads["SHOVEL_C"],
        "crusher_1_loads": crusher_loads["CRUSHER_1"],
        "crusher_2_loads": crusher_loads["CRUSHER_2"],
        "pm_bay_utilization": round(pm_slot_hours / max(pm_capacity * total_steps, 1), 6),
        "max_simultaneous_pm": max_simultaneous_pm,
        "standby_reserve_activations": counts["standby_reserve_activations"],
        "standby_decisions": counts["standby_decisions"],
    }
    return C5_5Result(policy_id, seed, summary, daily_records, event_log, failure_log)


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_5_policy_comparison.csv"
    json_path = target_dir / "c5_5_policy_comparison.json"
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
    summary_dir: str | Path | None = None,
    days: int | None = None,
) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []
    for seed in seeds:
        for policy_id in policies:
            result = run_policy_simulation(config, policy_id=policy_id, seed=seed, days=days)
            summary_rows.append(result.summary)
    if summary_dir is not None:
        write_summary(summary_rows, summary_dir)
    return summary_rows
