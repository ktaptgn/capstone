from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PM_ACTION_ALIAS = {
    "PM_VEHICLE": "PM_VEHICLE_BALANCED",
}


@dataclass(frozen=True)
class MaintenanceAction:
    action_id: str
    duration_hours: float
    cost_multiplier: float


class C5_1MaintenanceModel:
    def __init__(self, config: dict[str, Any]):
        self.actions = {
            action_id: MaintenanceAction(
                action_id=action_id,
                duration_hours=float(values["duration_hours"]),
                cost_multiplier=float(values["cost_multiplier"]),
            )
            for action_id, values in config["maintenance"]["actions"].items()
        }
        self.pm_bay_capacity = int(config["maintenance"]["pm_bay_capacity"])

    def resolve_action(self, action: str) -> MaintenanceAction:
        action_id = PM_ACTION_ALIAS.get(action, action)
        if action_id not in self.actions:
            return self.actions["NO_PM"]
        return self.actions[action_id]

    def is_pm_action(self, action: str) -> bool:
        return self.resolve_action(action).action_id != "NO_PM"
