from __future__ import annotations

from mine_env.policies.base_policy import BasePolicy


class H4FlowBackpressurePolicy(BasePolicy):
    policy_id = "H4"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H4 received no candidate trucks")

        pressure = self._demand_pressure(state)
        queue_time = float(state["queue_time"])
        backpressure_threshold = float(self.ops["backpressure_queue_threshold_hours"])
        highest_risk = self._highest_risk(trucks)
        risk = self._risk_score(highest_risk)

        if pressure >= float(self.ops["high_demand_pressure"]):
            truck = self._best_health(trucks)
            return self._decision(
                truck,
                "RUN_TO_CRUSHER",
                "FLOW_HIGH_DEMAND_RELEASE",
                pressure,
                state["next_crusher"],
            )

        if queue_time >= backpressure_threshold:
            if risk >= 0.5:
                return self._decision(
                    highest_risk,
                    self._pm_action_for(highest_risk),
                    "FLOW_BACKPRESSURE_PM",
                    risk,
                    "PM Bay",
                )
            return self._decision(
                self._least_pm_risk(trucks),
                "STANDBY",
                "FLOW_BACKPRESSURE_STANDBY",
                queue_time,
            )

        truck = self._best_health(trucks)
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "FLOW_BALANCED_DISPATCH",
            pressure - queue_time,
            state["next_crusher"],
        )
