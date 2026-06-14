from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from mine_env.costs_c5_3 import C5_3CostModel
from mine_env.pm_rule_engine_c5_3 import C5_3RuleBasedPMEngine
from mine_env.policies_c5_3 import create_dispatch_policy
from mine_env.reliability_c5_3 import COMPONENTS, C5_3ReliabilityModel


ROUTES = ("A", "B", "C")

SUMMARY_FIELDS = [
    "policy_id",
    "regime",
    "seed",
    "days",
    "total_demand",
    "completed_loads",
    "unmet_demand",
    "demand_fulfillment_rate",
    "total_tco",
    "total_tco_report_value",
    "pm_cost",
    "cm_cost",
    "downtime_cost",
    "degradation_cost",
    "unmet_demand_cost",
    "pm_count",
    "cm_count",
    "failure_count",
    "total_downtime_hours",
    "avg_truck_hi",
    "avg_tire_hi",
    "avg_engine_hi",
    "avg_brake_hi",
    "availability_rate",
    "route_a_loads",
    "route_b_loads",
    "route_c_loads",
]


@dataclass
class C5_3Result:
    policy_id: str
    seed: int
    summary: dict[str, Any]
    daily_records: list[dict[str, Any]] = field(default_factory=list)


def _build_trucks(
    config: dict[str, Any], reliability: C5_3ReliabilityModel, rng: np.random.Generator
) -> list[dict[str, Any]]:
    count = int(config["mine"]["truck_count"])
    initial = reliability.initial_hi()
    trucks: list[dict[str, Any]] = []
    for index in range(count):
        frailty = reliability.draw_frailty(rng)
        truck: dict[str, Any] = {
            "truck_id": f"T{index + 1:02d}",
            "status": "AVAILABLE",          # AVAILABLE | PM | CM
            "downtime_remaining": 0,
            "assigned_route": None,
            "loads_completed": 0,
        }
        for component in COMPONENTS:
            truck[f"{component}_hi"] = initial[component]
            truck[f"{component}_wear_multiplier"] = frailty[component]
        reliability.truck_hi(truck)
        reliability.observe(truck, rng)
        trucks.append(truck)
    return trucks


def run_policy_simulation(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    days: int | None = None,
    record_daily: bool = False,
) -> C5_3Result:
    """Run one dispatch policy for one seed over the hybrid daily campaign.

    One operating hour = one step; 24 steps = one day. Each day carries a fixed demand
    quota spread evenly across the hours; each route has a daily capacity. Dispatch (route
    choice for the available trucks) is the policy's only decision -- PM is the shared fixed
    rule engine. A haul wears the 3 components (frailty- and route-scaled, with noise); below
    the failure threshold a Weibull-like hazard can trigger a corrective repair (CM: load
    lost, expensive, long downtime). Costs decompose into pm/cm/downtime/degradation/unmet.
    """
    reliability = C5_3ReliabilityModel(config)
    cost_model = C5_3CostModel(config)
    pm_engine = C5_3RuleBasedPMEngine(config, reliability)
    policy = create_dispatch_policy(policy_id, config)

    rng = np.random.default_rng(seed)
    trucks = _build_trucks(config, reliability, rng)
    by_id = {truck["truck_id"]: truck for truck in trucks}
    fleet_size = len(trucks)

    sim = config["simulation"]
    total_days = int(
        days
        or sim.get("horizon_days")
        or (int(sim["horizon_steps"]) // int(config["demand"]["operating_hours_per_day"]))
    )
    steps_per_day = int(config["demand"]["operating_hours_per_day"])
    daily_demand = int(config["demand"]["daily_demand_loads"])
    per_step_cap = max(int(math.ceil(daily_demand / steps_per_day)), 1)
    route_caps = {r: int(config["routes"][r]["capacity_loads_per_day"]) for r in ROUTES}
    pm_bay = int(config["mine"]["pm_bay_count"])

    totals = {"pm": 0.0, "cm": 0.0, "downtime": 0.0, "degradation": 0.0, "unmet": 0.0}
    counts = {
        "pm_count": 0,
        "cm_count": 0,
        "failure_count": 0,
        "completed_loads": 0,
        "unmet_loads": 0,
        "total_demand": 0,
        "downtime_hours": 0,
    }
    route_loads = {r: 0 for r in ROUTES}
    availability_samples: list[int] = []
    daily_records: list[dict[str, Any]] = []

    pm_engine.reset()
    global_step = 0

    for day in range(1, total_days + 1):
        demand_remaining = daily_demand
        cap_remaining = dict(route_caps)
        counts["total_demand"] += daily_demand
        completed_today = 0

        for hour in range(steps_per_day):
            global_step += 1

            # 1. tick existing downtime (trucks in the bay / under repair)
            for truck in trucks:
                if truck["downtime_remaining"] > 0:
                    truck["downtime_remaining"] -= 1
                    totals["downtime"] += cost_model.downtime_rate
                    counts["downtime_hours"] += 1
                    if truck["downtime_remaining"] <= 0:
                        truck["status"] = "AVAILABLE"

            # 2. noisy condition observation for every truck (POMDP)
            for truck in trucks:
                reliability.observe(truck, rng)

            availability_samples.append(
                sum(1 for truck in trucks if truck["status"] == "AVAILABLE")
            )

            # 3. fixed rule-based PM (shared by all policies), respecting bay capacity
            available_ids = {t["truck_id"] for t in trucks if t["status"] == "AVAILABLE"}
            in_pm = sum(1 for t in trucks if t["status"] == "PM")
            free_bays = max(pm_bay - in_pm, 0)
            referrals = pm_engine.select_referrals(trucks, available_ids, global_step, free_bays)
            pm_ids: set[str] = set()
            for truck_id, component, _action, _risk in referrals:
                truck = by_id[truck_id]
                rec = cost_model.pm[component]
                truck[f"{component}_hi"] = min(
                    truck[f"{component}_hi"] + rec["recovery"], reliability.max_hi
                )
                reliability.truck_hi(truck)
                truck["status"] = "PM"
                truck["downtime_remaining"] = max(int(round(rec["duration"])), 1)
                totals["pm"] += rec["cost"]
                counts["pm_count"] += 1
                pm_ids.add(truck_id)

            # 4. dispatch: the policy assigns routes; greedily honour demand slots + capacity
            slots = min(per_step_cap, demand_remaining)
            if slots > 0:
                dispatch_trucks = [
                    t for t in trucks if t["status"] == "AVAILABLE" and t["truck_id"] not in pm_ids
                ]
                if dispatch_trucks:
                    state = {
                        "dispatch_trucks": dispatch_trucks,
                        "route_capacity_remaining": cap_remaining,
                        "demand_remaining": demand_remaining,
                        "day": day,
                        "hour": hour,
                    }
                    attempts = 0
                    for truck_id, ranked_routes in policy.decide_dispatch(state):
                        if attempts >= slots or demand_remaining <= 0:
                            break
                        route_id = next(
                            (r for r in ranked_routes if cap_remaining[r] > 0), None
                        )
                        if route_id is None:
                            continue  # every route's daily capacity exhausted; truck rests
                        truck = by_id[truck_id]
                        route = config["routes"][route_id]
                        losses = reliability.apply_route_wear(truck, route, rng)
                        totals["degradation"] += cost_model.degradation_cost(losses)
                        attempts += 1
                        failed = reliability.check_failures(truck, rng)
                        if failed:
                            max_duration = 0.0
                            for component in failed:
                                cm = cost_model.cm[component]
                                truck[f"{component}_hi"] = min(
                                    truck[f"{component}_hi"] + cm["recovery"], reliability.max_hi
                                )
                                totals["cm"] += cm["cost"]
                                counts["cm_count"] += 1
                                counts["failure_count"] += 1
                                max_duration = max(max_duration, cm["duration"])
                            reliability.truck_hi(truck)
                            truck["status"] = "CM"
                            truck["downtime_remaining"] = max(int(round(max_duration)), 1)
                            truck["assigned_route"] = route_id
                            # load lost: the haul failed mid-route, demand not delivered
                        else:
                            demand_remaining -= 1
                            completed_today += 1
                            cap_remaining[route_id] -= 1
                            route_loads[route_id] += 1
                            counts["completed_loads"] += 1
                            truck["loads_completed"] += 1
                            truck["assigned_route"] = route_id

        # end of day: unmet daily demand penalty
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
                    "avg_truck_hi": round(
                        float(np.mean([reliability.truck_hi(t) for t in trucks])), 4
                    ),
                }
            )

    total_tco = sum(totals.values())
    fulfillment = (
        counts["completed_loads"] / counts["total_demand"] if counts["total_demand"] else 1.0
    )
    summary = {
        "policy_id": policy_id,
        "regime": config.get("active_regime"),
        "seed": seed,
        "days": total_days,
        "total_demand": counts["total_demand"],
        "completed_loads": counts["completed_loads"],
        "unmet_demand": counts["unmet_loads"],
        "demand_fulfillment_rate": round(fulfillment, 6),
        "total_tco": round(total_tco, 6),
        "total_tco_report_value": round(cost_model.to_report_value(total_tco), 3),
        "pm_cost": round(totals["pm"], 6),
        "cm_cost": round(totals["cm"], 6),
        "downtime_cost": round(totals["downtime"], 6),
        "degradation_cost": round(totals["degradation"], 6),
        "unmet_demand_cost": round(totals["unmet"], 6),
        "pm_count": counts["pm_count"],
        "cm_count": counts["cm_count"],
        "failure_count": counts["failure_count"],
        "total_downtime_hours": counts["downtime_hours"],
        "avg_truck_hi": round(float(np.mean([reliability.truck_hi(t) for t in trucks])), 6),
        "avg_tire_hi": round(float(np.mean([t["tire_hi"] for t in trucks])), 6),
        "avg_engine_hi": round(float(np.mean([t["engine_hi"] for t in trucks])), 6),
        "avg_brake_hi": round(float(np.mean([t["brake_hi"] for t in trucks])), 6),
        "availability_rate": round(
            float(np.mean(availability_samples)) / max(fleet_size, 1), 6
        )
        if availability_samples
        else 1.0,
        "route_a_loads": route_loads["A"],
        "route_b_loads": route_loads["B"],
        "route_c_loads": route_loads["C"],
    }
    return C5_3Result(policy_id=policy_id, seed=seed, summary=summary, daily_records=daily_records)


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_3_policy_comparison.csv"
    json_path = target_dir / "c5_3_policy_comparison.json"
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
