from __future__ import annotations

from mine_env.policies.base_policy import BasePolicy


class H0BaselinePolicy(BasePolicy):
    policy_id = "H0"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H0 received no candidate trucks")

        pm_due = [truck for truck in trucks if self._needs_pm(truck)]
        if pm_due:
            truck = pm_due[0]
            return self._decision(
                truck,
                self._pm_action_for(truck),
                "BASELINE_PM_DUE",
                self._risk_score(truck),
                "PM Bay",
            )

        truck = trucks[0]
        if self._demand_pressure(state) <= 0:
            return self._decision(truck, "STANDBY", "DEMAND_ALREADY_MET", 0.0)
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "BASELINE_DISPATCH",
            self._demand_pressure(state),
            state["next_crusher"],
        )
