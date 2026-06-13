from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


RUN_ACTIONS = {"RUN_TO_SHOVEL", "RUN_TO_CRUSHER"}
PM_ACTIONS = {"PM_TIRE", "PM_VEHICLE"}
ACTION_SPACE = RUN_ACTIONS | PM_ACTIONS | {"STANDBY"}


class BasePolicy(ABC):
    policy_id = "BASE"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.ops = config["operations"]
        self.fleet = config["fleet"]

    @abstractmethod
    def decide(self, state: dict[str, Any]) -> dict[str, Any]:
        """Return a C5.1 decision dict for the current simulation state."""

    def _decision(
        self,
        truck: dict[str, Any],
        action: str,
        reason_code: str,
        score: float,
        destination: str | None = None,
    ) -> dict[str, Any]:
        if action not in ACTION_SPACE:
            raise ValueError(f"Action is outside C5.1 action space: {action}")
        return {
            "truck_id": truck["truck_id"],
            "action": action,
            "destination": destination,
            "reason_code": reason_code,
            "score": float(score),
        }

    def _candidate_trucks(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        remaining = set(state["remaining_truck_ids"])
        return [truck for truck in state["trucks"] if truck["truck_id"] in remaining]

    def _demand_pressure(self, state: dict[str, Any]) -> float:
        demand = max(float(state["daily_demand"]), 1.0)
        remaining = max(demand - float(state["completed_loads"]), 0.0)
        return remaining / demand

    def _risk_score(self, truck: dict[str, Any]) -> float:
        pm_due_threshold = max(float(self.ops["pm_due_threshold_hours"]), 1.0)
        truck_hi_risk = 1.0 - float(truck["truck_hi"])
        tire_hi_risk = 1.0 - float(truck["tire_hi"])
        pm_due_risk = max(
            0.0,
            (pm_due_threshold - float(truck["pm_due_hours"])) / pm_due_threshold,
        )
        return max(truck_hi_risk, tire_hi_risk, pm_due_risk)

    def _needs_pm(self, truck: dict[str, Any]) -> bool:
        return (
            float(truck["pm_due_hours"]) <= float(self.ops["pm_due_threshold_hours"])
            or float(truck["truck_hi"]) <= float(self.fleet["min_operating_hi"])
            or float(truck["tire_hi"]) <= float(self.fleet["min_operating_tire_hi"])
        )

    def _pm_action_for(self, truck: dict[str, Any]) -> str:
        tire_gap = 1.0 - float(truck["tire_hi"])
        vehicle_gap = 1.0 - float(truck["truck_hi"])
        if tire_gap >= vehicle_gap:
            return "PM_TIRE"
        return "PM_VEHICLE"

    def _best_health(self, trucks: list[dict[str, Any]]) -> dict[str, Any]:
        return max(
            trucks,
            key=lambda truck: (
                float(truck["truck_hi"]) + float(truck["tire_hi"]),
                float(truck["pm_due_hours"]),
            ),
        )

    def _highest_risk(self, trucks: list[dict[str, Any]]) -> dict[str, Any]:
        return max(trucks, key=self._risk_score)

    def _least_pm_risk(self, trucks: list[dict[str, Any]]) -> dict[str, Any]:
        return min(trucks, key=self._risk_score)
