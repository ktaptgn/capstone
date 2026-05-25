from __future__ import annotations

from mine_env.policies.base_policy import BasePolicy


class H1BottleneckDispatchPolicy(BasePolicy):
    policy_id = "H1"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H1 received no candidate trucks")

        queue_time = float(state["queue_time"])
        pressure = self._demand_pressure(state)
        queue_threshold = float(self.ops["bottleneck_queue_threshold_hours"])

        if queue_time > queue_threshold and pressure < float(
            self.ops["high_demand_pressure"]
        ):
            risky = self._highest_risk(trucks)
            if self._risk_score(risky) >= 0.45:
                return self._decision(
                    risky,
                    self._pm_action_for(risky),
                    "BOTTLENECK_WINDOW_PM",
                    self._risk_score(risky),
                    "PM Bay",
                )
            return self._decision(
                self._least_pm_risk(trucks),
                "STANDBY",
                "BOTTLENECK_QUEUE_HOLD",
                queue_time,
            )

        truck = self._best_health(trucks)
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "BOTTLENECK_DISPATCH_HEALTHY_TRUCK",
            pressure,
            state["next_crusher"],
        )
