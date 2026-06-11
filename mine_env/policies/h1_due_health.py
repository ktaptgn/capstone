from __future__ import annotations

from mine_env.policies.base_policy import BasePolicy


class H1DueHealthPolicy(BasePolicy):
    """Former H0: simple PM due/HI check followed by first-truck dispatch."""

    policy_id = "H1"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H1 received no candidate trucks")

        pm_due = [truck for truck in trucks if self._needs_pm(truck)]
        if pm_due:
            truck = pm_due[0]
            return self._decision(
                truck,
                self._pm_action_for(truck),
                "DUE_HEALTH_PM_REQUIRED",
                self._risk_score(truck),
                "PM Bay",
            )

        truck = trucks[0]
        if self._demand_pressure(state) <= 0:
            return self._decision(truck, "STANDBY", "DUE_HEALTH_DEMAND_MET", 0.0)
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "DUE_HEALTH_DISPATCH",
            self._demand_pressure(state),
            state["next_crusher"],
        )
