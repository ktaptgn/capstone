from __future__ import annotations

from mine_env.policies.base_policy import BasePolicy


class H2PmRiskPriorityPolicy(BasePolicy):
    policy_id = "H2"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H2 received no candidate trucks")

        highest_risk = self._highest_risk(trucks)
        risk = self._risk_score(highest_risk)
        pressure = self._demand_pressure(state)

        if risk >= float(self.ops["pm_risk_threshold"]) and pressure < 0.95:
            return self._decision(
                highest_risk,
                self._pm_action_for(highest_risk),
                "PM_RISK_PRIORITY",
                risk,
                "PM Bay",
            )

        truck = self._least_pm_risk(trucks)
        if pressure <= 0:
            return self._decision(truck, "STANDBY", "DEMAND_ALREADY_MET", risk)
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "PM_RISK_SAFE_TO_RUN",
            pressure - risk,
            state["next_crusher"],
        )
