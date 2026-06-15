from __future__ import annotations

from typing import Any

from mine_env.costs_c5_4 import C5_4CostModel
from mine_env.reliability_c5_4 import COMPONENTS, C5_4ReliabilityModel


# A PM referral is one *shop visit*: a single truck occupies one PM bay and the listed
# components are all serviced in that visit (cost = sum of component PM costs, downtime = sum
# of component PM durations). This per-truck-visit bay model is a deliberate refinement over
# C5.3's per-component bay slot -- it is the realistic semantics of a maintenance bay (a truck
# is in the shop once and several jobs are done) and it sharpens the C5.4 contrast: a BLIND
# baseline does a *full* service (all three components) on a fixed clock, while a STATE-AWARE
# rule services only the components actually flagged, when they are flagged.
#
# Referral tuple = (truck_id, components, priority_risk).
Referral = tuple[str, tuple[str, ...], float]


def _truck_index(truck_id: str) -> int:
    digits = "".join(ch for ch in truck_id if ch.isdigit())
    return int(digits) if digits else 0


class PMSchedulingRule:
    """Base class for a C5.4 PM-scheduling family.

    In C5.3 preventive maintenance was a single FIXED CBM rule shared by every policy. C5.4
    makes PM scheduling a *decision*: each policy carries one of these rules, so the comparison
    now spans the PM-trigger philosophy (calendar / operating-hours / condition / risk / value /
    flow), not only dispatch. Every rule reads the OBSERVED (noisy) component HI -- never the
    latent truth (POMDP) -- and returns up to ``free_bays`` shop-visit referrals, worst-priority
    first, at most one per truck this step. Subclasses implement :meth:`candidates`.
    """

    family = "BASE"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.reliability = C5_4ReliabilityModel(config)

    def reset(self) -> None:  # rules with internal clocks override this
        pass

    # subclasses return [(truck_id, components, priority_risk)] over eligible trucks (unsorted)
    def candidates(
        self,
        trucks: list[dict[str, Any]],
        available_ids: set[str],
        step: int,
        context: dict[str, Any],
    ) -> list[Referral]:
        raise NotImplementedError

    def select_referrals(
        self,
        trucks: list[dict[str, Any]],
        available_ids: set[str],
        step: int,
        free_bays: int,
        context: dict[str, Any],
    ) -> list[Referral]:
        if free_bays <= 0:
            return []
        cands = self.candidates(trucks, available_ids, step, context)
        cands.sort(key=lambda item: item[2], reverse=True)
        chosen: list[Referral] = []
        seen: set[str] = set()
        for truck_id, components, risk in cands:
            if len(chosen) >= free_bays:
                break
            if truck_id in seen or not components:
                continue
            seen.add(truck_id)
            chosen.append((truck_id, components, risk))
        return chosen

    # --- shared helpers (all on OBSERVED HI) ---
    def _obs(self, truck: dict[str, Any], component: str) -> float:
        return float(truck[f"observed_{component}_hi"])

    def _max_risk(self, truck: dict[str, Any], components: tuple[str, ...]) -> float:
        return max(
            (self.reliability.component_risk_score(c, self._obs(truck, c)) for c in components),
            default=0.0,
        )


# --------------------------------------------------------------------------------------------
# BLIND PERIODIC families -- trigger on a clock, service the whole vehicle (all components),
# condition-blind in WHEN they fire. Their nominal cadence is set to the steady-state cadence
# of the fastest-wearing component at average conditions (see configs/c5_4.yaml); under frailty
# and rough routes real wear outpaces that clock, so they under-protect fast trucks (CM) while
# over-paying for full services -- the C5.2 "blind periodic is penalised" lesson, reproduced.
# --------------------------------------------------------------------------------------------
class CalendarPMRule(PMSchedulingRule):
    """H0 family -- fixed calendar interval, full vehicle service, staggered across the fleet."""

    family = "calendar"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.interval_days = max(int(config["pm_scheduling"]["calendar"]["interval_days"]), 1)

    def candidates(self, trucks, available_ids, step, context):
        day = int(context["day"])
        out: list[Referral] = []
        for truck in trucks:
            tid = truck["truck_id"]
            if tid not in available_ids:
                continue
            phase = _truck_index(tid) % self.interval_days
            if day >= phase and (day - phase) % self.interval_days == 0:
                out.append((tid, COMPONENTS, self._max_risk(truck, COMPONENTS)))
        return out


class OperatingHoursPMRule(PMSchedulingRule):
    """H_TIME family -- PM when operating-hours-since-PM reach a usage budget; full service."""

    family = "operating_hours"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.due_hours = float(config["pm_scheduling"]["operating_hours"]["due_hours"])

    def candidates(self, trucks, available_ids, step, context):
        out: list[Referral] = []
        for truck in trucks:
            tid = truck["truck_id"]
            if tid not in available_ids:
                continue
            if float(truck.get("operating_hours_since_pm", 0.0)) >= self.due_hours:
                out.append((tid, COMPONENTS, self._max_risk(truck, COMPONENTS)))
        return out


# --------------------------------------------------------------------------------------------
# STATE-AWARE families -- trigger on the observed condition, service only the flagged
# components. These read the noisy observation, never the truth.
# --------------------------------------------------------------------------------------------
class ConditionCBMPMRule(PMSchedulingRule):
    """H1 family -- condition-based (CBM) threshold rule (the C5.3 frozen engine, now a choice).

    Refer the components whose OBSERVED HI is at/below a per-component threshold (the C6.1
    grid-search frozen optimum 0.21/0.21/0.28) or whose risk crosses the override; a
    per-(truck, component) cooldown prevents thrashing on noisy observations near the threshold.
    """

    family = "condition"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        rule = config["rule_based_pm"]
        self.thresholds = {c: float(rule["hi_threshold"][c]) for c in COMPONENTS}
        self.risk_override = float(rule.get("failure_risk_override", 1.0))
        self.cooldown = int(rule.get("cooldown_steps_per_truck_component", 0) or 0)
        self.last_pm_step: dict[tuple[str, str], int] = {}

    def reset(self) -> None:
        self.last_pm_step = {}

    def candidates(self, trucks, available_ids, step, context):
        out: list[Referral] = []
        for truck in trucks:
            tid = truck["truck_id"]
            if tid not in available_ids:
                continue
            flagged: list[str] = []
            best_risk = 0.0
            for component in COMPONENTS:
                obs = self._obs(truck, component)
                risk = self.reliability.component_risk_score(component, obs)
                critical = risk >= self.risk_override
                if not (obs <= self.thresholds[component] or critical):
                    continue
                if not critical and self.cooldown > 0:
                    last = self.last_pm_step.get((tid, component), -self.cooldown)
                    if step - last < self.cooldown:
                        continue
                flagged.append(component)
                best_risk = max(best_risk, risk)
            if flagged:
                for component in flagged:
                    self.last_pm_step[(tid, component)] = step
                out.append((tid, tuple(flagged), best_risk))
        return out


class RiskPriorityPMRule(PMSchedulingRule):
    """H2 family -- PM the highest-risk components first (risk-priority philosophy).

    Refer every component whose observed condition-risk is at/above a risk threshold; trucks are
    then ordered worst-risk first, so under bay contention the most dangerous trucks are served.
    """

    family = "risk_priority"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.risk_threshold = float(config["pm_scheduling"]["risk_priority"]["risk_threshold"])

    def candidates(self, trucks, available_ids, step, context):
        out: list[Referral] = []
        for truck in trucks:
            tid = truck["truck_id"]
            if tid not in available_ids:
                continue
            flagged: list[str] = []
            best_risk = 0.0
            for component in COMPONENTS:
                risk = self.reliability.component_risk_score(component, self._obs(truck, component))
                if risk >= self.risk_threshold:
                    flagged.append(component)
                    best_risk = max(best_risk, risk)
            if flagged:
                out.append((tid, tuple(flagged), best_risk))
        return out


class CostValuePMRule(PMSchedulingRule):
    """H3 family -- PM only when the expected corrective cost it avoids exceeds the PM cost.

    For each component, estimate hauls-until-it-crosses the failure threshold at the nominal
    (frailty=1, gentle-route) wear rate, turn that into a near-term failure probability
    ``p_soon = clip(1 - hauls_to_threshold / lookahead_hauls, 0, 1)``, and refer the component
    when ``p_soon * cm_cost >= pm_cost``. Because corrective repair costs ~4x a PM, this fires
    before the failure floor but tolerates wear longer than a fixed threshold -- a deliberately
    cost-driven operating point. All inputs are documented cost/wear values; the only knob is the
    anticipation window (~one day of hauls), which is principled, not tuned (see config).
    """

    family = "cost_value"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.lookahead = max(float(config["pm_scheduling"]["cost_value"]["lookahead_hauls"]), 1.0)
        costs = C5_4CostModel(config)
        self.pm_cost = {c: costs.pm[c]["cost"] for c in COMPONENTS}
        self.cm_cost = {c: costs.cm[c]["cost"] for c in COMPONENTS}
        self.threshold_hi = self.reliability.threshold_hi
        # nominal per-haul loss (frailty=1, gentle route mult=1) with the active regime wear
        self.nominal_loss = {
            c: float(self.reliability.base_loss.get(c, 0.0) or 0.0) * self.reliability.wear_multiplier
            for c in COMPONENTS
        }

    def _p_soon(self, component: str, obs: float) -> float:
        if obs <= self.threshold_hi:
            return 1.0
        loss = self.nominal_loss[component]
        if loss <= 0:
            return 0.0
        hauls_to_threshold = (obs - self.threshold_hi) / loss
        return max(0.0, min(1.0, 1.0 - hauls_to_threshold / self.lookahead))

    def candidates(self, trucks, available_ids, step, context):
        out: list[Referral] = []
        for truck in trucks:
            tid = truck["truck_id"]
            if tid not in available_ids:
                continue
            flagged: list[str] = []
            best_p = 0.0
            for component in COMPONENTS:
                p_soon = self._p_soon(component, self._obs(truck, component))
                if p_soon * self.cm_cost[component] >= self.pm_cost[component]:
                    flagged.append(component)
                    best_p = max(best_p, p_soon)
            if flagged:
                out.append((tid, tuple(flagged), best_p))
        return out


class FlowBackpressurePMRule(PMSchedulingRule):
    """H4 family -- opportunistic PM scheduled into spare fleet capacity (flow/backpressure).

    Maintenance is deferred while demand pressure is high (every truck is needed to haul) and is
    performed only when the fleet has slack -- more available trucks than the demand slots this
    step. When slack exists, it services the worn components (observed HI below a soft threshold)
    of as many trucks as the slack and free bays allow. The honest failure mode: under sustained
    high demand it keeps deferring PM, so components drift toward the floor and corrective repairs
    rise -- "maintain only when convenient" punished exactly when reliability binds.
    """

    family = "flow_backpressure"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.soft_threshold = float(
            config["pm_scheduling"]["flow_backpressure"]["soft_threshold_hi"]
        )

    def candidates(self, trucks, available_ids, step, context):
        slack = int(context.get("available_count", 0)) - int(context.get("slots_this_step", 0))
        if slack <= 0:
            return []
        out: list[Referral] = []
        for truck in trucks:
            tid = truck["truck_id"]
            if tid not in available_ids:
                continue
            flagged = [c for c in COMPONENTS if self._obs(truck, c) <= self.soft_threshold]
            if flagged:
                out.append((tid, tuple(flagged), self._max_risk(truck, tuple(flagged))))
        # only as many as the slack permits (free-bay cap is applied by select_referrals)
        out.sort(key=lambda item: item[2], reverse=True)
        return out[:slack]


PM_RULE_REGISTRY: dict[str, type[PMSchedulingRule]] = {
    "calendar": CalendarPMRule,
    "operating_hours": OperatingHoursPMRule,
    "condition": ConditionCBMPMRule,
    "risk_priority": RiskPriorityPMRule,
    "cost_value": CostValuePMRule,
    "flow_backpressure": FlowBackpressurePMRule,
}


def create_pm_rule(family: str, config: dict[str, Any]) -> PMSchedulingRule:
    if family not in PM_RULE_REGISTRY:
        raise ValueError(f"Unknown C5.4 PM-scheduling family: {family}")
    return PM_RULE_REGISTRY[family](config)


__all__ = [
    "Referral",
    "PMSchedulingRule",
    "CalendarPMRule",
    "OperatingHoursPMRule",
    "ConditionCBMPMRule",
    "RiskPriorityPMRule",
    "CostValuePMRule",
    "FlowBackpressurePMRule",
    "PM_RULE_REGISTRY",
    "create_pm_rule",
]
