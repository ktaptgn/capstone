from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from mine_env.costs_c5_4 import C5_4CostModel
from mine_env.policies_c5_53 import ROUTES, create_congestion_policy
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
    "route_r_a1_loads",
    "route_r_a2_loads",
    "route_r_b1_loads",
    "route_r_b2_loads",
    "route_r_c1_loads",
    "route_r_c2_loads",
    "shovel_a_loads",
    "shovel_b_loads",
    "shovel_c_loads",
    "crusher_1_loads",
    "crusher_2_loads",
    "pm_bay_utilization",
    "max_simultaneous_pm",
    "standby_reserve_activations",
    "avg_selected_route_value",
    "avg_selected_risk_penalty",
    "avg_selected_capacity_score",
    "avg_selected_queue_penalty",
    "shortfall_sensitivity",
    "target_effective_output",
    "effective_output_shortfall",
    "effective_output_shortfall_cost",
    "effective_fulfillment_rate",
    "avg_grade_per_load",
    "total_tco_v1",
    "total_tco_v2",
    "total_tco_v2_report_value",
    "congestion_alpha",
    "congestion_beta",
    "congestion_cost_level",
    "congestion_cost_per_hour",
    "congestion_delay_hours_total",
    "route_queue_hours_total",
    "shovel_queue_hours_total",
    "crusher_queue_hours_total",
    "congestion_cost",
    "total_tco_v3",
    "total_tco_v3_report_value",
    "avg_realized_cycle_time_min",
    "avg_base_cycle_time_min",
    "avg_realized_cycle_time_hours",
    "avg_base_cycle_time_hours",
    "completed_loads_per_hour",
    "route_hhi",
    "max_route_share",
    "route_fallback_loads",
    "route_rejected_loads",
    "route_r_a1_attempts",
    "route_r_a2_attempts",
    "route_r_b1_attempts",
    "route_r_b2_attempts",
    "route_r_c1_attempts",
    "route_r_c2_attempts",
    "shovel_a_attempts",
    "shovel_b_attempts",
    "shovel_c_attempts",
    "crusher_1_attempts",
    "crusher_2_attempts",
]

DISPATCH_EVENT_FIELDS = [
    "step",
    "day",
    "hour",
    "truck_id",
    "policy",
    "regime",
    "preferred_route",
    "assigned_route",
    "fallback_reason",
    "route_capacity_remaining_before",
    "route_capacity_remaining_after",
    "route_utilization_before",
    "route_utilization_after",
    "shovel_id",
    "crusher_id",
    "shovel_utilization_before",
    "shovel_utilization_after",
    "crusher_utilization_before",
    "crusher_utilization_after",
    "base_cycle_time_min",
    "base_cycle_time_hours",
    "route_cycle_time_factor",
    "route_queue_delay_min",
    "shovel_queue_delay_min",
    "crusher_queue_delay_min",
    "route_queue_delay_hours",
    "shovel_queue_delay_hours",
    "crusher_queue_delay_hours",
    "realized_cycle_time_min",
    "realized_cycle_time_hours",
]

DAILY_RECORD_FIELDS = [
    "policy_id",
    "regime",
    "seed",
    "day",
    "completed_loads",
    "unmet_loads",
    "route_fallback_loads",
    "route_rejected_loads",
    "route_queue_hours",
    "shovel_queue_hours",
    "crusher_queue_hours",
    "congestion_delay_hours_total",
    "congestion_cost",
    "avg_realized_cycle_time_min",
    "avg_realized_cycle_time_hours",
    "completed_loads_per_hour",
    "route_hhi",
    "max_route_share",
    "route_r_a1_loads",
    "route_r_a2_loads",
    "route_r_b1_loads",
    "route_r_b2_loads",
    "route_r_c1_loads",
    "route_r_c2_loads",
    "route_r_a1_attempts",
    "route_r_a2_attempts",
    "route_r_b1_attempts",
    "route_r_b2_attempts",
    "route_r_c1_attempts",
    "route_r_c2_attempts",
    "shovel_a_loads",
    "shovel_b_loads",
    "shovel_c_loads",
    "shovel_a_attempts",
    "shovel_b_attempts",
    "shovel_c_attempts",
    "crusher_1_loads",
    "crusher_2_loads",
    "crusher_1_attempts",
    "crusher_2_attempts",
]


@dataclass
class C5_53Result:
    policy_id: str
    seed: int
    summary: dict[str, Any]
    daily_records: list[dict[str, Any]] = field(default_factory=list)
    failure_log: list[dict[str, Any]] = field(default_factory=list)
    dispatch_events: list[dict[str, Any]] = field(default_factory=list)


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
            "status": "AVAILABLE" if is_operating else "STANDBY_RESERVE",
            "downtime_remaining": 0,
            "assigned_route": None,
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
    truck["assigned_route"] = None
    totals["pm"] += total_cost
    counts["pm_count"] += 1


def _apply_cm(
    truck: dict[str, Any],
    failed: list[str],
    day: int,
    hour: int,
    step: int,
    route_id: str,
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
                    "truck_hi_after": round(float(truck[f"{component}_hi"]), 4),
                    "route": route_id,
                }
            )
    reliability.truck_hi(truck)
    truck["status"] = "CM"
    truck["downtime_remaining"] = max(int(round(max_duration)), 1)
    truck["assigned_route"] = route_id


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
        raise ValueError(f"Unknown C5.53 shortfall sensitivity: {sensitivity}")
    return float(rates[sensitivity])


def _congestion_cost_rate(config: dict[str, Any], level: str) -> float:
    rates = config["congestion"]["congestion_cost_per_hour"]
    if level not in rates:
        raise ValueError(f"Unknown C5.53 congestion cost level: {level}")
    return float(rates[level])


def _queue_delay(utilization: float, alpha: float, beta: float) -> float:
    """Return deterministic queue delay in minutes for one dispatch."""
    if utilization <= 1.0 or alpha <= 0.0:
        return 0.0
    return float(alpha) * float(utilization - 1.0) ** float(beta)


def _facility_capacity(config: dict[str, Any], facility_type: str, facility_id: str) -> float:
    if facility_type == "shovel":
        return float(config["facilities"]["shovels"][facility_id]["capacity_loads_per_day"])
    if facility_type == "crusher":
        return float(config["facilities"]["crushers"][facility_id]["capacity_loads_per_day"])
    raise ValueError(f"Unknown facility type: {facility_type}")


def _route_group(route_id: str) -> str:
    return route_id.split("_", 1)[1][0]


def _shovel_proxy_key(shovel_id: str) -> str:
    return shovel_id.split("_", 1)[1]


def _crusher_proxy_key(crusher_id: str) -> str:
    return crusher_id.lower()


def route_cycle_time_components(config: dict[str, Any], route_id: str) -> dict[str, Any]:
    route = config["routes"][route_id]
    route_group = _route_group(route_id)
    shovel_key = _shovel_proxy_key(route["shovel_id"])
    crusher_key = _crusher_proxy_key(route["crusher_id"])
    motion = config["truck_motion"]
    distance = config["route_distances"][route_id]
    speed_factor = config["route_speed_factors"][route_group]
    crusher_factor = config["crusher_approach_factors"][crusher_key]
    shovel_proxy = config["shovel_loading_proxy"]["shovels"][shovel_key]
    crusher_proxy = config["crusher_service_proxy"]["crushers"][crusher_key]

    payload_ton = float(motion.get("payload_ton", config["mine"]["payload_ton"]))
    passes = int(math.ceil(payload_ton / float(shovel_proxy["bucket_payload_ton"])))
    loading_time_min = (
        float(shovel_proxy["spotting_time_min"])
        + passes * float(shovel_proxy["bucket_cycle_time_sec"]) / 60.0
    )
    crusher_service_time_min = (
        float(config["crusher_service_proxy"]["spotting_time_min"])
        + float(config["crusher_service_proxy"]["dumping_time_min"])
        + float(crusher_proxy["acceptance_time_min"])
    )
    empty_speed = float(motion["empty_speed_kmh"]["base"]) * float(speed_factor["empty_factor"])
    loaded_speed = (
        float(motion["loaded_speed_kmh"]["base"])
        * float(speed_factor["loaded_factor"])
        * float(crusher_factor["travel_factor"])
    )
    empty_travel_min = float(distance["empty_distance_km"]) / empty_speed * 60.0
    loaded_travel_min = float(distance["loaded_distance_km"]) / loaded_speed * 60.0
    base_cycle_time_min = (
        empty_travel_min + loading_time_min + loaded_travel_min + crusher_service_time_min
    )
    return {
        "route_id": route_id,
        "shovel_id": route["shovel_id"],
        "crusher_id": route["crusher_id"],
        "empty_distance_km": float(distance["empty_distance_km"]),
        "loaded_distance_km": float(distance["loaded_distance_km"]),
        "empty_speed_kmh_effective": empty_speed,
        "loaded_speed_kmh_effective": loaded_speed,
        "empty_travel_min": empty_travel_min,
        "loaded_travel_min": loaded_travel_min,
        "passes": passes,
        "loading_time_min": loading_time_min,
        "crusher_service_time_min": crusher_service_time_min,
        "base_cycle_time_min": base_cycle_time_min,
        "expected_loads_per_truck_hour": 60.0 / base_cycle_time_min if base_cycle_time_min else 0.0,
    }


def build_route_cycle_time_table(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [route_cycle_time_components(config, route_id) for route_id in ROUTES]


def write_route_cycle_time_table(config: dict[str, Any], analysis_dir: str | Path) -> None:
    fields = [
        "route_id",
        "shovel_id",
        "crusher_id",
        "empty_distance_km",
        "loaded_distance_km",
        "empty_speed_kmh_effective",
        "loaded_speed_kmh_effective",
        "empty_travel_min",
        "loaded_travel_min",
        "passes",
        "loading_time_min",
        "crusher_service_time_min",
        "base_cycle_time_min",
        "expected_loads_per_truck_hour",
    ]
    target_dir = Path(analysis_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with (target_dir / "c5_53_route_cycle_time_table.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in build_route_cycle_time_table(config):
            writer.writerow(
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def _hhi(counts: dict[str, int]) -> float:
    total = float(sum(counts.values()))
    if total <= 0:
        return 0.0
    return round(sum((float(value) / total) ** 2 for value in counts.values()), 6)


def _max_share(counts: dict[str, int]) -> float:
    total = float(sum(counts.values()))
    if total <= 0:
        return 0.0
    return round(max(float(value) / total for value in counts.values()), 6)


def run_policy_simulation(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    days: int | None = None,
    record_daily: bool = False,
    policy: Any | None = None,
    record_events: bool = False,
    shortfall_sensitivity: str = "base",
    congestion_alpha: float | None = None,
    congestion_beta: float | None = None,
    congestion_cost_level: str | None = None,
) -> C5_53Result:
    """Run one C5.53 congestion-aware route-ranking policy for one seed."""
    reliability = C5_4ReliabilityModel(config)
    cost_model = C5_4CostModel(config)
    if policy is None:
        policy = create_congestion_policy(policy_id, config)

    rng = np.random.default_rng(seed)
    trucks = _build_trucks(config, reliability, rng)
    by_id = {truck["truck_id"]: truck for truck in trucks}
    fleet_size = len(trucks)
    total_days = int(days or config["simulation"]["horizon_days"])
    steps_per_day = int(config["demand"]["operating_hours_per_day"])
    daily_demand = int(config["demand"]["daily_demand_loads"])
    per_step_cap = max(int(math.ceil(daily_demand / steps_per_day)), 1)
    pm_capacity = _pm_capacity(config)
    congestion_cfg = config.get("congestion", {})
    route_cycle_times = {
        route_id: route_cycle_time_components(config, route_id) for route_id in ROUTES
    }
    alpha = float(
        congestion_cfg.get("congestion_alpha", 1.0)
        if congestion_alpha is None
        else congestion_alpha
    )
    beta = float(
        congestion_cfg.get("congestion_beta", 2.0)
        if congestion_beta is None
        else congestion_beta
    )
    cost_level = str(congestion_cost_level or congestion_cfg.get("congestion_cost_level", "base"))
    congestion_cost_per_hour = _congestion_cost_rate(config, cost_level)

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
    }
    route_loads = {route_id: 0 for route_id in ROUTES}
    route_attempts = {route_id: 0 for route_id in ROUTES}
    shovel_loads = {sid: 0 for sid in SHOVELS}
    shovel_attempts = {sid: 0 for sid in SHOVELS}
    crusher_loads = {cid: 0 for cid in CRUSHERS}
    crusher_attempts = {cid: 0 for cid in CRUSHERS}
    selected_components = {
        "route_value": [],
        "risk_penalty": [],
        "capacity_score": [],
        "queue_penalty": [],
    }
    effective_output = 0.0
    pm_slot_hours = 0
    max_simultaneous_pm = 0
    availability_samples: list[int] = []
    daily_records: list[dict[str, Any]] = []
    failure_log: list[dict[str, Any]] = []
    dispatch_events: list[dict[str, Any]] = []
    cycle_time_min_samples: list[float] = []
    base_cycle_min_samples: list[float] = []
    route_queue_hours_total = 0.0
    shovel_queue_hours_total = 0.0
    crusher_queue_hours_total = 0.0
    route_fallback_loads = 0
    route_rejected_loads = 0

    policy.reset()
    global_step = 0

    for day in range(1, total_days + 1):
        demand_remaining = daily_demand
        counts["total_demand"] += daily_demand
        completed_today = 0
        route_cap = {
            route_id: int(config["routes"][route_id]["capacity_loads_per_day"])
            for route_id in ROUTES
        }
        day_route_loads = {route_id: 0 for route_id in ROUTES}
        day_route_attempts = {route_id: 0 for route_id in ROUTES}
        day_shovel_loads = {sid: 0 for sid in SHOVELS}
        day_shovel_attempts = {sid: 0 for sid in SHOVELS}
        day_crusher_loads = {cid: 0 for cid in CRUSHERS}
        day_crusher_attempts = {cid: 0 for cid in CRUSHERS}
        day_route_queue = 0.0
        day_shovel_queue = 0.0
        day_crusher_queue = 0.0
        day_fallback_loads = 0
        day_rejected_loads = 0
        day_cycle_time_samples: list[float] = []

        for hour in range(steps_per_day):
            global_step += 1

            for truck in trucks:
                if truck["downtime_remaining"] > 0:
                    truck["downtime_remaining"] -= 1
                    totals["downtime"] += cost_model.downtime_rate
                    counts["downtime_hours"] += 1
                    if truck["downtime_remaining"] <= 0:
                        truck["status"] = "AVAILABLE"

            active_serviceable = sum(
                1
                for t in trucks
                if t["status"] in {"AVAILABLE", "PM", "CM"} and t["role"] != "STANDBY_RESERVE"
            )
            target_operating = int(config["mine"]["operating_truck_count"])
            for truck in trucks:
                if active_serviceable >= target_operating or demand_remaining <= 0:
                    break
                if truck["status"] == "STANDBY_RESERVE":
                    truck["status"] = "AVAILABLE"
                    truck["role"] = "RESERVE_ACTIVE"
                    counts["standby_reserve_activations"] += 1
                    active_serviceable += 1

            for truck in trucks:
                reliability.observe(truck, rng)

            available_trucks = [t for t in trucks if t["status"] == "AVAILABLE"]
            available_ids = {t["truck_id"] for t in available_trucks}
            availability_samples.append(len(available_trucks))
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
                    "available_count": len(available_trucks),
                },
                "dispatch_state": {
                    "dispatch_trucks": available_trucks,
                    "route_capacity_remaining": route_cap,
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

            attempts = 0
            if slots > 0:
                for truck_id, ranked_routes in decision.get("dispatch", []):
                    if attempts >= slots or demand_remaining <= 0:
                        break
                    if truck_id in pm_ids or truck_id not in available_ids:
                        continue
                    truck = by_id[truck_id]
                    if truck["status"] != "AVAILABLE":
                        continue
                    valid_ranked = [route for route in ranked_routes if route in route_cap]
                    preferred_route = valid_ranked[0] if valid_ranked else None
                    if preferred_route is None:
                        continue

                    preferred_cfg = config["routes"][preferred_route]
                    preferred_shovel = preferred_cfg["shovel_id"]
                    preferred_crusher = preferred_cfg["crusher_id"]
                    preferred_route_capacity = max(
                        float(preferred_cfg["capacity_loads_per_day"]), 1.0
                    )
                    preferred_shovel_capacity = max(
                        _facility_capacity(config, "shovel", preferred_shovel), 1.0
                    )
                    preferred_crusher_capacity = max(
                        _facility_capacity(config, "crusher", preferred_crusher), 1.0
                    )
                    route_attempt_before = day_route_attempts[preferred_route]
                    shovel_attempt_before = day_shovel_attempts[preferred_shovel]
                    crusher_attempt_before = day_crusher_attempts[preferred_crusher]
                    route_attempt_after = route_attempt_before + 1
                    shovel_attempt_after = shovel_attempt_before + 1
                    crusher_attempt_after = crusher_attempt_before + 1
                    preferred_route_util_before = route_attempt_before / preferred_route_capacity
                    preferred_route_util_after = route_attempt_after / preferred_route_capacity
                    preferred_shovel_util_before = shovel_attempt_before / preferred_shovel_capacity
                    preferred_shovel_util_after = shovel_attempt_after / preferred_shovel_capacity
                    preferred_crusher_util_before = crusher_attempt_before / preferred_crusher_capacity
                    preferred_crusher_util_after = crusher_attempt_after / preferred_crusher_capacity

                    day_route_attempts[preferred_route] += 1
                    day_shovel_attempts[preferred_shovel] += 1
                    day_crusher_attempts[preferred_crusher] += 1
                    route_attempts[preferred_route] += 1
                    shovel_attempts[preferred_shovel] += 1
                    crusher_attempts[preferred_crusher] += 1

                    route_id = next((r for r in valid_ranked if route_cap[r] > 0), None)
                    if route_id is None:
                        route_rejected_loads += 1
                        day_rejected_loads += 1
                        continue
                    route = config["routes"][route_id]
                    fallback_reason = "none"
                    if route_id != preferred_route:
                        fallback_reason = "preferred_capacity_exhausted"
                        route_fallback_loads += 1
                        day_fallback_loads += 1
                    route_capacity_before = route_cap[route_id]
                    if hasattr(policy, "dispatch"):
                        comps = policy.dispatch.score_components(truck, route_id, state["dispatch_state"])
                        for key, value in comps.items():
                            selected_components[key].append(float(value))
                    losses = reliability.apply_route_wear(truck, route, rng)
                    totals["degradation"] += cost_model.degradation_cost(losses)
                    truck["operating_hours_since_pm"] += 1.0
                    attempts += 1
                    failed = reliability.check_failures(truck, rng)
                    if failed:
                        _apply_cm(
                            truck,
                            failed,
                            day,
                            hour,
                            global_step,
                            route_id,
                            cost_model,
                            reliability,
                            totals,
                            counts,
                            failure_log,
                            record_events,
                        )
                        continue
                    route_queue_delay_min = _queue_delay(preferred_route_util_after, alpha, beta)
                    shovel_queue_delay_min = _queue_delay(preferred_shovel_util_after, alpha, beta)
                    crusher_queue_delay_min = _queue_delay(preferred_crusher_util_after, alpha, beta)
                    route_cycle = route_cycle_times[route_id]
                    base_cycle_time_min = float(route_cycle["base_cycle_time_min"])
                    realized_cycle_time_min = (
                        base_cycle_time_min
                        + route_queue_delay_min
                        + shovel_queue_delay_min
                        + crusher_queue_delay_min
                    )
                    route_queue_delay_hours = route_queue_delay_min / 60.0
                    shovel_queue_delay_hours = shovel_queue_delay_min / 60.0
                    crusher_queue_delay_hours = crusher_queue_delay_min / 60.0
                    realized_cycle_time_hours = realized_cycle_time_min / 60.0
                    route_queue_hours_total += route_queue_delay_hours
                    shovel_queue_hours_total += shovel_queue_delay_hours
                    crusher_queue_hours_total += crusher_queue_delay_hours
                    day_route_queue += route_queue_delay_hours
                    day_shovel_queue += shovel_queue_delay_hours
                    day_crusher_queue += crusher_queue_delay_hours
                    cycle_time_min_samples.append(realized_cycle_time_min)
                    base_cycle_min_samples.append(base_cycle_time_min)
                    day_cycle_time_samples.append(realized_cycle_time_min)
                    demand_remaining -= 1
                    completed_today += 1
                    route_cap[route_id] -= 1
                    route_loads[route_id] += 1
                    day_route_loads[route_id] += 1
                    shovel_loads[route["shovel_id"]] += 1
                    day_shovel_loads[route["shovel_id"]] += 1
                    crusher_loads[route["crusher_id"]] += 1
                    day_crusher_loads[route["crusher_id"]] += 1
                    effective_output += float(config["mine"]["payload_ton"]) * float(route["grade_index"])
                    counts["completed_loads"] += 1
                    truck["loads_completed"] += 1
                    truck["assigned_route"] = route_id
                    if record_events:
                        dispatch_events.append(
                            {
                                "step": global_step,
                                "day": day,
                                "hour": hour,
                                "truck_id": truck_id,
                                "policy": policy_id,
                                "regime": config.get("active_regime"),
                                "preferred_route": preferred_route,
                                "assigned_route": route_id,
                                "fallback_reason": fallback_reason,
                                "route_capacity_remaining_before": route_capacity_before,
                                "route_capacity_remaining_after": route_cap[route_id],
                                "route_utilization_before": round(preferred_route_util_before, 6),
                                "route_utilization_after": round(preferred_route_util_after, 6),
                                "shovel_id": route["shovel_id"],
                                "crusher_id": route["crusher_id"],
                                "shovel_utilization_before": round(preferred_shovel_util_before, 6),
                                "shovel_utilization_after": round(preferred_shovel_util_after, 6),
                                "crusher_utilization_before": round(preferred_crusher_util_before, 6),
                                "crusher_utilization_after": round(preferred_crusher_util_after, 6),
                                "base_cycle_time_min": round(base_cycle_time_min, 6),
                                "base_cycle_time_hours": round(base_cycle_time_min / 60.0, 6),
                                "route_cycle_time_factor": round(
                                    float(route.get("cycle_time_factor", 1.0)), 6
                                ),
                                "route_queue_delay_min": round(route_queue_delay_min, 6),
                                "shovel_queue_delay_min": round(shovel_queue_delay_min, 6),
                                "crusher_queue_delay_min": round(crusher_queue_delay_min, 6),
                                "route_queue_delay_hours": round(route_queue_delay_hours, 6),
                                "shovel_queue_delay_hours": round(shovel_queue_delay_hours, 6),
                                "crusher_queue_delay_hours": round(crusher_queue_delay_hours, 6),
                                "realized_cycle_time_min": round(realized_cycle_time_min, 6),
                                "realized_cycle_time_hours": round(realized_cycle_time_hours, 6),
                            }
                        )

        unmet = max(demand_remaining, 0)
        totals["unmet"] += cost_model.unmet_demand_cost(unmet)
        counts["unmet_loads"] += unmet
        if record_daily:
            day_delay = day_route_queue + day_shovel_queue + day_crusher_queue
            day_congestion_cost = day_delay * congestion_cost_per_hour
            daily_records.append(
                {
                    "policy_id": policy_id,
                    "regime": config.get("active_regime"),
                    "seed": seed,
                    "day": day,
                    "completed_loads": completed_today,
                    "unmet_loads": unmet,
                    "route_fallback_loads": day_fallback_loads,
                    "route_rejected_loads": day_rejected_loads,
                    "route_queue_hours": round(day_route_queue, 6),
                    "shovel_queue_hours": round(day_shovel_queue, 6),
                    "crusher_queue_hours": round(day_crusher_queue, 6),
                    "congestion_delay_hours_total": round(day_delay, 6),
                    "congestion_cost": round(day_congestion_cost, 6),
                    "avg_realized_cycle_time_min": round(
                        float(np.mean(day_cycle_time_samples)) if day_cycle_time_samples else 0.0,
                        6,
                    ),
                    "avg_realized_cycle_time_hours": round(
                        (float(np.mean(day_cycle_time_samples)) / 60.0)
                        if day_cycle_time_samples
                        else 0.0,
                        6,
                    ),
                    "completed_loads_per_hour": round(completed_today / max(steps_per_day, 1), 6),
                    "route_hhi": _hhi(day_route_loads),
                    "max_route_share": _max_share(day_route_loads),
                    "route_r_a1_loads": day_route_loads["R_A1"],
                    "route_r_a2_loads": day_route_loads["R_A2"],
                    "route_r_b1_loads": day_route_loads["R_B1"],
                    "route_r_b2_loads": day_route_loads["R_B2"],
                    "route_r_c1_loads": day_route_loads["R_C1"],
                    "route_r_c2_loads": day_route_loads["R_C2"],
                    "route_r_a1_attempts": day_route_attempts["R_A1"],
                    "route_r_a2_attempts": day_route_attempts["R_A2"],
                    "route_r_b1_attempts": day_route_attempts["R_B1"],
                    "route_r_b2_attempts": day_route_attempts["R_B2"],
                    "route_r_c1_attempts": day_route_attempts["R_C1"],
                    "route_r_c2_attempts": day_route_attempts["R_C2"],
                    "shovel_a_loads": day_shovel_loads["SHOVEL_A"],
                    "shovel_b_loads": day_shovel_loads["SHOVEL_B"],
                    "shovel_c_loads": day_shovel_loads["SHOVEL_C"],
                    "shovel_a_attempts": day_shovel_attempts["SHOVEL_A"],
                    "shovel_b_attempts": day_shovel_attempts["SHOVEL_B"],
                    "shovel_c_attempts": day_shovel_attempts["SHOVEL_C"],
                    "crusher_1_loads": day_crusher_loads["CRUSHER_1"],
                    "crusher_2_loads": day_crusher_loads["CRUSHER_2"],
                    "crusher_1_attempts": day_crusher_attempts["CRUSHER_1"],
                    "crusher_2_attempts": day_crusher_attempts["CRUSHER_2"],
                }
            )

    total_tco = sum(totals.values())
    fulfillment = counts["completed_loads"] / counts["total_demand"] if counts["total_demand"] else 1.0
    target_effective = _target_effective_output(config, counts["total_demand"])
    effective_shortfall = max(target_effective - effective_output, 0.0)
    shortfall_cost = effective_shortfall * _shortfall_cost_rate(config, shortfall_sensitivity)
    total_tco_v1 = total_tco
    total_tco_v2 = total_tco_v1 + shortfall_cost
    congestion_delay_total = route_queue_hours_total + shovel_queue_hours_total + crusher_queue_hours_total
    congestion_cost = congestion_delay_total * congestion_cost_per_hour
    total_tco_v3 = total_tco_v2 + congestion_cost
    avg_grade = (
        effective_output / (counts["completed_loads"] * float(config["mine"]["payload_ton"]))
        if counts["completed_loads"] > 0
        else 0.0
    )
    frailty_vals = [
        float(truck[f"{component}_wear_multiplier"])
        for truck in trucks
        for component in COMPONENTS
    ]
    total_steps = max(total_days * steps_per_day, 1)

    def avg_selected(key: str) -> float:
        values = selected_components[key]
        return round(float(np.mean(values)), 6) if values else 0.0

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
        "route_r_a1_loads": route_loads["R_A1"],
        "route_r_a2_loads": route_loads["R_A2"],
        "route_r_b1_loads": route_loads["R_B1"],
        "route_r_b2_loads": route_loads["R_B2"],
        "route_r_c1_loads": route_loads["R_C1"],
        "route_r_c2_loads": route_loads["R_C2"],
        "shovel_a_loads": shovel_loads["SHOVEL_A"],
        "shovel_b_loads": shovel_loads["SHOVEL_B"],
        "shovel_c_loads": shovel_loads["SHOVEL_C"],
        "crusher_1_loads": crusher_loads["CRUSHER_1"],
        "crusher_2_loads": crusher_loads["CRUSHER_2"],
        "pm_bay_utilization": round(pm_slot_hours / max(pm_capacity * total_steps, 1), 6),
        "max_simultaneous_pm": max_simultaneous_pm,
        "standby_reserve_activations": counts["standby_reserve_activations"],
        "avg_selected_route_value": avg_selected("route_value"),
        "avg_selected_risk_penalty": avg_selected("risk_penalty"),
        "avg_selected_capacity_score": avg_selected("capacity_score"),
        "avg_selected_queue_penalty": avg_selected("queue_penalty"),
        "shortfall_sensitivity": shortfall_sensitivity,
        "target_effective_output": round(target_effective, 3),
        "effective_output_shortfall": round(effective_shortfall, 3),
        "effective_output_shortfall_cost": round(shortfall_cost, 6),
        "effective_fulfillment_rate": round(
            effective_output / target_effective if target_effective else 1.0, 6
        ),
        "avg_grade_per_load": round(avg_grade, 6),
        "total_tco_v1": round(total_tco_v1, 6),
        "total_tco_v2": round(total_tco_v2, 6),
        "total_tco_v2_report_value": round(cost_model.to_report_value(total_tco_v2), 3),
        "congestion_alpha": round(alpha, 6),
        "congestion_beta": round(beta, 6),
        "congestion_cost_level": cost_level,
        "congestion_cost_per_hour": round(congestion_cost_per_hour, 6),
        "congestion_delay_hours_total": round(congestion_delay_total, 6),
        "route_queue_hours_total": round(route_queue_hours_total, 6),
        "shovel_queue_hours_total": round(shovel_queue_hours_total, 6),
        "crusher_queue_hours_total": round(crusher_queue_hours_total, 6),
        "congestion_cost": round(congestion_cost, 6),
        "total_tco_v3": round(total_tco_v3, 6),
        "total_tco_v3_report_value": round(cost_model.to_report_value(total_tco_v3), 3),
        "avg_realized_cycle_time_min": round(
            float(np.mean(cycle_time_min_samples)) if cycle_time_min_samples else 0.0,
            6,
        ),
        "avg_base_cycle_time_min": round(
            float(np.mean(base_cycle_min_samples)) if base_cycle_min_samples else 0.0,
            6,
        ),
        "avg_realized_cycle_time_hours": round(
            (float(np.mean(cycle_time_min_samples)) / 60.0)
            if cycle_time_min_samples
            else 0.0,
            6,
        ),
        "avg_base_cycle_time_hours": round(
            (float(np.mean(base_cycle_min_samples)) / 60.0)
            if base_cycle_min_samples
            else 0.0,
            6,
        ),
        "completed_loads_per_hour": round(
            counts["completed_loads"] / max(total_days * steps_per_day, 1),
            6,
        ),
        "route_hhi": _hhi(route_loads),
        "max_route_share": _max_share(route_loads),
        "route_fallback_loads": route_fallback_loads,
        "route_rejected_loads": route_rejected_loads,
        "route_r_a1_attempts": route_attempts["R_A1"],
        "route_r_a2_attempts": route_attempts["R_A2"],
        "route_r_b1_attempts": route_attempts["R_B1"],
        "route_r_b2_attempts": route_attempts["R_B2"],
        "route_r_c1_attempts": route_attempts["R_C1"],
        "route_r_c2_attempts": route_attempts["R_C2"],
        "shovel_a_attempts": shovel_attempts["SHOVEL_A"],
        "shovel_b_attempts": shovel_attempts["SHOVEL_B"],
        "shovel_c_attempts": shovel_attempts["SHOVEL_C"],
        "crusher_1_attempts": crusher_attempts["CRUSHER_1"],
        "crusher_2_attempts": crusher_attempts["CRUSHER_2"],
    }
    return C5_53Result(policy_id, seed, summary, daily_records, failure_log, dispatch_events)


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_53_policy_comparison.csv"
    json_path = target_dir / "c5_53_policy_comparison.json"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary_rows)
    with json_path.open("w", encoding="utf-8") as stream:
        json.dump(summary_rows, stream, indent=2)


def write_dispatch_events(event_rows: list[dict[str, Any]], log_dir: str | Path) -> Path:
    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_53_dispatch_events.csv"
    try:
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=DISPATCH_EVENT_FIELDS)
            writer.writeheader()
            writer.writerows(event_rows)
        return csv_path
    except OSError:
        fallback_path = target_dir / "c5_53_dispatch_events_latest.csv"
        with fallback_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=DISPATCH_EVENT_FIELDS)
            writer.writeheader()
            writer.writerows(event_rows)
        return fallback_path


def write_daily_records(daily_rows: list[dict[str, Any]], log_dir: str | Path) -> Path:
    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_53_daily_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=DAILY_RECORD_FIELDS)
        writer.writeheader()
        writer.writerows(daily_rows)
    return csv_path


def run_policy_sweep(
    config: dict[str, Any],
    policies: list[str],
    seeds: list[int],
    summary_dir: str | Path | None = None,
    days: int | None = None,
    shortfall_sensitivity: str = "base",
    congestion_alpha: float | None = None,
    congestion_beta: float | None = None,
    congestion_cost_level: str | None = None,
) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []
    for seed in seeds:
        for policy_id in policies:
            result = run_policy_simulation(
                config,
                policy_id=policy_id,
                seed=seed,
                days=days,
                shortfall_sensitivity=shortfall_sensitivity,
                congestion_alpha=congestion_alpha,
                congestion_beta=congestion_beta,
                congestion_cost_level=congestion_cost_level,
            )
            summary_rows.append(result.summary)
    if summary_dir is not None:
        write_summary(summary_rows, summary_dir)
    return summary_rows
