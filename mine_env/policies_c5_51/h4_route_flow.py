from __future__ import annotations

from typing import Any

from mine_env.policies_c5_51.base_route_facility_dispatch import (
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)


class H4RouteFlowDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_flow"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return self._capacity_score(route_id, state) - 10.0 * self._queue_penalty(route_id, state)


class H4RouteFlowPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H4"
    pm_family = "flow_backpressure"
    dispatch_cls = H4RouteFlowDispatch
