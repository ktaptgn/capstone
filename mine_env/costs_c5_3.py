from __future__ import annotations

from typing import Any

from mine_env.reliability_c5_3 import COMPONENTS


class C5_3CostModel:
    """TCO cost model for C5.3 (C6 cost structure + heterogeneous_condition regime).

    TCO = pm + cm + downtime + degradation + unmet_demand. Production/cycle cost is
    deliberately NOT in the objective: it is the same for any policy that meets demand,
    and including it created an idle-exploit in the RL Lab (see C6 ``reward_tco``). C6's
    per-step idle term is also omitted here -- under C5.3's metered daily-demand model,
    a truck resting because the hourly demand slots are already filled is not a waste, and
    the production shortfall it would have flagged is already captured by the unmet-demand
    penalty.

    The ``heterogeneous_condition`` regime multipliers (``cm_cost`` x1.2, ``downtime`` x1.2)
    are applied transparently on top of the documented C6 base costs; PM/CM HI restore is
    additive by the configured ``recovery`` (a PM is a partial top-up, not a free full heal).
    """

    def __init__(self, config: dict[str, Any]):
        cost = config["cost"]
        regime = config["reliability"].get("regime", {}) or {}
        cm_mult = float(regime.get("cm_cost_multiplier", 1.0) or 1.0)
        dt_mult = float(regime.get("downtime_multiplier", 1.0) or 1.0)

        self.pm = {
            component: {
                "cost": float(cost["pm"][component]["cost_cu"]),
                "duration": float(cost["pm"][component]["duration_hours"]) * dt_mult,
                "recovery": float(cost["pm"][component]["recovery"]),
            }
            for component in COMPONENTS
        }
        self.cm = {
            component: {
                "cost": float(cost["cm"][component]["cost_cu"]) * cm_mult,
                "duration": float(cost["cm"][component]["duration_hours"]) * dt_mult,
                "recovery": float(cost["cm"][component]["recovery"]),
            }
            for component in COMPONENTS
        }
        self.downtime_rate = float(cost["downtime"]["downtime_cost_per_hour_cu"]) * dt_mult
        self.degradation = {
            component: float(cost["degradation"][f"{component}_hi_loss_cost"])
            for component in COMPONENTS
        }
        self.unmet_penalty = float(cost["demand"]["unmet_load_penalty_cu"])
        self.report_multiplier = float(config["simulation"]["report_value_multiplier"])

    def degradation_cost(self, losses: dict[str, float]) -> float:
        return sum(float(losses.get(c, 0.0)) * self.degradation[c] for c in COMPONENTS)

    def unmet_demand_cost(self, unmet_loads: float) -> float:
        return float(unmet_loads) * self.unmet_penalty

    def to_report_value(self, normalized_cost: float) -> float:
        return float(normalized_cost) * self.report_multiplier
