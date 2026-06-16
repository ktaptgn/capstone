"""Core environment for the RSW C5.4 Level 2 synthetic transfer mini-test.

Step 2 implements the shared physics, maintenance, cost, and logging surface. Step 3 policies live
in ``rsw_policies.py``; full policy episode integration and sweeps remain deferred to Step 4.
"""

from __future__ import annotations

import argparse
import copy
import csv
import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from rsw_policies import create_joint_policy, validate_policy_decision


ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "rsw_c5_4_config.yaml"


@dataclass
class SimulationResult:
    summary: dict[str, Any]
    event_log: list[dict[str, Any]] = field(default_factory=list)
    failure_log: list[dict[str, Any]] = field(default_factory=list)
    final_guns: list[dict[str, Any]] = field(default_factory=list)


def load_config(path: str | Path = CONFIG_PATH, regime: str | None = None) -> dict[str, Any]:
    """Load the UTF-8 YAML and attach the selected regime without mutating the source mapping."""
    with Path(path).open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    selected = regime or config["default_regime"]
    if selected not in config["regimes"]:
        raise ValueError(f"Unknown RSW regime: {selected}")
    config["active_regime"] = selected
    config["regime"] = copy.deepcopy(config["regimes"][selected])
    return config


def build_scenario_contract(
    base_config: dict[str, Any], scenario: str = "base"
) -> dict[str, Any]:
    """Return an isolated execution contract; base and sanity outputs can never share paths."""
    if scenario == "base":
        return {
            "scenario": "base",
            "days": int(base_config["simulation"]["campaign_days"]),
            "seeds": [int(seed) for seed in base_config["simulation"]["seeds"]],
            "regimes": list(base_config["regimes"]),
            "policies": list(base_config["policies"]["enabled"]),
            "family_daily_targets": copy.deepcopy(base_config["demand"]["family_daily_targets"]),
            "outputs": {
                key: base_config["outputs"][key]
                for key in ("directory", "policy_summary_csv", "event_log_csv", "failure_log_csv")
            },
        }
    scenarios = base_config.get("sanity_scenarios", {})
    if scenario not in scenarios:
        raise ValueError(f"Unknown RSW sanity scenario: {scenario}")
    spec = scenarios[scenario]
    return {
        "scenario": scenario,
        "days": int(spec["days"]),
        "seeds": [int(seed) for seed in spec["seeds"]],
        "regimes": list(spec["regimes"]),
        "policies": list(base_config["policies"]["enabled"]),
        "family_daily_targets": copy.deepcopy(
            spec.get("family_daily_targets", base_config["demand"]["family_daily_targets"])
        ),
        "outputs": copy.deepcopy(spec["outputs"]),
    }


def build_initial_state(config: dict[str, Any], rng: np.random.Generator) -> list[dict[str, Any]]:
    """Create guns with clipped component HI and component-specific Gamma frailty."""
    rel = config["reliability"]
    components = tuple(rel["components"])
    initial = rel["initial_hi"]
    frailty_cfg = rel["frailty"]
    cv = float(frailty_cfg["cv"])
    shape = 1.0 / max(cv * cv, 1e-12)
    scale = float(frailty_cfg.get("mean", 1.0)) / shape
    guns: list[dict[str, Any]] = []

    for index in range(int(config["simulation"]["gun_count"])):
        gun: dict[str, Any] = {
            "gun_id": f"G{index + 1:02d}",
            "status": "AVAILABLE",
            "downtime_remaining": 0,
            "operating_hours_since_pm": 0.0,
            "last_pm_day": 0,
            "pm_visit_count": 0,
        }
        for component in components:
            hi = rng.normal(float(initial["mean"][component]), float(initial["std"][component]))
            gun[f"{component}_hi"] = float(
                np.clip(hi, float(initial["lower_clip"]), float(initial["upper_clip"]))
            )
            frailty = rng.gamma(shape, scale)
            gun[f"{component}_frailty"] = float(
                np.clip(
                    frailty,
                    float(frailty_cfg["min_clip"]),
                    float(frailty_cfg["max_clip"]),
                )
            )
        update_gun_hi(gun, components)
        observe_state(gun, config, rng)
        guns.append(gun)
    return guns


def update_gun_hi(gun: dict[str, Any], components: tuple[str, ...]) -> float:
    gun["gun_hi"] = min(float(gun[f"{component}_hi"]) for component in components)
    return float(gun["gun_hi"])


def observe_state(
    gun: dict[str, Any], config: dict[str, Any], rng: np.random.Generator
) -> dict[str, float]:
    """Write noisy observed HI values. Policies introduced later must use only these values."""
    sensor = config["reliability"]["sensor_noise"]
    observed: dict[str, float] = {}
    for component in config["reliability"]["components"]:
        value = float(gun[f"{component}_hi"])
        if bool(sensor["enabled"]):
            value += float(rng.normal(0.0, float(sensor["sigma"])))
        value = float(np.clip(value, float(sensor["lower_clip"]), float(sensor["upper_clip"])))
        gun[f"observed_{component}_hi"] = value
        observed[component] = value
    gun["observed_gun_hi"] = min(observed.values())
    return observed


def compute_component_loss(
    gun: dict[str, Any],
    component: str,
    job: dict[str, Any],
    config: dict[str, Any],
    rng: np.random.Generator,
) -> float:
    wear = config["reliability"]["wear"]
    random_factor = max(
        float(wear["minimum_factor"]),
        float(rng.normal(1.0, float(wear["stochastic_sigma"]))),
    )
    return max(
        float(wear["base_loss_per_hour"][component])
        * float(job["severity"][component])
        * float(gun[f"{component}_frailty"])
        * float(config["regime"]["wear_factor"])
        * random_factor,
        0.0,
    )


def apply_production_wear(
    gun: dict[str, Any],
    job: dict[str, Any],
    config: dict[str, Any],
    rng: np.random.Generator,
) -> dict[str, float]:
    """Apply one production-hour wear update and return actual clipped HI loss."""
    rel = config["reliability"]
    losses: dict[str, float] = {}
    for component in rel["components"]:
        before = float(gun[f"{component}_hi"])
        raw_loss = compute_component_loss(gun, component, job, config, rng)
        after = float(np.clip(before - raw_loss, float(rel["min_hi"]), float(rel["max_hi"])))
        gun[f"{component}_hi"] = after
        losses[component] = before - after
    update_gun_hi(gun, tuple(rel["components"]))
    return losses


def compute_failure_probability(component: str, hi: float, config: dict[str, Any]) -> float:
    """Threshold-power wear-out hazard, zero above the configured component threshold."""
    hazard = config["reliability"]["failure_hazard"]
    threshold = float(hazard["threshold_hi"][component])
    if bool(hazard["zero_above_threshold"]) and hi > threshold:
        return 0.0
    if hi <= 0.0:
        return 1.0
    severity = max((threshold - float(hi)) / max(threshold, 1e-12), 0.0)
    probability = (
        float(hazard["p_max"][component])
        * severity ** float(hazard["shape"][component])
        * float(config["regime"]["hazard_factor"])
    )
    return float(np.clip(probability, 0.0, 1.0))


def sample_failures(
    gun: dict[str, Any], config: dict[str, Any], rng: np.random.Generator
) -> list[str]:
    failed = []
    for component in config["reliability"]["components"]:
        probability = compute_failure_probability(component, gun[f"{component}_hi"], config)
        if float(rng.random()) < probability:
            failed.append(component)
    return failed


def compute_defect_probability(gun: dict[str, Any], job: dict[str, Any], config: dict[str, Any]) -> float:
    """Synthetic quality-event risk, separate from component failure/CM."""
    defect = config["reliability"]["defect_hazard"]
    sigmoid = 1.0 / (
        1.0
        + math.exp(
            float(defect["slope"]) * (float(gun["gun_hi"]) - float(defect["center_hi"]))
        )
    )
    avg_severity = float(np.mean(list(job["severity"].values())))
    severity_factor = 1.0 + float(defect["job_severity_weight"]) * max(avg_severity - 1.0, 0.0)
    return float(np.clip(float(defect["p_max"]) * sigmoid * severity_factor, 0.0, 1.0))


def compute_degradation_cost(losses: dict[str, float], config: dict[str, Any]) -> float:
    rates = config["cost"]["degradation_cost_per_hi_loss"]
    return sum(float(losses[component]) * float(rates[component]) for component in losses)


def apply_pm_decision(
    gun: dict[str, Any], components: list[str] | tuple[str, ...], config: dict[str, Any]
) -> dict[str, Any]:
    """Apply one gun-level PM visit with additive partial restoration and configured caps."""
    valid_components = tuple(config["reliability"]["components"])
    selected = tuple(dict.fromkeys(components))
    if not selected or any(component not in valid_components for component in selected):
        raise ValueError(f"Invalid PM components: {selected}")
    if gun["status"] != "AVAILABLE":
        raise ValueError(f"Gun {gun['gun_id']} is not available for PM")

    duration = 0
    cost = 0.0
    for component in selected:
        before = float(gun[f"{component}_hi"])
        gun[f"{component}_hi"] = max(
            before,
            min(
                before + float(config["maintenance"]["pm_recovery"][component]),
                float(config["maintenance"]["pm_cap"][component]),
            ),
        )
        duration += int(config["cost"]["pm_downtime_hours"][component])
        cost += float(config["cost"]["pm_cost"][component])

    update_gun_hi(gun, valid_components)
    gun["status"] = "PM"
    gun["downtime_remaining"] = max(duration, 1)
    gun["operating_hours_since_pm"] = 0.0
    gun["pm_visit_count"] += 1
    return {"duration": duration, "cost": cost, "components": selected}


def apply_cm_repair(
    gun: dict[str, Any], components: list[str] | tuple[str, ...], config: dict[str, Any]
) -> dict[str, Any]:
    """Apply one corrective outage; component jobs proceed in parallel during the outage."""
    selected = tuple(dict.fromkeys(components))
    if not selected:
        raise ValueError("CM repair requires at least one failed component")
    duration = 0
    cost = 0.0
    for component in selected:
        before = float(gun[f"{component}_hi"])
        gun[f"{component}_hi"] = max(
            before,
            min(
                before + float(config["maintenance"]["cm_recovery"][component]),
                float(config["maintenance"]["cm_cap"][component]),
            ),
        )
        duration = max(duration, int(config["cost"]["cm_downtime_hours"][component]))
        cost += float(config["cost"]["cm_cost"][component])

    update_gun_hi(gun, tuple(config["reliability"]["components"]))
    gun["status"] = "CM"
    gun["downtime_remaining"] = max(duration, 1)
    return {"duration": duration, "cost": cost, "components": selected}


def tick_downtime(
    guns: list[dict[str, Any]], config: dict[str, Any], costs: dict[str, float]
) -> int:
    """Advance existing PM/CM outages by one hour and price each down gun-hour."""
    down_count = 0
    for gun in guns:
        if int(gun["downtime_remaining"]) <= 0:
            continue
        down_count += 1
        gun["downtime_remaining"] -= 1
        costs["downtime"] += float(config["cost"]["downtime_cost_per_gun_hour"])
        if gun["downtime_remaining"] <= 0:
            gun["status"] = "AVAILABLE"
    return down_count


def scaled_daily_targets(config: dict[str, Any]) -> dict[str, int]:
    factor = (
        float(config["regime"]["demand_factor"])
        if bool(config["demand"]["scale_family_targets_with_regime"])
        else 1.0
    )
    return {
        family: int(round(float(target) * factor))
        for family, target in config["demand"]["family_daily_targets"].items()
    }


def _record_event(
    event_log: list[dict[str, Any]],
    event_type: str,
    day: int,
    hour: int,
    gun: dict[str, Any],
    **details: Any,
) -> None:
    event_log.append(
        {
            "event_type": event_type,
            "day": day,
            "hour": hour,
            "gun_id": gun["gun_id"],
            "status": gun["status"],
            "gun_hi": round(float(gun["gun_hi"]), 6),
            **details,
        }
    )


def run_smoke_episode(
    config: dict[str, Any], seed: int = 101, days: int = 2
) -> SimulationResult:
    """Exercise Step 2 core mechanics with a deterministic, non-policy smoke schedule."""
    rng = np.random.default_rng(seed)
    guns = build_initial_state(config, rng)
    gun_by_id = {gun["gun_id"]: gun for gun in guns}
    components = tuple(config["reliability"]["components"])
    families = tuple(config["job_families"])
    maintenance_slots = int(config["simulation"]["maintenance_slots"])
    hours_per_day = int(config["simulation"]["hours_per_day"])

    costs = {name: 0.0 for name in config["cost"]["tco_components"]}
    counts = {
        "pm_visits": 0,
        "pm_components": 0,
        "cm_events": 0,
        "failures": 0,
        "defects": 0,
        "completed_welds": 0,
        "unmet_welds": 0,
        "downtime_hours": 0,
        "max_pm_slots_used": 0,
    }
    event_log: list[dict[str, Any]] = []
    failure_log: list[dict[str, Any]] = []

    for day in range(1, days + 1):
        remaining = scaled_daily_targets(config)
        for hour in range(hours_per_day):
            counts["downtime_hours"] += tick_downtime(guns, config, costs)
            for gun in guns:
                observe_state(gun, config, rng)

            # Step 2 smoke-only maintenance schedule: exercise one targeted and one full visit.
            pm_requests: list[tuple[str, tuple[str, ...]]] = []
            if day == 1 and hour == 0:
                pm_requests = [("G01", ("tip",)), ("G02", components)]

            active_pm = sum(1 for gun in guns if gun["status"] == "PM")
            free_slots = max(maintenance_slots - active_pm, 0)
            applied = 0
            for gun_id, selected in pm_requests:
                gun = gun_by_id[gun_id]
                if applied >= free_slots or gun["status"] != "AVAILABLE":
                    continue
                result = apply_pm_decision(gun, selected, config)
                costs["pm"] += result["cost"]
                counts["pm_visits"] += 1
                counts["pm_components"] += len(result["components"])
                applied += 1
                _record_event(
                    event_log,
                    "PM",
                    day,
                    hour,
                    gun,
                    components="|".join(result["components"]),
                    duration_hours=result["duration"],
                    cost=result["cost"],
                )
            counts["max_pm_slots_used"] = max(
                counts["max_pm_slots_used"],
                sum(1 for gun in guns if gun["status"] == "PM"),
            )

            available = [gun for gun in guns if gun["status"] == "AVAILABLE"]
            for index, gun in enumerate(available):
                family = next(
                    (
                        families[(index + offset + hour) % len(families)]
                        for offset in range(len(families))
                        if remaining[families[(index + offset + hour) % len(families)]] > 0
                    ),
                    None,
                )
                if family is None:
                    break

                job = config["job_families"][family]
                losses = apply_production_wear(gun, job, config, rng)
                costs["degradation"] += compute_degradation_cost(losses, config)
                gun["operating_hours_since_pm"] += float(config["simulation"]["step_hours"])

                failed = sample_failures(gun, config, rng)
                defect = float(rng.random()) < compute_defect_probability(gun, job, config)
                if defect:
                    counts["defects"] += 1
                    costs["defect"] += float(config["cost"]["defect_event_cost"])

                completed = 0
                if failed:
                    repair = apply_cm_repair(gun, failed, config)
                    counts["cm_events"] += 1
                    counts["failures"] += len(failed)
                    costs["cm"] += repair["cost"]
                    for component in failed:
                        failure_log.append(
                            {
                                "day": day,
                                "hour": hour,
                                "gun_id": gun["gun_id"],
                                "component": component,
                                "job_family": family,
                                "component_hi_after_repair": round(
                                    float(gun[f"{component}_hi"]), 6
                                ),
                            }
                        )
                else:
                    completed = min(int(job["welds_per_hour"]), remaining[family])
                    remaining[family] -= completed
                    counts["completed_welds"] += completed

                _record_event(
                    event_log,
                    "PRODUCTION",
                    day,
                    hour,
                    gun,
                    job_family=family,
                    completed_welds=completed,
                    defect=int(defect),
                    failed_components="|".join(failed),
                    degradation_cost=round(compute_degradation_cost(losses, config), 8),
                )

        unmet = sum(remaining.values())
        counts["unmet_welds"] += unmet
        costs["unmet_demand"] += unmet * float(config["cost"]["unmet_demand_cost_per_weld"])

    total_tco = sum(costs.values())
    total_demand = sum(scaled_daily_targets(config).values()) * days
    summary = {
        "regime": config["active_regime"],
        "seed": seed,
        "days": days,
        "total_demand": total_demand,
        **counts,
        **{f"{name}_cost": round(value, 6) for name, value in costs.items()},
        "TCO": round(total_tco, 6),
        "fulfillment": round(counts["completed_welds"] / max(total_demand, 1), 6),
        "endHI_mean": round(float(np.mean([gun["gun_hi"] for gun in guns])), 6),
    }
    return SimulationResult(
        summary=summary,
        event_log=event_log,
        failure_log=failure_log,
        final_guns=guns,
    )


def run_policy_episode(
    config: dict[str, Any],
    policy_id: str,
    seed: int,
    days: int | None = None,
    record_events: bool = False,
    scenario: str = "base",
) -> SimulationResult:
    """Run one joint policy on the shared RSW environment for one seed."""
    rng = np.random.default_rng(seed)
    policy = create_joint_policy(policy_id, config)
    policy.reset()
    guns = build_initial_state(config, rng)
    gun_by_id = {gun["gun_id"]: gun for gun in guns}
    components = tuple(config["reliability"]["components"])
    families = tuple(config["job_families"])
    maintenance_slots = int(config["simulation"]["maintenance_slots"])
    hours_per_day = int(config["simulation"]["hours_per_day"])
    total_days = int(days or config["simulation"]["campaign_days"])

    costs = {name: 0.0 for name in config["cost"]["tco_components"]}
    counts = {
        "pm_visits": 0,
        "pm_components": 0,
        "cm_events": 0,
        "failures": 0,
        "defects": 0,
        "completed_welds": 0,
        "unmet_welds": 0,
        "downtime_hours": 0,
        "max_pm_slots_used": 0,
    }
    pm_component_counts = {component: 0 for component in components}
    cm_component_counts = {component: 0 for component in components}
    route_counts = {family: 0 for family in families}
    event_log: list[dict[str, Any]] = []
    failure_log: list[dict[str, Any]] = []

    for day in range(1, total_days + 1):
        targets = scaled_daily_targets(config)
        remaining = dict(targets)
        for hour in range(hours_per_day):
            counts["downtime_hours"] += tick_downtime(guns, config, costs)
            for gun in guns:
                observe_state(gun, config, rng)

            available_ids = {gun["gun_id"] for gun in guns if gun["status"] == "AVAILABLE"}
            active_pm = sum(1 for gun in guns if gun["status"] == "PM")
            free_slots = max(maintenance_slots - active_pm, 0)
            state = {
                "guns": guns,
                "available_ids": available_ids,
                "free_slots": free_slots,
                "day": day,
                "hour": hour,
                "remaining_demand": remaining,
                "daily_targets": targets,
            }
            decision = policy.decide(state)
            validate_policy_decision(decision, state, config)

            pm_ids: set[str] = set()
            for gun_id, selected, risk_score in decision["pm"]:
                gun = gun_by_id[gun_id]
                if gun["status"] != "AVAILABLE" or gun_id in pm_ids:
                    continue
                result = apply_pm_decision(gun, selected, config)
                gun["last_pm_day"] = day
                costs["pm"] += result["cost"]
                counts["pm_visits"] += 1
                counts["pm_components"] += len(result["components"])
                for component in result["components"]:
                    pm_component_counts[component] += 1
                pm_ids.add(gun_id)
                if record_events:
                    _record_event(
                        event_log,
                        "PM",
                        day,
                        hour,
                        gun,
                        policy=policy_id,
                        scenario=scenario,
                        regime=config["active_regime"],
                        seed=seed,
                        components="|".join(result["components"]),
                        risk_score=round(float(risk_score), 6),
                        duration_hours=result["duration"],
                        cost=result["cost"],
                    )

            counts["max_pm_slots_used"] = max(
                counts["max_pm_slots_used"],
                sum(1 for gun in guns if gun["status"] == "PM"),
            )

            for gun_id, ranked_families in decision["dispatch"]:
                gun = gun_by_id[gun_id]
                if gun["status"] != "AVAILABLE" or gun_id in pm_ids:
                    continue
                family = next(
                    (candidate for candidate in ranked_families if remaining[candidate] > 0),
                    None,
                )
                if family is None:
                    continue

                job = config["job_families"][family]
                losses = apply_production_wear(gun, job, config, rng)
                degradation_cost = compute_degradation_cost(losses, config)
                costs["degradation"] += degradation_cost
                gun["operating_hours_since_pm"] += float(config["simulation"]["step_hours"])
                failed = sample_failures(gun, config, rng)
                defect = float(rng.random()) < compute_defect_probability(gun, job, config)
                if defect:
                    counts["defects"] += 1
                    costs["defect"] += float(config["cost"]["defect_event_cost"])

                completed = 0
                if failed:
                    repair = apply_cm_repair(gun, failed, config)
                    counts["cm_events"] += 1
                    counts["failures"] += len(failed)
                    costs["cm"] += repair["cost"]
                    for component in failed:
                        cm_component_counts[component] += 1
                        failure_log.append(
                            {
                                "policy": policy_id,
                                "scenario": scenario,
                                "regime": config["active_regime"],
                                "seed": seed,
                                "day": day,
                                "hour": hour,
                                "gun_id": gun_id,
                                "component": component,
                                "job_family": family,
                                "component_hi_after_repair": round(
                                    float(gun[f"{component}_hi"]), 6
                                ),
                                "gun_max_frailty": round(
                                    max(float(gun[f"{c}_frailty"]) for c in components), 6
                                ),
                            }
                        )
                else:
                    completed = min(int(job["welds_per_hour"]), remaining[family])
                    remaining[family] -= completed
                    counts["completed_welds"] += completed
                    route_counts[family] += completed

                if record_events:
                    _record_event(
                        event_log,
                        "PRODUCTION",
                        day,
                        hour,
                        gun,
                        policy=policy_id,
                        scenario=scenario,
                        regime=config["active_regime"],
                        seed=seed,
                        job_family=family,
                        completed_welds=completed,
                        defect=int(defect),
                        failed_components="|".join(failed),
                        degradation_cost=round(degradation_cost, 8),
                    )

        unmet = sum(remaining.values())
        counts["unmet_welds"] += unmet
        costs["unmet_demand"] += unmet * float(config["cost"]["unmet_demand_cost_per_weld"])

    total_demand = sum(scaled_daily_targets(config).values()) * total_days
    frailty_values = [
        float(gun[f"{component}_frailty"]) for gun in guns for component in components
    ]
    summary = {
        "scenario": scenario,
        "regime": config["active_regime"],
        "policy": policy_id,
        "seed": seed,
        "days": total_days,
        "total_demand": total_demand,
        **counts,
        **{f"pm_{component}": pm_component_counts[component] for component in components},
        **{f"cm_{component}": cm_component_counts[component] for component in components},
        **{f"route_{family}": route_counts[family] for family in families},
        **{f"{name}_cost": round(value, 6) for name, value in costs.items()},
        "TCO": round(sum(costs.values()), 6),
        "fulfillment": round(counts["completed_welds"] / max(total_demand, 1), 6),
        "endHI_mean": round(float(np.mean([gun["gun_hi"] for gun in guns])), 6),
        "avg_frailty": round(float(np.mean(frailty_values)), 6),
        "max_frailty": round(float(np.max(frailty_values)), 6),
    }
    return SimulationResult(summary, event_log, failure_log, guns)


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    return statistics.mean(float(row[key]) for row in rows)


def aggregate_policy_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build one required KPI summary row per regime and policy."""
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row.get("scenario", "base"), row["regime"], row["policy"]), []).append(row)
    output = []
    for (scenario, regime, policy), group in grouped.items():
        pm_total = max(_mean(group, "pm_components"), 1e-12)
        cm_total = max(_mean(group, "failures"), 1e-12)
        route_total = max(_mean(group, "completed_welds"), 1e-12)
        output.append(
            {
                "scenario": scenario,
                "regime": regime,
                "policy": policy,
                "seed_count": len(group),
                "days": int(group[0]["days"]),
                "TCO_mean": round(_mean(group, "TCO"), 6),
                "TCO_std": round(statistics.pstdev(float(row["TCO"]) for row in group), 6),
                "PMvisits_mean": round(_mean(group, "pm_visits"), 6),
                "PMcomps_mean": round(_mean(group, "pm_components"), 6),
                "CM_mean": round(_mean(group, "cm_events"), 6),
                "failure_mean": round(_mean(group, "failures"), 6),
                "defect_mean": round(_mean(group, "defects"), 6),
                "fulfillment_mean": round(_mean(group, "fulfillment"), 6),
                "completed_welds_mean": round(_mean(group, "completed_welds"), 6),
                "unmet_welds_mean": round(_mean(group, "unmet_welds"), 6),
                "endHI_mean": round(_mean(group, "endHI_mean"), 6),
                "downtime_hours_mean": round(_mean(group, "downtime_hours"), 6),
                **{
                    f"{name}_cost_mean": round(_mean(group, f"{name}_cost"), 6)
                    for name in ("pm", "cm", "downtime", "degradation", "unmet_demand", "defect")
                },
                **{
                    f"pm_{component}_share": round(_mean(group, f"pm_{component}") / pm_total, 6)
                    for component in ("tip", "cooling", "actuator")
                },
                **{
                    f"cm_{component}_share": round(_mean(group, f"cm_{component}") / cm_total, 6)
                    for component in ("tip", "cooling", "actuator")
                },
                **{
                    f"route_{family}_share": round(_mean(group, f"route_{family}") / route_total, 6)
                    for family in ("A", "B", "C")
                },
            }
        )
    return sorted(output, key=lambda row: (row["scenario"], row["regime"], row["TCO_mean"]))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_policy_sweep(
    base_config: dict[str, Any],
    policies: list[str],
    seeds: list[int],
    regimes: list[str],
    days: int,
    scenario: str = "base",
    output_spec: dict[str, Any] | None = None,
    family_daily_targets: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    """Run a policy sweep and write only to its explicit base or sanity output contract."""
    run_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    failure_rows: list[dict[str, Any]] = []
    for regime in regimes:
        config = load_config(regime=regime)
        if family_daily_targets is not None:
            config["demand"]["family_daily_targets"] = copy.deepcopy(family_daily_targets)
            config["demand"]["daily_weld_demand"] = sum(family_daily_targets.values())
        for policy_id in policies:
            for seed in seeds:
                result = run_policy_episode(
                    config, policy_id, seed, days, record_events=True, scenario=scenario
                )
                run_rows.append(result.summary)
                event_rows.extend(result.event_log)
                failure_rows.extend(result.failure_log)
            policy_rows = [row for row in run_rows if row["regime"] == regime and row["policy"] == policy_id]
            print(
                f"{regime} {policy_id}: TCO={_mean(policy_rows, 'TCO'):.2f} "
                f"PM={_mean(policy_rows, 'pm_visits'):.1f} CM={_mean(policy_rows, 'cm_events'):.1f}",
                flush=True,
            )

    outputs = output_spec or {
        key: base_config["outputs"][key]
        for key in ("directory", "policy_summary_csv", "event_log_csv", "failure_log_csv")
    }
    output_dir = ROOT / outputs["directory"]
    write_csv(output_dir / outputs["policy_summary_csv"], aggregate_policy_summaries(run_rows))
    write_csv(output_dir / outputs["event_log_csv"], event_rows)
    write_csv(output_dir / outputs["failure_log_csv"], failure_rows)
    return run_rows


def run_configured_scenario(
    base_config: dict[str, Any], scenario: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run one config-defined sanity scenario without inheriting base output paths."""
    contract = build_scenario_contract(base_config, scenario)
    rows = run_policy_sweep(
        base_config,
        policies=contract["policies"],
        seeds=contract["seeds"],
        regimes=contract["regimes"],
        days=contract["days"],
        scenario=contract["scenario"],
        output_spec=contract["outputs"],
        family_daily_targets=contract["family_daily_targets"],
    )
    return rows, contract


def validate_smoke_result(result: SimulationResult, config: dict[str, Any]) -> None:
    """Assert Step 2 invariants without claiming policy-comparison behavior."""
    components = config["reliability"]["components"]
    for gun in result.final_guns:
        assert 0.0 <= float(gun["gun_hi"]) <= 1.0
        assert 0.0 <= float(gun["observed_gun_hi"]) <= 1.0
        for component in components:
            assert 0.0 <= float(gun[f"{component}_hi"]) <= 1.0
            assert 0.0 <= float(gun[f"observed_{component}_hi"]) <= 1.0

    cost_sum = sum(
        float(result.summary[f"{name}_cost"]) for name in config["cost"]["tco_components"]
    )
    assert math.isclose(cost_sum, float(result.summary["TCO"]), abs_tol=1e-5)
    assert result.summary["max_pm_slots_used"] <= config["simulation"]["maintenance_slots"]
    assert result.summary["pm_visits"] == 2
    assert result.summary["pm_components"] == 4

    # G01 targeted tip PM and G02 full PM must remain below 1.0 because configured caps are partial.
    for gun_id in ("G01", "G02"):
        gun = next(gun for gun in result.final_guns if gun["gun_id"] == gun_id)
        assert all(float(gun[f"{component}_hi"]) < 1.0 for component in components)


def main() -> int:
    parser = argparse.ArgumentParser(description="RSW C5.4 Level 2 mini transfer simulation.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true", help="run the Step 2 core smoke episode")
    mode.add_argument("--sweep", action="store_true", help="run the approved Step 4 base policy sweep")
    mode.add_argument(
        "--demand-stress",
        action="store_true",
        help="run the optional config-defined demand pressure sanity scenario",
    )
    mode.add_argument(
        "--horizon-sanity-90",
        action="store_true",
        help="run the optional config-defined 90-day horizon sanity scenario",
    )
    parser.add_argument("--days", type=int, default=None, help="override campaign horizon")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--regime", default=None)
    parser.add_argument("--regimes", nargs="+", default=None)
    parser.add_argument("--policies", nargs="+", default=None)
    args = parser.parse_args()

    if args.demand_stress or args.horizon_sanity_90:
        overrides = (args.days, args.seed, args.seeds, args.regime, args.regimes, args.policies)
        if any(value is not None for value in overrides):
            parser.error("Sanity scenario flags use their config-defined execution contract; remove overrides.")
        scenario = "demand_pressure_stress" if args.demand_stress else "horizon_sanity_90"
        _, contract = run_configured_scenario(load_config(), scenario)
        print(f"Wrote {scenario} CSV outputs to {ROOT / contract['outputs']['directory']}")
        return 0

    if args.sweep:
        base = load_config()
        policies = args.policies or list(base["policies"]["enabled"])
        seeds = args.seeds or [int(seed) for seed in base["simulation"]["seeds"]]
        regimes = args.regimes or list(base["regimes"])
        days = int(args.days or base["simulation"]["campaign_days"])
        run_policy_sweep(base, policies, seeds, regimes, days)
        print(f"Wrote Step 4 CSV outputs to {ROOT / base['outputs']['directory']}")
        return 0

    config = load_config(regime=args.regime)
    result = run_smoke_episode(config, seed=int(args.seed or 101), days=int(args.days or 2))
    validate_smoke_result(result, config)
    print("RSW Step 2 smoke validation passed.")
    for key, value in result.summary.items():
        print(f"{key}: {value}")
    print(f"event_log_rows: {len(result.event_log)}")
    print(f"failure_log_rows: {len(result.failure_log)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
