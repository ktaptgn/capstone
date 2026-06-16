from __future__ import annotations

from typing import Any

from mine_env.policies_c5_51.base_route_facility_dispatch import (
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)


class H1RouteHealthDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_health"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return -self._weakness_stress(truck, route_id)


class H1RouteHealthPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H1"
    pm_family = "condition"
    dispatch_cls = H1RouteHealthDispatch
