from __future__ import annotations

from typing import Any

from mine_env.policies_c5_3.base_dispatch import BaseDispatchPolicy


class H2RiskRoutePolicy(BaseDispatchPolicy):
    """H2 -- PM-risk-priority philosophy recast as risk-aware routing.

    The C6 ``risk`` strategy: score a (truck, route) by route value minus the condition
    stress it imposes, i.e. ``value - sum(component_risk x route_wear_multiplier)``. Worn
    trucks are steered away from high-stress routes, minimising the degradation/failure that
    drives CM cost. Expected to be the strongest dispatch heuristic on TCO.
    """

    policy_id = "H2"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return self._route_value(route_id) - self._stress_cost(truck, route_id)
