from __future__ import annotations

from typing import Any

from mine_env.reliability_c5_3 import COMPONENTS
from mine_env.policies_c5_3.base_dispatch import BaseDispatchPolicy


class H1HealthRoutePolicy(BaseDispatchPolicy):
    """H1 -- due+health philosophy recast as health routing.

    Routes each truck to the gentlest route for ITS weak components: penalises a route by
    how much it would stress the components the truck is already low on. A worn truck thus
    prefers the smooth low-wear route; a healthy truck is indifferent.
    """

    policy_id = "H1"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        route = self.routes[route_id]
        weakness_weighted_wear = sum(
            (1.0 - self._obs(truck, component))
            * float(route.get(f"{component}_wear_multiplier", 1.0) or 1.0)
            for component in COMPONENTS
        )
        return -weakness_weighted_wear
