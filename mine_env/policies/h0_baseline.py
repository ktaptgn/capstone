from __future__ import annotations

import re

from mine_env.policies.base_policy import BasePolicy


class H0BaselinePolicy(BasePolicy):
    policy_id = "H0"

    def decide(self, state: dict) -> dict:
        trucks = self._candidate_trucks(state)
        if not trucks:
            raise ValueError("H0 received no candidate trucks")

        interval_days = max(int(self.ops["periodic_pm_interval_days"]), 1)
        scheduled_trucks = [
            truck for truck in trucks if self._is_calendar_pm_day(truck, state, interval_days)
        ]
        if scheduled_trucks:
            truck = min(scheduled_trucks, key=self._truck_number)
            return self._decision(
                truck,
                "PM_VEHICLE",
                "BASELINE_PERIODIC_PM_SLOT",
                1.0,
                "PM Bay",
            )

        truck = trucks[0]
        pressure = self._demand_pressure(state)
        if pressure <= 0:
            return self._decision(truck, "STANDBY", "BASELINE_PERIODIC_DEMAND_MET", 0.0)
        return self._decision(
            truck,
            "RUN_TO_CRUSHER",
            "BASELINE_PERIODIC_DISPATCH",
            pressure,
            state["next_crusher"],
        )

    def _is_calendar_pm_day(
        self, truck: dict, state: dict, interval_days: int
    ) -> bool:
        day = int(state["day"])
        offset = (self._truck_number(truck) - 1) % interval_days
        return (day - 1 - offset) % interval_days == 0

    def _truck_number(self, truck: dict) -> int:
        match = re.search(r"\d+", str(truck["truck_id"]))
        return int(match.group(0)) if match else 1
