from __future__ import annotations

from typing import Any

from mine_env.policies_c5_3.base_dispatch import BaseDispatchPolicy


class H4FlowRoutePolicy(BaseDispatchPolicy):
    """H4 -- flow/backpressure philosophy recast as capacity routing.

    The C6 ``capacity`` strategy (shortest-queue): send each truck to the route with the most
    remaining daily capacity, balancing load across routes and avoiding congestion. Condition-
    blind: it equalises throughput pressure rather than protecting components.
    """

    policy_id = "H4"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return float(state["route_capacity_remaining"][route_id])
