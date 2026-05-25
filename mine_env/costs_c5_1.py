from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PM_COST_KEYS = {
    "PM_TIRE": "pm_tire",
    "PM_VEHICLE": "pm_vehicle_balanced",
    "PM_VEHICLE_BALANCED": "pm_vehicle_balanced",
    "PM_VEHICLE_FAST_EXPENSIVE": "pm_vehicle_fast_expensive",
    "PM_VEHICLE_SLOW_CHEAP": "pm_vehicle_slow_cheap",
}


@dataclass(frozen=True)
class StepCost:
    pm_cost: float
    downtime_cost: float
    degradation_cost: float
    unmet_demand_cost: float

    @property
    def total(self) -> float:
        return (
            self.pm_cost
            + self.downtime_cost
            + self.degradation_cost
            + self.unmet_demand_cost
        )


class C5_1CostModel:
    def __init__(self, config: dict[str, Any]):
        self.event_costs = config["cost_model"]["event_costs"]
        self.report_value_multiplier = float(
            config["operations"]["report_value_multiplier"]
        )

    def pm_cost(self, action: str) -> float:
        key = PM_COST_KEYS.get(action)
        if key is None:
            return 0.0
        return float(self.event_costs[key])

    def downtime_cost(self, downtime_hours: float) -> float:
        return float(downtime_hours) * float(self.event_costs["downtime_cost_per_hour"])

    def degradation_cost(self, hi_loss: float) -> float:
        return float(hi_loss) * float(self.event_costs["degradation_cost_per_hi_loss"])

    def unmet_demand_cost(self, unmet_loads: float) -> float:
        return float(unmet_loads) * float(
            self.event_costs["unmet_demand_penalty_per_load"]
        )

    def step_cost(
        self,
        action: str,
        downtime_hours: float = 0.0,
        hi_loss: float = 0.0,
        unmet_loads: float = 0.0,
    ) -> StepCost:
        return StepCost(
            pm_cost=self.pm_cost(action),
            downtime_cost=self.downtime_cost(downtime_hours),
            degradation_cost=self.degradation_cost(hi_loss),
            unmet_demand_cost=self.unmet_demand_cost(unmet_loads),
        )

    def to_report_value(self, normalized_cost: float) -> float:
        return float(normalized_cost) * self.report_value_multiplier
