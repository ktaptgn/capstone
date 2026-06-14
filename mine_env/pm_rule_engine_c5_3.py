from __future__ import annotations

from typing import Any

from mine_env.reliability_c5_3 import COMPONENTS, C5_3ReliabilityModel


PM_BY_COMPONENT = {"tire": "PM_TIRE", "engine": "PM_ENGINE", "brake": "PM_BRAKE"}


class C5_3RuleBasedPMEngine:
    """Fixed, shared condition-based (CBM) preventive-maintenance rule.

    PM is NOT a decision variable in C5.3: every dispatch policy delegates maintenance to
    this byte-identical engine, so only dispatch differs across policies. Each step it
    refers components to the PM bay when their OBSERVED HI is at/below a per-component
    threshold (the C6.1 grid-search frozen CBM optimum, 0.21/0.21/0.28) or a failure-risk
    override fires. Referrals respect PM-bay capacity (worst failure-risk first, at most one
    component per truck per step) and a per-component cooldown. The engine reads only the
    noisy observation, never the latent truth (POMDP), exactly as a real CBM program would.
    """

    def __init__(self, config: dict[str, Any], reliability: C5_3ReliabilityModel):
        rule = config["rule_based_pm"]
        self.thresholds = {c: float(rule["hi_threshold"][c]) for c in COMPONENTS}
        self.risk_override = float(rule.get("failure_risk_override", 1.0))
        self.cooldown = int(rule.get("cooldown_steps_per_truck_component", 0) or 0)
        self.reliability = reliability
        self.last_pm_step: dict[tuple[str, str], int] = {}

    def reset(self) -> None:
        self.last_pm_step = {}

    def select_referrals(
        self,
        trucks: list[dict[str, Any]],
        available_ids: set[str],
        step: int,
        free_bays: int,
    ) -> list[tuple[str, str, str, float]]:
        """Return up to ``free_bays`` referrals as ``(truck_id, component, action, risk)``,
        worst failure-risk first; at most one component per truck this step."""
        if free_bays <= 0:
            return []
        candidates: list[tuple[float, str, str]] = []
        for truck in trucks:
            truck_id = truck["truck_id"]
            if truck_id not in available_ids:
                continue
            for component in COMPONENTS:
                observed_hi = float(truck[f"observed_{component}_hi"])
                risk = self.reliability.component_risk_score(component, observed_hi)
                critical = risk >= self.risk_override
                eligible = observed_hi <= self.thresholds[component] or critical
                if not eligible:
                    continue
                if not critical and self.cooldown > 0:
                    last = self.last_pm_step.get((truck_id, component), -self.cooldown)
                    if step - last < self.cooldown:
                        continue
                candidates.append((risk, truck_id, component))

        candidates.sort(key=lambda item: item[0], reverse=True)
        chosen: list[tuple[str, str, str, float]] = []
        used_trucks: set[str] = set()
        for risk, truck_id, component in candidates:
            if len(chosen) >= free_bays:
                break
            if truck_id in used_trucks:
                continue
            used_trucks.add(truck_id)
            self.last_pm_step[(truck_id, component)] = step
            chosen.append((truck_id, component, PM_BY_COMPONENT[component], risk))
        return chosen
