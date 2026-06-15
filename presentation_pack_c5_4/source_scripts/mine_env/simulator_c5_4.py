from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from mine_env.costs_c5_4 import C5_4CostModel
from mine_env.policies_c5_4 import create_joint_policy
from mine_env.reliability_c5_4 import COMPONENTS, C5_4ReliabilityModel


ROUTES = ("A", "B", "C")

# One summary row per (policy, seed) run. Groups, in order:
#   identity      -- policy_id, regime, seed, days
#   demand        -- total_demand, completed_loads, unmet_demand, demand_fulfillment_rate
#   objective     -- total_tco (the minimised objective) + its presentation-scaled value
#   cost split    -- pm/cm/downtime/degradation/unmet (sum == total_tco; test invariant)
#   PM activity   -- pm_count (shop VISITS) and pm_component_count (components serviced across visits)
#   failures      -- cm_count (== failure_count here; 1 CM per failed component) and the per-component
#                    split cm_tire/cm_engine/cm_brake (Tier-1 logging: which component breaks down)
#   health/avail  -- end-of-campaign avg truck/component HI, availability_rate, total_downtime_hours
#   dispatch mix  -- route_a/b/c_loads (completed loads by route; sum == completed_loads)
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
    "route_a_loads",
    "route_b_loads",
    "route_c_loads",
]


@dataclass
class C5_4Result:
    policy_id: str
    seed: int
    summary: dict[str, Any]
    daily_records: list[dict[str, Any]] = field(default_factory=list)
    # Per-failure events (only populated when run with record_events=True): one dict per failed
    # component haul -- {day, hour, step, truck_id, component, truck_hi_after, route}. Feeds the
    # Tier-3 failure-timing histogram and the per-seed failure-distribution analysis.
    failure_log: list[dict[str, Any]] = field(default_factory=list)


def _build_trucks(
    config: dict[str, Any], reliability: C5_4ReliabilityModel, rng: np.random.Generator
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
            # C5.4 PM-scheduling bookkeeping (maintained by the simulator, read by the PM rules):
            "operating_hours_since_pm": 0.0,  # accrues per haul; reset to 0 on a PM visit
            "last_pm_day": 0,                  # day of the last PM visit (0 = none yet)
            "pm_event_count": 0,
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
    policy: Any | None = None,
    record_events: bool = False,
) -> C5_4Result:
    """Run one JOINT (PM-scheduling + dispatch) policy for one seed over the daily campaign.

    Identical physics to C5.3 (3-component HI, frailty, sensor noise, Weibull failure -> CM,
    per-route per-component wear, TCO = pm+cm+downtime+degradation+unmet). The single change is the
    decision target: the policy now decides BOTH which trucks to refer to the PM bay (and which
    components to service in that shop visit) AND which route each remaining truck runs. Each step
    the policy is asked once; the simulator applies the accepted PM referrals (one truck per free
    bay), then dispatches the remaining available trucks by the policy's route ranking.

    ``policy`` lets a caller inject any object implementing the ``JointPolicy`` protocol
    (``decide(state)`` + ``reset()``) -- e.g. a trained ``AgentJointPolicy`` from the RL Lab -- so a
    learned policy runs through the exact same loop as the heuristics. When ``None`` (the default),
    the heuristic named by ``policy_id`` is created. ``policy_id`` always labels the summary row.
    """
    reliability = C5_4ReliabilityModel(config)
    cost_model = C5_4CostModel(config)
    if policy is None:
        policy = create_joint_policy(policy_id, config)

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
        "pm_count": 0,            # PM shop visits (bay occupations)
        "pm_component_count": 0,  # individual components serviced across all visits
        "pm_tire": 0,             # per-component preventive services (which component is maintained)
        "pm_engine": 0,
        "pm_brake": 0,
        "cm_count": 0,
        "cm_tire": 0,             # per-component corrective repairs (which component broke down)
        "cm_engine": 0,
        "cm_brake": 0,
        "failure_count": 0,
        "completed_loads": 0,
        "unmet_loads": 0,
        "total_demand": 0,
        "downtime_hours": 0,
    }
    route_loads = {r: 0 for r in ROUTES}
    availability_samples: list[int] = []
    daily_records: list[dict[str, Any]] = []
    failure_log: list[dict[str, Any]] = []

    policy.reset()
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

            available_trucks = [t for t in trucks if t["status"] == "AVAILABLE"]
            available_ids = {t["truck_id"] for t in available_trucks}
            availability_samples.append(len(available_trucks))

            in_pm = sum(1 for t in trucks if t["status"] == "PM")
            free_bays = max(pm_bay - in_pm, 0)
            slots = min(per_step_cap, demand_remaining)

            # 3. the JOINT decision: PM referrals + dispatch ranking, in one call
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
                    "route_capacity_remaining": cap_remaining,
                    "demand_remaining": demand_remaining,
                    "day": day,
                    "hour": hour,
                },
            }
            decision = policy.decide(state)

            # 4. apply PM referrals: one truck per free bay; a visit services all listed components
            pm_ids: set[str] = set()
            applied = 0
            for truck_id, components, _risk in decision.get("pm", []):
                if applied >= free_bays:
                    break
                if truck_id in pm_ids or truck_id not in available_ids:
                    continue
                truck = by_id[truck_id]
                total_cost = 0.0
                total_duration = 0.0
                for component in components:
                    rec = cost_model.pm[component]
                    truck[f"{component}_hi"] = min(
                        truck[f"{component}_hi"] + rec["recovery"], reliability.max_hi
                    )
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
                totals["pm"] += total_cost
                counts["pm_count"] += 1
                applied += 1
                pm_ids.add(truck_id)

            # 5. dispatch: honour demand slots + route capacity; skip trucks sent to PM
            if slots > 0:
                attempts = 0
                for truck_id, ranked_routes in decision.get("dispatch", []):
                    if attempts >= slots or demand_remaining <= 0:
                        break
                    if truck_id in pm_ids or truck_id not in available_ids:
                        continue
                    truck = by_id[truck_id]
                    if truck["status"] != "AVAILABLE":
                        continue
                    route_id = next((r for r in ranked_routes if cap_remaining[r] > 0), None)
                    if route_id is None:
                        continue  # every route's daily capacity exhausted; truck rests
                    route = config["routes"][route_id]
                    losses = reliability.apply_route_wear(truck, route, rng)
                    totals["degradation"] += cost_model.degradation_cost(losses)
                    truck["operating_hours_since_pm"] += 1.0
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
                            counts[f"cm_{component}"] += 1
                            counts["failure_count"] += 1
                            max_duration = max(max_duration, cm["duration"])
                            if record_events:
                                failure_log.append(
                                    {
                                        "day": day,
                                        "hour": hour,
                                        "step": global_step,
                                        "truck_id": truck_id,
                                        "component": component,
                                        "truck_hi_after": round(float(truck[f"{component}_hi"]), 4),
                                        "route": route_id,
                                    }
                                )
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
    # per-seed frailty descriptors (drawn once per truck per component at build): the MAX captures
    # the worst-frailty component in the fleet, which drives that seed's failure exposure (Tier-3
    # per-seed analysis -- does a high-CM seed correspond to an unlucky frailty draw?).
    frailty_vals = [
        float(truck[f"{component}_wear_multiplier"])
        for truck in trucks
        for component in COMPONENTS
    ]
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
        "availability_rate": round(
            float(np.mean(availability_samples)) / max(fleet_size, 1), 6
        )
        if availability_samples
        else 1.0,
        "route_a_loads": route_loads["A"],
        "route_b_loads": route_loads["B"],
        "route_c_loads": route_loads["C"],
    }
    return C5_4Result(
        policy_id=policy_id,
        seed=seed,
        summary=summary,
        daily_records=daily_records,
        failure_log=failure_log,
    )


def write_summary(summary_rows: list[dict[str, Any]], summary_dir: str | Path) -> None:
    target_dir = Path(summary_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    csv_path = target_dir / "c5_4_policy_comparison.csv"
    json_path = target_dir / "c5_4_policy_comparison.json"
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
