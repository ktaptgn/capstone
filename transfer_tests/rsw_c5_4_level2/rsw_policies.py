"""Joint PM-scheduling and production-assignment policies for the RSW Level 2 mini-test."""

from __future__ import annotations

import math
from typing import Any, Protocol


Referral = tuple[str, tuple[str, ...], float]
DispatchRanking = tuple[str, list[str]]


class JointPolicy(Protocol):
    policy_id: str

    def reset(self) -> None:
        ...

    def decide(self, state: dict[str, Any]) -> dict[str, list[Any]]:
        ...


def component_risk(component: str, observed_hi: float) -> float:
    """Bounded observed-condition risk; does not access latent true HI."""
    criticality = {"tip": 1.0, "cooling": 1.05, "actuator": 1.10}.get(component, 1.0)
    return min(max((1.0 - float(observed_hi)) * criticality, 0.0), 1.0)


def _gun_index(gun_id: str) -> int:
    digits = "".join(character for character in gun_id if character.isdigit())
    return int(digits) if digits else 0


class BaseJointPolicy:
    policy_id = "BASE"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.components = tuple(config["reliability"]["components"])
        self.families = tuple(config["job_families"])

    def reset(self) -> None:
        pass

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        raise NotImplementedError

    def dispatch_rankings(self, state: dict[str, Any]) -> list[DispatchRanking]:
        raise NotImplementedError

    def decide(self, state: dict[str, Any]) -> dict[str, list[Any]]:
        candidates = sorted(self.pm_candidates(state), key=lambda referral: referral[2], reverse=True)
        pm = candidates[: max(int(state["free_slots"]), 0)]
        return {"pm": pm, "dispatch": self.dispatch_rankings(state)}

    def observed(self, gun: dict[str, Any], component: str) -> float:
        return float(gun[f"observed_{component}_hi"])

    def max_risk(self, gun: dict[str, Any], components: tuple[str, ...]) -> float:
        return max((component_risk(c, self.observed(gun, c)) for c in components), default=0.0)

    def available_guns(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        available_ids = state["available_ids"]
        return [gun for gun in state["guns"] if gun["gun_id"] in available_ids]

    def family_stress(self, gun: dict[str, Any], family: str) -> float:
        severity = self.config["job_families"][family]["severity"]
        return sum(
            component_risk(component, self.observed(gun, component))
            * float(severity[component])
            for component in self.components
        )

    def family_value(self, family: str) -> float:
        return float(self.config["job_families"][family]["value_weight"])

    def family_severity(self, family: str) -> float:
        values = self.config["job_families"][family]["severity"].values()
        return sum(float(value) for value in values) / len(self.components)

    def remaining_fraction(self, state: dict[str, Any], family: str) -> float:
        remaining = float(state["remaining_demand"].get(family, 0))
        targets = state.get("daily_targets", {})
        target = max(float(targets.get(family, remaining)), 1.0)
        return remaining / target


class H0CalendarBlindPolicy(BaseJointPolicy):
    policy_id = "H0"

    def blind_priority(self, gun: dict[str, Any]) -> float:
        count = max(int(self.config["simulation"]["gun_count"]), 1)
        return max(0.0, 1.0 - _gun_index(gun["gun_id"]) / (count + 1.0))

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        interval = max(int(self.config["pm_scheduling"]["calendar"]["interval_days"]), 1)
        day = int(state["day"])
        candidates = []
        for gun in self.available_guns(state):
            phase = _gun_index(gun["gun_id"]) % interval
            if (
                day >= phase
                and (day - phase) % interval == 0
                and int(gun.get("last_pm_day", 0)) != day
            ):
                candidates.append((gun["gun_id"], self.components, self.blind_priority(gun)))
        return candidates

    def dispatch_rankings(self, state: dict[str, Any]) -> list[DispatchRanking]:
        output = []
        for index, gun in enumerate(self.available_guns(state)):
            ranked = [self.families[(index + offset) % len(self.families)] for offset in range(len(self.families))]
            output.append((gun["gun_id"], ranked))
        return output


class HTimeHoursBlindPolicy(H0CalendarBlindPolicy):
    policy_id = "H_TIME"

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        due = float(self.config["pm_scheduling"]["operating_hours"]["due_hours"])
        return [
            (gun["gun_id"], self.components, self.blind_priority(gun))
            for gun in self.available_guns(state)
            if float(gun["operating_hours_since_pm"]) >= due
        ]


class H1ConditionHealthPolicy(BaseJointPolicy):
    policy_id = "H1"

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        thresholds = self.config["pm_scheduling"]["cbm_threshold"]
        override = float(self.config["pm_scheduling"]["critical_risk_override"])
        output = []
        for gun in self.available_guns(state):
            flagged = tuple(
                component
                for component in self.components
                if self.observed(gun, component) <= float(thresholds[component])
                or component_risk(component, self.observed(gun, component)) >= override
            )
            if flagged:
                output.append((gun["gun_id"], flagged, self.max_risk(gun, flagged)))
        return output

    def dispatch_rankings(self, state: dict[str, Any]) -> list[DispatchRanking]:
        guns = sorted(
            self.available_guns(state),
            key=lambda gun: float(gun["observed_gun_hi"]),
            reverse=True,
        )
        output = []
        for gun in guns:
            ranked = sorted(
                self.families,
                key=lambda family: (
                    (float(gun["observed_gun_hi"]) - 0.5)
                    * self.family_severity(family)
                    + 0.1 * self.remaining_fraction(state, family)
                ),
                reverse=True,
            )
            output.append((gun["gun_id"], ranked))
        return output


class H2RiskPriorityPolicy(BaseJointPolicy):
    policy_id = "H2"

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        threshold = float(self.config["pm_scheduling"]["risk_priority"]["risk_threshold"])
        output = []
        for gun in self.available_guns(state):
            flagged = tuple(
                component
                for component in self.components
                if component_risk(component, self.observed(gun, component)) >= threshold
            )
            if flagged:
                output.append((gun["gun_id"], flagged, self.max_risk(gun, flagged)))
        return output

    def dispatch_rankings(self, state: dict[str, Any]) -> list[DispatchRanking]:
        guns = sorted(
            self.available_guns(state),
            key=lambda gun: self.max_risk(gun, self.components),
        )
        return [
            (
                gun["gun_id"],
                sorted(
                    self.families,
                    key=lambda family: (
                        self.remaining_fraction(state, family)
                        - self.family_stress(gun, family)
                    ),
                    reverse=True,
                ),
            )
            for gun in guns
        ]


class H3CostValuePolicy(BaseJointPolicy):
    policy_id = "H3"

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        lookahead = max(float(self.config["pm_scheduling"]["cost_value"]["lookahead_hours"]), 1.0)
        failure_thresholds = self.config["reliability"]["failure_hazard"]["threshold_hi"]
        base_loss = self.config["reliability"]["wear"]["base_loss_per_hour"]
        output = []
        for gun in self.available_guns(state):
            flagged = []
            best_probability = 0.0
            for component in self.components:
                observed = self.observed(gun, component)
                hourly_loss = (
                    float(base_loss[component])
                    * float(self.config["regime"]["wear_factor"])
                )
                hours_to_floor = max(
                    (observed - float(failure_thresholds[component])) / max(hourly_loss, 1e-12),
                    0.0,
                )
                p_soon = max(0.0, min(1.0, 1.0 - hours_to_floor / lookahead))
                avoided = p_soon * float(self.config["cost"]["cm_cost"][component])
                pm_cost = float(self.config["cost"]["pm_cost"][component])
                if avoided >= pm_cost:
                    flagged.append(component)
                    best_probability = max(best_probability, p_soon)
            if flagged:
                output.append((gun["gun_id"], tuple(flagged), best_probability))
        return output

    def dispatch_rankings(self, state: dict[str, Any]) -> list[DispatchRanking]:
        output = []
        for gun in self.available_guns(state):
            ranked = sorted(
                self.families,
                key=lambda family: (
                    self.family_value(family) * self.remaining_fraction(state, family)
                    - 2.0 * self.family_stress(gun, family)
                ),
                reverse=True,
            )
            output.append((gun["gun_id"], ranked))
        output.sort(
            key=lambda item: self.family_value(item[1][0]) * self.remaining_fraction(state, item[1][0]),
            reverse=True,
        )
        return output


class H4FlowBackpressurePolicy(BaseJointPolicy):
    policy_id = "H4"

    def pm_candidates(self, state: dict[str, Any]) -> list[Referral]:
        soft = float(self.config["pm_scheduling"]["flow_backpressure"]["soft_threshold_hi"])
        critical = float(self.config["pm_scheduling"]["flow_backpressure"]["critical_threshold_hi"])
        available = self.available_guns(state)
        remaining_welds = sum(max(int(value), 0) for value in state["remaining_demand"].values())
        max_rate = max(
            int(job["welds_per_hour"]) for job in self.config["job_families"].values()
        )
        guns_needed = min(math.ceil(remaining_welds / max(max_rate, 1)), len(available))
        slack = max(len(available) - guns_needed, 0)
        critical_output: list[Referral] = []
        soft_output: list[Referral] = []
        for gun in available:
            critical_components = tuple(
                component
                for component in self.components
                if self.observed(gun, component) <= critical
            )
            if critical_components:
                critical_output.append(
                    (gun["gun_id"], critical_components, self.max_risk(gun, critical_components))
                )
                continue
            soft_components = tuple(
                component
                for component in self.components
                if self.observed(gun, component) <= soft
            )
            if soft_components:
                soft_output.append(
                    (gun["gun_id"], soft_components, self.max_risk(gun, soft_components))
                )
        soft_output.sort(key=lambda referral: referral[2], reverse=True)
        return critical_output + soft_output[:slack]

    def dispatch_rankings(self, state: dict[str, Any]) -> list[DispatchRanking]:
        families = sorted(
            self.families,
            key=lambda family: (
                state["remaining_demand"].get(family, 0),
                self.config["job_families"][family]["welds_per_hour"],
            ),
            reverse=True,
        )
        guns = sorted(
            self.available_guns(state),
            key=lambda gun: float(gun["observed_gun_hi"]),
            reverse=True,
        )
        return [(gun["gun_id"], list(families)) for gun in guns]


POLICY_REGISTRY: dict[str, type[BaseJointPolicy]] = {
    "H0": H0CalendarBlindPolicy,
    "H_TIME": HTimeHoursBlindPolicy,
    "H1": H1ConditionHealthPolicy,
    "H2": H2RiskPriorityPolicy,
    "H3": H3CostValuePolicy,
    "H4": H4FlowBackpressurePolicy,
}


def create_joint_policy(policy_id: str, config: dict[str, Any]) -> BaseJointPolicy:
    if policy_id not in POLICY_REGISTRY:
        raise ValueError(f"Unknown RSW joint policy: {policy_id}")
    return POLICY_REGISTRY[policy_id](config)


def validate_policy_decision(
    decision: dict[str, list[Any]], state: dict[str, Any], config: dict[str, Any]
) -> None:
    """Validate the structural contract shared by every heuristic and future agent adapter."""
    assert set(decision) == {"pm", "dispatch"}
    assert len(decision["pm"]) <= int(state["free_slots"])
    available_ids = set(state["available_ids"])
    components = set(config["reliability"]["components"])
    families = set(config["job_families"])
    pm_ids = set()
    for gun_id, selected, risk in decision["pm"]:
        assert gun_id in available_ids and gun_id not in pm_ids
        assert selected and set(selected).issubset(components)
        assert 0.0 <= float(risk) <= 1.0
        pm_ids.add(gun_id)
    dispatch_ids = set()
    for gun_id, ranked in decision["dispatch"]:
        assert gun_id in available_ids and gun_id not in dispatch_ids
        assert len(ranked) == len(families) and set(ranked) == families
        dispatch_ids.add(gun_id)
    assert dispatch_ids == available_ids


__all__ = [
    "JointPolicy",
    "BaseJointPolicy",
    "POLICY_REGISTRY",
    "create_joint_policy",
    "validate_policy_decision",
]
