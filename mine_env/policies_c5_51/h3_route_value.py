from __future__ import annotations

from typing import Any

from mine_env.policies_c5_51.base_route_facility_dispatch import (
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)


class H3RouteValueDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_value"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return self._route_value(route_id)


class H3RouteValuePolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H3"
    pm_family = "cost_value"
    dispatch_cls = H3RouteValueDispatch
