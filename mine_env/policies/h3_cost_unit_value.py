from __future__ import annotations

from mine_env.costs_c5_1 import C5_1CostModel
from mine_env.policies.base_policy import BasePolicy


class H3CostUnitValuePolicy(BasePolicy):
    policy_id = "H3"

    def __init__(self, config: dict):
        super().__init__(config)
        self.cost_model = C5_1CostModel(config)

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H3 received no candidate trucks")

        pressure = self._demand_pressure(state)
        threshold = float(self.ops["cost_value_threshold"])

        def run_value(truck: dict) -> float:
            risk = self._risk_score(truck)
            health = (float(truck["truck_hi"]) + float(truck["tire_hi"])) / 2.0
            return pressure * health - self.cost_model.degradation_cost(risk)

        best_run_truck = max(trucks, key=run_value)
        best_run_value = run_value(best_run_truck)
        highest_risk = self._highest_risk(trucks)
        risk = self._risk_score(highest_risk)
        pm_action = self._pm_action_for(highest_risk)
        pm_cost = self.cost_model.pm_cost(pm_action)
        pm_value = risk - (pm_cost * 0.1)

        if pm_value > best_run_value and risk >= threshold:
            return self._decision(
                highest_risk,
                pm_action,
                "COST_VALUE_PM_SELECTED",
                pm_value,
                "PM Bay",
            )

        if pressure <= 0:
            return self._decision(
                self._least_pm_risk(trucks),
                "STANDBY",
                "COST_VALUE_DEMAND_MET",
                best_run_value,
            )
        return self._decision(
            best_run_truck,
            "RUN_TO_CRUSHER",
            "COST_VALUE_RUN_SELECTED",
            best_run_value,
            state["next_crusher"],
        )
