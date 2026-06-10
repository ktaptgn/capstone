from __future__ import annotations

from mine_env.policies.base_policy import BasePolicy


class HTimeDuePmPolicy(BasePolicy):
    policy_id = "H_TIME"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H_TIME received no candidate trucks")

        threshold = float(self.ops["pm_due_threshold_hours"])
        due_trucks = [
            truck for truck in trucks if float(truck["pm_due_hours"]) <= threshold
        ]
        if due_trucks:
            truck = min(due_trucks, key=lambda item: float(item["pm_due_hours"]))
            score = max(0.0, threshold - float(truck["pm_due_hours"]))
            return self._decision(
                truck,
                "PM_VEHICLE",
                "PM_DUE_TIME_PM_DUE",
                score,
                "PM Bay",
            )

        truck = trucks[0]
        pressure = self._demand_pressure(state)
        if pressure <= 0:
            return self._decision(
                truck,
                "STANDBY",
                "PM_DUE_TIME_DEMAND_MET",
                0.0,
            )
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "PM_DUE_TIME_DISPATCH",
            pressure,
            state["next_crusher"],
        )


HTimePeriodicPmPolicy = HTimeDuePmPolicy
